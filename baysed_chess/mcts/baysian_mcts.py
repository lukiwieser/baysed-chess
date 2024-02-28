import chess
import torch.distributions as dist

from baysed_chess.mcts.baysian_mcts_node import BayesianMctsNode
from baysed_chess.mcts.i_mcts import IMcts
from baysed_chess.mcts.i_mcts_node import IMctsNode
from baysed_chess.strategies.i_strategy import IStrategy


class BayesianMcts(IMcts):
    """
    Implementation of our Bayesian MCTS, focused on chess.
    """

    def __init__(self, board: chess.Board, strategy: IStrategy, color: chess.Color, seed: int | None = None):
        super().__init__(board, strategy, seed)
        self.root = BayesianMctsNode(board, strategy, color, None, None, self.random_state, visits=1)
        self.color = color

    def sample(self, runs: int = 1000) -> None:
        for i in range(runs):
            if self.board.is_game_over():
                break

            leaf_node = self.root.select().expand()
            _ = leaf_node.rollout()
            leaf_node.backpropagate()

    def apply_move(self, move: chess.Move) -> None:
        self.board.push(move)
        self.color = self.board.turn

        # if a child node contains the move, set this child as new root
        for child in self.get_children():
            if child.move == move:
                self.root = child
                child.depth = 0
                self.root.parent = None
                self.root.update_depth(0)
                self.root.visits = 1
                return

        # if no child node contains the move, initialize a new tree.
        self.root = BayesianMctsNode(self.board, self.root.strategy, self.color, None, None, self.random_state, visits=1)

    def get_children(self) -> list[BayesianMctsNode]:
        return self.root.children

    def get_moves(self) -> dict[chess.Move, dist.Normal]:
        res = {}
        for c in self.root.children:
            res[c.move] = dist.Normal(c.mu, c.sigma)
        return res

    def print(self):
        print("================================")
        self.root.print()
