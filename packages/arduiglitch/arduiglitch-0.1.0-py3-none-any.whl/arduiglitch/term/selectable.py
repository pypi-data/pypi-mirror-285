"""
`Selectable` class is a sort of button that can be toggled and selected by the
user. It was designed to be used by the `Menu` class.
"""

from .synchronization import synchronized
from threading import Thread
from queue import Queue
from blessed import Terminal
from time import time
import logging
from .inputter import Inputter

class Selectable:
    """
    A piece of text that can be selected and toggled by the user.
    """
    def __init__(
        self,
        term: Terminal,
        position: tuple[int, int],
        text: str,
        toggled: bool = False,
        selected: bool = False,
        untoggle_after: bool = True,
        animated: bool = True
    ):
        self._log = logging.getLogger(__name__)
        self._toggled: bool = toggled
        self._selected: bool = selected
        self._running: bool = False
        self._position: tuple[int, int] = position
        self._queue: Queue = Queue()
        # appearance
        with synchronized(term):
            self._look_normal = term.red
            self._look_selected = term.on_orange
            self._look_unselected = term.on_snow
            self._look_toggled = term.green

        self._text = text

        # animation
        self._frames = ["/", "|", "\\", "-"]
        self._fps = 5
        self._animated = animated

        # requirements
        self._requirements = []
        self._inputter: Inputter = None

        # callback
        self._callback = None
        self._callback_args = []
        self._untoggle_after = untoggle_after

    def with_requirement(
        self,
        user_inputs: tuple[str, type],
        inputter: Inputter
    ):
        """
        When running the selectable, some user inputs might be required for the
        callback to run. This method registers the values to ask the user
        before running.
        """
        self.add_requirement(user_inputs, inputter)
        return self

    def add_requirement(
        self,
        user_inputs: tuple[str, type],
        inputter: Inputter
    ):
        """
        When running the selectable, some user inputs might be required for the
        callback to run. This method registers the values to ask the user
        before running.
        """
        self._requirements.append(user_inputs)
        self._inputter = inputter

    def with_callback(self, callback, *args):
        """
        Callback is called when the selectable is run, after optionnal user
        inputs are valid.
        The prototype of the callback should be:
        ```def my_callback(*args, queue: Queue,user_inputs: dict[str, type]):```
        if user inputs are required. Else:
        ```def my_callback(*args, queue: Queue):```

        The queue is mostly used to enable to level threads to notify the
        callback that the program needs to exit
        """
        self.set_callback(callback, *args)
        return self

    def set_callback(self, callback, *args):
        """
        Callback is called when the selectable is run, after optionnal user
        inputs are valid.
        The prototype of the callback should be:
        ```def my_callback(*args, queue: Queue,user_inputs: dict[str, type]):```
        if user inputs are required. Else:
        ```def my_callback(*args, queue: Queue):```

        The queue is mostly used to enable to level threads to notify the
        callback that the program needs to exit.
        """
        self._callback = callback
        self._callback_args = args

    def render(self, term):
        text = self._text
        if self._selected:
            text = self._look_selected(text)
        else:
            text = self._look_unselected(text)
        if self._toggled:
            text = self._look_toggled(text)
        else:
            text = self._look_normal(text)
        with synchronized(term):
            print(term.move_xy(*self._position) + text)

    def run(
        self,
        term,
        wait_for_callback: bool = False
    ) -> bool:
        if not self._running:
            # before running, get user inputs from inputter if needed
            user_inputs = {}
            for (var_text, var_type) in self._requirements:
                match self._inputter.get(term, var_text, var_type):
                    case None:
                        # The user pressed ESC
                        return None
                    case value:
                        user_inputs[var_text] = value

            self._toggled = not self._toggled
            self._running = True
            self.render(term)
            if self._animated:
                t_anim = Thread(target=self._animation, args=(term,))
                t_anim.start()
            # Start run thread
            # Run regardless of user inputs or callback
            if user_inputs: # if not empty dict
                t_callback = Thread(
                    target=self._run,
                    args=(
                        term,
                        self._callback,
                        (*self._callback_args, self._queue, user_inputs, ),
                    )
                )
            else:
                t_callback = Thread(
                    target=self._run,
                    args=(
                        term,
                        self._callback,
                        (*self._callback_args, self._queue, ),
                    )
                )
            t_callback.start()
            if wait_for_callback:
                t_callback.join()
                if self._animated:
                    t_anim.join()
            return True
        else:
            return False

    def _run(
        self,
        term: Terminal,
        callback,
        callback_args,
    ):
        if callback is not None:
            callback(*callback_args)
        if self._untoggle_after:
            self._toggled = False
            self.render(term)
        self._running = False

    def _animation(self, term: Terminal):
        last_frame = 0
        last_update = time()
        while self._running:
            with synchronized(term):
                if time() - last_update > 1 / self._fps:
                    last_frame = (last_frame + 1) % len(self._frames)
                    last_update = time()
                    x, y = self._position
                    x += len(self._text) + 1
                    print(term.move_xy(x, y) + self._frames[last_frame])
        with synchronized(term):
            x, y = self._position
            x += len(self._text) + 1
            print(term.move_xy(x, y) + " ")

    def select(self, value: bool = True):
        self._selected = value

    def get_position(self) -> list[int]:
        return self._position

    def get_text(self) -> str:
        return self._text

    def is_running(self) -> bool:
        return self._running

    def is_toggled(self) -> bool:
        return self._toggled

    def queue_cmd(self, cmd):
        self._queue.put(cmd)
