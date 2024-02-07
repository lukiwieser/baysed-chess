import multiprocessing as mp
import random
import time
from dataclasses import dataclass
from enum import Enum

import chess
import chess.pgn

from chesspp.engine.i_engine import IEngine
from chesspp.engine_factory import StrategyEnum, EngineFactory, EngineEnum
from chesspp.limit import Limit


class Winner(Enum):
    Engine_A = 0
    Engine_B = 1
    Draw = 2


@dataclass
class GameStatistics:
    white: str
    black: str
    average_time_white: float
    average_time_black: float
    nodes_white: int
    nodes_black: int
    length: int


@dataclass
class MatchResult:
    winner: Winner
    game_as_pgn: str
    statistics: GameStatistics


class Matchmaker:
    def __init__(self, engine_a: EngineEnum, strategy_a, engine_b: EngineEnum, strategy_b, limit: Limit,
                 stockfish_path: str, lc0_path: str, stockfish_elo: int):
        self.engine_a = engine_a
        self.strategy_a = strategy_a
        self.engine_b = engine_b
        self.strategy_b = strategy_b
        self.stockfish_path = stockfish_path
        self.lc0_path = lc0_path
        self.limit = limit
        self.stockfish_elo = stockfish_elo

    def run(self, n_games=100, proc=mp.cpu_count()) -> list[MatchResult]:
        proc = min(proc, mp.cpu_count())
        arg = (
            self.engine_a, self.strategy_a, self.engine_b, self.strategy_b, self.limit, self.stockfish_path,
            self.lc0_path,
            self.stockfish_elo)
        if proc > 1:
            with mp.Pool(proc) as pool:
                args = [arg for i in range(n_games)]
                return pool.map(Matchmaker._run_single_match, args)
        return [
            Matchmaker._run_single_match(arg)
            for _ in range(n_games)
        ]

    @staticmethod
    def _run_single_match(arg: tuple[EngineEnum, StrategyEnum, EngineEnum, StrategyEnum, Limit, str, str, int]) -> MatchResult:
        """
        Runs a single game of chess.
        The colors are assigned randomly.
        """
        engine_a, strategy_a, engine_b, strategy_b, limit, stockfish_path, lc0_path, stockfish_elo = arg

        # assign color randomly
        flip_engines = bool(random.getrandbits(1))
        if flip_engines:
            black = EngineFactory.create_engine(engine_a, strategy_a, chess.BLACK,stockfish_path, lc0_path, stockfish_elo)
            white = EngineFactory.create_engine(engine_b, strategy_b, chess.WHITE, stockfish_path, lc0_path, stockfish_elo)
        else:
            white = EngineFactory.create_engine(engine_a, strategy_a, chess.WHITE, stockfish_path, lc0_path, stockfish_elo)
            black = EngineFactory.create_engine(engine_b, strategy_b, chess.BLACK, stockfish_path, lc0_path, stockfish_elo)

        # run single match of chess
        game, statistics = Matchmaker.simulate_game(white, black, limit, chess.Board())
        winner = game.end().board().outcome().winner

        # figure out winner
        match (winner, flip_engines):
            case (chess.BLACK, True) | (chess.WHITE, False):
                result = Winner.Engine_A
            case (chess.WHITE, True) | (chess.BLACK, False):
                result = Winner.Engine_B
            case _:
                result = Winner.Draw

        return MatchResult(result, str(game), statistics)

    @staticmethod
    def simulate_game(white: IEngine, black: IEngine, limit: Limit, board: chess.Board) -> tuple[chess.pgn.Game, GameStatistics]:
        """
        Runs a single game of chess.
        """
        is_white_playing = True
        times_white = []
        times_black = []
        game_length = 0

        while not board.is_game_over():
            start = time.time()
            play_result = white.play(board, limit) if is_white_playing else black.play(board, limit)
            end = time.time()
            times_white.append(end - start) if is_white_playing else times_black.append(end - start)
            board.push(play_result.move)
            is_white_playing = not is_white_playing
            game_length += 1

        game = chess.pgn.Game.from_board(board)
        game.headers['White'] = white.get_name()
        game.headers['Black'] = black.get_name()

        white_nodes = sum(white.node_counts) // len(white.node_counts) if hasattr(white, "node_counts") else 0
        black_nodes = sum(black.node_counts) // len(black.node_counts) if hasattr(black, "node_counts") else 0

        statistics = GameStatistics(white=white.get_name(),
                                    black=black.get_name(),
                                    average_time_white=(sum(times_white) / len(times_white)),
                                    average_time_black=(sum(times_black) / len(times_black)),
                                    nodes_white=white_nodes,
                                    nodes_black=black_nodes,
                                    length=game_length
                                    )

        return game, statistics
