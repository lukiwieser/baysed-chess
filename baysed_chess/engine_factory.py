import random
from enum import Enum

import chess

from baysed_chess.engine.bayes_mcts_engine import BayesMctsEngine
from baysed_chess.engine.classic_mcts_engine import ClassicMctsEngine
from baysed_chess.engine.i_engine import IEngine
from baysed_chess.engine.lc0_engine import Lc0Engine
from baysed_chess.engine.stockfish_engine import StockfishEngine
from baysed_chess.strategies.i_strategy import IStrategy
from baysed_chess.strategies.lc0_strategy import Lc0Strategy
from baysed_chess.strategies.pesto_strategy import PestoStrategy
from baysed_chess.strategies.random_stockfish_strategy import RandomStockfishStrategy
from baysed_chess.strategies.random_strategy import RandomStrategy
from baysed_chess.strategies.stockfish_strategy import StockfishStrategy


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
    """ Class to create Engines with the given parameters """

    @staticmethod
    def create_engine(engine_name: EngineEnum, strategy_name: StrategyEnum, color: chess.Color, stockfish_path: str,
                      lc0_path: str, stockfish_elo: int, rollout_depth: int = 4) -> IEngine:
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
            case _:
                raise ValueError(f"strategy_name={strategy_name} not supported")

        match engine_name:
            case EngineEnum.ClassicMcts:
                return EngineFactory._get_classic_mcts_engine(color, strategy)
            case EngineEnum.BayesianMcts:
                return EngineFactory._get_bayesian_mcts_engine(color, strategy)
            case EngineEnum.Stockfish:
                return EngineFactory._get_stockfish_engine(color, stockfish_path, stockfish_elo)
            case EngineEnum.Lc0:
                return EngineFactory._get_lc0_engine(color, lc0_path)

    @staticmethod
    def _get_stockfish_engine(color: chess.Color, engine_path: str, stockfish_elo: int) -> IEngine:
        return StockfishEngine(chess.Board(), color, stockfish_elo, engine_path)

    @staticmethod
    def _get_lc0_engine(color: chess.Color, engine_path: str) -> IEngine:
        return Lc0Engine(chess.Board(), color, engine_path)

    @staticmethod
    def _get_bayesian_mcts_engine(color: chess.Color, strategy: IStrategy) -> IEngine:
        return BayesMctsEngine(chess.Board(), color, strategy)

    @staticmethod
    def _get_classic_mcts_engine(color: chess.Color, strategy: IStrategy) -> IEngine:
        return ClassicMctsEngine(chess.Board(), color, strategy)

    @staticmethod
    def _get_random_strategy(rollout_depth: int) -> IStrategy:
        return RandomStrategy(random.Random(), rollout_depth)

    @staticmethod
    def _get_stockfish_strategy(engine_path: str, rollout_depth: int) -> IStrategy:
        return StockfishStrategy(engine_path, rollout_depth)

    @staticmethod
    def _get_random_stockfish_strategy(engine_path: str, rollout_depth: int) -> IStrategy:
        return RandomStockfishStrategy(rollout_depth, engine_path)

    @staticmethod
    def _get_lc0_strategy(engine_path: str, rollout_depth: int) -> IStrategy:
        return Lc0Strategy(engine_path, rollout_depth)

    @staticmethod
    def _get_pesto_strategy(rollout_depth: int) -> IStrategy:
        return PestoStrategy(rollout_depth)
