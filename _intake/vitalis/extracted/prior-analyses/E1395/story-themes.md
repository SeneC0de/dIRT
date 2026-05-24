# E1395 — Candidate Story Themes

Named seams where automation should slot in, each sourced to a concrete file/observation in *this job*. One sentence per theme. E1395 has the richest packet, so these seams are visible here even when they will recur on the other 3 jobs.

1. **Drawing-parameter catalog → templated drawing generation.** `Changelog.xlsx` lists 125 "Change N → parameter description" entries per drawing sheet (SH2..SH5) with no values; it's a partial template-engine spec missing a data layer. Automating the drawing pack so each parameter is bound to a value from the BOM / Load Calc would eliminate the manual revision passes that currently produce the `A..L` revision lettering in `Drawings/Old/`.

2. **BOM and IO-list drift across artifacts.** The drawings revision tracker says "MOVED DANFOSS WIRING TO MATCH IO LIST" and "ADDED IN SAFETY RELAY" and "ADDED PWS7151 TO LAYOUT AND BOM", yet the `IO - Control Panel` sheet in the main XLSX is ~empty and no safety-relay line exists in the BOM rows 14-84. A canonical, machine-checked IO-and-BOM source feeding both drawings and workbook would close this gap.

3. **Engineering redlines as structured deltas, not paragraph dumps.** `Danfoss Wire Changes.docx` is 23 plain-text lines encoding a module swap + IO rebalance — exactly the kind of artifact that should be a structured table (from-module / from-term / to-module / to-term / wire#) merged into a wire-list database that the drawings auto-rebuild from.

4. **Quantity-from-circuit-count derivation rule.** The BOM shows the same multipliers everywhere — qty 7 = (4 MT + 3 LT) for HOA/pilots/legends/6 A coil CBs; qty 4 = MT for main contactors+lugs+covers; qty 3 = subset-minus-VFD for aux contacts on LT2/3 and MT2/3/4. A rule engine that pre-fills BOM quantities from the circuit list (Panel Notes → BOM) would catch the MT1-2 vs MT3-4 trip-rating asymmetry and the "qty 2 vs qty 3" aux-block decisions automatically.

5. **The IO list is missing where it should be authoritative.** `IO - Control Panel` sheet has 2/1000 DI and 2/1000 DO rows filled. Either the drawings own the IO list (and the workbook is dead) or the workbook should own it (and the drawings drift). Picking one source of truth and enforcing it is a quick, high-leverage seam.

6. **Job-Tag template never substituted.** `E1395 - dC Job Tag for Traveler.docx` still says `PO# P-XXXXX` after the job shipped (actual PO is P-38262). A trivial print-time substitution from the job metadata in `Panel Notes` would eliminate the entire class of "the traveler is still a template" defects.

7. **As-Built BOM workflow specified but unexecuted.** The QC SOP describes a paper-then-digital As-Built BOM procedure with 7 specific photos and a blue-check/red-mark redline pass — but the `As Built/` folder doesn't exist in this job. Automating photo capture (e.g. shop-floor tablet that names and files photos) would convert this from a manual SOP into a measurable hand-off step.

8. **Wago small-part quantities are unowned guesses.** Caveat #3 acknowledges the small-TB / end-stop / marking / rail counts are estimates. A drawing-driven take-off (each schematic terminal symbol increments its part-number tally) would convert eight rows of low-confidence quantity into derived quantities.

9. **Photo-count and SOP drift between sister documents.** The Fab Packet says "interior and exterior" (2 photos); the QC Program says 7 specific shots. A single SOP source of truth (and a checklist instrument that enforces it) would collapse this kind of drift, which appears between every pair of docs in the corpus.

10. **Lifecycle gaps are silent.** `Invoice/` and `As Built/` are empty and there's no event marker saying "Invoice pending" or "As-Built TODO." A lifecycle-state model (RFQ → Proposal → PO → Drawings → Fab → QC → Ship → Invoice → As-Built) with required artifacts per state would expose where a job is actually parked, rather than treating folder-empty as ambiguous.
