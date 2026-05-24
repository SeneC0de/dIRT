# Artifact Lifecycle — E1392 / 4S Ranch (Vitalis)

Job folder: `inputs/jobs/E1392 - 4S Ranch/`
Customer: Vitalis (attn Jacob Vanzella)
Panel: 4S Ranch, tag MB0216, 208VAC 3ph+E, SCCR 65 kAIC

The folder has the standard dC lifecycle stages plus a couple of extras (`OLD`, `Drawings/OLD`, `Drawings/Red lines`, `Build Progress Photos`). 158 files total.

## Stage-by-stage walk

### 1. RFQ — `RFQ/`
- `Classic 4S Ranch - EXXXX RFQ 031626.xlsx` (1.3 MB, 2026-03-16)
  - Customer's request-for-quote workbook. Filename still has the placeholder job number "EXXXX" — pre-dates E1392 being assigned. Date 03/16/26.
  - This is the upstream input; everything downstream traces back to it.

### 2. Proposal — top-level + `OLD/`
- `OLD/E1392 - 4S Ranch Panel Proposal 031926.pdf` (3 days after RFQ)
- `OLD/E1392 - 4S Ranch Panel Proposal 032026.pdf` (one day later)
- `E1392 - 4S Ranch Panel Proposal 033126.pdf` and `.docx` (final, 03/31/26)
- **Lineage:** RFQ → draft proposal 03/19 → revised 03/20 → final 03/31 (~2 weeks of revisions). The two earlier PDFs in `OLD/` are superseded.

### 3. PO — `PO/`
- `Purchase Order - P-37066.pdf` (customer-issued purchase order)
- `PO# P-37066 - Order Acknowledgement.pdf`
- `PO# P-37066 - Order Acknowledgement.xlsx` (same content, machine-readable form)
- **Dependency:** PO# P-37066 follows acceptance of the 033126 proposal. The xlsx and pdf order ack are paired (different formats of the same document); supplemental XLSX worth profiling.

### 4. Job-tag / traveler — top-level
- `E1392 - dC Job Tag for Traveler.docx`
  - Sits at top level, not inside QC or Fab. This is a per-job traveler tag — fits a "fab packet" role but does not constitute a fab packet.

### 5. Drawings — `Drawings/` (the main engineering deliverable)
- `Drawings/DWGs 5-13-26/` — 81 numbered `.dwg` pages + AutoCAD Electrical project files (`.aepx`, `.wdp`, `.wdt`, `.mdb`, `.wdl`). Latest source DWG set.
- `Drawings/E1392 - 4S RANCH - 5-13-2026 - K.pdf` (4.2 MB) — current plotted DWG package, revision K.
- `Drawings/E1392 - 4S RANCH - 5-8-2026 - J.docx` — Word version of revision J (likely a redline/markup intermediate).
- `Drawings/plot.log` — trivial plot log.
- `Drawings/OLD/` — full revision history `0, A, B, C, D, E, F, G, H, I, J` from 04/14 → 05/08 (11 revs in ~25 days). Plus a one-off `E1392 - 4S RANCH - LAYOUT.pdf` and `OLD/LAYOUT DWGs/66-LAYOUT.dwg` (66 MB — predecessor of the current 75-LAYOUT.dwg numbering).
- `Drawings/Red lines/IMG_0331..0336.HEIC` — six iPhone photos. Customer-marked redlines, photographed.

**Revision arc:** 12 plotted revisions (0 → K) over 30 days. The redline-photos folder is the channel by which customer markups came in; the next PDF revision is the response.

**Sheet-numbering convention (from the DWG list):**
| Range | Section |
|---|---|
| 0 | REV TRACK |
| 1 | COVER SHEET |
| 2–5 | 3 PHASE |
| 6–7 | 120VAC DIST |
| 8–10 | MT1 GEN |
| 11–14 | MT1 C1 (compressor 1) |
| 15–18 | MT1 C2 |
| 19–22 | MT1 C3 |
| 23–26 | MT1 C4 |
| 27–32 | LT1 GEN |
| 33–36 | LT1 C1 |
| 37–40 | LT1 C2 |
| 41–44 | LT1 C3 |
| 45–48 | LT1 C4 |
| 49–50 | OIL SEP |
| 51 | HR GEN |
| 52 | HR SENSORS |
| 53 | HR 3-WAY |
| 54 | HR WATER PUMP |
| 55–57 | GAS COOLER |
| 58–60 | HIGH PRESS REG |
| 61–63 | MED PRESS REG |
| 64 | S2 GEN |
| 65 | S2 REFER COLLECT |
| 66 | S2 LIQ SUBCOOL |
| 67 | E3-CONTROLLER |
| 68 | MULTIFLEX 810-3065 |
| 69 | MULTIFLEX 810-3066 |
| 70 | IPRO_CO2 |
| 71 | IPRO DUAL_STEPPER_1 |
| 72 | IPRO DUAL_STEPPER_2 |
| 73 | MULTIFLEX 810-3064 |
| 74 | CO2 SENSOR |
| 75 | LAYOUT |
| 76 | DOOR LAYOUT |
| 77 | DOOR LAYOUT ZOOM |
| 78–80 | LAYOUT DETAILS 2/3/4 |

This sheet structure is the de-facto panel feature map for the job (it matches the BOM tags directly: e.g. `LT14131` = light on page 14 line 13 etc.). The drawings drive everything else, and the BOM tag column is a foreign key into this set.

### 6. Fab Packet
- **Not present as a named folder.** The job has a top-level `E1392 - dC Job Tag for Traveler.docx`, but no Fab Packet folder, no wire-pull list, no build-instructions doc. Per the project rule "fab packets are mostly incomplete shells / incomplete hopes" — here the absence is total, not partial. No signal can be derived from it.

### 7. QC — `QC/`
- `QC_Checklist_VITALIS.pdf` and `QC_Checklist_VITALIS.xlsx`
- Filename keyed to **customer (VITALIS)**, not to E1392 — almost certainly a template form that's reused across all Vitalis jobs.
- Inspect-worthy as a supplemental XLSX.

### 8. Shipping — `Shipping/`
- `Packing Slip - Vitalis - dC E1392 - 4S Ranch 051326.pdf` (05/13/26)
- `Shipping/Pictures/` — 28 iPhone HEIC photos (IMG_7332..IMG_7390). Pre-shipment / loading photos. Same date as the packing slip (05/13).

### 9. Invoice — `Invoice/`
- `Invoice 1086 - Vitalis 4S Ranch - dC E1392 051326.pdf` (05/13/26)
- Invoice number 1086 (sequential), dated the same day as ship.

### 10. Build progress — `Build Progress Photos/`
- 7 HEIC photos (IMG_6703..6705 + IMG_7250..7253). Two photo bursts — one early, one later (IMG number jump suggests different days).
- Lives outside the sequential lifecycle, more like an as-built record.

### 11. `OLD/` (top level, not Drawings/OLD)
- Holds the two superseded proposals only. A separate purge area at the document root for non-drawing artifacts.

## Lifecycle order and dependencies

```
RFQ (Classic 4S Ranch RFQ, 03/16)
   |
   v
Proposal v1 (03/19) -> v2 (03/20) -> FINAL (03/31, both .docx + .pdf)
   |                                       superseded copies -> /OLD
   v
PO  P-37066 (customer)  +  Order Acknowledgement (dC, pdf + xlsx)
   |
   v
Drawings rev 0 (04/14) -> A (04/15) -> B -> C -> D -> E -> F -> G (04/17)
                          -> H (04/23) -> I (04/29) -> J (05/08, pdf + docx)
                          -> K (05/13, current PDF + DWGs 5-13-26/ source)
   |     redlines -> photographed (Drawings/Red lines/IMG_0331..)
   v
[Build] -> Build Progress Photos (IMG_6703..6705, IMG_7250..7253)
   |
   v
QC checklist (VITALIS template, pdf+xlsx)
   |
   v
Shipping (Packing Slip 05/13 + 28 loading photos)
   |
   v
Invoice 1086 (05/13)

Auxiliary, not on critical path:
  Main XLSX (E1392 - 4S Ranch.xlsx) — feeds proposal pricing + tag/BOM lookup
  Job Tag for Traveler (top-level docx) — closest thing to a fab packet
```

The whole job ran from RFQ (03/16) to ship (05/13) — **~8 weeks**. Drawings rev K = ship date = invoice date, all 05/13. The drawing rev cycle (0 → K, 12 revisions in 30 days) is the heaviest activity stretch.

## Observations & gaps

1. **No Fab Packet folder.** The traveler-tag .docx is the only fab-side artifact at top level. Build photos exist but no build instructions, wire-pull sheet, panel-layout dimension callouts (beyond what's in the DWG package).
2. **QC checklist is a customer template, not job-specific.** `QC_Checklist_VITALIS` is named for the customer; if it were job-specific you'd expect `E1392` in the filename. Need to confirm in deep-read whether it was filled in for this job or stayed as a blank shell.
3. **Two parallel "OLD" folders.** Top-level `OLD/` (2 superseded proposals) and `Drawings/OLD/` (10 superseded drawing PDFs + 1 layout DWG). Same convention used at different depths — easy to lose track of.
4. **The 5-13-26 DWG source set + rev K plot are versioned implicitly by date in the folder name, not by rev letter.** Rev K is the latest plot; the DWG sources are dated `5-13-26`. To know "what DWG matches PDF rev K" you must trust the dates.
5. **Redlines arrive as iPhone photos** in `Drawings/Red lines/`. There's no PDF markup or annotated drawing — just six HEICs. This is a typed-from-photos workflow.
6. **Sheet 75 is "LAYOUT" in the current set, but `OLD/LAYOUT DWGs/66-LAYOUT.dwg` exists.** The layout sheet got renumbered from 66 to 75 during the rev cycle. Watch for stale cross-references.
7. **Job tag for Traveler sits at the top of the job folder rather than in a Fab/QC subfolder** — convention is unclear; might be a deliberate "first thing you grab" placement.
8. **Customer purchase order from Vitalis** is dated/processed under PO P-37066 — same number appears on the order acknowledgement, consistent.
9. **Estimate # 1392** on the Panel Notes sheet matches the job number E1392. Sell price on Panel Notes (43,751.25) is the proposal figure.
