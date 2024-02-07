import chess
import chess.engine


def score_lc0(board: chess.Board, lc0: chess.engine.SimpleEngine | None = None,
              limit: chess.engine.Limit= chess.engine.Limit(depth=0)) -> int:
    """
    Calculate the score of the given board using lc0
    :param board:
    :return:
    """
    if lc0 is None:
        engine = chess.engine.SimpleEngine.popen_uci("/home/luke/projects/pp-project/chess-engine-pp/lc0/lc0")
        info = engine.analyse(board, limit)
        engine.quit()
        return info["score"]
    else:
        info = lc0.analyse(board, limit)
        return info['score'].white().score(mate_score=100_000)
