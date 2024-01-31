import os
import asyncio

import aiohttp
from aiohttp import web

import chess
from chesspp import engine
from chesspp.engine_factory import EngineFactory
from chesspp.stockfish_strategy import StockFishStrategy
from chesspp.pesto_strategy import PestoStrategy

_DIR = os.path.abspath(os.path.dirname(__file__))
_DATA_DIR = os.path.abspath(os.path.join(_DIR, "static_data"))
_INDEX = os.path.join(_DATA_DIR, "index.html")


def load_index() -> str:
    """
        Load and return the chessboard html file from disk
    """
    with open(_INDEX, 'r') as fp:
        return fp.read()


class Simulate:
    """ Run a simulation of two engines"""
    def __init__(self, engine_white, engine_black):
        self.white = engine_white
        self.black = engine_black

    def run(self, limit: engine.Limit):
        board = chess.Board()

        is_white_playing = True
        while not board.is_game_over():
            play_result = self.white.play(board, limit) if is_white_playing else self.black.play(board, limit)
            board.push(play_result.move)
            yield board
            is_white_playing = not is_white_playing


class WebInterface:
    def __init__(self, white_engine, black_engine, strategy1, strategy2, stockfish_path, lc0_path, limit: engine.Limit):
        self.white = white_engine
        self.black = black_engine
        self.strategy1 = strategy1
        self.strategy2 = strategy2
        self.stockfish_path = stockfish_path
        self.lc0_path = lc0_path
        self.limit = limit


    async def handle_index(self, request) -> web.Response:
        """ Entry point of webpage, returns the index html"""
        return web.Response(text=load_index(), content_type='text/html')


    async def handle_websocket(self, request):
        """ Handles a websocket connection to the frontend"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)


        async def wait_msg():
            """ Handles messages from client """
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    if msg.data == 'close':
                        await ws.close()
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    print(f'ws connection closed with exception {ws.exception()}')


        async def turns():
            """ Simulates the game and sends the response to the client """
            white = EngineFactory.create_engine(self.white, self.strategy1, chess.WHITE, self.stockfish_path, self.lc0_path)
            black = EngineFactory.create_engine(self.black, self.strategy2, chess.BLACK, self.stockfish_path, self.lc0_path)
            runner = Simulate(white, black).run(self.limit)
            def sim():
                return next(runner, None)

            board = await asyncio.to_thread(sim)
            while board is not None:
                await ws.send_str(board.fen())
                board = await asyncio.to_thread(sim)


        async with asyncio.TaskGroup() as tg:
            tg.create_task(wait_msg())
            tg.create_task(turns())


        print('websocket connection closed')
        return ws

    def run_app(self):
        app = web.Application()
        app.add_routes([
            web.get('/', self.handle_index),
            web.get('/ws', self.handle_websocket),
            web.static('/img/chesspieces/wikipedia/', _DATA_DIR),
        ])
        web.run_app(app)
