import chess
import chess.engine

from baysed_chess.board_evaluations.evaluate_stockfish import score_stockfish
from baysed_chess.strategies.i_strategy import IStrategy


class StockfishStrategy(IStrategy):
    """
    Play the rollout with stockfish.
    Evaluate the terminal state with stockfish.
    """

    def __init__(self, path: str, rollout_depth: int = 4):
        super().__init__(rollout_depth)
        self._stockfish = None
        self.path = path
        self.limit = chess.engine.Limit(depth=4)

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
