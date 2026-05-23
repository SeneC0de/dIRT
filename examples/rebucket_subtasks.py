r"""HISTORICAL — one-shot reorg kept for reference. Will not be re-run.

Originally reorganized the dCAD director's 42 sub-tasks (then all under one
Phase-4 feature) into proper features. The "cd C:\Users\randa\Automation\..."
strings in the printed instructions below are vestigial — paths now live at
the director-pattern repo root, but this script is preserved verbatim as a
paper trail of the migration that produced today's board shape.
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import firestore_db as db

DIRECTOR_ID = "dcad"

# Title fragments used to match the 42 existing sub-tasks. Each tuple is
# (matcher, target_feature_key, override_priority_or_None).
# Matcher is a substring (case-insensitive). First match wins.
ROUTES = [
    # Phase 4
    ("P4.1",                        "phase4", 1),
    ("P4.2",                        "phase4", 1),
    ("P4.3",                        "phase4", 1),
    ("P4.4",                        "phase4", 1),
    # Full drawing set v1 (panel-shipping blocker)
    ("Plot full drawing set",       "fullv1", 1),
    ("v1 NETLOAD",                  "fullv1", 1),
    ("v1 second-pass",              "fullv1", 1),
    ("v1 cosmetic backlog",         "fullv1", 3),
    # Phase J renderers
    ("J.0 scaffolding",             "phaseJ", 3),
    ("J.1 WiringRungRenderer",      "phaseJ", 3),
    ("J.2 DCADRENDERSECTION",       "phaseJ", 3),
    ("J.3 ControllerSectionRenderer","phaseJ", 3),
    ("J.4 TabularSectionRenderer",  "phaseJ", 3),
    ("Integration merge",           "phaseJ", 3),
    # v7 schema cutover (A–G)
    ("A: Wire BlockCatalog",        "v7cut",  2),
    ("B: MainForm.SaveJobState",    "v7cut",  2),
    ("C: Remove AdaptV6ToV7",       "v7cut",  2),
    ("D: Remove v7->v6",            "v7cut",  2),
    ("E: Drop SystemMapping",       "v7cut",  2),
    ("F: Extend BlockManifest",     "v7cut",  2),
    ("G: Map view shows compressor","v7cut",  2),
    ("Renderer passes Tag not",     "v7cut",  2),
    # Wave-2 audits
    ("Wave-2",                      "wave2",  2),
    # Renderer & build hygiene
    ("Jesse Pinkman: dynamic block","hygiene",3),
    ("Build-error fix saga",        "hygiene",3),
    ("v6 and v7 in-memory adapters","hygiene",3),
    ("Walter renderer-primitive",   "hygiene",3),
    ("E2E DCADGEN",                 "hygiene",2),
    # Backlog
    ("Storage for 393MB",           "backlog",4),
    ("Decide storage for 393MB",    "backlog",4),
    ("Fix wirePurpose JSON",        "backlog",2),
    ("Lalo audit Findings",         "backlog",3),
    ("Consolidated SectionRoleVocabulary","backlog",3),
]

FEATURES = {
    "phase4":  ("Phase 4 — Repo Transfer",
                "Move dCAD repo to dapp-controls/dCAD. Re-wire origin, CI, NETLOAD-verify.", 1),
    "fullv1":  ("Plot full drawing set v1",
                "Panel-shipping blocker. DCADGEN renders the complete drawing set for both controller configs end-to-end.", 1),
    "phaseJ":  ("Phase J — Section renderers",
                "Section-type renderers (rung wiring, controller, tabular/BOM). Most sub-items marked done; integration merge still pending verification.", 3),
    "v7cut":   ("v7 schema cutover (A–G)",
                "Drop the v6 SystemMapping shim; cutover writes/reads to V7 per-LocTag mappings end-to-end. Sub-tasks A through G.", 2),
    "wave2":   ("Wave-2 audits",
                "Section-by-section reference-DWG audits (B0+G0, Compressor LocTags, L1, M0+M1, P1, R1+S1+S2, MR).", 2),
    "hygiene": ("Renderer & build hygiene",
                "Dynamic block-preload manifest, build-error saga, adapter cleanup, primitive audit, E2E run.", 3),
    "backlog": ("Backlog",
                "Lower-priority items: large DWG storage decision, wirePurpose JSON fix, Lalo audit findings, SectionRoleVocabulary gaps.", 4),
}

# Subtasks whose title indicates the work is already done.
DONE_MARKERS = ["(done)"]


def main():
    print("Loading current state from Firestore ...")
    features = db.list_features(DIRECTOR_ID)
    if not features:
        raise SystemExit("No features found for director 'dcad'. Run migrate_dcad.py first.")
    # There should be one feature today: the wrongly-named "Phase 4 — Repo Transfer".
    old_feature_id = features[0]["id"]
    print(f"  old feature: {features[0]['title']!r}  id={old_feature_id}")

    subs = db.list_subtasks(director_id=DIRECTOR_ID)
    print(f"  sub-tasks  : {len(subs)}")

    # Create the seven new features.
    print("\nCreating new features ...")
    feature_ids = {}
    for key, (title, desc, prio) in FEATURES.items():
        fid = db.add_feature(DIRECTOR_ID, title, desc, prio)
        feature_ids[key] = fid
        print(f"  {key:8} -> {fid}  ({title})")

    # Route every sub-task.
    print("\nRe-bucketing sub-tasks ...")
    routed, unrouted = 0, []
    for s in subs:
        title = (s.get("title") or "").lower()
        matched_key = None
        matched_prio = None
        for matcher, key, prio in ROUTES:
            if matcher.lower() in title:
                matched_key = key
                matched_prio = prio
                break
        if not matched_key:
            unrouted.append(s)
            continue
        updates = {"feature_id": feature_ids[matched_key]}
        if matched_prio is not None:
            updates["priority"] = matched_prio
        # Mark "(done)" items as done
        if any(m in s.get("title","").lower() for m in DONE_MARKERS) and s.get("status") not in ("done","completed"):
            updates["status"] = "done"
        db.update_subtask(s["id"], **updates)
        routed += 1
        print(f"  {s['id'][:8]}  {s['title'][:55]:55}  ->  {matched_key}")

    if unrouted:
        print(f"\n  WARNING: {len(unrouted)} unrouted sub-tasks (left on old feature):")
        for s in unrouted:
            print(f"    {s['id'][:8]}  {s['title']}")
    else:
        print(f"\n  All {routed} sub-tasks re-bucketed.")

    # Delete the now-empty placeholder Phase-4 feature
    # (only delete if it has no sub-tasks pointing at it anymore)
    remaining = [s for s in db.list_subtasks(feature_id=old_feature_id)]
    if not remaining:
        db.client().collection("features").document(old_feature_id).delete()
        print(f"\n  Deleted empty old feature {old_feature_id}.")
    else:
        print(f"\n  Kept old feature {old_feature_id} (still has {len(remaining)} unrouted sub-tasks).")

    db.add_event(DIRECTOR_ID, "rebucket",
                 payload=json.dumps({"note": f"Re-bucketed {routed} sub-tasks into 7 features."}))

    print("\nDone. Verify with:")
    print(f"  cd C:\\Users\\randa\\Automation\\directors\\dcad")
    print(f"  python ..\\..\\agent_cli.py status")


if __name__ == "__main__":
    main()
