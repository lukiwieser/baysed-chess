import os
import asyncio
import aiohttp
from aiohttp import web

import chess
from chesspp import engine

_DIR = os.path.abspath(os.path.dirname(__file__))
_INDEX = os.path.join(_DIR, "res/index.html")

def load_index():
    with open(_INDEX, 'r') as fp:
        return fp.read()


index_data = load_index()

async def handle_index(request):
    #raise web.HTTPFound('/index.html')
    return web.Response(text=load_index(), content_type='text/html')

class Simulate:
    def __init__(self):
        self.white = engine.ClassicMctsEngine(chess.WHITE)
        self.black = engine.ClassicMctsEngine(chess.BLACK)

    def run(self):
        board = chess.Board()

        is_white_playing = True
        while not board.is_game_over():
            play_result = self.white.play(board) if is_white_playing else self.black.play(board)
            yield play_result.move
            board.push(play_result.move)
            is_white_playing = not is_white_playing


async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async def wait_msg():
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                if msg.data == 'close':
                    await ws.close()
            elif msg.type == aiohttp.WSMsgType.ERROR:
                print(f'ws connection closed with exception {ws.exception()}')
    
    async def turns():
        runner = Simulate().run()
        def sim():
            return next(runner, None) 

        turn = await asyncio.to_thread(sim)
        while turn is not None:
            await ws.send_str(turn.uci())
            turn = await asyncio.to_thread(sim)
    
    async with asyncio.TaskGroup() as tg:
        tg.create_task(wait_msg())
        tg.create_task(turns())

    print('websocket connection closed')

    return ws


app = web.Application()
app.add_routes([
    web.get('/', handle_index),
    #web.static('/', os.path.join(_DIR, 'res')),
    web.static('/img/chesspieces/wikipedia/', os.path.join(_DIR, 'res')),
    web.get('/ws', websocket_handler),
])

if __name__ == '__main__':
    web.run_app(app)
