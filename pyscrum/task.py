import uuid
from .database import get_connection

class Task:
    STATUS_OPTIONS = {"todo", "in_progress", "done"}

    def __init__(self, title, description="", status="todo", task_id=None):
        self.id = task_id or str(uuid.uuid4())
        self.title = title
        self.description = description
        self.status = status

    def save(self):
        """Persist task to database."""
        with get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO tasks (id, title, description, status)
                VALUES (?, ?, ?, ?)
            """, (self.id, self.title, self.description, self.status))

    @staticmethod
    def load(task_id):
        """Load task from database."""
        with get_connection() as conn:
            cursor = conn.execute("SELECT id, title, description, status FROM tasks WHERE id=?", (task_id,))
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

    # Add alias method for set_status to match tests
    def update_status(self, status):
        """Alias for set_status to maintain backward compatibility."""
        return self.set_status(status)

    # Add update_description method
    def update_description(self, description):
        """Update the task's description."""
        self.description = description
        self.save()
        return self

    def __repr__(self):
        return f"<Task {self.id[:8]}: {self.title} [{self.status}]>"