import multiprocessing as mp
import random
import chess
import chess.pgn
from typing import Tuple, List
from enum import Enum
from dataclasses import dataclass
from chesspp.i_strategy import IStrategy

from chesspp.engine import Engine, Limit


class Winner(Enum):
    Engine_A = 0
    Engine_B = 1
    Draw = 2


@dataclass
class EvaluationResult:
    winner: Winner
    game: str


def simulate_game(white: Engine, black: Engine, limit: Limit, board: chess.Board) -> chess.pgn.Game:
    is_white_playing = True
    while not board.is_game_over():
        play_result = white.play(board, limit) if is_white_playing else black.play(board, limit)
        board.push(play_result.move)
        is_white_playing = not is_white_playing

    game = chess.pgn.Game.from_board(board)
    game.headers['White'] = white.get_name()
    game.headers['Black'] = black.get_name()
    return game


class Evaluation:
    def __init__(self, engine_a: Engine.__class__, strategy_a, engine_b: Engine.__class__, strategy_b, limit: Limit):
        self.engine_a = engine_a
        self.strategy_a = strategy_a
        self.engine_b = engine_b
        self.strategy_b = strategy_b
        self.limit = limit

    def run(self, n_games=100, proc=mp.cpu_count()) -> List[EvaluationResult]:
        proc = min(proc, mp.cpu_count())
        with mp.Pool(proc) as pool:
            args = [(self.engine_a, self.strategy_a, self.engine_b, self.strategy_b, self.limit) for i in range(n_games)]
            return pool.map(Evaluation._test_simulate, args)

    @staticmethod
    def _test_simulate(arg: Tuple[Engine.__class__, IStrategy,  Engine.__class__, IStrategy, Limit]) -> EvaluationResult:
        engine_a, strategy_a, engine_b, strategy_b, limit = arg
        flip_engines = bool(random.getrandbits(1))

        board = chess.Board()

        if flip_engines:
            black, white = engine_a(board.copy(), chess.BLACK, strategy_a), engine_b(board.copy(), chess.WHITE, strategy_b)
        else:
            white, black = engine_a(board.copy(), chess.WHITE, strategy_a), engine_b(board.copy(), chess.BLACK, strategy_b)

        game = simulate_game(white, black, limit, board)
        winner = game.end().board().outcome().winner

        result = Winner.Draw
        match (winner, flip_engines):
            case (chess.WHITE, True):
                result = Winner.Engine_B
            case (chess.BLACK, True):
                result = Winner.Engine_A
            case (chess.WHITE, False):
                result = Winner.Engine_A
            case (chess.BLACK, False):
                result = Winner.Engine_B

        return EvaluationResult(result, str(game))
