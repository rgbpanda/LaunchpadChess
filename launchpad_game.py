import logging

from helpers import *
from pygame.time import wait
from launchpad import Launchpad
from constants import *

logging.basicConfig(level=logging.INFO)


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
        self.set_player_indicator()

    def poll_for_event(self):
        return self.launchpad.poll_for_event()

    def reset_player_indicator(self):
        self.launchpad.set_color_raw(WHITE_TURN_BUTTON, OFF)
        self.launchpad.set_color_raw(BLACK_TURN_BUTTON, OFF)

    def set_player_indicator(self, white=True, off=False):
        self.launchpad.set_color_raw(BLACK_TURN_BUTTON, OFF)
        self.launchpad.set_color_raw(WHITE_TURN_BUTTON, OFF)

        if white and not off:
            self.launchpad.set_color_raw(WHITE_TURN_BUTTON, RED)
        elif not off:
            self.launchpad.set_color_raw(BLACK_TURN_BUTTON, RED)

    def set_winner_lights(self, white=True, stalemate=False):
        self.set_player_indicator(off=True)
        if not stalemate:
            winner_lights = WHITE_WIN_LIGHTS if white else BLACKs_WIN_LIGHTS
            for light in winner_lights:
                self.launchpad.set_color_raw(light, GREEN)
        else:
            for light in WHITE_WIN_LIGHTS + BLACKs_WIN_LIGHTS:
                self.launchpad.set_color_raw(light, YELLOW)

    def light_square(self, square, color):
        self.launchpad.set_color_uci(square, color)
