import chesspp
from chesspp import engine
from chesspp import web


if __name__ == '__main__':
    limit = engine.Limit(time=0.5)
    web.WebInterface(engine.BayesMctsEngine, engine.ClassicMctsEngine, limit).run_app()
