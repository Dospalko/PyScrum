import pytest
from pyscrum.sprint import Sprint
from pyscrum.task import Task

def test_sprint_creation():
    sprint = Sprint("Test Sprint")
    assert sprint.name == "Test Sprint"
    assert sprint.status == "Planned"  # Capital P in actual implementation

def test_sprint_add_task():
    sprint = Sprint("Test Sprint")
    task = Task("Test Task")
    sprint.add_task(task)
    assert task in sprint.tasks

def test_sprint_remove_task():
    sprint = Sprint("Test Sprint")
    task = Task("Test Task")
    sprint.add_task(task)
    sprint.remove_task(task)
    assert task not in sprint.tasks

def test_sprint_start():
    sprint = Sprint("Test Sprint")
    sprint.start()
    assert sprint.status == "In Progress"  # Actual status is "In Progress"

def test_sprint_archive():
    sprint = Sprint("Test Sprint")
    sprint.archive()
    assert sprint.status == "Archived"  # Capital A in actual implementation

def test_sprint_invalid_status():
    sprint = Sprint("Test Sprint")
    with pytest.raises(ValueError):
        sprint.status = "invalid"  # Using property setter instead of set_status

def test_sprint_from_name():
    sprint = Sprint("Test Sprint")
    loaded = Sprint.from_name("Test Sprint")
    assert loaded.name == sprint.name

def test_sprint_list_tasks():
    sprint = Sprint("Test Sprint")
    task1 = Task("Task 1")
    task2 = Task("Task 2")
    sprint.add_task(task1)
    sprint.add_task(task2)
    tasks = sprint.list_tasks()
    assert len(tasks) == 2  # Fixed expected count
    assert task1 in tasks
    assert task2 in tasks
