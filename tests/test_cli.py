import os
import pytest
from typer.testing import CliRunner
from pyscrum.cli import app
from pyscrum.database import init_db

runner = CliRunner()

@pytest.fixture(autouse=True)
def setup_db():
    # Reset before each test
    init_db()

def test_full_cli_workflow():
    # 1. Init
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0

    # 2. Add task
    result = runner.invoke(app, ["add-task", "Login Feature", "--description", "Add Google login"])
    assert "✅ Task added" in result.output

    # 3. List backlog
    result = runner.invoke(app, ["list-backlog"])
    assert "Login Feature" in result.output
    task_id = result.output.split("<Task ")[1].split(":")[0].strip()

    # 4. Set status using prefix
    result = runner.invoke(app, ["set-status", task_id[:8], "in_progress"])
    assert "status updated to in_progress" in result.output

    # 5. Get task
    result = runner.invoke(app, ["get-task", task_id[:8]])
    assert "Login Feature" in result.output
    assert "[in_progress]" in result.output

    # 6. Create and start sprint
    runner.invoke(app, ["create-sprint", "Sprint A"])
    result = runner.invoke(app, ["start-sprint", "Spr"])  # Prefix test
    assert "started" in result.output

    # 7. Archive sprint
    result = runner.invoke(app, ["archive-sprint", "Sprint A"])
    assert "archived" in result.output

    # 8. Set status for another task
    runner.invoke(app, ["add-task", "Second Task"])
    output = runner.invoke(app, ["list-backlog"]).output
    second_task_id = [line for line in output.splitlines() if "Second Task" in line][0].split("<Task ")[1].split(":")[0]

    result = runner.invoke(app, ["set-status", second_task_id[:8], "done"])
    assert result.exit_code == 0

    # 9. List by status
    result = runner.invoke(app, ["list-tasks-by-status", "done"])
    assert "Second Task" in result.output

    # 10. Remove task
    result = runner.invoke(app, ["remove-task", second_task_id[:8]])
    assert "removed" in result.output

    # 11. Export report (should not crash)
    result = runner.invoke(app, ["export-sprint-report", "Sprint A"])
    assert "Exported" in result.output

    # 12. Validate export files
    assert os.path.exists("Sprint_A_report.csv")
    assert os.path.exists("Sprint_A_report.html")

    # Clean up
    os.remove("Sprint_A_report.csv")
    os.remove("Sprint_A_report.html")
