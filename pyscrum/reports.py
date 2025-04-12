import csv
from pathlib import Path
from datetime import datetime
from html import escape
from typing import Optional, List, Tuple
from .database import get_connection


class ReportError(Exception):
    """Custom exception for report generation errors."""
    pass


def export_tasks_to_csv(filename: str = "tasks_report.csv") -> None:
    """
    Export all tasks to a CSV file.
    
    Args:
        filename: Output CSV filename
    Raises:
        ReportError: If database query or file writing fails
    """
    try:
        with get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT id, title, description, status, priority,
                       created_at, updated_at
                FROM tasks
                ORDER BY created_at DESC
                """
            )
            tasks = cursor.fetchall()

        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([
                "Task ID", "Title", "Description", "Status", "Priority",
                "Created", "Last Updated"
            ])
            writer.writerows(tasks)
    except Exception as e:
        raise ReportError(f"Failed to export tasks to CSV: {str(e)}")


def export_sprint_report_to_csv(
    sprint_name: str,
    filename: Optional[str] = None
) -> None:
    """
    Export sprint tasks to a CSV file.
    
    Args:
        sprint_name: Name of the sprint
        filename: Optional custom filename
    Raises:
        ReportError: If database query or file writing fails
    """
    try:
        filename = filename or f"{sprint_name.replace(' ', '_')}_report.csv"
        
        with get_connection() as conn:
            # Verify sprint exists
            cursor = conn.execute(
                "SELECT COUNT(*) FROM sprints WHERE name = ?",
                (sprint_name,)
            )
            if cursor.fetchone()[0] == 0:
                raise ReportError(f"Sprint '{sprint_name}' not found")

            cursor = conn.execute(
                """
                SELECT 
                    t.id,
                    t.title,
                    t.description,
                    t.status,
                    t.priority,
                    t.created_at,
                    t.updated_at,
                    COUNT(c.id) as comments
                FROM tasks t
                JOIN sprint_tasks st ON t.id = st.task_id
                LEFT JOIN task_comments c ON t.id = c.task_id
                WHERE st.sprint_name = ?
                GROUP BY t.id
                ORDER BY t.status, t.created_at
                """,
                (sprint_name,)
            )
            sprint_tasks = cursor.fetchall()

        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([
                "Task ID", "Title", "Description", "Status", "Priority",
                "Created", "Last Updated", "Comments"
            ])
            if sprint_tasks:
                writer.writerows(sprint_tasks)
    except ReportError:
        raise
    except Exception as e:
        raise ReportError(f"Failed to export sprint report to CSV: {str(e)}")


def export_tasks_to_html(filename: str = "tasks_report.html") -> None:
    """
    Export all tasks to an HTML file.
    
    Args:
        filename: Output HTML filename
    Raises:
        ReportError: If database query or file writing fails
    """
    try:
        with get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT 
                    t.id,
                    t.title,
                    t.description,
                    t.status,
                    t.priority,
                    t.created_at,
                    t.updated_at,
                    COUNT(c.id) as comments
                FROM tasks t
                LEFT JOIN task_comments c ON t.id = c.task_id
                GROUP BY t.id
                ORDER BY t.status, t.created_at
                """
            )
            tasks = cursor.fetchall()

        html_content = _render_html(
            title="All Tasks Report",
            tasks=tasks,
            extra_stats=_get_task_statistics()
        )
        Path(filename).write_text(html_content, encoding="utf-8")
    except Exception as e:
        raise ReportError(f"Failed to export tasks to HTML: {str(e)}")


def export_sprint_report_to_html(
    sprint_name: str,
    filename: Optional[str] = None
) -> None:
    """
    Export sprint tasks to an HTML file.
    
    Args:
        sprint_name: Name of the sprint
        filename: Optional custom filename
    Raises:
        ReportError: If database query or file writing fails
    """
    try:
        filename = filename or f"{sprint_name.replace(' ', '_')}_report.html"
        
        with get_connection() as conn:
            # Verify sprint exists
            cursor = conn.execute(
                "SELECT COUNT(*) FROM sprints WHERE name = ?",
                (sprint_name,)
            )
            if cursor.fetchone()[0] == 0:
                raise ReportError(f"Sprint '{sprint_name}' not found")

            cursor = conn.execute(
                """
                SELECT 
                    t.id,
                    t.title,
                    t.description,
                    t.status,
                    t.priority,
                    t.created_at,
                    t.updated_at,
                    COUNT(c.id) as comments
                FROM tasks t
                JOIN sprint_tasks st ON t.id = st.task_id
                LEFT JOIN task_comments c ON t.id = c.task_id
                WHERE st.sprint_name = ?
                GROUP BY t.id
                ORDER BY t.status, t.created_at
                """,
                (sprint_name,)
            )
            tasks = cursor.fetchall()

        html_content = _render_html(
            title=f"Sprint Report: {sprint_name}",
            tasks=tasks,
            extra_stats=_get_sprint_statistics(sprint_name)
        )
        Path(filename).write_text(html_content, encoding="utf-8")
    except ReportError:
        raise
    except Exception as e:
        raise ReportError(f"Failed to export sprint report to HTML: {str(e)}")


def _get_task_statistics() -> dict:
    """Get overall task statistics."""
    with get_connection() as conn:
        cursor = conn.execute(
            """
            SELECT 
                status,
                COUNT(*) as count
            FROM tasks
            GROUP BY status
            """
        )
        stats = dict(cursor.fetchall())
        
        return {
            "total": sum(stats.values()),
            "by_status": stats,
            "completion_rate": (
                (stats.get("done", 0) / sum(stats.values())) * 100
                if sum(stats.values()) > 0 else 0
            )
        }


def _get_sprint_statistics(sprint_name: str) -> dict:
    """Get sprint-specific statistics."""
    with get_connection() as conn:
        cursor = conn.execute(
            """
            SELECT 
                t.status,
                COUNT(*) as count
            FROM tasks t
            JOIN sprint_tasks st ON t.id = st.task_id
            WHERE st.sprint_name = ?
            GROUP BY t.status
            """,
            (sprint_name,)
        )
        stats = dict(cursor.fetchall())
        
        return {
            "total": sum(stats.values()),
            "by_status": stats,
            "completion_rate": (
                (stats.get("done", 0) / sum(stats.values())) * 100
                if sum(stats.values()) > 0 else 0
            )
        }


def _render_html(title: str, tasks: List[Tuple], extra_stats: dict) -> str:
    """Render HTML content with tasks and statistics."""
    rows = "".join(
        f"""
        <tr>
            <td>{escape(str(t[0]))}</td>
            <td>{escape(str(t[1]))}</td>
            <td>{escape(str(t[2]))}</td>
            <td class="status-{t[3]}">{escape(str(t[3]))}</td>
            <td class="priority-{t[4]}">{escape(str(t[4]))}</td>
            <td>{escape(str(t[5]))}</td>
            <td>{escape(str(t[6]))}</td>
            <td>{t[7] if len(t) > 7 else ''}</td>
        </tr>
        """
        for t in tasks
    )
    
    stats_html = f"""
        <div class="stats">
            <h3>Statistics</h3>
            <p>Total Tasks: {extra_stats['total']}</p>
            <p>Completion Rate: {extra_stats['completion_rate']:.1f}%</p>
            <h4>Tasks by Status:</h4>
            <ul>
                {''.join(f"<li>{status}: {count}</li>" for status, count in extra_stats['by_status'].items())}
            </ul>
        </div>
    """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{escape(title)}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f5f5f5; }}
            .status-done {{ color: green; }}
            .status-in_progress {{ color: orange; }}
            .status-todo {{ color: red; }}
            .priority-high {{ font-weight: bold; color: #d9534f; }}
            .priority-medium {{ color: #f0ad4e; }}
            .priority-low {{ color: #5bc0de; }}
            h2 {{ color: #333; }}
            .timestamp {{
                color: #666;
                font-size: 0.9em;
                margin-top: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>{escape(title)}</h2>
            {stats_html}
            <table>
                <tr>
                    <th>Task ID</th>
                    <th>Title</th>
                    <th>Description</th>
                    <th>Status</th>
                    <th>Priority</th>
                    <th>Created</th>
                    <th>Updated</th>
                    <th>Comments</th>
                </tr>
                {rows}
            </table>
            <div class="timestamp">
                Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </div>
        </div>
    </body>
    </html>
    """
