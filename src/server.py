import asyncio
import json
from threading import Thread

import websockets

from store import Entry, Store

class Server:
    def __init__(self, store: Store, host: str = '0.0.0.0', port: int = 6789):
        async def handler(websocket, path):
            nonlocal store
            try:
                while True:
                    msg = await websocket.recv()
                    entry = Entry(**json.loads(msg))
                    store.store(entry)
            except websockets.exceptions.ConnectionClosed:
                await websocket.close()
            except Exception as e:
                print('Server client exception:', e)
                pass
        self._event_loop = asyncio.new_event_loop()
        self._socket = self._event_loop.run_until_complete(websockets.serve(ws_handler=handler, host=host, port=port, loop=self._event_loop, max_size=None))

        def run_loop():
            nonlocal self
            try:
                self._event_loop.run_forever()
            finally:
                self._event_loop.run_until_complete(self._event_loop.shutdown_asyncgens())
                self._event_loop.close()
        self._asyncio_thread = Thread(target=run_loop)
        self._asyncio_thread.start()
