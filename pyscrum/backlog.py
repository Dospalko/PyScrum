import pytest

from pyscrum.task import Task
from pyscrum.sprint import Sprint

class Backlog:
    def __init__(self):
        self.tasks = []

    def add_task(self, task):
        self.tasks.append(task)

    def remove_task(self, task):
        if task in self.tasks:
            self.tasks.remove(task)
        else:
            raise ValueError("Task not found")

    def get_task(self, task):
        if task in self.tasks:
            return task
        raise ValueError("Task not found")

    def clear(self):
        self.tasks.clear()
