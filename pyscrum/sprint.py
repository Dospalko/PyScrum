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

    @classmethod
    def delete(cls, name):
        """Delete a sprint from the database, including its tasks from the sprint_tasks table."""
        try:
            with get_connection() as conn:
                conn.execute("DELETE FROM sprint_tasks WHERE sprint_name=?", (name,))
                conn.execute("DELETE FROM sprints WHERE name=?", (name,))
        except sqlite3.OperationalError:
            pass

    @classmethod
    def from_name(cls, name):
        """Load a Sprint instance from the database by its name, including its tasks."""
        try:
            with get_connection() as conn:
                cursor = conn.execute("SELECT name, status FROM sprints WHERE name=?", (name,))
                row = cursor.fetchone()
                if not row:
                    raise ValueError(f"Sprint '{name}' not found.")

                # Create a new Sprint instance with the loaded name
                sprint = cls(row[0])
                sprint.status = row[1]
                sprint._load_tasks()  # Load tasks from DB

                return sprint
        except sqlite3.OperationalError as e:
            raise RuntimeError(f"Database error while loading sprint '{name}': {e}")

    def get_tasks_by_status(self, status, export_to=None):
        """Return tasks in sprint filtered by status. Optionally export to file."""
        filtered = [task for task in self.tasks if task.status == status]

        if export_to:
            from pathlib import Path
            from html import escape
            filename = export_to.lower()
            if filename.endswith(".csv"):
                import csv
                with open(filename, mode="w", newline="", encoding="utf-8") as file:
                    writer = csv.writer(file)
                    writer.writerow(["Task ID", "Title", "Description", "Status"])
                    for t in filtered:
                        writer.writerow([t.id, t.title, t.description, t.status])
            elif filename.endswith(".html"):
                html = f"""<html><head><title>{status} Tasks in Sprint {self.name}</title></head><body>
                <h2>Tasks with status '{status}'</h2><table border="1">
                <tr><th>ID</th><th>Title</th><th>Description</th><th>Status</th></tr>
                {''.join(f"<tr><td>{escape(t.id)}</td><td>{escape(t.title)}</td><td>{escape(t.description)}</td><td>{t.status}</td></tr>" for t in filtered)}
                </table></body></html>"""
                Path(filename).write_text(html, encoding="utf-8")

        return filtered

    @classmethod
    def list_all(cls):
        """Return a list of all Sprint instances stored in the database."""
        sprints = []
        try:
            with get_connection() as conn:
                cursor = conn.execute("SELECT name, status FROM sprints")
                for row in cursor.fetchall():
                    sprint = cls(row[0])
                    sprint.status = row[1]
                    sprint._load_tasks()
                    sprints.append(sprint)
        except sqlite3.OperationalError:

            pass
        return sprints
