import chess
from chesspp.strategies.i_strategy import IStrategy
from chesspp.board_evaluations.evaluate_stockfish import score_stockfish
import chess.engine


class StockFishStrategy(IStrategy):

    def __init__(self, path="../stockfish/stockfish-windows-x86-64-avx2", rollout_depth: int = 4,
                 limit: chess.engine.Limit = chess.engine.Limit(depth=4)):
        super().__init__(rollout_depth)
        self._stockfish = None
        self.path = path
        self.limit = limit

    def __del__(self):
        if self._stockfish is not None:
            self._stockfish.quit()

    @property
    def stockfish(self) -> chess.engine.SimpleEngine:
        if self._stockfish is None:
            self._stockfish = self.stockfish = chess.engine.SimpleEngine.popen_uci(self.path)
        return self._stockfish

    @stockfish.setter
    def stockfish(self, stockfish):
        self._stockfish = stockfish

    def pick_next_move(self, board: chess.Board) -> chess.Move | None:
        return self.stockfish.play(board, self.limit).move

    def analyze_board(self, board: chess.Board) -> int:
        return score_stockfish(board, self.stockfish)
