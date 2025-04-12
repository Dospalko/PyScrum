import typer
from pyscrum.database import init_db
from pyscrum.task import Task
from pyscrum.backlog import Backlog
from pyscrum.sprint import Sprint
from pyscrum.reports import (
    export_sprint_report_to_csv,
    export_sprint_report_to_html,
)

app = typer.Typer()


@app.command()
def init():
    """Initialize the database."""
    init_db()
    typer.echo("✅ Database initialized.")


@app.command()
def add_task(
    title: str, description: str = typer.Option("", help="Optional task description")
):
    """Add a new task to the backlog."""
    task = Task(title, description)
    task.save()
    backlog = Backlog()
    backlog.add_task(task)
    typer.echo(f"✅ Task added: {task}")


@app.command()
def list_tasks():
    """List all tasks in the backlog."""
    backlog = Backlog()
    if not backlog.tasks:
        typer.echo("📭 No tasks in backlog.")
        return
    typer.echo("📋 Backlog tasks:")
    for task in backlog.tasks:
        typer.echo(f" - {task}")


@app.command()
def start_sprint(name: str):
    """Start a sprint (sets status to In Progress)."""
    try:
        sprint = Sprint.from_name_prefix(name)
        sprint.start()
        typer.echo(f"🚀 Sprint '{sprint.name}' started.")
    except ValueError as e:
        typer.echo(f"❌ {e}")


@app.command()
def set_status(task_id: str, status: str):
    """Set the status of a task (todo, in_progress, done)."""
    try:
        task = Task.load_by_prefix(task_id)
        task.set_status(status)
        typer.echo(f"✅ Task {task.id} status updated to {status}")
    except ValueError as e:
        typer.echo(f"❌ {e}")


@app.command()
def archive_sprint(name: str):
    """Archive a sprint (sets status to Archived)."""
    try:
        sprint = Sprint.from_name(name)
        sprint.archive()
        typer.echo(f"📦 Sprint '{name}' archived.")
    except ValueError:
        typer.echo(f"❌ Sprint '{name}' not found.")


@app.command()
def list_backlog():
    """List all tasks currently in the backlog."""
    backlog = Backlog()
    if not backlog.tasks:
        typer.echo("📭 Backlog is empty.")
        return
    typer.echo("📋 Backlog:")
    for task in backlog.tasks:
        typer.echo(f" - {task}")


@app.command()
def list_tasks_by_status(status: str):
    """List all tasks filtered by status."""
    tasks = Task.list_all(status=status)
    if not tasks:
        typer.echo(f"No tasks found with status '{status}'.")
        return
    for task in tasks:
        typer.echo(f"- {task}")


@app.command()
def create_sprint(name: str):
    """Create a new sprint."""
    sprint = Sprint(name)
    sprint.save()
    typer.echo(f"✅ Sprint '{name}' created.")


@app.command()
def get_task(task_id: str):
    """Get details of a specific task."""
    try:
        task = Task.load_by_prefix(task_id)
        typer.echo(f"🔍 Task found:\n{task}")
    except ValueError as e:
        typer.echo(f"❌ {e}")


@app.command()
def remove_task(task_id: str):
    """Remove a task from the backlog and database."""
    try:
        backlog = Backlog()
        task = Task.load_by_prefix(task_id)
        backlog.remove_task(task.id)
        typer.echo(f"🗑️ Task {task.id} removed from backlog.")
    except ValueError as e:
        typer.echo(f"❌ {e}")


@app.command()
def export_sprint_report(name: str):
    """Export sprint report to CSV and HTML."""
    try:
        export_sprint_report_to_csv(name)
        export_sprint_report_to_html(name)
        typer.echo(f"📤 Exported sprint '{name}' report to CSV and HTML.")
    except Exception as e:
        typer.echo(f"❌ Failed to export sprint report: {e}")

@app.command()
def add_to_sprint(task_id: str, sprint_name: str):
    """Add a task to a sprint."""
    try:
        task = Task.load_by_prefix(task_id)
        sprint = Sprint.from_name(sprint_name)
        sprint.add_task(task)
        typer.echo(f"✅ Task {task.id} added to sprint '{sprint_name}'")
    except ValueError as e:
        typer.echo(f"❌ {e}")
        
if __name__ == "__main__":
    app()
