import chess
import chess.pgn
import collections

import logging

from datetime import datetime

from constants import *

class Game:
    def __init__(self):
        self.board = chess.Board()

    def reset(self):
        self.board.reset()

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
    
    def attempt_move(self, square):
        # if self.selected_square == None: Handle this in launchpad game
        #     # TODO Raise exception here, this shouldn't be possible
        #     logging.error(f"Attempted to make move to {square} with no square selected")
        #     return

        # self._blink_square(square, RED, YELLOW) # Blink square to show player they cannot move there
        print(square)
        valid = self.get_valid_moves(square)
        print(valid)
        # Player made a valid move
        if square in valid:
            move_from = self.selected_square
            self._unselect_selected_square()
            # self.launchpad.set_color_uci(square, PURPLE)

            all_moves = [str(move) for move in self.board.legal_moves]
            if (move_from + square + "q") in all_moves:
                promotion = self._get_promotion()
                self.board.push(chess.Move.from_uci(move_from + square + promotion))
            else:
                self.board.push(chess.Move.from_uci(move_from + square))
            # wait(1000)
            # self._reset_square(square)
            self.update_status()
            return True
        else:
            return False
        
    def get_valid_moves(self, square):
        for move in self.board.legal_moves:
            valid_moves = []
            print(square)
            if str(move)[0:2] == square:
                valid_moves.append(str(move))
            # print(str(move))
            # print(str(move)[2:4])
        return valid_moves
        # # print(self.board.legal_moves)
        # valid_moves = set(
        #     str(move)[2:4]
        #     for move in self.board.legal_moves
        #     if str(move).startswith(square)
        # )  # These are the possible places that the piece on the selected square can move
        # return valid_moves

    def _get_promotion(self):
            # self.launchpad._set_color_uci("i6", GREEN)
            # self.launchpad._set_color_uci("i5", RED)
            # self.launchpad._set_color_uci("i4", BLUE)
            # self.launchpad._set_color_uci("i3", WHITE)
            selected_promotion = None
            while selected_promotion is None:
                event = self.launchpad.poll_for_event()
                if event is not None:
                    if event == "i6":
                        selected_promotion = "q"
                    if event == "i5":
                        selected_promotion = "r"
                    if event == "i4":
                        selected_promotion = "b"
                    if event == "i3":
                        selected_promotion = "n"
            # self.launchpad._set_color_uci("i6", OFF)
            # self.launchpad._set_color_uci("i5", OFF)
            # self.launchpad._set_color_uci("i4", OFF)
            # self.launchpad._set_color_uci("i3", OFF)
            return selected_promotion