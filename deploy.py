#!/usr/bin/env python3
"""Rebuild the apps and publish the site to the gh-pages branch.

Usage:  python deploy.py
Then GitHub serves it at https://davidpartridge3.github.io/apps/ within ~1 min.
(One-time: repo Settings -> Pages -> Source -> Deploy from a branch -> gh-pages -> /root.)
"""
import subprocess, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))

def git(*args, check=True):
    return subprocess.run(["git", *args], cwd=HERE, check=check)

# 1. rebuild kitchen + workout into dist/
subprocess.run([sys.executable, os.path.join(HERE, "build.py")], check=True)

# 2. commit any changes on main (no-op if nothing changed)
git("add", "-A")
git("commit", "-m", "Rebuild site", check=False)
git("push", "origin", "main")

# 3. re-split dist/ into gh-pages and force-push it
sha = subprocess.check_output(
    ["git", "subtree", "split", "--prefix", "dist", "main"], cwd=HERE).decode().strip()
git("push", "origin", f"{sha}:gh-pages", "--force")
print("\nDeployed. Live at https://davidpartridge3.github.io/apps/ shortly.")
