import chess
import chess.engine

from chesspp.engine.i_engine import IEngine
from chesspp.limit import Limit
from chesspp.mcts.classic_mcts import ClassicMcts
from chesspp.strategies.i_strategy import IStrategy


class ClassicMctsEngine(IEngine):
    def __init__(self, board: chess.Board, color: chess.Color, strategy: IStrategy):
        super().__init__(board, color, strategy)
        self.node_counts = []

    @staticmethod
    def get_name() -> str:
        return "ClassicMctsEngine"

    def play(self, board: chess.Board, limit: Limit) -> chess.engine.PlayResult:
        mcts_root = ClassicMcts(board, self.color, self.strategy)
        node_count = 0

        def do():
            nonlocal node_count
            mcts_root.build_tree(1)
            node_count += 1

        limit.run(do)
        self.node_counts.append(node_count)
        best_move = max(mcts_root.children, key=lambda x: x.score).move if board.turn == chess.WHITE else (
            min(mcts_root.children, key=lambda x: x.score).move)
        return chess.engine.PlayResult(move=best_move, ponder=None)
