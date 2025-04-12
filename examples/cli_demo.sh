#!/bin/bash

echo "🧹 Resetting DB..."
rm -f pyscrum.db

echo "✅ Initializing DB..."
pyscrum init

echo "📝 Adding tasks with priorities..."
pyscrum add-task "Login System" --description "Google & Email login"
pyscrum add-task "Design DB" --description "Initial schema" --priority "high"
pyscrum add-task "Build API" --description "REST endpoints" --priority "medium"
pyscrum add-task "Write Tests" --description "Unit tests coverage" --priority "high"

echo -e "\n📋 Listing all tasks..."
pyscrum list-tasks
pyscrum list-backlog

echo -e "\n📊 Listing tasks by priority..."
echo "High priority tasks:"
pyscrum list-by-priority high
echo "Medium priority tasks:"
pyscrum list-by-priority medium

echo -e "\n🔄 Setting task status..."
ID=$(pyscrum list-backlog | grep "Login System" | sed 's/.*<Task \([^:]*\):.*/\1/')
SHORT_ID=${ID:0:8}
pyscrum set-status "$SHORT_ID" in_progress

echo -e "\n🔍 Getting task by ID..."
pyscrum get-task "$SHORT_ID"

echo -e "\n🚀 Creating and managing sprint..."
pyscrum create-sprint "Sprint 1"
pyscrum start-sprint "Spr"

echo -e "\n➕ Adding tasks to sprint..."
pyscrum add-to-sprint "$SHORT_ID" "Sprint 1"
DB_ID=$(pyscrum list-backlog | grep "Design DB" | sed 's/.*<Task \([^:]*\):.*/\1/')
pyscrum add-to-sprint "${DB_ID:0:8}" "Sprint 1"

echo -e "\n📋 Listing sprint tasks..."
pyscrum list-sprint-tasks "Sprint 1"

echo -e "\n📊 Showing sprint statistics..."
pyscrum sprint-stats "Sprint 1"

echo -e "\n🔄 Updating task status in sprint..."
pyscrum set-status "${DB_ID:0:8}" done

echo -e "\n📊 Updated sprint statistics..."
pyscrum sprint-stats "Sprint 1"

echo -e "\n➖ Removing task from sprint..."
pyscrum remove-from-sprint "$SHORT_ID" "Sprint 1"

echo -e "\n📂 Listing tasks by status..."
echo "Todo tasks:"
pyscrum list-tasks-by-status todo
echo "In progress tasks:"
pyscrum list-tasks-by-status in_progress
echo "Done tasks:"
pyscrum list-tasks-by-status done

echo -e "\n📦 Archiving sprint..."
pyscrum archive-sprint "Sprint 1"

echo -e "\n📤 Exporting sprint report..."
pyscrum export-sprint-report "Sprint 1"

echo -e "\n🗑️ Removing a task..."
pyscrum remove-task "$SHORT_ID"

echo -e "\n✅ CLI demo finished!"
