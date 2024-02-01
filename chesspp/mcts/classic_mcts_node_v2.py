import math
import random
from typing import Self

import chess
import numpy as np

from chesspp.i_strategy import IStrategy
from chesspp.mcts.i_mcts_node import IMctsNode


class ClassicMctsNodeV2(IMctsNode):
    def __init__(self, board: chess.Board, color: chess.Color, strategy: IStrategy, parent: Self | None, move: chess.Move | None,
                 random_state: random.Random, depth: int = 0):
        super().__init__(board, strategy, parent, move, random_state)
        self.color = color
        self.parent = parent
        self.move = move
        self.children = []
        self.visits = 0
        self.legal_moves = list(board.legal_moves)
        self.untried_actions = self.legal_moves
        self.score = 0
        self.depth = depth

    def expand(self) -> Self:
        """
        Expands the node, i.e., choose an action and apply it to the board
        :return:
        """
        if self.is_fully_expanded():
            return self

        move = self.random_state.choice(self.untried_actions)
        self.untried_actions.remove(move)
        next_board = self.board.copy()
        next_board.push(move)
        child_node = ClassicMctsNodeV2(next_board, color=not self.color, strategy=self.strategy, parent=self, move=move, depth=self.depth+1, random_state=self.random_state)
        self.children.append(child_node)
        return child_node

    def rollout(self, rollout_depth: int = 4) -> int:
        """
        Rolls out the node by simulating a game for a given depth.
        Sometimes this step is called 'simulation' or 'playout'.
        :return: the score of the rolled out game
        """
        copied_board = self.board.copy()
        steps = self.depth
        for i in range(rollout_depth):
            if copied_board.is_game_over():
                break

            m = self.strategy.pick_next_move(copied_board)
            copied_board.push(m)
            steps += 1

        steps = max(2, steps)
        return int(self.strategy.analyze_board(copied_board) / math.log2(steps))

    def backpropagate(self, score: float | None = None) -> None:
        """
        Backpropagates the results of the rollout
        :param score:
        :return:
        """
        self.visits += 1
        # TODO: maybe use score + num of moves together (a win in 1 move is better than a win in 20 moves)

        if score is not None:
            self.score += score

        if self.parent:
            self.parent.backpropagate(score)

    def is_fully_expanded(self) -> bool:
        return len(self.untried_actions) == 0

    def _best_child(self) -> Self:
        """
        Picks the best child according to our policy
        :return: the best child
        """
        # NOTE: maybe clamp the score between [-1, +1] instead of [-inf, +inf]
        choices_weights = [(c.score / c.visits) + np.sqrt(((2 * np.log(self.visits)) / c.visits))
                           for c in self.children]
        best_child_index = np.argmax(choices_weights) if self.color == chess.WHITE else np.argmin(choices_weights)
        return self.children[best_child_index]

    def select(self) -> Self:
        """
        Selects a leaf node.
        If the node is not expanded is will be expanded.
        :return: Leaf node
        """
        current_node = self
        while not current_node.board.is_game_over():
            if not current_node.is_fully_expanded():
                return current_node
            current_node = current_node._best_child()

        return current_node
