"""
This abstract class cannot be instanced itself.
Use subclasses such as `SkipCampaign`.
Subclasses should be instanciated in the callback that runs a fault
injection campaign.
"""

from abc import abstractmethod
import pandas as pd
from ..arduino.target import Target
from ..arduino.glitcher import Glitcher
from ..utils.logger import Log
from ..utils.result import Ok, Err
from queue import Queue
from typing import Any

class Campaign:
    """
    This abstract class cannot be instanced itself.
    Use subclasses such as `SkipCampaign`.
    Subclasses should be instanciated in the callback that runs a fault
    injection campaign.
    """
    def __init__(
        self,
        log: Log,
        glitcher: Glitcher,
        target: Target,
        csv_filename: str,
        queue: Queue,
    ):
        self._log: Log = log
        self._glitcher: Glitcher = glitcher
        self._target: Target = target
        self._csv_filename: str = csv_filename
        self._queue: Queue = queue

        self._template_row: dict[str, Any] = {
            "time": 0,
            "delay": 0,
        }

    @abstractmethod
    def run(self):
        pass

    def set_glitch_delay(self, delay: int):
        match self._glitcher.set_first_glitch_delay(delay):
            case Err(e):
                # If communication with glitcher failed, close both Arduinos and
                # return.
                self._log.error("Error during communication with glitcher:")
                self._log.error(f"{e}")
                self._log.error(f"Could not set glitch delay to {delay}.")

    def ensure_set_glitch_cooldown(self, delay: int):
        """
        Tries to set the glitcher cooldown to the given value until it succeeds.
        """
        self._log.info("Setting glitcher cooldown to 100ms.")
        while True:
            if Campaign.should_stop_thread(self._queue):
                break
            match self._glitcher.set_glitch_cooldown(delay):
                case Ok(100):
                    break
                case Ok(val):
                    self._log.warning(f"Unexpected value returned: {val}")
                case Err(e):
                    self._log.error(e)

    def to_csv(self, results: list[dict[str, Any]], append: bool):
        header = list(self._template_row.keys())
        df = pd.DataFrame(results, columns=header)
        df.to_csv(
            self._csv_filename,
            mode="a" if append else "w+",
            header=not append,
            index=False
        )

    @staticmethod
    def should_stop_thread(control_queue: Queue) -> bool:
        if not control_queue.empty():
            return control_queue.get() == ("exit")
        return False
