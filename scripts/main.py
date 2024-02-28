from baysed_chess.hypothesis_test import hypothesis_test
from baysed_chess.limit import Limit
from baysed_chess.matchmaker import Matchmaker, Winner
from utils.read_arguments import read_arguments


def main():
    args = read_arguments()
    a = args.get("engine1")
    b = args.get("engine2")
    s1 = args.get("strategy1")
    s2 = args.get("strategy2")
    n = args.get("n")
    proc = args.get("proc")
    time_limit = args.get("time_limit")
    nodes_limit = args.get("nodes_limit")
    stockfish_path = args.get("stockfish_path")
    lc0_path = args.get("lc0_path")
    stockfish_elo = args.get("stockfish_elo")

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


if __name__ == '__main__':
    main()

    # Note: prevent endless wait on StockFish process
    # by allowing for cleanup of objects (which closes stockfish)
    import gc

    gc.collect()
