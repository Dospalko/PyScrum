from pyscrum.database import init_db
from pyscrum.task import Task
from pyscrum.backlog import Backlog
from pyscrum.sprint import Sprint
from pyscrum.reports import (
    export_tasks_to_csv,
    export_sprint_report_to_csv,
    export_tasks_to_html,
    export_sprint_report_to_html
)

def full_example():
    print("⏳ Initializing database...")
    init_db()

    print("\n📋 Cleaning previous state...")
    for sprint in Sprint.list_all():
        print(f" - Deleting old sprint: {sprint.name}")
        Sprint.delete(sprint.name)

    print("\n📋 Creating backlog and tasks...")
    backlog = Backlog()
    task1 = Task("Implement login", "Google + Email")
    task2 = Task("Design database", "Initial schema")
    task3 = Task("Build API", "RESTful endpoints")

    for task in [task1, task2, task3]:
        task.save()
        backlog.add_task(task)

    print("\n✅ Backlog populated with tasks:")
    for task in backlog.tasks:
        print(" -", task)

    print("\n✏️ Updating description for Task 1...")
    task1.update_description("Support Google, Apple ID & Email login")

    print("\n🔍 Searching tasks with keyword 'API'...")
    results = Task.search("API")
    for result in results:
        print(" -", result)

    print("\n🚀 Creating a sprint...")
    sprint = Sprint("Sprint 1")
    sprint.add_task(task1)
    sprint.add_task(task2)
    sprint.save()

    backlog.remove_task(task1.id)
    backlog.remove_task(task2.id)

    print("\n📝 Updating task statuses...")
    task1.set_status("in_progress")
    task2.set_status("todo")

    print("\n📈 Sprint overview:")
    print(sprint)
    for task in sprint.tasks:
        print(" -", task)

    print("\n🔁 Filtering sprint tasks by status 'todo' and exporting...")
    todo_tasks = sprint.get_tasks_by_status("todo", export_to="todo_tasks.html")

    print("\n✏️ Renaming sprint...")
    sprint.update_name("Frontend Sprint")

    print("\n📦 Archiving sprint...")
    sprint.archive()
    print(f"Archived: {sprint.name}, status={sprint.status}")

    print("\n🧹 Clearing backlog...")
    backlog.clear()
    print("Backlog cleared:", backlog)

    print("\n📄 Exporting reports...")
    export_tasks_to_csv("all_tasks.csv")
    export_tasks_to_html("all_tasks.html")
    export_sprint_report_to_csv("Frontend Sprint", "sprint_report.csv")
    export_sprint_report_to_html("Frontend Sprint", "sprint_report.html")

    print("\n✅ Reports generated:")
    print(" - all_tasks.csv")
    print(" - all_tasks.html")
    print(" - sprint_report.csv")
    print(" - sprint_report.html")

    print("\n📊 Listing all sprints from DB:")
    for s in Sprint.list_all():
        print(f" - {s} (status={s.status})")
        for t in s.tasks:
            print(f"   • {t}")

if __name__ == "__main__":
    full_example()
