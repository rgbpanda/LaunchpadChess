import chess
import chess.pgn
import collections
import logging

# from stockfish import Stockfish
from launchpad import Launchpad
from pygame.time import wait
from helpers import *
from datetime import datetime
from constants import *


# This class basically handles which squares are selected
# It then converts those (using raw input from the LaunchPad class)
# into game commands that the python chess library can use
class LaunchpadGame:
    def __init__(self):
        self.launchpad = Launchpad()
        self.board = chess.Board()  # Manages the game itself

        # engine = Stockfish() This is for analytics later

        self.selected_square = None
        self.valid_move_squares = []
        self.indicated_squares = [] # For check/checkmate

        self.start_game()

    def start_game(self):
        self.launchpad.reset()
        self.set_player_indicator()
        self.board.reset()
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
            self._attempt_move(square)


    def _unselect_selected_square(self):
        for square in [self.selected_square] + self.valid_move_squares + self.indicated_squares:
            self._reset_square((square)

        logging.info(f"Unselecting {square}")
        self.update_status()
        self.selected_square = None

    def _select_square(self, square):
        valid_moves = self._get_valid_moves(square)
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

        self._reset_square((square)

    def update_status(self):
        print(f"STALEMATE: {self.board.is_stalemate()}")
        print(f"INSUF MATERIAL DRAW: {self.board.is_insufficient_material()}")
        print(f"OUTCOME: {self.board.outcome()}")

        # Light up king with Yellow
        if self.board.is_check():
            if self.board.turn:  # White players turn
                king_square_index = self.board.king(chess.WHITE)
                king_square_name = chess.square_name(king_square_index)
                self.launchpad.set_color_uci(king_square_name, YELLOW)
            else:
                king_square_index = self.board.king(chess.BLACK)
                king_square_name = chess.square_name(king_square_index)
                self.launchpad.set_color_uci(king_square_name, YELLOW)
        else:
            king_square_index = self.board.king(chess.WHITE)
            king_square_index_b = self.board.king(chess.BLACK)
            # self._unselect_square(king_square_index)
            # self._unselect_square(king_square_index_b)

        outcome = self.board.outcome()
        if outcome:
            if outcome.winner == chess.WHITE:
                king_square_index = self.board.king(chess.BLACK)
                king_square_name = chess.square_name(king_square_index)
                self.launchpad.set_color_uci(king_square_name, RED)
                self._set_winner_lights(white=True)

            if outcome.winner == chess.BLACK:
                king_square_index = self.board.king(chess.WHITE)
                king_square_name = chess.square_name(king_square_index)
                self.launchpad.set_color_uci(king_square_name, RED)
                self._set_winner_lights(white=False)

            # Stalemate
            if outcome.winner is None:
                self._set_winner_lights(stalemate=True)

            self._reset_player_indicator()
            game = self.get_game_pgn()
            with open(f"{OUTPUT_DIR}/{datetime.now().isoformat()}.pgn", "w") as pgn:
                pgn.write(str(game))

        else:
            self._set_player_indicator(self.board.turn)

    def get_game_pgn(self):
        board = self.board
        game = chess.pgn.Game()

        # Undo all moves.
        switchyard = collections.deque()
        while board.move_stack:
            switchyard.append(board.pop())

        game.setup(board)
        node = game

        # Replay all moves.
        while switchyard:
            move = switchyard.pop()
            node = node.add_variation(move)
            board.push(move)
        game.headers["Event"] = datetime.now().strftime("%H:%M:%S")
        game.headers["Date"] = datetime.now().strftime("%Y.%m.%d")
        game.headers["Result"] = board.result()
        return game

    def _get_valid_moves(self, square):
        valid_moves = set(
            str(move)[2:4]
            for move in self.board.legal_moves
            if str(move).startswith(square)
        )  # These are the possible places that the piece on the selected square can move
        return valid_moves

    def _undo(self):
        try:
            last_move = str(self.board.pop())
            self.launchpad.set_color_uci(last_move[2:], RED)
            self.launchpad.set_color_uci(last_move[:-2], RED)
            wait(3000)
            self.launchpad.set_player_indicator(self.board.turn)
            self._unselect_selected_square()
        except IndexError:
            logging.warning(
                "Don't click the undo button if there aren't moves to undo"
            )
    
    def _attempt_move(self, square):
        if self.selected_square == None:
            # TODO Raise exception here, this shouldn't be possible
            logging.error(f"Attempted to make move to {square} with no square selected")
            return



        # self._blink_square(square, RED, YELLOW) # Blink square to show player they cannot move there

        # Player made a valid move
        if square in self.valid_moves:
            move_from = self.selected_square
            self._unselect_selected_square()
            self.launchpad.set_color_uci(square, PURPLE)

            all_moves = [str(move) for move in self.board.legal_moves]
            if (move_from + square + "q") in all_moves:
                self.board.push(chess.Move.from_uci(move_from + square + "q"))
            else:
                self.board.push(chess.Move.from_uci(move_from + square))
            wait(1000)
            self._reset_square((square)
            self.update_status()
            return True
        else:
            return False
        
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
