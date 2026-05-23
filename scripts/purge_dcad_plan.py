"""One-off: purge the dcad-plan Director without touching his tasks.

Removes:
  - directors/dcad-plan          (the Director doc)
  - agents/* where director_id == "dcad-plan"   (so nobody talks to him)

Leaves alone:
  - subtasks, features, epics with director_id == "dcad-plan"
    (orphaned but preserved per request)

Run from repo root:  python scripts/purge_dcad_plan.py --yes
"""
import argparse, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import firestore_db as db

DID = "dcad-plan"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--yes", action="store_true", help="confirm destructive op")
    args = ap.parse_args()
    if not args.yes:
        raise SystemExit("destructive op — pass --yes to confirm")

    doc = db.get_director(DID)
    if not doc:
        print(f"director {DID!r} not found — nothing to do")
        return

    agents = db.list_agents(DID)
    print(f"deleting director {DID!r} ({doc.get('name')!r}) and {len(agents)} agent(s)")

    for a in agents:
        db._delete("agents", a["id"])
    db._delete("directors", DID)

    print("done.")


if __name__ == "__main__":
    main()
