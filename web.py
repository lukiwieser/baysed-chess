from chesspp import engine
from chesspp import web
from main import read_arguments


if __name__ == '__main__':
    engine1, engine2, strategy1, strategy2, n_games, time, stockfish_path, lc0_path, n_proc = read_arguments()
    limit = engine.Limit(time=0.5)
    web.WebInterface(engine1, engine2, strategy1, strategy2, stockfish_path, lc0_path, limit).run_app()
