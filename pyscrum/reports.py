import csv
from .task import Task
from .database import get_connection

<<<<<<< HEAD
def export_tasks_to_csv(file_path):
    tasks = Task.get_all_tasks()  # recommended way
=======
from pathlib import Path

def export_tasks_to_csv(filename="tasks_report.csv"):
    """Export all tasks to a CSV file."""
    with get_connection() as conn:
        cursor = conn.execute("SELECT id, title, description, status FROM tasks")
        tasks = cursor.fetchall()
>>>>>>> 8f8c0f5b99debfd2ea9e35253ea8e10d72cbb1fc

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

def export_sprint_report_to_html(sprint_name, filename=None):
    """Export tasks of a specific sprint to an HTML file."""
    filename = filename or f"{sprint_name.replace(' ', '_')}_report.html"
    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT t.id, t.title, t.description, t.status
            FROM tasks t
            JOIN sprint_tasks st ON t.id = st.task_id
            WHERE st.sprint_name = ?
        """, (sprint_name,))
        tasks = cursor.fetchall()

    html_content = f"""
    <html>
    <head>
        <title>Sprint Report: {sprint_name}</title>
        <style>
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; }}
            th {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        <h2>Sprint Report: {sprint_name}</h2>
        <table>
            <tr>
                <th>Task ID</th>
                <th>Title</th>
                <th>Description</th>
                <th>Status</th>
            </tr>
            {''.join(f"<tr><td>{t[0]}</td><td>{t[1]}</td><td>{t[2]}</td><td>{t[3]}</td></tr>" for t in tasks)}
        </table>
    </body>
    </html>
    """

    Path(filename).write_text(html_content, encoding="utf-8")


def export_tasks_to_html(filename="tasks_report.html"):
    """Export all tasks in the system to an HTML file."""
    with get_connection() as conn:
        cursor = conn.execute("SELECT id, title, description, status FROM tasks")
        tasks = cursor.fetchall()

    html_content = f"""
    <html>
    <head>
        <title>All Tasks Report</title>
        <style>
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; }}
            th {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        <h2>All Tasks Report</h2>
        <table>
            <tr>
                <th>Task ID</th>
                <th>Title</th>
                <th>Description</th>
                <th>Status</th>
            </tr>
            {''.join(f"<tr><td>{t[0]}</td><td>{t[1]}</td><td>{t[2]}</td><td>{t[3]}</td></tr>" for t in tasks)}
        </table>
    </body>
    </html>
    """

    Path(filename).write_text(html_content, encoding="utf-8")
