import chess
import chess.engine
from torch import distributions as dist

from baysed_chess.engine.i_engine import IEngine
from baysed_chess.limit import Limit
from baysed_chess.mcts.baysian_mcts import BayesianMcts
from baysed_chess.strategies.i_strategy import IStrategy


class BayesMctsEngine(IEngine):
    mcts: BayesianMcts
    """The Bayesian MCTS"""

    def __init__(self, board: chess.Board, color: chess.Color, strategy: IStrategy):
        super().__init__(board, color, strategy)
        self.mcts = BayesianMcts(board, self.strategy, self.color)
        self.node_counts = []

    @staticmethod
    def get_name() -> str:
        return "BayesMctsEngine"

    def play(self, board: chess.Board, limit: Limit) -> chess.engine.PlayResult:
        if len(board.move_stack) != 0:  # apply previous move to mcts --> reuse previous simulation results
            self.mcts.apply_move(board.peek())

        node_count = 0

        def do():
            nonlocal node_count
            self.mcts.sample(1)
            node_count += 1

        limit.run(do)
        self.node_counts.append(node_count)
        best_move = self.get_best_move(self.mcts.get_moves(), board.turn)
        self.mcts.apply_move(best_move)
        return chess.engine.PlayResult(move=best_move, ponder=None)

    @staticmethod
    def get_best_move(possible_moves: dict[chess.Move, dist.Normal], color: chess.Color) -> chess.Move:
        moves = {}
        for m, d in possible_moves.items():
            moves[m] = d.sample()

        return max(moves.items(), key=lambda x: x[1])[0] if color == chess.WHITE else (
            min(moves.items(), key=lambda x: x[1])[0])
