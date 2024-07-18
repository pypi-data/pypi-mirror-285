"""
`Tab` subclass to display some text.
"""

from .synchronization import synchronized
from blessed import Terminal
from .tab import Tab

class TabText(Tab):
    """
    A tab that simply displays some text.
    """
    def __init__(
        self,
        term: Terminal,
        position: tuple[int, int],
        width: int,
        height: int,
        title: str,
        text: str,
        visible: bool = False
    ):
        super().__init__(
            term,
            position,
            width,
            height,
            title,
            visible,
            "on_peachpuff"
        )
        self._text = text

    def _render(self):
        x, y = self._position
        lines = self._text.splitlines()
        inner_width = self._width - 2
        wrapped_lines = []
        for line in lines:
            while len(line) > inner_width:
                wrapped_lines.append(line[:inner_width])
                line = line[inner_width:]
            else:
                wrapped_lines.append(line)
        if len(wrapped_lines) > self._height - 2:
            wrapped_lines = wrapped_lines[:self._height-1]
        for i in range(self._height):
            line = ""
            if i == 0:
                line = "┌" + self._title.center(inner_width, "─") + "┐"
            elif i == self._height - 1:
                line = "└" + "─" * inner_width + "┘"
            else:
                if len(wrapped_lines) == 0 or (i - 1) >= len(wrapped_lines):
                    line = "│" + " " * inner_width + "│"
                else:
                    line = "│" + wrapped_lines[i-1].ljust(inner_width) + "│"
            with synchronized(self._term):
                print(self._term.move_xy(x, y + i) + line)
