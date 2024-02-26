import chess
import chess.engine

from baysed_chess.engine.i_engine import IEngine
from baysed_chess.limit import Limit
from baysed_chess.mcts.classic_mcts import ClassicMcts
from baysed_chess.strategies.i_strategy import IStrategy


class ClassicMctsEngine(IEngine):
    """Engine that plays using our classic mcts implementation"""

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
