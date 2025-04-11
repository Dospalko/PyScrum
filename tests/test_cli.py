# test_cli.py

import pytest
from typer.testing import CliRunner
from pyscrum.cli import app
from pyscrum.database import init_db

runner = CliRunner()

@pytest.fixture(autouse=True)
def setup_db():
    init_db()

def test_init():
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
    assert "Database initialized" in result.output

def test_add_and_list_task():
    result = runner.invoke(app, ["add-task", "Test Task", "--description", "Test Desc"])
    assert result.exit_code == 0
    assert "✅ Task added" in result.output

    result = runner.invoke(app, ["list-backlog"])
    assert "Test Task" in result.output

def test_create_and_start_sprint():
    runner.invoke(app, ["create-sprint", "Sprint A"])
    result = runner.invoke(app, ["start-sprint", "Sprint A"])
    assert "started" in result.output

def test_set_task_status():
    runner.invoke(app, ["add-task", "Task for Status"])
    result = runner.invoke(app, ["list-backlog"])
    task_id = result.output.split("<Task ")[1].split(":")[0]

    result = runner.invoke(app, ["set-status", task_id, "in_progress"])
    assert result.exit_code == 0
    assert "status updated to in_progress" in result.output

def test_archive_sprint():
    runner.invoke(app, ["create-sprint", "ToArchive"])
    result = runner.invoke(app, ["archive-sprint", "ToArchive"])
    assert "archived" in result.output
