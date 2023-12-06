import logging

from helpers import *
from pygame.time import wait
from launchpad import Launchpad

logging.basicConfig(level=logging.INFO)

UNDO_BUTTON = ()
WHITE_TURN_BUTTON = (8, 8)
BLACK_TURN_BUTTON = (8, 1)


BLACKs_WIN_LIGHTS = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0)]
WHITE_WIN_LIGHTS = [(0, 9), (1, 9), (2, 9), (3, 9), (4, 9), (5, 9), (6, 9), (7, 9)]


"""
This class represents low level functions needed to receive input
and set a specific square to a color, or reset the board
"""


class LaunchPadGame:
    def __init__(self):
        self.default_colors = {}
        self.modified_spaces = []
        self.launchpad = Launchpad()

    def start_new_game(self):
        self.launchpad.reset()
        self._set_default_lights()
        self.set_player_indicator()

    def poll_for_event(self):
        self.launchpad.poll_for_event()

    def light_square(self, uci, color=None):
    #     if not color:
    #         self._set_color_uci(uci, self.default_colors[uci])
    #         if uci in self.modified_spaces:
    #             self.modified_spaces.remove(uci)
    #     else:
    #         self.modified_spaces.append(uci)
    #         self._set_color_uci(uci, color)

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
                self._set_color_raw(light, GREEN)
        else:
            for light in WHITE_WIN_LIGHTS + BLACKs_WIN_LIGHTS:
                self._set_color_raw(light, YELLOW)



    # Set color using notation to this library (not chess notation)
    # Useful for squares outside of the chess board (like player indicators)
    def _set_color_raw(self, space, color):
        self.lp.LedCtrlXY(space[0], space[1], color[0], color[1], color[2])
        wait(5)
        self.lp.LedCtrlXY(space[0], space[1], color[0], color[1], color[2])
        wait(5)
        self.lp.LedCtrlXY(space[0], space[1], color[0], color[1], color[2])
