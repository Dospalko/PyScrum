import csv
from .task import Task
from .database import get_connection

def export_tasks_to_csv(file_path):
    tasks = Task.get_all_tasks()  # recommended way

    with open(file_path, "w", newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Title', 'Description', 'Status'])

        for task in tasks:
            writer.writerow([task.title, task.description, task.status])

def export_sprint_report_to_csv(sprint_name, filename=None):
    """Export tasks of a specific sprint to a CSV file."""
    filename = filename or f"{sprint_name}_report.csv"
    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT t.id, t.title, t.description, t.status
            FROM tasks t
            JOIN sprint_tasks st ON t.id = st.task_id
            JOIN sprints s ON st.sprint_id = s.id
            WHERE s.name = ?
        """, (sprint_name,))
        sprint_tasks = cursor.fetchall()

    with open(filename, mode="w", newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Task ID", "Title", "Description", "Status"])
        writer.writerows(sprint_tasks)
