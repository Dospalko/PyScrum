import pytest
from pyscrum.backlog import Backlog

def test_add_task():
    backlog = Backlog()
    backlog.add_task("Task 1")
    assert "Task 1" in backlog.tasks

def test_remove_task():
    backlog = Backlog()
    backlog.add_task("Task 1")
    backlog.remove_task("Task 1")
    assert "Task 1" not in backlog.tasks

def test_get_task():
    backlog = Backlog()
    backlog.add_task("Task 1")
    task = backlog.get_task("Task 1")
    assert task == "Task 1"

def test_get_task_not_found():
    backlog = Backlog()
    with pytest.raises(ValueError):
        backlog.get_task("Task 404")

def test_clear_backlog():
    backlog = Backlog()
    backlog.add_task("Task 1")
    backlog.add_task("Task 2")
    backlog.clear()
    assert backlog.tasks == []

def test_remove_task_not_found():
    backlog = Backlog()
    backlog.add_task("Task 1")

    with pytest.raises(ValueError):
        backlog.remove_task("Task 404")
