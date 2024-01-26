import chess
from abc import ABC, abstractmethod
from IStrategy import IStrategy


class IMcts(ABC):

    def __init__(self, board: chess.Board, strategy: IStrategy):
        self.board = board

    @abstractmethod
    def sample(self, runs: int = 1000) -> None:
        pass

    @abstractmethod
    def apply_move(self, move: chess.Move) -> None:
        pass

    @abstractmethod
    def get_children(self) -> list['Mcts']:
        pass
