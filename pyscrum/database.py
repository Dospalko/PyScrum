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
                name TEXT PRIMARY KEY
            );

            CREATE TABLE IF NOT EXISTS sprint_tasks (
                sprint_name TEXT,
                task_id TEXT,
                PRIMARY KEY (sprint_name, task_id),
                FOREIGN KEY (sprint_name) REFERENCES sprints(name),
                FOREIGN KEY (task_id) REFERENCES tasks(id)
            );
        """)
