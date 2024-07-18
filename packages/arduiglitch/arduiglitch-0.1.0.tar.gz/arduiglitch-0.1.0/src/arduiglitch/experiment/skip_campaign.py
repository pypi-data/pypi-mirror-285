"""
This class should be instanciated in the callback that runs a fault
injection campaign. `Target` and `Glitcher` do not need to be already
opened before `__init__`.
"""
from ..arduino.target import Target
from ..arduino.glitcher import Glitcher
from ..utils.logger import Log
from ..utils.result import Ok, Err
from ..experiment.campaign import Campaign
from queue import Queue
from time import sleep, gmtime, strftime
from typing import Any


class SkipCampaign(Campaign):
    """
    This class should be instanciated in the callback that runs a fault
    injection campaign. `Target` and `Glitcher` do not need to be already
    opened before `__init__`.
    """

    def __init__(self, log: Log, glitcher: Glitcher, target: Target,
                 csv_filename: str, queue: Queue, min_delay: int,
                 max_delay: int, step_delay: int):
        super().__init__(log, glitcher, target, csv_filename, queue)

        self._min_delay: int = min_delay
        self._max_delay: int = max_delay
        self._step_delay: int = step_delay

        self._template_row: dict[str, Any] = {
            "time": 0,
            "min_delay": min_delay,
            "max_delay": max_delay,
            "step_delay": step_delay,
            "reg": "r0",
            "delay": 0,
        }

    def run(self):
        """
        Run experiment loop. Opens communication with instruments if not already
        opened. Sweeps through delays specified during instance initialization.
        """
        # Create panda data structure in which to store the results
        self.to_csv([], append=False)

        # Open instruments if not already
        self._target.open_instrument()
        self._glitcher.open_instrument()

        # Set glitcher cooldown to 100ms and reset target
        self.ensure_set_glitch_cooldown(100)
        self._glitcher.reset_target()
        sleep(0.8)

        self._log.info("Experiment started...")

        # Delays to iterate the test on
        delays = list(range(self._min_delay, self._max_delay,
                            self._step_delay))

        # Loop until process is shut down
        loop = True
        while loop:
            # For every delay to test
            for delay in delays:
                # Set new delay on glitcher Arduino board
                self.set_glitch_delay(delay)
                self._log.info("Glitch delay set to %d.", delay)

                for _ in range(5):
                    # Arduino start its operation (will trigger pulse)
                    # Repeat asm code until no timeout
                    loop = self._ensure_asm_code()
                    if loop is False:
                        break

                    # Get register values from arduino after the attack
                    timecode = strftime("%H:%M:%S", gmtime())
                    self._get_regs_and_update_graph(
                        timecode,
                        delay,
                    )

                if loop is False or Campaign.should_stop_thread(self._queue):
                    break

    def _ensure_asm_code(self) -> bool:
        """
        Returns False if the thread should stop, True otherwise.
        """
        self._log.info("...set_asmcode()")
        while True:
            if Campaign.should_stop_thread(self._queue):
                return False
            match self._target.set_asmcode():
                case Err(e):
                    self._log.error(e)
                    match self._target.set_led_off():
                        case Err(_):
                            self._log.error(
                                "Detected com crash, reset target.")
                            self._glitcher.reset_target()
                            sleep(0.8)
                case Ok(None):
                    return True
            self._log.warning("... ... retrying")

    def _get_regs_and_update_graph(
        self,
        timecode: str,
        delay: int,
    ):
        match self._target.get_regs():
            case Ok(regs):
                # If communication was a success, regs is an array of 10 ints
                results = []
                for reg_i, reg in enumerate(regs):
                    if reg == 0x55:
                        self._log.info(f"Detected 0x55 in register r{reg_i}.")
                        self._template_row["time"] = timecode
                        self._template_row["reg"] = f"r{reg_i}"
                        self._template_row["delay"] = delay
                        results.append(dict(self._template_row))
                if len(results) > 0:
                    self.to_csv(results, append=True)
            case Err(e):
                # Reset target Arduino board if communication failed
                self._log.error("Error during communication with target:")
                self._log.error(f"{e}")
                self._template_row["time"] = timecode
                self._template_row["reg"] = "Crash"
                self._template_row["delay"] = delay
                self.to_csv([dict(self._template_row)], append=True)
                self._glitcher.reset_target()
                sleep(0.8)
