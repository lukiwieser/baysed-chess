import chess
from chesspp.strategies.i_strategy import IStrategy
from chesspp.mcts.classic_mcts_node_v2 import ClassicMctsNodeV2
from chesspp.mcts.i_mcts import IMcts
from chesspp.mcts.i_mcts_node import IMctsNode


class ClassicMctsV2(IMcts):
    def __init__(self, board: chess.Board, color: chess.Color, strategy: IStrategy, seed: int | None = None):
        super().__init__(board, strategy, seed)
        self.color = color
        self.root = ClassicMctsNodeV2(board, color, strategy, None, None, self.random_state)

    def apply_move(self, move: chess.Move) -> None:
        pass

    def get_children(self) -> list[IMctsNode]:
        return self.root.children

    def sample(self, samples: int = 1000):
        """
        Runs the MCTS with the given number of samples
        :param samples: number of simulations
        :return: best node containing the best move
        """
        for i in range(samples):
            node = self.root.select().expand()
            score = node.rollout()
            node.backpropagate(score)
