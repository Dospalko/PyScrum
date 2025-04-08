from pyscrum.database import init_db
from pyscrum.task import Task
from pyscrum.sprint import Sprint

print("⏳ Initializing database...")
init_db()

print("\n🔍 Searching for tasks containing 'API'...")
results = Task.search("API")
for task in results:
    print(" -", task)

print("\n🔎 Filtering 'todo' tasks in a sprint...")
sprint = Sprint.from_name("Frontend Sprint")
todo_tasks = sprint.get_tasks_by_status("todo")
for task in todo_tasks:
    print(" -", task)
