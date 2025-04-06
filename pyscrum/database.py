import sqlite3
from contextlib import contextmanager

DB_NAME = "pyscrum.db"

@contextmanager
def get_connection():
    """Context manager for database connections."""
    conn = sqlite3.connect(DB_NAME)
    try:
        yield conn
    finally:
        conn.commit()
        conn.close()


def init_db():
    """Initialize the database schema."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS sprints (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS sprint_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sprint_id TEXT NOT NULL,
                task_id TEXT NOT NULL,
                FOREIGN KEY (sprint_id) REFERENCES sprints(id),
                FOREIGN KEY (task_id) REFERENCES tasks(id),
                UNIQUE(sprint_id, task_id)
            );

        """)
