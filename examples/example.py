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

    print("📋 Creating backlog and tasks...")
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

    print("\n🛠️ Updating task description...")
    task1.update_description("Google, Apple ID & Email login")

    print("\n🔎 Fetching task from backlog...")
    fetched = backlog.get_task(task3.id)
    print(" ✔️ Found in backlog:", fetched)

    print("\n🚀 Creating sprint and adding tasks...")
    sprint = Sprint("Sprint 1")
    sprint.add_task(task1)
    sprint.add_task(task2)

    backlog.remove_task(task1.id)
    backlog.remove_task(task2.id)

    print("\n📝 Updating task statuses...")
    task1.set_status("in_progress")
    task2.set_status("todo")

    print("\n📈 Sprint details:")
    print(sprint)
    for task in sprint.tasks:
        print(" -", task)

    print("\n✏️ Renaming sprint to 'Frontend Sprint'...")
    sprint.update_name("Frontend Sprint")

    print("\n❌ Removing task from sprint...")
    sprint.remove_task(task2)

    print("\n✅ Final sprint:")
    print(sprint)
    for task in sprint.list_tasks():
        print(" -", task)

    sprint.update_name("Frontend Sprint")

    print(sprint)
    for task in sprint.tasks:
            print(task)

    print("\n🧹 Clearing backlog...")
    backlog.clear()
    print("📦 Backlog cleared:", backlog)

    print("\n🧾 Exporting reports...")
    export_tasks_to_csv("all_tasks.csv")
    export_sprint_report_to_csv("Frontend Sprint", "sprint_report.csv")
    export_tasks_to_html("all_tasks.html")
    export_sprint_report_to_html("Frontend Sprint", "sprint_report.html")

    print("\n📄 Reports generated:")
    print(" - all_tasks.csv")
    print(" - sprint_report.csv")
    print(" - all_tasks.html")
    print(" - sprint_report.html")

if __name__ == "__main__":
    full_example()
