"""
`TabMenu` class to display only one tab at a time.
"""

from .tab import Tab

class TabMenu:
    """
    Contains a list of tabs and automatically switches the visibility of them.
    """
    def __init__(self, tabs: list[Tab], selected: int = 0):
        self._tabs = tabs
        self._selected = selected
        for tab in self._tabs:
            tab.hide()
        self._tabs[self._selected].show()

    def select(self, i: int):
        i = i % len(self._tabs)
        if i != self._selected:
            self._tabs[self._selected].hide()
            self._selected = i
            self._tabs[self._selected].show()

    def get_tabs(self) -> list[Tab]:
        return self._tabs
