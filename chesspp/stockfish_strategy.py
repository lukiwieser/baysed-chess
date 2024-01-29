import os
import chess
from chesspp.i_strategy import IStrategy
from chesspp.eval import score_stockfish
import chess.engine

_DIR = os.path.abspath(os.path.dirname(__file__))


class StockFishStrategy(IStrategy):

    def __init__(self, path="../stockfish/stockfish-windows-x86-64-avx2"):
        self._stockfish = None
        self.path = path

    def __del__(self):
        if self._stockfish is not None:
            self._stockfish.quit()

    @property
    def stockfish(self) -> chess.engine.SimpleEngine:
        if self._stockfish is None:
            self._stockfish = self.stockfish = chess.engine.SimpleEngine.popen_uci(
                os.path.join(_DIR, self.path))
        return self._stockfish

    @stockfish.setter
    def stockfish(self, stockfish):
        self._stockfish = stockfish

    def pick_next_move(self, board: chess.Board) -> chess.Move | None:
        return self.stockfish.play(board, chess.engine.Limit(depth=4)).move

    def analyze_board(self, board: chess.Board) -> int:
        return score_stockfish(board, self.stockfish)
