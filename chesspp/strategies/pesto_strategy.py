import chess
import chess.engine

from chesspp.board_evaluations.evaluate_pestos import score_pestos
from chesspp.strategies.i_strategy import IStrategy


class PestoStrategy(IStrategy):
    def __init__(self, rollout_depth: int = 4):
        super().__init__(rollout_depth)

    def pick_next_move(self, board: chess.Board) -> chess.Move | None:
        def score_move(move: chess.Move):
            bc = board.copy(stack=False)
            bc.push(move)
            return move, score_pestos(bc)

        moves = [score_move(move) for move in board.legal_moves]
        if board.turn != chess.WHITE:
            best_move = max(moves, key=lambda m: m[1])
        else:
            best_move = min(moves, key=lambda m: m[1])
        return best_move[0]

    def analyze_board(self, board: chess.Board) -> int:
        return score_pestos(board)
