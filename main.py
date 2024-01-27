import chess
import chess.engine
from classic_mcts import ClassicMcts
import engine
import eval
import util


def simulate_game(white: engine.Engine, black: engine.Engine) -> chess.pgn.Game:
    board = chess.Board()

    is_white_playing = True
    while not board.is_game_over():
        play_result = white.play(board) if is_white_playing else black.play(board)
        board.push(play_result.move)
        print(board)
        print()
        is_white_playing = not is_white_playing

    game = chess.pgn.Game.from_board(board)
    game.headers['White'] = white.get_name()
    game.headers['Black'] = black.get_name()
    return game


def test_simulate():
    white = engine.ClassicMctsEngine(chess.WHITE)
    black = engine.ClassicMctsEngine(chess.BLACK)
    game = simulate_game(white, black)
    print(game)


def test_mcts():
    fools_mate = "rnbqkbnr/pppp1ppp/4p3/8/5PP1/8/PPPPP2P/RNBQKBNR b KQkq f3 0 2"
    board = chess.Board(fools_mate)
    mcts_root = ClassicMcts(board, chess.BLACK)
    mcts_root.build_tree()
    sorted_moves = sorted(mcts_root.children, key=lambda x: x.move.uci())
    for c in sorted_moves:
        print("move (mcts):", c.move, " with score:", c.score)


def test_stockfish():
    fools_mate = "rnbqkbnr/pppp1ppp/4p3/8/5PP1/8/PPPPP2P/RNBQKBNR b KQkq f3 0 2"
    board = chess.Board(fools_mate)
    moves = {}
    untried_moves = list(board.legal_moves)
    for move in untried_moves:
        util.simulate_game(board, move, 100)
        moves[move] = board
        board = chess.Board(fools_mate)

    sorted_moves = dict(sorted(moves.items(), key=lambda x: x[0].uci()))
    analyze_results(sorted_moves)


def test_stockfish_prob():
    fools_mate = "rnbqkbnr/pppp1ppp/4p3/8/5PP1/8/PPPPP2P/RNBQKBNR b KQkq f3 0 2"
    board = chess.Board(fools_mate)
    moves = {}
    untried_moves = list(board.legal_moves)
    for move in untried_moves:
        mean, std = util.simulate_stockfish_prob(board, move, 10, 4)
        moves[move] = (mean, std)
        board = chess.Board(fools_mate)

    sorted_moves = dict(sorted(moves.items(), key=lambda x: x[0].uci()))
    for m, s in sorted_moves.items():
        print(f"move '{m.uci()}' (prob_stockfish): mean={s[0]}, std={s[1]}")


def analyze_results(moves: dict):
    for m, b in moves.items():
        manual_score = eval.score_manual(b)
        engine_score = eval.score_stockfish(b).white().score(mate_score=100_000)
        print(f"score for move {m}: manual_score={manual_score}, engine_score={engine_score}")


def main():
    test_simulate()
    # test_mcts()
    # test_stockfish()
    # test_stockfish_prob()


if __name__ == '__main__':
    main()
