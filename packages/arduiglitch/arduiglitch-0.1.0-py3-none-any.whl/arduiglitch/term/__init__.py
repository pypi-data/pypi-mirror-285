"""
This submodule provides classes to build a terminal interface for the user.

`Selectable` and `SelectableMenu` are used to create a menu with buttons that
can be cycled through with the arrow keys and pressed with the enter key to
run callbacks in separate threads.

The callbacks can be given resources used by
other callbacks, in wich case the `synchronised` decorator can be used to ensure
memory safety (especially functions that involve serial com.).
"""

from .inputter import Inputter
from .selectable import Selectable
from .selectable_menu import SelectableMenu
from .synchronization import synchronized
from .tab_menu import TabMenu
from .tab_log import TabLog
from .tab_text import TabText
from .tab import Tab
from .term_logger_handler import TermLogHandler

__all__ = [
    "Inputter",
    "Selectable",
    "SelectableMenu",
    "synchronized",
    "TabMenu",
    "TabLog",
    "TabText",
    "Tab",
    "TermLogHandler",
]
