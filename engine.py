import chess
import chess.engine
import random
import eval


def main():
    fools_mate = "rnbqkbnr/pppp1ppp/4p3/8/5PP1/8/PPPPP2P/RNBQKBNR b KQkq f3 0 2"
    board = chess.Board(fools_mate)
    print(board, '\n')
    moves = {}
    for i in range(10):
        move = pick_move(board)
        if move is None:
            break

        simulate_game(board, move, 100)
        moves[move] = board
        board = chess.Board(fools_mate)

    analyze_results(moves)


def analyze_results(moves: dict):
    for m, b in moves.items():
        manual_score = eval.score_game(b)
        engine_score = eval.analyze_with_stockfish(b)
        print(f"score for move {m}: manual_score={manual_score}, engine_score={engine_score}")


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
    print(move)
    print(board, '\n')
    for i in range(depth):
        if board.is_game_over():
            engine.quit()
            return
        r = engine.play(board, chess.engine.Limit(depth=2))
        print(r)
        board.push(r.move)
        print(board, '\n')

    engine.quit()


if __name__ == '__main__':
    main()
