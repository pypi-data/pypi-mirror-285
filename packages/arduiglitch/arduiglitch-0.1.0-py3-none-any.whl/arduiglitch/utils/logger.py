"""
Arduiglitch - voltage glitch training on an ATMega328P
Copyright (C) 2024  Hugo PERRIN (h.perrin@emse.fr)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

Contains a function that handles configuring the main Logger. The actual
configuration is contained in the associated yaml file. The goal is to enable
easy switch between a PyLabSAS version or without with minimal change in the
actual scripts.
"""

import logging
import logging.config
#from ..term.term_logger_handler import TermLogHandler
from logging import Handler


class Log(logging.Logger):
    """
    Small logging wrapper to provide a custom logging interface for the project.
    """

    def __init__(self, name: str, level: int = logging.DEBUG):
        super().__init__(__name__, level=level)
        self._logh: Handler | None = None
        self._logf: logging.FileHandler | None = None

    def with_term_handler(self, logh: Handler, level: int | None = None):
        """
        Example:
            .. code-block:: python

                log = Log(__name__, level=logging.DEBUG)
                        .with_term_handler(Handler())
        """
        if self._logh is None:
            # Create terminal display log handler
            self._logh = logh
            self._logh.setLevel(level if level is not None else self.level)
            self._logh.setFormatter(
                logging.Formatter("%(asctime)s | %(levelname)s | %(message)s",
                                  "%H:%M:%S"))
            self.addHandler(self._logh)
        return self

    def get_logh(self) -> Handler | None:
        """
        Return the terminal log handler if it was added to the logger with
        `with_term_handler`, else `None`.
        """
        return self._logh

    def with_file_handler(self, filename: str, level: int | None = None):
        if self._logf is None:
            # Create file log handler
            self._logf = logging.FileHandler(filename)
            self._logf.setLevel(level if level is not None else self.level)
            self._logf.setFormatter(
                logging.Formatter("%(asctime)s | %(levelname)s | %(message)s",
                                  "%H:%M:%S"))
            self.addHandler(self._logf)
        return self
