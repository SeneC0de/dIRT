# dIRT

Randall's personal Director runtime. A spin-off of `director-pattern` (the dAPP Controls company general Director, still at `C:\Users\randa\source\repos\director-pattern`).

Director: **Jones** (`project_id: dirt`), Steve Jobs persona: exact, diligent, craftsman, unrelenting. Defined in `project.json`.

Pushes to Randall's **personal GitHub**.

State lives in Firestore (`prj-tracker` @ `dapp-controls-internal`), shared with the rest of the dAPP Controls Director boards. dIRT participates as `directors/dirt`.

Python 3.12+, standard library + `google-auth` + `requests`.

---

## What's here

| Path | What |
|---|---|
| `agent_cli.py`, `firestore_db.py` | The dCLI and Firestore client — canonical implementations at repo root |
| `dcli`, `dcli.cmd` | Shell shims for `agent_cli.py` |
| `agents/director.md` | Director system prompt (doctrine) |
| `agents/head.md` | Head system prompt (doctrine) |
| `.claude/skills/` | `write-adr/`, `execute-adr/` — the procedures Heads load when drafting or implementing |
| `docs/decisions/` | ADRs for dIRT itself (system-level decisions only) |
| `scripts/` | ADR-flow scripts (`draft_adr.py`, `approve_adr.py`, `dispatch_executor.py`, `mark_tested.py`) and maintenance utilities |
| `backup_firestore.py` | Nightly Firestore snapshot script |
| `KICKOFF.md`, `GCP_SETUP.md` | Startup + Firebase service-account setup |

## What's NOT here

The dAPP Controls dashboard product — `web/`, dashboard ADRs (0001, 0003, 0004), Cloud Functions — lives in **`C:\Users\randa\source\repos\dASH`** and pushes to `dapp-controls/dASH`.

## Run

```
dcli kickoff
```

…from anywhere inside this repo. Reads the kickoff message, doctrine, and the project identity, then runs the startup ritual described in `agents/director.md`.

## Architecture in one picture

```
                            ┌────────────────────────────────────────────┐
                            │  Firestore (prj-tracker @ dapp-controls)   │
                            │  Collections: directors, features,         │
                            │  subtasks, agents, events, artifacts       │
                            └─────────────────────┬──────────────────────┘
                                                  │
              ┌───────────────────────────────────┴────────────────────────────────┐
              │                                                                    │
              ▼                                                                    ▼
   ┌────────────────────────────┐                              ┌────────────────────────────────┐
   │  dASH (separate repo)      │                              │  Director Cowork chats          │
   │  dapp-controls/dASH        │                              │  (one per Director repo)        │
   │  - Firebase Hosting        │                              │   - dIRT (this repo, personal)  │
   │  - Cloud Functions (dASH)  │                              │   - director-pattern (company)  │
   │  - direct-to-Firestore JS  │                              │   - dCAD, dERP, dPART, dWEB…    │
   └────────────────────────────┘                              └─────────────┬───────────────────┘
                                                                             │
                                                                             ▼
                                                              dispatches Heads via Agent / Task tool
                                                              Heads run `dcli …` (CLI → Firestore)
```

## History

This repo was spun off from `director-pattern` on 2026-05-23 by Jones (the very first thing Jones did after waking up). The original `director-pattern` continues to operate as the company general Director. dIRT operates as Randall's personal Director with elevated authority over his personal stack.

The split moved out:
- `web/`, `functions/`, dashboard ADRs → `dASH`
- Everything else (CLI, doctrine, workflow, system ADRs) stayed.
