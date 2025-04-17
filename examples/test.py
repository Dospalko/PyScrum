import pytest
from pyscrum.task import Task
from datetime import datetime


def test_is_high_priority():
    # Vytvoríme úlohu s vysokou prioritou a overíme True
    task_high = Task("High priority task", priority="high")
    assert task_high.is_high_priority() is True

    # Vytvoríme úlohu s nízkou prioritou a overíme False
    task_low = Task("Low priority task", priority="low")
    assert task_low.is_high_priority() is False


def test_toggle_status_transitions(monkeypatch):
    # Zamedzíme ukladaniu do databázy, aby testy boli izolované
    monkeypatch.setattr(Task, 'save', lambda self: None)

    # Vytvoríme úlohu s default statusom 'todo'
    task = Task("Toggle status task")
    assert task.status == "todo"

    # Preklikneme na 'in_progress' a skontrolujeme
    task.toggle_status()
    assert task.status == "in_progress"

    # Preklikneme na 'done' a skontrolujeme
    task.toggle_status()
    assert task.status == "done"

    # Preklikneme späť na 'todo' a skontrolujeme wrap-around
    task.toggle_status()
    assert task.status == "todo"


def test_age_in_days_and_seconds(monkeypatch):
    # Zamockujeme datetime.now() v module pyscrum.task na pevnú hodnotu
    import pyscrum.task as task_module
    class FixedDatetime(datetime):
        @classmethod
        def now(cls):
            return cls(2025, 4, 17, 12, 0, 0)

    monkeypatch.setattr(task_module, 'datetime', FixedDatetime)
    # Zamedzíme ukladaniu do DB
    monkeypatch.setattr(Task, 'save', lambda self: None)

    # Vytvoríme úlohu a nastavíme created_at na 2 dni pred pevným časom
    task = Task("Age test task")
    task.created_at = "2025-04-15T12:00:00"

    # Skontrolujeme age_in_days (~2 dni)
    days = task.age_in_days()
    assert abs(days - 2) < 1e-6

    # Skontrolujeme age_in_seconds (~2 * 86400 sekúnd)
    seconds = task.age_in_seconds()
    assert abs(seconds - 2 * 86400) < 1e-3


# Demo script: demo_helpers.py
if __name__ == "__main__":
    from pyscrum.database import init_db
    from pyscrum.task import Task

    print("⏳ Initializing database...")
    init_db()

    print("\n📋 Creating tasks...")
    tasks = [
        Task("Write docs", "Add helper function docs"),
        Task("Fix bugs", "Toggle and overdue tests"),
    ]

    # Ukážka is_high_priority
    print("\n🔖 Priority check:")
    for t in tasks:
        print(f"{t.title}: high priority? {t.is_high_priority()}")

    # Ukážka toggle_status
    print("\n🔄 Toggling status for first task:")
    first = tasks[0]
    print(f"Before: {first.status}")
    first.toggle_status()
    print(f"After: {first.status}")

    # Ukážka age_in_days a age_in_seconds
    print("\n⏱️ Age of tasks:")
    # Simulujeme, že bola vytvorená deň predtým
    import datetime as _dt
    yesterday = (_dt.datetime.now() - _dt.timedelta(days=1)).isoformat()
    tasks[1].created_at = yesterday
    print(f"{tasks[1].title}: {tasks[1].age_in_days():.2f} days, {int(tasks[1].age_in_seconds())} seconds")
