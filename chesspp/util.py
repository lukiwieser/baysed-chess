from typing import TypedDict

import chess
import chess.engine
from stockfish import Stockfish
import numpy as np
import random

from scipy.stats import binomtest


def pick_move(board: chess.Board) -> chess.Move | None:
    """
    Pick a random move
    :param board: chess board
    :return: a valid move or None if no valid move available
    """
    if len(list(board.legal_moves)) == 0:
        return None
    return random.choice(list(board.legal_moves))


def simulate_game(board: chess.Board, move: chess.Move, depth: int):
    """
    Simulate a game starting with the given move
    :param board: chess board
    :param move: chosen move
    :param depth: number of moves that should be simulated after playing the chosen move
    :return: the score for the simulated game
    """
    engine = chess.engine.SimpleEngine.popen_uci("./stockfish/stockfish-ubuntu-x86-64-avx2")
    board.push(move)
    for i in range(depth):
        if board.is_game_over():
            engine.quit()
            return
        r = engine.play(board, chess.engine.Limit(depth=2))
        board.push(r.move)

    engine.quit()


def simulate_stockfish_prob(board: chess.Board, move: chess.Move, games: int = 10, depth: int = 10) -> (float, float):
    """
    Simulate a game using
    :param board: chess board
    :param move: chosen move
    :param games: number of games that should be simulated after playing the move
    :param depth: simulation depth per game
    :return:
    """
    board.push(move)
    copied_board = board.copy()
    scores = []

    stockfish = Stockfish("./stockfish/stockfish-ubuntu-x86-64-avx2", depth=2, parameters={"Threads": 8, "Hash": 2048})
    stockfish.set_elo_rating(1200)
    stockfish.set_fen_position(board.fen())

    def reset_game():
        nonlocal scores, copied_board, board
        score = eval.score_stockfish(copied_board).white().score(mate_score=100_000)
        scores.append(score)
        copied_board = board.copy()
        stockfish.set_fen_position(board.fen())

    for _ in range(games):
        for d in range(depth):
            if copied_board.is_game_over() or d == depth - 1:
                reset_game()
                break

            if d == depth - 1:
                reset_game()

            top_moves = stockfish.get_top_moves(3)
            chosen_move = random.choice(top_moves)['Move']
            stockfish.make_moves_from_current_position([chosen_move])
            copied_board.push(chess.Move.from_uci(chosen_move))

    print(scores)
    # TODO: return distribution here?
    return np.array(scores).mean(), np.array(scores).std()


HypothesisTestResult = TypedDict('HypothesisTestResult', {"trials": int, "pvalue": float, "statistic": float})


def hypothesis_test(wins: int, draws: int, losses: int) -> HypothesisTestResult:
    """
    Hypothesis test using Binomial distributions.

    Null Hypothesis: Both engines have the same strength, aka they win on average half of the games.
    Alternative Hypothesis: Both engines have different strength.

    :returns: tuple of trials, pvalue, test-statistic
    """

    # wins give 1 point, and draws give 1/2 points
    score = wins + draws // 2

    # number of games
    trials = wins + draws + losses

    # due to rounding down the variable score, if draws are even, we have to reduce trials by one.
    if draws % 2 != 0:
        trials -= 1

    # we expect that if both engines have the same strength, that they "win" on 50% on average
    expected_success_rate = 0.5

    result = binomtest(score, trials, expected_success_rate, alternative='two-sided')

    return {
        "trials": trials,
        "pvalue": result.pvalue,
        "statistic": result.statistic
    }
