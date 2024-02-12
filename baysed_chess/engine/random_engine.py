import random

import chess
import chess.engine

from chesspp.limit import Limit
from chesspp.engine.i_engine import IEngine
from chesspp.strategies.i_strategy import IStrategy


class RandomEngine(IEngine):
    def __init__(self, board: chess.Board, color: chess.Color, strategy: IStrategy):
        super().__init__(board, color, strategy)

    @staticmethod
    def get_name() -> str:
        return "RandomEngine"

    def play(self, board: chess.Board, limit: Limit) -> chess.engine.PlayResult:
        move = random.choice(list(board.legal_moves))
        return chess.engine.PlayResult(move=move, ponder=None)
