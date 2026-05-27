"""Firestore-backed storage for the agent control plane (REST transport).

Why REST: the Cowork sandbox's egress is socks5h+HTTPS only, and gRPC (the
default transport in google-cloud-firestore) can't negotiate over socks5h.
Plain HTTPS via google-auth's AuthorizedSession goes through the proxy fine.

This module uses ONLY the Firestore REST API. The high-level
google.cloud.firestore Client / Document / Query objects are not imported.

Callers: `agent_cli.py` (CLI), `backup_firestore.py` (nightly dumps), and
the per-Director copies of `agent_cli.py` inside each `directors/<name>/`.
"""
from __future__ import annotations
import json, os, urllib.parse
from datetime import datetime, timezone
from pathlib import Path

import google.auth
from google.auth.transport.requests import AuthorizedSession

_HERE = Path(__file__).resolve().parent
_CONFIG_PATH = _HERE / "gcp_config.json"
_SCOPES = ["https://www.googleapis.com/auth/datastore"]

_config_cache: dict | None = None

def _config():
    """Return {project_id, database, credentials_path?}.

    Resolution order:
      1. gcp_config.json next to this file (local desk-box setup).
      2. Environment (CI / cloud): FIRESTORE_PROJECT_ID, FIRESTORE_DATABASE,
         FIREBASE_SA_FILE (or GOOGLE_APPLICATION_CREDENTIALS).
    """
    global _config_cache
    if _config_cache is not None:
        return _config_cache
    if _CONFIG_PATH.exists():
        _config_cache = json.loads(_CONFIG_PATH.read_text())
        return _config_cache
    pid = os.environ.get("FIRESTORE_PROJECT_ID")
    if not pid:
        raise RuntimeError(
            "No gcp_config.json next to firestore_db.py and FIRESTORE_PROJECT_ID is unset. "
            "Set FIRESTORE_PROJECT_ID (+ optional FIRESTORE_DATABASE) and one of "
            "GOOGLE_APPLICATION_CREDENTIALS / FIREBASE_SA_FILE."
        )
    _config_cache = {
        "project_id":       pid,
        "database":         os.environ.get("FIRESTORE_DATABASE", "(default)"),
        "credentials_path": os.environ.get("FIREBASE_SA_FILE")
                             or os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"),
    }
    return _config_cache

_session: AuthorizedSession | None = None
def _sess() -> AuthorizedSession:
    global _session
    if _session is None:
        cfg = _config()
        if cfg.get("credentials_path"):
            os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", cfg["credentials_path"])
        creds, _ = google.auth.default(scopes=_SCOPES)
        _session = AuthorizedSession(creds)
    return _session

def _base_url() -> str:
    cfg = _config()
    db_name = cfg.get("database", "(default)")
    return (f"https://firestore.googleapis.com/v1/projects/{cfg['project_id']}"
            f"/databases/{db_name}/documents")

def now() -> datetime:
    return datetime.now(timezone.utc)

# ---------- Value (de)serialization (Firestore REST typed wrappers) ----------

def _to_v(v):
    if v is None: return {"nullValue": None}
    if isinstance(v, bool): return {"booleanValue": v}
    if isinstance(v, int): return {"integerValue": str(v)}
    if isinstance(v, float): return {"doubleValue": v}
    if isinstance(v, str): return {"stringValue": v}
    if isinstance(v, datetime):
        # Firestore expects RFC3339 / ISO8601 with Z suffix
        iso = v.astimezone(timezone.utc).isoformat()
        if iso.endswith("+00:00"): iso = iso[:-6] + "Z"
        return {"timestampValue": iso}
    if isinstance(v, list):
        return {"arrayValue": {"values": [_to_v(x) for x in v]}}
    if isinstance(v, dict):
        return {"mapValue": {"fields": {k: _to_v(x) for k, x in v.items()}}}
    raise TypeError(f"Cannot serialize {type(v).__name__}")

def _from_v(v):
    if "nullValue"      in v: return None
    if "booleanValue"   in v: return v["booleanValue"]
    if "integerValue"   in v: return int(v["integerValue"])
    if "doubleValue"    in v: return v["doubleValue"]
    if "stringValue"    in v: return v["stringValue"]
    if "timestampValue" in v: return v["timestampValue"]  # leave as ISO string for simplicity
    if "arrayValue"     in v: return [_from_v(x) for x in v["arrayValue"].get("values", [])]
    if "mapValue"       in v: return {k: _from_v(x) for k, x in v["mapValue"].get("fields", {}).items()}
    return None

def _doc_to_dict(doc):
    """Firestore REST document -> our dict, with `id` set from the document name."""
    if not doc or "fields" not in doc:
        return None
    out = {k: _from_v(x) for k, x in doc["fields"].items()}
    name = doc.get("name", "")
    if name:
        out["id"] = name.split("/")[-1]
    return out

# ---------- Low-level helpers ----------

def _req(method, path, **kwargs):
    url = _base_url() + path
    r = _sess().request(method, url, **kwargs)
    if not r.ok:
        try:
            err = r.json()
        except Exception:
            err = r.text
        raise RuntimeError(f"Firestore {method} {path} failed [{r.status_code}]: {err}")
    return r.json() if r.text else {}

def _runquery(structured_query, transaction=None):
    """:runQuery endpoint — sits at the database root, not under /documents."""
    cfg = _config()
    db_name = cfg.get("database", "(default)")
    url = (f"https://firestore.googleapis.com/v1/projects/{cfg['project_id']}"
           f"/databases/{db_name}/documents:runQuery")
    body = {"structuredQuery": structured_query}
    if transaction:
        body["transaction"] = transaction
    r = _sess().post(url, json=body)
    if not r.ok:
        try: err = r.json()
        except Exception: err = r.text
        raise RuntimeError(f"runQuery failed [{r.status_code}]: {err}")
    out = []
    for item in r.json():
        if "document" in item:
            out.append(_doc_to_dict(item["document"]))
    return out


def _db_root_url() -> str:
    """Firestore database root (not /documents) — used for transaction endpoints."""
    cfg = _config()
    db_name = cfg.get("database", "(default)")
    return (f"https://firestore.googleapis.com/v1/projects/{cfg['project_id']}"
            f"/databases/{db_name}")


def _begin_transaction(read_write=True):
    """Open a Firestore transaction. Returns the transaction token (bytes-as-base64 string)."""
    url = _db_root_url() + "/documents:beginTransaction"
    body = {"options": {"readWrite": {}} if read_write else {"readOnly": {}}}
    r = _sess().post(url, json=body)
    if not r.ok:
        try: err = r.json()
        except Exception: err = r.text
        raise RuntimeError(f"beginTransaction failed [{r.status_code}]: {err}")
    return r.json()["transaction"]


def _commit(writes, transaction):
    """Commit a list of Firestore Write objects under `transaction`.

    `writes` is a list of Firestore REST Write objects:
      - {"update": {<document resource>}, "updateMask": {...}} for creates/patches
      - {"delete": "<doc_name>"} for deletes
    Returns the commit response dict.
    """
    url = _db_root_url() + "/documents:commit"
    r = _sess().post(url, json={"writes": writes, "transaction": transaction})
    if not r.ok:
        try: err = r.json()
        except Exception: err = r.text
        raise RuntimeError(f"commit failed [{r.status_code}]: {err}")
    return r.json()


def _doc_name(collection, doc_id=None):
    """Build a Firestore document resource name."""
    cfg = _config()
    db_name = cfg.get("database", "(default)")
    base = (f"projects/{cfg['project_id']}/databases/{db_name}/documents"
            f"/{collection}")
    return f"{base}/{doc_id}" if doc_id else base


def _commit_batch(writes):
    """Commit multiple writes atomically (no pre-existing transaction).

    Uses a single :commit call without beginTransaction — Firestore applies
    the writes in order with at-most-once semantics.
    """
    url = _db_root_url() + "/documents:commit"
    r = _sess().post(url, json={"writes": writes})
    if not r.ok:
        try: err = r.json()
        except Exception: err = r.text
        raise RuntimeError(f"commit_batch failed [{r.status_code}]: {err}")
    return r.json()

_OP_MAP = {"==":"EQUAL", ">":"GREATER_THAN", "<":"LESS_THAN",
           ">=":"GREATER_THAN_OR_EQUAL", "<=":"LESS_THAN_OR_EQUAL", "!=":"NOT_EQUAL",
           "array_contains": "ARRAY_CONTAINS"}

def _build_query(collection, where=None, order_by=None, limit=None):
    sq = {"from": [{"collectionId": collection}]}
    if where:
        conds = []
        for field, op, val in where:
            conds.append({"fieldFilter": {
                "field": {"fieldPath": field},
                "op": _OP_MAP[op],
                "value": _to_v(val),
            }})
        sq["where"] = conds[0] if len(conds) == 1 else {
            "compositeFilter": {"op": "AND", "filters": conds}
        }
    if order_by:
        if isinstance(order_by, str):
            order_by = [(order_by, "ASCENDING")]
        sq["orderBy"] = [{"field": {"fieldPath": f}, "direction": d} for f, d in order_by]
    if limit:
        sq["limit"] = int(limit)
    return sq

def _create(collection, data):
    """Create with auto-generated doc id. Returns the new id."""
    r = _req("POST", f"/{collection}", json={"fields": {k: _to_v(v) for k, v in data.items()}})
    return r["name"].split("/")[-1]

def _patch(collection, doc_id, data, merge=True):
    """Set or merge a doc."""
    path = f"/{collection}/{doc_id}"
    if merge:
        masks = "&".join(f"updateMask.fieldPaths={urllib.parse.quote(k)}" for k in data.keys())
        path = f"{path}?{masks}"
    return _req("PATCH", path, json={"fields": {k: _to_v(v) for k, v in data.items()}})

def _get(collection, doc_id):
    try:
        return _doc_to_dict(_req("GET", f"/{collection}/{doc_id}"))
    except RuntimeError as e:
        if "404" in str(e):
            return None
        raise

def _delete(collection, doc_id):
    return _req("DELETE", f"/{collection}/{doc_id}")

# ---------- High-level domain ops (signatures match the previous SDK version) ----------

# ----- Directors -----

def upsert_director(project, **fields):
    fields.setdefault("id", project)
    fields["updated_at"] = now()
    _patch("directors", project, fields, merge=True)
    return project

def get_director(project):
    return _get("directors", project)

# ----- Features (displayed as "Story" in the UI) -----

FEATURE_STATUSES = ("open", "claimed", "in_progress", "blocked", "needs-testing", "done", "cancelled")

def add_feature(project, title, description="", priority=3,
                author=None, estimate=None, test_plan=None):
    data = {"project": project, "title": title, "description": description,
            "priority": priority, "status": "open", "archived": False,
            "author": author, "estimate": estimate, "test_plan": test_plan,
            "created_at": now(), "updated_at": now()}
    fid = _create("features", data)
    # backfill `id` for consumers reading via _get
    _patch("features", fid, {"id": fid}, merge=True)
    _touch_meta(project, by=author, kind="feature_created", doc_id=fid)
    return fid

def list_features(project=None, status=None, assignee=None, label=None,
                  due_before=None, priority_max=None, include_archived=False):
    where = []
    if project:  where.append(("project", "==", project))
    if status:       where.append(("status", "==", status))
    if assignee:     where.append(("assigned_to", "==", assignee))
    if label:        where.append(("labels", "array_contains", label))
    if due_before:   where.append(("due_date", "<=", due_before))
    if priority_max: where.append(("priority", "<=", int(priority_max)))
    feats = _runquery(_build_query("features", where=where or None))
    if not include_archived:
        feats = [f for f in feats if not f.get("archived")]
    return feats

def update_feature(feature_id, **fields):
    if "status" in fields and fields["status"] not in FEATURE_STATUSES:
        raise ValueError(f"status must be one of {FEATURE_STATUSES}")
    fields["updated_at"] = now()
    _patch("features", feature_id, fields, merge=True)
    feat = _get("features", feature_id)
    if feat:
        kind = f"feature_{fields['status']}" if "status" in fields else "feature_updated"
        _touch_meta(feat.get("project"), by=fields.get("author"), kind=kind, doc_id=feature_id)

def delete_feature(feature_id, cascade=False):
    """Delete a feature. If cascade, also delete every sub-task that references it.
    Returns dict with counts of what was removed."""
    children = list_subtasks(feature_id=feature_id)
    if children and not cascade:
        raise ValueError(f"feature {feature_id} has {len(children)} sub-task(s); pass cascade=True to remove them too")
    removed_subs = 0
    for s in children:
        _delete("subtasks", s["id"])
        removed_subs += 1
    _delete("features", feature_id)
    return {"feature_deleted": feature_id, "subtasks_deleted": removed_subs}


def get_feature(feature_id):
    return _get("features", feature_id)


def get_subtask(subtask_id):
    return _get("subtasks", subtask_id)


# ----- Subtasks -----

SUBTASK_STATUSES = ("proposed", "open", "claimed", "in_progress", "blocked", "done", "cancelled")

def add_subtask(feature_id=None, title="", description="", priority=3, project=None,
                author=None, adr_id=None, status="open"):
    """Create a subtask.

    `feature_id` and `adr_id` are both optional so that proposed subtasks
    created during ADR drafting can carry adr_id without a feature yet.
    `status` defaults to 'open'; use 'proposed' for subtasks created before
    the ADR is approved (feature_id will be None at that point).

    If `project` is not given and `feature_id` is set, it is resolved from
    the parent feature. If both are None, raises ValueError.
    """
    if status not in SUBTASK_STATUSES:
        raise ValueError(f"status must be one of {SUBTASK_STATUSES}, got {status!r}")
    if project is None:
        if feature_id:
            feat = _get("features", feature_id)
            if not feat: raise ValueError(f"feature {feature_id} not found")
            project = feat["project"]
        elif adr_id:
            adr = _get("adrs", adr_id)
            if not adr: raise ValueError(f"adr {adr_id} not found")
            project = adr.get("project")
        if project is None:
            raise ValueError("project could not be resolved; pass project= explicitly")
    data = {"feature_id": feature_id, "adr_id": adr_id, "project": project,
            "title": title, "description": description, "priority": priority,
            "status": status, "agent_id": None, "author": author, "archived": False,
            "created_at": now(), "updated_at": now(),
            "started_at": None, "completed_at": None, "output_ref": None}
    sid = _create("subtasks", data)
    _patch("subtasks", sid, {"id": sid}, merge=True)
    return sid

def list_subtasks(feature_id=None, project=None, status=None,
                  assignee=None, label=None, due_before=None, priority_max=None,
                  include_archived=False, adr_id=None):
    where = []
    if feature_id:   where.append(("feature_id", "==", feature_id))
    if adr_id:       where.append(("adr_id", "==", adr_id))
    if project:      where.append(("project", "==", project))
    if status:       where.append(("status", "==", status))
    if assignee:     where.append(("assigned_to", "==", assignee))
    if label:        where.append(("labels", "array_contains", label))
    if due_before:   where.append(("due_date", "<=", due_before))
    if priority_max: where.append(("priority", "<=", int(priority_max)))
    subs = _runquery(_build_query("subtasks", where=where or None))
    if not include_archived:
        subs = [s for s in subs if not s.get("archived")]
    return subs

def claim_subtask(subtask_id, agent_id):
    _patch("subtasks", subtask_id, {"agent_id": agent_id, "status": "claimed", "updated_at": now()})

def start_subtask(subtask_id):
    _patch("subtasks", subtask_id, {"status": "in_progress", "started_at": now()})

def update_subtask(subtask_id, **fields):
    fields["updated_at"] = now()
    _patch("subtasks", subtask_id, fields, merge=True)
    sub = _get("subtasks", subtask_id)
    if sub:
        kind = f"task_{fields['status']}" if "status" in fields else "task_updated"
        fid = sub.get("feature_id")
        doc_id = fid if fid else sub.get("project")
        _touch_meta(sub.get("project"), by=fields.get("author"), kind=kind, doc_id=doc_id)

def delete_subtask(subtask_id):
    _delete("subtasks", subtask_id)
    return {"subtask_deleted": subtask_id}


def complete_subtask(subtask_id, output_ref=None):
    _patch("subtasks", subtask_id,
           {"status": "done", "completed_at": now(), "updated_at": now(), "output_ref": output_ref})
    sub = _get("subtasks", subtask_id)
    if sub:
        fid = sub.get("feature_id")
        doc_id = fid if fid else sub.get("project")
        _touch_meta(sub.get("project"), by=None, kind="task_done", doc_id=doc_id)

# ----- Agents -----

def register_agent(project, role, name=None, system_prompt=None, parent_id=None, head_type=None):
    data = {"project": project, "role": role, "name": name,
            "system_prompt": system_prompt, "parent_id": parent_id,
            "head_type": head_type,
            "status": "idle", "created_at": now()}
    aid = _create("agents", data)
    _patch("agents", aid, {"id": aid}, merge=True)
    return aid

def set_agent_status(agent_id, status):
    _patch("agents", agent_id, {"status": status, "updated_at": now()})

def list_agents(project):
    return _runquery(_build_query("agents", where=[("project", "==", project)]))

# ----- Events -----

def add_event(project, type, agent_id=None, feature_id=None, subtask_id=None, payload=None, user=None):
    data = {"project": project, "type": type, "agent_id": agent_id,
            "feature_id": feature_id, "subtask_id": subtask_id,
            "payload": payload, "user": user, "ts": now()}
    eid = _create("events", data)
    _patch("events", eid, {"id": eid}, merge=True)
    return eid

def recent_events(project, limit=25):
    return _runquery(_build_query("events",
                                  where=[("project", "==", project)],
                                  order_by=[("ts", "DESCENDING")],
                                  limit=limit))

# ----- Artifacts -----

def add_artifact(project, kind, path_or_url, description="",
                 feature_id=None, subtask_id=None, agent_id=None):
    data = {"project": project, "kind": kind, "path_or_url": path_or_url,
            "description": description, "feature_id": feature_id,
            "subtask_id": subtask_id, "agent_id": agent_id, "created_at": now()}
    aid = _create("artifacts", data)
    _patch("artifacts", aid, {"id": aid}, merge=True)
    return aid

# ----- Rollup -----

def status(project, include_archived=False):
    features = list_features(project, include_archived=include_archived)
    subtasks = list_subtasks(project=project, include_archived=include_archived)
    agents   = list_agents(project)
    events   = recent_events(project, limit=10)
    by_feat = {}
    for s in subtasks:
        by_feat.setdefault(s.get("feature_id") or "_orphan", []).append(s)
    return {
        "director": get_director(project),
        "features": features,
        "subtasks_by_feature": by_feat,
        "agents": agents,
        "recent_events": events,
    }


# ----- Archive helpers (soft hide; cards stay queryable with include_archived=True) -----

def archive_feature(feature_id, archived=True):
    _patch("features", feature_id, {"archived": archived, "updated_at": now()}, merge=True)

def archive_subtask(subtask_id, archived=True):
    _patch("subtasks", subtask_id, {"archived": archived, "updated_at": now()}, merge=True)


# ----- blocked-by hierarchical label rendering -----

def _resolve_blocker_label(blocker_id, features_by_id=None, subtasks_by_id=None):
    """Return a human-readable 'Story > Task' label for a blocker ID.
    Caller can pass pre-fetched lookup dicts to avoid extra round-trips."""
    # Try subtask first (most specific)
    sub = (subtasks_by_id or {}).get(blocker_id)
    if sub is None:
        sub = _get("subtasks", blocker_id)
    if sub:
        feat = (features_by_id or {}).get(sub.get("feature_id")) or (_get("features", sub.get("feature_id")) if sub.get("feature_id") else None)
        parts = []
        if feat: parts.append(feat.get("title", "?"))
        parts.append(sub.get("title", "?"))
        return " > ".join(parts), "subtask"
    # Try feature
    feat = (features_by_id or {}).get(blocker_id) or _get("features", blocker_id)
    if feat:
        return feat.get("title", "?"), "feature"
    return blocker_id, "unknown"

# ----- Shim for old `client()` callers (rebucket_dcad.py uses it for deletes) -----

class _CollectionShim:
    def __init__(self, name): self._name = name
    def document(self, doc_id): return _DocShim(self._name, doc_id)

class _DocShim:
    def __init__(self, coll, doc_id):
        self._coll, self._id = coll, doc_id
    def delete(self): return _delete(self._coll, self._id)
    def get(self):
        d = _get(self._coll, self._id)
        return _DocSnapshot(d)
    def set(self, fields, merge=False):
        return _patch(self._coll, self._id, fields, merge=merge)

class _DocSnapshot:
    def __init__(self, data):
        self._data = data
        self.exists = data is not None
    def to_dict(self): return self._data

class _ClientShim:
    def collection(self, name): return _CollectionShim(name)

def client():
    """Back-compat shim. Returns an object with .collection() that supports the
    minimal surface rebucket_dcad.py and migrate_dcad.py used."""
    return _ClientShim()

def list_stuck(project, hours=8):
    """Return sub-tasks that have been in_progress longer than `hours` — Heads that may have died mid-task.

    A Head is considered "stuck" if status==in_progress and started_at is older than the threshold.
    The Director's startup ritual queries this so silent Head crashes don't get lost.
    """
    from datetime import timedelta
    threshold = now() - timedelta(hours=float(hours))
    in_progress = list_subtasks(project=project, status="in_progress")
    threshold_iso = threshold.isoformat().replace("+00:00", "Z")
    stuck = []
    for s in in_progress:
        started = s.get("started_at")
        if not started:
            continue  # No start time — odd, but skip
        # started_at is an ISO string after _from_v
        if isinstance(started, str) and started < threshold_iso:
            # Compute age in hours for the UI
            try:
                from datetime import datetime as _dt
                started_dt = _dt.fromisoformat(started.replace("Z", "+00:00"))
                age_h = (now() - started_dt).total_seconds() / 3600.0
                s["_stuck_hours"] = round(age_h, 1)
            except Exception:
                s["_stuck_hours"] = None
            stuck.append(s)
    stuck.sort(key=lambda x: x.get("started_at") or "")
    return stuck


def add_message(thread_id, thread_type, from_name, to_name, body):
    """Append a message to a chat-dock thread. Used by the cloud agent to post replies."""
    data = {
        "thread_id":   thread_id,
        "thread_type": thread_type,
        "from":        from_name,
        "to":          to_name,
        "body":        body,
        "ts":          now(),
        "read_by":     [from_name],
    }
    mid = _create("messages", data)
    _patch("messages", mid, {"id": mid}, merge=True)
    return mid


# ----- ADRs (Architecture Decision Records) -----
# Top-level collection; one document per ADR. Features reference an ADR via
# `adr_id` (and keep adr_url/adr_number denormalized so existing UI keeps working).
# Status vocabulary follows the ADR convention: draft, proposed, accepted,
# rejected, superseded. Caller is responsible for keeping `supersedes` /
# `superseded_by` symmetric — there's no DB-level enforcement.

ADR_STATUSES = ("draft", "proposed", "accepted", "rejected", "superseded")

def add_adr(number, title, url=None, status="draft", author=None,
            decision_date=None, description=None, supersedes=None,
            project=None):
    """Create an ADR. `number` is required and must be unique per project; the caller
    decides the numbering scheme (e.g. 27 for ADR-0027). `supersedes` is a list of
    ADR ids this one replaces; this function also patches the older docs' `superseded_by`.
    Returns the new ADR id."""
    if status not in ADR_STATUSES:
        raise ValueError(f"status must be one of {ADR_STATUSES}, got {status!r}")
    data = {
        "number": int(number),
        "title": title,
        "url": url,
        "status": status,
        "author": author,
        "decision_date": decision_date,   # ISO date string or None
        "description": description,
        "supersedes": list(supersedes or []),
        "superseded_by": None,
        "project": project,
        "created_at": now(),
        "updated_at": now(),
    }
    aid = _create("adrs", data)
    _patch("adrs", aid, {"id": aid}, merge=True)
    # Mirror the supersedes -> superseded_by relationship on the older docs.
    for old_id in (supersedes or []):
        try:
            _patch("adrs", old_id, {"superseded_by": aid, "status": "superseded",
                                    "updated_at": now()}, merge=True)
        except Exception:
            pass  # tolerate stale ids; don't fail the create
    return aid

def get_adr(adr_id):
    return _get("adrs", adr_id)

def get_adr_by_number(n):
    """Fetch a single ADR by its integer `number` field."""
    results = _runquery(_build_query("adrs", where=[("number", "==", int(n))], limit=1))
    return results[0] if results else None

def list_adrs(status=None, limit=200):
    where = []
    if status: where.append(("status", "==", status))
    return _runquery(_build_query("adrs", where=where or None,
                                  order_by=[("number", "DESCENDING")],
                                  limit=limit))

def update_adr(adr_id, **fields):
    if "status" in fields and fields["status"] not in ADR_STATUSES:
        raise ValueError(f"status must be one of {ADR_STATUSES}")
    fields["updated_at"] = now()
    _patch("adrs", adr_id, fields, merge=True)
    if "status" in fields:
        adr = _get("adrs", adr_id)
        if adr and adr.get("project"):
            kind = f"adr_{fields['status']}"
            _touch_meta(adr["project"], by=fields.get("accepted_by"), kind=kind)
    return adr_id

def delete_adr(adr_id):
    return _delete("adrs", adr_id)

def next_adr_number():
    """Return the next unallocated ADR number = max(existing.number) + 1, or 1 if none exist.
    Read-only; does not reserve. For atomic allocation use `reserve_adr_number`."""
    top = _runquery(_build_query("adrs",
                                 order_by=[("number", "DESCENDING")],
                                 limit=1))
    if not top:
        return 1
    return int(top[0].get("number") or 0) + 1

def reserve_adr_number(title, author=None, description=None, project=None):
    """Atomically allocate the next ADR number using a Firestore read-write transaction.

    Flow:
      1. beginTransaction (readWrite)
      2. runQuery max(number) inside the transaction
      3. commit with a single document write: the new stub ADR doc

    Collision safety: the transaction's read set includes the query snapshot;
    if another writer inserts a doc concurrently, Firestore aborts and retries
    (up to `_MAX_RESERVE_RETRIES` times).

    Returns the newly created stub ADR doc (same shape as get_adr()).
    """
    _MAX_RESERVE_RETRIES = 5
    for attempt in range(_MAX_RESERVE_RETRIES):
        txn = _begin_transaction(read_write=True)
        # Read the highest-numbered ADR inside the transaction
        top = _runquery(
            _build_query("adrs", order_by=[("number", "DESCENDING")], limit=1),
            transaction=txn,
        )
        n = (int(top[0].get("number") or 0) + 1) if top else 1

        # Build the stub doc fields
        ts = now()
        stub_fields = {
            "number":       _to_v(n),
            "title":        _to_v(title),
            "url":          _to_v(None),
            "status":       _to_v("draft"),
            "author":       _to_v(author),
            "decision_date": _to_v(None),
            "description":  _to_v(description),
            "supersedes":   _to_v([]),
            "superseded_by": _to_v(None),
            "project":      _to_v(project),
            "body":         _to_v(None),
            "created_at":   _to_v(ts),
            "updated_at":   _to_v(ts),
        }
        # Firestore auto-generates the doc ID when we POST to the collection.
        # In a commit Write we must supply a doc name, so we generate one:
        import uuid as _uuid
        new_id = _uuid.uuid4().hex
        doc_name = _doc_name("adrs", new_id)
        write = {
            "update": {"name": doc_name, "fields": stub_fields},
        }
        try:
            _commit([write], transaction=txn)
            # Backfill `id` field so _get / list callers see it
            _patch("adrs", new_id, {"id": new_id}, merge=True)
            return get_adr(new_id)
        except RuntimeError as exc:
            if attempt < _MAX_RESERVE_RETRIES - 1 and "ABORTED" in str(exc):
                continue  # transaction conflict — retry
            raise
    raise RuntimeError("reserve_adr_number: exceeded retry limit on transaction conflicts")


# ----- projects_meta (Operations surface — software rows) -----

PROJECTS_META_STAGES = (
    "discovery", "adr-drafting", "adr-review", "in-flight",
    "testing", "ready-to-ship", "closed",
)

def get_projects_meta(doc_id):
    """Return a projects_meta doc by its Firestore doc ID, or None if it doesn't exist."""
    return _get("projects_meta", doc_id)

def upsert_projects_meta(doc_id, **fields):
    """Create or overwrite a projects_meta document with the given fields."""
    fields["updated_at"] = now()
    _patch("projects_meta", doc_id, fields, merge=True)
    return doc_id

def update_projects_meta_if_exists(doc_id, **fields):
    """Patch a projects_meta doc only if it already exists. Returns True if patched, False if not found."""
    existing = get_projects_meta(doc_id)
    if existing is None:
        return False
    fields["updated_at"] = now()
    _patch("projects_meta", doc_id, fields, merge=True)
    return True


def _touch_meta(project, by, kind, doc_id=None):
    """Best-effort update of projects_meta to record the last action.

    `doc_id` — the projects_meta document ID (defaults to `project`).
    Only patches the four last_action_* fields; does not create the row if
    it doesn't exist (avoids spurious rows for non-Operations features).

    Called from every state-transition function so the Operations overlay
    always reflects the latest board activity.
    """
    if not project:
        return
    ts = now()
    target = doc_id or project
    try:
        update_projects_meta_if_exists(target, **{
            "last_action_at":   ts,
            "last_action_by":   by or "agent",
            "last_action_kind": kind,
            "updated_at":       ts,
        })
    except Exception:
        pass  # Never fail a primary write because of a meta update

def find_projects_meta_by_source_id(source_id):
    """Return the first projects_meta doc whose source_id matches, or None."""
    results = _runquery(_build_query("projects_meta", where=[("source_id", "==", source_id)], limit=1))
    return results[0] if results else None


def list_blocked_rollup(project):
    """Return every feature that's blocked OR has at least one blocked sub-task.

    Bridges the historical "gate sub-task" pattern (feature stays open, one
    sub-task is status=blocked) with the new ADR-first pattern (feature itself
    is status=blocked pending review).

    Returns: [{ "feature": <feature doc>, "blocked_subtasks": [<subtask doc>, ...],
                "reason": "feature_blocked" | "gate_subtask" }, ...]
    """
    feats = list_features(project)
    subs_blocked = list_subtasks(project=project, status="blocked")
    by_feat = {}
    for s in subs_blocked:
        by_feat.setdefault(s.get("feature_id"), []).append(s)
    out = []
    for f in feats:
        fid = f.get("id")
        gates = by_feat.get(fid, [])
        is_blocked = f.get("status") == "blocked"
        if is_blocked or gates:
            out.append({
                "feature": f,
                "blocked_subtasks": gates,
                "reason": "feature_blocked" if is_blocked else "gate_subtask",
            })
    out.sort(key=lambda e: (e["feature"].get("priority", 5), e["feature"].get("title", "")))
    return out

