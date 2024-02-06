import argparse
import os
import random
import time

import chess
import chess.engine
import chess.pgn

from chesspp import engine
from chesspp import simulation, eval
from chesspp import util
from chesspp.engine_factory import EngineEnum, StrategyEnum
from chesspp.mcts.baysian_mcts import BayesianMcts
from chesspp.mcts.classic_mcts import ClassicMcts
from chesspp.strategies.random_strategy import RandomStrategy
from chesspp.strategies.stockfish_strategy import StockFishStrategy
from chesspp.util import hypothesis_test


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
    a, b, s1, s2, n, limit, stockfish_path, lc0_path, proc, nodes, stockfish_elo = read_arguments()
    limit = engine.Limit(time=limit) if limit != -1 else engine.Limit(nodes=nodes)

    evaluator = simulation.Evaluation(a, s1, b, s2, limit, stockfish_path, lc0_path, stockfish_elo)
    results = evaluator.run(n, proc)

    for r in results:
        stats = r.statistics
        print("====================================")
        print(f"Game length: {stats.length} moves")
        print(f"{stats.white} (White):")
        print(f"Average node count: {stats.nodes_white}")
        print(f"Average simulation time: {stats.average_time_white}")
        print()
        print(f"{stats.black} (Black):")
        print(f"Average node count: {stats.nodes_black}")
        print(f"Average simulation time: {stats.average_time_black}")
        print("====================================")
        print()

    games_played = len(results)
    a_wins = len(list(filter(lambda x: x.winner == simulation.Winner.Engine_A, results)))
    b_wins = len(list(filter(lambda x: x.winner == simulation.Winner.Engine_B, results)))
    draws = len(list(filter(lambda x: x.winner == simulation.Winner.Draw, results)))

    alpha = 0.001
    test_result = hypothesis_test(a_wins, draws, b_wins)
    reject_h0 = test_result['pvalue'] < alpha

    print(f"{games_played} games played")
    print(f"Engine {a} won {a_wins} games ({a_wins / games_played:.2%})")
    print(f"Engine {b} won {b_wins} games ({b_wins / games_played:.2%})")
    print(f"{draws} games ({draws / games_played:.2%}) resulted in a draw")
    print(f"Hypothesis test: trials={test_result['trials']}, pvalue={test_result['pvalue']:2.10f}, statistic={test_result['statistic']:2.4f}, reject_h0={reject_h0}")


def read_arguments():
    parser = argparse.ArgumentParser(
        prog='EvaluateEngine',
        description='Compare two engines by playing multiple games against each other'
    )

    engines = {"ClassicMCTS": EngineEnum.ClassicMcts, "BayesianMCTS": EngineEnum.BayesianMcts, "ClassicMCTSV2": EngineEnum.ClassicMctsV2,
               "Random": EngineEnum.Random, "Stockfish": EngineEnum.Stockfish, "Lc0": EngineEnum.Lc0}
    strategies = {"Random": StrategyEnum.Random, "Stockfish": StrategyEnum.Stockfish, "Lc0": StrategyEnum.Lc0,
                  "RandomStockfish": StrategyEnum.RandomStockfish, "PESTO": StrategyEnum.Pestos}

    if os.name == 'nt':
        stockfish_default = "stockfish/stockfish-windows-x86-64-avx2"
        lc0_default = "lc0/lc0.exe"
    else:
        stockfish_default = "stockfish/stockfish-ubuntu-x86-64-avx2"
        lc0_default = "lc0/lc0"

    parser.add_argument("--proc", default=2, help="Number of processors to use for simulation, default=1")
    parser.add_argument("--time", default=-1, help="Time limit for each simulation step, default=-1")
    parser.add_argument("--nodes", default=-1, help="Node limit for each simulation step, default=-1")
    parser.add_argument("-n", default=100, help="Number of games to simulate, default=100")
    parser.add_argument("--stockfish_path", default=stockfish_default,
                        help=f"Path for engine executable, default='{stockfish_default}'")
    parser.add_argument("--stockfish_elo", default=1500, help="Elo for stockfish engine, default=1500")
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

    print(engine1, engine2, strategy1, strategy2, int(args.n), args.time, args.stockfish_path, args.lc0_path,
          int(args.proc), int(args.nodes), int(args.stockfish_elo))
    return (engine1, engine2, strategy1, strategy2, int(args.n), float(args.time),
            args.stockfish_path, args.lc0_path, int(args.proc), int(args.nodes), int(args.stockfish_elo))


def main():
    test_evaluation()
    # test_simulate()
    # test_mcts()
    # test_stockfish()
    # test_stockfish_prob()
    # test_bayes_mcts()


if __name__ == '__main__':
    main()

    # Note: prevent endless wait on StockFish process
    # by allowing for cleanup of objects (which closes stockfish)
    import gc
    gc.collect()
