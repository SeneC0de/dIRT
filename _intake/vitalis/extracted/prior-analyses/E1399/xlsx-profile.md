# E1399 — Main XLSX Profile

**File:** `inputs/jobs/E1399 - YCH Freecovery Roxsta G6 MB0206/E1399 - YCH Freecovery Roxsta G6 MB0206.xlsx`
**Customer:** Vitalis (Attn: Jacob Vanzella) — Estimate # E1399 — Date 2026-04-22 — Rev 1 (request: Email)

## Sheet inventory

| Sheet | Dims (rows x cols) | Role | Populated? |
|---|---|---|---|
| Panel Notes | 30 x 13 | Cover / metadata for the estimate | Yes — header block only |
| BOM - SCP-01 | 1128 x 35 | Active BOM with revision/notes columns | Yes — see bar rules |
| Clean BOM & Pick List | 78 x 5 | Pick-list output template | EMPTY — headers only |
| IO - Control Panel | 1002 x 12 | I/O channel map template | EMPTY — only the DI/DO scaffolding rows |
| Load Calc | 961 x 10 | Electrical load summation | Yes — 11 entry rows + transformer calcs |
| Legend Plates | 1002 x 26 | Bulkhead legend plate text | Yes — 33 plate rows |
| Clean BOM | 1006 x 26 | Reformatted BOM template | EMPTY — headers only |
| Categories | 30 x 2 | QBO product-category enum (validation lookup) | Yes — reference list |

## BOM - SCP-01 — bar rule applied

Cell-fill inspection (openpyxl):

- **Purple bar** at row 14 (fill `FF8E7CC3`), col D text: `NO MODS BELOW THIS LINE`
- **Red bar** at row 89 (fill `FFE06666`), col D text: `DO NOT COPY TO SUBMITTAL BOM BELOW THIS LINE`

Per the rule:

- Rows 1-13 — header block + two stray part rows (R11 `2006-1201` WAGO feedthrough TB qty 1; R12 `UD6C500AL` Power Dist Block qty 6). **Ignored** as pre-purple noise (these look like leftover scratch entries).
- **Rows 15-88 → REAL BOM (74 line-item rows)**
- Rows 90-end — removed-for-posterity + fudges + cost roll-up. **Ignored** for BOM count.

### Headers (row 9)
`Tag | Part # | Description | Manufacturer | Qty | Category | Price/Unit | Ext. Cost | PO# | PO Date | Ship Date | Total (mA) | Weight (lb) | Total (lb)`

### Real BOM observations (rows 15-88)
- **74 rows, 70 with real qty > 0**; total material rolled up below the red bar = $26,660.85 (Material 22,951.06 + Labor 20,750 → Sell $43,701.06 on the sheet).
- **Manufacturer mix:** Danfoss (10 rows — control system AK-* modules), ABB (12 — breakers, contactors, pilot lights, group switches), WAGO (15 — relays, TBs, jumpers, PSU base, rail), Schneider (4), WEG (12 — motor protectors, contactors, transformer), Littelfuse (5 — fuses incl. spares), Finder (4 — panel HVAC), Saginaw (2 — enclosure + subpanel), Phoenix Contact (3), nVent (2), Carolina Laser (1), Penn Union (1), 1 generic.
- **Spare fuses are kept as their own BOM rows** (R45, R47, R70 "SPARE FUSES" tag) — consistent line-item accounting.
- **Wago-outside-relays-and-PSUs** flagged low-confidence per charter: rows R74-R85 (`2006-1207, 249-117, 2002-3227, 2002-1207, 2002-1201, 2002-3201, 2016-1201, 2016-1207, 2002-3217, 2006-1201, 788-113, 210-112`). These are TBs / end stops / jumpers / DIN rail — all estimates.
- **`=AI("...")` placeholder formulas** in 7 cells across rows R31-R40 (description and/or manufacturer fields for WEG motor-protection parts). The sheet authoring tool tried to AI-fill metadata and left the formulas live. Flagged as a finding.

### Rows excluded (and why)
- **R10-R13 (pre-purple):** stray entries above `NO MODS BELOW THIS LINE` purple bar.
- **R90-R95:** zero-qty parts (XB5AVG1/XB5AVG4 pilot lights, WAGO 858-series basic relay set, SS-tagged group switches) — kept-for-posterity / not on this build.
- **R96-R100:** **fudges** — explicit `Wire`, `2.25"x3" Wire Duct, 2M`, `Panel CNC cutouts`, `Labels`, `Hardware` lump-sum lines under the red bar.
- **R102-R121:** an entire alternate ABB-based MT/LT distribution kit (XT1HU3100, AF96/65/52/40, MS165, AF/BEA, CA4 aux contacts). This is the prior topology before the WEG motor-protection package was adopted — kept for posterity.
- **R136-R144:** a second WEG-package variant (MPW100-3-U100, CWM105, MPW40, ECCMP-40B38, CWB18, CWCA0-31) — another stale alternative.
- **R147-R156:** labor roll-up (Engineering 20h, Drafting 40h, Assembly 80h, QA & Test 8h, Shipping Prep 4h) + grand totals. Not BOM.

## Load Calc

11 installation rows, all 460V three-phase loads:
- GENERAL POWER: T5031 3kVA 208/120 transformer + T5071 500VA 208/24 transformer.
- MT1 stack: 5 compressors (C1 VFD 63.6A, C2 VFD 74.2A, C3-C5 across-the-line contactors 77.1A each).
- LT1 stack: 4 compressors (C1 VFD 35A, C2 VFD 49.4A, C3-C4 contactors 49.4A).
- Totals: FLA 559.9 A, MCA 579.2 A, MOCP 656.3 A → matches the XT6 MCB at R27. Cross-checks.

## Legend Plates
33 rows, columns `Line 1 | Line 2 | Line 3 | Page # | Bulkhead #`. Tag examples: `B0-2B1 SUCTION GAS TEMP (SENSOR 1)`, `B0-4B1 DISCHARGE GAS TEMP`. Maps to drawing pages 7 and 8 (sensors).

## IO - Control Panel
**Effectively empty.** Rows 3-52 contain only the DI/DO channel-number scaffolding; no descriptions, signal types, or voltages populated. Row 53 onwards is a second blank table. **The IO sheet was never filled in for this job.** — flagged.

## Clean BOM & Clean BOM & Pick List
**Both empty templates.** Headers only. The downstream "submittal-ready" and "pick-list-ready" views were never generated from the BOM. — flagged.

## Categories
Reference list of QBO product categories (`Buttons & Lights`, `Cable Management`, `Cables`, ...). Drives the `Category` column on the BOM via data validation, presumably.

## Naming conventions observed
- **Tag style:** alpha prefix + 4-digit numeric (CB11071, CR2031, FU4121, LT14131, TG14071, MTR5041, RECP5061, TAS5041, WLT5021). Multiple tags can share one BOM row when the same part is reused (R52: 6 TG tags; R66: 14 CB tags on one ST201M-C2 line). Pages on the drawing are encoded in the second pair of tag digits.
- **Bulkhead tags** on Legend Plates: `B0-2B1` (panel-bulkhead-position-instance).
- **Part numbers** are the manufacturer PN as-is — no internal SKU layer.
