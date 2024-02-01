import chess
from chesspp.i_strategy import IStrategy
from chesspp.mcts.classic_mcts_node_v2 import ClassicMctsNodeV2


class ClassicMctsV2:
    def __init__(self, board: chess.Board, color: chess.Color, strategy: IStrategy):
        self.board = board
        self.color = color
        self.strategy = strategy
        self.root = ClassicMctsNodeV2(board, color, strategy)

    def build_tree(self, samples: int = 1000):
        """
        Runs the MCTS with the given number of samples
        :param samples: number of simulations
        :return: best node containing the best move
        """
        for i in range(samples):
            node = self.root._select_leaf()
            score = node._rollout()
            node._backpropagate(score)


