"""Firestore-backed agent control CLI.

Run from anywhere inside a project repo containing project.json (CLI walks up to find it),
or pass --director. All output is JSON to stdout.
"""
import argparse, json, sys
from pathlib import Path

# Resolve firestore_db.py — it lives next to this script at the director-pattern repo root.
_here = Path(__file__).resolve().parent
for candidate in [_here, _here.parent, _here.parent.parent]:
    if (candidate / "firestore_db.py").exists():
        sys.path.insert(0, str(candidate))
        break
import firestore_db as db


def _find_project_json():
    """Walk up from cwd looking for project.json. Returns Path or None."""
    p = Path.cwd().resolve()
    while True:
        cand = p / "project.json"
        if cand.exists():
            return cand
        if p == p.parent:
            return None
        p = p.parent


def resolve_director_id(arg_director):
    if arg_director:
        return arg_director
    cfg = _find_project_json()
    if cfg:
        d = json.loads(cfg.read_text(encoding="utf-8"))
        return d.get("director_id") or d.get("name", "").lower()
    raise SystemExit("No --director and no project.json found in cwd or any parent.")


def out(data):
    print(json.dumps(data, indent=2, default=str))


def cmd_info(args):
    did = resolve_director_id(args.director)
    out({"director_id": did, "director": db.get_director(did)})


def cmd_status(args):
    did = resolve_director_id(args.director)
    out(db.status(did))


def cmd_add_feature(args):
    """Create a Story (Firestore collection: features, displayed as 'Story' in the UI)."""
    did = resolve_director_id(args.director)
    author = _current_user()
    fid = db.add_feature(did, args.title, args.description, args.priority,
                         author=author,
                         estimate=getattr(args, "estimate", None))
    db.add_event(did, "feature_created", user=author, feature_id=fid,
                 payload=json.dumps({"title": args.title, "author": author,
                                     "estimate": getattr(args, "estimate", None)}))
    out({"feature_id": fid})


def cmd_add_subtask(args):
    """Create a Task (Firestore collection: subtasks, displayed as 'Task' in the UI)."""
    did = resolve_director_id(args.director)
    author = _current_user()
    sid = db.add_subtask(args.feature_id, args.title, args.description, args.priority,
                         director_id=did, author=author)
    db.add_event(did, "subtask_created", user=author, subtask_id=sid, feature_id=args.feature_id,
                 payload=json.dumps({"title": args.title, "author": author}))
    out({"subtask_id": sid})


def cmd_archive(args):
    """Soft-archive a story or task. Use --unarchive to reverse.

    Determines kind automatically from which --*-id flag is set."""
    did = resolve_director_id(args.director)
    archived = not args.unarchive
    if args.feature_id:
        db.archive_feature(args.feature_id, archived=archived)
        db.add_event(did, "feature_archived" if archived else "feature_unarchived",
                     user=_current_user(), feature_id=args.feature_id,
                     payload=json.dumps({"feature_id": args.feature_id}))
        out({"ok": True, "feature_id": args.feature_id, "archived": archived})
    elif args.subtask_id:
        db.archive_subtask(args.subtask_id, archived=archived)
        db.add_event(did, "subtask_archived" if archived else "subtask_unarchived",
                     user=_current_user(), subtask_id=args.subtask_id,
                     payload=json.dumps({"subtask_id": args.subtask_id}))
        out({"ok": True, "subtask_id": args.subtask_id, "archived": archived})
    else:
        raise SystemExit("must specify one of --feature-id / --subtask-id")


def cmd_register_agent(args):
    did = resolve_director_id(args.director)
    if args.role != "head" and args.head_type:
        raise SystemExit("--head-type is only valid with --role head")
    aid = db.register_agent(did, args.role, args.name, args.system_prompt, args.parent_id,
                            head_type=args.head_type)
    db.add_event(did, "agent_registered", user=_current_user(), agent_id=aid,
                 payload=json.dumps({"role": args.role, "name": args.name,
                                     "head_type": args.head_type}))
    out({"agent_id": aid, "head_type": args.head_type})


def cmd_set_agent_status(args):
    db.set_agent_status(args.agent_id, args.status)
    out({"ok": True})


def cmd_claim(args):
    db.claim_subtask(args.subtask_id, args.agent_id)
    out({"ok": True})


def cmd_start(args):
    db.start_subtask(args.subtask_id)
    out({"ok": True})


def cmd_complete(args):
    did = resolve_director_id(args.director)
    db.complete_subtask(args.subtask_id, args.output_ref)
    db.add_event(did, "subtask_completed", user=_current_user(), subtask_id=args.subtask_id,
                 payload=json.dumps({"output_ref": args.output_ref}))
    out({"ok": True})


def cmd_event(args):
    did = resolve_director_id(args.director)
    eid = db.add_event(did, args.type, user=_current_user(), agent_id=args.agent_id,
                       feature_id=args.feature_id, subtask_id=args.subtask_id,
                       payload=args.payload)
    out({"event_id": eid})


def cmd_list_features(args):
    did = resolve_director_id(args.director)
    out(db.list_features(director_id=did, status=args.status, assignee=args.assignee,
                         label=args.label, due_before=args.due_before,
                         priority_max=args.priority_max,
                         include_archived=getattr(args, "include_archived", False)))


def cmd_list_subtasks(args):
    did = resolve_director_id(args.director)
    out(db.list_subtasks(feature_id=args.feature_id, director_id=did, status=args.status,
                         assignee=args.assignee, label=args.label,
                         due_before=args.due_before, priority_max=args.priority_max,
                         include_archived=getattr(args, "include_archived", False)))


def cmd_list_agents(args):
    did = resolve_director_id(args.director)
    out(db.list_agents(did))


def cmd_recent_events(args):
    did = resolve_director_id(args.director)
    out(db.recent_events(did, limit=args.limit))


def cmd_update_subtask(args):
    fields = {}
    if args.status is not None: fields["status"] = args.status
    if args.note   is not None: fields["note"]   = args.note
    if not fields:
        raise SystemExit("update-subtask needs at least --status or --note")
    db.update_subtask(args.subtask_id, **fields)
    did = resolve_director_id(args.director)
    db.add_event(did, "subtask_updated", user=_current_user(), subtask_id=args.subtask_id,
                 payload=json.dumps(fields))
    out({"ok": True})


def _arr_add(existing, value):
    arr = list(existing or [])
    if value not in arr:
        arr.append(value)
    return arr


def _arr_remove(existing, value):
    return [x for x in (existing or []) if x != value]


def _build_edit_fields(args, doc):
    """Build the dict of fields to patch from edit-* CLI args."""
    fields = {}
    for k in ("title", "description", "status", "assigned_to", "due_date", "start_date", "adr_url", "estimate"):
        v = getattr(args, k.replace("-", "_"), None)
        if v is not None:
            fields[k] = v
    if getattr(args, "adr_number", None) is not None:
        fields["adr_number"] = int(args.adr_number)
    if getattr(args, "priority", None) is not None:
        fields["priority"] = int(args.priority)
    # Array mutations: labels
    cur_labels = doc.get("labels") if doc else None
    new_labels = cur_labels
    if getattr(args, "add_label", None):
        new_labels = _arr_add(new_labels, args.add_label)
    if getattr(args, "remove_label", None):
        new_labels = _arr_remove(new_labels, args.remove_label)
    if new_labels != cur_labels:
        fields["labels"] = new_labels
    # Array mutations: blocked_by
    cur_blk = doc.get("blocked_by") if doc else None
    new_blk = cur_blk
    if getattr(args, "add_blocked_by", None):
        new_blk = _arr_add(new_blk, args.add_blocked_by)
    if getattr(args, "remove_blocked_by", None):
        new_blk = _arr_remove(new_blk, args.remove_blocked_by)
    if new_blk != cur_blk:
        fields["blocked_by"] = new_blk
    return fields


def cmd_edit_feature(args):
    did = resolve_director_id(args.director)
    doc = db.get_feature(args.feature_id)
    if not doc:
        raise SystemExit(f"feature {args.feature_id} not found")
    fields = _build_edit_fields(args, doc)
    if not fields:
        raise SystemExit("nothing to update (no flags set)")
    # If status flips to 'done' and completed_at not set, stamp it
    if fields.get("status") == "done" and not doc.get("completed_at"):
        from datetime import datetime, timezone
        fields["completed_at"] = datetime.now(timezone.utc)
    db.update_feature(args.feature_id, **fields)
    db.add_event(did, "feature_edited", user=_current_user(), feature_id=args.feature_id,
                 payload=json.dumps({k: str(v) for k, v in fields.items()}))
    out({"ok": True, "updated": list(fields.keys())})


def cmd_edit_subtask(args):
    did = resolve_director_id(args.director)
    doc = db.get_subtask(args.subtask_id)
    if not doc:
        raise SystemExit(f"subtask {args.subtask_id} not found")
    fields = _build_edit_fields(args, doc)
    if not fields:
        raise SystemExit("nothing to update (no flags set)")
    db.update_subtask(args.subtask_id, **fields)
    db.add_event(did, "subtask_edited", user=_current_user(), subtask_id=args.subtask_id,
                 payload=json.dumps({k: str(v) for k, v in fields.items()}))
    out({"ok": True, "updated": list(fields.keys())})


def cmd_delete_feature(args):
    did = resolve_director_id(args.director)
    if not args.yes:
        raise SystemExit("destructive op — pass --yes to confirm")
    doc = db.get_feature(args.feature_id)
    if not doc:
        raise SystemExit(f"feature {args.feature_id} not found")
    try:
        result = db.delete_feature(args.feature_id, cascade=args.cascade)
    except ValueError as e:
        raise SystemExit(str(e))
    db.add_event(did, "feature_deleted", user=_current_user(), feature_id=args.feature_id,
                 payload=json.dumps({"title": doc.get("title"), **result}))
    out(result)


def cmd_delete_subtask(args):
    did = resolve_director_id(args.director)
    if not args.yes:
        raise SystemExit("destructive op — pass --yes to confirm")
    doc = db.get_subtask(args.subtask_id)
    if not doc:
        raise SystemExit(f"subtask {args.subtask_id} not found")
    result = db.delete_subtask(args.subtask_id)
    db.add_event(did, "subtask_deleted", user=_current_user(), subtask_id=args.subtask_id,
                 payload=json.dumps({"title": doc.get("title"), **result}))
    out(result)


def cmd_list_directors(args):
    """List every Director doc in Firestore. No filtering by your own director_id — this is the
    discovery query, useful for cleanup and for finding stale Director records."""
    out([{"id": d.get("id"), "name": d.get("name"),
          "director_name": d.get("director_name"),
          "description": d.get("description")}
         for d in db.list_directors()])


def cmd_delete_director(args):
    """Permanently delete a Director document. Refuses if there are any features/subtasks/agents
    under it unless --cascade is also passed (cascade deletes EVERYTHING under that director_id).
    """
    if not args.yes:
        raise SystemExit("destructive op — pass --yes to confirm")
    did = args.director_id
    doc = db.get_director(did)
    if not doc:
        raise SystemExit(f"director {did} not found")
    feats = db.list_features(director_id=did, include_archived=True)
    subs  = db.list_subtasks(director_id=did, include_archived=True)
    agents = db.list_agents(did)
    total_children = len(feats) + len(subs) + len(agents)
    if total_children and not args.cascade:
        raise SystemExit(
            f"director {did} has {len(feats)} story(ies), "
            f"{len(subs)} task(s), {len(agents)} agent(s). Pass --cascade to delete them all."
        )
    deleted = {"features": 0, "subtasks": 0, "agents": 0}
    if args.cascade:
        for f in feats:    db._delete("features", f["id"]);  deleted["features"] += 1
        for s in subs:     db._delete("subtasks", s["id"]);  deleted["subtasks"] += 1
        for a in agents:   db._delete("agents", a["id"]);    deleted["agents"] += 1
    db._delete("directors", did)
    out({"director_deleted": did, **deleted})


def cmd_doctrine(args):
    """Print absolute paths to the canonical director.md and head.md.

    Use this from a Head or Director when you need to Read the canonical doctrine
    and don't want to hardcode paths. JSON output to stay consistent with the rest of the CLI."""
    pattern_home = Path(__file__).resolve().parent
    agents_dir = pattern_home / "agents"
    out({
        "director": str(agents_dir / "director.md"),
        "head": str(agents_dir / "head.md"),
        "pattern_home": str(pattern_home),
    })


def cmd_kickoff(args):
    """Print the canonical kickoff message with resolved doctrine paths.

    Intended use: paste this output (or run this command) as the first message in a
    fresh Claude Code session opened in a project repo containing project.json.
    Claude reads the absolute paths and runs the startup ritual.

    Branding: if the resolved project.json has `"system_root": true`, the kickoff
    text frames the agent as the system itself (e.g. dIRT) rather than as a single
    project's Director. The director-pattern repo is the canonical system root;
    other project repos fall through to the per-project Director persona via
    `dcli info` step 4 of the ritual.
    """
    pattern_home = Path(__file__).resolve().parent
    agents_dir = pattern_home / "agents"
    director_md = agents_dir / "director.md"
    head_md = agents_dir / "head.md"
    cfg_path = _find_project_json()
    repo_hint = str(cfg_path.parent) if cfg_path else "(no project.json found in this folder)"

    system_root = False
    system_name = "dIRT"
    if cfg_path:
        try:
            cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
            system_root = bool(cfg.get("system_root"))
            system_name = cfg.get("system_name") or system_name
        except (OSError, ValueError):
            pass

    if system_root:
        identity_line = (
            f"You are **{system_name}** -- the overarching agentic system, launched from its root at "
            f"`{repo_hint}`. You are not a single project's Director; you are the system that orchestrates "
            f"every Director. When the User asks you to ship cross-cutting work (infra, doctrine, dashboard, "
            f"analytics, the CLI itself), you act as {system_name}. When the User scopes you to a single "
            f"project (per `dcli info`), you adopt that project's Director persona for that scope and revert "
            f"to {system_name} afterward."
        )
        info_step = (
            f"4. `dcli info` - this repo's project identity (used when work is scoped to a single project). "
            f"From the system root, **do not adopt** the per-project Director character for cross-cutting "
            f"work; keep speaking as {system_name}."
        )
    else:
        identity_line = (
            f"You are now the **Director** of the project at `{repo_hint}` (identified by `project.json` "
            f"in that folder). `dcli` is on PATH; use it for every CLI command."
        )
        info_step = "4. `dcli info` - your project identity + character + personality (adopt them for the session)"

    msg = f"""# KICKOFF

{identity_line}

Read these in order, then run the startup ritual described in director.md:

1. `{director_md}` - your full operating manual (everything not in this prompt lives there)
2. `{head_md}` - canonical Head doctrine. Reference this path in every brief; don't restate it.
3. `dcli whoami` - who is the User
{info_step}
5. `dcli status` and `dcli recent-events --limit 10`

Then greet the User by name and run the startup ritual. Don't restate the rules - they're in the docs.
"""
    print(msg)


def cmd_init_director(args):
    """Bootstrap this Director's Firestore record from project.json (idempotent)."""
    cfg_path = _find_project_json()
    if not cfg_path:
        raise SystemExit("project.json not found in cwd or any parent.")
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    did = cfg.get("director_id") or cfg.get("name", "").lower()
    if not did:
        raise SystemExit("director_id missing in project.json")
    # repo_path defaults to the directory containing project.json — the project.json
    # now ships with the code, so its location IS the repo root.
    repo_path = cfg.get("repo_path") or str(cfg_path.parent)
    db.upsert_director(did,
        name=cfg.get("name", did),
        description=cfg.get("description", ""),
        director_name=cfg.get("director_name", did),
        personality=cfg.get("personality", ""),
        head_naming_pool=cfg.get("head_naming_pool", []),
        repo_path=repo_path)
    db.add_event(did, "director_initialized", user=_current_user(), payload=json.dumps({"name": cfg.get("name", did)}))
    out({"ok": True, "director_id": did, "repo_path": repo_path})


def cmd_whoami(args):
    """Print the current User's identity from user.json (walks up from cwd to find it)."""
    import json as _j
    p = Path.cwd().resolve()
    while True:
        cand = p / "user.json"
        if cand.exists():
            cfg = _j.loads(cand.read_text(encoding="utf-8"))
            cfg["_path"] = str(cand)
            out(cfg)
            return
        if p == p.parent: break
        p = p.parent
    # Fallback: check next to firestore_db.py
    here = Path(__file__).resolve().parent
    for c in (here, here.parent, here.parent.parent):
        cand = c / "user.json"
        if cand.exists():
            cfg = _j.loads(cand.read_text(encoding="utf-8"))
            cfg["_path"] = str(cand)
            out(cfg)
            return
    raise SystemExit(
        "user.json not found. Create one with {name, email} either in the current "
        "directory, an ancestor, or next to agent_cli.py at the director-pattern repo root."
    )


def _current_user():
    """Walk up cwd then __file__ tree to find user.json; return the user's name or None."""
    import json as _j
    candidates = [Path.cwd().resolve()]
    here = Path(__file__).resolve().parent
    candidates.extend([here, here.parent, here.parent.parent])
    seen = set()
    for start in candidates:
        p = start
        while p not in seen:
            seen.add(p)
            f = p / "user.json"
            if f.exists():
                try:
                    return _j.loads(f.read_text(encoding="utf-8")).get("name")
                except Exception:
                    return None
            if p == p.parent: break
            p = p.parent
    return None


def cmd_list_blocked(args):
    """Union of: features with status=blocked AND features whose sub-tasks are blocked.

    Bridges the historical gate-sub-task pattern with the new ADR-first feature-level pattern."""
    did = resolve_director_id(args.director)
    out(db.list_blocked_rollup(did))


def cmd_add_artifact(args):
    """Record a file, doc, or URL produced by this work as an artifact. Heads call this at done-lifecycle."""
    did = resolve_director_id(args.director)
    aid = db.add_artifact(did, args.kind, args.path_or_url, description=args.description or "",
                          feature_id=args.feature_id, subtask_id=args.subtask_id, agent_id=args.agent_id)
    db.add_event(did, "artifact_added", user=_current_user(),
                 feature_id=args.feature_id, subtask_id=args.subtask_id, agent_id=args.agent_id,
                 payload=json.dumps({"kind": args.kind, "path_or_url": args.path_or_url,
                                     "description": args.description, "artifact_id": aid}))
    out({"artifact_id": aid})


def cmd_list_stuck(args):
    """Sub-tasks with status=in_progress older than --hours. Catches Heads that died mid-task."""
    did = resolve_director_id(args.director)
    out(db.list_stuck(did, hours=args.hours))


# ----- ADR commands -----
def cmd_add_adr(args):
    """Create a new ADR record (top-level adrs collection)."""
    supersedes = [s.strip() for s in (args.supersedes or "").split(",") if s.strip()]
    aid = db.add_adr(
        number=args.number,
        title=args.title,
        url=args.url,
        status=args.status,
        author=args.author or _current_user(),
        decision_date=args.decision_date,
        description=args.description,
        supersedes=supersedes,
    )
    out({"adr_id": aid, "number": args.number, "title": args.title})


def cmd_reserve_adr(args):
    """Allocate the next ADR number by creating a draft stub. Hand the number to a Drafter."""
    rec = db.reserve_adr_number(
        title=args.title,
        author=args.author or _current_user(),
        description=args.description,
    )
    out({"adr_id": rec["id"], "number": rec["number"], "title": rec["title"], "status": rec["status"]})


def cmd_next_adr_number(args):
    """Print the next ADR number without reserving it."""
    out({"next": db.next_adr_number()})


def cmd_list_adrs(args):
    out(db.list_adrs(status=args.status, limit=args.limit))


def cmd_get_adr(args):
    rec = db.get_adr(args.adr_id)
    if not rec: sys.exit(f"ADR {args.adr_id} not found")
    out(rec)


def cmd_update_adr(args):
    fields = {}
    for k in ("title", "url", "status", "author", "decision_date", "description"):
        v = getattr(args, k, None)
        if v is not None: fields[k] = v
    if args.number is not None: fields["number"] = int(args.number)
    if getattr(args, "body_file", None):
        with open(args.body_file, encoding="utf-8") as f:
            fields["body"] = f.read()
    if not fields: sys.exit("nothing to update — pass at least one --<field>")
    db.update_adr(args.adr_id, **fields)
    out({"adr_id": args.adr_id, "updated": list(fields.keys())})


def cmd_delete_adr(args):
    db.delete_adr(args.adr_id)
    out({"adr_id": args.adr_id, "deleted": True})


def cmd_mark_adr_accepted(args):
    """Flip an ADR's status to 'accepted' by number, then unblock any Stories
    on this Director's board that referenced it (status: blocked -> open)."""
    did = resolve_director_id(args.director)
    n = int(args.adr_number)
    matched = [a for a in db.list_adrs(limit=500) if int(a.get("number", -1)) == n]
    if not matched:
        sys.exit(f"no ADR with number {n}")
    aid = matched[0]["id"]
    db.update_adr(aid, status="accepted")
    unblocked = 0
    for f in db.list_features(director_id=did):
        if f.get("adr_number") == n and f.get("status") == "blocked":
            db.update_feature(f["id"], status="open")
            unblocked += 1
    out({"accepted": n, "adr_id": aid, "stories_unblocked": unblocked})


def _classify_thread(thread_id):
    """Return ('users'|'directors'|'user_director'|'unknown', participants_list)."""
    if not thread_id or not isinstance(thread_id, str):
        return ("unknown", [])
    if ":" not in thread_id:
        return ("unknown", [])
    prefix, _, rest = thread_id.partition(":")
    parts = rest.split("-") if rest else []
    if prefix == "users":
        return ("users", parts)
    if prefix == "directors":
        return ("directors", parts)
    if prefix == "user_director":
        return ("user_director", parts)
    return ("unknown", parts)


def cmd_list_messages(args):
    """List messages in any thread where this Director participates.

    Thread types surfaced by default:
      - directors:<sorted ids>            — director-to-director chats
      - user_director:<sorted [user, did]> — User-to-Director DMs

    The users:<sorted user names> threads are user-to-user; skipped unless
    --include-user-dms is passed (in which case they're still skipped here —
    they don't involve a director_id and never match this filter).
    """
    # Subparser --director (if supplied) wins over the global flag/project.json default.
    did = resolve_director_id(getattr(args, "director_sub", None) or args.director)
    # Pull recent messages and filter client-side. At current scale this is fine,
    # and it keeps us out of firestore_db.py per the scope guardrails on this branch.
    rows = db._runquery(db._build_query(
        "messages",
        order_by=[("ts", "DESCENDING")],
        limit=max(int(args.limit) * 10, 200),  # over-fetch then filter
    )) or []

    matched = []
    for m in rows:
        thread_id = m.get("thread_id") or ""
        ttype, parts = _classify_thread(thread_id)
        if ttype == "directors" and did in parts:
            include = True
        elif ttype == "user_director" and did in parts:
            include = True
        else:
            include = False
        if not include:
            continue
        if args.unread_only:
            read_by = m.get("read_by") or []
            if did in read_by:
                continue
        matched.append({
            "id": m.get("id"),
            "thread_id": thread_id,
            "thread_type": ttype,
            "from": m.get("from"),
            "to": m.get("to"),
            "body": m.get("body"),
            "ts": m.get("ts"),
        })
        if len(matched) >= int(args.limit):
            break

    # Friendly stdout summary BEFORE the JSON dump so humans can scan it.
    print(f"{len(matched)} messages addressed to {did}:", file=sys.stderr)
    for m in matched:
        body = (m.get("body") or "")
        excerpt = body[:60] + ("..." if len(body) > 60 else "")
        print(f"  {m.get('ts')} {m['thread_type']} from {m.get('from')}: {excerpt}",
              file=sys.stderr)

    out(matched)


def cmd_approve_feature(args):
    """Unblock a feature whose ADR has been approved by the User. Sets status->open and emits a feature_approved event.
    """
    did = resolve_director_id(args.director)
    doc = db.get_feature(args.feature_id)
    if not doc:
        raise SystemExit(f"feature {args.feature_id} not found")
    if doc.get("status") != "blocked":
        raise SystemExit(f"feature {args.feature_id} is not blocked (status={doc.get('status')})")
    db.update_feature(args.feature_id, status="open")
    db.add_event(did, "feature_approved", user=_current_user(), feature_id=args.feature_id,
                 payload=json.dumps({"title": doc.get("title"), "adr_url": doc.get("adr_url"), "approved_by": _current_user()}))

    out({"ok": True, "feature_id": args.feature_id})



def main():
    p = argparse.ArgumentParser(description="Firestore-backed agent control CLI")
    p.add_argument("--director", default=None,
                   help="director_id (defaults to project.json in cwd)")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("kickoff", help="Print the canonical Director startup message (with resolved doctrine paths). Run as the first command in a fresh Claude Code session.").set_defaults(func=cmd_kickoff)
    sub.add_parser("doctrine", help="Print absolute paths to the canonical director.md + the three head templates (head_drafter.md, head_coder.md, head_triage.md) as JSON.").set_defaults(func=cmd_doctrine)
    sub.add_parser("init-director", help="Bootstrap this Director's Firestore record from project.json").set_defaults(func=cmd_init_director)
    sub.add_parser("list-directors", help="List every Director in Firestore.").set_defaults(func=cmd_list_directors)

    sp = sub.add_parser("delete-director", help="Permanently delete a Director and (with --cascade) its stories/tasks/agents.")
    sp.add_argument("--director-id", dest="director_id", required=True)
    sp.add_argument("--cascade", action="store_true", help="also delete every story, task, agent under this director_id")
    sp.add_argument("--yes", action="store_true", help="required to confirm destructive op")
    sp.set_defaults(func=cmd_delete_director)
    sub.add_parser("whoami", help="Print current User's identity from user.json").set_defaults(func=cmd_whoami)
    sub.add_parser("list-blocked", help="Features that are blocked OR have a blocked sub-task (gate pattern)").set_defaults(func=cmd_list_blocked)

    sp = sub.add_parser("add-artifact", help="Record a file/doc/URL deliverable produced by a sub-task or feature.")
    sp.add_argument("--kind", required=True, help="file | doc | url | report | image | etc.")
    sp.add_argument("--path-or-url", dest="path_or_url", required=True,
                    help="Local path under the repo (preferred) or http(s) URL.")
    sp.add_argument("--description", default=None, help="One-line plain-English summary.")
    sp.add_argument("--feature-id", dest="feature_id", default=None)
    sp.add_argument("--subtask-id", dest="subtask_id", default=None)
    sp.add_argument("--agent-id", dest="agent_id", default=None)
    sp.set_defaults(func=cmd_add_artifact)

    sp = sub.add_parser("list-stuck", help="Sub-tasks in_progress for too long; suggests Head death.")
    sp.add_argument("--hours", type=float, default=8.0, help="threshold (default 8h)")
    sp.set_defaults(func=cmd_list_stuck)

    # ----- ADR subcommands -----
    sp = sub.add_parser("add-adr", help="Create an ADR record in the top-level adrs collection.")
    sp.add_argument("--number", type=int, required=True, help="ADR number (e.g. 27 for ADR-0027)")
    sp.add_argument("--title",  required=True)
    sp.add_argument("--url",    help="GitHub URL of the ADR markdown")
    sp.add_argument("--status", default="draft", choices=list(db.ADR_STATUSES))
    sp.add_argument("--author")
    sp.add_argument("--decision-date", dest="decision_date", help="ISO date (YYYY-MM-DD) the ADR was accepted")
    sp.add_argument("--description")
    sp.add_argument("--supersedes", help="Comma-separated list of ADR ids this one replaces")
    sp.set_defaults(func=cmd_add_adr)

    sp = sub.add_parser("reserve-adr",
        help="Allocate the next ADR number by creating a draft stub. Returns {adr_id, number}.")
    sp.add_argument("--title", required=True, help="Short slug/title for the ADR (e.g. 'kafka-vs-sqs')")
    sp.add_argument("--author")
    sp.add_argument("--description", help="One-line summary (optional; can be set later via update-adr)")
    sp.set_defaults(func=cmd_reserve_adr)

    sp = sub.add_parser("next-adr-number",
        help="Show the next ADR number without reserving it. Read-only.")
    sp.set_defaults(func=cmd_next_adr_number)

    sp = sub.add_parser("list-adrs", help="List ADR records.")
    sp.add_argument("--status", choices=list(db.ADR_STATUSES))
    sp.add_argument("--limit", type=int, default=200)
    sp.set_defaults(func=cmd_list_adrs)

    sp = sub.add_parser("get-adr", help="Fetch a single ADR by id.")
    sp.add_argument("adr_id")
    sp.set_defaults(func=cmd_get_adr)

    sp = sub.add_parser("update-adr", help="Patch fields on an existing ADR.")
    sp.add_argument("adr_id")
    sp.add_argument("--number", type=int)
    sp.add_argument("--title")
    sp.add_argument("--url")
    sp.add_argument("--status", choices=list(db.ADR_STATUSES))
    sp.add_argument("--author")
    sp.add_argument("--decision-date", dest="decision_date")
    sp.add_argument("--description")
    sp.add_argument("--body-file", dest="body_file",
                    help="Path to a file containing the full ADR Markdown body. "
                         "Stored as the ADR's `body` field — the canonical content lives in Firestore.")
    sp.set_defaults(func=cmd_update_adr)

    sp = sub.add_parser("delete-adr", help="Hard-delete an ADR record.")
    sp.add_argument("adr_id")
    sp.set_defaults(func=cmd_delete_adr)

    sp = sub.add_parser("mark-adr-accepted",
        help="Flip an ADR to 'accepted' by number; also unblock Stories that reference it.")
    sp.add_argument("--adr-number", required=True, dest="adr_number")
    sp.set_defaults(func=cmd_mark_adr_accepted)


    sp = sub.add_parser("list-messages",
        help="Messages addressed to this Director (user_director DMs + director-to-director chats).")
    # Accept --director on the subparser as well as globally — doctrine writes
    # `dcli list-messages --director <my_id>`, so honor that placement.
    sp.add_argument("--director", default=None, dest="director_sub",
                    help="director_id (overrides global --director / project.json).")
    sp.add_argument("--limit", type=int, default=25,
                    help="Max messages to return (default 25).")
    sp.add_argument("--unread-only", action="store_true", dest="unread_only",
                    help="Skip messages whose read_by[] already contains this director_id.")
    sp.add_argument("--include-user-dms", action="store_true", dest="include_user_dms",
                    help="(Reserved) include users:<a>-<b> threads. These don't involve a director_id, so they're skipped either way today; flag is here for future expansion.")
    sp.set_defaults(func=cmd_list_messages)

    sp = sub.add_parser("approve-feature", help="Mark a blocked feature's ADR as approved; unblocks the feature.")
    sp.add_argument("--feature-id", required=True)
    sp.set_defaults(func=cmd_approve_feature)

    sub.add_parser("info").set_defaults(func=cmd_info)
    sub.add_parser("status").set_defaults(func=cmd_status)

    # Story creation — feature collection internally, displayed as "Story". Aliases: add-story.
    for cmd_name in ("add-feature", "add-story"):
        sp = sub.add_parser(cmd_name, help="Create a Story (top-tier card; parent of Tasks).")
        sp.add_argument("--title", required=True)
        sp.add_argument("--description", default="")
        sp.add_argument("--priority", type=int, default=3)
        sp.add_argument("--estimate", default=None,
                        help="T-shirt size: XS / S / M / L / XL. Required by doctrine on creation.")
        sp.set_defaults(func=cmd_add_feature)

    sp = sub.add_parser("archive", help="Soft-archive a Story (feature) or Task (subtask). Reversible.")
    sp.add_argument("--feature-id", dest="feature_id", default=None)
    sp.add_argument("--subtask-id", dest="subtask_id", default=None)
    sp.add_argument("--unarchive", action="store_true", help="restore from archived")
    sp.set_defaults(func=cmd_archive)

    # Task creation — subtask collection internally, displayed as "Task". Aliases: add-task.
    for cmd_name in ("add-subtask", "add-task"):
        sp = sub.add_parser(cmd_name, help="Create a Task (executable unit; assigned to a Head; child of a Story).")
        sp.add_argument("--feature-id", required=True,
                        dest="feature_id", help="Parent Story (feature) ID.")
        sp.add_argument("--title", required=True)
        sp.add_argument("--description", default="")
        sp.add_argument("--priority", type=int, default=3)
        sp.set_defaults(func=cmd_add_subtask)

    sp = sub.add_parser("register-agent")
    sp.add_argument("--role", required=True, choices=["director", "head"])
    sp.add_argument("--name", default=None)
    sp.add_argument("--parent-id", default=None)
    sp.add_argument("--system-prompt", default=None)
    sp.add_argument("--head-type", default=None,
                    help="Optional free-form tag retained for legacy records and analytics. Heads no longer have type-enforced doctrine — the brief defines the work.")
    sp.set_defaults(func=cmd_register_agent)

    sp = sub.add_parser("set-agent-status")
    sp.add_argument("--agent-id", required=True)
    sp.add_argument("--status", required=True)
    sp.set_defaults(func=cmd_set_agent_status)

    sp = sub.add_parser("claim-task")
    sp.add_argument("--subtask-id", required=True)
    sp.add_argument("--agent-id", required=True)
    sp.set_defaults(func=cmd_claim)

    sp = sub.add_parser("start-task")
    sp.add_argument("--subtask-id", required=True)
    sp.set_defaults(func=cmd_start)


    sp = sub.add_parser("update-subtask")
    sp.add_argument("--subtask-id", required=True)
    sp.add_argument("--status", default=None)
    sp.add_argument("--note", default=None)
    sp.set_defaults(func=cmd_update_subtask)

    sp = sub.add_parser("complete-task")
    sp.add_argument("--subtask-id", required=True)
    sp.add_argument("--output-ref", default=None)
    sp.set_defaults(func=cmd_complete)

    sp = sub.add_parser("event")
    sp.add_argument("--type", required=True)
    sp.add_argument("--agent-id", default=None)
    sp.add_argument("--feature-id", default=None)
    sp.add_argument("--subtask-id", default=None)
    sp.add_argument("--payload", default=None)
    sp.set_defaults(func=cmd_event)

    def _add_edit_args(sp):
        sp.add_argument("--title", default=None)
        sp.add_argument("--description", default=None)
        sp.add_argument("--priority", default=None, type=int)
        sp.add_argument("--status", default=None, choices=["open","claimed","in_progress","blocked","done","cancelled"])
        sp.add_argument("--assigned-to", dest="assigned_to", default=None)
        sp.add_argument("--due-date", dest="due_date", default=None, help="ISO date YYYY-MM-DD")
        sp.add_argument("--start-date", dest="start_date", default=None, help="ISO date YYYY-MM-DD")
        sp.add_argument("--add-label", dest="add_label", default=None)
        sp.add_argument("--remove-label", dest="remove_label", default=None)
        sp.add_argument("--add-blocked-by", dest="add_blocked_by", default=None)
        sp.add_argument("--remove-blocked-by", dest="remove_blocked_by", default=None)
        sp.add_argument("--adr-url", dest="adr_url", default=None, help="GitHub URL of the ADR doc backing this feature")
        sp.add_argument("--adr-number", dest="adr_number", default=None, help="ADR number for display (e.g. 8)")
        sp.add_argument("--estimate", default=None,
                        help="T-shirt size: XS / S / M / L / XL")

    sp = sub.add_parser("edit-feature")
    sp.add_argument("--feature-id", required=True)
    _add_edit_args(sp)
    sp.set_defaults(func=cmd_edit_feature)

    sp = sub.add_parser("edit-subtask")
    sp.add_argument("--subtask-id", required=True)
    _add_edit_args(sp)
    sp.set_defaults(func=cmd_edit_subtask)
    sp = sub.add_parser("delete-feature")
    sp.add_argument("--feature-id", required=True)
    sp.add_argument("--cascade", action="store_true", help="also delete every sub-task under this feature")
    sp.add_argument("--yes", action="store_true", help="required to confirm destructive op")
    sp.set_defaults(func=cmd_delete_feature)

    sp = sub.add_parser("delete-subtask")
    sp.add_argument("--subtask-id", required=True)
    sp.add_argument("--yes", action="store_true", help="required to confirm destructive op")
    sp.set_defaults(func=cmd_delete_subtask)


    # list-features (alias: list-stories) — Stories in the UI
    for cmd_name in ("list-features", "list-stories"):
        sp = sub.add_parser(cmd_name, help="List Stories under this Director.")
        sp.add_argument("--status", default=None)
        sp.add_argument("--assignee", default=None)
        sp.add_argument("--label", default=None)
        sp.add_argument("--due-before", default=None, help="ISO date YYYY-MM-DD")
        sp.add_argument("--priority-max", default=None, help="Stories at this priority or higher (lower number = higher priority)")
        sp.add_argument("--include-archived", action="store_true", help="include soft-archived Stories")
        sp.set_defaults(func=cmd_list_features)

    # list-subtasks (alias: list-tasks) — Tasks in the UI
    for cmd_name in ("list-subtasks", "list-tasks"):
        sp = sub.add_parser(cmd_name, help="List Tasks under this Director.")
        sp.add_argument("--feature-id", default=None, dest="feature_id", help="parent Story ID")
        sp.add_argument("--status", default=None)
        sp.add_argument("--assignee", default=None)
        sp.add_argument("--label", default=None)
        sp.add_argument("--due-before", default=None, help="ISO date YYYY-MM-DD")
        sp.add_argument("--priority-max", default=None)
        sp.add_argument("--include-archived", action="store_true", help="include soft-archived Tasks")
        sp.set_defaults(func=cmd_list_subtasks)

    sub.add_parser("list-agents").set_defaults(func=cmd_list_agents)

    sp = sub.add_parser("recent-events")
    sp.add_argument("--limit", type=int, default=25)
    sp.set_defaults(func=cmd_recent_events)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
