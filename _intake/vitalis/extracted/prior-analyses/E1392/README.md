# E1392 — 4S Ranch Recon (Salvor Hardin, Head agent)

Customer: **Vitalis** (Plant 3 – Velocity, Kelowna BC, Canada)
Panel: **MB0216 — Roxsta G6 Rack Control Panel**, 208 VAC 3ph+E, SCCR 65 kAIC, NEMA 3R, Rittal 1400×800×(500 *or* 700) mm
Lifecycle: RFQ 03/16/26 → ship/invoice 05/13/26 (~8 weeks)

## Artifacts in this folder

| File | Subtask | One-paragraph summary |
|---|---|---|
| [`xlsx-profile.md`](xlsx-profile.md) | Profile main job XLSX (P1) | Sheet-by-sheet profile of `E1392 - 4S Ranch.xlsx`. The 8 sheets and their roles, BOM column schema, the purple-bar (row 22) and red-bar (row 101) locations, the 78 real BOM rows between them, plus 30+ rows outside-the-bars classified as removed-for-posterity, fudges (wire, duct, labels), labor estimates, and markup factors. |
| [`lifecycle.md`](lifecycle.md) | Map artifact lifecycle (P1) | Stage-by-stage walk of all 158 files. Two parallel "OLD" folders, 11 drawing revisions (0 → K) in 30 days, redlines arriving as 6 iPhone photos, no Fab Packet folder (only a 4-line traveler tag), QC checklist that's a customer-template not a job record. Full lineage diagram from RFQ to invoice. |
| [`process-docs.md`](process-docs.md) | Deep-read process docs (P2) | Summaries of the four process-flavored artifacts present (traveler tag, panel proposal final + 2 older drafts, QC template, and the in-XLSX mini-changelog). Every gap is called out: no fab steps, no QC results, no wire-change log, no narrative. The proposal scope (single line, $45,615.96, MB0216, 4-6 week lead time) is itemized. Flags the $1,864.71 price gap vs the XLSX. |
| [`feature-parts-association.md`](feature-parts-association.md) | Panel-feature → BOM parts (P2) | All 78 real BOM rows grouped by panel feature: main disconnect, PDB, per-compressor MPR/contactor sets, control xfmrs, UPS, energy meter, Copeland stack (customer-furnished), branch CBs, terminal blocks (Wago — low-confidence per project rule), and more. Includes a per-compressor pattern table showing the 5 compressors and their door-device counts line up cleanly (5 × XB5/XB4/legend plate). Open questions: MPR count off by 1, CR count off by 1, Rittal depth mismatch. |
| [`part-feel.md`](part-feel.md) | Part-feel pre-pass (P2) | Row-by-row first-pass intuition for what attributes drove each part choice (FLA, coil voltage, SCCR, frame size, etc.) with H/M/L confidence per row. Per the project rule, every Wago small-TB row is L (estimate). Surfaces the dominant selection drivers: coil voltage matching to control bus, trip ratings traced to Load Calc, SCCR-driven main breaker choice, 22 mm pilot-device family lock-in. |
| [`supplemental.md`](supplemental.md) | Profile supplemental XLSXs (P2) | Three supplemental XLSXs profiled: customer RFQ (with 3 high-value reusable reference sheets — FLA / Wire Ampacity / NEC 240.6A — and several `#VALUE!` errors), PO order acknowledgement (with the **MB0217 vs MB0216 mismatch** flagged), and the QC checklist which describes an entirely different panel (460 V / 9 comp / 75 HP / Danfoss). |
| [`story-themes.md`](story-themes.md) | Candidate story themes (P3) | 12 named seams where automation would slot in, sourced from concrete observations in this job: pricing reconciliation, job-ID drift detection, auto-generation of fab packet from XLSX + DWGs, purple/red bar rule enforcement, Wago-quantity audits, tag-to-drawing foreign-key validation, redline-from-photos workflow, customer-furnished part detection, count invariants vs Load Calc, dimension-consistency between docs. |

## Top flagged findings (emitted as events)

1. **QC checklist is for a different panel.** `QC_Checklist_VITALIS.xlsx` describes 460 V, 9 compressors, 75 HP, Danfoss AK-PC-782B, ABB XT6 700 A — not E1392.
2. **Panel tag MB0217 on the PO Order Acknowledgement** while every other artifact says **MB0216** — off-by-one.
3. **Proposal sell price $45,615.96 vs XLSX Panel Notes $43,751.25** — $1,864.71 discrepancy.
4. **BOM sheet "Notes" date cell row 3 contains 43751.249** (i.e. the sell price was pasted into the date column) — original-draft date is unknown.
5. **Rittal enclosure depth 700 mm (BOM) vs 500 mm (proposal)** — 200 mm discrepancy on the main enclosure dimension.

## Key constants & numbers (for downstream use)

- Real BOM row range: rows **23..100** on sheet `BOM - SCP-01` (78 rows).
- Excluded rows: 21 above purple, ~30 below red. See `xlsx-profile.md` for the per-row classification.
- Drawing pages: 80 (numbered 0..80 with one duplicate; see DWG inventory in `lifecycle.md`).
- Compressor inventory: 3 MT1 + 2 LT1 = 5 compressors. 2 VFD-fed (B1, G1), 3 across-the-line (B2, B3, G2).
- Load Calc: FLA 293.40, MCA 314.55, MOCP 399.15 A.
- Disconnect: ABB XT5N 400 A frame, adjustable 300–3000 A trip, with 500 MCM Cu/Al lug kit and rotary handle.
- Control bus: 120 VAC from 3 kVA xfmr; 24 VAC from 500 VA xfmr; 24 VDC from WAGO 5 A PSU + 1 kVA Phoenix UPS w/ 2× 7 Ah batteries.
- Per-compressor door pattern: 1× white pilot (RUNNING) + 1× red pilot (FAULT) + 1× 2-pos selector switch + 3× legend plates = 6 door devices × 5 compressors = 30, but BOM has 15 legend plates (3-line plates, one per device cluster of two).

## Open items / not completed

All 7 subtasks completed.
