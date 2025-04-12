import uuid
from .database import get_connection


class Task:
    STATUS_OPTIONS = {"todo", "in_progress", "done"}
    PRIORITY_OPTIONS = {"high", "medium", "low"}

    def __init__(self, title, description="", status="todo", task_id=None, priority="medium"):
        self.id = task_id or str(uuid.uuid4())
        self.title = title
        self.description = description
        self.status = status
        self.priority = priority

    def save(self):
        """Persist task to database."""
        with get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO tasks (id, title, description, status, priority)
                VALUES (?, ?, ?, ?, ?)
            """,
                (self.id, self.title, self.description, self.status, self.priority),
            )

    @staticmethod
    def load(task_id):
        """Load task from database."""
        with get_connection() as conn:
            cursor = conn.execute(
                "SELECT id, title, description, status, priority FROM tasks WHERE id=?",
                (task_id,),
            )
            row = cursor.fetchone()
            if row:
                task = Task(row[1], row[2], row[3], row[0])
                task.priority = row[4]
                return task
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
    def list_all(status=None, priority=None):
        """List all tasks, optionally filtered by status and/or priority."""
        with get_connection() as conn:
            query = "SELECT id, title, description, status, priority FROM tasks"
            conditions = []
            params = []
            
            if status:
                conditions.append("status = ?")
                params.append(status)
            if priority:
                conditions.append("priority = ?")
                params.append(priority)
                
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
                
            cursor = conn.execute(query, params)
            tasks = []
            for row in cursor.fetchall():
                task = Task(row[1], row[2], row[3], row[0])
                task.priority = row[4]
                tasks.append(task)
            return tasks

    @staticmethod
    def load_by_prefix(prefix):
        """Load task by ID prefix (at least 3 chars)."""
        if len(prefix) < 3:
            raise ValueError("Prefix must be at least 3 characters long")
        
        with get_connection() as conn:
            cursor = conn.execute(
                "SELECT id, title, description, status, priority FROM tasks WHERE id LIKE ?",
                (f"{prefix}%",),
            )
            rows = cursor.fetchall()
            if not rows:
                raise ValueError(f"No task found with prefix '{prefix}'")
            if len(rows) > 1:
                raise ValueError(f"Multiple tasks found with prefix '{prefix}'")
            
            row = rows[0]
            task = Task(row[1], row[2], row[3], row[0])
            task.priority = row[4]
            return task

    def __repr__(self):
        return f"<Task {self.id[:8]}: {self.title} [{self.status}]>"
