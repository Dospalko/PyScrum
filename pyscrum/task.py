import uuid

class Task:
    STATUS_OPTIONS = {"todo", "in_progress", "done"}

    def __init__(self, title, description=""):
        # Generate a unique task identifier
        self.id = str(uuid.uuid4())
        self.title = title
        self.description = description
        self.status = "todo"

    def set_status(self, status):
        if status in self.STATUS_OPTIONS:
            self.status = status
        else:
            raise ValueError(f"Invalid status: {status}")

    def __repr__(self):
        # Short representation for clarity
        return f"<Task {self.id[:8]}: {self.title} [{self.status}]>"
