import multiprocessing as mp
import random
import chess
import chess.pgn
from typing import Tuple, List
from enum import Enum
from dataclasses import dataclass

from chesspp.engine import Engine


class Winner(Enum):
    Engine_A = 0
    Engine_B = 1
    Draw = 2


@dataclass
class EvaluationResult:
    winner: Winner
    game: chess.pgn.Game


def simulate_game(white: Engine, black: Engine) -> chess.pgn.Game:
    board = chess.Board()

    is_white_playing = True
    while not board.is_game_over():
        play_result = white.play(board) if is_white_playing else black.play(board)
        board.push(play_result.move)
        is_white_playing = not is_white_playing

    game = chess.pgn.Game.from_board(board)
    game.headers['White'] = white.get_name()
    game.headers['Black'] = black.get_name()
    return game


class Evaluation:
    def __init__(self, engine_a: Engine.__class__, engine_b: Engine.__class__):
        self.engine_a = engine_a
        self.engine_b = engine_b

    def run(self, n_games=100) -> List[EvaluationResult]:
        with mp.Pool(mp.cpu_count()) as pool:
            args = [(self.engine_a, self.engine_b) for i in range(n_games)]
            return pool.map(Evaluation._test_simulate, args)

    @staticmethod
    def _test_simulate(arg: Tuple[Engine.__class__, Engine.__class__]) -> EvaluationResult:
        engine_a, engine_b = arg
        flip_engines = bool(random.getrandbits(1))
        if flip_engines:
            black, white = engine_a(chess.BLACK), engine_b(chess.WHITE)
        else:
            white, black = engine_a(chess.WHITE), engine_b(chess.BLACK)

        game = simulate_game(white, black)
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

        return EvaluationResult(result, game)