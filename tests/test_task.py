import pytest
from pyscrum.task import Task


def test_task_creation():
    task = Task("Test Task", "Test Description", "high")
    assert task.title == "Test Task"
    assert task.description == "Test Description"
    assert task.priority == "high"
    assert task.status == "todo"


def test_task_status_update():
    task = Task("Test Task")
    task.set_status("in_progress")
    assert task.status == "in_progress"


def test_invalid_status():
    task = Task("Test Task")
    with pytest.raises(ValueError):
        task.set_status("invalid")


def test_task_search():
    Task("Search Test 1", "Description 1")
    Task("Search Test 2", "Description 2")
    results = Task.search("Search Test")
    assert len(results) == 2


def test_task_list_all():
    # Clear existing tasks first
    Task.clear_all()  # Add this method if it doesn't exist
    
    # Create test tasks
    Task("List Test 1", priority="high").save()
    Task("List Test 2", priority="low").save()
    
    # Test filtering
    tasks = Task.list_all(priority="high")
    assert len(tasks) == 1
    assert tasks[0].title == "List Test 1"


def test_task_load_by_prefix():
    task = Task("Prefix Test")
    prefix = task.id[:3]
    loaded = Task.load_by_prefix(prefix)
    assert loaded.id == task.id


def test_task_update_description():
    task = Task("Description Test")
    task.update_description("New Description")
    assert task.description == "New Description"


def test_task_set_priority():
    task = Task("Priority Test")
    task.set_priority("high")
    assert task.priority == "high"
    with pytest.raises(ValueError):
        task.set_priority("invalid")
