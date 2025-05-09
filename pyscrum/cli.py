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
    title: str,
    description: str = typer.Option("", help="Optional task description"),
    priority: str = typer.Option("medium", help="Task priority (low/medium/high)")
):
    """Add a new task to the backlog."""
    if priority not in ["low", "medium", "high"]:
        typer.echo("❌ Priority must be one of: low, medium, high")
        return
    task = Task(title, description, priority)
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
    # First validate the name
    is_valid, error_message = Sprint.validate_name(name)
    if not is_valid:
        typer.echo(f"❌ {error_message}")
        return

    try:
        if Sprint.exists(name):
            typer.echo(f"❌ Sprint '{name}' already exists.")
            return
        
        sprint = Sprint(name)
        sprint.save()
        typer.echo(f"✅ Sprint '{name}' created.")
    except Exception as e:
        typer.echo(f"❌ Failed to create sprint: {e}")


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

@app.command()
def remove_from_sprint(task_id: str, sprint_name: str):
    """Remove a task from a sprint."""
    try:
        sprint = Sprint.from_name(sprint_name)
        sprint.remove_task(task_id)
        typer.echo(f"✅ Task {task_id} removed from sprint '{sprint_name}'")
    except ValueError as e:
        typer.echo(f"❌ {e}")  


@app.command()
def list_sprint_tasks(sprint_name: str):
    """List all tasks in a sprint."""
    try:
        sprint = Sprint.from_name(sprint_name)
        if not sprint.tasks:
            typer.echo(f"📭 No tasks in sprint '{sprint_name}'")
            return
        typer.echo(f"📋 Tasks in sprint '{sprint_name}':")
        for task in sprint.tasks:
            typer.echo(f" - {task}")
    except ValueError as e:
        typer.echo(f"❌ {e}")     


@app.command()
def edit_task(
    task_id: str,
    title: str = typer.Option(None, help="New task title"),
    description: str = typer.Option(None, help="New task description"),
):
    """Edit task title or description."""
    try:
        task = Task.load_by_prefix(task_id)
        if title:
            task.title = title
        if description:
            task.description = description
        task.save()
        typer.echo(f"✅ Task {task.id} updated")
    except ValueError as e:
        typer.echo(f"❌ {e}")

@app.command()
def sprint_stats(sprint_name: str):
    """Show sprint statistics."""
    try:
        sprint = Sprint.from_name(sprint_name)
        total = len(sprint.tasks)
        done = len([t for t in sprint.tasks if t.status == "done"])
        in_progress = len([t for t in sprint.tasks if t.status == "in_progress"])
        todo = len([t for t in sprint.tasks if t.status == "todo"])
        
        typer.echo(f"📊 Sprint '{sprint_name}' statistics:")
        typer.echo(f"Total tasks: {total}")
        typer.echo(f"Done: {done}")
        typer.echo(f"In Progress: {in_progress}")
        typer.echo(f"Todo: {todo}")
        if total > 0:
            progress = (done / total) * 100
            typer.echo(f"Progress: {progress:.1f}%")
    except ValueError as e:
        typer.echo(f"❌ {e}")

@app.command()
def set_priority(task_id: str, priority: str = typer.Option(..., help="high/medium/low")):
    """Set task priority."""
    try:
        task = Task.load_by_prefix(task_id)
        task.set_priority(priority)
        typer.echo(f"✅ Task {task.id} priority set to {priority}")
    except ValueError as e:
        typer.echo(f"❌ {e}")
@app.command()
def remove_from_sprint(task_id: str, sprint_name: str):
    """Remove a task from a sprint."""
    try:
        sprint = Sprint.from_name_prefix(sprint_name)
        task = Task.load_by_prefix(task_id)
        sprint.remove_task(task)
        sprint.save()  # Ulož zmeny
        typer.echo(f"🗑️ Task '{task.title}' removed from sprint '{sprint.name}'.")
    except ValueError as e:
        typer.echo(f"❌ {e}")

@app.command()
def list_by_priority(priority: str):
    """List all tasks with specified priority."""
    if priority not in ["low", "medium", "high"]:
        typer.echo("❌ Priority must be one of: low, medium, high")
        return
    
    tasks = Task.load_all()
    priority_tasks = [task for task in tasks if task.priority == priority]
    
    if not priority_tasks:
        typer.echo(f"No tasks with priority '{priority}'")
        return
    
    typer.echo(f"📋 Tasks with {priority} priority:")
    for task in priority_tasks:
        typer.echo(f" - {task}")
@app.command()
def is_high_priority(task_id: str):
    """Check if a task has high priority."""
    try:
        task = Task.load_by_prefix(task_id)
        typer.echo(task.is_high_priority())
    except ValueError as e:
        typer.echo(f"❌ {e}")

@app.command()
def toggle_status(task_id: str):
    """Toggle task status (todo → in_progress → done → todo)."""
    try:
        task = Task.load_by_prefix(task_id)
        task.toggle_status()
        typer.echo(task.status)
    except ValueError as e:
        typer.echo(f"❌ {e}")

@app.command()
def age_in_days(task_id: str):
    """Show number of days since task creation."""
    try:
        task = Task.load_by_prefix(task_id)
        typer.echo(f"{task.age_in_days():.2f}")
    except ValueError as e:
        typer.echo(f"❌ {e}")

@app.command()
def age_in_seconds(task_id: str):
    """Show number of seconds since task creation."""
    try:
        task = Task.load_by_prefix(task_id)
        typer.echo(f"{int(task.age_in_seconds())}")
    except ValueError as e:
        typer.echo(f"❌ {e}")


@app.command()
def search_sprint_tasks(sprint_name: str, query: str):
    """Search tasks in sprint by title or description (case-insensitive)."""
    try:
        sprint = Sprint.from_name(sprint_name)
        matches = sprint.search_tasks(query)
        if not matches:
            typer.echo("No matching tasks found.")
            return
        for task in matches:
            typer.echo(f" - {task}")
    except ValueError as e:
        typer.echo(f"❌ {e}")

@app.command()
def count_tasks_by_priority(sprint_name: str):
    """Count tasks in sprint grouped by priority."""
    try:
        sprint = Sprint.from_name(sprint_name)
        counts = sprint.count_tasks_by_priority()
        for prio, num in counts.items():
            typer.echo(f"{prio}: {num}")
    except ValueError as e:
        typer.echo(f"❌ {e}")

@app.command()
def group_tasks_by_status(sprint_name: str):
    """Group tasks in sprint by status."""
    try:
        sprint = Sprint.from_name(sprint_name)
        groups = sprint.group_tasks_by_status()
        for status, tasks in groups.items():
            typer.echo(f"{status} ({len(tasks)}):")
            for t in tasks:
                typer.echo(f"  - {t}")
    except ValueError as e:
        typer.echo(f"❌ {e}")
if __name__ == "__main__":
    app()
