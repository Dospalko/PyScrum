import pytest
import os
from pyscrum.backlog import Backlog
from pyscrum.task import Task
from pyscrum.database import init_db


@pytest.fixture(autouse=True)
def setup_database():
    """Setup a fresh database for each test."""
    if os.path.exists("pyscrum.db"):
        os.remove("pyscrum.db")
    init_db()
    yield
    if os.path.exists("pyscrum.db"):
        os.remove("pyscrum.db")


def test_add_task():
    backlog = Backlog()
    task = Task("Backlog Task", "Testing add")
    backlog.add_task(task)

    assert task in backlog.tasks
    assert len(backlog.tasks) == 1


def test_add_duplicate_task():
    backlog = Backlog()
    
    # Create first task
    task = Task("Duplicate Task")
    task_id = task.id
    backlog.add_task(task)
    
    # Create second task with same ID
    duplicate_task = Task("Duplicate Task")
    duplicate_task.id = task_id  # Force same ID
    backlog.add_task(duplicate_task)
    
    # Verify only one task exists
    assert len(backlog.tasks) == 1
    assert backlog.tasks[0].id == task_id


def test_remove_existing_task():
    backlog = Backlog()
    task = Task("Remove Me")
    backlog.add_task(task)
    
    # Clear any other tasks that might be in the backlog
    backlog.tasks = [task]  # Reset to only contain our test task
    
    backlog.remove_task(task.id)
    assert len(backlog.tasks) == 0


def test_remove_nonexistent_task():
    backlog = Backlog()
    with pytest.raises(ValueError):
        backlog.remove_task("nonexistent-id")


def test_get_existing_task():
    backlog = Backlog()
    task = Task("Find Me")
    backlog.add_task(task)
    found = backlog.get_task(task.id)

    assert found == task


def test_get_nonexistent_task():
    backlog = Backlog()
    with pytest.raises(ValueError):
        backlog.get_task("ghost-id")


def test_clear_backlog():
    backlog = Backlog()
    task1 = Task("Task 1")
    task2 = Task("Task 2")
    backlog.add_task(task1)
    backlog.add_task(task2)

    backlog.clear()
    assert len(backlog.tasks) == 0


def test_repr_format():
    backlog = Backlog()
    task = Task("Repr Test")
    backlog.add_task(task)

    result = repr(backlog)
    assert "Backlog" in result
    assert "1 tasks" in result
