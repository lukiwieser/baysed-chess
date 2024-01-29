import math

import torch.distributions as dist
from chesspp.i_mcts import *
from chesspp.i_strategy import IStrategy
from chesspp.util_gaussian import gaussian_ucb1, max_gaussian, min_gaussian


class BayesianMctsNode(IMctsNode):
    def __init__(self, board: chess.Board, strategy: IStrategy, color: chess.Color, parent: Self | None,
                 move: chess.Move | None,
                 random_state: random.Random, inherit_result: int | None = None, depth: int = 0, visits: int = 0):
        super().__init__(board, strategy, parent, move, random_state)
        self.color = color  # Color of the player whose turn it is
        self.visits = visits
        self.result = inherit_result if inherit_result is not None else 0
        self._set_mu_sigma()
        self.depth = depth

    def _create_child(self, move: chess.Move) -> IMctsNode:
        copied_board = self.board.copy()
        copied_board.push(move)
        return BayesianMctsNode(copied_board, self.strategy, not self.color, self, move, self.random_state, self.result,
                                self.depth + 1)

    def _set_mu_sigma(self) -> None:
        self.mu = self.result
        self.sigma = 1

    def _is_new_ucb1_better(self, current, new) -> bool:
        if self.color == chess.WHITE:
            # maximize ucb1
            return new > current
        else:
            # minimize ubc1
            return new < current

    def _select_best_child(self) -> IMctsNode:
        """
        Returns the child with the *best* ucb1 score.
        It chooses the child with maximum ucb1 for WHITE, and with minimum ucb1 for BLACK.
        """

        if self.board.is_game_over():
            return self

        best_child = self.random_state.choice(self.children)
        best_ucb1 = gaussian_ucb1(best_child.mu, best_child.sigma, self.visits)
        for child in self.children:
            # if child has no visits, prioritize this child.
            if child.visits == 0:
                best_child = child
                break

            # save child if it has a *better* score, than our previous best child.
            ucb1 = gaussian_ucb1(child.mu, child.sigma, self.visits)
            if self._is_new_ucb1_better(best_ucb1, ucb1):
                best_ucb1 = ucb1
                best_child = child

        return best_child

    def update_depth(self, depth: int) -> None:
        self.depth = depth
        for c in self.children:
            c.update_depth(depth + 1)

    def select(self) -> IMctsNode:
        if len(self.children) == 0 or self.board.is_game_over():
            return self

        return self._select_best_child().select()

    def expand(self) -> IMctsNode:
        if self.visits == 0:
            return self

        for move in self.legal_moves:
            self.children.append(self._create_child(move))

        return self._select_best_child()

    def rollout(self, rollout_depth: int = 4) -> int:
        copied_board = self.board.copy()
        steps = self.depth
        for i in range(rollout_depth):
            if copied_board.is_game_over():
                break

            m = self.strategy.pick_next_move(copied_board)
            if m is None:
                break

            copied_board.push(m)
            steps += 1

        steps = max(1, steps)
        score = int(self.strategy.analyze_board(copied_board) / (math.log2(steps) + 1))
        self.result = score
        return score

    def _combine_gaussians(self, mu1: float, sigma1: float, mu2: float, sigma2: float) -> tuple[float, float]:
        if self.color == chess.WHITE:
            return max_gaussian(mu1, sigma1, mu2, sigma2)
        else:
            return min_gaussian(mu1, sigma1, mu2, sigma2)

    def backpropagate(self, score: int | None = None) -> None:
        self.visits += 1

        if score is not None:
            self.result = score

        if len(self.children) == 0:
            # leaf node
            self._set_mu_sigma()
        else:
            # interior node
            shuffled_children = self.random_state.sample(self.children, len(self.children))
            mu = shuffled_children[0].mu
            sigma = shuffled_children[0].sigma
            for c in shuffled_children[1:]:
                mu, sigma = self._combine_gaussians(mu, sigma, c.mu, c.sigma)

            # if max_sigma == 0:
            #     max_sigma = 0.001
            self.mu = mu
            self.sigma = sigma

        if self.parent:
            self.parent.backpropagate()

    def print(self, indent=0):
        print("\t" * indent + f"move={self.move}, visits={self.visits}, mu={self.mu}, sigma={self.sigma}")
        for c in self.children:
            c.print(indent + 1)


class BayesianMcts(IMcts):

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

    def get_children(self) -> list[IMctsNode]:
        return self.root.children

    def get_moves(self) -> Dict[chess.Move, dist.Normal]:
        res = {}
        for c in self.root.children:
            res[c.move] = dist.Normal(c.mu, c.sigma)
        return res

    def print(self):
        print("================================")
        self.root.print()
