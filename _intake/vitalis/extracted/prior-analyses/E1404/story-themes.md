# E1404 — Candidate Story Themes

Named seams where automation should slot in, sourced to specific files/observations from E1404. One sentence per theme.

1. **Single source of truth for motor protection selections.** The Main BOM and `Motor_Protection_Selections_NG49-53-54.xlsx` disagree on MMP frame, MMP range, and contactor frame for the same motors — a tool that derives the motor-protection rows from the RFQ FLA values (and a coordination table) would eliminate the manual copy/paste error path. (Files: `E1404...xlsx` BOM rows R19/R21/R24/R26; `Motor_Protection_Selections_NG49-53-54.xlsx` Selections Summary.)

2. **Cluster-aware engineering reuse — siblings, not corpus.** `Motor_Protection_Selections_NG49-53-54.xlsx` is one document serving three near-identical Northgate stores; the reusable layer in this corpus is the **cluster of sibling jobs**, not a single global master, and tooling should learn to detect and surface clusters automatically by RFQ-feature similarity. (File: `Motor_Protection_Selections_NG49-53-54.xlsx` panel header lists NG49 / NG53 / NG54, all 460V/65kAIC/identical MT motor selection.)

3. **The "external" coordination spreadsheet is the real master.** The Motor Protection notes cite an `MMP_Contactor_Type_1_Coordination` spreadsheet as the authoritative source, but that file is **not in this job folder** — finding and surfacing organization-level masters (ABB UL coordination tables, NEC ampacity tables) is itself a discovery seam. (File: `Motor_Protection_Selections_NG49-53-54.xlsx` Selections Summary notes section R26.)

4. **Customer-intent capture from email is currently informal.** The Panel Notes sheet pastes a free-text customer email into a single cell (R6) carrying real engineering requirements ("RUN LIGHT - FAULT LIGHT - SWITCH from left to right", "LT switches above MT", "CO2 sensor", "spare I/O board"), and converting that paragraph into structured requirements automatically would close a fragile transcription loop. (File: `E1404...xlsx` Panel Notes R6.)

5. **Tag-prefix conventions are stable but not formalized.** Tag prefixes (CB, FU, T, UPS, BAT, PDB, GND, LT, RECP, PC, XM, SM, CM, PWS) carry feature semantics consistently across the BOM — promoting this to an enforced taxonomy would let auto-grouping tools generate the panel-feature view without human authoring. (File: `E1404...xlsx` BOM column B, all 70 rows.)

6. **Purple/red bar BOM convention is mechanically detectable.** The BOM uses fill colors `FF8E7CC3` (purple) and `FFE06666` (red) plus literal text "DO NOT COPY TO SUBMITTAL BOM BELOW THIS LINE" — automation can rely on this convention to safely extract the BOM region across all jobs in the corpus. (File: `E1404...xlsx` BOM - SCP-01 rows R12 and R84.)

7. **Below-bar fudges are structured and could be priced from a rates table.** The "fudges" below the red bar (wire by gauge, panel CNC cutouts, labels lump, hardware lump, UL, labor by activity) repeat across jobs and represent a small finite vocabulary that could be priced from a per-org rates table instead of typed per-job. (File: `E1404...xlsx` BOM rows R85–R114.)

8. **Clean BOM and IO map are unfilled placeholders.** The `Clean BOM` and `IO - Control Panel` tabs are populated only with headers / channel numbers — these are mechanical exports that could be generated from the SCP-01 BOM + the customer email's I/O hints, removing two manual data-re-entry steps. (File: `E1404...xlsx` Clean BOM 2 rows, IO - Control Panel 101 rows of empty channels.)

9. **Stale-template filenames leak.** The RFQ workbook is named `NG49 - MB0221 - EXXXX RFQ XXXXXX.xlsx` — the estimate-number placeholder `EXXXX` survived the assignment of the actual estimate E1404, suggesting filename hygiene is not being driven by the workbook contents and could be auto-rectified at save time. (File: `RFQ/NG49 - MB0221 - EXXXX RFQ XXXXXX.xlsx`.)

10. **Purchasing-log files live mis-shelved inside job folders.** The `Vitalis Control Parts Inventory.xlsx` is a personal stockroom/missing-parts log scoped to jobs E-1395 and E-1399 (not E-1404) but sits inside E1404's folder; recognizing "this file is not really about this job" and re-homing it (or surfacing it once as a global resource) is a small but high-value sweep. (File: `Vitalis Control Parts Inventory.xlsx` Missing Parts sheet Job Number column.)
