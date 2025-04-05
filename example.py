from pyscrum import Task, Sprint, Backlog
from pyscrum.database import init_db

# Inicializácia databázy (ak je to prvý beh)
init_db()

# Vytvor backlog a pridaj úlohy
backlog = Backlog()
task1 = Task("Prepare presentation", "Create slides for project presentation")
task2 = Task("Setup server", "Deploy application to staging environment")

backlog.add_task(task1)
backlog.add_task(task2)

# Ulož úlohy do databázy
task1.save()
task2.save()

# Vytvor nový sprint
sprint = Sprint("Release Sprint")

# Presuň úlohu z backlogu do sprintu
backlog.move_task_to_sprint(task1.id, sprint)

# Aktualizuj status úlohy
task1.set_status("in_progress")

# Výpis stavu sprintu
print("Sprint overview:")
print(sprint)
for task in sprint.tasks:
    print(task)

# Výpis stavu backlogu
print("\nRemaining tasks in backlog:")
print(backlog)
for task in backlog.tasks:
    print(task)
