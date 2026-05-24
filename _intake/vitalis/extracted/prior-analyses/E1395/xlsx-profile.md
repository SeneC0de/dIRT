# E1395 - Lazy Acres - MB0219.xlsx — Profile

File: `inputs/jobs/E1395 - Lazy Acres - MB0219/E1395 - Lazy Acres - MB0219.xlsx`

## Sheets

| Sheet | Rows | Cols | Purpose (inferred) |
|---|---:|---:|---|
| `BOM - SCP-01` | 1097 | 35 | The build BOM. Sheet name encodes the panel tag (SCP-01). |
| `Panel Notes` | 30 | 13 | Header card: customer, estimate #, panel tag, voltage, SCCR, totals, IO counts, project email body. |
| `Clean BOM` | 72 | 24 | Pick-list shell. **Empty** — only headers `Part # / Description / Manufacturer / Qty / Picked` populated. |
| `Danfoss Inventory` | 40 | 5 | Reference list of Danfoss part numbers + quantities. Looks like a stocking sheet. |
| `IO - Control Panel` | 1002 | 12 | DI/DO/AI/AO templates with channel numbers 1..N pre-populated. **Almost entirely empty** — only 2 DI and 2 DO rows actually have a Description filled in. |
| `Load Calc` | 998 | 23 | Live load calculation — 3-phase loads, transformer sizing, FLA/MCA/MOCP arithmetic. Densely populated through ~row 35; trails off. |
| `Categories` | 30 | 2 | QBO product category lookup (Buttons & Lights, Cables, Contactors, Controllers, Display, Enclosure, Engineering, Fees, Hardware, IO Devices, Instrumentation, Jumpers, Labeling, Labor, Marking, Memory, Mileage, Networking, Panel AC & Heating, Power Supplies, Printers & Labels, Protection Devices, Relays, Software, Terminal Blocks, Transformers, Wire). |

## `BOM - SCP-01` — the bar rule

Column layout (row 9 header row):

| Col | Header |
|---|---|
| B | Tag |
| C | Part # |
| D | Description |
| E | Manufacturer |
| F | Qty |
| G | Category |
| H | Price/Unit |
| I | Ext. Cost |
| J | PO# |
| K | PO Date |
| L | Ship Date |
| M | Total (mA) |
| N | Weight (lb) |
| O | Total (lb) |

### Bar locations (by fill-color scan)

| Row | Fill RGB | Color name | Role |
|---:|---|---|---|
| 13 | `FF8E7CC3` | Purple bar | Start of real BOM. |
| 85 | `FFE06666` | Red bar | End of real BOM. Cell D85 literally contains `"DO NOT COPY TO SUBMITTAL BOM BELOW THIS LINE"`. |

Other fills in the sheet (helpful but not BOM-delimiting):
- `FFFFF2CC` (pale yellow) rows 17-26 — marks the Danfoss block (highlighted as a group).
- `FFF6B26B` (orange) rows 86-93 — wire fudge entries (below red bar).
- `FFCFE2F3` (light blue) rows 113-117 — labor/cost totals.
- `FF0A77B5` row 9 — header row banding.

### Real BOM rows = 14..84 inclusive = **71 BOM items**

No rows above the purple bar contain part data (rows 1-12 are metadata: customer, header, signoff). The "Initials / Date / Notes" mini-table at rows 2-3 is a sign-off block, not BOM. Only nonblank row above the purple bar with a part-shaped pattern: row 9 (the header), which is *equipment-correct* per the rule (a header sits above, ignored as far as "items" go but used to interpret columns).

**Categories present in real BOM rows (71 items):**

| Category | Count |
|---:|---|
| Protection Devices | 19 |
| IO Devices | 7 |
| Terminal Blocks | 6 |
| Relays | 5 |
| Power Supplies | 4 |
| Buttons & Lights | 4 |
| Transformers | 3 |
| Panel AC & Heating | 3 |
| Hardware | 3 |
| Enclosure | 2 |
| Controllers | 2 |
| Contactors | 1 |
| Networking | 1 |
| Labeling | 1 |
| *(blank)* | 10 |

**Manufacturers present:** WEG (15), SCHNEIDER (14), WAGO (13), DANFOSS (10), FINDER (4), ABB (3), LITTELFUSE (3), SAGINAW (2), PHOENIX CONTACT (2), PxC (2), nVent (1), PENN UNION (1), CAROLINA LASER (1).

### Rows EXCLUDED and why

| Rows | Why excluded |
|---|---|
| 1-8 | Pre-header metadata: customer name, sign-off mini-table. Not BOM. |
| 9 | Column header. |
| 10-12 | Three blank-ish rows with `0` in the Ext. Cost column — formula placeholders or removed-but-not-deleted items. |
| 13 | The purple bar itself (no content). |
| 85 | The red bar — literal "DO NOT COPY TO SUBMITTAL BOM" warning. |
| 86-101 | Wire / wire-tray / "CNC cutouts" / "Wire" / "Labels" / "Hardware" line items (the **fudges**). These are bulk consumables priced in lump sums — not BOM items. |
| 102-107 | Removed enclosure options (`SCE-FK0618`, `SCE-72SMP14`, `SCE-724818FSD`, `SCE-72P48F1`) all with Qty=0 — **kept for posterity** per rule 2. These document the design path: the team considered floor kit + side panel + a 48"W enclosure, then settled on the 60"W FSD enclosure that lives at rows 14-15. |
| 108-112 | Labor breakdown (Engineering 21h, Drafting 35h, Assembly 60h, QA & Testing 8h, Shipping Prep 4h). Not BOM. |
| 113-117 | Cost rollup: Material total $20,707.99, Labor total $7,065 → Sell $43,547.49 (the 0.2 in F114 = material markup factor 0.2 → material × 1.25; the 0.6 in F115 = labor markup 0.6 → labor × 2.5). Not BOM. |
| 118+ | Empty (nothing through row 1097 — the sheet has been allocated for growth). |

### Within-BOM caveats (carrying caveat #3 forward)

- Wago entries in the real BOM rows 14-84 include: `2002-1201` (feedthrough TB), `2002-3201` (triple-deck TB), `210-112` (DIN-rail steel carrier), `249-116` (end stop), and the highlighted Danfoss-adjacent block. **All Wago small-TB / end-stop / rail items in rows 80-83 should be treated as estimates** — only Wago entries that are functionally relays/power supplies get full confidence. None of the Wago rows in the real BOM are relays; the relays come from FINDER, SCHNEIDER, ABB.

## `Panel Notes` sheet — key values

```
Customer:            Vitalis
Attn:                Sean Demers
Estimate #:          E1395
Rev:                 1
Name:                Lazy Acres
Panel Tag:           SCP-01
Incoming Power:      208 V
SCCR:                65 kAIC          (note: customer email asked for 100k; downgraded to 65k)
UL Sticker(s):       True
NEMA Rating:         (blank)          — flagged: not specified
Sell Price:          $43,547.49
DI/DO/AI/AO counts:  all 0           — should be populated; the IO sheet is also blank
```

The full customer-email body is pasted into cell G6 (multi-line string). That is the closest thing to an RFQ in this corpus.

## `Load Calc` sheet — what's there

Densely populated through ~row 35, with transformer sizing math (1kVA, 3kVA, 500VA) and per-compressor load entries:

- MT1: 4× Dorin CD3501M @ 156 A (one VFD + three contactor-fed). Tag prefix B1/B2/B3/B4.
- LT1: 3× Dorin CDS351B/CDS301B @ 15.2 A. Tag prefix G1/G2/G3.
- Computed totals: Total FLA 687.6 A, MCA 726.6 A, MOCP 882.6 A.
- Transformer math down-the-page: T1 = 3 kVA 208→120, primary current 14.42 A → 36 A protection; T2 = 500 VA 208→24, primary 2.40 A → 6 A primary protection, secondary 20.83 A → 30 A protection.
- After row 35 the calc trails off — likely because subsequent transformer sub-sections were left as templates. Total populated rows in the 998-row sheet: 34.

**Self-inconsistencies inside Load Calc** (flag these — don't fix):
- Row 12 description says `COMP 2 MOTOR` for tag `G2-2U1` but the part number is `CDS301B`, not the `CDS351B` shown in row 11 for G1. Rows 11-13 part numbers: CDS351B, CDS301B, CDS301B. The customer email says all LT compressors are CDS351B with FLA 15.2 A. Inconsistency: part numbers `301B` vs `351B`. **Flag as finding.**
- Row 12-13 are missing AWG values that row 11 has, even though FLAs are identical.

## `IO - Control Panel` sheet — what's NOT there

Of 1002 rows: only 2 DI rows and 2 DO rows actually have a Description filled. The remainder is a pre-numbered channel template (Ch 1..N for DI/DO/AI/AO blocks). The Panel Notes sheet shows IO counts as 0 across DI/DO/AI/AO, consistent with this. **The IO list is effectively unbuilt in this artifact, yet the published drawings explicitly reference "MOVED DANFOSS WIRING TO MATCH IO LIST" as a revision-table comment.** Implies the canonical IO list lives in the drawings (or in the engineer's head), not in this spreadsheet. (See findings / story-themes.)

## `Clean BOM` sheet — empty pick list

Header row at row 2 with `Part # | Description | Manufacturer | Qty | Picked`. Title row at row 1 says "REV.2" — implying a pick list was prepared at one point and then either cleared or never filled. The QC SOP describes an "As-Built BOM" step that this sheet might feed, but the sheet is empty.

## `Danfoss Inventory` sheet

A small reference table — 12 Danfoss SKUs with their Danfoss-internal part numbers and module descriptions. Counts shown are higher than the BOM uses for some parts (e.g. AK-XM 103A qty 7, AK-XM 205A qty 2, MMIGRS2 qty 3). Reads like a **shared organization-wide Danfoss inventory snapshot** copy-pasted in, not job-specific. Cross-check other jobs.

## `Categories` sheet

27 QBO product categories — purely a dropdown source for the `Category` column in the BOM. Not job-specific.

---

## Summary observations

1. The workbook has **one densely populated sheet (BOM)**, one **partly-populated sheet (Load Calc)**, and **three near-empty sheets** (Clean BOM, IO - Control Panel, Categories-as-template). The IO sheet is the surprising gap given that the drawings have already been revised to "match IO list."
2. The purple/red bar convention works mechanically: 71 BOM items between rows 13 and 85. Below the red bar the cost rollup is intentional and useful, but **the wire / labor / fudge rows must not be re-treated as BOM**.
3. The 4 enclosure rows with Qty=0 (102-106) are a useful **design-history trail** — a small forensic anchor for understanding why the chosen 60"W enclosure was chosen over a 48"W variant.
