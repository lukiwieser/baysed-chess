import random

import chess

from baysed_chess.board_evaluations.evaluate_michniewsk import score_michniewsk
from baysed_chess.strategies.i_strategy import IStrategy


class RandomStrategy(IStrategy):
    """
    Play the rollout randomly.
    Evaluate the terminal state with a simple board evaluation by Tomasz Michniewski.
    """

    def __init__(self, random_state: random.Random, rollout_depth: int = 4):
        super().__init__(rollout_depth)
        self.random_state = random_state

    def pick_next_move(self, board: chess.Board) -> chess.Move | None:
        if len(list(board.legal_moves)) == 0:
            return None
        return self.random_state.choice(list(board.legal_moves))

    def analyze_board(self, board: chess.Board) -> int:
        return score_michniewsk(board)
