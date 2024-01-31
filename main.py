import random
import time
import chess
import chess.engine
import chess.pgn
from chesspp.classic_mcts import ClassicMcts
from chesspp.baysian_mcts import BayesianMcts
from chesspp.engine_factory import EngineEnum, StrategyEnum
from chesspp.random_strategy import RandomStrategy
from chesspp.stockfish_strategy import StockFishStrategy
from chesspp import engine
from chesspp import util
from chesspp import simulation, eval
import argparse
import os


def test_simulate():
    board = chess.Board()
    strategy = StockFishStrategy()
    white = engine.BayesMctsEngine(board.copy(), chess.WHITE, strategy)
    black = engine.RandomEngine(board.copy(), chess.BLACK, RandomStrategy(random.Random()))
    game = simulation.simulate_game(white, black, engine.Limit(time=0.5), board)
    print(game)


def test_mcts():
    fools_mate = "rnbqkbnr/pppp1ppp/4p3/8/5PP1/8/PPPPP2P/RNBQKBNR b KQkq f3 0 2"
    board = chess.Board(fools_mate)
    mcts_root = ClassicMcts(board, chess.BLACK)
    mcts_root.build_tree()
    sorted_moves = sorted(mcts_root.children, key=lambda x: x.move.uci())
    for c in sorted_moves:
        print("move (mcts):", c.move, " with score:", c.score)


def test_bayes_mcts():
    global lookup_count
    fools_mate = "rnbqkbnr/pppp1ppp/4p3/8/5PP1/8/PPPPP2P/RNBQKBNR b KQkq f3 0 2"
    board = chess.Board(fools_mate)
    seed = None
    strategy = RandomStrategy(random.Random(seed))
    mcts = BayesianMcts(board, strategy, chess.BLACK, seed)
    t1 = time.time_ns()
    mcts.sample(1)
    t2 = time.time_ns()
    print((t2 - t1) / 1e6)
    mcts.print()
    for move, score in mcts.get_moves().items():
        print("move (mcts):", move, " with score:", score)


def test_stockfish():
    fools_mate = "rnbqkbnr/pppp1ppp/4p3/8/5PP1/8/PPPPP2P/RNBQKBNR b KQkq f3 0 2"
    board = chess.Board(fools_mate)
    moves = {}
    untried_moves = list(board.legal_moves)
    for move in untried_moves:
        util.simulate_game(board, move, 100)
        moves[move] = board
        board = chess.Board(fools_mate)

    sorted_moves = dict(sorted(moves.items(), key=lambda x: x[0].uci()))
    analyze_results(sorted_moves)


def test_stockfish_prob():
    fools_mate = "rnbqkbnr/pppp1ppp/4p3/8/5PP1/8/PPPPP2P/RNBQKBNR b KQkq f3 0 2"
    board = chess.Board(fools_mate)
    moves = {}
    untried_moves = list(board.legal_moves)
    for move in untried_moves:
        mean, std = util.simulate_stockfish_prob(board, move, 10, 4)
        moves[move] = (mean, std)
        board = chess.Board(fools_mate)

    sorted_moves = dict(sorted(moves.items(), key=lambda x: x[0].uci()))
    for m, s in sorted_moves.items():
        print(f"move '{m.uci()}' (prob_stockfish): mean={s[0]}, std={s[1]}")


def analyze_results(moves: dict):
    for m, b in moves.items():
        manual_score = eval.score_manual(b)
        engine_score = eval.score_stockfish(b).white().score(mate_score=100_000)
        print(f"score for move {m}: manual_score={manual_score}, engine_score={engine_score}")


def test_evaluation():
    a, b, s1, s2, n, limit, stockfish_path, lc0_path, proc = read_arguments()
    limit = engine.Limit(time=limit)

    evaluator = simulation.Evaluation(a, s1, b, s2, limit, stockfish_path, lc0_path)
    results = evaluator.run(n, proc)
    a_results = len(list(filter(lambda x: x.winner == simulation.Winner.Engine_A, results))) / len(results) * 100
    b_results = len(list(filter(lambda x: x.winner == simulation.Winner.Engine_B, results))) / len(results) * 100
    draws = len(list(filter(lambda x: x.winner == simulation.Winner.Draw, results))) / len(results) * 100

    print(f"Engine {a} won {a_results}% of games")
    print(f"Engine {b} won {b_results}% of games")
    print(f"{draws}% of games resulted in a draw")


def read_arguments():
    parser = argparse.ArgumentParser(
        prog='EvaluateEngine',
        description='Compare two engines by playing multiple games against each other'
    )

    engines = {"ClassicMCTS": EngineEnum.ClassicMcts, "BayesianMCTS": EngineEnum.BayesianMcts,
               "Random": EngineEnum.Random, "Stockfish": EngineEnum.Stockfish, "Lc0": EngineEnum.Lc0}
    strategies = {"Random": StrategyEnum.Random, "Stockfish": StrategyEnum.Stockfish, "Lc0": StrategyEnum.Lc0,
                  "RandomStockfish": StrategyEnum.RandomStockfish}

    if os.name == 'nt':
        stockfish_default = "stockfish/stockfish-windows-x86-64-avx2"
        lc0_default = "lc0/lc0.exe"
    else:
        stockfish_default = "stockfish/stockfish-ubuntu-x86-64-avx2"
        lc0_default = "lc0/lc0"

    parser.add_argument("--proc", default=2, help="Number of processors to use for simulation, default=1")
    parser.add_argument("--time", default=0.5, help="Time limit for each simulation step, default=0.5")
    parser.add_argument("-n", default=100, help="Number of games to simulate, default=100")
    parser.add_argument("--stockfish_path", default=stockfish_default,
                        help=f"Path for engine executable, default='{stockfish_default}'")
    parser.add_argument("--lc0_path", default=lc0_default,
                        help=f"Path for engine executable, default='{stockfish_default}'")
    parser.add_argument("--engine1", "--e1", help="Engine A for the simulation", choices=engines.keys(), required=True)
    parser.add_argument("--engine2", "--e2", help="Engine B for the simulation", choices=engines.keys(), required=True)
    parser.add_argument("--strategy1", "--s1", default=list(strategies.keys())[0],
                        help="Strategy for engine A for the rollout",
                        choices=strategies.keys())
    parser.add_argument("--strategy2", "--s2", default=list(strategies.keys())[0],
                        help="Strategy for engine B for the rollout",
                        choices=strategies.keys())
    args = parser.parse_args()

    engine1 = engines[args.engine1]
    engine2 = engines[args.engine2]
    strategy1 = strategies[args.strategy1]
    strategy2 = strategies[args.strategy2]

    print(engine1, engine2, strategy1, strategy2, int(args.n), float(args.time), args.stockfish_path, args.lc0_path,
          int(args.proc))
    return engine1, engine2, strategy1, strategy2, int(args.n), float(
        args.time), args.stockfish_path, args.lc0_path, int(args.proc)


def main():
    test_evaluation()
    # test_simulate()
    # test_mcts()
    # test_stockfish()
    # test_stockfish_prob()
    # test_bayes_mcts()


if __name__ == '__main__':
    main()
