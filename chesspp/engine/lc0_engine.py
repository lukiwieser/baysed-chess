import chess
import chess.engine

from chesspp.limit import Limit
from chesspp.engine.i_engine import IEngine


class Lc0Engine(IEngine):
    def __init__(self, board: chess.Board, color: chess, path="../lc0/lc0"):
        super().__init__(board, color, None)
        self.lc0 = chess.engine.SimpleEngine.popen_uci(path)

    def play(self, board: chess.Board, limit: Limit) -> chess.engine.PlayResult:
        return self.lc0.play(board, limit.translate_to_engine_limit())

    @staticmethod
    def get_name() -> str:
        return "Lc0"
