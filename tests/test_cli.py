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
    # Create tasks with unique names
    runner.invoke(app, ["add-task", "UniqueTask1", "--priority", "high"])
    runner.invoke(app, ["add-task", "UniqueTask2", "--priority", "medium"])
    
    # Get task IDs and verify they exist
    task1_id = get_task_id_by_title("UniqueTask1")
    task2_id = get_task_id_by_title("UniqueTask2")
    assert task1_id is not None
    assert task2_id is not None
    
    # Create sprint
    result = runner.invoke(app, ["create-sprint", "TestSprint1"])
    assert result.exit_code == 0
    
    # Add tasks to sprint
    result = runner.invoke(app, ["add-to-sprint", task1_id[:8], "TestSprint1"])
    assert result.exit_code == 0
    
    result = runner.invoke(app, ["add-to-sprint", task2_id[:8], "TestSprint1"])
    assert result.exit_code == 0
    
    # Start sprint
    result = runner.invoke(app, ["start-sprint", "TestSprint1"])
    assert result.exit_code == 0
    
    # List sprint tasks and verify both tasks are present
    result = runner.invoke(app, ["list-sprint-tasks", "TestSprint1"])
    assert result.exit_code == 0
    output = result.output.lower()
    assert "uniquetask1" in output
    assert "uniquetask2" in output
    
    # Remove first task from sprint
    result = runner.invoke(app, ["remove-from-sprint", task1_id[:8], "TestSprint1"])
    assert result.exit_code == 0
    
    # Verify task removal
    result = runner.invoke(app, ["list-sprint-tasks", "TestSprint1"])
    assert result.exit_code == 0
    output = result.output.lower()
    assert "uniquetask2" in output
    assert "uniquetask1" not in output

    # Clean up
    runner.invoke(app, ["remove-task", task1_id[:8]])
    runner.invoke(app, ["remove-task", task2_id[:8]])


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


def test_sprint_stats():
    # Create sprint
    runner.invoke(app, ["create-sprint", "StatsSprint"])
    
    # Add tasks
    runner.invoke(app, ["add-task", "StatsTask1"])
    runner.invoke(app, ["add-task", "StatsTask2"])
    
    # Get task IDs
    task1_id = get_task_id_by_title("StatsTask1")
    task2_id = get_task_id_by_title("StatsTask2")
    assert task1_id is not None
    assert task2_id is not None
    
    # Add tasks to sprint
    runner.invoke(app, ["add-to-sprint", task1_id[:8], "StatsSprint"])
    runner.invoke(app, ["add-to-sprint", task2_id[:8], "StatsSprint"])
    
    # Start sprint
    runner.invoke(app, ["start-sprint", "StatsSprint"])
    
    # Set task statuses
    runner.invoke(app, ["set-status", task1_id[:8], "done"])
    runner.invoke(app, ["set-status", task2_id[:8], "in_progress"])
    
    # Check sprint statistics
    result = runner.invoke(app, ["sprint-stats", "StatsSprint"])
    assert result.exit_code == 0
    output = result.output.lower()
    assert "total tasks: 2" in output
    assert "done: 1" in output
    assert "in progress: 1" in output


def test_invalid_sprint_operations():
    # Try operations with non-existent sprint
    result = runner.invoke(app, ["start-sprint", "NonExistentSprint"])
    assert "❌" in result.output
    assert "not found" in result.output.lower()
    
    result = runner.invoke(app, ["archive-sprint", "NonExistentSprint"])
    assert "❌" in result.output
    assert "not found" in result.output.lower()
    
    result = runner.invoke(app, ["list-sprint-tasks", "NonExistentSprint"])
    assert "❌" in result.output
    assert "not found" in result.output.lower()


def test_task_priority_operations():
    # Add task with priority
    result = runner.invoke(app, ["add-task", "PriorityTask", "--priority", "high"])
    assert "✅" in result.output
    
    task_id = get_task_id_by_title("PriorityTask")
    assert task_id is not None
    
    # List by priority to verify initial state
    result = runner.invoke(app, ["list-by-priority", "high"])
    assert "PriorityTask" in result.output
    
    # Try invalid priority
    result = runner.invoke(app, ["add-task", "InvalidTask", "--priority", "invalid"])
    assert "❌" in result.output
    assert "Priority must be one of: low, medium, high" in result.output
    
    # List tasks to verify
    result = runner.invoke(app, ["list-tasks"])
    assert "PriorityTask" in result.output

def test_duplicate_sprint_creation():
    """Test that duplicate sprint names are properly handled"""
    # First creation should succeed
    result1 = runner.invoke(app, ["create-sprint", "DuplicateSprint"])
    assert result1.exit_code == 0
    assert "✅ Sprint 'DuplicateSprint' created" in result1.output
    
    # Second creation with same name should fail
    result2 = runner.invoke(app, ["create-sprint", "DuplicateSprint"])
    assert result2.exit_code == 0  # Command should complete but with error message
    assert "❌ Sprint 'DuplicateSprint' already exists" in result2.output
    
    # Verify case sensitivity
    result3 = runner.invoke(app, ["create-sprint", "duplicatesprint"])
    assert result3.exit_code == 0
    assert "✅ Sprint 'duplicatesprint' created" in result3.output
    
    # Clean up
    Sprint.clear_all()


def test_sprint_name_validation():
    """Test sprint name validation rules"""
    # Test empty name
    result1 = runner.invoke(app, ["create-sprint", ""])
    assert "❌ Sprint name cannot be empty" in result1.output

    # Test whitespace-only name
    result2 = runner.invoke(app, ["create-sprint", "   "])
    assert "❌ Sprint name cannot be empty" in result2.output

    # Test name that's too long (51 characters)
    long_name = "x" * 51
    result3 = runner.invoke(app, ["create-sprint", long_name])
    assert "❌ Sprint name cannot be longer than 50 characters" in result3.output

    # Test valid name
    result4 = runner.invoke(app, ["create-sprint", "Valid Sprint Name"])
    assert "✅ Sprint 'Valid Sprint Name' created" in result4.output

    # Clean up
    Sprint.clear_all()


# Helper function to verify task exists in sprint
def verify_task_in_sprint(task_title: str, sprint_name: str) -> bool:
    result = runner.invoke(app, ["list-sprint-tasks", sprint_name])
    return task_title.lower() in result.output.lower()

# Helper function to verify task status
def verify_task_status(task_id: str, expected_status: str) -> bool:
    result = runner.invoke(app, ["get-task", task_id])
    return expected_status.lower() in result.output.lower()
