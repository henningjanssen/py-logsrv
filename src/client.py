#!/usr/bin/env python3

import asyncio
import socket
from queue import Queue
from struct import unpack_from
from time import sleep, time
from threading import Thread
from uuid import uuid4

import websockets

from store import Entry

class Client:
    def __init__(self, client_type: str, host: str = None, port: int = 6789):
        hostname = f'{host}:{port}' if host is not None else f'{socket.gethostname()}.local:{port}'
        self._client_id = str(uuid4())
        self._client_type = client_type
        self._queue = Queue()

        async def log_sender():
            nonlocal self
            async with websockets.connect(f'ws://{hostname}') as websocket:
                while True:
                    msg = self._queue.get()
                    print(msg)
                    await websocket.send(msg)

        def run_loop():
            asyncio.run(log_sender())
        self._asyncio_thread = Thread(target=run_loop)
        self._asyncio_thread.start()

    def log(self, data: dict):
        entry = Entry(
            client_id = self._client_id,
            client_type = self._client_type,
            timestamp = time(),
            data = data,
        )
        self._queue.put(str(entry))

if __name__ == '__main__':
    client = Client('test')

    while True:
        payload = {
            'test': 'data',
            'timestamp': time(),
            'randstuff': uuid4().hex,
        }
        client.log(payload)
        sleep(1/5)
