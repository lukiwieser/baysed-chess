import random

import chess
import chess.engine

from chesspp.strategies.i_strategy import IStrategy
from chesspp.board_evaluations.evaluate_stockfish import score_stockfish


class RandomStockfishStrategy(IStrategy):
    def __init__(self, rollout_depth: int, path="../stockfish/stockfish-windows-x86-64-avx2",
                 random_seed: random.Random = random.Random()) -> None:
        super().__init__(rollout_depth)
        self._stockfish = None
        self.path = path
        self.random_seed = random_seed

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

    def pick_next_move(self, board: chess.Board) -> chess.Move:
        return self.random_seed.choice(list(board.legal_moves))

    def analyze_board(self, board: chess.Board) -> int:
        return score_stockfish(board, self.stockfish)
