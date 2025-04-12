import uuid
from .database import get_connection


class Task:
    STATUS_OPTIONS = {"todo", "in_progress", "done"}
    PRIORITY_OPTIONS = {"high", "medium", "low"}
    
    def __init__(self, title, description="", status="todo", task_id=None):
        self.id = task_id or str(uuid.uuid4())
        self.title = title
        self.description = description
        self.status = status

    def save(self):
        """Persist task to database."""
        with get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO tasks (id, title, description, status)
                VALUES (?, ?, ?, ?)
            """,
                (self.id, self.title, self.description, self.status),
            )

    @staticmethod
    def load(task_id):
        """Load task from database."""
        with get_connection() as conn:
            cursor = conn.execute(
                "SELECT id, title, description, status FROM tasks WHERE id=?",
                (task_id,),
            )
            row = cursor.fetchone()
            if row:
                return Task(row[1], row[2], row[3], row[0])
            else:
                raise ValueError("Task not found")

    def set_status(self, status):
        if status not in self.STATUS_OPTIONS:
            raise ValueError("Invalid status")
        self.status = status
        self.save()

    def update_status(self, status):
        """Alias for set_status."""
        return self.set_status(status)

    def update_description(self, description):
        """Update task description."""
        self.description = description
        self.save()
        return self

    @staticmethod
    def search(query):
        """Search for tasks by title or description."""
        results = []
        try:
            with get_connection() as conn:
                cursor = conn.execute(
                    """
                    SELECT id, title, description, status
                    FROM tasks
                    WHERE title LIKE ? OR description LIKE ?
                """,
                    (f"%{query}%", f"%{query}%"),
                )
                for row in cursor.fetchall():
                    task = Task(row[1], row[2], row[3], row[0])
                    results.append(task)
        except sqlite3.OperationalError:
            pass
        return results

    @staticmethod
    def list_all(status=None):
        """Return all tasks from DB, optionally filtered by status."""
        tasks = []
        try:
            with get_connection() as conn:
                if status:
                    cursor = conn.execute(
                        "SELECT id, title, description, status FROM tasks WHERE status=?",
                        (status,),
                    )
                else:
                    cursor = conn.execute(
                        "SELECT id, title, description, status FROM tasks"
                    )
                for row in cursor.fetchall():
                    tasks.append(Task(row[1], row[2], row[3], row[0]))
        except sqlite3.OperationalError:
            pass
        return tasks

    @staticmethod
    def load_by_prefix(prefix: str):
        """Load task by ID prefix (min. 4 chars)."""
        if len(prefix) < 4:
            raise ValueError("Prefix too short, must be at least 4 characters.")

        with get_connection() as conn:
            cursor = conn.execute(
                "SELECT id, title, description, status FROM tasks WHERE id LIKE ?",
                (f"{prefix}%",),
            )
            matches = cursor.fetchall()
            if not matches:
                raise ValueError("Task not found.")
            if len(matches) > 1:
                raise ValueError("Multiple tasks match the prefix.")

            row = matches[0]
            return Task(row[1], row[2], row[3], row[0])

    def __repr__(self):
        return f"<Task {self.id[:8]}: {self.title} [{self.status}]>"
