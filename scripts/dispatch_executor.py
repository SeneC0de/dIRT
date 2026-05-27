"""dispatch_executor.py — Post-approval marker for the execute-adr skill.

Called by the execute-adr skill when it finishes implementation to record
the branch and signal Jones that the branch is ready.

Usage:
  python scripts/dispatch_executor.py --feature-id <id> --branch impl/adr-0086-slug
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
        description="Record implementation branch on a feature and emit executor-dispatched event."
    )
    parser.add_argument("--feature-id", dest="feature_id", required=True,
                        help="Firestore feature (Story) doc ID.")
    parser.add_argument("--branch", required=True,
                        help="Implementation branch name (e.g. impl/adr-0086-cache-busting).")
    args = parser.parse_args()

    feat = db.get_feature(args.feature_id)
    if not feat:
        print(f"ERROR: feature {args.feature_id} not found.", file=sys.stderr)
        sys.exit(1)

    project = feat.get("project")

    # Record the branch on the feature
    db.update_feature(args.feature_id, branch=args.branch, status="needs-testing")

    # Emit a note event
    db.add_event(
        project,
        "note",
        feature_id=args.feature_id,
        payload=json.dumps({"note": f"execute-adr branch ready: {args.branch}"}),
    )

    # Touch projects_meta
    db._touch_meta(project, by="execute-adr", kind="executor_dispatched",
                   doc_id=args.feature_id)

    result = {
        "ok": True,
        "feature_id": args.feature_id,
        "branch": args.branch,
        "status": "needs-testing",
        "project": project,
    }
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
