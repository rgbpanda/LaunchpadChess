import logging

import launchpad_py as launchpad
from helpers import uci_to_launchpad
from pygame.time import wait

BLACK_SPACES = [
    int(str(x) + str(y))
    for x in range(1, 9)
    for y in range(1, 9)
    if (y % 2 == 0 and x % 2 == 0) or (y % 2 != 0 and x % 2 != 0)
]
BLACK_SPACE_COLOR = (0, 0, 30)


WHITE_SPACES = [
    int(str(x) + str(y))
    for x in range(1, 9)
    for y in range(1, 9)
    if int(str(x) + str(y)) not in BLACK_SPACES
]
WHITE_SPACE_COLOR = (5, 5, 3)


class Launchpad:
    def __init__(self):
        self.lp = launchpad.Launchpad()
        if self.lp.Check(0):
            self.lp = launchpad.LaunchpadPro()
            if self.lp.Open(0):
                logging.info("Launchpad Pro Initialized")
            else:
                raise Exception(message="ERROR: Failed to initialize launchpad")

        self.reset()

    def reset(self):
        self.lp.Reset()
        self._create_checkerboard()
        self.modified_spaces = []

    def reset_space(self, space):
        if space in self.modified_spaces:
            self._set_unmodified(space)

        if space in WHITE_SPACES:
            self._light_space(space, WHITE_SPACE_COLOR)
        elif space in BLACK_SPACES:
            self._light_space(space, BLACK_SPACE_COLOR)

    def reset_spaces(self, spaces):
        for space in spaces:
            if space in WHITE_SPACES:
                self._light_space(space, WHITE_SPACE_COLOR)
            elif space in BLACK_SPACES:
                self._light_space(space, BLACK_SPACE_COLOR)
        self.modified_spaces = []

    def poll_for_event(self):
        events = self.lp.ButtonStateRaw(returnPressure=True)
        if events != [] and events[0] != 255 and events[1] > 0:
            return events[0]

    def _create_checkerboard(self):
        for space in BLACK_SPACES:
            self._light_space(space, BLACK_SPACE_COLOR)

        for space in WHITE_SPACES:
            self._light_space(space, WHITE_SPACE_COLOR)

    def _light_space(self, space, color):
        self.lp.LedCtrlRaw(space, color[0], color[1], color[2])

    # Chess square is a string representing the chess square i.e. "a8"
    # Color is a tuple containing the RGB values to set that square
    def set_color_raw(self, space, color):
        self._light_space(space, color)
        self._set_modified(space)

    # Chess square is a string representing the chess square i.e. "a8"
    # Color is a tuple containing the RGB values to set that square
    def set_color_uci(self, uci, color):
        # TODO: Add more validation
        if int(uci[1]) > 8 or int(uci[1]) < 1:
            logging.error(f"Invalid uci: {uci}, cannot set sqaure color")

        space = uci_to_launchpad(uci)
        self.set_color_raw(space, color)

    def _set_modified(self, space):
        self.modified_spaces.append(space)

    def _set_unmodified(self, space):
        if space in self.modified_spaces:
            self.modified_spaces.remove(space)


launchpad = Launchpad()
