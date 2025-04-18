from pyscrum.database import init_db
from pyscrum.task import Task
from pyscrum.backlog import Backlog
from pyscrum.sprint import Sprint

print("⏳ Initializing database...")
init_db()

print("\n📋 Creating backlog and tasks...")
backlog = Backlog()
task1 = Task("Implement login", "Google + Email")
task2 = Task("Design database", "Initial schema")
task3 = Task("Build API", "RESTful endpoints")

for task in [task1, task2, task3]:
    task.save()
    backlog.add_task(task)

print("\n✅ Backlog populated:")
for task in backlog.tasks:
    print(" -", task)

print("\n🚀 Creating sprint and adding tasks...")
sprint = Sprint("Sprint 1")
sprint.add_task(task1)
sprint.add_task(task2)

print("\n📝 Updating task statuses...")
task1.set_status("in_progress")
task2.set_status("todo")

print("\n📈 Sprint overview:")
print(sprint)
for task in sprint.tasks:
    print(" -", task)

# --- Nové: vyhľadávanie úloh v sprinte podľa textu ---
print("\n🔍 Searching sprint tasks for 'Design':")
matches = sprint.search_tasks("Design")
if matches:
    for t in matches:
        print(" -", t)
else:
    print("No matches found.")


sprint = Sprint.from_name("Sprint 1")
# predpokladáme, že už máš do sprintu pridelené nejaké úlohy
counts = sprint.count_tasks_by_priority()
print("📊 Tasks by priority:")
for prio, num in counts.items():
    print(f"  - {prio}: {num}")
# Výstup môže byť napr.:
#   - high: 3
#   - medium: 5
#   - low: 2
