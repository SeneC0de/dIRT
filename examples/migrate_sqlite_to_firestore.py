r"""HISTORICAL — one-shot migration kept for reference. Will not run as-is.

Originally read SQLite at `C:\Users\randa\Automation\directors\dcad\dcad.db`
(the pre-Firestore desk-box state) and pushed to Firestore with the
reorganized features/sub-tasks model — the four P4.* tasks became subtasks
of a single 'Phase 4 — Repo Transfer' feature.

The Automation/ folder and the SQLite source it referenced are gone (state
lives in Firestore now); the paths below are kept verbatim as a paper trail
of what used to be migrated from where. To re-run a similar migration, fork
this and rewrite SQLITE_PATH to wherever your source DB lives.
"""
import json, sqlite3, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import firestore_db as db

SQLITE_PATH = Path(__file__).resolve().parent / "directors" / "dcad" / "dcad.db"
DIRECTOR_ID = "dcad"

def main():
    if not SQLITE_PATH.exists():
        raise SystemExit(f"Source DB not found: {SQLITE_PATH}")

    c = sqlite3.connect(SQLITE_PATH)
    c.row_factory = sqlite3.Row

    print(f"Reading {SQLITE_PATH} ...")
    # Read the project, agents, tasks
    proj_row = c.execute("SELECT * FROM projects WHERE id=1").fetchone()
    if not proj_row:
        raise SystemExit("No project_id=1 in dcad.db; aborting.")
    proj = dict(proj_row)

    agents = [dict(r) for r in c.execute("SELECT * FROM agents WHERE project_id=1 OR project_id IS NULL")]
    tasks  = [dict(r) for r in c.execute("SELECT * FROM tasks WHERE project_id=1 ORDER BY id")]
    events = [dict(r) for r in c.execute("SELECT * FROM events WHERE project_id=1 ORDER BY id")]
    c.close()

    print(f"  project: {proj['name']}")
    print(f"  agents : {len(agents)}")
    print(f"  tasks  : {len(tasks)}")
    print(f"  events : {len(events)}")

    # 1. Upsert the Director
    print("\nUpserting director ...")
    db.upsert_director(
        DIRECTOR_ID,
        name=proj["name"],
        description=proj.get("description", ""),
        goal=proj.get("goal", ""),
        priority=proj.get("priority", 1),
        status=proj.get("status", "active"),
    )

    # 2. Create the Phase 4 feature
    print("Creating 'Phase 4 — Repo Transfer' feature ...")
    feature_id = db.add_feature(
        DIRECTOR_ID,
        title="Phase 4 — Repo Transfer",
        description="Move dCAD repo from personal GitHub to dapp-controls org as dapp-controls/dCAD. Re-wire origin, CI, branch protections. Verify NETLOAD works from new origin.",
        priority=1,
    )
    print(f"  feature_id: {feature_id}")

    # 3. Migrate the four P4.* tasks as sub-tasks of that feature
    print("Migrating P4.* tasks as sub-tasks ...")
    old_to_new = {}   # sqlite task id -> firestore subtask id
    for t in tasks:
        sid = db.add_subtask(
            feature_id=feature_id,
            title=t["title"],
            description=t.get("description") or "",
            priority=t.get("priority", 1),
            director_id=DIRECTOR_ID,
        )
        old_to_new[t["id"]] = sid
        # Carry forward status / output_ref
        if t["status"] != "open":
            db.update_subtask(sid, status=t["status"])
        if t.get("output_ref"):
            db.update_subtask(sid, output_ref=t["output_ref"])
        print(f"  task {t['id']} ({t['title'][:50]}) -> subtask {sid}")

    # 4. Migrate agents (skip the 0-byte placeholder Director if any)
    print("Migrating agents ...")
    old_to_new_agent = {}
    for a in agents:
        aid = db.register_agent(
            DIRECTOR_ID,
            role=a["role"],
            name=a["name"],
            system_prompt=a.get("system_prompt"),
            parent_id=None,
        )
        old_to_new_agent[a["id"]] = aid
        if a["status"] != "idle":
            db.set_agent_status(aid, a["status"])
        print(f"  agent {a['id']} ({a['name']}) -> {aid}")

    # Re-claim any task that was previously claimed
    for t in tasks:
        if t.get("agent_id"):
            new_sid = old_to_new[t["id"]]
            new_aid = old_to_new_agent.get(t["agent_id"])
            if new_aid:
                db.claim_subtask(new_sid, new_aid)
                print(f"  re-claimed subtask {new_sid} -> agent {new_aid}")

    # 5. Migrate events (top ~100 most recent)
    print("Migrating events ...")
    for e in events[-100:]:
        new_sid = old_to_new.get(e.get("task_id"))
        new_aid = old_to_new_agent.get(e.get("agent_id"))
        db.add_event(
            DIRECTOR_ID,
            type=e["type"],
            agent_id=new_aid,
            feature_id=feature_id if new_sid else None,
            subtask_id=new_sid,
            payload=e.get("payload"),
        )

    db.add_event(DIRECTOR_ID, "migration_note",
                 payload=json.dumps({"note": "Migrated from SQLite dcad.db. P4.1-P4.4 collapsed into Phase 4 feature with 4 sub-tasks."}))

    print(f"\nDone. Feature ID: {feature_id}")
    print("Verify with:")
    print(f"  cd C:\\Users\\randa\\Automation\\directors\\dcad")
    print(f"  python ..\\..\\agent_cli.py status")


if __name__ == "__main__":
    main()
