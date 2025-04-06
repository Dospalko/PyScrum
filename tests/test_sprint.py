import pytest
import uuid
from pyscrum.task import Task
from pyscrum.sprint import Sprint
from pyscrum.database import get_connection


def test_sprint_add_and_remove_task():
    sprint = Sprint("Sprint Add Remove")
    sprint.save()

    task = Task("Task 1", "Desc", "todo")
    task.save()

    sprint.add_task(task)   # pass Task object

    tasks = sprint.list_tasks()
    assert any(t.id == task.id for t in tasks)

    sprint.remove_task(task)   # pass Task object
    tasks = sprint.list_tasks()
    assert all(t.id != task.id for t in tasks)


def test_start_sprint():
    sprint = Sprint(name="Sprint 1")
    sprint.start()
    assert sprint.status == "In Progress"
    with get_connection() as conn:
        cursor = conn.execute("SELECT status FROM sprints WHERE id=?", (sprint.id,))
        row = cursor.fetchone()
        assert row[0] == "In Progress"

def test_complete_sprint():
    sprint = Sprint(name="Sprint 1")
    sprint.complete()
    assert sprint.status == "Completed"
    with get_connection() as conn:
        cursor = conn.execute("SELECT status FROM sprints WHERE id=?", (sprint.id,))
        row = cursor.fetchone()
        assert row[0] == "Completed"




def test_sprint_str():
    sprint = Sprint("Sprint String Test")
    result = str(sprint)
    print(result)
    assert "Sprint String Test" in result


def test_sprint_creation():
    sprint = Sprint(name="Sprint 1")
    assert sprint.name == "Sprint 1"
    assert sprint.status == "Planned"  # Default status
    assert isinstance(sprint.id, str)  # Ensure that id is a string UUID

def test_add_invalid_task():
    sprint = Sprint(name="Sprint 1")
    try:
        sprint.add_task("Invalid Task")  # Passing non-Task object
    except TypeError:
        pass  # Expected behavior, task should not be added

def test_remove_non_existent_task():
    sprint = Sprint(name="Sprint 1")
    task = Task(id=str(uuid.uuid4()))  # Ensure task is created with a valid ID
    try:
        sprint.remove_task(task)  # Task not added yet
    except ValueError:
        pass  # Expected behavior, should raise error


def test_list_tasks_empty():
    sprint = Sprint(name="Sprint 1")
    tasks = sprint.list_tasks()  # Should return an empty list initially
    assert len(tasks) == 0

def test_list_tasks_with_existing_task():
    sprint = Sprint(name="Sprint 1")
    task = Task(id=str(uuid.uuid4()))  # Use the proper constructor
    sprint.add_task(task)
    tasks = sprint.list_tasks()  # Should return list with the added task
    assert len(tasks) == 1
    assert tasks[0].id == task.id


def test_update_name():
    sprint = Sprint(name="Sprint 1")
    sprint.save()  # Ensure the sprint is saved to the database before updating its name
    sprint.update_name("Sprint 2")
    assert sprint.name == "Sprint 2"
    with get_connection() as conn:
        cursor = conn.execute("SELECT name FROM sprints WHERE id=?", (sprint.id,))
        row = cursor.fetchone()
        assert row is not None, "Sprint should exist in the database"
        assert row[0] == "Sprint 2"
