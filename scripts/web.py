from baysed_chess.web.web import WebInterface
from main import read_arguments
from baysed_chess.limit import Limit

if __name__ == '__main__':
    engine1, engine2, strategy1, strategy2, n_games, time, stockfish_path, lc0_path, n_proc, nodes, stockfish_elo = read_arguments()
    limit = Limit(time=time) if time != -1 else Limit(nodes=nodes)
    WebInterface(engine1, engine2, strategy1, strategy2, stockfish_path, lc0_path, limit, stockfish_elo).run_app()
