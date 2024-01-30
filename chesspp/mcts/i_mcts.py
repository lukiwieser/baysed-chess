import random
from abc import ABC, abstractmethod
from typing import Dict

import chess

from chesspp.i_strategy import IStrategy
from chesspp.mcts.i_mcts_node import IMctsNode


class IMcts(ABC):
    def __init__(self, board: chess.Board, strategy: IStrategy, seed: int | None):
        self.board = board
        self.strategy = strategy
        self.random_state = random.Random(seed)

    @abstractmethod
    def sample(self, runs: int = 1000) -> None:
        """
        Run the MCTS simulation
        :param runs: number of runs
        :return:
        """
        pass

    @abstractmethod
    def apply_move(self, move: chess.Move) -> None:
        """
        Apply the move to the chess board
        :param move: move to apply
        :return:
        """
        pass

    @abstractmethod
    def get_children(self) -> list[IMctsNode]:
        """
        Return the immediate children of the root node
        :return: list of immediate children of mcts root
        """
        pass

    @abstractmethod
    def get_moves(self) -> Dict[chess.Move, int]:
        """
        Return all legal moves from this node with respective scores
        :return: dictionary with moves as key and scores as values
        """
        pass

"""
TODO: add score class:
how many moves until the end of the game?
score ranges?
perspective of white/black
"""