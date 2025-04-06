class Backlog:
  
    def __init__(self):
        self.tasks = []

    def add_task(self, task):
        self.tasks.append(task)

    def remove_task(self, task_id):
         self.tasks = [task for task in self.tasks if task.id != task_id]

    def move_task_to_sprint(self, task_id, sprint):
        task = next((t for t in self.tasks if t.id == task_id), None)
        if task:
            sprint.add_task(task)
            self.tasks.remove(task)
        else:
            raise ValueError("Task not found in backlog")

    def __repr__(self):
        return f"<Backlog: {len(self.tasks)} tasks pending>"
