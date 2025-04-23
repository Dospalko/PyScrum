import sqlite3
from .database import get_connection
from .task import Task


class Backlog:
    def __init__(self):
        self.tasks = []
        self._load_tasks()

    @classmethod
    def load(cls):
        """Load backlog from database."""
        backlog = cls()
        try:
            with get_connection() as conn:
                cursor = conn.execute("SELECT task_id FROM backlog_tasks")
                task_ids = [row[0] for row in cursor.fetchall()]
                backlog.tasks = [Task.load(task_id) for task_id in task_ids]
        except sqlite3.OperationalError:
            pass
        return backlog

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

    def list_by_status(self, status: str):
        """Return list of tasks filtered by status."""
        if status not in Task.STATUS_OPTIONS:
            raise ValueError("Invalid status")
        return [task for task in self.tasks if task.status == status]
    
    def list_by_priority(self, priority: str):
        """Return list of tasks filtered by priority."""
        if priority not in Task.PRIORITY_OPTIONS:
            raise ValueError("Invalid priority")
        return [task for task in self.tasks if task.priority == priority]

    def find_by_tag(self, tag: str):
        """Return tasks that contain the given tag."""
        return [task for task in self.tasks if hasattr(task, 'tags') and tag in task.tags]
    
    def sort_by_due_date(self):
        """Return tasks sorted by due date (None at the end)."""
        return sorted(self.tasks, key=lambda t: t.due_date or datetime.max)

    def has_task(self, task_id: str):
        """Check if a task with the given ID is in the backlog."""
        return any(task.id == task_id for task in self.tasks)


    def __repr__(self):
        return f"<Backlog: {len(self.tasks)} tasks pending>"
