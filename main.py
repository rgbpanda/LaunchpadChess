import chess
import logging

# from stockfish import Stockfish
from launchpad_board import LaunchPadBoard

launchpad = LaunchPadBoard()
# engine = Stockfish()
board = chess.Board()

ORANGE = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)


def light_valid_moves(square):
    for move in board.legal_moves:
        move = str(move)
        if move.startswith(square):
            launchpad.light_square(move[2:], GREEN)


last_event = None
while True:
    event = launchpad.poll_for_event()

    if event and event != last_event:
        logging.info(f"Selected square is {event}")
        launchpad.reset()
        launchpad.light_square(event, ORANGE)
        light_valid_moves(event)
        last_event = event

    elif event and event == last_event:
        logging.info(f"Unselecting {last_event}")
        launchpad.reset()
        last_event = None
