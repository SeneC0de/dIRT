# E1399 — Artifact Lifecycle

Job root: `inputs/jobs/E1399 - YCH Freecovery Roxsta G6 MB0206/`

E1399 is the **sparest** of the four packets. Below: what is present at each stage, what it looks like, and — explicitly — what's missing relative to what jobs of this shape typically carry.

## Stage 0 — Job-level (root)

Present:
- `E1399 - YCH Freecovery Roxsta G6 MB0206.xlsx` — main engineering workbook (BOM, Load Calc, Legend Plates, IO scaffolding). Profile in `xlsx-profile.md`.

Missing here:
- **No `QC` folder.** No QC plan, no inspection checklist, no test report.
- **No `Fab Packet` folder.** No fabrication-traveler or assembly instruction set.
- **No Changelog / Wire Changes / Rev Notes** anywhere outside the embedded `0-REV TRACK.dwg` (just an AutoCAD title-block tracker, not a process narrative).
- **No engineering submittal package** explicitly named (submittal was committed in the PO description but never staged here).

## Stage 1 — RFQ

Present (1 file):
- `RFQ/YCH Roxsta G6 MB0206 - EXXXX RFQ XXXXX.xlsx` — the project-intake template. **9 sheets**: Project Info, Panel Options, Input Power List, Logos, FLA / MCA / MOCP / NEC 240.6A reference, Wire Ampacity.
  - **Smoking gun:** filename retains `EXXXX` and `XXXXX` placeholders; inside the workbook the `Estimate #` cell still reads `[JOB ID]`, and multiple cells return `#VALUE!`. The template was filled out partially but never resolved to the actual estimate number when the job was christened E1399.
  - Customer captured: Vitalis, contact Jacob Vanzella, location WA U.S.A., Panel Tag MB0206, Date 2026-04-21, Rev 1.11.
  - Panel Options flagged TRUE: Ethernet Switch, Machine Stop Button. FALSE: UPS, 6" floor legs, Energy Meter, Spare 8/8 IO board.

Missing:
- No customer-supplied original RFQ (PDF, email, spec sheet). Only dAPP's intake-template version.

## Stage 2 — Proposal

Present (4 files = 2 revs x [docx + pdf]):
- `E1399 - YCH Freecovery Roxsta G6 MB0206 Panel Proposal 033126.docx` + `.pdf` — Mar 31 proposal.
- `E1399 - YCH Freecovery Roxsta G6 MB0206 Panel Proposal 042326.docx` + `.pdf` — Apr 23 proposal (the one that priced at $42,535.42, lead time 4-6 weeks).

Observations:
- Two priced revisions ~3 weeks apart; no diff doc or revision note in the folder explains what changed between 0331 and 0423. The docx files are 7-byte-different in size (140,027 vs 140,034) — almost identical.
- Pricing matches what the PO eventually paid → 0423 proposal was the accepted version.

Missing:
- No client-signed copy of the proposal in this folder. The docx has signature placeholders, no countersign artifact.
- No "Lost / Won" status marker.

## Stage 3 — PO

Present (3 files):
- `Purchase Order - P-38256.pdf` — Vitalis-issued PO.
- `PO# P-38256 - Order Acknowledgement - Purchase order.pdf` — dAPP's countersigned ack.
- `PO# P-38256 - Order Acknowledgement.xlsx` — XLSX source of the ack (1 line item: $42,535.42; PO date 2026-05-04; ship date 2026-05-21; NET 30; Ex-works Cumming GA; Ship-to Vitalis Plant 3, Kelowna BC Canada).

Observations:
- PO ack `Job ID: MB0206` is the customer's internal panel tag, **not** dAPP's estimate number — those two identifiers cross-walk here for the first time.
- "Attention to: Pouya Yazdchi" appears as the dAPP-side owner on the ack.

Missing:
- No deposit / payment trace.
- No PO change order — useful because the BOM XLSX contains *three* alternate motor-protection topologies (alive in pre-purple, dead in below-red rows) that suggest scope churn that's never written down.

## Stage 4 — Drawings

Present:
- `Drawings/E1399-YCH Freecovery - 5-13-2026 - G.pdf` — **Rev G** is the live submittal PDF (6.3 MB).
- `Drawings/E1399-YCH Freecovery - 5-6-2026 - B.docx` — a docx mirror dated May 6, Rev B — odd format choice for drawings.
- `Drawings/DWGs 5-13-26/` — **84 numbered .dwg files** (00 REV TRACK through 84 MOTOR PROTECTION) + AutoCAD Electrical project files (`.aepx`, `.wdp`, `.wdt`, `.wdl`). Major page groups:
  - 1: Cover; 2-7: 3-phase + 120 VAC distribution; 8-31: MT1 (medium-temp) general + 5 compressors; 32-50: LT1 (low-temp) general + 4 compressors; 51-66: oil separator, HR (heat recovery), way, gas cooler, high/med pressure reg, refer collect; 67-74: Modules 1-7 + Com Module; 75: HMI; 76: motor room; 77-78: BOM (drawn version); 78-82: Layout / door / details; 83: Danfoss; 84: motor protection.
- `Drawings/OLD/` — 6 prior submittal-PDF revs A through F (2026-05-05 through 2026-05-08, daily cadence), plus `DWGs 5-8-26/` snapshot.

Observations:
- Drawing-rev cadence: A→B→C→D→E→F→G in 8 days (5/5 → 5/13). That's daily revs for a week — heavy iteration just before ship. No human-readable changelog explains the deltas; the only diff source would be the embedded `0-REV TRACK.dwg` (38 MB).
- Two distinct BOM pages on the drawing (`77-BOM.dwg`, `78-BOM.dwg`) suggests the BOM occupies multiple sheets; would need to cross-check with the XLSX BOM (74 line items, fits).

Missing:
- No DXF / IGES / step exports — only native .dwg + a PDF render.
- No bookmark sheet listing drawing rev history outside the binary AutoCAD file.

## Stage 5 — Shipping

Present (2 files):
- `Shipping/Delivery Slip - dAPP Controls LLC - P3_RES_00107.pdf`
- `Shipping/P-38256 P3 RES 00107 UPS Label.pdf`

Observations:
- Carrier: UPS. Customer shipping reference: `P3 RES 00107`. PO match: P-38256.
- One delivery slip → one parcel. Plausible for a single 72x60x18 enclosure but worth flagging — large enclosures usually move LTL/freight, not UPS. Either the UPS label is for accessories (manuals, keys) while the panel went freight, or UPS Freight is being used and the document name is misleading.

Missing:
- **No proof-of-delivery / BOL / freight receipt** for the enclosure itself. Only a UPS small-parcel label.
- No packing slip itemization.
- No customer-receipt confirmation.

## Stage 6 — Invoice

Present:
- **The `Invoice` folder is empty.**

Missing:
- Invoice copy, payment receipt, AR-aging note — none.

## Stage 7 — QC / Fab / Process

**Absent entirely.** This is the load-bearing absence in E1399:
- No QC inspection record (open-box, hi-pot, continuity, label-verify) — no folder, no PDF, no checklist.
- No Fab Packet / assembly traveler.
- No wire-pull list (the IO sheet in the XLSX is empty, which means no upstream IO map ever got turned into a wire schedule).
- No commissioning notes.

## Cross-stage observations

1. **The job was shipped without writing down how it was built or tested.** Drawings ship; build doesn't. The XLSX has all the engineering inputs (Load Calc, Legend Plates), but the *Clean BOM*, *Clean BOM & Pick List*, and *IO - Control Panel* sheets — the three views a builder would consume — are unfilled templates.
2. **Scope churn lives in dead rows, not in a changelog.** The BOM XLSX contains 3 alternate motor-protection topologies (pre-purple, below-red WEG-package A, below-red WEG-package B). The decisions that killed those alternatives aren't documented anywhere in the packet.
3. **Daily drawing revs A-G** in 8 days suggest active redlining right up to ship, but no narrative survives. The PDF render is the only artifact a downstream consumer can read.
4. **Estimate-number provenance is fragile.** The RFQ workbook still says `[JOB ID]` and the filename still says `EXXXX`. The number "E1399" only appears reliably in the proposal + PO ack — i.e., once the job left engineering and entered commerce.
