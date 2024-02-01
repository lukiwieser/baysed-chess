import random
import time
from abc import ABC, abstractmethod

from torch import distributions as dist
import chess
import chess.engine
from stockfish import Stockfish

from chesspp.mcts.baysian_mcts import BayesianMcts
from chesspp.mcts.classic_mcts import ClassicMcts
from chesspp.i_strategy import IStrategy

from typing import Dict

from chesspp.mcts.classic_mcts_v2 import ClassicMctsV2


class Limit:
    """ Class to determine when to stop searching for moves """

    time: float | None
    """ Search for `time` seconds """

    nodes: int | None
    """ Search for a limited number of `nodes`"""

    def __init__(self, time: float | None = None, nodes: int | None = None):
        self.time = time
        self.nodes = nodes
        self.node_count = 0

    def run(self, func, *args, **kwargs):
        """
        Run `func` until the limit condition is reached
        :param func: the func that performs one search iteration
        :param *args: are passed to `func`
        :param **kwargs: are passed to `func`
        """

        if self.nodes:
            self._run_nodes(func, *args, **kwargs)
            self.node_count = self.nodes
        elif self.time:
            self._run_time(func, *args, **kwargs)

    def _run_nodes(self, func, *args, **kwargs):
        for _ in range(self.nodes):
            func(*args, **kwargs)

    def _run_time(self, func, *args, **kwargs):
        start = time.perf_counter_ns()
        while (time.perf_counter_ns() - start) / 1e9 < self.time:
            func(*args, **kwargs)
            self.node_count += 1

    def translate_to_engine_limit(self) -> chess.engine.Limit:
        if self.nodes:
            return chess.engine.Limit(nodes=self.nodes)
        elif self.time:
            return chess.engine.Limit(time=self.time)


class Engine(ABC):
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


class BayesMctsEngine(Engine):
    mcts: BayesianMcts
    """The Bayesian MCTS"""

    def __init__(self, board: chess.Board, color: chess.Color, strategy: IStrategy):
        super().__init__(board, color, strategy)
        self.mcts = BayesianMcts(board, self.strategy, self.color)
        self.node_counts = []

    @staticmethod
    def get_name() -> str:
        return "BayesMctsEngine"

    def play(self, board: chess.Board, limit: Limit) -> chess.engine.PlayResult:
        if len(board.move_stack) != 0:  # apply previous move to mcts --> reuse previous simulation results
            self.mcts.apply_move(board.peek())

        node_count = 0

        def do():
            nonlocal node_count
            self.mcts.sample(1)
            node_count += 1

        limit.run(do)
        self.node_counts.append(node_count)
        best_move = self.get_best_move(self.mcts.get_moves(), board.turn)
        self.mcts.apply_move(best_move)
        return chess.engine.PlayResult(move=best_move, ponder=None)

    @staticmethod
    def get_best_move(possible_moves: Dict[chess.Move, dist.Normal], color: chess.Color) -> chess.Move:
        moves = {}
        for m, d in possible_moves.items():
            moves[m] = d.sample()

        return max(moves.items(), key=lambda x: x[1])[0] if color == chess.WHITE else (
            min(moves.items(), key=lambda x: x[1])[0])


class ClassicMctsEngine(Engine):
    def __init__(self, board: chess.Board, color: chess.Color, strategy: IStrategy):
        super().__init__(board, color, strategy)
        self.node_counts = []

    @staticmethod
    def get_name() -> str:
        return "ClassicMctsEngine"

    def play(self, board: chess.Board, limit: Limit) -> chess.engine.PlayResult:
        mcts_root = ClassicMcts(board, self.color, self.strategy)
        node_count = 0

        def do():
            nonlocal node_count
            mcts_root.build_tree(1)
            node_count += 1

        limit.run(do)
        self.node_counts.append(node_count)
        best_move = max(mcts_root.children, key=lambda x: x.score).move if board.turn == chess.WHITE else (
            min(mcts_root.children, key=lambda x: x.score).move)
        return chess.engine.PlayResult(move=best_move, ponder=None)


class ClassicMctsEngineV2(Engine):
    def __init__(self, board: chess.Board, color: chess.Color, strategy: IStrategy):
        super().__init__(board, color, strategy)
        self.node_counts = []

    @staticmethod
    def get_name() -> str:
        return "ClassicMctsEngine V2"

    def play(self, board: chess.Board, limit: Limit) -> chess.engine.PlayResult:
        mcts = ClassicMctsV2(board, self.color, self.strategy)
        node_count = 0

        def do():
            nonlocal node_count
            mcts.build_tree(1)
            node_count += 1

        limit.run(do)
        self.node_counts.append(node_count)
        best_move = max(mcts.root.children, key=lambda x: x.score).move if board.turn == chess.WHITE else (
            min(mcts.root.children, key=lambda x: x.score).move)
        return chess.engine.PlayResult(move=best_move, ponder=None)


class RandomEngine(Engine):
    def __init__(self, board: chess.Board, color: chess.Color, strategy: IStrategy):
        super().__init__(board, color, strategy)

    @staticmethod
    def get_name() -> str:
        return "RandomEngine"

    def play(self, board: chess.Board, limit: Limit) -> chess.engine.PlayResult:
        move = random.choice(list(board.legal_moves))
        return chess.engine.PlayResult(move=move, ponder=None)


class StockFishEngine(Engine):
    def __init__(self, board: chess.Board, color: chess, stockfish_elo: int,
                 path="../stockfish/stockfish-ubuntu-x86-64-avx2"):
        super().__init__(board, color, None)
        self.stockfish = Stockfish(path)
        self.stockfish.set_elo_rating(stockfish_elo)

    def play(self, board: chess.Board, limit: Limit) -> chess.engine.PlayResult:
        self.stockfish.set_fen_position(board.fen())
        m = chess.Move.from_uci(self.stockfish.get_best_move())
        return chess.engine.PlayResult(move=m, ponder=None)

    @staticmethod
    def get_name() -> str:
        return "Stockfish"


class Lc0Engine(Engine):
    def __init__(self, board: chess.Board, color: chess, path="../lc0/lc0"):
        super().__init__(board, color, None)
        self.lc0 = chess.engine.SimpleEngine.popen_uci(path)

    def play(self, board: chess.Board, limit: Limit) -> chess.engine.PlayResult:
        return self.lc0.play(board, limit.translate_to_engine_limit())

    @staticmethod
    def get_name() -> str:
        return "Lc0"
