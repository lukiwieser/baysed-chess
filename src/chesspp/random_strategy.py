import chess
import random
from chesspp.i_strategy import IStrategy


class RandomStrategy(IStrategy):
    def __init__(self, random_state: random.Random):
        self.random_state = random_state

    def pick_next_move(self, board: chess.Board) -> chess.Move | None:
        if len(list(board.legal_moves)) == 0:
            return None
        return self.random_state.choice(list(board.legal_moves))
