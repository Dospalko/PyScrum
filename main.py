from pyscrum import Task, Sprint, Backlog
from pyscrum.database import init_db

def main():
    # Initialize the database schema (run once)
    init_db()

    # Create backlog and tasks
    backlog = Backlog()

    task1 = Task("User authentication", "Implement login/logout features")
    task2 = Task("Database schema", "Create initial database schema")
    task3 = Task("API endpoints", "Develop RESTful API")

    backlog.add_task(task1)
    backlog.add_task(task2)
    backlog.add_task(task3)

    # Persist tasks to database
    task1.save()
    task2.save()
    task3.save()

    print("Initial backlog state:")
    print(backlog)

    # Create sprint
    sprint = Sprint("Sprint 1")

    # Move tasks from backlog to sprint
    backlog.move_task_to_sprint(task1.id, sprint)
    backlog.move_task_to_sprint(task2.id, sprint)

    # Update task statuses
    task1.set_status("in_progress")
    task2.set_status("todo")

    print("\nSprint details after adding tasks:")
    print(sprint)
    for task in sprint.tasks:
        print(task)

    print("\nBacklog after moving tasks to sprint:")
    print(backlog)
    for task in backlog.tasks:
        print(task)

if __name__ == "__main__":
    main()
