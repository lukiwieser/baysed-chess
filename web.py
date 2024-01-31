from chesspp import engine
from chesspp import web
from main import read_arguments

if __name__ == '__main__':
    engine1, engine2, strategy1, strategy2, n_games, time, stockfish_path, lc0_path, n_proc, nodes, stockfish_elo = read_arguments()
    limit = engine.Limit(time=time) if time != -1 else engine.Limit(nodes=nodes)
    web.WebInterface(engine1, engine2, strategy1, strategy2, stockfish_path, lc0_path, limit, stockfish_elo).run_app()
