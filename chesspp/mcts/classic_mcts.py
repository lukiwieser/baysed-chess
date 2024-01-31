import chess
import random
import numpy as np
from chesspp.i_strategy import IStrategy


class ClassicMcts:

    def __init__(self, board: chess.Board, color: chess.Color, strategy: IStrategy, parent=None, move: chess.Move | None = None,
                 random_state: int | None = None):
        self.random = random.Random(random_state)
        self.board = board
        self.color = color
        self.strategy = strategy
        self.parent = parent
        self.move = move
        self.children = []
        self.visits = 0
        self.legal_moves = list(board.legal_moves)
        self.untried_actions = self.legal_moves
        self.score = 0

    def _expand(self) -> 'ClassicMcts':
        """
        Expands the node, i.e., choose an action and apply it to the board
        :return:
        """
        move = self.random.choice(self.untried_actions)
        self.untried_actions.remove(move)
        next_board = self.board.copy()
        next_board.push(move)
        child_node = ClassicMcts(next_board, color=not self.color, strategy=self.strategy, parent=self, move=move)
        self.children.append(child_node)
        return child_node

    def _rollout(self, rollout_depth: int = 4) -> int:
        """
        Rolls out the node by simulating a game for a given depth.
        Sometimes this step is called 'simulation' or 'playout'.
        :return: the score of the rolled out game
        """
        copied_board = self.board.copy()
        steps = 1
        for i in range(rollout_depth):
            if copied_board.is_game_over():
                break

            m = self.strategy.pick_next_move(copied_board)
            copied_board.push(m)
            steps += 1

        return self.strategy.analyze_board(copied_board) // steps

    def _backpropagate(self, score: float) -> None:
        """
        Backpropagates the results of the rollout
        :param score:
        :return:
        """
        self.visits += 1
        # TODO: maybe use score + num of moves together (a win in 1 move is better than a win in 20 moves)
        self.score += score
        if self.parent:
            self.parent._backpropagate(score)

    def is_fully_expanded(self) -> bool:
        return len(self.untried_actions) == 0

    def _best_child(self) -> 'ClassicMcts':
        """
        Picks the best child according to our policy
        :return: the best child
        """
        # NOTE: maybe clamp the score between [-1, +1] instead of [-inf, +inf]
        choices_weights = [(c.score / c.visits) + np.sqrt(((2 * np.log(self.visits)) / c.visits))
                           for c in self.children]
        best_child_index = np.argmax(choices_weights) if self.color == chess.WHITE else np.argmin(choices_weights)
        return self.children[best_child_index]

    def _select_leaf(self) -> 'ClassicMcts':
        """
        Selects a leaf node.
        If the node is not expanded is will be expanded.
        :return: Leaf node
        """
        current_node = self
        while not current_node.board.is_game_over():
            if not current_node.is_fully_expanded():
                return current_node._expand()
            else:
                current_node = current_node._best_child()

        return current_node

    def build_tree(self, samples: int = 1000) -> 'ClassicMcts':
        """
        Runs the MCTS with the given number of samples
        :param samples: number of simulations
        :return: best node containing the best move
        """
        for i in range(samples):
            # selection & expansion
            # rollout
            # backpropagate score
            node = self._select_leaf()
            score = node._rollout()
            node._backpropagate(score)

        return self._best_child()
