from abc import ABC, abstractmethod

import chess


# TODO extend class
class IStrategy(ABC):

    @abstractmethod
    def pick_next_move(self, board: chess.Board) -> chess.Move:
        pass
