import uuid
from .database import get_connection
from .task import Task

class Sprint:
    def __init__(self, name, sprint_id=None, status='Planned'):
        self.id = sprint_id or str(uuid.uuid4())
        self.name = name
        self._status = status  # Internal use for status
        self.tasks = []

    @property
    def status(self):
        return self._status  # Getter for status

    @status.setter
    def status(self, value):
        if value not in ['Planned', 'In Progress', 'Completed']:
            raise ValueError("Invalid status")
        self._status = value  # Setter for status

    def save(self):
        with get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO sprints (id, name, status)
                VALUES (?, ?, ?)
            """, (self.id, self.name, self._status))

    def add_task(self, task):
        if not isinstance(task, Task):
            raise TypeError("Expected a Task instance")

        # Ensure task is saved before adding it to the sprint
        task.save()  # Ensure task is saved in the database

        with get_connection() as conn:
            conn.execute("INSERT INTO sprint_tasks (sprint_id, task_id) VALUES (?, ?)", (self.id, task.id))

        self.tasks.append(task)

    def remove_task(self, task):
        if isinstance(task, str):  # If a task ID is passed as a string
            task = Task.load(task)  # Load the Task object by ID
        elif not isinstance(task, Task):  # If it’s not a Task object, raise an error
            raise TypeError("Expected a Task instance or task ID string")

        # Check if task exists in the sprint_tasks before removing it
        with get_connection() as conn:
            cursor = conn.execute("SELECT 1 FROM sprint_tasks WHERE sprint_id = ? AND task_id = ?", (self.id, task.id))
            if not cursor.fetchone():
                raise ValueError(f"Task with ID {task.id} not found in sprint {self.name}")

            conn.execute("DELETE FROM sprint_tasks WHERE sprint_id = ? AND task_id = ?", (self.id, task.id))

        # Remove task from the list of tasks
        self.tasks = [t for t in self.tasks if t.id != task.id]


    def list_tasks(self):
        if not self.tasks:
            with get_connection() as conn:
                cursor = conn.execute("""
                    SELECT task_id FROM sprint_tasks WHERE sprint_id=?
                """, (self.id,))
                for row in cursor.fetchall():
                    task = Task.load(row[0])
                    if task:  # Ensure that the task exists in the database
                        self.tasks.append(task)
                    else:
                        raise ValueError(f"Task with ID {row[0]} not found in the database")
        return self.tasks


    @staticmethod
    def load(sprint_name):
        with get_connection() as conn:
            cursor = conn.execute("""
                SELECT id, name, status FROM sprints WHERE name=?
            """, (sprint_name,))
            row = cursor.fetchone()
            if not row:
                raise ValueError("Sprint not found")

            sprint = Sprint(row[1], sprint_id=row[0], status=row[2])

            cursor = conn.execute("""
                SELECT task_id FROM sprint_tasks WHERE sprint_id=?
            """, (row[0],))
            for task_row in cursor.fetchall():
                sprint.tasks.append(Task.load(task_row[0]))

            return sprint

    def start(self):
        self.status = 'In Progress'  # Using the setter
        self.save()

    def complete(self):
        self.status = 'Completed'  # Using the setter
        self.save()

    def update_name(self, new_name):
        with get_connection() as conn:
            conn.execute("""
                UPDATE sprints SET name=? WHERE id=?
            """, (new_name, self.id))

        self.name = new_name

    def __repr__(self):
        return f"<Sprint {self.name} [{self._status}]: ({len(self.tasks)} tasks)>"
