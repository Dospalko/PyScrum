import sqlite3
from .database import get_connection
from .task import Task

class Sprint:
    def __init__(self, name):
        self.name = name
        self.status = "Planned"
        self.tasks = []
        self._load_tasks()

    def _load_tasks(self):
        """Load tasks assigned to this sprint from the database."""
        try:
            with get_connection() as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS sprint_tasks (
                        sprint_name TEXT,
                        task_id TEXT,
                        PRIMARY KEY (sprint_name, task_id)
                    )
                """)
                cursor = conn.execute("""
                    SELECT task_id FROM sprint_tasks WHERE sprint_name=?
                """, (self.name,))
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

    def save(self):
        """Persist the sprint and task assignments to the database."""
        try:
            with get_connection() as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS sprints (
                        name TEXT PRIMARY KEY,
                        status TEXT DEFAULT 'Planned'
                    )
                """)
                conn.execute("""
                    INSERT OR REPLACE INTO sprints (name, status)
                    VALUES (?, ?)
                """, (self.name, self.status))
                for task in self.tasks:
                    conn.execute("""
                        INSERT OR IGNORE INTO sprint_tasks (sprint_name, task_id)
                        VALUES (?, ?)
                    """, (self.name, task.id))
        except sqlite3.OperationalError:
            pass

    def add_task(self, task):
        """Add a Task to the sprint."""
        if not isinstance(task, Task):
            raise TypeError("Sprint accepts only Task instances.")

        if any(t.id == task.id for t in self.tasks):
            return  # Avoid duplicates

        self.tasks.append(task)
        try:
            task.save()
            self.save()
        except (AttributeError, sqlite3.OperationalError):
            pass

    def remove_task(self, task_or_id):
        """Remove a Task by object or ID."""
        task_id = task_or_id.id if hasattr(task_or_id, 'id') else task_or_id
        self.tasks = [task for task in self.tasks if task.id != task_id]
        try:
            with get_connection() as conn:
                conn.execute("""
                    DELETE FROM sprint_tasks WHERE sprint_name=? AND task_id=?
                """, (self.name, task_id))
        except sqlite3.OperationalError:
            pass

    def get_tasks_by_status(self, status):
        """Return list of tasks filtered by status."""
        return [task for task in self.tasks if task.status == status]

    def list_tasks(self):
        """Return all tasks in the sprint."""
        return self.tasks

    def start(self):
        """Mark sprint as started."""
        self.status = "In Progress"
        self.save()

    def complete(self):
        """Mark sprint as completed."""
        self.status = "Completed"
        self.save()

    def update_name(self, new_name):
        """Update the sprint name in the DB and memory."""
        old_name = self.name
        try:
            with get_connection() as conn:
                conn.execute("""
                    UPDATE sprints SET name=? WHERE name=?
                """, (new_name, old_name))
                conn.execute("""
                    UPDATE sprint_tasks SET sprint_name=? WHERE sprint_name=?
                """, (new_name, old_name))
            self.name = new_name  # Update in-memory only after DB update succeeds
        except (sqlite3.OperationalError, sqlite3.IntegrityError):
            pass

    def __repr__(self):
        return f"<Sprint {self.name}: {len(self.tasks)} tasks>"
