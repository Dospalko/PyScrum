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
    # Vytvoríme fake triedu, ktorá vráti fixný čas
    class FixedDatetime(datetime):
        @classmethod
        def now(cls):
            return cls(2025, 4, 17, 12, 0, 0)

    monkeypatch.setattr(task_module, 'datetime', FixedDatetime)
    # Zamedzíme ukladaniu do DB
    monkeypatch.setattr(Task, 'save', lambda self: None)

    # Vytvoríme úlohu, jej created_at bude '2025-04-17T12:00:00'
    task = Task("Age test task")
    # Nastavíme created_at na 2 dni pred pevným časom
    task.created_at = "2025-04-15T12:00:00"

    # Skontrolujeme age_in_days (~2 dni)
    days = task.age_in_days()
    assert abs(days - 2) < 1e-6

    # Skontrolujeme age_in_seconds (~2 * 86400 sekúnd)
    seconds = task.age_in_seconds()
    assert abs(seconds - 2 * 86400) < 1e-3
