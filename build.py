#!/usr/bin/env python3
"""Build both apps into dist/. Run from anywhere: `python build.py`."""
import subprocess, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
for script in ("src/recipe/build_app.py", "src/workout/build_workout.py"):
    print(f"--- {script} ---")
    subprocess.run([sys.executable, os.path.join(HERE, script)], check=True)
print("Done. Deploy the contents of dist/ to GitHub Pages.")
