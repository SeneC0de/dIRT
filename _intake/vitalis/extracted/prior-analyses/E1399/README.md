# E1399 — YCH Freecovery Roxsta G6 MB0206 — Analysis Index

**Customer:** Vitalis (Jacob Vanzella) · **Panel Tag:** MB0206 · **PO:** P-38256 · **Price:** $42,535.42 · **Ship:** UPS to Kelowna BC.
Analyst: Bel Riose, Head agent, dcad-plan. Charter: read absence as data — E1399 is the sparsest of the four packets.

| File | What it covers |
|---|---|
| [`lifecycle.md`](lifecycle.md) | Per-stage artifact map (RFQ → Proposal → PO → Drawings → Shipping → Invoice) with explicit "what's missing here vs other jobs." Empty Invoice folder; no QC folder; no Fab Packet; no Changelog; UPS label where a freight BOL is expected. |
| [`xlsx-profile.md`](xlsx-profile.md) | Main workbook profile: 8 sheets, purple bar at row 14 + red bar at row 89, 74 real BOM rows. IO sheet and Clean BOM views are unfilled templates. Live `=AI()` placeholder formulas left in WEG-package rows. |
| [`process-docs.md`](process-docs.md) | N/A — no process docs in this job. The absence is the finding. |
| [`supplemental.md`](supplemental.md) | Two non-main XLSXs: the RFQ intake template (still carrying `[JOB ID]` and `EXXXX` placeholders) and the PO acknowledgement sheet. |
| [`feature-parts-association.md`](feature-parts-association.md) | BOM grouped by panel-feature (main disconnect, distribution, motor protection MT/LT, control transformers, AK controller stack, interposing relays, door operators, etc). VFDs intentionally absent (customer-supplied). SPD also absent — flagged. |
| [`part-feel.md`](part-feel.md) | First-pass attributes driving each BOM-row's selection, with confidence ratings. Wago non-relay/non-PSU rows correctly marked low-confidence per charter. |
| [`story-themes.md`](story-themes.md) | 10 automation seams sourced to this job, including: missing submittal-view rendering, IO-sheet never populated, scope-changes-in-dead-rows, drawing-rev narrative locked in `.dwg`, unresolved `=AI()` cells, packet-completeness check across the lifecycle gaps. |

Events logged to the board: (1) IO sheet + Clean BOM views never generated; live `=AI()` placeholders in BOM. (2) Lifecycle absences — no QC, Fab, Changelog; A→G drawing revs with no narrative; UPS label only for a 72×60×18 enclosure. (3) Legend-plate count mismatch (18 in BOM vs 33 on Legend Plates sheet) and tag `PC54071` reuse on R15 + R17.
