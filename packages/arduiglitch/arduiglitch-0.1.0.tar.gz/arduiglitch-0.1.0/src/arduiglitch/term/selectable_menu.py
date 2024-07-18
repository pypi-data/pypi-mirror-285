"""
`SelectableMenu` to handle selection and user input of `Selectable` instances.
"""

from .selectable import Selectable
from .tab_menu import TabMenu
from ..utils.logger import Log
from queue import Queue
from blessed import Terminal


class SelectableMenu:
    """
    Group of buttons that the user can cycle through to run callbacks in
    separate threads.
    """

    def __init__(self, log: Log, selectables: list[Selectable], tabs: TabMenu):
        self._log: Log = log
        self._selectables: list[Selectable] = selectables
        self._tabs: TabMenu = tabs
        # indexes of closest neighbours for each selectable
        # [up, down, left, right]
        self._neighbours: list[list[int]] = self._compute_neighbours()
        self._main_loop_queue: Queue = Queue()

    def _compute_neighbours(self) -> list[list[int]]:
        """
        This method creates an array of tuples that contain the index of the
        previous and next selectable for each selectable in the list depending
        on their relative position on screen.
        """

        if len(self._selectables) == 0:
            return []

        # all neighbours should be computed before needing to iterate over every
        # selectable since assignments are symetrical (ie. if i is closest to j,
        # then j is closest to i)
        neighbours: list[list[int]] = []
        for i in range(len(self._selectables)):
            neighbours.append([i, i, i, i])

        # [min_x, min_y, max_x, max_y] of the selectables
        # used to wrap coordinates around the screen
        first_sel_pos = self._selectables[0].get_position()
        first_sel_text = self._selectables[0].get_text()
        xy_bounds = [
            first_sel_pos[0] + len(first_sel_text) / 2.0, first_sel_pos[1],
            first_sel_pos[0] + len(first_sel_text) / 2.0, first_sel_pos[1]
        ]
        for i in range(len(self._selectables)):
            pos = self._selectables[i].get_position()
            text = self._selectables[i].get_text()
            x, y = pos[0] + len(text) / 2.0, pos[1]
            xy_bounds[0] = min(x, xy_bounds[0]) - 1.0
            xy_bounds[1] = min(y, xy_bounds[1]) - 1.0
            xy_bounds[2] = max(x, xy_bounds[2]) + 1.0
            xy_bounds[3] = max(y, xy_bounds[3]) + 1.0

        for i in range(len(self._selectables)):
            # (up, down, left, right)
            closest_i: list[int] = [i, i, i, i]
            closest_i_dir: list[int] = [i, i, i, i]
            closest_delta: list[float | None] = [None, None, None, None]
            closest_delta_dir: list[float | None] = [None, None, None, None]
            for j in range(len(self._selectables)):
                if i != j:
                    xmin, ymin, xmax, ymax = xy_bounds[0], xy_bounds[
                        1], xy_bounds[2], xy_bounds[3]
                    xi, yi = self._selectables[i].get_position()
                    xj, yj = self._selectables[j].get_position()
                    xi += len(self._selectables[i].get_text()) / 2.0
                    xj += len(self._selectables[j].get_text()) / 2.0

                    dists_dir: list[float] = [
                        SelectableMenu._dist_in_direction(yi, yj, False),  # up
                        SelectableMenu._dist_in_direction(yi, yj,
                                                          True),  # down
                        SelectableMenu._dist_in_direction(xi, xj,
                                                          False),  # left
                        SelectableMenu._dist_in_direction(xi, xj,
                                                          True),  # right
                    ]
                    dists: list[float] = [
                        SelectableMenu._dist_in_direction_wrapped(
                            yi, yj, False, ymin, ymax),  # up
                        SelectableMenu._dist_in_direction_wrapped(
                            yi, yj, True, ymin, ymax),  # down
                        SelectableMenu._dist_in_direction_wrapped(
                            xi, xj, False, xmin, xmax),  # left
                        SelectableMenu._dist_in_direction_wrapped(
                            xi, xj, True, xmin, xmax),  # right
                    ]
                    # for each direction (up, down, left, right)
                    for dir_ in range(4):
                        if closest_delta_dir[dir_] is None or dists_dir[
                                dir_] < closest_delta_dir[dir_]:
                            # no update if distance is 0 (aligned selectables)
                            if dists_dir[dir_] != 0:
                                closest_i_dir[dir_] = j
                                closest_delta_dir[dir_] = dists_dir[dir_]
                        if closest_delta[dir_] is None or abs(
                                dists[dir_]) < abs(closest_delta[dir_]):
                            # no update if distance is 0 (aligned selectables)
                            if dists[dir_] != 0:
                                closest_i[dir_] = j
                                closest_delta[dir_] = dists[dir_]
                    # When no directionnal neighbour was found, consider wrapped ones
                    for dir_ in range(4):
                        if closest_delta_dir[dir_] is None:
                            closest_i_dir[dir_] = closest_i[dir_]
            #print(f"{i} => closest_delta:     {closest_delta}")
            # assign the index of the closest neighbours to the current one
            neighbours[i] = closest_i_dir
            # inversely, if j is closest above i, then i is closest below j
            # except when neighbours were already assigned
            symmetry = [
                (0, 1),  # up to down
                (1, 0),  # down to up
                (2, 3),  # left to right
                (3, 2),  # right to left
            ]
            for (dir_, inv_dir) in symmetry:
                if neighbours[
                        closest_i_dir[dir_]][inv_dir] == closest_i_dir[dir_]:
                    neighbours[closest_i_dir[dir_]][inv_dir] = i
        return neighbours

    @staticmethod
    def _dist_in_direction(a: float, b: float, left_to_right: bool) -> float:
        """
        Returns the distance from selectable i to j in the direction `left_to_right`.
        Returns 0.0 when the distance is infinite.
        """
        if not left_to_right:
            a, b = b, a
        return b - a if a < b else 0.0

    @staticmethod
    def _dist_in_direction_wrapped(a: float, b: float, left_to_right: bool,
                                   min_: float, max_: float) -> float:
        """
        Returns the distance from selectable i to j in the direction `left_to_right`,
        wrapping around the bounds.
        Returns 0.0 when the distance is infinite.
        """
        dist = b - a
        if left_to_right:
            if dist < 0:
                dist += max_ - min_
            else:
                dist = 0.0
        else:
            if dist > 0:
                dist -= max_ - min_
            else:
                dist = 0.0
        return abs(dist)

    def set_selectable_callback(self, i: int, callback, *args):
        """
        Enables retroactively adding a callback to a selectable (enables
        giving it menu main loop queue access for example).
        """
        self._selectables[i].set_callback(callback, *args)

    def queue_cmd(self, cmd):
        self._main_loop_queue.put(cmd)

    def close_threads(self, skip_tabs: bool = False):
        # Waits for all selectables to be done with their running threads
        all_threads_closed = False
        while not all_threads_closed:
            all_threads_closed = True
            for selectable in self._selectables:
                if selectable.is_running():
                    selectable.queue_cmd(("exit"))
                    all_threads_closed = False
                    break
        if not skip_tabs:
            for tab in self._tabs.get_tabs():
                tab.hide()

    def main_loop(self, term: Terminal):
        inp = None
        choice = 0
        for i in range(len(self._selectables)):
            self._selectables[i].select(i == choice)
            self._selectables[i].render(term)

        with term.cbreak(), term.hidden_cursor():
            while True:
                # check main loop queue for cmds from threads
                if not self._main_loop_queue.empty():
                    cmd = self._main_loop_queue.get()
                    match cmd:
                        case ("exit"):
                            self.close_threads()
                            return True

                inp = term.inkey(timeout=0.1)

                if inp == "":
                    pass
                elif inp.name == "KEY_ESCAPE":
                    self.close_threads(skip_tabs=True)
                    self._log.info(term.bold_green("Cancelled running tasks."))
                elif inp.name == "KEY_ENTER":
                    self._selectables[choice].run(term,
                                                  wait_for_callback=False)
                else:
                    self._selectables[choice].select(False)
                    self._selectables[choice].render(term)
                    if inp.name == "KEY_UP":
                        choice = self._neighbours[choice][0]
                    if inp.name == "KEY_DOWN":
                        choice = self._neighbours[choice][1]
                    if inp.name == "KEY_LEFT":
                        choice = self._neighbours[choice][2]
                    if inp.name == "KEY_RIGHT":
                        choice = self._neighbours[choice][3]
                    self._selectables[choice].select(True)
                    self._selectables[choice].render(term)
