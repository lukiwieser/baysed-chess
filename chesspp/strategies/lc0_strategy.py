import chess
import chess.engine
import os

from chesspp.strategies.i_strategy import IStrategy
from chesspp.board_evaluations.evaluate_lc0 import score_lc0

_DIR = os.path.abspath(os.path.dirname(__file__))


class Lc0Strategy(IStrategy):
    def __init__(self, path: str, rollout_depth: int = 4, limit = chess.engine.Limit(depth=4)):
        super().__init__(rollout_depth)
        self._lc0 = None
        self.path = path
        self.limit = limit

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
        score = score_lc0(board, self.lc0)
        return score
