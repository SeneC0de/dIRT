"""seed_vendor_parts.py — Idempotent loader for VendorPart rows from Vitalis
intake pricing CSVs (mcb_breaker_prices.csv and motor_protection_prices.csv).

WHAT IT DOES
  For each row in the input CSVs:
    1. Ensure the named Vendor exists in dERP — POST /api/vendors (idempotent
       by name: look up first via GET /api/vendors?q={name}, create only if
       absent).
    2. Resolve the catalog Part by part number — GET /api/parts/by-number/{pn}.
       Rows whose part number is not yet in the catalog are SKIPPED with a
       warning (not an error; the catalog seed is a separate step).
    3. Upsert the primary VendorPart — PUT /api/vendor-parts/primary with
       { partId, vendorId, unitCost, vendorSku: null } (the CSVs carry no
       separate SKU column; part number is the identifier).

IDEMPOTENCE
  - Vendor create: GET first, POST only on 404. A vendor with the same name
    returned by the search is assumed to be the correct vendor (case-insensitive
    equality check; error if multiple hits resolve ambiguously).
  - VendorPart upsert: PUT /api/vendor-parts/primary always; dERP demotes any
    prior primary for the same Part+different Vendor, then upserts atomically.
    Running twice over the same CSV is safe.

CSV SCHEMA (both input files)
  Columns: part_number, price, vendor, kind
  - part_number  — catalog part number (must already exist in dERP)
  - price        — unit cost in USD (decimal)
  - vendor       — vendor display name (e.g. "ABB", "Eaton", "WEG")
  - kind         — informational only (breaker / mmp / contactor / accessory)

VENDOR INFERENCE
  Both CSVs carry a "vendor" column; NO inference is needed.  Each row
  explicitly names its vendor.  See --dry-run output for the resolved vendor
  names.

USAGE
  python scripts/seed_vendor_parts.py --dry-run            # parse + print payloads, no HTTP
  python scripts/seed_vendor_parts.py --dry-run --csv-dir scripts/seed_data   # explicit dir
  python scripts/seed_vendor_parts.py --seed               # GATED: write to dERP

  Credentials (--seed):
    DERP_API_KEY        -> X-Api-Key header
    DERP_BEARER_TOKEN   -> Authorization: Bearer header
    DERP_BASE_URL       -> base URL (default: http://localhost:5180)

  Both price CSVs in --csv-dir (or the directory containing this script's
  seed_data/ sub-folder) are loaded automatically.  You may also pass explicit
  --mcb-csv and --motor-csv paths.

PROD APPLY (gated — run after merge + deploy of ADR-0162 dERP branch)
  export DERP_API_KEY=<from dweb-derp-api-key secret>
  export DERP_BEARER_TOKEN=$(gcloud auth print-identity-token \
      --impersonate-service-account=api-runtime@dappcontrols-dweb.iam.gserviceaccount.com)
  export DERP_BASE_URL=https://derp-api-ntyhimxcca-uc.a.run.app
  python scripts/seed_vendor_parts.py --seed
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Optional

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DEFAULT_BASE_URL = "http://localhost:5180"
VENDORS_PATH = "/api/vendors"
PARTS_BY_NUMBER_PATH = "/api/parts/by-number"
UPSERT_PRIMARY_PATH = "/api/vendor-parts/primary"

# CSVs relative to the scripts/seed_data directory
DEFAULT_SEED_DATA_DIR = Path(__file__).parent / "seed_data"
MCB_CSV_NAME = "mcb_breaker_prices.csv"
MOTOR_CSV_NAME = "motor_protection_prices.csv"

REQUIRED_CSV_COLUMNS = {"part_number", "price", "vendor", "kind"}


# ---------------------------------------------------------------------------
# CSV loading
# ---------------------------------------------------------------------------

def load_csv(path: Path) -> list[dict[str, str]]:
    """Return list of row dicts from a price CSV; validate required columns."""
    with path.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            raise ValueError(f"{path}: empty file or no header")
        cols = {c.strip() for c in reader.fieldnames}
        missing = REQUIRED_CSV_COLUMNS - cols
        if missing:
            raise ValueError(f"{path}: missing columns {missing!r}")
        rows = [
            {k.strip(): v.strip() for k, v in row.items()}
            for row in reader
            if any(v.strip() for v in row.values())  # skip blank rows
        ]
    return rows


def load_all_rows(csv_dir: Path,
                  mcb_override: Optional[Path],
                  motor_override: Optional[Path]) -> list[tuple[str, dict[str, str]]]:
    """Load both CSVs; return list of (source_file_name, row)."""
    mcb_path = mcb_override or (csv_dir / MCB_CSV_NAME)
    motor_path = motor_override or (csv_dir / MOTOR_CSV_NAME)
    results: list[tuple[str, dict[str, str]]] = []
    for path in (mcb_path, motor_path):
        rows = load_csv(path)
        results.extend((path.name, r) for r in rows)
    return results


# ---------------------------------------------------------------------------
# HTTP helpers (stdlib only — mirrors seed_e1404.py / seed_weg_mmp.py)
# ---------------------------------------------------------------------------

def _auth_headers() -> dict[str, str]:
    h: dict[str, str] = {}
    if os.environ.get("DERP_API_KEY"):
        h["X-Api-Key"] = os.environ["DERP_API_KEY"]
    if os.environ.get("DERP_BEARER_TOKEN"):
        h["Authorization"] = "Bearer " + os.environ["DERP_BEARER_TOKEN"]
    return h


def _json_headers() -> dict[str, str]:
    h = {"Content-Type": "application/json", "Accept": "application/json"}
    h.update(_auth_headers())
    return h


def _send(req: urllib.request.Request) -> tuple[int, Any]:
    """Return (status_code, parsed_body_or_raw_str)."""
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            raw = resp.read().decode("utf-8")
            return resp.status, _maybe_json(raw)
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "replace")
        return e.code, _maybe_json(raw)
    except urllib.error.URLError as e:
        return 0, f"connection failed: {e.reason}"
    except (TimeoutError, OSError) as e:
        return 0, f"connection failed: {e}"


def _maybe_json(raw: str) -> Any:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


def _get(base_url: str, path: str) -> tuple[int, Any]:
    req = urllib.request.Request(
        base_url.rstrip("/") + path,
        headers={"Accept": "application/json", **_auth_headers()},
        method="GET",
    )
    return _send(req)


def _post(base_url: str, path: str, payload: dict[str, Any]) -> tuple[int, Any]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        base_url.rstrip("/") + path,
        data=data,
        headers=_json_headers(),
        method="POST",
    )
    return _send(req)


def _put(base_url: str, path: str, payload: dict[str, Any]) -> tuple[int, Any]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        base_url.rstrip("/") + path,
        data=data,
        headers=_json_headers(),
        method="PUT",
    )
    return _send(req)


# ---------------------------------------------------------------------------
# Vendor resolution (idempotent GET-then-POST)
# ---------------------------------------------------------------------------

class VendorCache:
    """Maintains an in-process cache of vendor name -> vendorId to avoid
    repeated GET calls for the same vendor within one run."""

    def __init__(self) -> None:
        # normalized_name -> vendor_id (str)
        self._cache: dict[str, str] = {}

    def _normalize(self, name: str) -> str:
        return name.strip().lower()

    def get_or_create(self,
                      base_url: str,
                      vendor_name: str,
                      dry_run: bool,
                      created_vendors: list[str]) -> Optional[str]:
        """Return the vendorId (str UUID) for vendor_name, creating if needed.
        In dry_run mode: no HTTP; returns a deterministic fake id.
        Returns None on unrecoverable error."""
        key = self._normalize(vendor_name)
        if key in self._cache:
            return self._cache[key]

        if dry_run:
            # In dry-run mode we cannot call the server; assign a deterministic
            # placeholder id so the PUT payload shapes are visible and valid.
            fake_id = f"<VENDOR-{vendor_name}>"
            post_payload: dict[str, Any] = {"name": vendor_name, "isActive": True}
            print(f"  [DRY-RUN] POST {VENDORS_PATH} {json.dumps(post_payload)}")
            print(f"           -> would resolve/create vendor {vendor_name!r}, id={fake_id}")
            self._cache[key] = fake_id
            if vendor_name not in created_vendors:
                created_vendors.append(vendor_name)
            return fake_id

        # Search for existing vendor
        qs = urllib.parse.urlencode({"q": vendor_name, "take": "5"})
        status, body = _get(base_url, f"{VENDORS_PATH}?{qs}")
        if status != 200:
            print(f"  [ERROR] GET /api/vendors?q={vendor_name!r} -> HTTP {status}: {body!r}")
            return None

        items: list[dict[str, Any]] = []
        if isinstance(body, dict):
            items = body.get("items", [])
        elif isinstance(body, list):
            items = body

        # Case-insensitive exact match on name
        matches = [v for v in items if v.get("name", "").strip().lower() == key]

        if len(matches) == 1:
            vid = str(matches[0]["id"])
            self._cache[key] = vid
            return vid
        if len(matches) > 1:
            print(f"  [ERROR] multiple vendors named {vendor_name!r}; manual cleanup required")
            return None

        # Not found — create
        post_payload = {"name": vendor_name, "isActive": True}
        status, body = _post(base_url, VENDORS_PATH, post_payload)
        if status not in (200, 201):
            print(f"  [ERROR] POST /api/vendors -> HTTP {status}: {body!r}")
            return None

        if isinstance(body, dict) and "id" in body:
            vid = str(body["id"])
            self._cache[key] = vid
            created_vendors.append(vendor_name)
            print(f"  [CREATED] vendor {vendor_name!r} -> {vid}")
            return vid

        print(f"  [ERROR] POST /api/vendors unexpected response: {body!r}")
        return None


# ---------------------------------------------------------------------------
# Part lookup (by part number)
# ---------------------------------------------------------------------------

class PartCache:
    """Cache of partNumber -> partId (str UUID) or None (not found)."""

    def __init__(self) -> None:
        self._cache: dict[str, Optional[str]] = {}

    def lookup(self, base_url: str, part_number: str, dry_run: bool) -> Optional[str]:
        if part_number in self._cache:
            return self._cache[part_number]

        if dry_run:
            # In dry-run mode we can't hit the server; use a placeholder that
            # makes the shape obvious but clearly fake
            fake_id = f"<PART-{part_number}>"
            self._cache[part_number] = fake_id
            return fake_id

        enc = urllib.parse.quote(part_number, safe="")
        status, body = _get(base_url, f"{PARTS_BY_NUMBER_PATH}/{enc}")
        if status == 404:
            self._cache[part_number] = None
            return None
        if status != 200:
            print(f"  [ERROR] GET /api/parts/by-number/{part_number!r} -> HTTP {status}: {body!r}")
            self._cache[part_number] = None
            return None

        if isinstance(body, dict) and "id" in body:
            pid = str(body["id"])
            self._cache[part_number] = pid
            return pid

        print(f"  [ERROR] GET /api/parts/by-number/{part_number!r} unexpected: {body!r}")
        self._cache[part_number] = None
        return None


# ---------------------------------------------------------------------------
# Core seeding loop
# ---------------------------------------------------------------------------

def run(base_url: str,
        all_rows: list[tuple[str, dict[str, str]]],
        dry_run: bool) -> dict[str, int]:
    """Process all rows. Returns a stats dict."""
    vendor_cache = VendorCache()
    part_cache = PartCache()
    created_vendors: list[str] = []

    stats = {
        "total": 0,
        "skipped_no_part": 0,
        "skipped_no_vendor": 0,
        "upserted": 0,
        "errors": 0,
    }

    for src_file, row in all_rows:
        stats["total"] += 1
        pn = row["part_number"]
        vendor_name = row["vendor"]
        try:
            unit_cost = float(row["price"])
        except (ValueError, KeyError):
            print(f"  [SKIP] {pn}: invalid price {row.get('price')!r}")
            stats["errors"] += 1
            continue

        # 1. Ensure vendor exists
        vendor_id = vendor_cache.get_or_create(
            base_url, vendor_name, dry_run, created_vendors)
        if vendor_id is None:
            print(f"  [SKIP] {pn}: could not resolve/create vendor {vendor_name!r}")
            stats["skipped_no_vendor"] += 1
            continue

        # 2. Resolve part
        part_id = part_cache.lookup(base_url, pn, dry_run)
        if part_id is None:
            print(f"  [SKIP] {pn}: not in catalog (seed catalog first)")
            stats["skipped_no_part"] += 1
            continue

        # 3. Upsert primary VendorPart
        put_payload: dict[str, Any] = {
            "partId": part_id,
            "vendorId": vendor_id,
            "unitCost": round(unit_cost, 2),
        }
        # No vendorSku in these CSVs — omit the field entirely so dERP
        # preserves any existing SKU on update.

        if dry_run:
            print(f"  [DRY-RUN] PUT /api/vendor-parts/primary")
            print(f"            source={src_file} part={pn} vendor={vendor_name}")
            print(f"            payload={json.dumps(put_payload)}")
            stats["upserted"] += 1
            continue

        status, body = _put(base_url, UPSERT_PRIMARY_PATH, put_payload)
        if status == 200:
            created_flag = body.get("created", "?") if isinstance(body, dict) else "?"
            action = "INSERTED" if created_flag is True else "UPDATED"
            print(f"  [{action}] {pn} -> vendor={vendor_name}")
            stats["upserted"] += 1
        else:
            print(f"  [ERROR] PUT /api/vendor-parts/primary for {pn}: "
                  f"HTTP {status} {body!r}")
            stats["errors"] += 1

    return stats


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def resolve_base_url(cli: Optional[str]) -> str:
    return cli or os.environ.get("DERP_BASE_URL", DEFAULT_BASE_URL)


def main(argv: Optional[list[str]] = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

    p = argparse.ArgumentParser(
        description="Seed VendorPart rows from Vitalis intake pricing CSVs.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--base-url", default=None,
                   help="dERP base URL (default: $DERP_BASE_URL or http://localhost:5180)")
    p.add_argument("--csv-dir", type=Path, default=DEFAULT_SEED_DATA_DIR,
                   help=f"Directory containing both price CSVs "
                        f"(default: {DEFAULT_SEED_DATA_DIR})")
    p.add_argument("--mcb-csv", type=Path, default=None,
                   help="Override path to mcb_breaker_prices.csv")
    p.add_argument("--motor-csv", type=Path, default=None,
                   help="Override path to motor_protection_prices.csv")
    p.add_argument("--dry-run", action="store_true",
                   help="Parse CSVs and print payloads; do NOT contact the server")
    p.add_argument("--seed", action="store_true",
                   help="GATED: write VendorPart rows to dERP (requires credentials)")
    args = p.parse_args(argv)

    if not args.dry_run and not args.seed:
        print("No action specified. Pass --dry-run (safe) or --seed (gated live run).")
        print("  python scripts/seed_vendor_parts.py --dry-run")
        return 1

    # Load CSVs
    try:
        all_rows = load_all_rows(args.csv_dir, args.mcb_csv, args.motor_csv)
    except (FileNotFoundError, ValueError) as e:
        print(f"[ERROR] CSV load failed: {e}")
        return 1

    print(f"Loaded {len(all_rows)} rows from 2 CSVs")

    base_url = resolve_base_url(args.base_url)

    if args.dry_run:
        print(f"=== DRY-RUN (no HTTP) — would target {base_url} ===")
    else:
        print(f"=== SEED -> {base_url} ===")

    print()
    stats = run(base_url, all_rows, dry_run=args.dry_run)

    print()
    print("=== SUMMARY ===")
    print(f"  total rows    : {stats['total']}")
    print(f"  upserted      : {stats['upserted']}")
    print(f"  skipped (no part in catalog) : {stats['skipped_no_part']}")
    print(f"  skipped (vendor error)       : {stats['skipped_no_vendor']}")
    print(f"  errors        : {stats['errors']}")

    if args.dry_run:
        # Summarize unique vendors seen
        vendors_seen: set[str] = set()
        for _, row in all_rows:
            vendors_seen.add(row["vendor"])
        print(f"  vendors in CSVs: {sorted(vendors_seen)}")

    ok = stats["errors"] == 0
    print()
    print("DRY-RUN complete — no writes." if args.dry_run else
          ("SEED OK" if ok else "SEED COMPLETE WITH ERRORS"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
