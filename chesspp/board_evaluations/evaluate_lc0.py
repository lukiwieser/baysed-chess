import chess
import chess.engine


def score_lc0(board: chess.Board, lc0: chess.engine.SimpleEngine) -> int:
    """
    Calculate the score of the given board using lc0
    """
    limit = chess.engine.Limit(depth=0)
    info = lc0.analyse(board, limit)
    return info['score'].white().score(mate_score=100_000)
