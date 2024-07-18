"""
`Tab` subclass to display live log.
Tweak `TermLogHandler` to change what ends up displayed in the `Tablog`.
"""

from .synchronization import synchronized
from blessed import Terminal
from .tab import Tab
from .term_logger_handler import TermLogHandler
from time import time, sleep
from threading import Thread

class TabLog(Tab):
    """
    TabLog is a Tab subclass that renders the output of a custom logger handler.
    """
    def __init__(self, log: TermLogHandler, term: Terminal, position: tuple[int, int], width: int, height: int, title: str, visible: bool = False, fps: int = 10):
        super().__init__(term, position, width, height, title, visible, "on_peachpuff")
        self._log: TermLogHandler = log
        self._running: bool = False

        self._fps: float = float(fps)
        self._last_render = time()
        self._last_text: list[str] = []

        self._render_thread: Thread = Thread(target=self._render)

        # how many lines to scroll up when the log is too long
        self._render_offset: int = 0

    def _render(self):
        is_first_render: bool = True
        while True:
            sleep(0.05)
            current_time = time()
            if current_time - self._last_render > 1.0 / self._fps:
                # `self._last_render` is updated later only if the text changed
                x, y = self._position
                text: list[str] = list(self._log.get_log())

                log_too_long = len(text) > (self._height-2)

                scroll_offset = 0
                if log_too_long:
                    scroll_offset = min(max(0, len(text) - (self._height-2)), self._render_offset)
                    text = text[len(text) - scroll_offset - (self._height-2):len(text) - scroll_offset]
                else:
                    while len(text) < (self._height-2):
                        text.append("")

                hidding_lines_before = scroll_offset < len(self._log.get_log()) - (self._height-2)
                hidding_lines_after = scroll_offset > 0 and len(self._log.get_log()) > (self._height-2)

                log_updated = text != self._last_text
                if log_updated or is_first_render:
                    is_first_render = False
                    self._last_render = current_time
                    self._last_text = text
                    for i in range(self._height):
                        # box drawing
                        if i == 0:
                            line = "┌" + self._title.center(self._width - 2, "─") + "┐"
                        elif i == self._height - 1:
                            line = "└" + "─" * (self._width - 2) + "┘"
                        else:
                            if len(text[i - 1]) > self._width - 3:
                                line = "│" + text[i-1][:self._width - 4] + "▹ │"
                            else:
                                line = "".join([
                                    "│",
                                    text[i-1],
                                    " " * (self._width - 2 - len(self._term.strip_seqs(text[i-1]))),
                                    "│",
                                ])

                        with synchronized(self._term):
                            # scrolling indicator drawing
                            if hidding_lines_before and i == 0:
                                line = line[:len(line) - 2] + self._term.bold_red("▲") + line[-1]
                            elif hidding_lines_after and i == self._height - 1:
                                line = line[:len(line) - 2] + self._term.bold_red("▼") + line[-1]
                            print(
                                self._term.move_xy(x, y + i)
                                + line
                            )
                if not self._queue.empty():
                    cmd = self._queue.get()
                    match cmd:
                        case ("exit"):
                            break
        self._running = False

    def show(self):
        self._visible = True
        if not self._running:
            self._running = True
            self._render_thread = Thread(target=self._render)
            self._render_thread.start()

    def hide(self):
        self._visible = False
        if self._running:
            self.queue_cmd(("exit"))
            self._render_thread.join()
        self._clear()

    def toggle(self):
        if not self._visible:
            self.show()
        else:
            self.hide()

    def add_scroll(self, n: int):
        """
        Increments/Decrements the scroll offset value.
        n > 0 => scroll up.
        Offset is limited by the size of the log.
        Offset cannot be negative.
        """
        self.set_scroll(self._render_offset + n)

    def set_scroll(self, n: int):
        """
        Sets the scroll offset value.
        n >= 0.
        Offset is limited by the size of the log.
        Offset cannot be negative.
        """
        self._render_offset = max(0, n)
        self._render_offset = max(0, min(self._render_offset, len(self._log.get_log()) - self._height + 2))
