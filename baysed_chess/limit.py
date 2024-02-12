import time

import chess
import chess.engine


class Limit:
    """ Class to determine when to stop searching for moves """

    time: float | None
    """ Search for `time` seconds """

    nodes: int | None
    """ Search for a limited number of `nodes`"""

    def __init__(self, time: float | None = None, nodes: int | None = None):
        self.time = time
        self.nodes = nodes
        self.node_count = 0

    def run(self, func, *args, **kwargs):
        """
        Run `func` until the limit condition is reached
        :param func: the func that performs one search iteration
        :param *args: are passed to `func`
        :param **kwargs: are passed to `func`
        """

        if self.nodes:
            self._run_nodes(func, *args, **kwargs)
            self.node_count = self.nodes
        elif self.time:
            self._run_time(func, *args, **kwargs)

    def _run_nodes(self, func, *args, **kwargs):
        for _ in range(self.nodes):
            func(*args, **kwargs)

    def _run_time(self, func, *args, **kwargs):
        start = time.perf_counter_ns()
        while (time.perf_counter_ns() - start) / 1e9 < self.time:
            func(*args, **kwargs)
            self.node_count += 1

    def translate_to_engine_limit(self) -> chess.engine.Limit:
        if self.nodes:
            return chess.engine.Limit(nodes=self.nodes)
        elif self.time:
            return chess.engine.Limit(time=self.time)
