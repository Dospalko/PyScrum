#!/bin/bash

echo "🧹 Resetting DB..."
rm -f pyscrum.db

echo "✅ Initializing DB..."
pyscrum init

echo "📝 Adding tasks..."
pyscrum add-task "Login System" --description "Google & Email login"
pyscrum add-task "Design DB" --description "Initial schema"
pyscrum add-task "Build API" --description "REST endpoints"

echo -e "\n📋 Listing all tasks..."
pyscrum list-tasks
pyscrum list-backlog

echo -e "\n🔄 Setting task status..."
ID=$(pyscrum list-backlog | grep "Login System" | sed 's/.*<Task \([^:]*\):.*/\1/')
SHORT_ID=${ID:0:8}
pyscrum set-status "$SHORT_ID" in_progress

echo -e "\n🔍 Getting task by ID..."
pyscrum get-task "$SHORT_ID"

echo -e "\n📦 Removing a task..."
pyscrum remove-task "$SHORT_ID"

echo -e "\n🚀 Creating and starting sprint..."
pyscrum create-sprint "Sprint 1"
pyscrum start-sprint "Spr"

echo -e "\n📦 Archiving sprint..."
pyscrum archive-sprint "Sprint 1"

echo -e "\n📂 Listing tasks by status 'todo'..."
pyscrum list-tasks-by-status todo

echo -e "\n📂 Listing tasks by status 'in_progress'..."
pyscrum list-tasks-by-status in_progress

echo -e "\n📤 Exporting sprint report..."
pyscrum export-sprint-report "Sprint 1"

echo -e "\n✅ CLI demo finished!"
