import chess
import chess.engine


def score_stockfish(board: chess.Board, stockfish: chess.engine.SimpleEngine | None = None,
                    limit: chess.engine.Limit = chess.engine.Limit(depth=0)) -> int:
    """
    Calculate the score of the given board using stockfish
    :param board:
    :param stockfish:
    :param limit:
    :return:
    """
    if stockfish is None:
        engine = chess.engine.SimpleEngine.popen_uci(
            "/home/luke/projects/pp-project/chess-engine-pp/stockfish/stockfish-ubuntu-x86-64-avx2")
        info = engine.analyse(board, limit)
        engine.quit()
        return info['score'].white().score(mate_score=100_000)
    else:
        info = stockfish.analyse(board, limit)
        return info['score'].white().score(mate_score=100_000)
