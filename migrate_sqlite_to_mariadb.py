"""One-time migration of Jingum records from SQLite to MariaDB."""

import argparse
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from database import get_conn, init_db


def parse_updated_at(value):
    """Convert an SQLite ISO timestamp to a timezone-free UTC datetime."""
    if not value:
        return datetime.now(timezone.utc).replace(tzinfo=None)
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if parsed.tzinfo is not None:
            parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)
        return parsed
    except ValueError:
        return datetime.now(timezone.utc).replace(tzinfo=None)


def migrate(sqlite_path, overwrite=False):
    sqlite_path = Path(sqlite_path).resolve()
    if not sqlite_path.is_file():
        raise FileNotFoundError(f"SQLite file not found: {sqlite_path}")

    source = sqlite3.connect(f"file:{sqlite_path.as_posix()}?mode=ro", uri=True)
    try:
        rows = source.execute(
            "SELECT collection, doc_id, data, updated_at FROM records"
        ).fetchall()
    finally:
        source.close()

    init_db()
    target = get_conn()
    try:
        with target.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM records")
            existing = cursor.fetchone()[0]
            if existing and not overwrite:
                raise RuntimeError(
                    f"MariaDB already contains {existing} records. "
                    "Use --overwrite only if existing records may be replaced."
                )

            cursor.executemany(
                """
                INSERT INTO records (collection, doc_id, data, updated_at)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    data = VALUES(data),
                    updated_at = VALUES(updated_at)
                """,
                [
                    (collection, doc_id, data, parse_updated_at(updated_at))
                    for collection, doc_id, data, updated_at in rows
                ],
            )
        target.commit()
    except Exception:
        target.rollback()
        raise
    finally:
        target.close()

    print(f"Migrated {len(rows)} records from {sqlite_path} to MariaDB.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("sqlite_path", nargs="?", default="data.db")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="replace matching records when the MariaDB table is not empty",
    )
    args = parser.parse_args()
    migrate(args.sqlite_path, overwrite=args.overwrite)
