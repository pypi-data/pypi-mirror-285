"""
`Inputter` class enables adding a user input box to the terminal. It is used
by the `Selectable` class when a requirement is added before running a
callback.
"""

from .synchronization import synchronized
from blessed import Terminal
from time import sleep

class Inputter:
    """
    A displayable value input box that can be used to get user input.
    """
    def __init__(self, position: tuple[int, int], width: int = 14):
        self._position = position
        self._width = width

    def render(self, term: Terminal):
        with synchronized(self):
            x, y = self._position
            inner_width = self._width - 2
        with synchronized(term):
            print(term.move_xy(x, y) + "┌" + "─" * inner_width + "┐")
            print(term.move_xy(x, y+1)+"│"+"Input: ".ljust(inner_width)+"│")
            print(term.move_xy(x, y+2) + "│" + "(/)".ljust(inner_width) + "│")
            print(term.move_xy(x, y+3) + "│" + "".ljust(inner_width) + "│")
            print(term.move_xy(x, y+4) + "└" + "─" * inner_width + "┘")

    def get(self, term: Terminal, var_text: str, var_type: str):
        """
        var_type: (type) The type to cast the user value into.
        Will get stuck until a valid user value was entered and casted (or ESC
        is pressed). Returns None when ESC is pressed.
        """
        assert var_type in [str, int, float]
        value: str = ""
        inp = None
        blink_state: bool = False
        x, y = self._position
        inner_width = self._width - 2
        input_line_len = len("Input: ") + len(var_text) + 2
        input_ln = "Input: " + term.bold_red_on_snow3(" " + var_text + " ")
        input_ln += "".ljust(inner_width - input_line_len)
        typ_line = term.bold_orange(
            f"({var_type.__name__})".ljust(inner_width)
        )
        while inp is None or inp.name != "KEY_ESCAPE":
            while inp is None or inp.name != "KEY_ENTER":
                cursor = "▒" if blink_state else " "
                with synchronized(term):
                    color = term.bold_orange if blink_state \
                                                 else term.bold_black
                    val_line = term.bold_red(value)\
                        + cursor \
                        + "".ljust(max(0, inner_width - len(value) - 1))

                    print(term.move_xy(x, y)+color("┌"+"─"*inner_width+"┐"))
                    print(term.move_xy(x, y + 1)+color("│")+input_ln+color("│"))
                    print(term.move_xy(x, y + 2)+color("│")+typ_line+color("│"))
                    print(term.move_xy(x, y + 3)+color("│")+val_line+color("│"))
                    print(term.move_xy(x, y + 4)+color("└"+"─"*inner_width+"┘"))
                inp = term.inkey(timeout=0.4)
                if inp == "":
                    # timed out
                    blink_state = not blink_state
                elif inp.name == "KEY_ESCAPE":
                    # Returns None if the user pressed ESC, parent script needs
                    # to handle this case.
                    self.render(term)
                    return None
                elif inp.is_sequence:
                    blink_state = True
                    if inp.name == "KEY_BACKSPACE":
                        value = value[:-1]
                else:
                    blink_state = True
                    if len(value) < inner_width:
                        value += inp
            try:
                if var_type == str:
                    self.render(term)
                    return value
                elif var_type == int:
                    self.render(term)
                    return int(value)
                elif var_type == float:
                    self.render(term)
                    return float(value)
                else:
                    raise ValueError
            except ValueError:
                with synchronized(term):
                    x, y = self._position
                    print(term.move_xy(x, y + 3)+"│"+term.on_darkorange1("INVALID".ljust(inner_width))+"│")
                sleep(1)
                value = ""
                inp = None
