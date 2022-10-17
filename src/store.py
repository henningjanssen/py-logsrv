from abc import ABC, abstractmethod
from dataclasses import dataclass
import json
from pathlib import Path
import sqlite3
from threading import Lock

@dataclass
class Entry:
    client_id: str
    client_type: str
    timestamp: int
    data_type: str
    data: dict

    def __str__(self):
        return json.dumps(
            {
                'client_id': self.client_id,
                'client_type': self.client_type,
                'timestamp': self.timestamp,
                'data_type': self.data_type,
                'data': self.data,
            },
            separators=(',', ':')
        )

class Store(ABC):
    @abstractmethod
    def store(self, entry: Entry) -> bool:
        return False

class FileStore(Store):
    def __init__(self, path: Path):
        self._path = path

    def store(self, entry: Entry) -> bool:
        with open(self._path, 'a+') as f:
            f.write(f'{str(entry)}\n')
        return True

class PrintStore(Store):
    def store(self, entry: Entry):
        print(str(entry))
        return True

class SQLiteStore(Store):
    def __init__(self, file: Path):
        self._connection = sqlite3.connect(file, check_same_thread=False)
        self._lock = Lock()

        self._connection.execute('''
            create table if not exists logentries (
                id integer primary key autoincrement,
                client_id text not null,
                client_type text not null,
                timestamp int not null,
                data_type text not null,
                data json
            );
        ''')

    def store(self, entry: Entry) -> bool:
        with self._lock:
            self._connection.execute(
                '''
                insert into logentries (
                    client_id,
                    client_type,
                    timestamp,
                    data_type,
                    data
                ) values (
                    :client_id,
                    :client_type,
                    :timestamp,
                    :data_type,
                    :data
                )
                ''',
                {
                    'client_id': entry.client_id,
                    'client_type': entry.client_type,
                    'timestamp': entry.timestamp,
                    'data_type': entry.data_type,
                    'data': json.dumps(entry.data)
                }
            )
            self._connection.commit()
        return True

class MultiStore(Store):
    def __init__(self, stores: list[Store]):
        self._stores = stores

    def add_store(self, store: Store) -> Store:
        self._stores.append(store)
        return self

    def store(self, entry: Entry) -> bool:
        for store in self._stores:
            store.store(entry)
        return True
