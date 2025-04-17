import uuid
from datetime import datetime
from .database import get_connection


class Task:
    STATUS_OPTIONS = {"todo", "in_progress", "done"}
    PRIORITY_OPTIONS = {"high", "medium", "low"}

    def __init__(self, title, description="", priority="medium"):
        self.id = str(uuid.uuid4())
        self.title = title
        self.description = description
        self.status = "todo"
        self.priority = priority
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        self.save()

    def save(self):
        """Persist task to database."""
        self.updated_at = datetime.now().isoformat()
        
        with get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO tasks 
                (id, title, description, status, priority, created_at, updated_at) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (self.id, self.title, self.description, self.status, 
                 self.priority, self.created_at, self.updated_at),
            )

    @classmethod
    def load(cls, task_id):
        """Load a task from the database."""
        with get_connection() as conn:
            row = conn.execute(
                """
                SELECT id, title, description, status, priority, created_at, updated_at
                FROM tasks WHERE id = ?
                """,
                (task_id,),
            ).fetchone()
            
            if row is None:
                raise ValueError(f"No task found with ID {task_id}")
                
            task = cls(row[1], row[2], row[4])  # title, description, priority
            task.id = row[0]
            task.status = row[3]
            task.created_at = row[5]
            task.updated_at = row[6]
            return task

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
        with get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT id, title, description, status, priority
                FROM tasks
                WHERE title LIKE ? OR description LIKE ?
                """,
                (f"%{query}%", f"%{query}%"),
            )
            for row in cursor.fetchall():
                # Create task instance without saving
                task = Task.__new__(Task)
                task.id = row[0]
                task.title = row[1]
                task.description = row[2]
                task.status = row[3]
                task.priority = row[4]
                results.append(task)
        return results

    @staticmethod
    def list_all(status=None, priority=None):
        """List all tasks, optionally filtered by status and/or priority."""
        with get_connection() as conn:
            query = """SELECT id, title, description, status, priority, created_at 
                      FROM tasks"""
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
                task = Task.__new__(Task)
                task.id = row[0]
                task.title = row[1]
                task.description = row[2]
                task.status = row[3]
                task.priority = row[4]
                task.created_at = row[5]
                tasks.append(task)
            return tasks

    @staticmethod
    def load_by_prefix(prefix):
        """Load task by ID prefix (at least 3 chars)."""
        if len(prefix) < 3:
            raise ValueError("Prefix must be at least 3 characters long")
        
        with get_connection() as conn:
            cursor = conn.execute(
                """SELECT id, title, description, status, priority, created_at 
                   FROM tasks WHERE id LIKE ?""",
                (f"{prefix}%",),
            )
            rows = cursor.fetchall()
            if not rows:
                raise ValueError(f"No task found with prefix '{prefix}'")
            if len(rows) > 1:
                raise ValueError(f"Multiple tasks found with prefix '{prefix}'")
            
            row = rows[0]
            task = Task.__new__(Task)
            task.id = row[0]
            task.title = row[1]
            task.description = row[2]
            task.status = row[3]
            task.priority = row[4]
            task.created_at = row[5]
            return task

    @classmethod
    def load_all(cls):
        """Load all tasks from the database."""
        with get_connection() as conn:
            cursor = conn.execute("SELECT id, title, description, status, priority FROM tasks")
            tasks = []
            for row in cursor:
                # Create task instance without saving
                task = cls.__new__(cls)
                task.id = row[0]
                task.title = row[1]
                task.description = row[2]
                task.status = row[3]
                task.priority = row[4]
                tasks.append(task)
            return tasks

    @classmethod
    def clear_all(cls):
        """Clear all tasks from the database."""
        try:
            with get_connection() as conn:
                conn.execute("DELETE FROM tasks")
        except sqlite3.OperationalError:
            pass

    def set_priority(self, priority):
        """Set the priority of the task."""
        if priority not in ["low", "medium", "high"]:
            raise ValueError("Priority must be one of: low, medium, high")
        self.priority = priority
        self.save()
    
    def is_high_priority(self):
        """
        Skontroluje, či je priorita úlohy nastavená na 'high'.
        Vracia True, ak áno, inak False.
        """
        return self.priority == "high"

    def toggle_status(self):
        """
        Preklikne status úlohy:
        - "todo"       → "in_progress"
        - "in_progress"→ "done"
        - "done"       → "todo"
        Uloží zmenu do DB a vráti self pre prípadné chainovanie.
        """
        # poradie statusov
        order = ["todo", "in_progress", "done"]
        # nájdi aktuálny index a preklikni na ďalší (s wrap-around)
        current_idx = order.index(self.status)
        new_idx = (current_idx + 1) % len(order)
        self.status = order[new_idx]
        # ulož do DB
        self.save()
        return self

    def age_in_days(self):
        """
        Vráti počet dní (vrátane desatinnej časti) 
        ktoré ubehli od vytvorenia úlohy.
        """
        # parsed = datetime objekt z uloženého ISO reťazca
        created_dt = datetime.fromisoformat(self.created_at)
        # rozdiel medzi teraz a časom vytvorenia
        delta = datetime.now() - created_dt
        # prepočet sekúnd na dni
        return delta.total_seconds() / 86400
    
    def age_in_seconds(self):
        """
        Vráti počet sekúnd, ktoré ubehli od vytvorenia úlohy.
        """
        created_dt = datetime.fromisoformat(self.created_at)
        delta = datetime.now() - created_dt
        return delta.total_seconds()
    
    def __repr__(self):
        return f"<Task {self.id}: {self.title} ({self.status}) [{self.priority}]>"
