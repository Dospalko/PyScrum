
# Welcome to PyScrum 👋

**PyScrum** is a lightweight and developer-friendly library for managing tasks, sprints, and backlogs — built with simplicity in mind.

## Features

- 🧩 Manage tasks and sprints in Python
- 🧪 CLI with `typer` for productivity workflows
- 📦 CSV & HTML reports
- 💾 SQLite backend, zero setup
- 🧪 Built-in tests and CI

---

## Installation

```bash
pip install git+https://github.com/dospalko/pyscrum.git@v0.0.1
```

## Usage

Use the Python API or the CLI:

```bash
pyscrum init
pyscrum add-task "Implement login" --description "Google & Email"
pyscrum list-backlog
```

---
```

---

### ✅ `docs/cli.md`

```markdown
# CLI Usage

The `pyscrum` CLI provides commands to manage your backlog, sprints and tasks directly from the terminal.

---

## ⚙️ Setup

```bash
pyscrum init
```

---

## ✅ Task management

| Command | Description |
|--------|-------------|
| `add-task <title> [--description]` | Create a new task |
| `list-backlog` | Show all backlog tasks |
| `set-status <id> <status>` | Set task status |
| `get-task <id>` | Show task details |
| `remove-task <id>` | Delete task |

Status options: `todo`, `in_progress`, `done`

---

## 🚀 Sprint management

| Command | Description |
|--------|-------------|
| `create-sprint <name>` | Create a sprint |
| `start-sprint <prefix>` | Start sprint (sets status) |
| `archive-sprint <name>` | Archive sprint |

---

## 📄 Reports

| Command | Description |
|--------|-------------|
| `export-sprint-report <sprint_name>` | Exports report to CSV & HTML |

---

## 🧪 Examples

```bash
pyscrum add-task "Login" --description "Email + Google"
pyscrum set-status 123abcde done
pyscrum create-sprint "Frontend Sprint"
pyscrum start-sprint Front
pyscrum archive-sprint "Frontend Sprint"
pyscrum export-sprint-report "Frontend Sprint"
```
```

---

