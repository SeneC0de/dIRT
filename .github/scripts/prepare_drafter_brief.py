"""Pre-step: reserve an ADR number atomically and write a lean drafter brief.

Uses the shared firestore_db.py REST client.

Reads:
  .agent_context.json    — board state (director description, prior ADRs)

Writes:
  drafter_brief.md           — short, doctrine-free brief for the agent
  /tmp/adr_reservation.json  — {adr_id, adr_number} for the post-step
  $GITHUB_OUTPUT             — adr_id, adr_number
"""
import json
import os
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))          # project repos: firestore_db.py in .github/scripts/
sys.path.insert(0, str(_HERE.parent.parent))  # director-pattern: firestore_db.py at repo root
import firestore_db as db


director_id = os.environ["DIRECTOR_ID"]
intent      = os.environ.get("INTENT", "")

with open(".agent_context.json") as f:
    ctx = json.load(f)

director_desc = ctx.get("director", {}).get("description", "")
prior_adrs    = ctx.get("adrs", [])[:5]

# Two paths:
#   1. Pre-reserved by the Cloud Function (drafter intents from chat) — use
#      the provided ADR_ID + ADR_NUMBER env vars. This is the normal path
#      in production; the reservation is transactional so two concurrent
#      messages can't race to the same number.
#   2. No pre-reservation (manual workflow_dispatch, or legacy callers) —
#      reserve here as a fallback. Race-prone but acceptable as a backstop.
pre_adr_id     = os.environ.get("ADR_ID", "").strip()
pre_adr_number = os.environ.get("ADR_NUMBER", "").strip()
if pre_adr_id and pre_adr_number:
    adr_id     = pre_adr_id
    adr_number = int(pre_adr_number)
    print(f"Using pre-reserved ADR {adr_number:04d} (id={adr_id}) from Cloud Function")
else:
    n = db.next_adr_number()
    adr_id = db.add_adr(
        number=n,
        title="(pending)",
        url=None,
        status="draft",
        author="",
        description=intent[:200],
        director_id=director_id,
    )
    adr_number = n
    print(f"Reserved ADR {adr_number:04d} (id={adr_id}) inline (no Cloud Function pre-reservation)")

with open("/tmp/adr_reservation.json", "w") as f:
    json.dump({"adr_id": adr_id, "adr_number": adr_number}, f)

prior_block = "(none yet)"
if prior_adrs:
    lines = []
    for a in prior_adrs:
        num   = a.get("number")
        title = a.get("title", "")
        if isinstance(num, int):
            lines.append(f"- ADR {num:04d}: {title}")
        else:
            lines.append(f"- {title}")
    prior_block = "\n".join(lines)

brief = f"""# Draft ADR {adr_number:04d}

Reserved ADR number: **{adr_number:04d}**.
Firestore ADR id (patch this document with the body): **{adr_id}**

The procedure, stop conditions, and ADR template are in the **write-adr skill**. Follow it.

**ADRs live in Firestore, not git.** Do not create a branch, do not commit files, do not open a PR. Write the body to `.work/adr.md`, then push it into the ADR document via `agent_cli.py update-adr {adr_id} --body-file .work/adr.md --title "..." --status proposed`.

## Request

A user of the **{director_id}** project sent this message:

> {intent}

## Project context

{director_desc or "(no description on file)"}

## Recent ADRs in this project (for tone/format reference)

{prior_block}
"""

with open("drafter_brief.md", "w") as f:
    f.write(brief)

gho = os.environ.get("GITHUB_OUTPUT", "")
if gho:
    with open(gho, "a") as f:
        f.write(f"adr_id={adr_id}\n")
        f.write(f"adr_number={adr_number}\n")

print(f"Reserved ADR {adr_number:04d} (id={adr_id}) for {director_id}")
