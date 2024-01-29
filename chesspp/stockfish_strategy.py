import chess
from chesspp.i_strategy import IStrategy
import chess.engine


class StockFishStrategy(IStrategy):
    stockfish: chess.engine.SimpleEngine

    def __init__(self):
        self.stockfish = chess.engine.SimpleEngine.popen_uci(
            "/home/luke/projects/pp-project/chess-engine-pp/stockfish/stockfish-ubuntu-x86-64-avx2")

    def pick_next_move(self, board: chess.Board) -> chess.Move | None:
        move = self.stockfish.play(board, chess.engine.Limit(depth=4)).move
        print("stockfish picked:", move)
        return move
