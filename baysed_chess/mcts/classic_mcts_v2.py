import chess

from baysed_chess.mcts.classic_mcts_node_v2 import ClassicMctsNodeV2
from baysed_chess.mcts.i_mcts import IMcts
from baysed_chess.mcts.i_mcts_node import IMctsNode
from baysed_chess.strategies.i_strategy import IStrategy


class ClassicMctsV2(IMcts):
    """
    Implementation of our Classic MCTS, focused on chess.
    """

    def __init__(self, board: chess.Board, color: chess.Color, strategy: IStrategy, seed: int | None = None):
        super().__init__(board, strategy, seed)
        self.color = color
        self.root = ClassicMctsNodeV2(board, color, strategy, None, None, self.random_state)

    def apply_move(self, move: chess.Move) -> None:
        # TODO: Add implementation for apply move, and benchmark the changes, to see if they make a difference.
        pass

    def get_children(self) -> list[IMctsNode]:
        return self.root.children

    def sample(self, samples: int = 1000):
        for i in range(samples):
            node = self.root.select().expand()
            score = node.rollout()
            node.backpropagate(score)
