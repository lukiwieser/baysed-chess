"""
Some example strategies for people who want to create a custom, homemade bot.

With these classes, bot makers will not have to implement the UCI or XBoard interfaces themselves.
"""

from __future__ import annotations
import chess
from chess.engine import PlayResult, Limit
import random
from lib.engine_wrapper import MinimalEngine, MOVE
from typing import Any
import logging

import chesspp
from chesspp.engine import ClassicMctsEngine, Engine
from chesspp.engine_factory import EngineFactory, EngineEnum, StrategyEnum

# Use this logger variable to print messages to the console or log files.
# logger.info("message") will always print "message" to the console or log file.
# logger.debug("message") will only print "message" if verbose logging is enabled.
logger = logging.getLogger(__name__)


class ExampleEngine(MinimalEngine):
    """An example engine that all homemade engines inherit."""

    pass


# Strategy names and ideas from tom7's excellent eloWorld video

class RandomMove(ExampleEngine):
    """Get a random move."""

    def search(self, board: chess.Board, *args: Any) -> PlayResult:
        """Choose a random move."""
        return PlayResult(random.choice(list(board.legal_moves)), None)


class Alphabetical(ExampleEngine):
    """Get the first move when sorted by san representation."""

    def search(self, board: chess.Board, *args: Any) -> PlayResult:
        """Choose the first move alphabetically."""
        moves = list(board.legal_moves)
        moves.sort(key=board.san)
        return PlayResult(moves[0], None)


class FirstMove(ExampleEngine):
    """Get the first move when sorted by uci representation."""

    def search(self, board: chess.Board, *args: Any) -> PlayResult:
        """Choose the first move alphabetically in uci representation."""
        moves = list(board.legal_moves)
        moves.sort(key=str)
        return PlayResult(moves[0], None)


class ComboEngine(ExampleEngine):
    """
    Get a move using multiple different methods.

    This engine demonstrates how one can use `time_limit`, `draw_offered`, and `root_moves`.
    """

    def search(self, board: chess.Board, time_limit: Limit, ponder: bool, draw_offered: bool,
               root_moves: MOVE) -> PlayResult:
        """
        Choose a move using multiple different methods.

        :param board: The current position.
        :param time_limit: Conditions for how long the engine can search (e.g. we have 10 seconds and search up to depth 10).
        :param ponder: Whether the engine can ponder after playing a move.
        :param draw_offered: Whether the bot was offered a draw.
        :param root_moves: If it is a list, the engine should only play a move that is in `root_moves`.
        :return: The move to play.
        """
        if isinstance(time_limit.time, int):
            my_time = time_limit.time
            my_inc = 0
        elif board.turn == chess.WHITE:
            my_time = time_limit.white_clock if isinstance(time_limit.white_clock, int) else 0
            my_inc = time_limit.white_inc if isinstance(time_limit.white_inc, int) else 0
        else:
            my_time = time_limit.black_clock if isinstance(time_limit.black_clock, int) else 0
            my_inc = time_limit.black_inc if isinstance(time_limit.black_inc, int) else 0

        possible_moves = root_moves if isinstance(root_moves, list) else list(board.legal_moves)

        if my_time / 60 + my_inc > 10:
            # Choose a random move.
            move = random.choice(possible_moves)
        else:
            # Choose the first move alphabetically in uci representation.
            possible_moves.sort(key=str)
            move = possible_moves[0]
        return PlayResult(move, None, draw_offered=draw_offered)


# class ProbStockfish(MinimalEngine):
#     def search(self, board: chess.Board, time_limit: chess.engine.Limit, ponder: bool, draw_offered: bool,
#                root_moves: MOVE) -> chess.engine.PlayResult:
#         moves = {}
#         untried_moves = list(board.legal_moves)
#         for move in untried_moves:
#             mean, std = engine.simulate_stockfish_prob(board.copy(), move, 10, 2)
#             moves[move] = (mean, std)
#             if mean == 100_000 and std == 0:
#                 return chess.engine.PlayResult(move, None)
#
#         return self.get_best_move(moves)
#
#     def get_best_move(self, moves: dict) -> chess.engine.PlayResult:
#         best_avg = max(moves.items(), key=lambda m: m[1][0])
#         next_move = best_avg[0]
#         return chess.engine.PlayResult(next_move, None)


class MctsEngine(MinimalEngine):
    def search(self, board: chess.Board, time_limit: chess.engine.Limit, ponder: bool, draw_offered: bool,
               root_moves: MOVE) -> chess.engine.PlayResult:
        my_engine = ClassicMctsEngine(board.turn)
        print("Color:", board.turn)
        print("engine play result: ", my_engine.play(board.copy(), chesspp.engine.Limit(0.5)))
        print("Engine name", my_engine)
        return my_engine.play(board.copy(), chesspp.engine.Limit())


class MyBayesMctsEngine(MinimalEngine):
    def __init__(self, commands: COMMANDS_TYPE, options: OPTIONS_TYPE, stderr: Optional[int],
                 draw_or_resign: Configuration, name: Optional[str] = None, **popen_args: str) -> None:
        """
        Initialize the values of the engine that all homemade engines inherit.

        :param options: The options to send to the engine.
        :param draw_or_resign: Options on whether the bot should resign or offer draws.
        """
        super().__init__(commands, options, stderr, draw_or_resign, name, **popen_args)
        self._engine = None

    def get_engine(self, color: chess.Color) -> chess.engine:
        if self._engine is None:
            self._engine = EngineFactory.create_engine(EngineEnum.BayesianMcts, StrategyEnum.Stockfish, color,
                                                       "/home/luke/projects/pp-project/chess-engine-pp/stockfish/stockfish-ubuntu-x86-64-avx2",
                                                       "", 1500, 4)

        return self._engine

    def search(self, board: chess.Board, time_limit: chess.engine.Limit, ponder: bool, draw_offered: bool,
               root_moves: MOVE) -> chess.engine.PlayResult:
        my_engine = self.get_engine(board.turn)
        r = my_engine.play(board.copy(), chesspp.engine.Limit(2))
        return r
