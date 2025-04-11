import pytest
from pyscrum.backlog import Backlog
from pyscrum.task import Task


def test_add_task():
    backlog = Backlog()
    task = Task("Backlog Task", "Testing add")
    backlog.add_task(task)

    assert task in backlog.tasks
    assert len(backlog.tasks) == 1


def test_add_duplicate_task():
    backlog = Backlog()
    task = Task("Duplicate Task")
    backlog.add_task(task)
    backlog.add_task(task)

    assert len(backlog.tasks) == 1  # Should not add twice


def test_remove_existing_task():
    backlog = Backlog()
    task = Task("Remove Me")
    backlog.add_task(task)
    backlog.remove_task(task.id)

    assert task not in backlog.tasks
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
