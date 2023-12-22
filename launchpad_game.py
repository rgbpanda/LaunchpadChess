
import logging

# from stockfish import Stockfish
from launchpad import Launchpad
from pygame.time import wait
from helpers import *
from constants import *
from game import Game

# This class basically handles which squares are selected
# It then converts those (using raw input from the LaunchPad class)
# And sends them to the game class which handles the game
# into game commands that the python chess library can use
class LaunchpadGame:
    def __init__(self):
        self.launchpad = Launchpad()
        self.game = Game()

        # engine = Stockfish() This is for analytics later

        self.selected_square = None
        self.valid_move_squares = []
        self.indicated_squares = [] # For check/checkmate

        self.start_game()

    def start_game(self):
        self.launchpad.reset()
        self._set_player_indicator()
        self.game.reset()
        while True:
            event = self.launchpad.poll_for_event()
            if event:
                self.process_touch_event(event)

    # This takes a touch input on a square, updates the selected square
    # And makes the move if it is valid
    def process_touch_event(self, event):
        square = launchpad_to_uci(event)
        if event == UNDO_BUTTON:  # Player pressed the undo button
            logging.info("Undo button pressed")
            self._undo()
        elif event == NEW_GAME_BUTTON:  # Player pressed the new game button
            logging.info("New game button pressed")
            self.start_game()

        # Player is selecting a square to make a move
        elif not self.selected_square:
            self._select_square(square)

        # Player is unselecting an already selected square
        elif square == self.selected_square:
            self._unselect_selected_square()
        
        else: # Attempt to make the move the player of the player
            if self.game.attempt_move(square):
                self._unselect_selected_square()
            else:
                self._blink_square(square, RED, YELLOW)



    def _unselect_selected_square(self):
        for square in [self.selected_square] + self.valid_move_squares + self.indicated_squares:
            self._reset_square(square)

        logging.info(f"Unselecting {square}")
        self.update_status()
        self.selected_square = None

    def _select_square(self, square):
        valid_moves = self.game.get_valid_moves(square)
        if not valid_moves:
            logging.info(f"No valid moves from {square}, ignoring input")
            return

        logging.info(f"Selected square is {square}")
        self.selected_square = square
        self.launchpad.set_color_uci(square, ORANGE)

        self.valid_moves = valid_moves
        for move_square in valid_moves:
            self.launchpad.set_color_uci(move_square, GREEN)

    def _blink_square(self, square, color1, color2, blinks=2):
        for _ in range(0, blinks):
            self.launchpad.set_color_uci(square, color1)
            wait(100)
            self.launchpad.set_color_uci(square, color2)
            wait(100)

        self._reset_square(square)

    def _undo(self):
        try:
            last_move = str(self.board.pop())
            self.launchpad.set_color_uci(last_move[2:], RED)
            self.launchpad.set_color_uci(last_move[:-2], RED)
            wait(3000)
            self._set_player_indicator(self.board.turn)
            self._unselect_selected_square()
        except IndexError:
            logging.warning(
                "Don't click the undo button if there aren't moves to undo"
            )
        
    def _reset_player_indicator(self):
        self.launchpad.set_color_raw(WHITE_TURN_BUTTON, OFF)
        self.launchpad.set_color_raw(BLACK_TURN_BUTTON, OFF)

    def _set_player_indicator(self, white=True, off=False):
        self.launchpad.set_color_raw(BLACK_TURN_BUTTON, OFF)
        self.launchpad.set_color_raw(WHITE_TURN_BUTTON, OFF)

        if white and not off:
            self.launchpad.set_color_raw(WHITE_TURN_BUTTON, RED)
        elif not off:
            self.launchpad.set_color_raw(BLACK_TURN_BUTTON, RED)

    def _set_winner_lights(self, white=True, stalemate=False):
        self._set_player_indicator(off=True)
        if not stalemate:
            winner_lights = WHITE_WIN_LIGHTS if white else BLACKs_WIN_LIGHTS
            for light in winner_lights:
                self.launchpad.set_color_raw(light, GREEN)
        else:
            for light in WHITE_WIN_LIGHTS + BLACKs_WIN_LIGHTS:
                self.launchpad.set_color_raw(light, YELLOW)

    def _reset_square(self, square):
        launchpad_square = uci_to_launchpad(square)
        self.launchpad.reset_space(launchpad_square)
