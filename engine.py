import chess
import chess.engine
import random


def pick_move(board: chess.Board) -> chess.Move | None:
    """
    Pick a random move
    :param board: chess board
    :return: a valid move or None if no valid move available
    """
    if len(list(board.legal_moves)) == 0:
        return None
    return random.choice(list(board.legal_moves))


def simulate_game(board: chess.Board, move: chess.Move, depth: int):
    """
    Simulate a game starting with the given move
    :param board: chess board
    :param move: chosen move
    :param depth: number of moves that should be simulated after playing the chosen move
    :return: the score for the simulated game
    """
    engine = chess.engine.SimpleEngine.popen_uci("./stockfish/stockfish-ubuntu-x86-64-avx2")
    board.push(move)
    for i in range(depth):
        if board.is_game_over():
            engine.quit()
            return
        r = engine.play(board, chess.engine.Limit(depth=2))
        board.push(r.move)

    engine.quit()
