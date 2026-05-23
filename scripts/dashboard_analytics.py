"""Cross-director analytics for dIRT — pulls raw Firestore state and computes
the metrics needed to ground the dashboard redesign in data, not impressions.

Output: markdown to stdout. Run from anywhere (resolves firestore_db via PATH).

What it answers:
- Which event types fire, how often, on what cadence (last 7d / 30d / lifetime)?
- Where do features stall? (status distribution, age of blocked/open, archive rate)
- Where do tasks rot? (in_progress age distribution, cycle time for done)
- Which directors are actually active? (events/features in last 7d)
- Message volume per thread — is the chat dock load-bearing or noise?
- How many ADRs accepted vs draft vs stale?
"""
from __future__ import annotations
import sys, os, json, statistics, io
from collections import Counter, defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Force UTF-8 stdout on Windows (cp1252 chokes on arrows etc.)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# Resolve firestore_db.py — lives at the repo root, one level up from scripts/.
_REPO_ROOT = Path(__file__).resolve().parent.parent
if (_REPO_ROOT / "firestore_db.py").exists():
    sys.path.insert(0, str(_REPO_ROOT))
import firestore_db as db


NOW = datetime.now(timezone.utc)
D7  = NOW - timedelta(days=7)
D30 = NOW - timedelta(days=30)


def _ts(v):
    """Coerce a Firestore timestamp into a tz-aware datetime, or None."""
    if v is None:
        return None
    if isinstance(v, datetime):
        return v if v.tzinfo else v.replace(tzinfo=timezone.utc)
    if isinstance(v, str):
        try:
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        except ValueError:
            return None
    return None


def fetch_all(collection):
    """Pull every document from a top-level collection. No filter."""
    return db._runquery(db._build_query(collection))


def hours(td): return td.total_seconds() / 3600
def days(td):  return td.total_seconds() / 86400


def fmt_h(td):
    h = hours(td)
    return f"{h:.1f}h" if h < 48 else f"{h/24:.1f}d"


def percentile(xs, p):
    if not xs: return None
    xs = sorted(xs)
    k = (len(xs)-1) * p / 100
    f = int(k); c = min(f+1, len(xs)-1)
    if f == c: return xs[f]
    return xs[f] + (xs[c]-xs[f]) * (k-f)


def section(title): print(f"\n## {title}\n")
def kv(k, v): print(f"- **{k}**: {v}")
def row(*cells): print("| " + " | ".join(str(c) for c in cells) + " |")
def hdr(*cells):
    row(*cells)
    row(*("---" for _ in cells))


# --------------------- pull ---------------------

print("# dIRT analytics snapshot")
print(f"\n_Generated {NOW.isoformat()}_")

directors = fetch_all("directors")
features  = fetch_all("features")
subtasks  = fetch_all("subtasks")
events    = fetch_all("events")
adrs      = fetch_all("adrs")
try:
    messages = fetch_all("messages")
except Exception as e:
    messages = []
    print(f"\n_(messages collection unavailable: {e})_")
try:
    agents = fetch_all("agents")
except Exception:
    agents = []

director_by_id = {d["id"]: d for d in directors}

# --------------------- topline ---------------------

section("Topline")
kv("Directors", len(directors))
kv("Features (all)", f"{len(features)} ({sum(1 for f in features if f.get('archived')):,} archived)")
kv("Subtasks (all)", f"{len(subtasks)} ({sum(1 for s in subtasks if s.get('archived')):,} archived)")
kv("Events (all-time)", len(events))
kv("Events (last 7d)", sum(1 for e in events if (_ts(e.get('ts')) or NOW) >= D7))
kv("Events (last 30d)", sum(1 for e in events if (_ts(e.get('ts')) or NOW) >= D30))
kv("ADRs", len(adrs))
kv("Messages", len(messages))
kv("Agents", len(agents))

# --------------------- event types ---------------------

section("Event types (frequency)")
event_types_lifetime = Counter(e.get("type", "?") for e in events)
event_types_30d = Counter(e.get("type", "?") for e in events if (_ts(e.get("ts")) or NOW) >= D30)
event_types_7d  = Counter(e.get("type", "?") for e in events if (_ts(e.get("ts")) or NOW) >= D7)

hdr("type", "7d", "30d", "lifetime")
for t, _ in event_types_lifetime.most_common(40):
    row(t, event_types_7d.get(t, 0), event_types_30d.get(t, 0), event_types_lifetime[t])

# --------------------- director activity ---------------------

section("Director activity (events in last 7d / last 30d / lifetime)")
ev_per_dir_7  = Counter(e.get("director_id") for e in events if (_ts(e.get("ts")) or NOW) >= D7)
ev_per_dir_30 = Counter(e.get("director_id") for e in events if (_ts(e.get("ts")) or NOW) >= D30)
ev_per_dir_lt = Counter(e.get("director_id") for e in events)

hdr("director", "7d", "30d", "lifetime", "open features", "blocked features", "in_progress tasks")
for d in sorted(directors, key=lambda x: -ev_per_dir_7.get(x["id"], 0)):
    did = d["id"]
    open_ct  = sum(1 for f in features if f.get("director_id") == did and f.get("status") == "open" and not f.get("archived"))
    block_ct = sum(1 for f in features if f.get("director_id") == did and f.get("status") == "blocked" and not f.get("archived"))
    ip_ct    = sum(1 for s in subtasks if s.get("director_id") == did and s.get("status") == "in_progress" and not s.get("archived"))
    row(did, ev_per_dir_7.get(did, 0), ev_per_dir_30.get(did, 0), ev_per_dir_lt.get(did, 0),
        open_ct, block_ct, ip_ct)

# --------------------- feature status ---------------------

section("Feature status (live, non-archived)")
status_counter = Counter()
for f in features:
    if f.get("archived"): continue
    status_counter[f.get("status", "?")] += 1
hdr("status", "count")
for s, c in status_counter.most_common():
    row(s, c)

# --------------------- feature age by status ---------------------

section("Age of features by status (non-archived, days since created)")
ages_by_status = defaultdict(list)
for f in features:
    if f.get("archived"): continue
    created = _ts(f.get("created_at"))
    if not created: continue
    ages_by_status[f.get("status", "?")].append(days(NOW - created))

hdr("status", "n", "p50 (d)", "p75 (d)", "p90 (d)", "max (d)")
for s, ages in sorted(ages_by_status.items()):
    row(s, len(ages),
        f"{percentile(ages, 50):.1f}" if ages else "-",
        f"{percentile(ages, 75):.1f}" if ages else "-",
        f"{percentile(ages, 90):.1f}" if ages else "-",
        f"{max(ages):.1f}" if ages else "-")

# --------------------- archive rate ---------------------

section("Archive rate (lifetime)")
arch_f = sum(1 for f in features if f.get("archived"))
arch_s = sum(1 for s in subtasks if s.get("archived"))
kv("Features archived", f"{arch_f} / {len(features)} ({arch_f/max(1,len(features))*100:.1f}%)")
kv("Subtasks archived", f"{arch_s} / {len(subtasks)} ({arch_s/max(1,len(subtasks))*100:.1f}%)")

# --------------------- subtask in_progress age ---------------------

section("In-progress task age (non-archived)")
ip_ages = []
for s in subtasks:
    if s.get("archived"): continue
    if s.get("status") != "in_progress": continue
    started = _ts(s.get("started_at")) or _ts(s.get("claimed_at")) or _ts(s.get("created_at"))
    if not started: continue
    ip_ages.append(hours(NOW - started))

if ip_ages:
    hdr("n in_progress", "p50 (h)", "p75 (h)", "p90 (h)", "max (h)", ">24h", ">7d")
    row(len(ip_ages),
        f"{percentile(ip_ages, 50):.1f}",
        f"{percentile(ip_ages, 75):.1f}",
        f"{percentile(ip_ages, 90):.1f}",
        f"{max(ip_ages):.1f}",
        sum(1 for h in ip_ages if h > 24),
        sum(1 for h in ip_ages if h > 168))
else:
    print("_No in_progress subtasks._")

# --------------------- subtask cycle time ---------------------

section("Subtask cycle time (start → done, last 90d)")
cycle_hours = []
for s in subtasks:
    if s.get("status") != "done": continue
    started   = _ts(s.get("started_at")) or _ts(s.get("claimed_at"))
    completed = _ts(s.get("completed_at"))
    if not (started and completed): continue
    if completed < NOW - timedelta(days=90): continue
    cycle_hours.append(hours(completed - started))

if cycle_hours:
    hdr("n", "p50 (h)", "p75 (h)", "p90 (h)", "max (h)")
    row(len(cycle_hours),
        f"{percentile(cycle_hours, 50):.1f}",
        f"{percentile(cycle_hours, 75):.1f}",
        f"{percentile(cycle_hours, 90):.1f}",
        f"{max(cycle_hours):.1f}")
else:
    print("_No completed subtasks with timing data._")

# --------------------- messages per thread ---------------------

section("Messages per thread (volume)")
if messages:
    by_thread = Counter(m.get("thread_id", "?") for m in messages)
    hdr("thread_id", "messages")
    for tid, c in by_thread.most_common(15):
        row(tid, c)
    kv("Total threads", len(by_thread))
    kv("Total messages", len(messages))
else:
    print("_No messages._")

# --------------------- ADR pipeline ---------------------

section("ADR pipeline state")
adr_by_status = Counter(a.get("status", "?") for a in adrs)
hdr("status", "count")
for s, c in adr_by_status.most_common():
    row(s, c)

# Stale draft ADRs
stale_drafts = []
for a in adrs:
    if a.get("status") != "draft": continue
    updated = _ts(a.get("updated_at")) or _ts(a.get("created_at"))
    if not updated: continue
    if updated < NOW - timedelta(days=2):
        stale_drafts.append((a.get("number"), a.get("title"), days(NOW - updated)))

if stale_drafts:
    print("\n_Draft ADRs untouched for >2 days (Step 4 stalls):_")
    hdr("number", "title", "days stale")
    for n, t, d in sorted(stale_drafts, key=lambda x: -x[2]):
        row(n, (t or "")[:60], f"{d:.1f}")

# --------------------- approval→work gap (the bug ADR 0037 fixes) ---------------------

section("Approval → next-action latency (the gap ADR 0037 closes)")
fapp = [e for e in events if e.get("type") == "feature_approved"]
gaps = []
for e in fapp:
    fid = e.get("feature_id")
    if not fid: continue
    appr_ts = _ts(e.get("ts"))
    if not appr_ts: continue
    later = [_ts(x.get("ts")) for x in events
             if x.get("feature_id") == fid
             and x.get("type") in ("subtask_created", "agent_registered")
             and _ts(x.get("ts")) and _ts(x.get("ts")) > appr_ts]
    if later:
        gap = hours(min(later) - appr_ts)
        gaps.append(gap)
    else:
        # nothing happened after approval — count as "still open" gap
        gaps.append(hours(NOW - appr_ts))

if gaps:
    hdr("n approvals", "p50 (h)", "p75 (h)", "p90 (h)", "max (h)", ">24h after approve")
    row(len(gaps),
        f"{percentile(gaps, 50):.1f}",
        f"{percentile(gaps, 75):.1f}",
        f"{percentile(gaps, 90):.1f}",
        f"{max(gaps):.1f}",
        sum(1 for h in gaps if h > 24))
else:
    print("_No feature_approved events to measure._")

# --------------------- feature edit churn ---------------------

section("Most-edited features (event count, lifetime)")
ev_per_feat = Counter(e.get("feature_id") for e in events if e.get("feature_id"))
hdr("feature_id", "director", "title", "events")
for fid, c in ev_per_feat.most_common(10):
    f = next((x for x in features if x.get("id") == fid), None)
    if not f: continue
    row(fid[:12], f.get("director_id", "?"), (f.get("title") or "")[:60], c)

# --------------------- "hot" pointers ---------------------

section("Hot pointers (set_hot usage)")
hot_set = sum(1 for d in directors if d.get("hot_1"))
kv("Directors with hot_1 set", f"{hot_set} / {len(directors)}")
for d in directors:
    h = d.get("hot_1")
    if not h: continue
    ts = _ts(h.get("set_at"))
    age = fmt_h(NOW - ts) if ts else "?"
    kv(f"{d['id']}", f"{(h.get('title') or '')[:60]} ({age} old)")

print("\n---\n_End of snapshot._")
