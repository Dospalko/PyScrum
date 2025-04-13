import pytest
from pyscrum.sprint import Sprint
from pyscrum.task import Task
import sqlite3

@pytest.fixture
def clean_sprint():
    sprint = Sprint("Test Sprint")
    yield sprint
    # Cleanup after each test
    try:
        with get_connection() as conn:
            conn.execute("DELETE FROM sprints")
            conn.execute("DELETE FROM sprint_tasks")
    except:
        pass

def test_sprint_creation(clean_sprint):
    assert clean_sprint.name == "Test Sprint"
    assert clean_sprint.status == "Planned"

def test_sprint_invalid_status(clean_sprint):
    with pytest.raises(ValueError):
        clean_sprint.status = "invalid"

def test_sprint_valid_status_changes(clean_sprint):
    clean_sprint.status = "In Progress"
    assert clean_sprint.status == "In Progress"
    clean_sprint.status = "Completed"
    assert clean_sprint.status == "Completed"
    clean_sprint.status = "Archived"
    assert clean_sprint.status == "Archived"

def test_sprint_list_tasks(clean_sprint):
    # Clear existing tasks
    clean_sprint.tasks = []
    
    # Add new tasks
    task1 = Task("Task 1")
    task2 = Task("Task 2")
    clean_sprint.add_task(task1)
    clean_sprint.add_task(task2)
    
    tasks = clean_sprint.list_tasks()
    assert len(tasks) == 2
    assert task1 in tasks
    assert task2 in tasks

def test_sprint_get_tasks_by_status(clean_sprint):
    task1 = Task("Task 1")
    task2 = Task("Task 2")
    task1.set_status("done")
    
    clean_sprint.add_task(task1)
    clean_sprint.add_task(task2)
    
    done_tasks = clean_sprint.get_tasks_by_status("done")
    assert len(done_tasks) == 1
    assert done_tasks[0].title == "Task 1"

def test_sprint_get_tasks_by_priority(clean_sprint):
    task1 = Task("Task 1", priority="high")
    task2 = Task("Task 2", priority="low")
    
    clean_sprint.add_task(task1)
    clean_sprint.add_task(task2)
    
    high_priority = clean_sprint.get_tasks_by_priority("high")
    assert len(high_priority) == 1
    assert high_priority[0].title == "Task 1"

def test_sprint_get_statistics(clean_sprint):
    task1 = Task("Task 1")
    task2 = Task("Task 2")
    task1.set_status("done")
    
    clean_sprint.add_task(task1)
    clean_sprint.add_task(task2)
    
    stats = clean_sprint.get_statistics()
    assert stats["total"] == 2
    assert stats["done"] == 1
    assert stats["todo"] == 1
    assert stats["progress"] == 50.0

def test_sprint_export_tasks(clean_sprint, tmp_path):
    task = Task("Export Test")
    clean_sprint.add_task(task)
    
    # Test CSV export
    csv_file = tmp_path / "tasks.csv"
    clean_sprint.get_tasks_by_status("todo", export_to=str(csv_file))
    assert csv_file.exists()
    
    # Test HTML export
    html_file = tmp_path / "tasks.html"
    clean_sprint.get_tasks_by_status("todo", export_to=str(html_file))
    assert html_file.exists()

def test_sprint_list_all():
    # Clear existing sprints
    Sprint.clear_all()
    
    # Create and save sprints
    sprint1 = Sprint("Sprint 1")
    sprint1.save()
    sprint2 = Sprint("Sprint 2")
    sprint2.save()
    
    # Get all sprints
    sprints = Sprint.list_all()
    assert len(sprints) == 2
    sprint_names = {s.name for s in sprints}
    assert "Sprint 1" in sprint_names
    assert "Sprint 2" in sprint_names

def test_sprint_get_statistics():
    # Clear existing sprints
    Sprint.clear_all()
    
    # Create a new sprint
    sprint = Sprint("Stats Test Sprint")
    
    # Add tasks with different statuses
    task1 = Task("Task 1")
    task1.set_status("done")
    task2 = Task("Task 2")
    task2.set_status("todo")
    
    sprint.add_task(task1)
    sprint.add_task(task2)
    
    # Get statistics
    stats = sprint.get_statistics()
    assert stats["total"] == 2
    assert stats["done"] == 1
    assert stats["todo"] == 1
    assert stats["progress"] == 50.0

def test_sprint_repr(clean_sprint):
    task = Task("Repr Test")
    task.set_status("done")
    clean_sprint.add_task(task)
    repr_output = repr(clean_sprint)
    assert "Test Sprint" in repr_output
    assert "100.0% complete" in repr_output

def test_sprint_from_name_and_delete():
    Sprint.clear_all()
    s = Sprint("LoadMe")
    s.save()
    loaded = Sprint.from_name("LoadMe")
    assert loaded.name == "LoadMe"
    Sprint.delete("LoadMe")
    with pytest.raises(ValueError):
        Sprint.from_name("LoadMe")

def test_sprint_update_name():
    s = Sprint("OldName")
    s.save()
    s.update_name("NewName")
    assert s.name == "NewName"
    loaded = Sprint.from_name("NewName")
    assert loaded.name == "NewName"

def test_sprint_from_prefix_unique():
    Sprint.clear_all()
    Sprint("AlphaSprint").save()
    loaded = Sprint.from_name_prefix("Alph")
    assert loaded.name == "AlphaSprint"

def test_sprint_from_prefix_too_short():
    with pytest.raises(ValueError):
        Sprint.from_name_prefix("Al")

def test_sprint_from_prefix_ambiguous():
    Sprint.clear_all()
    Sprint("PrefixOne").save()
    Sprint("PrefixTwo").save()
    with pytest.raises(ValueError):
        Sprint.from_name_prefix("Pre")

def test_sprint_clear_all():
    Sprint("Temp1").save()
    Sprint("Temp2").save()
    Sprint.clear_all()
    assert len(Sprint.list_all()) == 0

def test_sprint_remove_task(clean_sprint):
    task = Task("Removable")
    clean_sprint.add_task(task)
    assert any(t.id == task.id for t in clean_sprint.tasks)
    clean_sprint.remove_task(task)
    assert all(t.id != task.id for t in clean_sprint.tasks)

def test_sprint_start_and_complete(clean_sprint):
    assert clean_sprint.status == "Planned"
    clean_sprint.start()
    assert clean_sprint.status == "In Progress"
    clean_sprint.complete()
    assert clean_sprint.status == "Completed"

def test_sprint_archive(clean_sprint):
    clean_sprint.archive()
    assert clean_sprint.status == "Archived"

    # Try archiving again – should be no-op
    clean_sprint.archive()
    assert clean_sprint.status == "Archived"

def test_add_task_duplicate(clean_sprint):
    task = Task("Duplicate Task")
    clean_sprint.add_task(task)
    clean_sprint.add_task(task)  # should not duplicate
    assert clean_sprint.tasks.count(task) == 1

def test_add_task_invalid_type(clean_sprint):
    with pytest.raises(TypeError):
        clean_sprint.add_task("not a task")

def test_remove_task_by_id(clean_sprint):
    task = Task("Remove by ID")
    clean_sprint.add_task(task)
    clean_sprint.remove_task(task.id)
    assert task not in clean_sprint.tasks

def test_sprint_repr_empty(clean_sprint):
    # No tasks added
    output = repr(clean_sprint)
    assert "0 tasks" in output
    assert "0.0% complete" in output

def test_get_tasks_by_status_invalid(clean_sprint):
    # Should return empty list, not error
    results = clean_sprint.get_tasks_by_status("nonexistent_status")
    assert isinstance(results, list)
    assert len(results) == 0

def test_get_tasks_by_priority_none(clean_sprint):
    task = Task("No Priority")
    clean_sprint.add_task(task)
    results = clean_sprint.get_tasks_by_priority("high")
    assert results == []  # none matches

def test_sprint_database_error_on_load(monkeypatch):
    def broken_conn():
        raise sqlite3.OperationalError("Simulated DB error")
    monkeypatch.setattr("pyscrum.sprint.get_connection", broken_conn)
    with pytest.raises(RuntimeError):
        Sprint.from_name("FailMe")
