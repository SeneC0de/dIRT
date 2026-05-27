"""approve_adr.py — Approval mutation (CLI fallback for the dASH Approve button).

Executes the full ADR approval atomically:
  1. Validates ADR status == 'proposed'
  2. Queries proposed subtasks linked to this ADR
  3. Creates a feature (Story) from the ADR
  4. Promotes proposed subtasks → open, links feature_id
  5. Marks the ADR accepted, links feature_id
  6. Updates projects_meta
All Firestore writes in steps 3-6 are submitted as a single batch commit.

Usage:
  python scripts/approve_adr.py --adr-id <id> --approver "Randall"
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from datetime import timezone

_here = Path(__file__).resolve().parent
for _candidate in [_here.parent, _here]:
    if (_candidate / "firestore_db.py").exists():
        sys.path.insert(0, str(_candidate))
        break
import firestore_db as db


def main():
    parser = argparse.ArgumentParser(
        description="Approve an ADR: create the feature, materialize subtasks, mark ADR accepted."
    )
    parser.add_argument("--adr-id", dest="adr_id", required=True,
                        help="Firestore doc ID of the ADR to approve.")
    parser.add_argument("--approver", required=True,
                        help="Name of the approver (stored on the feature and ADR).")
    args = parser.parse_args()

    # --- Step 1: Read ADR, validate status ---
    adr = db.get_adr(args.adr_id)
    if not adr:
        print(f"ERROR: ADR {args.adr_id} not found.", file=sys.stderr)
        sys.exit(1)
    if adr.get("status") != "proposed":
        print(
            f"ERROR: ADR {args.adr_id} has status '{adr.get('status')}', expected 'proposed'.",
            file=sys.stderr,
        )
        sys.exit(1)

    project = adr.get("project")
    if not project:
        print("ERROR: ADR has no project field.", file=sys.stderr)
        sys.exit(1)

    # --- Step 2: Query proposed subtasks ---
    proposed_subtasks = db.list_subtasks(adr_id=args.adr_id, status="proposed")

    # --- Step 3-6: Build batch writes ---
    import uuid as _uuid
    ts = db.now()
    ts_str = ts.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

    # New feature doc ID
    new_feature_id = _uuid.uuid4().hex
    feature_name = db._doc_name("features", new_feature_id)

    feature_fields = {
        "project":      db._to_v(project),
        "title":        db._to_v(adr.get("title", "")),
        "status":       db._to_v("open"),
        "adr_id":       db._to_v(args.adr_id),
        "adr_number":   db._to_v(adr.get("number")),
        "priority":     db._to_v(int(adr.get("priority") or 2)),
        "description":  db._to_v(adr.get("description") or ""),
        "author":       db._to_v(args.approver),
        "archived":     db._to_v(False),
        "created_at":   db._to_v(ts),
        "updated_at":   db._to_v(ts),
    }

    writes = []

    # Write 1: create feature
    writes.append({
        "update": {"name": feature_name, "fields": feature_fields},
    })

    # Write 2: backfill feature.id
    writes.append({
        "update": {
            "name": feature_name,
            "fields": {"id": db._to_v(new_feature_id)},
        },
        "updateMask": {"fieldPaths": ["id"]},
    })

    # Writes 3+: update each proposed subtask → open, link feature_id
    for sub in proposed_subtasks:
        sub_name = db._doc_name("subtasks", sub["id"])
        writes.append({
            "update": {
                "name": sub_name,
                "fields": {
                    "status":     db._to_v("open"),
                    "feature_id": db._to_v(new_feature_id),
                    "updated_at": db._to_v(ts),
                },
            },
            "updateMask": {"fieldPaths": ["status", "feature_id", "updated_at"]},
        })

    # Write: update ADR → accepted
    adr_name = db._doc_name("adrs", args.adr_id)
    writes.append({
        "update": {
            "name": adr_name,
            "fields": {
                "status":      db._to_v("accepted"),
                "feature_id":  db._to_v(new_feature_id),
                "accepted_by": db._to_v(args.approver),
                "accepted_at": db._to_v(ts),
                "updated_at":  db._to_v(ts),
            },
        },
        "updateMask": {
            "fieldPaths": ["status", "feature_id", "accepted_by", "accepted_at", "updated_at"]
        },
    })

    # Execute the atomic batch
    db._commit_batch(writes)

    # --- Touch projects_meta (non-critical, outside batch) ---
    db._touch_meta(project, by=args.approver, kind="adr_approved")

    result = {
        "ok": True,
        "adr_id": args.adr_id,
        "adr_number": adr.get("number"),
        "feature_id": new_feature_id,
        "subtasks_materialized": len(proposed_subtasks),
        "project": project,
        "approver": args.approver,
    }
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
