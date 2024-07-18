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


class SkipMaxAttemptsCampaign(Campaign):
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
            "reg": "AA",
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

                for _ in range(10):
                    # Loop over params and push errors in data_out_queue to
                    # update gui.
                    # Following control_queue read and handle must be in loop to
                    # be executed regularily.
                    loop = not Campaign.should_stop_thread(self._queue)

                    # Arduino start its operation (will trigger pulse)
                    timecode = strftime("%H:%M:%S", gmtime())
                    match self._target.verifypin():
                        case Ok(True):
                            # Successful fault injection
                            self._template_row["time"] = timecode
                            self._template_row["delay"] = delay
                            self._template_row["reg"] = "AA"
                            self.to_csv([dict(self._template_row)],
                                        append=True)
                        case Err(err):
                            # Reset target Arduino board if communication failed
                            self._log.warning("Error during com. with target:")
                            self._log.warning(f"{err}")
                            self._template_row["time"] = timecode
                            self._template_row["delay"] = delay
                            self._template_row["reg"] = "Crash"
                            self.to_csv([dict(self._template_row)],
                                        append=True)
                            self._glitcher.reset_target()
                            sleep(0.8)
                    if not loop:
                        break
                if not loop:
                    break

    def brute_force_pin(self,
                        min_pin: int,
                        max_pin: int,
                        verbose: bool = True) -> int | None:
        """
        This function tries to brute force the PIN of the target.
        It opens instruments if they are not already opened.

        :return: pin from 0 to 9999 if it was successfully found
        """
        for pin in range(min_pin, max_pin + 1):
            if self._log_with_pin(pin, verbose=verbose):
                return pin
            if Campaign.should_stop_thread(self._queue):
                break
        return None

    def _log_with_pin(self, pin: int, verbose: bool = True) -> bool:
        """
        This function ought to be used once g_ptc decrement was successfully
        faulted. It tries to authenticate with `pin`.
        """
        self._target.open_instrument()
        self._glitcher.open_instrument()

        if verbose:
            self._log.info(f"Trying PIN {pin}")
        match self._target.set_user_pin(pin):
            case Ok(None):
                sleep(0.1)
                match self._target.verifypin():
                    case Ok(True):
                        if verbose:
                            self._log.info(f"PIN found : {pin}")
                        return True
                    case Err(err):
                        self._log.warning(err)
            case Err(err):
                self._log.warning(err)
        return False
