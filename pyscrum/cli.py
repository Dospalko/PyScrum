import typer
from pyscrum.database import init_db
from pyscrum.task import Task
from pyscrum.backlog import Backlog

app = typer.Typer()

@app.command()
def init():
    """Initialize the database."""
    init_db()
    typer.echo("✅ Database initialized.")

@app.command()
def add_task(title: str, description: str = typer.Option("", help="Optional task description")):
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

if __name__ == "__main__":
    app()
