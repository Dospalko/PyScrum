from pyscrum.database import init_db
from pyscrum.reports import (
    export_tasks_to_csv,
    export_tasks_to_html,
    export_sprint_report_to_csv,
    export_sprint_report_to_html
)

print("⏳ Initializing database...")
init_db()

print("\n📄 Exporting task and sprint reports...")
export_tasks_to_csv("all_tasks.csv")
export_tasks_to_html("all_tasks.html")
export_sprint_report_to_csv("Frontend Sprint", "sprint_report.csv")
export_sprint_report_to_html("Frontend Sprint", "sprint_report.html")

print("\n✅ Reports generated:")
print(" - all_tasks.csv")
print(" - all_tasks.html")
print(" - sprint_report.csv")
print(" - sprint_report.html")
