from uuid import uuid4

class Task:
    def __init__(self, title, description=""):
        self.id = str(uuid4())  # Unikátne ID tasku
        self.title = title      # Názov tasku
        self.description = description  # Popis
        self.status = "todo"    # Stav: todo, in_progress, done

    def set_status(self, status):
        if status in ["todo", "in_progress", "done"]:
            self.status = status
        else:
            raise ValueError("Invalid status")

    def __repr__(self):
        return f"[{self.status.upper()}] {self.title} (ID: {self.id[:8]})"
