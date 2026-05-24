# Vitalis — Document intake

Raw documents from Vitalis panel jobs land here. AI ingests them and produces three derivatives in `extracted/`, which then seed dCAD / dPART / dERP for the panel→PO pipeline.

## Pipeline

```
_intake/vitalis/{drawings,boms,config-sheets,pos,rfqs,invoices,order-acks,jobs}/
        │
        ▼  (AI extraction pass — cross-references prior analyses)
_intake/vitalis/extracted/
        ├── panel-template.yaml        ← the 85% invariant panel
        ├── selection-rules.yaml       ← the 15% variable (controller + HMI/PLC logic)
        ├── parts-additions.json       ← anything missing from dPART's catalog
        ├── po-summary.json            ← 30 POs / 100 parts / 7 vendors / 19 categories (prior pass)
        └── prior-analyses/            ← per-job Head-agent recon (E1392, E1395, E1399, E1404)
        │
        ▼  (review + merge, one ADR per phase)
dCAD.Configuration / dPART seed / dERP Part catalog
```

Once extraction has been reviewed and merged downstream, this folder stops being load-bearing. It's source material, not runtime data.

## Folder map

| Folder | What goes here | Examples / notes |
|---|---|---|
| `drawings/` | Panel schematics, layout, dimension, GA, single-line | `E####_*.pdf` |
| `boms/` | Historical BOMs in any format | `E#### - <site>.xlsx` |
| `config-sheets/` | Selection criteria — "if input X then choose Y" | `IO List w Card Mapping DANFOSS.xlsx` |
| `pos/` | POs you issued to vendors | `Purchase Order - P-####.pdf` |
| `rfqs/` | RFQs sent to vendors (precursor to POs, distinct bucket) | `NG## - MB#### - RFQ.xlsx` |
| `invoices/` | Vendor invoices — validates part numbers + pricing | `Invoice #### - Vitalis <site>.pdf` |
| `order-acks/` | OAs + packing lists from vendors | `PO# P-#### - Order Acknowledgement.pdf` |
| `jobs/<job-id>/` | Optional: bundle a single job's docs together | `jobs/E1392/...` |
| `context/` | Landscape / orientation docs AI reads before extraction | `roadmap.md`, `api-landscape.md`, `database-landscape.md` |
| `reference/` | Non-customer reference material (commits) | ACADE API library, drawing templates |
| `extracted/` | AI-derived outputs (commits) | See pipeline above |

## Bedrock data rules — read before extracting (from Randall, via Carl Sagan's recon 2026-05-18)

**All data is HUMAN-PRODUCED. Errors exist; flag them, don't repair.**

- **BOM rows: ONLY rows between the purple bar and the red bar count.**
  - Above purple = made-up section headers, **ignore**.
  - Outside the bars = removed-for-posterity OR fudges (wire, cable tray, consumables).
- **Wago parts outside relays/PSUs** (small TBs, marking, etc.) = **estimates, low confidence**.
- **Fab packets** are mostly incomplete shells.
- Cross-document drift is real and load-bearing — flag mismatches between PO / OA / BOM / drawing as findings, don't silently reconcile them.

## Controller variability — explicit scope

Per Randall: "every panel is 85% the same except the controller." That **controller** dimension spans two axes:

1. **Refrigeration controller family** — Danfoss AK vs Copeland CC vs other. dCAD already targets Danfoss + Copeland.
2. **HMI/PLC selection on top** — separate hardware stack feeding the same refrigeration logic.

`selection-rules.yaml` must capture both. The `panel-template.yaml` invariant ends where these two start.

## Prior analyses (in `extracted/prior-analyses/`)

Four jobs already analyzed end-to-end by Head agents (Gaal Dornick, Salvor Hardin). Each folder is a self-contained recon packet:

| Job | Customer site | Panel tag | Notes |
|---|---|---|---|
| `E1392` | 4S Ranch | MB0216 | 78 BOM rows, 5 compressors (3 MT + 2 LT), Copeland, ABB XT5N 400A main, NEMA 3R |
| `E1395` | Lazy Acres | SCP-01 / MB0219 | 71 BOM rows, Danfoss stack, PO P-38262 |
| `E1399` | YCH Freecovery | Roxsta G6 MB0206 | (see folder) |
| `E1404` | Northgate 49 | MB0221 | (see folder) |

Each packet contains 7-8 files: `lifecycle.md` (RFQ → invoice), `xlsx-profile.md` (BOM bar layout), `process-docs.md` (Fab Packet / QC / wire changes), `feature-parts-association.md` (panel feature → BOM rows), `part-feel.md` (row-by-row selection-criteria intuition with H/M/L confidence), `story-themes.md` (12 named automation seams), `supplemental.md`. Some include `_bom_raw.json`.

**The cross-job synthesis (what's common across all 4) is the next extraction step.**

## How to annotate

When you drop a file in, append a line to the **File index** below noting:

- **Representative** or **unusual**? AI will weight representative jobs heavily when inferring the 85% invariant. Edge cases need explicit flagging.
- **Complete** or **partial**? A BOM missing the controller section is different from a complete BOM.
- **Anything notable** AI shouldn't generalize? Customer rush job, vendor substitution, post-build correction, etc.

Without annotation, every job looks equally representative and the extraction will be wrong.

## File index

```
# Format:
# <path>                    [representative | unusual | partial]   notes

drawings/
boms/
config-sheets/
pos/
rfqs/
invoices/
order-acks/
jobs/
```

## Confidentiality

Raw documents (drawings, BOMs, config sheets, POs, RFQs, invoices, OAs) are gitignored at the dIRT root (`_intake/*/{drawings,boms,…,rfqs}/**`). Only this README, the `.gitkeep` markers, `context/`, `reference/`, and `extracted/` outputs commit. If a document needs review outside, copy it elsewhere — don't unignore.
