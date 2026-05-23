"""Post-agent step: read the agent's reply file and post it to the chat thread.

The reply file location moved when we discovered the agent sandbox forbids
writes to /tmp/. The agent now writes to `.work/agent_reply.txt` in the
workspace. We check workspace first, then fall back to /tmp/ for any
in-flight legacy runs.
"""
import os
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))          # project repos: firestore_db.py in .github/scripts/
sys.path.insert(0, str(_HERE.parent.parent))  # director-pattern: firestore_db.py at repo root
import firestore_db as db


# Where the agent might have written its reply. First match wins.
_CANDIDATES = [
    ".work/agent_reply.txt",   # current convention (agent writes here)
    "agent_reply.txt",         # alt workspace root
    "/tmp/agent_reply.txt",    # legacy / drafter post-step still writes here
]

body = None
for path in _CANDIDATES:
    if os.path.exists(path):
        with open(path) as f:
            body = f.read().strip()
        print(f"Reply read from: {path}")
        break

if not body:
    job_status = os.environ.get("JOB_STATUS", "unknown")
    body = f"Agent run finished (status: {job_status}). Check GitHub Actions for details."

thread_id   = os.environ["THREAD_ID"]
from_name   = os.environ["FROM_NAME"]
to_name     = os.environ["TO_NAME"]
thread_type = os.environ.get("THREAD_TYPE", "user_director")

db.add_message(thread_id, thread_type, from_name, to_name, body)

print(f"Reply posted to thread: {thread_id}")
print(f"Body: {body[:120]}")
