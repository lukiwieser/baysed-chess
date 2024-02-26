import chess.engine


def score_stockfish(board: chess.Board, stockfish: chess.engine.SimpleEngine) -> int:
    """
    Calculate the score of the given board using stockfish
    """

    limit = chess.engine.Limit(depth=0)
    info = stockfish.analyse(board, limit)
    return info['score'].white().score(mate_score=100_000)
