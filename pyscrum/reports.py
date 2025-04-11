import csv
from pathlib import Path
from .database import get_connection


def export_tasks_to_csv(filename="tasks_report.csv"):
    with get_connection() as conn:
        cursor = conn.execute("SELECT id, title, description, status FROM tasks")
        tasks = cursor.fetchall()

    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Task ID", "Title", "Description", "Status"])
        writer.writerows(tasks)


def export_sprint_report_to_csv(sprint_name, filename=None):
    filename = filename or f"{sprint_name.replace(' ', '_')}_report.csv"
    with get_connection() as conn:
        cursor = conn.execute(
            """
            SELECT t.id, t.title, t.description, t.status
            FROM tasks t
            JOIN sprint_tasks st ON t.id = st.task_id
            WHERE st.sprint_name = ?
            """,
            (sprint_name,),
        )
        sprint_tasks = cursor.fetchall()

    # Always generate the file, even if empty
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Task ID", "Title", "Description", "Status"])
        if sprint_tasks:
            writer.writerows(sprint_tasks)



def export_tasks_to_html(filename="tasks_report.html"):
    with get_connection() as conn:
        cursor = conn.execute("SELECT id, title, description, status FROM tasks")
        tasks = cursor.fetchall()

    html_content = _render_html("All Tasks Report", tasks)
    Path(filename).write_text(html_content, encoding="utf-8")


def export_sprint_report_to_html(sprint_name, filename=None):
    filename = filename or f"{sprint_name.replace(' ', '_')}_report.html"
    with get_connection() as conn:
        cursor = conn.execute(
            """
            SELECT t.id, t.title, t.description, t.status
            FROM tasks t
            JOIN sprint_tasks st ON t.id = st.task_id
            WHERE st.sprint_name = ?
            """,
            (sprint_name,),
        )
        tasks = cursor.fetchall()

    html_content = _render_html(f"Sprint Report: {sprint_name}", tasks)
    Path(filename).write_text(html_content, encoding="utf-8")



def _render_html(title, tasks):
    rows = "".join(
        f"<tr><td>{t[0]}</td><td>{t[1]}</td><td>{t[2]}</td><td>{t[3]}</td></tr>"
        for t in tasks
    )
    return f"""
    <html>
    <head>
        <title>{title}</title>
        <style>
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; }}
            th {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        <h2>{title}</h2>
        <table>
            <tr>
                <th>Task ID</th>
                <th>Title</th>
                <th>Description</th>
                <th>Status</th>
            </tr>
            {rows}
        </table>
    </body>
    </html>
    """
