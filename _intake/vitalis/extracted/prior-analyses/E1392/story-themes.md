# Candidate Story Themes — E1392 / 4S Ranch

Named seams where automation should slot in, sourced to specific observations from this job. One sentence each.

1. **Pricing reconciliation across artifacts** — The proposal says $45,615.96, the main XLSX Panel Notes sheet says $43,751.25, and the BOM "Notes" date cell holds the same 43,751.25 figure where a date should live (see `xlsx-profile.md` and `process-docs.md`); a small tool that diffs the sell-price field across Panel Notes ↔ Proposal ↔ Order Ack would catch this in seconds.

2. **Job-ID drift detector across job-folder docs** — Panel tag MB0216 appears on every artifact except the PO Order Acknowledgement which says MB0217 (see `supplemental.md`); a per-job consistency check on tag, estimate#, PO# across XLSX/DOCX/PDF would flag that off-by-one before the doc leaves the desk.

3. **QC checklist regeneration from main XLSX** — `QC_Checklist_VITALIS.xlsx` in this folder describes a different panel entirely (460 V, 9 comp, 75 HP, Danfoss controller) yet ships unfilled in the E1392 folder (see `supplemental.md`); the checklist structure is great but its specs and per-compressor row count should be auto-populated from the BOM + Load Calc rather than copied as a stale template.

4. **Auto-emit a real Fab Packet from the main XLSX + DWGs** — The only fab-side artifact for this job is a 4-line traveler tag (see `process-docs.md`); the BOM (78 rows) + the Legend Plates sheet + the page-numbered DWG set are enough to generate a real per-compressor build packet (wire-pull list, torque table, sign-off boxes) automatically.

5. **Purple/red bar rule enforcement on BOM ingestion** — Rows above the purple bar at row 22 are headers and rows below the red bar at row 101 are fudges/labor/markup factors (see `xlsx-profile.md`); any automation that reads the BOM must honor those fill-color boundaries — and a one-time lint pass could move any "real" parts mistakenly outside the bars back inside.

6. **Wago small-TB quantity audit (low-confidence flag)** — Rows 88–99 contain ~200+ small Wago TB items at round-number quantities (51, 33, 35, 25 etc.) with no tags (see `feature-parts-association.md` and `part-feel.md`); flagging these as low-confidence everywhere they appear (proposal cost roll-up, pick list, packing slip) — and back-deriving the count from drawing terminal-strip metadata — would replace estimates with actual counts.

7. **Tag-to-drawing-page foreign key** — Every device tag in the BOM encodes its drawing page (e.g. `LT14131` = page 14 line 13), so a tag/page validator could check that every tagged BOM row maps to an existing DWG page (1..80) and that every drawing-page device has a matching BOM row.

8. **Empty "Clean BOM" sheet population** — The main XLSX has two sheets ("Clean BOM" and "Clean BOM & Pick List") that are header-only shells with zero populated rows (see `xlsx-profile.md`); these should auto-populate from the rows-between-bars on `BOM - SCP-01` so pickers/buyers have a real document to work from.

9. **Redline-from-photos workflow** — The customer redlines arrived as 6 iPhone HEIC photos in `Drawings/Red lines/`, then the drawing went through 11 plotted revisions (0 → K) in 30 days (see `lifecycle.md`); an OCR-or-vision-on-HEIC step that extracts the marked-up changes and pre-stages them as proposed DWG edits would compress that revision cycle.

10. **Auto-detect customer-furnished vs purchased BOM rows** — Rows 23–30 (the Copeland controller stack) are priced at $0 with PO column = "FI" / "stock" / "backordered" because the proposal explicitly says "Copeland E3 controller and I/O provided by Vitalis" (see `feature-parts-association.md`); a rule that flags any $0-priced BOM row as either customer-furnished, stock-pull, or missing-price would prevent cost-roll-up surprises.

11. **MPR/contactor count vs Load Calc compressor count check** — The BOM has 3 × MPW100 motor protectors but the Load Calc shows 2 across-the-line MT1 compressors (see `feature-parts-association.md`); a one-line invariant ("count(MPR) == count(across-the-line compressors) [+ spares declared]") would surface this kind of off-by-one immediately.

12. **Dimension-consistency check between proposal and BOM** — Proposal says the Rittal enclosure is 1400×800×500 mm; the BOM row for the Rittal SKU 8845500 unpacks to 1400×800×700 mm (see `feature-parts-association.md`); a numeric extractor over both docs comparing length/width/depth would have caught the 200 mm discrepancy before customer sign-off.
