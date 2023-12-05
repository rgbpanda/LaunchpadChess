import launchpad_py as launchpad
import logging

from helpers import touch_to_uci, uci_to_xy
from pygame.time import wait

logging.basicConfig(level=logging.INFO)

BOARD_WHITE_COLOR = (5, 5, 2)
BOARD_BLACK_COLOR = (0, 0, 10)


class LaunchPadBoard:
    def __init__(self):
        self.lp = launchpad.Launchpad()
        if self.lp.Check(0):
            self.lp = launchpad.LaunchpadPro()
            if self.lp.Open(0):
                logging.info("Launchpad Pro Initialized")
            else:
                raise Exception(message="ERROR: Failed to initialize launchpad")

        self.default_colors = {}
        self.modified_spaces = []

        # Setup all the lights for the chessboard
        self.lp.Reset()
        self._set_default_lights()
        self._set_default_lights()  # Yes this needs to run twice

    def reset(self):
        for space in self.modified_spaces:
            self._set_color_uci(space, self.default_colors[space])
        self.modified_spaces = []

    def poll_for_event(self):
        events = self.lp.ButtonStateRaw(returnPressure=True)

        # release_event is events[1] <= 0
        if events != [] and events[0] != 255 and events[1] > 0:
            return touch_to_uci(events[0])

    def light_square(self, uci, color):
        self.modified_spaces.append(uci)
        self._set_color_uci(uci, color)

    # Chess square is a string representing the chess square i.e. "a8"
    # Color is a tuple containing the RGB values to set that square
    def _set_color_uci(self, uci, color):
        x, y = uci_to_xy(uci)  # Try several times to be sure
        self.lp.LedCtrlXY(x, y, color[0], color[1], color[2])
        wait(5)
        self.lp.LedCtrlXY(x, y, color[0], color[1], color[2])
        wait(5)
        self.lp.LedCtrlXY(x, y, color[0], color[1], color[2])

    def _set_default_lights(self):
        for x in range(1, 9):
            for y in range(1, 9):
                square_touch_event = int(str(x) + str(y))
                uci = touch_to_uci(square_touch_event)
                if (x % 2 == 0 and y % 2 == 0) or (x % 2 != 0 and y % 2 != 0):
                    self.default_colors[uci] = BOARD_BLACK_COLOR
                    self._set_color_uci(uci, BOARD_BLACK_COLOR)
                else:
                    self.default_colors[uci] = BOARD_WHITE_COLOR
                    self._set_color_uci(uci, BOARD_WHITE_COLOR)
