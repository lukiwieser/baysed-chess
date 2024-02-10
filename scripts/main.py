import argparse
import os

from chesspp.engine_factory import EngineEnum, StrategyEnum
from chesspp.hypothesis_test import hypothesis_test
from chesspp.limit import Limit
from chesspp.matchmaker import Matchmaker, Winner


def read_arguments() -> tuple[EngineEnum, EngineEnum, StrategyEnum, StrategyEnum, int, int, float, int, str, str, int]:
    parser = argparse.ArgumentParser(
        prog='EvaluateEngine',
        description='Compare two engines by playing multiple games against each other'
    )

    engines = {"ClassicMCTS": EngineEnum.ClassicMcts, "BayesianMCTS": EngineEnum.BayesianMcts,
               "ClassicMCTSV2": EngineEnum.ClassicMctsV2,
               "Random": EngineEnum.Random, "Stockfish": EngineEnum.Stockfish, "Lc0": EngineEnum.Lc0}
    strategies = {"Random": StrategyEnum.Random, "Stockfish": StrategyEnum.Stockfish, "Lc0": StrategyEnum.Lc0,
                  "RandomStockfish": StrategyEnum.RandomStockfish, "PESTO": StrategyEnum.Pestos}

    if os.name == 'nt':
        stockfish_default = "stockfish/stockfish-windows-x86-64-avx2"
        lc0_default = "lc0/lc0"
    else:
        stockfish_default = "stockfish/stockfish-ubuntu-x86-64-avx2"
        lc0_default = "lc0/lc0"

    parser.add_argument("--engine1", "--e1", help="Engine A for the simulation", choices=engines.keys(), required=True)
    parser.add_argument("--engine2", "--e2", help="Engine B for the simulation", choices=engines.keys(), required=True)
    parser.add_argument("--strategy1", "--s1", default=list(strategies.keys())[0],
                        help="Strategy for engine A for the rollout",
                        choices=strategies.keys())
    parser.add_argument("--strategy2", "--s2", default=list(strategies.keys())[0],
                        help="Strategy for engine B for the rollout",
                        choices=strategies.keys())
    parser.add_argument("--proc", default=1, help="Number of processors to use for simulation, default=1", type=int, choices=range(1,os.cpu_count()+1))
    parser.add_argument("--time", default=-1, help="Time limit for each simulation step, default=-1")
    parser.add_argument("--nodes", default=-1, help="Node limit for each simulation step, default=-1")
    parser.add_argument("-n", default=100, help="Number of games to simulate, default=100")
    parser.add_argument("--stockfish_path", default=stockfish_default,
                        help=f"Path for stockfish engine executable, default='{stockfish_default}'")
    parser.add_argument("--stockfish_elo", default=1500, help="Elo for stockfish engine, default=1500")
    parser.add_argument("--lc0_path", default=lc0_default,
                        help=f"Path for lc0 engine executable, default='{lc0_default}'")
    args = parser.parse_args()

    engine1: EngineEnum = engines[args.engine1]
    engine2: EngineEnum = engines[args.engine2]
    strategy1: StrategyEnum = strategies[args.strategy1]
    strategy2: StrategyEnum = strategies[args.strategy2]
    n = int(args.n)
    proc = int(args.proc)
    time_limit = float(args.time)
    nodes_limit = int(args.nodes)
    stockfish_path: str = args.stockfish_path
    lc0_path: str = args.lc0_path
    stockfish_elo = int(args.stockfish_elo)

    print(engine1, engine2, strategy1, strategy2, n, proc, time_limit, nodes_limit, stockfish_path, lc0_path,
          stockfish_elo)
    return (
        engine1, engine2, strategy1, strategy2, n, proc, time_limit, nodes_limit, stockfish_path, lc0_path,
        stockfish_elo)


def run_matches(args: tuple[EngineEnum, EngineEnum, StrategyEnum, StrategyEnum, int, int, float, int, str, str, int]):
    a, b, s1, s2, n, proc, time_limit, nodes_limit, stockfish_path, lc0_path, stockfish_elo = args

    limit = Limit(time=time_limit) if time_limit != -1 else Limit(nodes=nodes_limit)

    m = Matchmaker(a, s1, b, s2, limit, stockfish_path, lc0_path, stockfish_elo)
    results = m.run(n, proc)

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
    a_wins = len(list(filter(lambda x: x.winner == Winner.Engine_A, results)))
    b_wins = len(list(filter(lambda x: x.winner == Winner.Engine_B, results)))
    draws = len(list(filter(lambda x: x.winner == Winner.Draw, results)))

    alpha = 0.001
    test_result = hypothesis_test(a_wins, draws, b_wins)
    reject_h0 = test_result['pvalue'] < alpha

    print(f"{games_played} games played")
    print(f"Engine {a} won {a_wins} games ({a_wins / games_played:.2%})")
    print(f"Engine {b} won {b_wins} games ({b_wins / games_played:.2%})")
    print(f"{draws} games ({draws / games_played:.2%}) resulted in a draw")
    print(f"Hypothesis test: trials={test_result['trials']}, pvalue={test_result['pvalue']:2.10f}, "
          f"statistic={test_result['statistic']:2.4f}, reject_h0={reject_h0}")


def main():
    args = read_arguments()
    run_matches(args)


if __name__ == '__main__':
    main()

    # Note: prevent endless wait on StockFish process
    # by allowing for cleanup of objects (which closes stockfish)
    import gc

    gc.collect()
