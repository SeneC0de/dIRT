# Process Docs — E1392 / 4S Ranch

Goal: summarize Fab Packet, QC Program, Changelog, Wire Changes, and process-narrative docs present in this job. Per project rule: fab packets are typically incomplete shells — note their gaps explicitly. Absence is not signal.

## What's actually here

This job has **no Fab Packet folder**, **no Wire Changes log**, and **no narrative/process docs** beyond two small Word files at the top level. The only process-flavored artifacts are:

1. The traveler Job-Tag docx (top level)
2. The Panel Proposal docx/pdf (top level + OLD/ supersedes)
3. The QC checklist (`QC/QC_Checklist_VITALIS.{pdf,xlsx}`) — Vitalis-branded template, not E1392-specific
4. The in-XLSX "Initials / Date / Notes" mini-changelog at the top of the BOM sheet

I'll cover what each one actually contains.

---

## 1. `E1392 - dC Job Tag for Traveler.docx`

**What it is:** a printable single-page traveler/tag that gets attached to the physical job folder or panel during fab.

**Contents (all body text shown):**
- "E1392 - 4S Ranch"
- "Roxsta G6"
- "Parts"
- "PO# P-37066"

That's the whole document — 4 short text lines. No build instructions, no torque specs, no wire-list, no sign-off boxes, no signature lines, no checklist. This is the closest thing this job has to a "fab packet" and it is in fact a label, not a packet.

**Gaps (explicit):**
- No fab-step checklist
- No layout/wiring diagram callouts
- No sign-off boxes for assembler / QC / shipping
- No torque table, no panel-cutout schedule
- No spare-parts list (despite "Parts" appearing as a heading word)
- No revision/date stamp

**Verdict:** treat as a name tag, not a process doc. The fab packet for this job is, in effect, absent.

---

## 2. Panel Proposal — `E1392 - 4S Ranch Panel Proposal 033126.docx` (final 03/31/26)

**What it is:** the customer-facing sales document for the panel scope.

**Header / metadata:**
- Date: Mar 31, 2026
- Estimate # 1392
- Attn: Jacob Vanzella (Vitalis)
- Subject line: "E1392 - 4S Ranch Roxsta G6 Panel - Proposal"
- Lead time stated: 4–6 weeks upon receipt of PO

**Scope (single-line item, Line 1):**
- Qty 1 - MB0216 - Roxsta G6 Rack Control Panel
- Incoming power = 208VAC, 3-phase+E, 60Hz
- SCCR = 65 kAIC
- Rittal enclosure: 1400 mm × 800 mm × 500 mm S/D, NEMA & UL Type 3R / 12 / 13, w/ 2 side panels + back panel
- UL 508A & cUL compliant, assembled & tested
- PDF drawing package (schematic, layout, BOM) — 2 sets
- Copeland E3 controller and I/O **provided by Vitalis** (customer-furnished)
- Submittal drawings
- Energy meter w/ Rogowski coils
- Ethernet switch
- UPS w/ battery backup
- Add an 88 I/O board to the Copeland bus with spare terminals provided for the I/O
- **Unit price: $45,615.96**

**Terms & Conditions (boilerplate, P19–P25):** Net-30 payment, 30-day quote validity with passthrough escalation, partial-delivery rights, 12-mo-after-install / 18-mo-after-mfg warranty, liability limited to refund, no responsibility for engineering/installation/programming on customer-spec panels, cancellation only with consent + charges.

**Gaps:** no wiring scope statement, no commissioning scope, no FAT/SAT procedures, no documentation deliverables beyond "2 sets of PDFs", no acceptance criteria, no spares quantity. The doc is purely a sales/scope sheet — not a process document and not intended to be one.

**Lineage of older drafts in `OLD/`:**
- `E1392 - 4S Ranch Panel Proposal 031926.pdf` — first draft (03/19, 200 KB)
- `E1392 - 4S Ranch Panel Proposal 032026.pdf` — next-day revision (03/20, 213 KB)
- The size jump from 031926 → 032026 (+12 KB) suggests scope language was added or images/header changed; the final 033126 version is the same size as the 032026 version (212 KB) — content footprint stable from 03/20 onward.

**Anomaly flagged:** the proposal unit price is **$45,615.96**, but the main XLSX `Panel Notes` sheet records the panel sell price as **$43,751.25**. Difference: $1,864.71 (~4.1 % higher in the proposal). Could be a markup added at proposal time, a rounding/holdback, or a stale XLSX. Worth confirming.

---

## 3. QC Program — `QC/QC_Checklist_VITALIS.pdf` and `.xlsx`

**What it is:** a Vitalis-branded QC checklist. Filename is keyed to the **customer (VITALIS)**, not to E1392 — strongly suggests it's a customer template reused for every Vitalis panel rather than a populated, job-specific record.

The XLSX form is profiled in `supplemental.md`. The PDF (70 KB) is the printable companion of the same form.

**Gaps:**
- No QC results / pass-fail marks visible in the filename or the spreadsheet check (a populated job-specific QC record would typically be `E1392_QC_filled.pdf` or similar).
- No FAT report, no hi-pot/megger test results document, no continuity log.
- No nonconformance log (`NCR`s).

**Verdict:** unfilled (or template-form) customer-furnished QC checklist. Treat as a process **input**, not a process record.

---

## 4. In-XLSX mini-changelog (BOM sheet, rows 1–8)

The BOM sheet `BOM - SCP-01` has a 3-column "Initials / Date / Notes" header at rows 2–8. Only one entry exists:

| Row | Initials | Date | Notes |
|---|---|---|---|
| 3 | (blank) | 43751.249 *(see flag)* | "Original genuine draft" |

**Gaps:** no subsequent rev entries, no author initials. Only one row was ever filled in. If this XLSX has been edited since 03/18 (Estimate date on Panel Notes), the changes are untracked.

**Anomaly (flagged via event):** The Date cell for row 3 contains 43751.249 — which is the same number as the panel sell price (43,751.25) shown on the Panel Notes sheet. Looks like an accidental paste of the price into the date column. The true original-draft date is therefore unknown.

---

## 5. Wire Changes / Redlines

There is no "Wire Changes" text doc. The only wire-change artifact is the 6 iPhone photos in `Drawings/Red lines/IMG_0331..0336.HEIC` — customer markups received as photographs. The downstream record of those changes is the drawing revision sequence (`0` → `K`) in `Drawings/OLD/`, not a written changelog.

## Summary of process-doc state

| Doc type | Present? | Substance |
|---|---|---|
| Fab Packet | **No** | Only a 4-line traveler tag at top level. |
| QC Checklist (filled) | **No** | Only a Vitalis customer-template form (unfilled). |
| Changelog | **Partial** | XLSX has a "Notes" column header but only one row populated, with a corrupted date. |
| Wire Changes log | **No** | Redlines exist only as 6 HEIC photos. |
| Process narrative | **No** | None. |
| Proposal (scope) | **Yes** | Final 033126 + 2 superseded drafts in OLD. |
| Terms & Conditions | **Yes** | Embedded in proposal body. |

The process-doc footprint of this job is thin: the proposal carries the sales scope, the DWGs carry the engineering, and everything in between (fab, build instructions, QC results, change tracking) is essentially undocumented in textual form. The build photos and shipping photos serve as the de-facto build/QC record.
