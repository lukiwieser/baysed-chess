import chess
import chess.engine
from stockfish import Stockfish

from baysed_chess.engine.i_engine import IEngine
from baysed_chess.limit import Limit


class StockfishEngine(IEngine):
    """Engine that plays using the `stockfish` engine"""

    def __init__(self, board: chess.Board, color: chess, stockfish_elo: int | None, path: str):
        super().__init__(board, color, None)
        self.stockfish = Stockfish(path)
        if stockfish_elo is not None:
            self.stockfish.set_elo_rating(stockfish_elo)

    def play(self, board: chess.Board, limit: Limit) -> chess.engine.PlayResult:
        self.stockfish.set_fen_position(board.fen())
        m = chess.Move.from_uci(self.stockfish.get_best_move())
        return chess.engine.PlayResult(move=m, ponder=None)

    @staticmethod
    def get_name() -> str:
        return "Stockfish"
