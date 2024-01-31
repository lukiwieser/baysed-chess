import random
from abc import ABC, abstractmethod
from typing import Self

import chess

from chesspp.i_strategy import IStrategy


class IMctsNode(ABC):
    def __init__(self, board: chess.Board, strategy: IStrategy, parent: Self | None, move: chess.Move | None,
                 random_state: random.Random):
        self.board = board
        self.strategy = strategy
        self.parent = parent
        self.children = []
        self.move = move
        self.legal_moves = list(board.legal_moves)
        self.random_state = random_state

    @abstractmethod
    def select(self) -> Self:
        """
        Selects the next node leaf node in the tree
        :return:
        """
        pass

    @abstractmethod
    def expand(self) -> Self:
        """
        Expands this node creating X child leaf nodes, i.e., choose an action and apply it to the board
        :return:
        """
        pass

    @abstractmethod
    def rollout(self, rollout_depth: int = 20) -> int:
        """
        Rolls out the node by simulating a game for a given depth.
        Sometimes this step is called 'simulation' or 'playout'.
        :return: the score of the rolled out game
        """
        pass

    @abstractmethod
    def backpropagate(self, score: float | None = None) -> None:
        """
        Backpropagates the results of the rollout
        :param score:
        :return:
        """
        pass

    def update_depth(self, depth: int) -> None:
        """
        Recursively updates the depth the current node and all it's children
        :param depth: new depth for current node
        :return:
        """
