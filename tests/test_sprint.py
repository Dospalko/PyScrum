import pytest
from pyscrum.task import Task
from pyscrum.sprint import Sprint
from pyscrum.database import init_db, get_connection

# Ensure database schema exists
init_db()


def test_sprint_creation():
    sprint = Sprint("Test Sprint")
    assert sprint.name == "Test Sprint"
    assert sprint.status == "Planned"
    assert isinstance(sprint.tasks, list)
    assert len(sprint.tasks) == 0


def test_add_and_list_tasks():
    sprint = Sprint("AddTaskSprint")
    task = Task("Test Task", "Description")
    task.save()

    sprint.add_task(task)
    tasks = sprint.list_tasks()

    assert len(tasks) == 1
    assert tasks[0].id == task.id


def test_remove_task():
    sprint = Sprint("RemoveTaskSprint")
    task = Task("Removable Task", "To be removed")
    task.save()
    sprint.add_task(task)

    assert len(sprint.list_tasks()) == 1
    sprint.remove_task(task)
    assert len(sprint.list_tasks()) == 0


def test_start_and_complete_sprint():
    sprint = Sprint("LifecycleSprint")
    sprint.save()
    sprint.start()
    assert sprint.status == "In Progress"

    sprint.complete()
    assert sprint.status == "Completed"

    with get_connection() as conn:
        row = conn.execute(
            "SELECT status FROM sprints WHERE name=?", (sprint.name,)
        ).fetchone()
        assert row[0] == "Completed"


def test_get_tasks_by_status():
    sprint = Sprint("FilterStatusSprint")
    task1 = Task("Task 1", "desc", status="todo")
    task2 = Task("Task 2", "desc", status="done")
    task1.save()
    task2.save()

    sprint.add_task(task1)
    sprint.add_task(task2)

    todo_tasks = sprint.get_tasks_by_status("todo")
    done_tasks = sprint.get_tasks_by_status("done")

    assert len(todo_tasks) == 1
    assert todo_tasks[0].status == "todo"
    assert len(done_tasks) == 1
    assert done_tasks[0].status == "done"


def test_update_sprint_name():
    sprint = Sprint("Old Name")
    sprint.save()
    sprint.update_name("New Name")

    assert sprint.name == "New Name"
    with get_connection() as conn:
        result = conn.execute(
            "SELECT name FROM sprints WHERE name=?", ("New Name",)
        ).fetchone()
        assert result is not None


def test_repr_contains_name():
    sprint = Sprint("ReprTest")
    result = repr(sprint)
    assert "ReprTest" in result
    assert result.startswith("<Sprint")


def test_add_invalid_type_raises():
    sprint = Sprint("InvalidTaskSprint")
    with pytest.raises(TypeError):  # ✅ očakávaj TypeError, nie AttributeError
        sprint.add_task("not-a-task")


def test_remove_nonexistent_task_does_not_crash():
    sprint = Sprint("RemoveGhostTask")
    ghost_task = Task("Ghost", "Never added")
    # should silently ignore
    sprint.remove_task(ghost_task)
    assert True  # no exception = pass


def test_duplicate_task_not_added_twice():
    sprint = Sprint("DuplicateTaskSprint")
    task = Task("Once only", "desc")
    task.save()
    sprint.add_task(task)
    sprint.add_task(task)  # should not be added again
    assert len(sprint.list_tasks()) == 1
