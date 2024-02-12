import chess
import chess.engine

from chesspp.engine.i_engine import IEngine
from chesspp.limit import Limit
from chesspp.mcts.classic_mcts_v2 import ClassicMctsV2
from chesspp.strategies.i_strategy import IStrategy


class ClassicMctsEngineV2(IEngine):
    def __init__(self, board: chess.Board, color: chess.Color, strategy: IStrategy):
        super().__init__(board, color, strategy)
        self.node_counts = []

    @staticmethod
    def get_name() -> str:
        return "ClassicMctsEngine V2"

    def play(self, board: chess.Board, limit: Limit) -> chess.engine.PlayResult:
        mcts = ClassicMctsV2(board, self.color, self.strategy)
        node_count = 0

        def do():
            nonlocal node_count
            mcts.sample(1)
            node_count += 1

        limit.run(do)
        self.node_counts.append(node_count)
        best_move = max(mcts.root.children, key=lambda x: x.score).move if board.turn == chess.WHITE else (
            min(mcts.root.children, key=lambda x: x.score).move)
        return chess.engine.PlayResult(move=best_move, ponder=None)
