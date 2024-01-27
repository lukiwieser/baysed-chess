from abc import ABC, abstractmethod
import chess
import chess.engine
import random

from chesspp.classic_mcts import ClassicMcts


class Engine(ABC):
    color: chess.Color
    """The side the engine plays (``chess.WHITE`` or ``chess.BLACK``)."""

    def __init__(self, color: chess.Color):
        self.color = color

    @abstractmethod
    def play(self, board: chess.Board) -> chess.engine.PlayResult:
        """
        Return the next action the engine chooses based on the given board
        :param board: the chess board
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


class ClassicMctsEngine(Engine):
    def __init__(self, color: chess.Color):
        super().__init__(color)

    @staticmethod
    def get_name() -> str:
        return "ClassicMctsEngine"

    def play(self, board: chess.Board) -> chess.engine.PlayResult:
        mcts_root = ClassicMcts(board, self.color)
        mcts_root.build_tree()
        best_move = max(mcts_root.children, key=lambda x: x.score).move if board.turn == chess.WHITE else (
            min(mcts_root.children, key=lambda x: x.score).move)
        return chess.engine.PlayResult(move=best_move, ponder=None)


class RandomEngine(Engine):
    def __init__(self, color: chess.Color):
        super().__init__(color)

    @staticmethod
    def get_name() -> str:
        return "Random"

    def play(self, board: chess.Board) -> chess.engine.PlayResult:
        move = random.choice(list(board.legal_moves))
        return chess.engine.PlayResult(move=move, ponder=None)
