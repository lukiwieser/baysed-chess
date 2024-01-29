import random
import chess
import chess.engine
import chess.pgn
from chesspp.classic_mcts import ClassicMcts
from chesspp.baysian_mcts import BayesianMcts
from chesspp.random_strategy import RandomStrategy
from chesspp.stockfish_strategy import StockFishStrategy
from chesspp import engine
from chesspp import util
from chesspp import simulation, eval


def test_simulate():
    board = chess.Board()
    strategy = StockFishStrategy()
    white = engine.BayesMctsEngine(board.copy(), chess.WHITE, strategy)
    black = engine.RandomEngine(board.copy(), chess.BLACK, RandomStrategy(random.Random()))
    game = simulation.simulate_game(white, black, engine.Limit(time=0.5), board)
    print(game)


def test_mcts():
    fools_mate = "rnbqkbnr/pppp1ppp/4p3/8/5PP1/8/PPPPP2P/RNBQKBNR b KQkq f3 0 2"
    board = chess.Board(fools_mate)
    mcts_root = ClassicMcts(board, chess.BLACK)
    mcts_root.build_tree()
    sorted_moves = sorted(mcts_root.children, key=lambda x: x.move.uci())
    for c in sorted_moves:
        print("move (mcts):", c.move, " with score:", c.score)


def test_bayes_mcts():
    global lookup_count
    fools_mate = "rnbqkbnr/pppp1ppp/4p3/8/5PP1/8/PPPPP2P/RNBQKBNR b KQkq f3 0 2"
    board = chess.Board(fools_mate)
    seed = None
    strategy = RandomStrategy(random.Random(seed))
    mcts = BayesianMcts(board, strategy, chess.BLACK, seed)
    mcts.sample()
    mcts.print()
    for move, score in mcts.get_moves().items():
        print("move (mcts):", move, " with score:", score)


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


def test_evaluation():
    a = engine.ClassicMctsEngine
    b = engine.RandomEngine
    limit = engine.Limit(time=0.5)
    evaluator = simulation.Evaluation(a, b, limit)
    results = evaluator.run(1)
    a_results = len(list(filter(lambda x: x.winner == simulation.Winner.Engine_A, results))) / len(results) * 100
    b_results = len(list(filter(lambda x: x.winner == simulation.Winner.Engine_B, results))) / len(results) * 100
    draws = len(list(filter(lambda x: x.winner == simulation.Winner.Draw, results))) / len(results) * 100

    print(f"Engine {a.get_name()} won {a_results}% of games")
    print(f"Engine {b.get_name()} won {b_results}% of games")
    print(f"{draws}% of games resulted in a draw")


def main():
    # test_evaluation()
    test_simulate()
    # test_mcts()
    # test_stockfish()
    # test_stockfish_prob()
    # test_bayes_mcts()


if __name__ == '__main__':
    main()
