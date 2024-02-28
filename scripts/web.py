from baysed_chess.limit import Limit
from baysed_chess.web.web import WebInterface
from scripts.utils.read_arguments import read_arguments


def main():
    args = read_arguments()
    engine1 = args.get("engine1")
    engine2 = args.get("engine2")
    strategy1 = args.get("strategy1")
    strategy2 = args.get("strategy2")
    time = args.get("time_limit")
    nodes = args.get("nodes_limit")
    stockfish_path = args.get("stockfish_path")
    lc0_path = args.get("lc0_path")
    stockfish_elo = args.get("stockfish_elo")

    limit = Limit(time=time) if time != -1 else Limit(nodes=nodes)

    WebInterface(engine1, engine2, strategy1, strategy2, stockfish_path, lc0_path, limit, stockfish_elo).run_app()


if __name__ == '__main__':
    main()
