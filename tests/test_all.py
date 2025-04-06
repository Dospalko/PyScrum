import sys
import pytest
import os
import sqlite3
import csv
from pyscrum.backlog import Backlog
from pyscrum.task import Task
from pyscrum.sprint import Sprint
from pyscrum.database import init_db, get_connection
from pyscrum.reports import export_tasks_to_csv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# This fixture will run before every test function
@pytest.fixture(autouse=True)
def setup_and_teardown():
    # Setup → Initialize DB before test
    init_db()
    yield
    # Teardown → Delete test DB after test
    if os.path.exists('tasks.db'):
        os.remove('tasks.db')


# ------------------ Test for backlog.py ------------------ #
def test_add_task_to_backlog():
    backlog = Backlog()
    task = Task("Task 1", "Description 1")
    backlog.add_task(task)
    assert len(backlog.tasks) == 1


# ------------------ Test for task.py ------------------ #
def test_update_task_status():
    task = Task("Task 2", "Description 2")
    task.update_status("in_progress")
    assert task.status == "in_progress"

def test_update_task_description():
    task = Task("Task 3", "Old Description")
    task.update_description("New Description")
    assert task.description == "New Description"


# ------------------ Test for sprint.py ------------------ #
def test_add_remove_task_from_sprint():
    sprint = Sprint("Sprint Alpha")
    task = Task("Sprint Task", "Sprint Description")
    sprint.add_task(task)
    assert task in sprint.tasks

    sprint.remove_task(task.id)
    assert task not in sprint.tasks

def test_list_tasks_in_sprint():
    sprint = Sprint("Sprint Beta")
    task1 = Task("Task A")
    task2 = Task("Task B")
    sprint.add_task(task1)
    sprint.add_task(task2)
    assert sprint.list_tasks() == [task1, task2]


# ------------------ Test for database.py ------------------ #
def test_database_insertion_and_retrieval():
    with get_connection() as conn:
        # Insert
        conn.execute("INSERT INTO tasks (id, title, description, status) VALUES (?, ?, ?, ?)",
             ('1', 'DB Task', 'DB Desc', 'todo'))
        conn.commit()

        # Retrieve
        cursor = conn.execute("SELECT id, title, description, status FROM tasks WHERE id=?", ('1',))
        row = cursor.fetchone()

        assert row is not None
        assert row[1] == 'DB Task'
        assert row[2] == 'DB Desc'
        assert row[3] == 'todo'





# ------------------ Test for reports.py ------------------ #
def test_export_tasks_to_csv(tmp_path):
    from pyscrum.task import Task
    from pyscrum.database import get_connection
    from pyscrum.reports import export_tasks_to_csv  # ye import bhi jaruri hai bro

    # Clear existing tasks
    with get_connection() as conn:
        conn.execute("DELETE FROM tasks")

    # Create and Save tasks
    task1 = Task("CSV Task 1", "Desc 1", "todo")
    task1.save()

    task2 = Task("CSV Task 2", "Desc 2", "done")
    task2.save()

    file_path = tmp_path / "tasks.csv"
    export_tasks_to_csv(str(file_path))

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    assert "CSV Task 1" in content
    assert "CSV Task 2" in content
