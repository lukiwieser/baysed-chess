from lichess_bot.lib.engine_wrapper import MinimalEngine, MOVE
import chess.engine

from chesspp import engine


class ProbStockfish(MinimalEngine):
    def search(self, board: chess.Board, time_limit: chess.engine.Limit, ponder: bool, draw_offered: bool,
               root_moves: MOVE) -> chess.engine.PlayResult:
        moves = {}
        untried_moves = list(board.legal_moves)
        for move in untried_moves:
            mean, std = engine.simulate_game(board, move, 10)
            moves[move] = (mean, std)

        return self.get_best_move(moves)

    def get_best_move(self, moves: dict) -> chess.engine.PlayResult:
        best_avg = max(moves.items(), key=lambda m: m[1][0])
        next_move = best_avg[0]
        return chess.engine.PlayResult(next_move, None)
