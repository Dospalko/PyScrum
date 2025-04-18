import sqlite3
from datetime import datetime
from .database import get_connection
from .task import Task


class Sprint:
    VALID_STATUSES = {"Planned", "In Progress", "Completed", "Archived"}
    MAX_NAME_LENGTH = 50  # Maximum allowed length for sprint name

    @staticmethod
    def validate_name(name: str) -> tuple[bool, str]:
        """
        Validate sprint name.
        Returns (is_valid, error_message)
        """
        if not name or name.isspace():
            return False, "Sprint name cannot be empty"
        if len(name) > Sprint.MAX_NAME_LENGTH:
            return False, f"Sprint name cannot be longer than {Sprint.MAX_NAME_LENGTH} characters"
        return True, ""

    def __init__(self, name: str):
        is_valid, error_message = self.validate_name(name)
        if not is_valid:
            raise ValueError(error_message)
        self.name = name
        self._status = "Planned"  # Use private attribute
        self.tasks = []
        self._load_tasks()

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        if value not in self.VALID_STATUSES:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(self.VALID_STATUSES)}")
        self._status = value
        self.save()

    def _load_tasks(self):
        """Load tasks assigned to this sprint from the database."""
        try:
            with get_connection() as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS sprint_tasks (
                        sprint_name TEXT,
                        task_id TEXT,
                        PRIMARY KEY (sprint_name, task_id)
                    )
                """
                )
                cursor = conn.execute(
                    """
                    SELECT task_id FROM sprint_tasks WHERE sprint_name=?
                """,
                    (self.name,),
                )
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
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS sprints (
                        name TEXT PRIMARY KEY,
                        status TEXT DEFAULT 'Planned'
                    )
                """
                )
                conn.execute(
                    """
                    INSERT OR REPLACE INTO sprints (name, status)
                    VALUES (?, ?)
                """,
                    (self.name, self.status),
                )
                for task in self.tasks:
                    conn.execute(
                        """
                        INSERT OR IGNORE INTO sprint_tasks (sprint_name, task_id)
                        VALUES (?, ?)
                    """,
                        (self.name, task.id),
                    )
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
        task_id = task_or_id.id if hasattr(task_or_id, "id") else task_or_id
        self.tasks = [task for task in self.tasks if task.id != task_id]
        try:
            with get_connection() as conn:
                conn.execute(
                    """
                    DELETE FROM sprint_tasks WHERE sprint_name=? AND task_id=?
                """,
                    (self.name, task_id),
                )
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
                conn.execute(
                    """
                    UPDATE sprints SET name=? WHERE name=?
                """,
                    (new_name, old_name),
                )
                conn.execute(
                    """
                    UPDATE sprint_tasks SET sprint_name=? WHERE sprint_name=?
                """,
                    (new_name, old_name),
                )
            self.name = new_name  # Update in-memory only after DB update succeeds
        except (sqlite3.OperationalError, sqlite3.IntegrityError):
            pass

    def __repr__(self):
        stats = self.get_statistics()
        return f"<Sprint {self.name}: {len(self.tasks)} tasks, {stats['progress']:.1f}% complete>"

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
                cursor = conn.execute(
                    "SELECT name, status FROM sprints WHERE name=?", (name,)
                )
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

    def archive(self):
        """Archive the sprint."""
        if self.status == "Archived":
            return
        
        self.status = "Archived"
        self.save()

    def get_statistics(self):
        """Get sprint statistics."""
        total = len(self.tasks)
        if total == 0:
            return {
                "total": 0,
                "done": 0,
                "in_progress": 0,
                "todo": 0,
                "progress": 0.0
            }
        
        done = len([t for t in self.tasks if t.status == "done"])
        in_progress = len([t for t in self.tasks if t.status == "in_progress"])
        todo = len([t for t in self.tasks if t.status == "todo"])
        
        progress = (done / total * 100) if total > 0 else 0.0
        
        return {
            "total": total,
            "done": done,
            "in_progress": in_progress,
            "todo": todo,
            "progress": progress
        }
    
    def get_tasks_by_priority(self, priority):
        """Get tasks with specified priority."""
        return [task for task in self.tasks if task.priority == priority]

    @classmethod
    def from_name_prefix(cls, prefix: str):
        """Load sprint by name prefix (requires unique match)."""
        if len(prefix) < 3:
            raise ValueError("Prefix too short, must be at least 3 characters.")

        with get_connection() as conn:
            cursor = conn.execute(
                "SELECT name, status FROM sprints WHERE name LIKE ?", (f"{prefix}%",)
            )
            rows = cursor.fetchall()
            if not rows:
                raise ValueError("Sprint not found.")
            if len(rows) > 1:
                raise ValueError("Multiple sprints match the prefix.")

            name, status = rows[0]
            sprint = cls(name)
            sprint.status = status
            sprint._load_tasks()
            return sprint

    @classmethod
    def list_all(cls):
        """Return a list of all Sprint instances stored in the database."""
        sprints = []
        try:
            with get_connection() as conn:
                # Ensure tables exist
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS sprints (
                        name TEXT PRIMARY KEY,
                        status TEXT DEFAULT 'Planned'
                    )
                """)
                
                cursor = conn.execute("SELECT name, status FROM sprints")
                for row in cursor.fetchall():
                    sprint = cls(row[0])
                    sprint.status = row[1]
                    sprint._load_tasks()
                    sprints.append(sprint)
        except sqlite3.OperationalError:
            pass
        return sprints
    
    def search_tasks(self, query: str) -> list[Task]:
        """
        Vyhľadá všetky úlohy v tomto sprinte,
        ktorých názov alebo popis obsahuje zadaný reťazec (case‑insensitive).
        Vracia zoznam Task objektov.
        """
        q = query.lower()
        return [
            task
            for task in self.tasks
            if q in task.title.lower() or q in task.description.lower()
        ]

    @classmethod
    def clear_all(cls):
        """Clear all sprints from the database."""
        try:
            with get_connection() as conn:
                conn.execute("DELETE FROM sprints")
                conn.execute("DELETE FROM sprint_tasks")
        except sqlite3.OperationalError:
            pass

    @classmethod
    def exists(cls, name: str) -> bool:
        """Check if a sprint with the given name already exists."""
        try:
            with get_connection() as conn:
                cursor = conn.execute(
                    "SELECT COUNT(*) FROM sprints WHERE name=?", 
                    (name,)
                )
                count = cursor.fetchone()[0]
                return count > 0
        except sqlite3.OperationalError:
            return False
