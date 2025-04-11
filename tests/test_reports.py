import os
from pyscrum.task import Task
from pyscrum.sprint import Sprint
from pyscrum.reports import (
    export_tasks_to_csv,
    export_sprint_report_to_csv,
    export_tasks_to_html,
    export_sprint_report_to_html,
)


def test_export_tasks_to_csv(tmp_path):
    Task("CSV Export Test").save()
    file = tmp_path / "tasks.csv"
    export_tasks_to_csv(filename=str(file))

    assert file.exists()
    content = file.read_text()
    assert "CSV Export Test" in content


def test_export_sprint_to_csv(tmp_path):
    task = Task("Sprint CSV Task")
    task.save()

    sprint = Sprint("CSV Sprint")
    sprint.add_task(task)

    file = tmp_path / "sprint.csv"
    export_sprint_report_to_csv("CSV Sprint", filename=str(file))

    assert file.exists()
    content = file.read_text()
    assert "Sprint CSV Task" in content


def test_export_tasks_to_html(tmp_path):
    Task("HTML Export Test").save()
    file = tmp_path / "tasks.html"
    export_tasks_to_html(filename=str(file))

    assert file.exists()
    content = file.read_text()
    assert "HTML Export Test" in content
    assert "<table>" in content


def test_export_sprint_to_html(tmp_path):
    task = Task("Sprint HTML Task")
    task.save()

    sprint = Sprint("HTML Sprint")
    sprint.add_task(task)

    file = tmp_path / "sprint.html"
    export_sprint_report_to_html("HTML Sprint", filename=str(file))

    assert file.exists()
    content = file.read_text()
    assert "Sprint HTML Task" in content
    assert "<table>" in content
