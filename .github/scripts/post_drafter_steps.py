"""Post-step (drafter path): create the implementation Story on the board.

The drafter agent has already persisted the ADR body to Firestore via
`agent_cli.py update-adr --body-file ...`. This step's job is just to:

  1. Read the drafter's result summary
  2. Create the Story (Feature) on the board, status=blocked, linked to the ADR
  3. Format the user-facing reply

Runs even on agent failure. If no agent result is present, leaves the
reservation stub on the board and writes a fallback reply.

Reads:
  /tmp/adr_reservation.json   — {adr_id, adr_number} from the pre-step
  .work/agent_result.json     — agent's deliverable summary

Writes:
  Firestore: features/{id} created on success
  /tmp/agent_reply.txt        — user-facing reply for post_reply.py
"""
import json
import os
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))          # project repos: firestore_db.py in .github/scripts/
sys.path.insert(0, str(_HERE.parent.parent))  # director-pattern: firestore_db.py at repo root
import firestore_db as db


director_id   = os.environ["DIRECTOR_ID"]
director_name = os.environ.get("DIRECTOR_NAME", director_id)

reservation_path = "/tmp/adr_reservation.json"

# Where the drafter might have written the result. First match wins.
_RESULT_CANDIDATES = [
    ".work/agent_result.json",  # current convention (agent writes here)
    "agent_result.json",        # alt workspace root
    "/tmp/agent_result.json",   # legacy
]

if not os.path.exists(reservation_path):
    # Pre-step never ran (e.g. coder path, or pre-step crashed).
    print("No reservation file; nothing to do.")
    if not os.path.exists("/tmp/agent_reply.txt"):
        with open("/tmp/agent_reply.txt", "w") as f:
            f.write("Agent run did not produce an ADR. Check the GitHub Actions log.")
    sys.exit(0)

with open(reservation_path) as f:
    res = json.load(f)
adr_id     = res["adr_id"]
adr_number = int(res["adr_number"])

result = None
for cand in _RESULT_CANDIDATES:
    if os.path.exists(cand):
        try:
            with open(cand) as f:
                result = json.load(f)
            print(f"Result read from: {cand}")
            break
        except Exception as e:
            print(f"Could not parse {cand}: {e}")

# Success path: agent wrote a result with at least enough info to identify the ADR.
# The agent has already patched the ADR document with body, title, status — we just
# create the implementation Story on the board.
if result and (result.get("adr_id") or result.get("adr_number") or result.get("adr_title")):
    title   = result.get("adr_title") or "(untitled)"
    summary = result.get("decision_summary") or ""

    # Defensive: if the agent forgot to flip status, do it here.
    current = db.get_adr(adr_id) or {}
    if current.get("status") == "draft":
        db.update_adr(adr_id, status="proposed")

    story_title = f"[ADR {adr_number:04d}] {title}"
    story_desc  = f"Implements ADR {adr_number:04d}. Awaiting User review on the board.\n\n{summary}"
    feature_id  = db.add_feature(director_id, story_title, story_desc, priority=3,
                                 author=director_name)
    db.update_feature(feature_id,
                      status="blocked",
                      adr_number=adr_number)
    db.add_event(director_id, "feature_created",
                 user=director_name,
                 feature_id=feature_id,
                 payload=json.dumps({"title": title, "adr_number": adr_number}))

    reply = (
        f"ADR {adr_number:04d}: {title}\n"
        f"{summary}\n"
        f"On the board for review."
    )
    print(f"Created story {feature_id} for ADR {adr_id}")
else:
    reply = (
        f"ADR {adr_number:04d} was reserved but the drafter did not produce a result. "
        f"Check the GitHub Actions run; the stub is on the board."
    )
    print(f"No agent result; left ADR {adr_id} as draft stub.")

with open("/tmp/agent_reply.txt", "w") as f:
    f.write(reply)
