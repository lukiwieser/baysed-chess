import os
import chess
from chesspp.i_strategy import IStrategy
import chess.engine

_DIR = os.path.abspath(os.path.dirname(__file__))

class StockFishStrategy(IStrategy):

    def __init__(self):
        self._stockfish = None

    @property
    def stockfish(self) -> chess.engine.SimpleEngine:
        if self._stockfish is None:
            self._stockfish = self.stockfish = chess.engine.SimpleEngine.popen_uci(
                os.path.join(_DIR, "../stockfish/stockfish-ubuntu-x86-64-avx2"))
        return self._stockfish

    @stockfish.setter
    def stockfish(self, stockfish):
        self._stockfish = stockfish

    def pick_next_move(self, board: chess.Board) -> chess.Move | None:
        move = self.stockfish.play(board, chess.engine.Limit(depth=4)).move
        print("stockfish picked:", move)
        return move
