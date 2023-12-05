import chess
import logging

# from stockfish import Stockfish
from launchpad import LaunchPad
from pygame.time import wait

ORANGE = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
PURPLE = (255, 0, 255)


# This class basically handles which squares are selected
# It then converts those (using raw input from the LaunchPad class)
# into game commands that the python chess library can use
class Game:
    def __init__(self):
        self.launchpad = LaunchPad()
        self.board = chess.Board()  # Manages the game itself

        # engine = Stockfish() This is for analytics later

        self.selected_square = None
        self.valid_moves = None

        while True:
            event = self.launchpad.poll_for_event()
            if event:
                self.process_touch_event(event)

    # This takes a touch input on a square, updates the selected square
    # And makes the move if it is valid
    def process_touch_event(self, square):
        if square == "`6":  # Player pressed the undo button
            print("undo button pressed")
            try:
                last_move = str(self.board.pop())
                self.launchpad.light_square(last_move[2:], RED)
                self.launchpad.light_square(last_move[:-2], RED)
                wait(3000)
                self.launchpad.reset()
                self.launchpad.set_player_indicator(self.board.turn)
            except IndexError:
                logging.warning(
                    "Don't click the undo button if there aren't moves to undo"
                )

        # Player is selecting a square to make a move
        elif not self.selected_square:
            self._select_square(square)

        # Player made a valid move
        elif square in self.valid_moves:
            self.launchpad.reset()
            self.launchpad.light_square(square, PURPLE)
            self.board.push(chess.Move.from_uci(self.selected_square + square))
            self.selected_square = None
            wait(1000)
            self.launchpad.reset()
            self.launchpad.set_player_indicator(self.board.turn)

        elif square == self.selected_square:
            self._unselect_square(square)

        else:  # This is not a valid move
            self._blink_square(square, RED, YELLOW)

    def _unselect_square(self, square):
        if square != self.selected_square:
            logging.error(f"Cannot unselect {square}, it is not selected!")
            return

        logging.info(f"Unselecting {square}")
        self.launchpad.reset()
        self.selected_square = None

    def _select_square(self, square):
        if square == self.selected_square:
            logging.error(f"Cannot select {square}, it is already selected!")
            return

        valid_moves = set(
            str(move)[2:]
            for move in self.board.legal_moves
            if str(move).startswith(square)
        )  # These are the possible places that the piece on the selected square can move

        if not valid_moves:
            logging.info(f"No valid moves from {square}, ignoring input")
            return

        logging.info(f"Selected square is {square}")
        self.launchpad.reset()
        self.selected_square = square
        self.launchpad.light_square(square, ORANGE)

        self.valid_moves = valid_moves
        for move_square in valid_moves:
            self.launchpad.light_square(move_square, GREEN)

    def _blink_square(self, square, color1, color2, blinks=2):
        for _ in range(0, blinks):
            self.launchpad.light_square(square, color1)
            wait(100)
            self.launchpad.light_square(square, color2)
            wait(100)

        self.launchpad.light_square(square)
