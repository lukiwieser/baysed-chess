from abc import ABC, abstractmethod

import chess.engine

from baysed_chess.limit import Limit
from baysed_chess.strategies.i_strategy import IStrategy


class IEngine(ABC):
    board: chess.Board
    """The chess board"""
    color: chess.Color
    """The side the engine plays (``chess.WHITE`` or ``chess.BLACK``)."""
    strategy: IStrategy
    """The strategy used to pick moves when simulating games."""

    def __init__(self, board: chess.Board, color: chess.Color, strategy: IStrategy | None):
        self.board = board
        self.color = color
        self.strategy = strategy

    @abstractmethod
    def play(self, board: chess.Board, limit: Limit) -> chess.engine.PlayResult:
        """
        Return the next action the engine chooses based on the given board
        :param board: the chess board
        :param limit: a limit specifying when to stop searching
        :return: the engine's PlayResult
        """
        pass

    @staticmethod
    @abstractmethod
    def get_name() -> str:
        """
        Return the engine's name
        :return: the engine's name
        """
        pass
