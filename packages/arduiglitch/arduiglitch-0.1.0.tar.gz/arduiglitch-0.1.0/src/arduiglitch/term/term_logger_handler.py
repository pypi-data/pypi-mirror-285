"""
This logging handler prints to strings instead of files so that it can be
rendered in the terminal with the `blessed` module.
"""
from logging import Handler

class TermLogHandler(Handler):
    """
    Log handler to easily render formatted log output in terminal.
    """
    def __init__(self, height: int = 10, max_lines: int = -1):
        super().__init__()
        self._log: list[str] = []
        self.height = height
        self.max_lines = max_lines

    def emit(self, record: str):
        if self.max_lines > 0 and len(self._log) >= self.max_lines:
            self._log.pop(0)
        self._log.append(self.format(record))

    def get_log(self):
        return self._log

    def clear_log(self):
        self._log = []

    def render_log(self, height: int):
        return "\n".join(self.get_log()[:height])

    def flush(self) -> None:
        return self._log.clear()
