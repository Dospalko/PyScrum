class Sprint:
    def __init__(self, name):
        self.name = name
        self.tasks = []

    def add_task(self, task):
        if task not in self.tasks:
            self.tasks.append(task)

    def remove_task(self, task_id):
        self.tasks = [task for task in self.tasks if task.id != task_id]

    def get_tasks_by_status(self, status):
        return [task for task in self.tasks if task.status == status]

    def __repr__(self):
        return f"<Sprint {self.name}: {len(self.tasks)} tasks>"
