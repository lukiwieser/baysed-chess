import os
import random
import time

import chess
from chess.engine import SimpleEngine

from baysed_chess.board_evaluations.evaluate_lc0 import score_lc0
from baysed_chess.board_evaluations.evaluate_stockfish import score_stockfish
from baysed_chess.mcts.baysian_mcts import BayesianMcts
from baysed_chess.mcts.classic_mcts import ClassicMcts
from baysed_chess.strategies.random_strategy import RandomStrategy


def analyze_stockfish(fen):
    board = chess.Board(fen)

    if os.name == 'nt':
        path = "stockfish/stockfish-windows-x86-64-avx2"
    else:
        path = "stockfish/stockfish-ubuntu-x86-64-avx2"

    stockfish = SimpleEngine.popen_uci(path)
    score = score_stockfish(board, stockfish)
    print(score)
    result = stockfish.play(board, limit=chess.engine.Limit(depth=4))
    print(result.move)
    stockfish.quit()


def analyze_lc0(fen):
    board = chess.Board(fen)

    if os.name == 'nt':
        path = "lc0/lc0"
    else:
        path = "lc0/lc0"

    lc0 = SimpleEngine.popen_uci(path)
    score = score_lc0(board, lc0)
    print(score)
    lc0.quit()


def analyze_classic_mcts(fen):
    board = chess.Board(fen)
    strategy = RandomStrategy(random.Random())
    mcts = ClassicMcts(board, chess.BLACK, strategy)
    mcts.sample()
    # TODO: return correct type-hint depending on which class mcts is
    sorted_moves = sorted(mcts.get_children(), key=lambda x: x.move.uci())
    for c in sorted_moves:
        print("move (mcts):", c.move, " with score:", c.score)


def analyze_bayes_mcts(fen):
    board = chess.Board(fen)
    seed = None
    strategy = RandomStrategy(random.Random(seed))
    mcts = BayesianMcts(board, strategy, chess.BLACK, seed=None)
    t1 = time.time_ns()
    mcts.sample(1)
    t2 = time.time_ns()
    print((t2 - t1) / 1e6)
    mcts.print()
    for move, score in mcts.get_moves().items():
        print("move (mcts):", move, " with score:", score)


def main():
    # foolsmate in fen notation
    board = "rnbqkbnr/pppp1ppp/4p3/8/5PP1/8/PPPPP2P/RNBQKBNR b KQkq f3 0 2"

    # EXAMPLE BOARDS
    # board = "2r5/pN1k4/b1pp2B1/Bp5p/2P5/P3PQ1P/P2N1PP1/R2K3R w - - 1 23" # whites turn, best move yields checkmate
    # board = "2r5/pN1k1Q2/b1pp2B1/Bp5p/2P5/P3P2P/P2N1PP1/R2K3R b - - 2 23" # checkmate, white has won
    # board = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1" # blacks turn, best move yields checkmate
    # board = "rnb1kbnr/pppp1ppp/4p3/8/5PPq/8/PPPPP2P/RNBQKBNR w KQkq - 1 3" # black has won

    analyze_stockfish(board)
    # analyze_classic_mcts(fools_mate)
    # analyze_bayes_mcts(fools_mate)
    analyze_lc0(board)


if __name__ == '__main__':
    main()
