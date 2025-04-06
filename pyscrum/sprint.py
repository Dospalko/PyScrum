import uuid
from .database import get_connection
from .task import Task


class Sprint:
    def __init__(self, name, sprint_id=None):
        self.id = sprint_id or str(uuid.uuid4())
        self.name = name
        self.tasks = []

    def save(self):
        """Persist sprint to database."""
        with get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO sprints (id, name)
                VALUES (?, ?)
            """, (self.id, self.name))

    def add_task(self, task):
        """Assign a task to this sprint."""
        if not isinstance(task, Task):
            raise TypeError("Expected a Task instance")

        with get_connection() as conn:
            conn.execute("""
                INSERT INTO sprint_tasks (sprint_name, task_id)
                VALUES (?, ?)
            """, (self.name, task.id)) # Corrected from sprint_name to sprint_id

        self.tasks.append(task)  # Add to in-memory list too

    def list_tasks(self):
        """List all tasks assigned to this sprint."""
        if not self.tasks:  # Lazy load from DB if empty
            with get_connection() as conn:
                cursor = conn.execute("""
                    SELECT task_id FROM sprint_tasks WHERE sprint_id=?
                """, (self.id,))
                for row in cursor.fetchall():
                    self.tasks.append(Task.load(row[0]))
        return self.tasks

    @staticmethod
    def load(sprint_id):
        """Load sprint and its tasks from database."""
        with get_connection() as conn:
            cursor = conn.execute("SELECT id, name FROM sprints WHERE id=?", (sprint_id,))
            row = cursor.fetchone()
            if not row:
                raise ValueError("Sprint not found")

            sprint = Sprint(row[1], row[0])

            cursor = conn.execute("""
                SELECT task_id FROM sprint_tasks WHERE sprint_id=?
            """, (sprint_id,))
            for task_row in cursor.fetchall():
                sprint.tasks.append(Task.load(task_row[0]))

            return sprint

    def update_name(self, new_name):
        """Update sprint name."""
        self.name = new_name
        self.save()

    def __repr__(self):
        return f"<Sprint {self.id[:8]}: {self.name} ({len(self.tasks)} tasks)>"
