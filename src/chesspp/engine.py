from abc import ABC, abstractmethod
import chess
import chess.engine
import random
import time
from chesspp.classic_mcts import ClassicMcts
from chesspp.baysian_mcts import BayesianMcts
from chesspp.random_strategy import RandomStrategy


class Limit:
    """ Class to determine when to stop searching for moves """

    time: float|None
    """ Search for `time` seconds """

    nodes: int|None
    """ Search for a limited number of `nodes`"""

    def __init__(self, time: float|None = None, nodes: int|None = None):
        self.time = time
        self.nodes = nodes

    def run(self, func, *args, **kwargs):
        """
        Run `func` until the limit condition is reached
        :param func: the func that performs one search iteration
        :param *args: are passed to `func`
        :param **kwargs: are passed to `func`
        """

        if self.nodes:
            self._run_nodes(func, *args, **kwargs)
        elif self.time:
            self._run_time(func, *args, **kwargs)

    def _run_nodes(self, func, *args, **kwargs):
        for _ in range(self.nodes):
            func(*args, **kwargs)

    def _run_time(self, func, *args, **kwargs):
        start = time.perf_counter_ns()
        while (time.perf_counter_ns()-start)/1e9 < self.time:
            func(*args, **kwargs)


class Engine(ABC):
    color: chess.Color
    """The side the engine plays (``chess.WHITE`` or ``chess.BLACK``)."""

    def __init__(self, color: chess.Color):
        self.color = color

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


class BayesMctsEngine(Engine):
    def __init__(self, color: chess.Color):
        super().__init__(color)

    @staticmethod
    def get_name() -> str:
        return "BayesMctsEngine"

    def play(self, board: chess.Board, limit: Limit) -> chess.engine.PlayResult:
        strategy = RandomStrategy(random.Random())
        bayes_mcts = BayesianMcts(board, strategy, self.color)
        bayes_mcts.sample(1000)
        # limit.run(lambda: mcts_root.build_tree())
        best_move = max(bayes_mcts.get_moves().items(), key=lambda x: x[1])[0] if board.turn == chess.WHITE else (
            min(bayes_mcts.get_moves().items(), key=lambda x: x[1])[0])
        print(best_move)
        return chess.engine.PlayResult(move=best_move, ponder=None)


class ClassicMctsEngine(Engine):
    def __init__(self, color: chess.Color):
        super().__init__(color)

    @staticmethod
    def get_name() -> str:
        return "ClassicMctsEngine"

    def play(self, board: chess.Board, limit: Limit) -> chess.engine.PlayResult:
        mcts_root = ClassicMcts(board, self.color)
        mcts_root.build_tree()
        # limit.run(lambda: mcts_root.build_tree())
        best_move = max(mcts_root.children, key=lambda x: x.score).move if board.turn == chess.WHITE else (
            min(mcts_root.children, key=lambda x: x.score).move)
        return chess.engine.PlayResult(move=best_move, ponder=None)


class RandomEngine(Engine):
    def __init__(self, color: chess.Color):
        super().__init__(color)

    @staticmethod
    def get_name() -> str:
        return "Random"

    def play(self, board: chess.Board, limit: Limit) -> chess.engine.PlayResult:
        move = random.choice(list(board.legal_moves))
        return chess.engine.PlayResult(move=move, ponder=None)
