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
        with get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO tasks (id, title, description, status)
                VALUES (?, ?, ?, ?)
            """, (self.id, self.title, self.description, self.status))

    @staticmethod

    def get_all_tasks():
        with get_connection() as conn:
            cursor = conn.execute("SELECT id, title, description, status FROM tasks")
            rows = cursor.fetchall()

        return [Task(title=row[1], description=row[2], status=row[3], task_id=row[0]) for row in rows]

    def load(task_id):
        with get_connection() as conn:
            cursor = conn.execute("""
                SELECT id, title, description, status FROM tasks WHERE id=?
            """, (task_id,))
            row = cursor.fetchone()
            if not row:
                raise ValueError("Task not found")
            return Task(row[1], row[2], row[3], row[0])

    def set_status(self, status):
        if status not in self.STATUS_OPTIONS:
            raise ValueError("Invalid status")
        self.status = status
        self.save()

    def update_status(self, new_status):
        self.set_status(new_status)

    def update_description(self, new_description):
        self.description = new_description
        self.save()

    def exists(task_id):
        with get_connection() as conn:
            cursor = conn.execute("SELECT 1 FROM tasks WHERE id = ?", (task_id,))
            return cursor.fetchone() is not None
    
    def __repr__(self):
        return f"<Task {self.id[:8]}: {self.title} [{self.status}]>"
