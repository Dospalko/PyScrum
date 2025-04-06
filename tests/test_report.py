import pytest
from pyscrum.task import Task
from pyscrum.sprint import Sprint
from pyscrum.database import get_connection
from pyscrum.reports import export_tasks_to_csv, export_sprint_report_to_csv


def test_export_tasks_to_csv(tmp_path):
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


def test_export_sprint_report_to_csv(tmp_path):
    # Create Sprint
    sprint = Sprint("Sprint 1")
    sprint.save()

    # Add tasks to sprint
    task1 = Task("Sprint Task 1", "Desc 1", "todo")
    task1.save()
    sprint.add_task(task1)

    task2 = Task("Sprint Task 2", "Desc 2", "in-progress")
    task2.save()
    sprint.add_task(task2)

    # Export Sprint Report
    file_path = tmp_path / "sprint_report.csv"
    export_sprint_report_to_csv("Sprint 1", str(file_path))

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "Sprint Task 1" in content
    assert "Sprint Task 2" in content
