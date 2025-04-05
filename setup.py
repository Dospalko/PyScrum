from pyscrum import Task, Sprint, Backlog

# Create backlog and tasks
backlog = Backlog()

task_login = Task("User login", "Implement authentication flow")
task_db = Task("Database setup", "Define schema and migrations")

backlog.add_task(task_login)
backlog.add_task(task_db)

# Create sprint
sprint_1 = Sprint("Sprint 1")

# Move tasks to sprint
backlog.move_task_to_sprint(task_login.id, sprint_1)

# Update task status
task_login.set_status("in_progress")

# Display sprint overview
print(sprint_1)
for task in sprint_1.tasks:
    print(task)

# Display remaining backlog tasks
print(backlog)
