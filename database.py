"""MariaDB adapter that preserves the small SQLite-style API used by app.py."""

import os
import threading
from pathlib import Path

import pymysql
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "127.0.0.1"),
    "port": int(os.environ.get("DB_PORT", 3306)),
    "user": os.environ.get("DB_USER", "jingum"),
    "password": os.environ.get("DB_PASSWORD", ""),
    "database": os.environ.get("DB_NAME", "jingum"),
    "charset": "utf8mb4",
    "connect_timeout": int(os.environ.get("DB_CONNECT_TIMEOUT", 10)),
    "autocommit": False,
}

_schema_ready = False
_schema_lock = threading.Lock()


class MariaDBConnection:
    """Expose execute/commit/close like the sqlite3 connection used previously."""

    def __init__(self, connection):
        self._connection = connection
        self._open_cursors = []

    @staticmethod
    def _translate_sql(sql):
        sql = sql.replace("INSERT OR REPLACE INTO", "REPLACE INTO")
        return sql.replace("?", "%s")

    def execute(self, sql, parameters=None):
        cursor = self._connection.cursor()
        self._open_cursors.append(cursor)
        cursor.execute(self._translate_sql(sql), parameters or ())
        return cursor

    def cursor(self):
        return self._connection.cursor()

    def commit(self):
        self._connection.commit()

    def rollback(self):
        self._connection.rollback()

    def close(self):
        for cursor in self._open_cursors:
            cursor.close()
        self._open_cursors.clear()
        self._connection.close()


def _connect():
    return MariaDBConnection(pymysql.connect(**DB_CONFIG))


def _ensure_schema(conn):
    global _schema_ready
    if _schema_ready:
        return
    with _schema_lock:
        if _schema_ready:
            return
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS records (
                collection VARCHAR(64) NOT NULL,
                doc_id VARCHAR(255) NOT NULL,
                data JSON NOT NULL,
                updated_at VARCHAR(40) NOT NULL,
                PRIMARY KEY (collection, doc_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
        )
        conn.commit()
        _schema_ready = True


def get_conn():
    """Return a MariaDB connection compatible with the former sqlite3 usage."""
    conn = _connect()
    try:
        _ensure_schema(conn)
        return conn
    except Exception:
        conn.close()
        raise


def init_db():
    """Create the schema without keeping a connection open."""
    get_conn().close()
