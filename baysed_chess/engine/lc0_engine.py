import chess
import chess.engine

from baysed_chess.engine.i_engine import IEngine
from baysed_chess.limit import Limit


class Lc0Engine(IEngine):
    def __init__(self, board: chess.Board, color: chess, path: str):
        super().__init__(board, color, None)
        self.lc0 = chess.engine.SimpleEngine.popen_uci(path)

    def __del__(self):
        self.lc0.quit()

    def play(self, board: chess.Board, limit: Limit) -> chess.engine.PlayResult:
        return self.lc0.play(board, limit.translate_to_engine_limit())

    @staticmethod
    def get_name() -> str:
        return "Lc0"
