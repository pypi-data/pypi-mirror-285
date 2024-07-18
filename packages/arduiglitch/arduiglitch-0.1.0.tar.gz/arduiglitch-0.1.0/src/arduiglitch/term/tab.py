"""
`Tab` class for adding text panels that can be shown or hidden.
"""

from .synchronization import synchronized
from queue import Queue
from blessed import Terminal


class Tab:
    """
    Tab that can be shown and updated or hidden.
    The rendering runs in a thread separate to the menu main loop to be
    independant from user input.
    """

    def __init__(self,
                 term: Terminal,
                 position: tuple[int, int],
                 width: int,
                 height: int,
                 title: str,
                 visible: bool = False,
                 bg_color: str = "on_snow4"):
        self._term: Terminal = term
        self._position = position
        self._width = width
        self._height = height
        self._title = title
        self._visible = visible
        self._bg_color = bg_color

        self._queue: Queue = Queue()

    def _clear(self):
        x, y = self._position
        for i in range(self._height):
            with synchronized(self._term):
                print(self._term.move_xy(x, y + i) + "".ljust(self._width))

    def _render(self):
        term = self._term
        x, y = self._position
        for i in range(self._height):
            with synchronized(term):
                print(
                    term.move_xy(x, y + i)\
                    + getattr(term, self._bg_color)("".ljust(self._width)))

    def is_visible(self) -> bool:
        return self._visible

    def show(self):
        self._visible = True
        self._render()

    def hide(self):
        self._visible = False
        self._clear()

    def toggle(self):
        if not self._visible:
            self.show()
        else:
            self.hide()

    def queue_cmd(self, cmd):
        self._queue.put(cmd)

    def draw_box(self, width: int, height: int, style: str):
        lines: list[str] = []
        in_width = width - 2
        for y in range(height):
            if y == 0:
                lines.append(style + "┌" + "─" * in_width + "┐" +
                             self._term.normal)
            elif y == height - 1:
                lines.append(style + "└" + "─" * in_width + "┘" +
                             self._term.normal)
            else:
                lines.append(style + "│" + self._term.normal + " " * in_width +
                             style + "│" + self._term.normal)
        return lines

    def draw_text_in_box(
        self,
        width: int,
        height: int,
        text: list[str],
        box_style: str,
    ):
        lines: list[str] = self.draw_box(width, height, box_style)
        in_width = width - 2

        # Write text lines in box, truncating if necessary
        for y in width:
            if y == 0:
                pass
            elif y == height - 1:
                pass
            else:
                lines[y] = lines[y][0] + text[y - 1][:in_width] + lines[y][-1]

        return lines
