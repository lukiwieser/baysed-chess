import random
from abc import ABC, abstractmethod

import chess

from baysed_chess.mcts.i_mcts_node import IMctsNode
from baysed_chess.strategies.i_strategy import IStrategy


class IMcts(ABC):
    """
    Interface for our MCTS (Monte Carlo Tree Search) implementations.
    """

    def __init__(self, board: chess.Board, strategy: IStrategy, seed: int | None):
        self.board = board
        self.strategy = strategy
        self.random_state = random.Random(seed)

    @abstractmethod
    def sample(self, runs: int = 1000) -> None:
        """
        Run the MCTS with the given number of samples.
        :param runs: Number of runs/samples
        """
        pass

    @abstractmethod
    def apply_move(self, move: chess.Move) -> None:
        """
        Apply the move to the chess board.
        :param move: Move to apply.
        """
        pass

    @abstractmethod
    def get_children(self) -> list[IMctsNode]:
        """
        Return the immediate children of the root node.
        :return: List of immediate children of mcts root.
        """
        pass
