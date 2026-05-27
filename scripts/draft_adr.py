"""draft_adr.py — Drafter procedure (CLI entry point).

Writes body + proposed subtasks to Firestore via the ADR's existing stub doc,
then records each proposed subtask as a `proposed`-status subtask linked to
the ADR. Replaces the old `dcli update-adr --body-file` + manual subtask steps.

Usage:
  python scripts/draft_adr.py \\
    --adr-id <firestore-doc-id> \\
    --body-file .work/adr.md \\
    --title "ADR 0086: cache-busting strategy" \\
    --proposed-subtasks .work/subtasks.json

subtasks.json schema:
  [{"title": "...", "description": "...", "priority": 2}, ...]
  `description` and `priority` are optional.
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

# Resolve firestore_db.py — try repo root relative to this script's location
_here = Path(__file__).resolve().parent
for _candidate in [_here.parent, _here]:
    if (_candidate / "firestore_db.py").exists():
        sys.path.insert(0, str(_candidate))
        break
import firestore_db as db


def main():
    parser = argparse.ArgumentParser(
        description="Drafter: write ADR body + proposed subtasks to Firestore."
    )
    parser.add_argument("--adr-id", dest="adr_id", required=True,
                        help="Firestore doc ID of the reserved ADR stub.")
    parser.add_argument("--body-file", dest="body_file", required=True,
                        help="Path to a Markdown file containing the full ADR body.")
    parser.add_argument("--title", required=True,
                        help="Human-readable ADR title (e.g. 'ADR 0086: cache strategy').")
    parser.add_argument("--proposed-subtasks", dest="proposed_subtasks", default=None,
                        help="Path to a JSON file with a list of proposed subtask objects "
                             "[{title, description?, priority?}].")
    args = parser.parse_args()

    # --- Validate inputs ---
    body_path = Path(args.body_file)
    if not body_path.exists():
        print(f"ERROR: --body-file not found: {body_path}", file=sys.stderr)
        sys.exit(1)
    body = body_path.read_text(encoding="utf-8")

    proposed = []
    if args.proposed_subtasks:
        st_path = Path(args.proposed_subtasks)
        if not st_path.exists():
            print(f"ERROR: --proposed-subtasks file not found: {st_path}", file=sys.stderr)
            sys.exit(1)
        proposed = json.loads(st_path.read_text(encoding="utf-8"))
        if not isinstance(proposed, list):
            print("ERROR: --proposed-subtasks JSON must be a list of objects.", file=sys.stderr)
            sys.exit(1)

    # --- Fetch the ADR stub to get project ---
    adr = db.get_adr(args.adr_id)
    if not adr:
        print(f"ERROR: ADR {args.adr_id} not found in Firestore.", file=sys.stderr)
        sys.exit(1)
    project = adr.get("project")
    if not project:
        print("ERROR: ADR has no project field. Run reserve-adr with --project.", file=sys.stderr)
        sys.exit(1)

    # --- Update the ADR doc ---
    db.update_adr(args.adr_id, title=args.title, body=body, status="proposed")

    # --- Create proposed subtasks ---
    created_subtask_ids = []
    for st in proposed:
        if not st.get("title"):
            print(f"WARNING: skipping subtask with no title: {st}", file=sys.stderr)
            continue
        sid = db.add_subtask(
            feature_id=None,
            adr_id=args.adr_id,
            status="proposed",
            title=st["title"],
            description=st.get("description", ""),
            priority=int(st.get("priority", 3)),
            project=project,
        )
        created_subtask_ids.append(sid)

    # --- Touch projects_meta ---
    db._touch_meta(project, by="drafter", kind="adr_drafted")

    result = {
        "ok": True,
        "adr_id": args.adr_id,
        "adr_number": adr.get("number"),
        "title": args.title,
        "status": "proposed",
        "project": project,
        "proposed_subtasks_created": len(created_subtask_ids),
        "subtask_ids": created_subtask_ids,
    }
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
