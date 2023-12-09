import chess
import chess.pgn
import collections
import logging

# from stockfish import Stockfish
from launchpad_game import LaunchPadGame
from pygame.time import wait
from helpers import *
from datetime import datetime
from constants import *


# This class basically handles which squares are selected
# It then converts those (using raw input from the LaunchPad class)
# into game commands that the python chess library can use
class Game:
    def __init__(self):
        self.launchpad = LaunchPadGame()
        self.board = chess.Board()  # Manages the game itself

        # engine = Stockfish() This is for analytics later

        self.selected_square = None
        self.valid_moves = None
        self.start_game()

    def start_game(self):
        self.launchpad.start_new_game()
        self.board.reset()
        while True:
            event = self.launchpad.poll_for_event()
            if event:
                self.process_touch_event(event)

    # This takes a touch input on a square, updates the selected square
    # And makes the move if it is valid
    def process_touch_event(self, event):
        square = launchpad_to_uci(event)
        if event == 60:  # Player pressed the undo button
            logging.info("Undo button pressed")
            try:
                last_move = str(self.board.pop())
                self.launchpad.light_square(last_move[2:], RED)
                self.launchpad.light_square(last_move[:-2], RED)
                wait(3000)
                # self.launchpad.reset()
                self.launchpad.set_player_indicator(self.board.turn)
            except IndexError:
                logging.warning(
                    "Don't click the undo button if there aren't moves to undo"
                )
        elif event == 30:  # Player pressed the new game button
            logging.info("New game button pressed")
            self.start_game()

        # Player is selecting a square to make a move
        elif not self.selected_square:
            self._select_square(square)

        # Player made a valid move
        elif square in self.valid_moves:
            move_from = self.selected_square
            self._unselect_square(move_from)
            self.launchpad.light_square(square, PURPLE)

            all_moves = [str(move) for move in self.board.legal_moves]
            if (move_from + square + "q") in all_moves:
                self.board.push(chess.Move.from_uci(move_from + square + "q"))
            else:
                self.board.push(chess.Move.from_uci(move_from + square))
            wait(1000)
            self.launchpad.reset_square(square)
            self.update_status()

        elif square == self.selected_square:
            self._unselect_square(square)

        else:  # This is not a valid move
            print(square)
            print(self.valid_moves)
            self._blink_square(square, RED, YELLOW)

    def _unselect_square(self, square):
        if square != self.selected_square:
            logging.error(f"Cannot unselect {square}, it is not selected!")
            return

        valid_moves = set(
            str(move)[2:]
            for move in self.board.legal_moves
            if str(move).startswith(square)
        )  # These are the possible places that the piece on the selected square can move

        for move_square in valid_moves:
            self.launchpad.reset_square(move_square)
        self.launchpad.reset_square(square)
        logging.info(f"Unselecting {square}")
        self.update_status()
        self.selected_square = None

    def _select_square(self, square):
        if square == self.selected_square:
            logging.error(f"Cannot select {square}, it is already selected!")
            return

        valid_moves = set(
            str(move)[2:4]
            for move in self.board.legal_moves
            if str(move).startswith(square)
        )  # These are the possible places that the piece on the selected square can move

        if not valid_moves:
            logging.info(f"No valid moves from {square}, ignoring input")
            return

        logging.info(f"Selected square is {square}")
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

        self.launchpad.reset_square(square)

    def update_status(self):
        print(f"STALEMATE: {self.board.is_stalemate()}")
        print(f"INSUF MATERIAL DRAW: {self.board.is_insufficient_material()}")
        print(f"OUTCOME: {self.board.outcome()}")

        # Light up king with Yellow
        if self.board.is_check():
            if self.board.turn:  # White players turn
                king_square_index = self.board.king(chess.WHITE)
                king_square_name = chess.square_name(king_square_index)
                self.launchpad.light_square(king_square_name, YELLOW)
            else:
                king_square_index = self.board.king(chess.BLACK)
                king_square_name = chess.square_name(king_square_index)
                self.launchpad.light_square(king_square_name, YELLOW)
        else:
            king_square_index = self.board.king(chess.WHITE)
            king_square_index_b = self.board.king(chess.BLACK)
            self._unselect_square(king_square_index)
            self._unselect_square(king_square_index_b)

        outcome = self.board.outcome()
        if outcome:
            if outcome.winner == chess.WHITE:
                king_square_index = self.board.king(chess.BLACK)
                king_square_name = chess.square_name(king_square_index)
                self.launchpad.light_square(king_square_name, RED)
                self.launchpad.set_winner_lights(white=True)

            if outcome.winner == chess.BLACK:
                king_square_index = self.board.king(chess.WHITE)
                king_square_name = chess.square_name(king_square_index)
                self.launchpad.light_square(king_square_name, RED)
                self.launchpad.set_winner_lights(white=False)

            # Stalemate
            if outcome.winner is None:
                self.launchpad.set_winner_lights(stalemate=True)

            self.launchpad.reset_player_indicator()
            game = self.get_game_pgn()
            with open(f"{OUTPUT_DIR}/{datetime.now().isoformat()}.pgn", "w") as pgn:
                pgn.write(str(game))

        else:
            self.launchpad.set_player_indicator(self.board.turn)

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
