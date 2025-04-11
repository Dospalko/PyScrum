import os
import pytest
from typer.testing import CliRunner
from pyscrum.cli import app
from pyscrum.database import init_db

runner = CliRunner()


@pytest.fixture(autouse=True)
def clean_db():
    if os.path.exists("pyscrum.db"):
        os.remove("pyscrum.db")


@pytest.fixture(autouse=True)
def setup_db():
    init_db()


def get_task_id_by_title(title: str):
    result = runner.invoke(app, ["list-backlog"])
    for line in result.output.splitlines():
        if title in line:
            return line.split("<Task ")[1].split(":")[0]
    return None


def test_list_tasks_by_status_empty():
    result = runner.invoke(app, ["list-tasks-by-status", "done"])
    assert "no tasks found" in result.output.lower()


def test_init_and_add_task():
    result = runner.invoke(app, ["init"])
    assert "Database initialized" in result.output

    result = runner.invoke(app, ["add-task", "Task A", "--description", "desc"])
    assert "Task added" in result.output


def test_list_backlog():
    runner.invoke(app, ["add-task", "BacklogTask"])
    result = runner.invoke(app, ["list-backlog"])
    assert "BacklogTask" in result.output


def test_set_status_and_get_task():
    runner.invoke(app, ["add-task", "StatusTask"])
    task_id = get_task_id_by_title("StatusTask")

    result = runner.invoke(app, ["set-status", task_id[:8], "in_progress"])
    assert "status updated to in_progress" in result.output

    result = runner.invoke(app, ["get-task", task_id[:8]])
    assert "StatusTask" in result.output
    assert "[in_progress]" in result.output


def test_invalid_status():
    runner.invoke(app, ["add-task", "InvalidStatus"])
    task_id = get_task_id_by_title("InvalidStatus")

    result = runner.invoke(app, ["set-status", task_id[:8], "not_a_status"])
    assert "Invalid status" in result.output or "❌" in result.output


def test_remove_task():
    runner.invoke(app, ["add-task", "ToRemove"])
    task_id = get_task_id_by_title("ToRemove")

    result = runner.invoke(app, ["remove-task", task_id[:8]])
    assert "removed" in result.output


def test_create_start_archive_sprint():
    runner.invoke(app, ["create-sprint", "My Sprint"])
    result = runner.invoke(app, ["start-sprint", "My "])
    assert "started" in result.output

    result = runner.invoke(app, ["archive-sprint", "My Sprint"])
    assert "archived" in result.output


def test_export_sprint_report():
    runner.invoke(app, ["create-sprint", "Report Sprint"])
    result = runner.invoke(app, ["export-sprint-report", "Report Sprint"])
    assert "Exported" in result.output

    assert os.path.exists("Report_Sprint_report.csv")
    assert os.path.exists("Report_Sprint_report.html")
    os.remove("Report_Sprint_report.csv")
    os.remove("Report_Sprint_report.html")


def test_list_tasks_by_status():
    runner.invoke(app, ["add-task", "ToBeDone"])
    task_id = get_task_id_by_title("ToBeDone")
    runner.invoke(app, ["set-status", task_id[:8], "done"])

    result = runner.invoke(app, ["list-tasks-by-status", "done"])
    assert "ToBeDone" in result.output


def test_get_nonexistent_task():
    result = runner.invoke(app, ["get-task", "notreal"])
    assert "not found" in result.output or "❌" in result.output


def test_remove_nonexistent_task():
    result = runner.invoke(app, ["remove-task", "invalid"])
    assert "not found" in result.output or "❌" in result.output


def test_list_tasks():
    runner.invoke(app, ["add-task", "Test List Tasks", "--description", "test"])
    result = runner.invoke(app, ["list-tasks"])
    assert "Backlog tasks" in result.output
    assert "Test List Tasks" in result.output


def test_get_task_not_found():
    result = runner.invoke(app, ["get-task", "nonexistent"])
    assert "not found" in result.output.lower()


def test_remove_task_not_found():
    result = runner.invoke(app, ["remove-task", "invalid"])
    assert "not found" in result.output.lower()


def test_export_sprint_report_nonexistent():
    result = runner.invoke(app, ["export-sprint-report", "Nonexistent Sprint"])
