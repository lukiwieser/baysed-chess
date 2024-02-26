import chess
import chess.engine

from baysed_chess.board_evaluations.evaluate_lc0 import score_lc0
from baysed_chess.strategies.i_strategy import IStrategy


class Lc0Strategy(IStrategy):
    """
    Play the rollout with lc0.
    Evaluate the terminal state with lc0.
    """

    def __init__(self, path: str, rollout_depth: int = 4):
        super().__init__(rollout_depth)
        self._lc0 = None
        self.path = path
        self.limit = chess.engine.Limit(depth=4)

    def __del__(self):
        if self._lc0 is not None:
            self._lc0.quit()

    @property
    def lc0(self) -> chess.engine.SimpleEngine:
        if self._lc0 is None:
            self._lc0 = self.lc0 = chess.engine.SimpleEngine.popen_uci(self.path)
        return self._lc0

    @lc0.setter
    def lc0(self, value):
        self._lc0 = value

    def pick_next_move(self, board: chess.Board) -> chess.Move | None:
        return self.lc0.play(board, self.limit).move

    def analyze_board(self, board: chess.Board) -> int:
        return score_lc0(board, self.lc0)
