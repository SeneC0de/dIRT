#!/usr/bin/env python
"""Migrate Firestore directors collection to single-Director multi-project model.

Per ADR 0038 (dIRT: Single-Director, Multi-Project Runtime):

- Each project record (dcad, derp, dweb, dace, dash, dOCS, dpart) gets:
    runtime:          "dirt"
    commit_signature: {name, email}
    github_remote:    <url>     (where known)
    repo_path:        <local>   (where known)

- directors/dirt gets:
    runtime:          "dirt"
    owned_projects:   [<7 ids>]

This is a SEMANTIC SHIFT, not a data migration. No features/subtasks are touched.
The `director_id` field on features/subtasks remains unchanged — under the new
model it now functions as `project_id` for project records.

Idempotent. Re-runs are safe (upsert_director merges fields). updated_at is
touched on every run, but no other state moves.

Run from anywhere:
    python C:/Users/randa/source/repos/dIRT/scripts/migrate_to_multi_project_runtime.py
"""
from __future__ import annotations
import sys
from pathlib import Path

# This script lives in scripts/; firestore_db.py is at the repo root.
_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

import firestore_db as fdb  # noqa: E402


PROJECTS = {
    "dcad": {
        "commit_signature": {"name": "Carl Sagan", "email": "dcad@dapp-controls.com"},
        "github_remote": "https://github.com/dapp-controls/dCAD.git",
        "repo_path": r"C:\Users\randa\source\repos\dCAD",
    },
    "derp": {
        "commit_signature": {"name": "Benjamin Franklin", "email": "derp@dapp-controls.com"},
        "github_remote": "https://github.com/dapp-controls/dERP.git",
        "repo_path": r"C:\Users\randa\source\repos\dERP",
    },
    "dweb": {
        "commit_signature": {"name": "Tim Berners-Lee", "email": "dweb@dapp-controls.com"},
        "github_remote": "https://github.com/dapp-controls/dWEB.git",
        "repo_path": r"C:\Users\randa\source\repos\VitalisCAD-Web",
    },
    "dace": {
        "commit_signature": {"name": "Calvin Cordozar Broadus Jr", "email": "dace@dapp-controls.com"},
        "github_remote": "https://github.com/dapp-controls/dACE.git",
        "repo_path": r"C:\Users\randa\source\repos\dACE-filter-temp",
    },
    "dash": {
        "commit_signature": {"name": "Hermione Granger", "email": "dash@dapp-controls.com"},
        "github_remote": "https://github.com/dapp-controls/dASH.git",
        "repo_path": r"C:\Users\randa\source\repos\dASH",
    },
    "dOCS": {
        "commit_signature": {"name": "Alex Trebek", "email": "docs@dapp-controls.com"},
        # No local repo or known remote for dOCS yet.
    },
    "dpart": {
        "commit_signature": {"name": "Dmitri Mendeleev", "email": "dpart@dapp-controls.com"},
        "github_remote": "https://github.com/dapp-controls/dPART.git",
        "repo_path": r"C:\Users\randa\source\repos\dC-TopPart",
    },
}

OWNED_PROJECTS = list(PROJECTS.keys())


def main() -> int:
    print("Migrating directors/ collection to multi-project runtime model (ADR 0038)")
    print()

    print("Updating project records:")
    for project_id, fields in PROJECTS.items():
        existing = fdb.get_director(project_id)
        if existing is None:
            print(f"  WARN: directors/{project_id} does not exist - skipping.")
            continue
        update = {"runtime": "dirt"}
        update.update(fields)
        fdb.upsert_director(project_id, **update)
        added = sorted(update.keys())
        print(f"  OK   directors/{project_id}: set {added}")
    print()

    print("Updating directors/dirt:")
    fdb.upsert_director("dirt", runtime="dirt", owned_projects=OWNED_PROJECTS)
    print(f"  OK   directors/dirt: runtime='dirt', owned_projects={OWNED_PROJECTS}")
    print()

    print("Done. Verify with: dcli list-directors")
    return 0


if __name__ == "__main__":
    sys.exit(main())
