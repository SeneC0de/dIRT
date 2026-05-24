# XLSX Profile — `E1392 - 4S Ranch.xlsx`

Source file: `inputs/jobs/E1392 - 4S Ranch/E1392 - 4S Ranch.xlsx`

## Sheet inventory

| Sheet | Rows × Cols | Populated cells | Purpose (observed) |
|---|---|---|---|
| Panel Notes | 30 × 13 | 43 | Customer/job metadata: Vitalis, Attn Jacob Vanzella, Estimate #1392, Rev 1, panel name "4S Ranch", panel tag MB0216, incoming 208VAC 3ph+E, SCCR 65 kAIC, UL Sticker = TRUE, sell price 43,751.25. |
| BOM - SCP-01 | 1103 × 35 | 856 | The actual bill of materials for panel SCP-01. Purple/red bars present (see below). |
| Clean BOM & Pick List | 77 × 5 | 8 | Header-only shell ("E1392 - 4S Ranch REV.2 / BOM Pick List / Part #, Description, Manufacturer, Qty, Picked"). No rows populated — an empty template. |
| IO - Control Panel | 1002 × 12 | 404 | I/O index template — DI / DO / AI / AO column groups, channels 1..N pre-numbered, but the `Desc / Signal Type / Voltage` columns are empty. Essentially a blank I/O sheet. |
| Load Calc | 982 × 13 | 139 | Genuine load calculation. 3-phase loads (208V/60Hz), with line items for T5031 (3kVA xfmr), T5071 (500VA xfmr), B1-2U1, B2-2M1, B3-2M1 (MT1 compressors at 84.6 FLA each), G1-2U1, G2-2U1 (LT1 compressors at 11.1 FLA). Total FLA 293.40 A, MCA 314.55 A, MOCP 399.15 A. Plus transformer sizing tabs for 1kVA and 500VA. |
| Legend Plates | 1002 × 26 | 168 | Legend-plate text for sensor bulkheads + pilot lights. Two tables: bulkhead labels (rows 2..~23, e.g. `B0-2B1 / SUCTION GAS TEMP / (SENSOR 1) / pg 7 / bulkhead #1`), and pilot-light labels (rows 27..N, e.g. `LT14131 / MT1 COMPRESSOR 1 / RUNNING / pg 14 / light #1`). |
| Clean BOM | 1006 × 26 | 6 | Header-only shell, never populated. Twin of "Clean BOM & Pick List". |
| Categories | 30 × 2 | 29 | QBO product categories list (Buttons & Lights, Cable Management, Cables, Contactors, Controllers, Display, Enclosure, Engineering, Fees, Hardware, IO Devices, Instrumentation, Jumpers, Labeling, Labor, Marking, Memory, Mileage, Networking, Panel AC & Heating, Power Supplies, Printers & Labels, Protection Devices, Relays, Software, Terminal Blocks, Transformers, Wire). Reference list. |

## BOM sheet — `BOM - SCP-01`

### Column schema (header row = row 9)

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

Above row 9 (rows 1..8): a "Initials / Date / Notes" mini-changelog. Row 3 carries the only entry: "Original genuine draft" with serial date 43751.249 (the same 43751.25 figure appears as the sell price on Panel Notes — strongly suggests this cell was over-typed by accident rather than being a date; flagged as a finding).

### Purple / red bar rule applied

- Purple bar fill `FF8E7CC3` appears on **row 22** (cell B22). Row 22 itself reads `NO MODS BELOW THIS LINE` in column D — i.e. the purple bar is the **upper** boundary marker.
- Red bar fill `FFE06666` appears on **row 101** (cell B101). Row 101 itself reads `DO NOT COPY TO SUBMITTAL BOM BELOW THIS LINE` in column D — the **lower** boundary.
- **Real BOM rows = 23..100 inclusive = 78 rows.**

### Rows excluded above the purple bar (rows 1..21)

Only rows 2..3 hold content (the "Initials / Date / Notes" header + the "Original genuine draft" entry). Rows 4..21 are empty (a few rows have `0` in the Ext. Cost column from formulas referencing empty cells). Nothing here is a BOM item — excluded per the rule.

### Rows excluded below the red bar (rows 101..end)

| Row | Content | Reason for exclusion (per rule) |
|---|---|---|
| 101 | Red bar; "DO NOT COPY TO SUBMITTAL BOM BELOW THIS LINE" | Marker row |
| 102 | WAGO `858-158` 120 VAC basic relay, qty 0 | Removed-for-posterity (qty 0) |
| 103 | WAGO `858-110` ejector, qty 0 | Removed-for-posterity |
| 104 | WAGO `858-100` relay socket, qty 0 | Removed-for-posterity |
| 105 | ABB `E214-16-101` group switch, qty 0, tagged to selector switches `SS14061…SS37061` | Removed-for-posterity — appears superseded by the Schneider `XB4BD21` at row 87 |
| 106 | `Wire` qty 1 | Fudge (consumable) |
| 107 | `Ground bar kit` qty 2 | Fudge |
| 108 | `2.25"x3" Wire Duct, 2M` qty 4 | Fudge (cable tray / wire duct) |
| 109 | `Panel CNC cutouts` qty 1 | Fudge (process cost line, not a BOM part) |
| 110 | `Labels` qty 1 | Fudge |
| 111 | `Hardware` qty 1 | Fudge |
| 113..118 | qty 0 rows with category only | Empty / removed placeholders |
| 122..126 | `Engineering` 20, `Drafting` 64, `Assembly` 80, `QA & Testing` 8, `Shipping Prep` 4 | Labor-hour estimates — not BOM parts |
| 128..129 | `Material` 0.2 / `Labor` 0.6 | Markup factors — not BOM parts |

All 22 of those rows are excluded from the real BOM count per the rules.

### Real BOM contents (78 rows between bars)

Distribution by category (rows 23..100):

| Category (as written) | Row count |
|---|---|
| Controllers / IO Devices / Instrumentation (Copeland kit) | 8 |
| Enclosure (Rittal) | 4 |
| Protection Devices | 22 |
| Contactors | 5 (incl. some tagged "Protection Devices") |
| Transformers | 4 |
| Panel AC & Heating | 3 |
| Buttons & Lights | 3 |
| Relays | 3 |
| Labeling | 1 |
| Networking | 1 |
| Power Supplies | 3 |
| Hardware | 3 |
| Terminal Blocks | 9 |
| Jumpers | 1 |
| (blank category) | 8 |

Approximate — categories are inconsistent (e.g. row 43 IB MPW100 is tagged "Contactors" but it's an insulating plate for a motor protector). Treat category column as low-confidence metadata.

### Tag conventions observed

- Device-tag style: `<TYPE><PAGE><LINE>`, e.g. `CB6111` = circuit-breaker on drawing page 61 line 11; `LT14131` = pilot light on page 14 line 13; `T4131` = transformer on page 41 line 3.
- Many BOM rows carry multiple tags in one cell, comma-separated (e.g. row 76: 14 different CB tags share one part number M9F42102).
- Some rows have no tag (Rittal enclosure parts, Wago small TBs, ground bars) — consistent with the rule that small Wago TB counts are estimates.

### Anomalies / flags

1. **Row 3 "Date" cell holds 43751.249** — that's the same number as the panel sell price on Panel Notes ($43,751.25). Almost certainly an accidental paste into the Date column; intended value is unknown.
2. **Category inconsistencies** — `IB MPW100` (insulating plate) tagged "Contactors"; `709-591` switchgear drawer tagged "Hardware" while functionally it holds spare fuses; several rows have blank category.
3. **Two BOM picklist sheets ("Clean BOM" + "Clean BOM & Pick List") are header-only.** They exist as shells; nothing has been clean-ified. Treat as not-yet-done work, not as authoritative.
4. **"IO - Control Panel" sheet is a numbered skeleton.** All 1..N channel rows are present but the Desc / Signal Type / Voltage columns are empty across DI / DO / AI / AO. Not a real I/O map for this job.
5. **Wago small-TB rows (88..97) carry no tags and round counts** (51, 33, 35, 25 etc.). Per project rule these are estimates — confidence is LOW on those quantities.
6. **Spare-fuses block (rows 83..85)** uses the tag string "SPARE FUSES" — not a device tag; it's a function tag. Counted as real BOM (qty 1 drawer + 2+2 fuses) but worth knowing the tag column is overloaded.
7. **DISC2011 (rows 35..37)** repeats the same tag across three sub-parts of one ABB XT5N disconnect kit (breaker + lug kit + RHE rotary handle). Tag is the device, not the line.
8. **Row 37 description includes "RETURNED"** ("RHE XT5 F/P STAND. RETURNED | ABB") — possibly a vendor-return note carried through from a quote, not a removal. Ambiguous.

### Counts to remember

- **Sheets:** 8
- **Real BOM rows:** 78 (rows 23..100)
- **Excluded above purple bar:** 21 rows (mostly empty)
- **Excluded below red bar:** ~30 rows (qty-0 removed parts, fudges, labor estimates, markup factors)
- **Distinct manufacturers in real BOM:** ABB, COPELAND, FINDER, LITTELFUSE, MOUSER, nVent, PENN UNION, PHOENIX CONTACT, RIB, RITTAL, SCHNEIDER, WAGO, WEG, CAROLINA LASER (~14)
