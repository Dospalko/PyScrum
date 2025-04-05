from .database import get_connection
from .task import Task

class Sprint:
    def __init__(self, name):
        self.name = name
        self.tasks = []
        self._load_tasks()

    def _load_tasks(self):
        """Load associated tasks from database."""
        with get_connection() as conn:
            cursor = conn.execute("""
                SELECT task_id FROM sprint_tasks WHERE sprint_name=?
            """, (self.name,))
            task_ids = cursor.fetchall()
            self.tasks = [Task.load(task_id[0]) for task_id in task_ids]

    def save(self):
        """Persist sprint to database."""
        with get_connection() as conn:
            conn.execute("INSERT OR IGNORE INTO sprints (name) VALUES (?)", (self.name,))
            for task in self.tasks:
                conn.execute("""
                    INSERT OR IGNORE INTO sprint_tasks (sprint_name, task_id)
                    VALUES (?, ?)
                """, (self.name, task.id))

    def add_task(self, task):
        if task not in self.tasks:
            self.tasks.append(task)
            task.save()
            self.save()

    def remove_task(self, task_id):
        self.tasks = [task for task in self.tasks if task.id != task_id]
        with get_connection() as conn:
            conn.execute("""
                DELETE FROM sprint_tasks WHERE sprint_name=? AND task_id=?
            """, (self.name, task_id))

    def get_tasks_by_status(self, status):
        return [task for task in self.tasks if task.status == status]

    def __repr__(self):
        return f"<Sprint {self.name}: {len(self.tasks)} tasks>"
