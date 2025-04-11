import pytest
from pyscrum.task import Task
from pyscrum.database import get_connection


def test_create_task():
    task = Task("Login Page", "Implement frontend login")
    assert task.title == "Login Page"
    assert task.description == "Implement frontend login"
    assert task.status == "todo"
    assert len(task.id) > 0


def test_save_and_load_task():
    task = Task("Save/Load Test", "Check DB persistence")
    task.save()

    loaded = Task.load(task.id)
    assert loaded.title == task.title
    assert loaded.description == task.description
    assert loaded.status == task.status
    assert loaded.id == task.id


def test_set_valid_status():
    task = Task("Status Test")
    task.set_status("in_progress")
    assert task.status == "in_progress"

    task.set_status("done")
    assert task.status == "done"


def test_set_invalid_status():
    task = Task("Invalid Status Test")
    with pytest.raises(ValueError):
        task.set_status("blocked")


def test_update_description():
    task = Task("Description Update", "Old description")
    task.update_description("New description")
    assert task.description == "New description"


def test_repr_format():
    task = Task("Repr Test", "Check __repr__")
    result = repr(task)
    assert task.title in result
    assert task.status in result
    assert task.id[:8] in result
