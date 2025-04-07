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
        self.tasks = []  # Clear existing tasks
        try:
            with get_connection() as conn:
                # Ensure table exists
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS sprint_tasks (
                        sprint_name TEXT,
                        task_id TEXT,
                        PRIMARY KEY (sprint_name, task_id)
                    )
                """)
                
                # Get unique task IDs for this sprint
                cursor = conn.execute("""
                    SELECT DISTINCT task_id 
                    FROM sprint_tasks 
                    WHERE sprint_name = ?
                """, (self.name,))
                
                # Load each task
                for (task_id,) in cursor.fetchall():
                    try:
                        task = Task.load(task_id)
                        if task and not any(t.id == task.id for t in self.tasks):
                            self.tasks.append(task)
                    except ValueError:
                        continue
        except sqlite3.OperationalError:
            pass

    def save(self):
        """Persist the sprint and task assignments to the database."""
        try:
            with get_connection() as conn:
                conn.execute("BEGIN")
                try:
                    # Ensure sprints table exists
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS sprints (
                            name TEXT PRIMARY KEY,
                            status TEXT DEFAULT 'Planned'
                        )
                    """)
                    
                    # Save sprint
                    conn.execute("""
                        INSERT OR REPLACE INTO sprints (name, status)
                        VALUES (?, ?)
                    """, (self.name, self.status))
                    
                    # Clear existing task assignments
                    conn.execute("DELETE FROM sprint_tasks WHERE sprint_name = ?", (self.name,))
                    
                    # Save task assignments
                    for task in self.tasks:
                        conn.execute("""
                            INSERT OR IGNORE INTO sprint_tasks (sprint_name, task_id)
                            VALUES (?, ?)
                        """, (self.name, task.id))
                    
                    conn.commit()
                except Exception as e:
                    conn.rollback()
                    raise e
        except sqlite3.OperationalError:
            pass

    def add_task(self, task):
        """Add a Task to the sprint."""
        if not isinstance(task, Task):
            raise TypeError("Sprint accepts only Task instances.")
        
        # Only add if not already in tasks
        if not any(t.id == task.id for t in self.tasks):
            task.save()  # Ensure task is saved first
            self.tasks.append(task)
            self.save()  # Update sprint_tasks table

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
        if new_name == self.name:
            return
            
        try:
            with get_connection() as conn:
                conn.execute("BEGIN")
                try:
                    # Update sprint name
                    conn.execute("""
                        INSERT OR REPLACE INTO sprints (name, status)
                        VALUES (?, ?)
                    """, (new_name, self.status))
                    
                    # Update task assignments
                    conn.execute("""
                        UPDATE sprint_tasks 
                        SET sprint_name = ? 
                        WHERE sprint_name = ?
                    """, (new_name, self.name))
                    
                    conn.commit()
                    self.name = new_name
                except Exception as e:
                    conn.rollback()
                    raise e
        except sqlite3.OperationalError:
            pass

    def __repr__(self):
        return f"<Sprint {self.name}: {len(self.tasks)} tasks>"

    @classmethod
    def delete(cls, name):
        """Remove a sprint and its associated tasks from the database.
        
        Args:
            name (str): The name of the sprint to delete
        """
        try:
            with get_connection() as conn:
                # First delete from sprint_tasks to maintain referential integrity
                conn.execute("""
                    DELETE FROM sprint_tasks WHERE sprint_name=?
                """, (name,))
                
                # Then delete the sprint itself
                conn.execute("""
                    DELETE FROM sprints WHERE name=?
                """, (name,))
        except sqlite3.OperationalError:
            pass
