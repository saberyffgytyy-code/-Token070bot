import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.config import BOT_DB_PATH


def ensure_db() -> str:
    db_path = Path(BOT_DB_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    db_path.touch(exist_ok=True)
    return str(db_path)


def init_db() -> None:
    db_path = ensure_db()
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS searches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                query TEXT NOT NULL,
                source TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )


def log_search(user_id: int, query: str, source: str) -> None:
    db_path = ensure_db()
    timestamp = datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO searches (user_id, query, source, created_at) VALUES (?, ?, ?, ?)",
            (user_id, query, source, timestamp),
        )


def get_recent_searches(user_id: int, limit: int = 10):
    db_path = ensure_db()
    with sqlite3.connect(db_path) as conn:
        return conn.execute(
            "SELECT query, source, created_at FROM searches WHERE user_id = ? ORDER BY id DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()


def get_usage_stats():
    db_path = ensure_db()
    with sqlite3.connect(db_path) as conn:
        total_searches = conn.execute("SELECT COUNT(*) FROM searches").fetchone()[0]
        unique_users = conn.execute("SELECT COUNT(DISTINCT user_id) FROM searches").fetchone()[0]

        last_24h = datetime.now(timezone.utc) - timedelta(hours=24)
        recent_searches = conn.execute(
            "SELECT COUNT(*) FROM searches WHERE created_at >= ?",
            (last_24h.isoformat(),),
        ).fetchone()[0]

        return {
            "total_searches": total_searches,
            "unique_users": unique_users,
            "recent_24h": recent_searches,
        }
