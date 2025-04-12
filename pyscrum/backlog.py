import sqlite3
from .database import get_connection
from .task import Task


class Backlog:
    def __init__(self):
        self.tasks = []
        self._load_tasks()

    def _load_tasks(self):
        try:
            with get_connection() as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS backlog_tasks (
                        task_id TEXT PRIMARY KEY
                    )
                """
                )
                cursor = conn.execute("SELECT task_id FROM backlog_tasks")
                task_ids = cursor.fetchall()
                self.tasks = []
                for task_id in task_ids:
                    try:
                        task = Task.load(task_id[0])
                        self.tasks.append(task)
                    except ValueError:
                        pass
        except sqlite3.OperationalError:
            self.tasks = []

    def add_task(self, task):
        """Add a task to the backlog if it doesn't already exist."""
        if isinstance(task, str):
            task = Task(task)

        # Check if task with same ID already exists
        existing_task_ids = {t.id for t in self.tasks}
        if task.id not in existing_task_ids:
            self.tasks.append(task)
            try:
                with get_connection() as conn:
                    conn.execute(
                        """
                        INSERT OR IGNORE INTO backlog_tasks (task_id)
                        VALUES (?)
                        """,
                        (task.id,),
                    )
            except sqlite3.OperationalError:
                pass

    def remove_task(self, task_id):
        for task in self.tasks:
            if hasattr(task, "id") and task.id == task_id:
                self.tasks.remove(task)
                try:
                    with get_connection() as conn:
                        conn.execute(
                            "DELETE FROM backlog_tasks WHERE task_id=?", (task_id,)
                        )
                except sqlite3.OperationalError:
                    pass
                return
        raise ValueError(f"Task '{task_id}' not found in backlog")

    def get_task(self, task_id):
        for task in self.tasks:
            if hasattr(task, "id") and task.id == task_id:
                return task
        raise ValueError(f"Task '{task_id}' not found in backlog")

    def clear(self):
        self.tasks = []
        try:
            with get_connection() as conn:
                conn.execute("DELETE FROM backlog_tasks")
        except sqlite3.OperationalError:
            pass

    def __repr__(self):
        return f"<Backlog: {len(self.tasks)} tasks pending>"
