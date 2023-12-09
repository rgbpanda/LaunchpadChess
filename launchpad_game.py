import logging

from helpers import *
from pygame.time import wait
from launchpad import Launchpad

logging.basicConfig(level=logging.INFO)

UNDO_BUTTON = ()
WHITE_TURN_BUTTON = 19
BLACK_TURN_BUTTON = 89


BLACKs_WIN_LIGHTS = [59, 69, 79, 89]
WHITE_WIN_LIGHTS = [19, 29, 39, 49]


"""
This class represents low level functions needed to receive input
and set a specific square to a color, or reset the board
"""


class LaunchPadGame:
    def __init__(self):
        self.default_colors = {}
        self.launchpad = Launchpad()

    def start_new_game(self):
        self.launchpad.reset()
        self._set_default_lights()
        self.set_player_indicator()

    def poll_for_event(self):
        self.launchpad.poll_for_event()

    def reset_player_indicator(self):
        self._set_color_raw(WHITE_TURN_BUTTON, OFF)
        self._set_color_raw(BLACK_TURN_BUTTON, OFF)

    def set_player_indicator(self, white=True, off=False):
        self._set_color_raw(BLACK_TURN_BUTTON, OFF)
        self._set_color_raw(WHITE_TURN_BUTTON, OFF)

        if white and not off:
            self._set_color_raw(WHITE_TURN_BUTTON, RED)
        elif not off:
            self._set_color_raw(BLACK_TURN_BUTTON, RED)

    def set_winner_lights(self, white=True, stalemate=False):
        self.set_player_indicator(off=True)
        if not stalemate:
            winner_lights = WHITE_WIN_LIGHTS if white else BLACKs_WIN_LIGHTS
            for light in winner_lights:
                self.launchpad.se
                self._set_color_raw(light, GREEN)
        else:
            for light in WHITE_WIN_LIGHTS + BLACKs_WIN_LIGHTS:
                self._set_color_raw(light, YELLOW)

    # # Set color using notation to this library (not chess notation)
    # # Useful for squares outside of the chess board (like player indicators)
    # def _set_color_raw(self, space, color):
    #     self.lp.LedCtrlXY(space[0], space[1], color[0], color[1], color[2])
    #     wait(5)
    #     self.lp.LedCtrlXY(space[0], space[1], color[0], color[1], color[2])
    #     wait(5)
    #     self.lp.LedCtrlXY(space[0], space[1], color[0], color[1], color[2])
