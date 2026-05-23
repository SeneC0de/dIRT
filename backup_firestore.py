"""Daily Firestore backup — dumps every collection to a timestamped JSON file.

Run from the director-pattern repo root (or any folder with firestore_db.py importable):
    python backup_firestore.py
    python backup_firestore.py --out <some-dir>/backups
    python backup_firestore.py --keep-days 30      # prune older snapshots

Default --out is `backups/` next to this script (i.e., the repo root).
Schedule it via Windows Task Scheduler nightly. Output file:
    <out-dir>/firestore-YYYY-MM-DD_HHMMSS.json

This is the "oh god what did I just do to the board" insurance policy.
"""
import argparse, json, sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
import firestore_db as db

COLLECTIONS = ["directors", "features", "subtasks", "agents", "events", "artifacts"]


def _dump_collection(name):
    """Pull every doc in a collection via :runQuery (no filters)."""
    return db._runquery({"from": [{"collectionId": name}]})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(_HERE / "backups"),
                    help="output folder (default: <repo-root>/backups/, i.e. next to this script)")
    ap.add_argument("--keep-days", type=int, default=30,
                    help="prune snapshots older than N days (default 30, 0 = keep all)")
    args = ap.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")
    out_file = out_dir / f"firestore-{ts}.json"

    snapshot = {
        "_generated_at": datetime.now(timezone.utc).isoformat(),
        "_database": db._config().get("database", "(default)"),
        "_project_id": db._config().get("project_id", ""),
    }
    total_docs = 0
    for c in COLLECTIONS:
        docs = _dump_collection(c)
        snapshot[c] = docs
        total_docs += len(docs)
        print(f"  {c}: {len(docs)} docs")

    out_file.write_text(json.dumps(snapshot, indent=2, default=str), encoding="utf-8")
    print(f"Wrote {out_file} ({total_docs} docs total, {out_file.stat().st_size:,} bytes)")

    # Prune
    if args.keep_days > 0:
        cutoff = datetime.now(timezone.utc) - timedelta(days=args.keep_days)
        pruned = 0
        for f in out_dir.glob("firestore-*.json"):
            mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)
            if mtime < cutoff:
                f.unlink()
                pruned += 1
        if pruned:
            print(f"Pruned {pruned} snapshot(s) older than {args.keep_days} days")


if __name__ == "__main__":
    main()
