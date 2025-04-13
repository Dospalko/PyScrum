import os
import pytest
from typer.testing import CliRunner
from pyscrum.cli import app
from pyscrum.database import init_db
from pyscrum.task import Task
from pyscrum.sprint import Sprint

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
    assert "status updated" in result.output.lower()

    result = runner.invoke(app, ["get-task", task_id[:8]])
    assert "StatusTask" in result.output
    assert "in_progress" in result.output


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
    assert "no task found" in result.output.lower()


def test_remove_task_not_found():
    result = runner.invoke(app, ["remove-task", "invalid"])
    assert "no task found" in result.output.lower()


def test_export_sprint_report_nonexistent():
    result = runner.invoke(app, ["export-sprint-report", "Nonexistent Sprint"])
    assert "not found" in result.output.lower() or "❌" in result.output


def test_export_tasks_with_priority():
    # Create sprint and add tasks with priorities
    runner.invoke(app, ["create-sprint", "Priority Sprint"])
    runner.invoke(app, ["add-task", "High Task", "--priority", "high"])
    runner.invoke(app, ["add-task", "Medium Task", "--priority", "medium"])
    runner.invoke(app, ["add-task", "Low Task", "--priority", "low"])

    # Add tasks to sprint
    for task_name in ["High Task", "Medium Task", "Low Task"]:
        task_id = get_task_id_by_title(task_name)
        runner.invoke(app, ["add-to-sprint", task_id[:8], "Priority Sprint"])

    # Export sprint report
    result = runner.invoke(app, ["export-sprint-report", "Priority Sprint"])
    assert "exported" in result.output.lower()

    # Check CSV file
    csv_file = "Priority_Sprint_report.csv"
    assert os.path.exists(csv_file)
    with open(csv_file, "r") as f:
        content = f.read()
        assert "High Task" in content
        assert "Medium Task" in content
        assert "Low Task" in content
        assert "high" in content.lower()
    
    os.remove(csv_file)
    os.remove("Priority_Sprint_report.html")


def test_export_sprint_with_tasks():
    # Create sprint and add tasks
    runner.invoke(app, ["create-sprint", "Export Test Sprint"])
    runner.invoke(app, ["add-task", "Sprint Task 1", "--priority", "high"])
    task_id = get_task_id_by_title("Sprint Task 1")
    runner.invoke(app, ["add-to-sprint", task_id[:8], "Export Test Sprint"])

    # Export sprint report in both formats
    result = runner.invoke(app, ["export-sprint-report", "Export Test Sprint"])
    assert "exported" in result.output.lower()

    # Check CSV file
    csv_file = "Export_Test_Sprint_report.csv"
    assert os.path.exists(csv_file)
    with open(csv_file, "r") as f:
        content = f.read()
        assert "Sprint Task 1" in content
        assert "high" in content.lower()

    # Check HTML file
    html_file = "Export_Test_Sprint_report.html"
    assert os.path.exists(html_file)
    with open(html_file, "r") as f:
        content = f.read()
        assert "Sprint Task 1" in content
        assert "priority-high" in content.lower()
        assert "<table>" in content

    # Cleanup
    os.remove(csv_file)
    os.remove(html_file)


def test_export_empty_sprint():
    runner.invoke(app, ["create-sprint", "Empty Sprint"])
    result = runner.invoke(app, ["export-sprint-report", "Empty Sprint"])
    assert "exported" in result.output.lower()

    csv_file = "Empty_Sprint_report.csv"
    html_file = "Empty_Sprint_report.html"
    
    # Check if files exist and contain headers
    assert os.path.exists(csv_file)
    assert os.path.exists(html_file)
    
    with open(csv_file, "r") as f:
        content = f.read()
        assert "Task ID" in content
        assert "Priority" in content
    
    with open(html_file, "r") as f:
        content = f.read()
        assert "Statistics" in content
        assert "Total Tasks: 0" in content
    
    # Cleanup
    os.remove(csv_file)
    os.remove(html_file)


# Remove test_export_tasks_invalid_format as it's no longer needed


def test_export_sprint_report_with_status_changes():
    # Create sprint and task
    runner.invoke(app, ["create-sprint", "Status Sprint"])
    runner.invoke(app, ["add-task", "Progress Task"])
    task_id = get_task_id_by_title("Progress Task")
    runner.invoke(app, ["add-to-sprint", task_id[:8], "Status Sprint"])
    
    # Change task status
    runner.invoke(app, ["set-status", task_id[:8], "in_progress"])
    
    # Export report
    result = runner.invoke(app, ["export-sprint-report", "Status Sprint"])
    assert "exported" in result.output.lower()
    
    # Check status in files
    csv_file = "Status_Sprint_report.csv"
    html_file = "Status_Sprint_report.html"
    
    with open(csv_file, "r") as f:
        content = f.read()
        assert "in_progress" in content.lower()
    
    with open(html_file, "r") as f:
        content = f.read()
        assert "status-in_progress" in content.lower()
    
    # Cleanup
    os.remove(csv_file)
    os.remove(html_file)


def test_init():
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
    assert "✅ Database initialized" in result.stdout


def test_add_task():
    runner.invoke(app, ["init"])
    result = runner.invoke(app, ["add-task", "Test Task", "--description", "Test Description", "--priority", "high"])
    assert result.exit_code == 0
    assert "✅ Task added" in result.stdout


def test_invalid_priority():
    result = runner.invoke(app, ["add-task", "Test Task", "--priority", "invalid"])
    assert result.exit_code == 0
    assert "❌ Priority must be one of: low, medium, high" in result.stdout


def test_list_tasks_empty():
    result = runner.invoke(app, ["list-tasks"])
    assert "📭 No tasks in backlog" in result.output


def test_list_backlog_empty():
    result = runner.invoke(app, ["list-backlog"])
    assert "📭 Backlog is empty" in result.output


def test_sprint_management_workflow():
    # Create tasks
    runner.invoke(app, ["add-task", "Sprint Task 1", "--priority", "high"])
    runner.invoke(app, ["add-task", "Sprint Task 2", "--priority", "medium"])
    
    # Get task IDs
    task1_id = get_task_id_by_title("Sprint Task 1")
    task2_id = get_task_id_by_title("Sprint Task 2")
    
    # Create and manage sprint
    runner.invoke(app, ["create-sprint", "Test Sprint"])
    runner.invoke(app, ["add-to-sprint", task1_id[:8], "Test Sprint"])
    runner.invoke(app, ["add-to-sprint", task2_id[:8], "Test Sprint"])
    
    # List sprint tasks
    result = runner.invoke(app, ["list-sprint-tasks", "Test Sprint"])
    assert "Sprint Task 1" in result.output
    assert "Sprint Task 2" in result.output
    
    # Remove task from sprint
    result = runner.invoke(app, ["remove-from-sprint", task1_id[:8], "Test Sprint"])
    assert "✅ Task" in result.output
    
    # Verify task removed
    result = runner.invoke(app, ["list-sprint-tasks", "Test Sprint"])
    assert "Sprint Task 1" not in result.output
    assert "Sprint Task 2" in result.output


def test_list_by_priority():
    # Add tasks with different priorities
    runner.invoke(app, ["add-task", "High Priority", "--priority", "high"])
    runner.invoke(app, ["add-task", "Medium Priority", "--priority", "medium"])
    runner.invoke(app, ["add-task", "Low Priority", "--priority", "low"])
    
    # Test high priority
    result = runner.invoke(app, ["list-by-priority", "high"])
    assert "High Priority" in result.output
    assert "Medium Priority" not in result.output
    
    # Test invalid priority
    result = runner.invoke(app, ["list-by-priority", "invalid"])
    assert "❌ Priority must be one of: low, medium, high" in result.output


def test_sprint_not_found():
    result = runner.invoke(app, ["list-sprint-tasks", "NonExistentSprint"])
    assert "❌" in result.output


def test_task_not_found():
    result = runner.invoke(app, ["get-task", "nonexistent"])
    assert "❌" in result.output


def test_add_task_invalid_priority():
    result = runner.invoke(app, ["add-task", "Invalid Task", "--priority", "super-high"])
    assert "❌ Priority must be one of: low, medium, high" in result.output


def test_export_sprint_report_nonexistent():
    result = runner.invoke(app, ["export-sprint-report", "NonExistentSprint"])
    assert "❌" in result.output
