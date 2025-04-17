import pytest
from pyscrum.task import Task


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
