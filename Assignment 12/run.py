"""
run.py — SentinelPay Assignment 12 startup script.
Uses PYTHONPATH env var instead of sys.path so uvicorn's reload
subprocess inherits the correct paths.

Run from inside Assignment 12/:
    python run.py
"""

import os
import sys
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
A10 = os.path.join(REPO, "Assignment 10")
A11 = os.path.join(REPO, "Assignment 11")

# Build PYTHONPATH — propagates into every subprocess uvicorn spawns
paths = [HERE, A10, A11]
existing = os.environ.get("PYTHONPATH", "")
if existing:
    paths.append(existing)
os.environ["PYTHONPATH"] = os.pathsep.join(paths)

for p in paths:
    if p not in sys.path:
        sys.path.insert(0, p)

if __name__ == "__main__":
    subprocess.run(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "api.main:app",
            "--host",
            "0.0.0.0",
            "--port",
            "8000",
            "--reload",
            "--reload-dir",
            HERE,
        ]
    )
