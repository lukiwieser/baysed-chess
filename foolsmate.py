import os
import random
import time

import chess
from chess.engine import SimpleEngine

from chesspp.mcts.baysian_mcts import BayesianMcts
from chesspp.mcts.classic_mcts import ClassicMcts
from chesspp.strategies.random_strategy import RandomStrategy


def analyze_stockfish(fen):
    board = chess.Board(fen)

    if os.name == 'nt':
        path = "stockfish/stockfish-windows-x86-64-avx2"
    else:
        path = "stockfish/stockfish-ubuntu-x86-64-avx2"

    stockfish = SimpleEngine.popen_uci(path)
    result = stockfish.play(board, limit=chess.engine.Limit(depth=4))
    print(result.move)
    stockfish.quit()


def analyze_classic_mcts(fen):
    board = chess.Board(fen)
    strategy = RandomStrategy(random.Random())
    mcts_root = ClassicMcts(board, chess.BLACK, strategy)
    mcts_root.build_tree()
    sorted_moves = sorted(mcts_root.children, key=lambda x: x.move.uci())
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
    fools_mate = "rnbqkbnr/pppp1ppp/4p3/8/5PP1/8/PPPPP2P/RNBQKBNR b KQkq f3 0 2"

    analyze_stockfish(fools_mate)
    analyze_classic_mcts(fools_mate)
    analyze_bayes_mcts(fools_mate)


if __name__ == '__main__':
    main()
