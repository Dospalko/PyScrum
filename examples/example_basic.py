from datetime import date, timedelta
from pyscrum.database import init_db
from pyscrum.task import Task
from pyscrum.backlog import Backlog

def setup_sample_tasks():
    """Vytvorí a pridá do backlogu ukážkové úlohy so statusmi, prioritami, tagmi a dátumami."""
    init_db()
    backlog = Backlog()
    backlog.clear()

    task1 = Task("Task 1", "High priority, done", priority="high")
    task1.set_status("done")
    task1.tags = ["urgent", "dev"]
  
    task2 = Task("Task 2", "Medium priority, todo", priority="medium")
    task2.set_status("todo")
    task2.tags = ["frontend"]
   
    task3 = Task("Task 3", "Low priority, in progress", priority="low")
    task3.set_status("in_progress")
    task3.tags = ["backend", "urgent"]
  
    for task in [task1, task2, task3]:
        backlog.add_task(task)

    print("📦 Sample tasks setup complete.\n")
    return backlog

def test_filter_by_status(backlog):
    print("🔍 Tasks with status = 'todo':")
    for task in backlog.list_by_status("todo"):
        print(f" - {task}")
    print()

def test_filter_by_priority(backlog):
    print("🔍 Tasks with priority = 'high':")
    for task in backlog.list_by_priority("high"):
        print(f" - {task}")
    print()

def test_find_by_tag(backlog):
    print("🏷️ Tasks with tag = 'urgent':")
    for task in backlog.find_by_tag("urgent"):
        print(f" - {task}")
    print()

def test_has_task(backlog):
    task_id = backlog.tasks[0].id
    print(f"✅ Has task with id {task_id[:8]}: {backlog.has_task(task_id)}")
    print(f"❌ Has task with id 'nonexistent': {backlog.has_task('nonexistent')}")
    print()

def test_count_by_status(backlog):
    print("📊 Task counts by status:")
    counts = backlog.count_by_status()
    for status, count in counts.items():
        print(f" - {status}: {count}")
    print()

if __name__ == "__main__":
    backlog = setup_sample_tasks()
    test_filter_by_status(backlog)
    test_filter_by_priority(backlog)
    test_find_by_tag(backlog)
    test_has_task(backlog)
    test_count_by_status(backlog)
