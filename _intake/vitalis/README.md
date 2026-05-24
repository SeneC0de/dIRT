# Vitalis — Document intake

Raw documents from Vitalis panel jobs land here. AI ingests them and produces three derivative files in `extracted/`, which then seed dCAD / dPART / dERP for the panel→PO pipeline.

## Pipeline

```
_intake/vitalis/{drawings,boms,config-sheets,pos,invoices,order-acks,jobs}/
        │
        ▼  (AI extraction pass)
_intake/vitalis/extracted/
        ├── panel-template.yaml        ← the 85% invariant panel
        ├── selection-rules.yaml       ← the 15% variable (config-sheet logic as data)
        └── parts-additions.json       ← anything missing from dPART's catalog
        │
        ▼  (review + merge, one ADR per phase)
dCAD.Configuration / dPART seed / dERP Part catalog
```

Once extraction has been reviewed and merged downstream, this folder stops being load-bearing. It's source material, not runtime data.

## Folder map

| Folder | What goes here | Examples |
|---|---|---|
| `drawings/` | Panel schematics, layout, dimension, GA, single-line | `.pdf`, `.dwg`, `.dxf`, `.png` |
| `boms/` | Historical BOMs in any format | `.xlsx`, `.csv`, `.pdf` |
| `config-sheets/` | Selection criteria — "if input X then choose Y" | sizing rules, controller-selection guides |
| `pos/` | POs you issued to vendors | one per vendor per job |
| `invoices/` | Vendor invoices — validates part numbers + pricing | one per vendor per shipment |
| `order-acks/` | Order acknowledgements from vendors | for cross-check vs PO |
| `jobs/<job-id>/` | **Preferred shape:** one folder per past job, bundling drawing + BOM + config sheet + PO together | `jobs/2024-vitalis-mtr-3/` |
| `extracted/` | AI-derived outputs (this commits to git) | `panel-template.yaml`, etc. |

## Annotation — the most important step

When you drop a file in, append a line to the **File index** below noting:

- **Representative** or **unusual**? AI will weight representative jobs heavily when inferring the 85% invariant. Edge cases need explicit flagging or they distort the template.
- **Complete** or **partial**? A BOM missing the controller section is different from a complete BOM.
- **Anything notable** AI shouldn't generalize? Customer rush job, vendor substitution, post-build correction, etc.

Without annotation, every job looks equally representative and the extraction will be wrong.

## Controller variability — explicit scope

Per Randall: "every panel is 85% the same except the controller." That **controller** dimension spans two axes:

1. **Refrigeration controller family** — Danfoss AK vs Copeland CC vs other. dCAD already targets Danfoss + Copeland.
2. **HMI/PLC selection on top** — separate hardware stack feeding the same refrigeration logic.

`selection-rules.yaml` must capture both. The `panel-template.yaml` invariant ends where these two start.

## File index

Add an entry per file (or per job folder) as you drop them in. Brief is fine.

```
# Format:
# <path>                    [representative | unusual | partial]   notes

drawings/
boms/
config-sheets/
pos/
invoices/
order-acks/
jobs/
```

## Confidentiality

Raw documents (POs, invoices, drawings, config sheets) are gitignored at the dIRT root (`_intake/*/{drawings,boms,…}/**`). Only this README, the `.gitkeep` markers, and `extracted/` outputs commit. If a document needs review outside, copy it elsewhere — don't unignore.
