from pyscrum.reports import export_tasks_to_csv, export_sprint_report_to_csv

from pyscrum.reports import export_sprint_report_to_html

# Export všetkých úloh do tasks_report.csv
export_tasks_to_csv()

# Export konkrétneho sprintu do Release_Sprint_report.csv
export_sprint_report_to_csv("Release Sprint")

export_sprint_report_to_html("Release Sprint")
