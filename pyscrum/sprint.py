import uuid
from .database import get_connection
from .task import Task


class Sprint:
    def __init__(self, name, sprint_id=None):
        self.id = sprint_id or str(uuid.uuid4())
        self.name = name
        self.tasks = []

    def save(self):
        with get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO sprints (name)
                VALUES (?)
            """, (self.name,))

    def add_task(self, task):
        if not isinstance(task, Task):
            raise TypeError("Expected a Task instance")

        with get_connection() as conn:
            conn.execute("""
                INSERT OR IGNORE INTO sprint_tasks (sprint_name, task_id)
                VALUES (?, ?)
            """, (self.name, task.id))

        self.tasks.append(task)

    def list_tasks(self):
        if not self.tasks:
            with get_connection() as conn:
                cursor = conn.execute("""
                    SELECT task_id FROM sprint_tasks WHERE sprint_name=?
                """, (self.name,))
                for row in cursor.fetchall():
                    self.tasks.append(Task.load(row[0]))
        return self.tasks

    @staticmethod
    def load(sprint_name):
        with get_connection() as conn:
            cursor = conn.execute("SELECT name FROM sprints WHERE name=?", (sprint_name,))
            row = cursor.fetchone()
            if not row:
                raise ValueError("Sprint not found")

            sprint = Sprint(row[0])

            cursor = conn.execute("""
                SELECT task_id FROM sprint_tasks WHERE sprint_name=?
            """, (sprint_name,))
            for task_row in cursor.fetchall():
                sprint.tasks.append(Task.load(task_row[0]))

            return sprint

    def update_name(self, new_name):
        with get_connection() as conn:
            # Update in sprints table
            conn.execute("""
                UPDATE sprints SET name=? WHERE name=?
            """, (new_name, self.name))

            # Update in sprint_tasks table
            conn.execute("""
                UPDATE sprint_tasks SET sprint_name=? WHERE sprint_name=?
            """, (new_name, self.name))

        self.name = new_name

    def __repr__(self):
        return f"<Sprint {self.name}: ({len(self.tasks)} tasks)>"

    def remove_task(self, task_id):
        with get_connection() as conn:
            conn.execute("""
                DELETE FROM sprint_tasks WHERE task_id=? AND sprint_name=?
            """, (task_id, self.name))

        # Remove from local list as well
        self.tasks = [task for task in self.tasks if task.id != task_id]