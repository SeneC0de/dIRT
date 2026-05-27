"""mark_tested.py — Mark a Story done after Jones confirms tests pass.

Usage:
  python scripts/mark_tested.py --feature-id <id>
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
for _candidate in [_here.parent, _here]:
    if (_candidate / "firestore_db.py").exists():
        sys.path.insert(0, str(_candidate))
        break
import firestore_db as db


def main():
    parser = argparse.ArgumentParser(
        description="Mark a Story (feature) done after testing passes."
    )
    parser.add_argument("--feature-id", dest="feature_id", required=True,
                        help="Firestore feature (Story) doc ID.")
    args = parser.parse_args()

    feat = db.get_feature(args.feature_id)
    if not feat:
        print(f"ERROR: feature {args.feature_id} not found.", file=sys.stderr)
        sys.exit(1)

    project = feat.get("project")
    ts = db.now()

    db.update_feature(args.feature_id, status="done", completed_at=ts)

    # Touch projects_meta
    db._touch_meta(project, by="jones", kind="feature_done", doc_id=args.feature_id)

    result = {
        "ok": True,
        "feature_id": args.feature_id,
        "status": "done",
        "completed_at": str(ts),
        "project": project,
    }
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
