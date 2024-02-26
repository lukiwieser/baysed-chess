import chess
import chess.engine


def score_lc0(board: chess.Board, lc0: chess.engine.SimpleEngine) -> int:
    """
    Calculate the score of the given board using lc0
    """

    limit: chess.engine.Limit = chess.engine.Limit(depth=0)

    # lc0 cannot calculate a score if there is already a checkmate => return score manually for this case
    outcome = board.outcome()
    if outcome is not None and outcome.termination == chess.Termination.CHECKMATE:
        return 100_000 if outcome.winner == chess.WHITE else -100_000

    info = lc0.analyse(board, limit)
    return info['score'].white().score(mate_score=100_000)
