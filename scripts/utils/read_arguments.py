import argparse
import os
from typing import TypedDict

from baysed_chess.engine_factory import EngineEnum, StrategyEnum

ARGS = TypedDict("ARGS", {
    "engine1": EngineEnum,
    "engine2": EngineEnum,
    "strategy1": StrategyEnum,
    "strategy2": StrategyEnum,
    "n": int,
    "proc": int,
    "time_limit": float,
    "nodes_limit": int,
    "stockfish_path": str,
    "lc0_path": str,
    "stockfish_elo": int
})


def read_arguments() -> ARGS:
    parser = argparse.ArgumentParser(
        prog='EvaluateEngine',
        description='Compare two engines by playing multiple games against each other'
    )

    engines = {"ClassicMCTS": EngineEnum.ClassicMcts, "BayesianMCTS": EngineEnum.BayesianMcts,
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
    parser.add_argument("--proc", default=1, help="Number of processors to use for simulation, default=1", type=int,
                        choices=range(1, os.cpu_count() + 1))
    parser.add_argument("--time", default=-1, help="Time limit for each simulation step, default=-1")
    parser.add_argument("--nodes", default=-1, help="Node limit for each simulation step, default=-1")
    parser.add_argument("-n", default=100, help="Number of games to simulate, default=100")
    parser.add_argument("--stockfish_path", default=stockfish_default,
                        help=f"Path for stockfish engine executable, default='{stockfish_default}'")
    parser.add_argument("--stockfish_elo", default=1500, help="Elo for stockfish engine, default=1500")
    parser.add_argument("--lc0_path", default=lc0_default,
                        help=f"Path for lc0 engine executable, default='{lc0_default}'")
    args = parser.parse_args()

    _args = {
        "engine1": engines[args.engine1],
        "engine2": engines[args.engine2],
        "strategy1": strategies[args.strategy1],
        "strategy2": strategies[args.strategy2],
        "n": int(args.n),
        "proc": int(args.proc),
        "time_limit": float(args.time),
        "nodes_limit": int(args.nodes),
        "stockfish_path": args.stockfish_path,
        "lc0_path": args.lc0_path,
        "stockfish_elo": int(args.stockfish_elo)
    }
    print(_args)
    return _args
