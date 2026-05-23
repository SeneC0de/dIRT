"""Pre-agent step: fetch board context from Firestore and write .agent_context.json.

Uses the shared firestore_db.py REST client (same code path as local dcli).
Credentials come from FIREBASE_SA_FILE or GOOGLE_APPLICATION_CREDENTIALS.
"""
import json
import os
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))          # project repos: firestore_db.py in .github/scripts/
sys.path.insert(0, str(_HERE.parent.parent))  # director-pattern: firestore_db.py at repo root
import firestore_db as db


did = os.environ["DIRECTOR_ID"]

director = db.get_director(did) or {}

stories = db.list_features(director_id=did)[:25]
adrs    = db.list_adrs(limit=20)

ctx = {
    "director": {
        "director_id":  director.get("director_id") or director.get("id") or did,
        "name":         director.get("name", did),
        "description":  director.get("description", ""),
        "personality":  director.get("personality", ""),
    },
    "stories": [
        {
            "id":         s.get("id"),
            "title":      s.get("title"),
            "status":     s.get("status"),
            "adr_url":    s.get("adr_url"),
            "adr_number": s.get("adr_number"),
        }
        for s in stories
    ],
    "adrs": [
        {
            "id":     a.get("id"),
            "number": a.get("number"),
            "title":  a.get("title"),
            "status": a.get("status"),
            "url":    a.get("url"),
        }
        for a in adrs
    ],
}

with open(".agent_context.json", "w") as f:
    json.dump(ctx, f, indent=2, default=str)

print(f"Context written for director: {did}")
print(f"  Stories: {len(stories)}, ADRs: {len(adrs)}")
