# E1404 — Northgate 49 MB0221 — Analysis Index

Agent: **Hari Seldon** (Head, dcad-plan). Feature: `qfJACspuV3M8JO1lkCKg`. All 7 subtasks complete.

## Files

- **`lifecycle.md`** — Folder-by-folder lifecycle map. Job is arrested at the proposal stage: RFQ + engineering workbook + customer proposal present, but Drawings folder is empty and no fab packet exists. Documents what's missing vs a fuller packet.

- **`supplemental.md`** — Priority-1 deep dive on the two supplemental XLSXs. **Refutes** the hypothesis that `Vitalis Control Parts Inventory.xlsx` is a corpus-wide master parts list (it is a small personal stockroom + missing-parts log referencing jobs E-1395 / E-1399, not E-1404). Profiles `Motor_Protection_Selections_NG49-53-54.xlsx` as a cluster-level engineering selection doc serving three sibling Northgate jobs, and notes it cites an external `MMP_Contactor_Type_1_Coordination` spreadsheet as the real upstream authority.

- **`xlsx-profile.md`** — Profile of the main job workbook (`E1404 - Northgate 49 MB0221.xlsx`). Six sheets; only Panel Notes, BOM - SCP-01, and Load Calc are populated; Clean BOM and IO - Control Panel are placeholder shells. Purple bar at R12, red bar at R84 (with literal "DO NOT COPY TO SUBMITTAL BOM BELOW THIS LINE" text), 70 real BOM rows between them. Flags the MS165/MS132/AF-frame disagreement with Motor Protection supplemental and the SCP-01 vs RCP-01 panel-code drift.

- **`process-docs.md`** — Verdict: **N/A — no process docs in this job beyond the customer-facing proposal.** No fab packet, no QC, no wire-change log. Consistent with proposal-stage arrest. The closest thing to a change-log is a single row on the BOM sheet ("MB / 2026-05-01 / Original genuine draft").

- **`part-feel.md`** — First-pass attribute reasoning for each of the 70 real BOM rows. 36 high, 18 medium, 16 low confidence — low confidence concentrated on (a) the four MMP/contactor rows that disagree with the Motor Protection supplemental and (b) Wago non-relay/PSU rows that are estimates by upstream practice.

- **`feature-parts-association.md`** — The 70 BOM rows grouped by panel feature (enclosure, main breaker, MT branches, LT branches, pack controller, system manager, I/O bank, Danfoss bus PSU, phase monitor, PDBs, ground, control transformers, control fuses, UPS+battery, Ethernet switch, service outlet, door indicators, door selectors, nameplates, branch CBs, secondary 24 V supply, interposing relays, mini-contactors, panel HVAC, terminal blocks). Includes open questions on missing VFD parts and the implicit CO2 sensor.

- **`story-themes.md`** — 10 named seams for automation: single-source-of-truth coordination for motor selections, cluster-aware reuse, external master discovery, structured intake from customer email, tag-prefix taxonomy, bar-fill BOM region detection, fudges as a priced vocabulary, auto-generation of Clean BOM and IO map, filename hygiene, and re-homing mis-shelved files like the Vitalis Parts Inventory.

## Headline findings

1. **Vitalis Parts Inventory is NOT a master.** It is a personal purchasing log scoped to jobs E-1395 / E-1399 — explicit evidence (file size ~35 rows, only 2 manufacturers in stock list, references two prior jobs only).
2. **MS165 / MS132 / AF-frame sizing disagrees between the Main BOM and the Motor Protection supplemental** for the same motors in the same panel — a concrete human-authored contradiction worth raising before this job ships.
3. **The real reusable artifact is at the cluster level** (`NG49-53-54` Motor Protection doc) and the real master likely sits in an unfound `MMP_Contactor_Type_1_Coordination` spreadsheet referenced in the notes — search the rest of the corpus for it.

## Events logged

- `FAg9TB0pxb7PSHowneFY` — Vitalis Parts Inventory is not a master.
- `Q1XYRvKaU4Qo7ypnINRe` — MS165 sizing contradiction between Main BOM and Motor Protection Selections.
- `5vO3nSe3EC1dXB98eUGQ` — Panel code drift (SCP-01 vs RCP-01) and customer naming inconsistency (Vitalis vs Classic).
- `wrv0wy5FGPqnQcqtQISi` — VFD parts missing from BOM despite VFD=True on MT1 and LT1 in the RFQ.

## Subtasks (all complete)

| Priority | Subtask | Output |
|---|---|---|
| 1 | Profile the main job XLSX | `xlsx-profile.md` |
| 1 | Profile supplemental XLSXs | `supplemental.md` |
| 1 | Map artifact lifecycle | `lifecycle.md` |
| 2 | Deep-read process docs | `process-docs.md` |
| 2 | Part-feel pre-pass | `part-feel.md` |
| 2 | Panel-feature → BOM parts association | `feature-parts-association.md` |
| 3 | Candidate story themes | `story-themes.md` |
