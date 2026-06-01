import sqlite3
import threading
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent.parent / "data" / "twilio.db"


class Database:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls) -> "Database":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._conn = None
        return cls._instance

    def connect(self) -> sqlite3.Connection:
        if self._conn is None:
            DB_PATH.parent.mkdir(parents=True, exist_ok=True)
            self._conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA foreign_keys=ON")
            self._create_tables()
        return self._conn

    def _create_tables(self) -> None:
        self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL UNIQUE,
                avatar_color TEXT NOT NULL DEFAULT '#128C7E',
                created_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
            );

            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contact_id INTEGER NOT NULL,
                direction TEXT NOT NULL CHECK(direction IN ('sent','received')),
                content TEXT NOT NULL,
                channel TEXT NOT NULL DEFAULT 'sms',
                status TEXT NOT NULL DEFAULT 'sent',
                created_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
                FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS call_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contact_id INTEGER NOT NULL,
                direction TEXT NOT NULL CHECK(direction IN ('incoming','outgoing')),
                duration INTEGER NOT NULL DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'completed',
                created_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
                FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_messages_contact ON messages(contact_id);
            CREATE INDEX IF NOT EXISTS idx_call_logs_contact ON call_logs(contact_id);
        """)
        self._conn.commit()

    def get_conn(self) -> sqlite3.Connection:
        if self._conn is None:
            return self.connect()
        return self._conn

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None
