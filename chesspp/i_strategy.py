from abc import ABC, abstractmethod

import chess


class IStrategy(ABC):
    rollout_depth: int

    def __init__(self, rollout_depth: int = 4):
        self.rollout_depth = rollout_depth

    @abstractmethod
    def pick_next_move(self, board: chess.Board) -> chess.Move:
        pass

    @abstractmethod
    def analyze_board(self, board: chess.Board) -> int:
        pass
