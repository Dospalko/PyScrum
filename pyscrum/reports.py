import csv
from .database import get_connection

def export_tasks_to_csv(file_path):
    with get_connection() as conn:
        cursor = conn.execute("SELECT title, description, status FROM tasks")
        rows = cursor.fetchall()

    with open(file_path, "w", newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Title', 'Description', 'Status'])
        writer.writerows(rows)

def export_sprint_report_to_csv(sprint_name, filename=None):
    """Export tasks of a specific sprint to a CSV file."""
    filename = filename or f"{sprint_name}_report.csv"
    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT t.id, t.title, t.description, t.status
            FROM tasks t
            JOIN sprint_tasks st ON t.id = st.task_id
            WHERE st.sprint_name = ?
        """, (sprint_name,))
        sprint_tasks = cursor.fetchall()

    with open(filename, mode="w", newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Task ID", "Title", "Description", "Status"])
        writer.writerows(sprint_tasks)
