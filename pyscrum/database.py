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
        # Check if the 'tags' column exists and migrate if needed
        columns = conn.execute("PRAGMA table_info(tasks)").fetchall()
        existing_columns = {col[1] for col in columns}

        if 'tags' not in existing_columns:
            # Recreate the tasks table with 'tags' if it's missing
            conn.execute("DROP TABLE IF EXISTS tasks")

        # Create updated tasks table with tags support
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'todo',
                priority TEXT DEFAULT 'medium',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tags TEXT DEFAULT ''
            )
            """
        )

        # Other tables
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sprints (
                name TEXT PRIMARY KEY,
                status TEXT DEFAULT 'Planned',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sprint_tasks (
                sprint_name TEXT,
                task_id TEXT,
                PRIMARY KEY (sprint_name, task_id),
                FOREIGN KEY (sprint_name) REFERENCES sprints(name),
                FOREIGN KEY (task_id) REFERENCES tasks(id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS backlog_tasks (
                task_id TEXT PRIMARY KEY,
                FOREIGN KEY (task_id) REFERENCES tasks(id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS task_comments (
                id TEXT PRIMARY KEY,
                task_id TEXT,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (task_id) REFERENCES tasks(id)
            )
            """
        )
