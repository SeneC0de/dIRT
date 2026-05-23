#!/usr/bin/env python
"""Rename a Director by migrating its director_id across every child collection.

USE CASE
--------
Sometimes a Director is created under one id (e.g. `dprj`) and later we realise
the work it tracks really belongs under a different id (e.g. `dash`). Renaming
the doc itself in Firestore isn't possible — document IDs are immutable — so
this script does the equivalent: it creates `directors/{to_id}` as a faithful
copy of `directors/{from_id}`, then sweeps every child collection
(`epics`, `features`, `subtasks`, `agents`, `events`, `artifacts`) and rewrites
each record's `director_id` field from `from_id` to `to_id`. Same character,
same personality, same Stories/Tasks — just rebucketed under a new key.

Run:
    python scripts/migrate_director_id.py --from dprj --to dash [--delete-source]

--delete-source
    Optional. After every child record has been moved successfully, delete
    `directors/{from_id}`. Without this flag the source Director doc is left
    alone (useful for dry-run-style first passes, or when you want to keep
    the old doc around as a tombstone).

    The flag only fires AT THE VERY END, after all child updates have
    succeeded. If anything raises mid-sweep, the source Director is preserved
    so you can re-run and finish the job, or roll back.

IDEMPOTENCY
-----------
Re-running the script is safe:

  * If `directors/{to_id}` already exists AND its fields match the source,
    we skip the copy and proceed with the child-record sweep. (This covers
    "the copy succeeded but a child-collection update crashed last time".)
  * If `directors/{to_id}` already exists AND its fields *differ* from the
    source, we refuse — clobbering an unrelated Director would lose data.
  * Each child sweep simply finds rows where `director_id == from_id` and
    sets them to `to_id`. On a clean re-run there will be zero rows to update
    and the script prints `0 records moved per collection` and exits 0.
  * `--delete-source` on a re-run where the source doc is already gone is
    also a no-op (it just notes that the source is already absent).

ROLLBACK
--------
If something goes wrong mid-run, the partial state is recoverable:

  1. Restore the latest nightly dump from `<director-pattern>/backups/` (these
     are produced by `backup_firestore.py`). The dump is a full snapshot of every
     collection — replay it doc-by-doc to undo the partial migration.
  2. Alternatively, if `--delete-source` was NOT passed (the recommended
     first pass), you can re-run the script to finish what crashed: the
     source Director doc is still there, and the child sweeps will pick up
     anything that didn't get moved the first time.
  3. If `--delete-source` WAS passed and the source doc is now gone, you'll
     need the backup. The script intentionally deletes the source LAST so
     this should be a rare path.

The script edits production Firestore — there is no dry-run mode. Test on a
spare director id first if you're unsure.
"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path

# This script lives in scripts/; firestore_db.py is at the repo root.
_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

import firestore_db as fdb  # noqa: E402

# Collections that carry a `director_id` field and must be swept.
# Order doesn't matter for correctness (each sweep is independent) but
# putting `events` near the end keeps the noisy log of what we did flowing
# in a sensible read order when the operator scans the output.
CHILD_COLLECTIONS = ("epics", "features", "subtasks", "agents", "artifacts", "events")


def _list_by_director(collection: str, director_id: str) -> list[dict]:
    """Return every doc in `collection` where director_id == director_id."""
    return fdb._runquery(fdb._build_query(
        collection, where=[("director_id", "==", director_id)]
    ))


def _count_by_director(collection: str, director_id: str) -> int:
    return len(_list_by_director(collection, director_id))


def _print_counts(label: str, director_id: str) -> dict[str, int]:
    """Print per-collection counts for one director_id and return the dict."""
    counts = {c: _count_by_director(c, director_id) for c in CHILD_COLLECTIONS}
    print(f"  {label} (director_id == {director_id!r}):")
    for c in CHILD_COLLECTIONS:
        print(f"    {c:<10} {counts[c]:>5}")
    return counts


def _copy_director_doc(from_id: str, to_id: str) -> dict | None:
    """Copy directors/{from_id} to directors/{to_id}.

    Returns the new (or existing-and-matching) target doc, or None if the source
    is already gone AND the target already exists (the "fully-migrated" idempotent
    case — caller treats this as success).

    Refuses if {to_id} already exists with fields that differ from the source.
    If {to_id} exists and matches, returns the existing doc.
    Otherwise creates {to_id} as a faithful copy with `id` set to the new id.
    """
    src = fdb.get_director(from_id)
    existing = fdb.get_director(to_id)

    if src is None:
        if existing is not None:
            # Source already gone and target exists — migration was completed on
            # a prior run (with --delete-source). The child sweep below will be
            # a no-op. This is the idempotent "already done" path.
            print(f"  directors/{from_id} already absent; directors/{to_id} exists "
                  f"— migration appears already complete.")
            return existing
        raise RuntimeError(
            f"directors/{from_id} does not exist and directors/{to_id} also does "
            f"not exist — nothing to migrate. Check the --from / --to ids."
        )

    if existing is not None:
        # Compare field-by-field, ignoring `id` (which differs by definition)
        # and `updated_at` (touched by upsert_director on every write).
        def _trimmed(d: dict) -> dict:
            return {k: v for k, v in d.items() if k not in ("id", "updated_at")}
        if _trimmed(src) == _trimmed(existing):
            print(f"  directors/{to_id} already exists and matches source — skipping copy.")
            return existing
        raise RuntimeError(
            f"directors/{to_id} already exists and its fields DIFFER from "
            f"directors/{from_id}. Refusing to clobber. Inspect the doc, "
            f"delete it manually if it's truly stale, then re-run."
        )

    # Build the payload: every field on the source EXCEPT `id` (we override that
    # to `to_id` so the field matches the new doc key — the doctrine convention).
    payload = {k: v for k, v in src.items() if k != "id"}
    # If the source had an explicit `id` field, restamp it to the new id.
    if "id" in src:
        payload["id"] = to_id
    fdb.upsert_director(to_id, **payload)
    print(f"  Created directors/{to_id} as a copy of directors/{from_id}.")
    return fdb.get_director(to_id)


def _sweep_collection(collection: str, from_id: str, to_id: str) -> int:
    """Rewrite director_id from from_id to to_id across one collection.

    Returns the number of docs updated. Uses _patch directly (not the domain
    helpers like update_feature) because some collections — events, artifacts —
    don't have a public "update arbitrary fields" helper, and we want one
    minimal-touch write per row: just the `director_id` field, nothing else.
    """
    rows = _list_by_director(collection, from_id)
    n = 0
    for row in rows:
        doc_id = row.get("id")
        if not doc_id:
            # Defensive: every doc has been backfilled with an `id` field by
            # the various add_*() helpers. If we hit one without, log loudly.
            print(f"  WARN: {collection}/<unknown> has no `id` field — skipping. Raw: {row}")
            continue
        fdb._patch(collection, doc_id, {"director_id": to_id}, merge=True)
        n += 1
    print(f"  {collection:<10} moved {n:>5} record(s)")
    return n


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Rename a Director by migrating director_id across all collections."
    )
    ap.add_argument("--from", dest="from_id", required=True,
                    help="Existing director_id to migrate FROM (e.g. dprj).")
    ap.add_argument("--to", dest="to_id", required=True,
                    help="New director_id to migrate TO (e.g. dash).")
    ap.add_argument("--delete-source", action="store_true",
                    help="After all child updates succeed, delete directors/<from_id>.")
    args = ap.parse_args()

    if args.from_id == args.to_id:
        print(f"ERROR: --from and --to are both {args.from_id!r}; nothing to do.")
        return 2

    print(f"Migrating director_id: {args.from_id!r} -> {args.to_id!r}")
    print()

    print("BEFORE:")
    _print_counts("source", args.from_id)
    _print_counts("target", args.to_id)
    print()

    print("Copying directors/ doc...")
    _copy_director_doc(args.from_id, args.to_id)
    print()

    print("Sweeping child collections...")
    total = 0
    for coll in CHILD_COLLECTIONS:
        total += _sweep_collection(coll, args.from_id, args.to_id)
    print(f"  total: {total} record(s) moved")
    print()

    print("AFTER:")
    _print_counts("source", args.from_id)
    _print_counts("target", args.to_id)
    print()

    if args.delete_source:
        existing = fdb.get_director(args.from_id)
        if existing is None:
            print(f"directors/{args.from_id} already absent — nothing to delete.")
        else:
            # Final guard: if any child collection still references from_id,
            # refuse to delete. Catches subtle bugs in the sweep above.
            stragglers = {c: _count_by_director(c, args.from_id) for c in CHILD_COLLECTIONS}
            leftover = {c: n for c, n in stragglers.items() if n > 0}
            if leftover:
                print(f"REFUSING to delete directors/{args.from_id}: "
                      f"child records still reference it: {leftover}. "
                      "Investigate and re-run.")
                return 1
            fdb._delete("directors", args.from_id)
            print(f"Deleted directors/{args.from_id}.")
    else:
        print(f"--delete-source not passed; directors/{args.from_id} left in place.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
