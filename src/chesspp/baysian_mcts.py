import chess
from src.chesspp.i_mcts import *
from src.chesspp.i_strategy import IStrategy
from src.chesspp.util_gaussian import gaussian_ucb1, max_gaussian, beta_std, beta_mean
from src.chesspp.eval import *
import numpy as np
import math


class BayesianMctsNode(IMctsNode):
    def __init__(self, board: chess.Board, strategy: IStrategy, parent: Self | None, move: chess.Move | None,
                 random_state: random.Random, inherit_results: list[int] | None = None):
        super().__init__(board, strategy, parent, move, random_state)
        self.visits = 0
        self.results = inherit_results.copy() if inherit_results is not None else [1, 1]

        self._set_mu_sigma()

    def _create_child(self, move: chess.Move):
        copied_board = self.board.copy()
        copied_board.push(move)
        return BayesianMctsNode(copied_board, self.strategy, self, move, self.random_state, inherit_results=self.results)

    def _set_mu_sigma(self):
        alpha = self.results[0]
        beta = self.results[1]

        self.mu = beta_mean(alpha, beta)
        self.sigma = beta_std(alpha, beta)

    def _select_child(self) -> IMctsNode:
        # select child by modified UCB1
        if self.board.is_game_over():
            return self

        best_child = self.random_state.choice(self.children)
        best_val = gaussian_ucb1(best_child.mu, best_child.sigma, self.visits)
        for c in self.children:
            g = gaussian_ucb1(c.mu, c.sigma, self.visits)

            if g > best_val:
                best_val = g
                best_child = c
        return best_child

    def select(self) -> IMctsNode:
        if len(self.children) == 0:
            return self
        else:
            return self._select_child().select()

    def expand(self) -> IMctsNode:
        if self.visits == 0:
            return self

        for move in self.legal_moves:
            self.children.append(self._create_child(move))

        return self._select_child()

    def rollout(self, rollout_depth: int = 20) -> int:
        copied_board = self.board.copy()
        steps = 1
        for i in range(rollout_depth):
            if copied_board.is_game_over():
                break

            m = self.strategy.pick_next_move(copied_board)
            if m is None:
                break

            copied_board.push(m)
            steps += 1

        score = eval.score_manual(copied_board) // steps
        if score > 0:
            self.results[1] += 1
        else:
            self.results[0] += abs(score) // 50_000
        return score

    def backpropagate(self, score: int | None = None) -> None:
        self.visits += 1

        if score is not None:
            self.results.append(score)

        if len(self.children) == 0:
            # leaf node
            self._set_mu_sigma()
        else:
            # interior node
            shuffled_children = self.random_state.sample(self.children, len(self.children))
            max_mu = shuffled_children[0].mu
            max_sigma = shuffled_children[0].sigma
            for c in shuffled_children[1:]:
                max_mu, max_sigma = max_gaussian(max_mu, max_sigma, c.mu, c.sigma)

            if max_sigma == 0:
                max_sigma = 0.001
            self.mu = max_mu
            self.sigma = max_sigma

        if self.parent:
            self.parent.backpropagate()

    def print(self, indent=0):
        print("\t"*indent + f"visits={self.visits}, mu={self.mu}, sigma={self.sigma}")
        for c in self.children:
            c.print(indent+1)


class BayesianMcts(IMcts):
    def __init__(self, board: chess.Board, strategy: IStrategy, seed: int | None = None):
        super().__init__(board, strategy, seed)
        self.root = BayesianMctsNode(board, strategy, None, None, self.random_state)
        self.root.visits += 1

    def sample(self, runs: int = 1000) -> None:
        for i in range(runs):
            #print(f"sample {i}")
            leaf_node = self.root.select().expand()
            _ = leaf_node.rollout()
            leaf_node.backpropagate()
            #self.root.print()

    def apply_move(self, move: chess.Move) -> None:
        self.board.push(move)

        # if a child node contains the move, set this child as new root
        for child in self.get_children():
            if child.move == move:
                self.root = child
                self.root.parent = None
                return

        # if no child node contains the move, initialize a new tree.
        self.root = BayesianMctsNode(self.board, self.root.strategy, None, None, self.random_state)

    def get_children(self) -> list[IMctsNode]:
        return self.root.children

    def print(self):
        print("================================")
        self.root.print()