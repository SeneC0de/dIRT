# E1399 — Candidate Story Themes

Seams where automation slots in, sourced from THIS job. Per charter, the absences in E1399 (vs richer packets) are theme fodder, not exceptions.

1. **The "submittal view" never gets generated.** The main XLSX has `Clean BOM` and `Clean BOM & Pick List` as fully-templated but empty sheets. The author works in `BOM - SCP-01` (purple/red bar layout) and downstream consumers never get the rendered handoff. *Automation seam:* a single transform that reads rows-between-bars and emits the two clean views (and a CSV for purchasing). Source: `xlsx-profile.md` § Sheet Inventory.

2. **IO map never makes it from drawings into structured data.** The `IO - Control Panel` sheet contains only DI/DO channel scaffolding — no descriptions, signal types, or voltages. Yet drawing pages 67-74 are seven full Module pages plus a Com Module. *Seam:* extract IO from the AutoCAD `.aepx` project (which knows the Danfoss AK XM channel assignments) → populate the XLSX IO sheet → flow into wire-pull list. Source: `xlsx-profile.md` § IO; drawings inventory in `lifecycle.md`.

3. **Scope changes live in dead BOM rows, not a changelog.** Three alternate motor-protection topologies sit below the red bar (ABB MS165/AF block at R102-R121; WEG package variant A at R136-R144; pre-purple stragglers at R11-R12). No prose anywhere explains which was picked or why. *Seam:* a "decision log" that pins each topology to a date + rationale + signoff; auto-derive the dead-row set as evidence. Source: `xlsx-profile.md` § Rows Excluded.

4. **Drawing-rev narrative is locked inside the binary.** Submittal PDFs rev A→G in 8 days (5/5 → 5/13) with zero textual changelog in the packet; the only diff source is the 38 MB `0-REV TRACK.dwg`. *Seam:* an AutoCAD-Electrical rev-block exporter that emits a markdown changelog per rev. Source: `lifecycle.md` § Drawings.

5. **`=AI()` placeholder formulas survived to a shipped sheet.** Rows R31, R33, R34, R36, R38, R39, R40 in the active BOM region have live `=AI("Fill an appropriate value...")` formulas in Description/Manufacturer cells. The auto-fill never resolved and was never caught. *Seam:* a lint pass on the BOM that fails CI if any cell has an unresolved `=AI(...)`, broken formula, or `#VALUE!`. Source: `xlsx-profile.md` § Real BOM Observations.

6. **Job identifiers don't propagate cleanly from intake.** The RFQ workbook still carries `[JOB ID]` and `EXXXX` placeholders in cells and filename. The number `E1399` only stabilizes once the proposal is generated. *Seam:* a rename + cell-rewrite step on RFQ-template instantiation that takes `{estimate_id, panel_tag, customer}` and binds them everywhere at once. Source: `supplemental.md` § RFQ.

7. **Counts don't reconcile across views of the same content.** BOM row 87 buys 18 legend plates; the Legend Plates sheet lists 33. Either side could be right, neither is checked. Similarly, tag `PC54071` is used twice in the BOM (R15 and R17). *Seam:* a cross-sheet integrity check — tag uniqueness, BOM-qty vs derived-from-tag-list count, Legend-Plates-row vs BOM-plate-qty. Source: `feature-parts-association.md`, `part-feel.md`.

8. **What's missing is missing everywhere.** No QC folder, no Fab Packet, no Changelog, no submittal docx checked into PO/, no invoice, no freight BOL for a 72×60×18 enclosure (only a UPS small-parcel label). This is not "the next job will have them" — the *packet shape itself* doesn't require them, so they aren't present in any job at the moment of ship. *Seam:* a packet-completeness check that asserts a required-folder/file set at "job closed" — and demotes the job-state until they're filled. Source: `lifecycle.md` § Stage 6/7 and § Cross-stage.

9. **The same Wago tier is always priced as estimate.** The charter says it; the BOM confirms it — TBs, end stops, jumpers, rail are sized by rule of thumb (round numbers: 25, 35, 51, 33). *Seam:* a Wago auto-sizer that consumes the wire schedule (which we don't have yet — see theme 2) and emits exact quantities — closing two themes with one input.

10. **PO scope drift goes uncaptured between proposal revs.** Two proposals (033126 and 042326) almost identical in size, no diff doc, no rationale. The accepted price matches the second one. *Seam:* a proposal-diff macro that emits a "what changed since last rev" block at the top of each new proposal — auto-generated from the prior version. Source: `lifecycle.md` § Proposal.
