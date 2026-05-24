# E1395 - Lazy Acres - MB0219 — Artifact Lifecycle Map

*Walk of every folder in the job dir. Lifecycle stages are inferred from folder names + filenames.*

Observed top-level layout of `inputs/jobs/E1395 - Lazy Acres - MB0219/`:

```
Changelog.xlsx                            (parameter-driver catalog, NOT a per-job changelog — see Note A)
Danfoss Wire Changes.docx                 (after-engineering redline of wire numbers between Danfoss modules)
Drawings/                                 (active + Old subfolder)
E1395 - Lazy Acres - MB0219.xlsx          (main job workbook: BOM, IO, Load Calc, Notes)
E1395 - dC Job Tag for Traveler.docx      (physical traveler tag — 2 page placeholders, PARTS + FABRICATION)
E1395 Fabrication Packet.docx             (fab checklist / SOP shell)
E1395 dC Quality Control Program.docx     (QC SOP — generic, lightly job-specific)
Invoice/                                  (EMPTY)
OLD/                                      (early proposal under prior project name "Vitalis Northgate")
PO/                                       (P-38262 acknowledgement + PO)
Proposal/                                 (two dated revisions + OLD subfolder)
Shipping/                                 (Delivery slip + UPS shipping labels — implies physical shipment happened)
```

## Stage-by-stage inventory

### 1. RFQ / Inception
- No explicit RFQ file. The original RFQ content survives as **plain text inside `Panel Notes` sheet of the main XLSX** (the customer email pasted into cell starting "Hey guys / In today's meeting…"). That's the project genesis record.
- `OLD/` folder contains the **pre-renaming proposal** under the codename "Vitalis Northgate 11 Panel (100kA SCCR)":
  - `E1395 - Vitalis Northgate 11 Panel (100kA SCCR) Proposal 041326.pdf` (2026-04-13)
  - `E1395 - Vitalis Northgate 11 Panel (100kA SCCR) Proposal 041526.docx` and `.pdf` (2026-04-15)
- Customer originally asked for **100 kA SCCR**; the panel was actually built to **65 kA SCCR** (see Panel Notes sheet cell B15). The "100k" in the email is crossed out and replaced with "65k" — that decision lives only in the email body, not in any change record.

### 2. Proposal
- `Proposal/`
  - `E1395 - Lazy Acres - MB0219 Panel Proposal 041526.docx/.pdf` (2026-04-15) — first proposal under the new project name.
  - `E1395 - Lazy Acres - MB0219 Panel Proposal 042226.docx/.pdf/v2.pdf` (2026-04-22) — revised proposal, including a `v2 042226.pdf` co-existing with the un-versioned 042226 PDF (filename collision risk: two PDFs same date, different content).
  - `Proposal/OLD/E1395 - Lazy Acres - MB0219 Panel Proposal 042226.pdf` — an older copy of the 042226 proposal nested inside OLD.
- Proposal docx is mostly boilerplate T&Cs; the technical content is one paragraph listing the 4 MT + 3 LT Dorin compressors and their FLAs. Identical compressor list also appears in the Panel Notes sheet (the customer email).

### 3. PO
- `PO/`
  - `Purchase Order - P-38262.pdf` — customer-issued PO.
  - `PO# P-38262 - Order Acknowledgement - Purchase order.pdf` — dC's acknowledgement.
  - `PO# P-38262 - Order Acknowledgement.xlsx` — same acknowledgement, editable form.
- PO number `P-38262` also written into the Shipping packet filename `P-38262 P3 RES 00110 UPS Labels.pdf` — confirms PO→shipping linkage. The internal panel tag is `SCP-01` (Panel Notes B13).

### 4. Drawings
- Active drawings live in `Drawings/DWGs 5-8-2026/` — 75 `.dwg` files plus AutoCAD Electrical project files (`.aepx`, `.wdp`, `.wdt`, `.wdtitle.wdl`).
- Drawing set is **the most decomposed I've seen**: per-cover-sheet, 3-phase, 120 VAC dist, per-circuit (MT1 C1..C4, LT1 C1..C3), oil-sep, gas cooler, pressure regs, per-Danfoss-module sheets, motor protection, BOM, layout details (2 separate sets), Danfoss page, door layout.
- Drawings have a **published-PDF rendering** at the parent level: `E1395 - LAZY ACRES - 5-12-2026 - L.docx` and `.pdf`. The `-L` suffix is the **revision letter** (currently L). Earlier revisions A through K all live in `Drawings/Old/` as PDFs.
- `Drawings/Old/` also has folders `DWGs 2-27-2026/` and `DWGs 4-21-2026/` (DWG source archives at older revisions).
- Revision tracking lives **embedded inside the published docx** as a 107-row revision table (Lazy Acres Vitalis) — engineer initials = "HG" throughout. Captured changes include: "VITALIS REDLINES…", "MOVED DANFOSS WIRING TO MATCH IO LIST", "FIXED G3 CONTACT TO BE MOTOR", "DISCONNECT AMPERAGE, LAYOUT AND BOM UPDATED 3 PHASE WIRE SIZING, REPLACED FU7011 WITH CB 7011", "ADDED IN SAFETY RELAY", "ADDED PWS7151 TO LAYOUT AND BOM, FIXED 24VDC3 NOT EXISTING", etc.

### 5. Fab Packet
- `E1395 Fabrication Packet.docx` — a **shell** (caveat #4): heading-driven checklist (Pre-Fab → Pre-Wiring → Wago Rail Exports → Fab → Testing → Packaging → Notes). It is *organized* but mostly bullet-point reminders; almost no per-job parameters. Empty section "Wago Rail Exports" (heading only — no actual exports). One job-specific datum: P59 "UPS and Battery not in BOM because we are sizing them per customer requests" — this is the only place that note lives.
- `E1395 - dC Job Tag for Traveler.docx` — two title pages (PARTS, FABRICATION), each with the placeholder `PO# P-XXXXX` (un-substituted). The actual PO is P-38262 — this template was never filled in.

### 6. QC
- `E1395 dC Quality Control Program.docx` — **generic SOP**, not job-tailored. Boilerplate sections (Defined Terms, Calibration, System Setup, As-Built BOM procedure, Warnings & Shutdowns, Appendix). The "As-Built BOM" section is the most concrete: take 7 photos (inside panel, inside door, outside door, 4 sides), justify drawing BOM against every component, blue-check installed items, red-mark deltas, save into "As Built/Photos". *No `As Built/` folder yet exists in the job dir* — implying QC handoff for THIS job hasn't been completed, or the As-Built was never produced.
- Section "System Setup & Configuration" still contains placeholder text "Setup is done by access level…" — template not customized.

### 7. Shipping
- `Shipping/Delivery Slip - dAPP Controls LLC - P3_RES_00110.pdf`
- `Shipping/P-38262 P3 RES 00110 UPS Labels.pdf`
- Internal shipment ID format `P3_RES_00110` — appears nowhere else in the corpus. Linkage to PO P-38262 only via filename.

### 8. Invoice
- `Invoice/` — **EMPTY**. Either invoicing not yet done, or invoices live in QuickBooks and never get filed back here.

### 9. OLD (top-level)
- See RFQ section. Contains the pre-rename Vitalis proposals. Behavior: when project was renamed, OLD docs were preserved under the original codename, the new proposals re-issued under the new name in `Proposal/`. **The rename itself is not documented anywhere as a change event** — only inferable by comparing filenames.

## Ordering / dependency observations

1. **Customer email → Panel Notes sheet → Load Calc sheet → Drawings → BOM**. Compressor list is identical across the first three; it's a manually-propagated parameter.
2. **Changelog.xlsx is mis-named**. It's not a history log — it's a *parameter-change registry per drawing sheet* (SH2..SH5 = drawing sheets 2-5). Each row enumerates the dimensions that vary between jobs ("MT1C1 Breaker Rating", "T2 Fuse Holder SCCR", etc). This is a **template parameterization spec, not a per-job artifact** — almost certainly copied unchanged into every job folder. Cross-check the other jobs to confirm.
3. **Two parallel revision streams** exist for drawings: the named DWG snapshots (`DWGs 2-27-2026`, `DWGs 4-21-2026`, `DWGs 5-8-2026`) and the revision-letter PDFs (A through L). The DWG-folder dates don't line up with the letter revisions cleanly — Old PDFs span 2-23 through 5-12, but only 3 DWG folders archive. Implies the team archives DWGs less often than they re-publish PDFs.
4. **Job Tag (Traveler)** carries `PO# P-XXXXX` placeholder — never substituted. Either the traveler is filled in on paper after printing, or this is a stale template.
5. **Invoice + As-Built absent** = the job is partially closed in the file system. Shipping completed (labels exist), but downstream artifacts (invoice, as-built BOM, photos) are not present.

## Note A — Changelog.xlsx interpretation

Despite the filename `Changelog.xlsx`, the 4 sheets `SH2/SH3/SH4/SH5` contain ordered lists like:

```
Change 1   Disconnect Amperage
Change 2   Disconnect Part Number
Change 3   Disconnect SCCR
...
```

There is no date, no author, no before/after. These are the *kinds of things* that change from job to job, scoped per drawing sheet. Best interpretation: this is a **drawing parameterization manifest** that the engineer uses as a checklist when adapting the master drawing set to a new job. If true, it's evidence of a partial-but-not-formal template system (see story-themes.md).
