import chess
import random
from chesspp.strategies.i_strategy import IStrategy
from chesspp.eval import score_manual


class RandomStrategy(IStrategy):
    def __init__(self, random_state: random.Random, rollout_depth: int = 4):
        super().__init__(rollout_depth)
        self.random_state = random_state

    def pick_next_move(self, board: chess.Board) -> chess.Move | None:
        if len(list(board.legal_moves)) == 0:
            return None
        return self.random_state.choice(list(board.legal_moves))

    def analyze_board(self, board: chess.Board) -> int:
        return score_manual(board)
