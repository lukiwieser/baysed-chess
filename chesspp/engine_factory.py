from enum import Enum

from chesspp.engine import *
from chesspp.lc0_strategy import Lc0Strategy
from chesspp.random_strategy import RandomStrategy
from chesspp.stockfish_strategy import StockFishStrategy
from chesspp.random_stockfish_strategy import RandomStockfishStrategy
from chesspp.pesto_strategy import PestoStrategy
from chesspp.i_strategy import IStrategy
import chess


class EngineEnum(Enum):
    ClassicMcts = 0
    BayesianMcts = 1
    Stockfish = 2
    Lc0 = 3
    Random = 4


class StrategyEnum(Enum):
    Stockfish = 0
    Lc0 = 1
    Random = 2
    RandomStockfish = 3
    Pestos = 4


class EngineFactory:

    @staticmethod
    def create_engine(engine_name: EngineEnum, strategy_name: StrategyEnum, color: chess.Color, stockfish_path: str, lc0_path: str, rollout_depth: int = 4) -> Engine:
        match strategy_name:
            case StrategyEnum.Stockfish:
                strategy = EngineFactory._get_stockfish_strategy(stockfish_path, rollout_depth)
            case StrategyEnum.Lc0:
                strategy = EngineFactory._get_lc0_strategy(lc0_path, rollout_depth)
            case StrategyEnum.Random:
                strategy = EngineFactory._get_random_strategy(rollout_depth)
            case StrategyEnum.RandomStockfish:
                strategy = EngineFactory._get_random_stockfish_strategy(stockfish_path, rollout_depth)
            case StrategyEnum.Pestos:
                strategy = EngineFactory._get_pesto_strategy(rollout_depth)

        match engine_name:
            case EngineEnum.ClassicMcts:
                return EngineFactory.classic_mcts(color, strategy)

            case EngineEnum.BayesianMcts:
                return EngineFactory.bayesian_mcts(color, strategy)

            case EngineEnum.Stockfish:
                return EngineFactory.stockfish_engine(color, stockfish_path)

            case EngineEnum.Lc0:
                return EngineFactory.lc0_engine(color, lc0_path)

    @staticmethod
    def stockfish_engine(color: chess.Color, engine_path: str, board: chess.Board | None = chess.Board()) -> Engine:
        return StockFishEngine(board, color, engine_path)

    @staticmethod
    def lc0_engine(color: chess.Color, engine_path: str, board: chess.Board | None = chess.Board()) -> Engine:
        return Lc0Engine(board, color, engine_path)

    @staticmethod
    def bayesian_mcts(color: chess.Color, strategy: IStrategy, board: chess.Board | None = chess.Board()) -> Engine:
        return BayesMctsEngine(board, color, strategy)

    @staticmethod
    def classic_mcts(color: chess.Color, strategy: IStrategy, board: chess.Board | None = chess.Board()) -> Engine:
        return ClassicMctsEngine(board, color, strategy)

    @staticmethod
    def _get_random_strategy(rollout_depth: int) -> IStrategy:
        return RandomStrategy(random.Random(), rollout_depth)

    @staticmethod
    def _get_stockfish_strategy(engine_path: str, rollout_depth: int) -> IStrategy:
        return StockFishStrategy(engine_path, rollout_depth)

    @staticmethod
    def _get_random_stockfish_strategy(engine_path: str, rollout_depth: int) -> IStrategy:
        return RandomStockfishStrategy(rollout_depth, engine_path)

    @staticmethod
    def _get_lc0_strategy(engine_path: str, rollout_depth: int) -> IStrategy:
        return Lc0Strategy(engine_path, rollout_depth)

    @staticmethod
    def _get_pesto_strategy(rollout_depth: int) -> IStrategy:
        return PestoStrategy(rollout_depth)
