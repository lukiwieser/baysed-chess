import chess
import chess.engine

# Eval constants for scoring chess boards
# Evaluation metric inspired by Tomasz Michniewski: https://www.chessprogramming.org/Simplified_Evaluation_Function

PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000
}

pawn_eval = [
    0, 0, 0, 0, 0, 0, 0, 0,
    5, 10, 10, -20, -20, 10, 10, 5,
    5, -5, -10, 0, 0, -10, -5, 5,
    0, 0, 0, 20, 20, 0, 0, 0,
    5, 5, 10, 25, 25, 10, 5, 5,
    10, 10, 20, 30, 30, 20, 10, 10,
    50, 50, 50, 50, 50, 50, 50, 50,
    0, 0, 0, 0, 0, 0, 0, 0
]
knight_eval = [
    -50, -40, -30, -30, -30, -30, -40, -50,
    -40, -20, 0, 0, 0, 0, -20, -40,
    -30, 0, 10, 15, 15, 10, 0, -30,
    -30, 5, 15, 20, 20, 15, 5, -30,
    -30, 0, 15, 20, 20, 15, 0, -30,
    -30, 5, 10, 15, 15, 10, 5, -30,
    -40, -20, 0, 5, 5, 0, -20, -40,
    -50, -40, -30, -30, -30, -30, -40, -50
]
bishop_eval = [
    -20, -10, -10, -10, -10, -10, -10, -20,
    -10, 5, 0, 0, 0, 0, 5, -10,
    -10, 10, 10, 10, 10, 10, 10, -10,
    -10, 0, 10, 10, 10, 10, 0, -10,
    -10, 5, 5, 10, 10, 5, 5, -10,
    -10, 0, 5, 10, 10, 5, 0, -10,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -20, -10, -10, -10, -10, -10, -10, -20
]
rook_eval = [
    0, 0, 0, 5, 5, 0, 0, 0,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    5, 10, 10, 10, 10, 10, 10, 5,
    0, 0, 0, 0, 0, 0, 0, 0
]
queen_eval = [
    -20, -10, -10, -5, -5, -10, -10, -20,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -10, 0, 5, 5, 5, 5, 0, -10,
    -5, 0, 5, 5, 5, 5, 0, -5,
    0, 0, 5, 5, 5, 5, 0, -5,
    -10, 5, 5, 5, 5, 5, 0, -10,
    -10, 0, 5, 0, 0, 0, 0, -10,
    -20, -10, -10, -5, -5, -10, -10, -20
]
king_eval = [
    20, 30, 10, 0, 0, 10, 30, 20,
    20, 20, 0, 0, 0, 0, 20, 20,
    -10, -20, -20, -20, -20, -20, -20, -10,
    20, -30, -30, -40, -40, -30, -30, -20,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30
]
king_endgame_eval = [
    50, -30, -30, -30, -30, -30, -30, -50,
    -30, -30,  0,  0,  0,  0, -30, -30,
    -30, -10, 20, 30, 30, 20, -10, -30,
    -30, -10, 30, 40, 40, 30, -10, -30,
    -30, -10, 30, 40, 40, 30, -10, -30,
    -30, -10, 20, 30, 30, 20, -10, -30,
    -30, -20, -10,  0,  0, -10, -20, -30,
    -50, -40, -30, -20, -20, -30, -40, -50
]

PIECE_TABLES = {
    chess.WHITE: {
        chess.PAWN: pawn_eval,
        chess.KNIGHT: knight_eval,
        chess.BISHOP: bishop_eval,
        chess.ROOK: rook_eval,
        chess.QUEEN: queen_eval,
        chess.KING: king_eval,
        'end_game_king': king_endgame_eval
    },
    chess.BLACK: {
        chess.PAWN: list(reversed(pawn_eval)),
        chess.KNIGHT: list(reversed(knight_eval)),
        chess.BISHOP: list(reversed(bishop_eval)),
        chess.ROOK: list(reversed(rook_eval)),
        chess.QUEEN: list(reversed(queen_eval)),
        chess.KING: list(reversed(king_eval)),
        'end_game_king': list(reversed(king_endgame_eval))
    }
}


def check_endgame(board: chess.Board) -> bool:
    """
    Endgame according to Tomasz Michniewski:
        1. Both sides have no queens or
        2. Every side which has a queen has additionally no other pieces or one minorpiece maximum.
    """
    queens_white = 0
    minors_white = 0
    queens_black = 0
    minors_black = 0
    for s in chess.SQUARES:
        piece = board.piece_at(s)
        if piece is None:
            continue

        if piece.piece_type == chess.QUEEN:
            if piece.color == chess.WHITE:
                queens_white += 1 
            else:
                queens_black += 1

        if piece.piece_type == chess.BISHOP or piece.piece_type == chess.KNIGHT:
            if piece.color == chess.WHITE:
                minors_white += 1 
            else:
                minors_black += 1

    return (queens_black == 0 and queens_white == 0) or ((queens_black >= 1 and minors_black <= 1) or (queens_white >= 1 and minors_white <= 1))




def score_game(board: chess.Board) -> float:
    """
    Calculate the score of the given board regarding the given color
    :param board: the chess board
    :return: score metric
    """
    outcome = board.outcome()
    if outcome is not None:
        if outcome.termination == chess.Termination.CHECKMATE:
            return float('inf') if outcome.winner == chess.WHITE else float('-inf')
        else:  # draw
            return 0

    score = 0
    for s in chess.SQUARES:
        piece = board.piece_at(s)
        if piece is None:
            continue

        if piece.color == chess.WHITE:
            if piece.piece_type == chess.KING and check_endgame(board):
                score += PIECE_VALUES[piece.piece_type] * PIECE_TABLES[chess.WHITE]['end_game_king'][s]
            else:
                score += PIECE_VALUES[piece.piece_type] * PIECE_TABLES[chess.WHITE][piece.piece_type][s]
        else:
            if piece.piece_type == chess.KING and check_endgame(board):
                score -= PIECE_VALUES[piece.piece_type] * PIECE_TABLES[chess.BLACK]['end_game_king'][s]
            else:
                score -= PIECE_VALUES[piece.piece_type] * PIECE_TABLES[chess.BLACK][piece.piece_type][s]

    return score


def analyze_with_stockfish(board: chess.Board) -> chess.engine.PovScore:
    """
    Calculate the score of the given board using stockfish
    :param board:
    :return:
    """
    engine = chess.engine.SimpleEngine.popen_uci("./stockfish/stockfish-ubuntu-x86-64-avx2")
    info = engine.analyse(board, chess.engine.Limit(depth=20))
    engine.quit()
    return info["score"]
