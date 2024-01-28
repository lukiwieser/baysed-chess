import chess
import random
from abc import ABC, abstractmethod
from typing import Dict, Self
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
    def backpropagate(self, score: float) -> None:
        """
        Backpropagates the results of the rollout
        :param score:
        :return:
        """
        pass


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