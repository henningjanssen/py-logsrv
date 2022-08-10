#!/usr/bin/env python3

from store import FileStore, PrintStore, SQLiteStore, MultiStore
from server import Server

if __name__ == '__main__':
    store = MultiStore([
        FileStore('logs.log'),
        PrintStore(),
        SQLiteStore('logs.sqlite'),
    ])
    server = Server(
        store = store
    )
