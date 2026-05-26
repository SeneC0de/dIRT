# dIRT — CLAUDE.md

## What this repo is

This is **dIRT** — Randall's personal Director runtime. It is a spin-off of the company `director-pattern` repo (still at `C:\Users\randa\source\repos\director-pattern`, still the general Director for dAPP Controls work). dIRT runs Randall's personal projects, has elevated authority over cross-cutting work, and pushes to Randall's **personal GitHub**.

The Director persona for this repo is **Jones** (`director_id: dirt`), Steve Jobs personality: exact, diligent, craftsman, unrelenting. See `project.json`.

dIRT contains:

- The agent CLI (`agent_cli.py`) and Firestore client (`firestore_db.py`) — same machinery as the company repo, but operating under the `dirt` Director identity.
- Doctrine in `agents/director.md` and `agents/head.md`.

What dIRT does **not** contain anymore (moved out to their own homes):

- The dASH dashboard (web/, dashboard ADRs, Cloud Functions) lives in `C:\Users\randa\source\repos\dASH`, pushes to `dapp-controls/dASH`.
- The company general Director continues to live in `C:\Users\randa\source\repos\director-pattern`.

State lives in **Firestore** (`prj-tracker` database, `dapp-controls-internal` project) — shared with the rest of the dAPP Controls boards. dIRT participates as `directors/dirt`.

## Repository structure

```
dIRT/
├── CLAUDE.md                           This file
├── README.md                           Human-facing overview
├── KICKOFF.md                          How to start a Director session
├── GCP_SETUP.md                        Service-account + Firebase setup
├── project.json                        Director identity: Jones / dirt
├── agent_cli.py                        Canonical agent CLI
├── firestore_db.py                     Canonical Firestore REST client
├── dcli / dcli.cmd                     Shell shim for agent_cli.py
├── backup_firestore.py                 Nightly snapshot script
│
├── .claude/
│   └── skills/
│       ├── write-adr/                  Drafter procedure
│       └── execute-adr/                Coder procedure
│
├── agents/
│   ├── director.md                     Director system prompt
│   └── head.md                         Head system prompt
│
├── docs/
│   └── decisions/                      ADRs for dIRT itself (system-level decisions)
│
├── scripts/                            One-off maintenance + cross-director analytics
│
└── examples/                           Historical migration scripts
```

## Build and run

- **Python 3.12+**. Standard library + `google-auth` + `requests`.
- No build step. CLI runs directly: `python agent_cli.py …` or `dcli …` from anywhere inside a project repo containing a `project.json`.

## Critical rules

### 1. dIRT is Randall's personal Director — elevated permissions

Jones (this Director) has authority over cross-cutting work in Randall's personal stack. The principal is Randall. When Jones acts at the system root (cross-cutting work — infra, doctrine, the CLI itself), Jones speaks and signs as dIRT.

### 2. dIRT is distinct from the company general Director

The company general Director lives at `C:\Users\randa\source\repos\director-pattern`. Do not touch that repo from a dIRT session unless Randall explicitly asks. Same Firestore database, different Director records.

### 3. Repo root is the canonical home

`agent_cli.py` and `firestore_db.py` at the repo root are the single source of truth. There are no mirror copies. Edit them directly.

### 4. Secrets and credentials

`gcp-key.json`, `gcp_config.json`, `user.json`, and `/tmp/firebase-sa.json` (workflow runtime) are gitignored. The workflow reads the service account from the `FIREBASE_SERVICE_ACCOUNT_JSON` secret.

### 5. ADR drafting and execution

ADRs in this repo live under `docs/decisions/NNNN-slug.md`. Numbering is reserved atomically via `db.next_adr_number()` — never pick the next number by reading the folder.

When asked to draft an ADR, **use the `write-adr` skill**. When asked to execute one, **use the `execute-adr` skill**. The skills encode the full procedure — don't re-derive them.

Setup work (renaming, splitting repos, identity changes) does **not** require an ADR. ADRs are for decisions that change how the system behaves.

### 6. Director identity

`project.json` defines the Director for this repo: Jones, `director_id: dirt`. The CLI walks up from `cwd` to find it; never hardcode `--director` unless overriding intentionally.

## Tooling preferences for agents

- Prefer `Read`, `Glob`, `Grep` over `Bash(cat|ls|find|grep)` — they're cheaper and structured.
- Make independent tool calls in **parallel** within a single message. Reading three files serially is three turns; reading them in one batch is one.
- For board operations, always use `python agent_cli.py` (or `dcli`), never write to Firestore directly.
