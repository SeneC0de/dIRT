#!/usr/bin/env python
"""Reshape each project repo's project.json to the new schema (ADR 0038 step 5).

For each project under dIRT (the 6 with local repos; dOCS skipped):
  1. Read canonical data from Firestore directors/{project_id}.
  2. Compose the new project.json (per ADR 0038's "project.json shape" section).
  3. Switch to chore/strip-runtime-to-dirt branch (create from default if absent).
  4. Write the new project.json.
  5. Commit + push (skips silently if content matches — idempotent).

New shape:
    {
      "project_id":       "<id>",
      "project_name":     "<name>",
      "runtime":          "dirt",
      "repo_path":        "<absolute path on this machine>",
      "github_remote":    "https://github.com/<org>/<repo>.git",
      "github_org":       "<org>",
      "commit_signature": { "name": "<character>", "email": "<id>@dapp-controls.com" },
      "description":      "<from Firestore>"
    }

Old fields (director_id, director_name, personality, head_naming_pool) are dropped.

Idempotent. Re-runs on a repo whose project.json already matches the canonical
shape produce no commit.

Run:
    python C:/Users/randa/source/repos/dIRT/scripts/reshape_project_jsons.py
"""
from __future__ import annotations
import json
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

import firestore_db as fdb  # noqa: E402

BRANCH = "chore/strip-runtime-to-dirt"

# Projects with local repos. dOCS has no local repo; skipped.
PROJECT_IDS = ["dcad", "derp", "dweb", "dace", "dash", "dpart"]


def git(repo_path: str, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    cmd = ["git", "-C", repo_path, *args]
    return subprocess.run(cmd, capture_output=True, text=True, check=check)


def default_branch(repo_path: str) -> str:
    """Return the repo's default branch name (main or master)."""
    r = git(repo_path, "symbolic-ref", "refs/remotes/origin/HEAD", check=False)
    if r.returncode == 0 and r.stdout.strip():
        return r.stdout.strip().split("/")[-1]
    for candidate in ("main", "master"):
        r = git(repo_path, "rev-parse", "--verify", f"refs/heads/{candidate}", check=False)
        if r.returncode == 0:
            return candidate
    raise RuntimeError(f"Cannot determine default branch for {repo_path}")


def working_tree_clean(repo_path: str) -> tuple[bool, str]:
    r = git(repo_path, "status", "--porcelain")
    return (r.stdout.strip() == "", r.stdout)


def ensure_branch(repo_path: str, branch: str) -> None:
    """Check out `branch`. Create from default branch if it doesn't exist."""
    r = git(repo_path, "rev-parse", "--verify", f"refs/heads/{branch}", check=False)
    if r.returncode == 0:
        git(repo_path, "checkout", branch)
    else:
        db = default_branch(repo_path)
        git(repo_path, "checkout", "-b", branch, db)


def derive_github_org(remote: str) -> str:
    """Parse https://github.com/<org>/<repo>.git → <org>."""
    if not remote:
        return ""
    parts = remote.rstrip("/").replace(".git", "").split("/")
    return parts[-2] if len(parts) >= 2 else ""


def compose_project_json(project_id: str) -> tuple[dict, str]:
    """Pull from Firestore and compose canonical project.json. Returns (dict, repo_path)."""
    rec = fdb.get_director(project_id)
    if rec is None:
        raise RuntimeError(f"directors/{project_id} not found in Firestore")

    sig = rec.get("commit_signature") or {}
    if not isinstance(sig, dict) or "name" not in sig or "email" not in sig:
        raise RuntimeError(
            f"directors/{project_id} missing commit_signature {{name,email}}; "
            f"run migrate_to_multi_project_runtime.py first"
        )

    remote = rec.get("github_remote") or ""
    repo_path = rec.get("repo_path") or ""
    if not repo_path:
        raise RuntimeError(f"directors/{project_id} has no repo_path")

    data = {
        "project_id":   project_id,
        "project_name": rec.get("name") or project_id,
        "runtime":      "dirt",
        "repo_path":    repo_path,
        "github_remote": remote,
        "github_org":   derive_github_org(remote),
        "commit_signature": {
            "name":  sig["name"],
            "email": sig["email"],
        },
        "description":  rec.get("description") or "",
    }
    return data, repo_path


def write_project_json(repo_path: str, data: dict) -> None:
    """Write project.json (always writes; caller decides whether to commit)."""
    target = Path(repo_path) / "project.json"
    new_text = json.dumps(data, indent=2) + "\n"
    target.write_text(new_text, encoding="utf-8")


def commit_and_push(repo_path: str, char_name: str, char_email: str) -> str | None:
    """Stage project.json, commit, push. Returns commit SHA, or None if nothing to commit."""
    # -f bypasses .gitignore; some repos exclude project.json by default from the old single-file-config era.
    git(repo_path, "add", "-f", "project.json")
    r = git(repo_path, "diff", "--cached", "--quiet", check=False)
    if r.returncode == 0:
        return None

    msg = (
        "chore: reshape project.json to multi-project schema (ADR 0038)\n\n"
        "Adopts the new schema: project_id, project_name, runtime, repo_path,\n"
        "github_remote, github_org, commit_signature{name,email}, description.\n"
        "Old shape (director_id, director_name, personality, head_naming_pool) dropped.\n\n"
        f"Co-Authored-By: {char_name} <{char_email}>"
    )
    git(repo_path, "commit", "-m", msg)

    branch = git(repo_path, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    git(repo_path, "push", "-u", "origin", branch)
    return git(repo_path, "rev-parse", "HEAD").stdout.strip()


def main() -> int:
    print("Reshaping project.json files across 6 project repos (ADR 0038 step 5)")
    print()

    results: list[tuple[str, str, str]] = []

    for project_id in PROJECT_IDS:
        print(f"=== {project_id} ===")
        try:
            data, repo_path = compose_project_json(project_id)
            print(f"  repo_path: {repo_path}")
            char_name = data["commit_signature"]["name"]
            char_email = data["commit_signature"]["email"]

            ensure_branch(repo_path, BRANCH)
            print(f"  on branch: {BRANCH}")

            # Capture any pre-existing dirty state in a WIP commit so the reshape lands clean.
            clean, status = working_tree_clean(repo_path)
            if not clean:
                print("  dirty tree found; capturing in WIP commit:")
                for line in status.strip().split("\n"):
                    print(f"    {line}")
                git(repo_path, "add", "-A")
                r = git(repo_path, "diff", "--cached", "--quiet", check=False)
                if r.returncode != 0:
                    wip_msg = (
                        "wip: snapshot pre-existing working-tree state\n\n"
                        "Captures uncommitted changes so the project.json reshape lands clean.\n\n"
                        f"Co-Authored-By: {char_name} <{char_email}>"
                    )
                    git(repo_path, "commit", "-m", wip_msg)
                    wip_sha = git(repo_path, "rev-parse", "HEAD").stdout.strip()
                    print(f"  wip commit: {wip_sha}")

            write_project_json(repo_path, data)
            sha = commit_and_push(repo_path, char_name, char_email)
            if sha:
                print(f"  committed: {sha}")
                results.append((project_id, "OK", sha))
            else:
                print("  no-op: project.json already matches committed state")
                results.append((project_id, "OK", "no-op"))

        except subprocess.CalledProcessError as e:
            stderr = (e.stderr or "").strip() or str(e)
            print(f"  FAIL: git command failed: {stderr}")
            results.append((project_id, "FAIL", stderr))
        except Exception as e:
            print(f"  FAIL: {type(e).__name__}: {e}")
            results.append((project_id, "FAIL", str(e)))

        print()

    print("Summary:")
    for pid, status, info in results:
        print(f"  {pid:8} {status:5} {info}")

    return 0 if all(r[1] in ("OK", "SKIP") for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
