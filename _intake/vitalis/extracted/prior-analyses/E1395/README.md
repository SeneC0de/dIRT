# E1395 — Lazy Acres — MB0219 — Analysis Index

Job: `E1395 - Lazy Acres - MB0219` · Customer: Vitalis · Panel tag: `SCP-01` · PO: `P-38262` · Drawing rev at hand-off: `L` (2026-05-12).

Built by **Gaal Dornick** (Head agent), director board `dcad-plan`.

## Artifacts

| File | What it contains |
|---|---|
| [`lifecycle.md`](./lifecycle.md) | Stage-by-stage walk of every folder in the job dir (RFQ → Proposal → PO → Drawings → Fab Packet → QC → Shipping → Invoice → OLD). Notes which folders are empty, where the project was renamed from "Vitalis Northgate 11", how revisions are tracked, and the dependency ordering between artifacts. |
| [`xlsx-profile.md`](./xlsx-profile.md) | Profile of the main `E1395 - Lazy Acres - MB0219.xlsx`. Sheet inventory, column layout, location of the purple bar (row 13) and red bar (row 85), the 71 in-bar BOM items, and detailed exclusion notes for rows above/below the bars (labor rollup, wire fudges, dead enclosure options). |
| [`process-docs.md`](./process-docs.md) | Deep read of Fab Packet, QC Program, Danfoss Wire Changes, and Job Tag docx files. Distills implicit shop flow, calls out gaps in each shell, and decodes the Danfoss wire-move redline as a cascading IO rebalance. |
| [`supplemental.md`](./supplemental.md) | Profile of `Changelog.xlsx` (a misnamed *parameter-driver catalog* per drawing sheet — 125 parameter labels, no values) and a pointer to the PO acknowledgement XLSX. |
| [`part-feel.md`](./part-feel.md) | Row-by-row first-pass guesses about what attributes drove each BOM part selection, with H/M/L confidence. Identifies dominant patterns (compressor-count signature, VFD asymmetry) and flags MT1-2 vs MT3-4 trip-rating mismatch. |
| [`feature-parts-association.md`](./feature-parts-association.md) | Groups the 71 BOM rows by panel feature (Enclosure, Main disconnect, PDB, MT circuits, LT circuits, HOA, Transformers, UPS, Danfoss stack, Climate, Relays, etc.). Calls out features absent from BOM but referenced elsewhere (VFDs, safety relay, HMI). |
| [`story-themes.md`](./story-themes.md) | 10 named seams where automation should slot in, each sourced to a concrete observation from this job. |
| `_bom_raw.json` | Internal: dumped BOM rows 14-84 as JSON for traceability. |

## How to read these together

1. Start with **`lifecycle.md`** to understand what *exists* in the job folder and what's missing.
2. Read **`xlsx-profile.md`** to understand the main workbook's structure and the rules used to extract the 71 BOM rows.
3. Read **`process-docs.md`** alongside **`feature-parts-association.md`** — the process docs tell you *what the shop does*, the feature-parts table tells you *with which parts*, and disagreements between them are the most interesting findings.
4. **`part-feel.md`** is the row-level reference; consult it when you need to know why a specific part was likely chosen.
5. **`story-themes.md`** is the only forward-looking artifact — it points at where automation could plug in.

## Cross-cutting events logged

- Load Calc rows 11-13 part-number drift (`CDS351B` vs `CDS301B`) vs the customer RFQ.
- `IO - Control Panel` sheet essentially empty (2/1000 DI rows populated) while drawings claim to be matched to the IO list.
- Customer-requested 100 kA SCCR downgraded to 65 kAIC, undocumented except as a strikethrough inside the pasted email body.
- `Changelog.xlsx` is misnamed — it is a parameter catalog, not a per-job log.
- Photo-count drift between Fab Packet (2) and QC Program (7).
- Job Tag traveler shows `PO# P-XXXXX` un-substituted after shipment.
- MT1-2 breakers 250 A vs MT3-4 breakers 200 A despite identical FLAs.
- Danfoss module swap (103A → 101A) in the wire-changes doc but BOM still shows 2× 103A.
- VFDs absent from BOM rows 14-84 despite being referenced everywhere else.
- Safety relay, HMI (MMIGRS2), EKE 1C superheat controllers all absent from in-bar BOM despite drawing-revision / inventory references.
