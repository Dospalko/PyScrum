import subprocess
import os

examples = [
    "example_basic.py",
    "example_manage_sprint.py",
    "example_search.py",
    "example_export.py"
]

print("🚀 Running all PyScrum examples...\n")

for script in examples:
    print(f"🔧 Running {script}...")
    path = os.path.join(os.path.dirname(__file__), script)
    try:
        subprocess.run(["python3", path], check=True)
        print(f"✅ {script} completed.\n")
    except subprocess.CalledProcessError:
        print(f"❌ {script} failed.\n")

print("🏁 All examples finished.")
