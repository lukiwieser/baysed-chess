import chess
from abc import ABC, abstractmethod
from i_strategy import IStrategy


class IMcts(ABC):

    def __init__(self, board: chess.Board, strategy: IStrategy):
        self.board = board

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
    def get_children(self) -> list['Mcts']:
        """
        Return the immediate children of the root node
        :return: list of immediate children of mcts root
        """
        pass
