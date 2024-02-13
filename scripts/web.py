from baysed_chess.limit import Limit
from baysed_chess.web.web import WebInterface
from main import read_arguments

if __name__ == '__main__':
    engine1, engine2, strategy1, strategy2, n_games, n_proc, time, nodes, stockfish_path, lc0_path, stockfish_elo = read_arguments()
    limit = Limit(time=time) if time != -1 else Limit(nodes=nodes)
    WebInterface(engine1, engine2, strategy1, strategy2, stockfish_path, lc0_path, limit, stockfish_elo).run_app()
