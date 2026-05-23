# GCP setup for Firestore-backed agent control

Run these steps once. Total time ~10 minutes. You'll come back with two values: a **project ID** and a **service-account key file path**.

## 1. Create a GCP project

Easiest via the browser at <https://console.cloud.google.com/projectcreate>:

- **Project name:** `dapp-controls-agents` (any name is fine — pick what fits).
- **Project ID:** GCP will auto-suggest one (e.g. `dapp-controls-agents-123456`). Note it — you'll paste it back to me.
- **Organization / Location:** pick your dapp-controls org if you have a GCP org; otherwise "No organization" is fine.

Click **Create**, wait ~30 seconds for it to provision.

## 2. Enable Firestore in Native mode

<https://console.cloud.google.com/firestore/databases>

- Make sure the project selector (top of page) is set to the new project.
- Click **Create Database**.
- Pick **Native mode** (not Datastore mode — they're not the same and we want Native).
- Location: pick a region close to you (`us-east1`, `us-central1`, `us-east4` for Atlanta — `us-east1` is geographically closest).
- Click **Create Database**. Takes ~1 minute.

## 3. Create a service account for the agent CLI

<https://console.cloud.google.com/iam-admin/serviceaccounts>

- Click **Create Service Account**.
- Name: `agent-control`. ID auto-fills.
- **Grant access:** add the role **Cloud Datastore User** (this works for Firestore Native too — Firestore inherits Datastore's IAM names). If you can find "Firestore Service Agent" or "Firestore User", that's fine too.
- Skip the optional "Grant users access" step.
- Click **Done**.

## 4. Download the service account key

Back on the service-accounts page, click the new `agent-control@...` row → **Keys** tab → **Add Key** → **Create new key** → **JSON** → **Create**.

A JSON file downloads. **Move it to your director-pattern repo root** as `gcp-key.json` (e.g. `C:\Users\<you>\source\repos\director-pattern\gcp-key.json`). Don't commit it to git — `.gitignore` already lists `gcp-key.json`.

## 5. Install the Firestore Python SDK

In PowerShell:

```powershell
pip install google-cloud-firestore
```

## 6. Verify

```powershell
cd C:\Users\<you>\source\repos\director-pattern
$env:GOOGLE_APPLICATION_CREDENTIALS = "$PWD\gcp-key.json"
python -c "from google.cloud import firestore; c = firestore.Client(project='YOUR_PROJECT_ID'); c.collection('_smoke').document('hello').set({'ok': True}); print('OK'); doc = c.collection('_smoke').document('hello').get(); print(doc.to_dict())"
```

Substitute `YOUR_PROJECT_ID`. Output should be:

```
OK
{'ok': True}
```

If that prints, you're set.

## 7. Tell me

Paste back:

- The **project ID** (the auto-generated one or the one you chose).
- Confirm `gcp-key.json` is at the director-pattern repo root.

Then I'll do the migration: import dcad.db's current state into Firestore (collapsing P4.1–P4.4 into a single "Phase 4 — Repo Transfer" feature with the four as sub-tasks), wire up the new agent_cli.py, and build the collapsed dashboard.
