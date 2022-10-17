#!/usr/bin/env python3

import asyncio
import socket
from queue import Empty, Queue
from struct import unpack_from
from time import sleep, time
from threading import Thread
from uuid import uuid4

import websockets

from .store import Entry

class Client:
    def __init__(self, client_type: str, host: str = None, port: int = 6789):
        hostname = f'{host}:{port}' if host is not None else f'{socket.gethostname()}.local:{port}'
        print('Hostname:', hostname)
        self._client_id = str(uuid4())
        self._client_type = client_type
        self._queue = Queue()
        self._abort = False

        async def log_sender():
            nonlocal self
            async with websockets.connect(f'ws://{hostname}') as websocket:
                while not self._abort:
                    try:
                        msg = self._queue.get(True, 2)
                        self._queue.task_done()
                        await websocket.send(msg)
                    except Empty:
                        pass

        def run_loop():
            asyncio.run(log_sender())
        self._asyncio_thread = Thread(target=run_loop)
        self._asyncio_thread.start()

    def log(self, data_type: str, data: dict):
        entry = Entry(
            client_id = self._client_id,
            client_type = self._client_type,
            timestamp = time(),
            data_type = data_type,
            data = data,
        )
        self._queue.put(str(entry))

    def stop(self):
        self._abort = True
        self._asyncio_thread.join()

if __name__ == '__main__':
    client = Client('test')#, '127.0.0.1')

    while True:
        payload = {
            'test': 'data',
            'timestamp': time(),
            'randstuff': uuid4().hex,
        }
        client.log('nonsense', payload)
        sleep(1/5)
