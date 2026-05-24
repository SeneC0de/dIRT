# E1404 — Main XLSX Profile

File: `E1404 - Northgate 49 MB0221.xlsx`

## Sheet inventory

| Sheet | Declared size | Real rows (last non-empty) | Purpose |
|---|---|---|---|
| Panel Notes | 30 × 13 | 28 | Customer / project header + email request text + signature scratchpad |
| BOM - SCP-01 | 1099 × 36 | 119 | The job BOM (main artifact of this workbook) |
| Clean BOM | 60 × 25 | 2 | Submittal/pick-list export — **header only, never populated** |
| IO - Control Panel | 1002 × 12 | 101 | DI/DO channel map — channels listed, descriptions/signal types **blank** |
| Load Calc | 997 × 23 | 58 | Load calculation worksheet feeding FLA/MCA/MOCP |
| Categories | 30 × 2 | 30 | Reference list of QBO product categories (lookup) |

## BOM - SCP-01: the bar logic in this file

The BOM uses the purple/red bar convention. Inspecting cell fills:

- **Purple bar = row 12** (fill `FF8E7CC3`). Single full-width purple stripe.
- **Red bar = row 84** (fill `FFE06666`). Single full-width red stripe. The text on row 84 col D reads: **"DO NOT COPY TO SUBMITTAL BOM BELOW THIS LINE"** — explicit author instruction confirming the convention.

So **real BOM rows = R13 through R83 = 70 line items**.

### What lives above the purple bar (R1–R11)

Header / metadata only. Not BOM items.

- R2–R3: Initials / Date / Notes change-log row ("MB / 2026-05-01 / Original genuine draft").
- R9: column headers — `Tag | Part # | Description | Manufacturer | Qty | Category | Price/Unit | Ext. Cost | PO# | PO Date | Ship Date | Supplier`.
- R10–R11: stray category lines ("Protection Devices", "Terminal Blocks") with no part numbers — these are the "made-up section headers" mentioned in the data rules. Excluded.

### What lives between the bars (R13–R83) — REAL BOM, 70 rows

All 70 rows have a part number. Total individual unit qty across the BOM = **407**. Category breakdown:

| Category | Rows |
|---|---|
| Protection Devices | 23 |
| IO Devices | 7 |
| Terminal Blocks | 6 |
| Buttons & Lights | 6 |
| Relays | 5 |
| Power Supplies | 4 |
| Enclosure | 3 |
| Contactors | 3 |
| Panel AC & Heating | 3 |
| Transformers | 3 |
| Hardware | 3 |
| Controllers | 2 |
| Networking | 1 |
| Labeling | 1 |

Columns 7–13 (Category / Price / Ext. Cost / PO# / PO Date / Ship Date / Supplier) are mostly populated — this is a working purchase-tracking BOM, not just a parts list. Only the enclosure rows (R13–R15) and Saginaw items have PO# `1213` and PO Date 2026-05-12; ABB rows have prices but no PO# yet, consistent with the proposal-stage status of the job.

### What lives below the red bar (R84–R119) — EXCLUDED

Per data rules: these are removed-for-posterity rows or "fudges" (wire, cable tray, consumables, labor).

- **R84**: red separator with "DO NOT COPY TO SUBMITTAL BOM BELOW THIS LINE".
- **R85–R92** (orange fill `FFF6B26B`): **wire fudges** by gauge — "400 KCMIL Black", "1 AWG Black", "#10 AWG Black", "#14 AWG Black", "#18 AWG Black/White", "#8 AWG Black/White". No qty / no price. These are placeholders for wire spool consumption.
- **R93–R96**: Wago wire tray (4×3, 4×1, 4×2.5). Tray is cable management consumable — sits below the red line as a fudge.
- **R97–R101**: line-item fudges with hardcoded prices — "Panel CNC cutouts" $255, "Labels" $200, "Hardware" $420.69, "Wire" $850, "UL" $1850. These are lump-sum cost allocations, not parts.
- **R103** (dark gray fill `FF666666`): second separator bar before the labor block.
- **R110–R114**: labor lines — Engineering 12 hr, Drafting 20 hr, Assembly 60 hr, QA & Testing 8 hr, Shipping Prep 4 hr.
- **R116–R118**: roll-up to Material / Labor / Total / Sell. Sell = $35,654.67 (matches the figure that also appeared in R3 col K of the header zone — that is the "preview" of total sell cached at the top for quick scan).

**Rows excluded from BOM count: ~30 rows of fudges + labor + totals.**

## Cross-sheet observations

### Customer naming inconsistency (flag)

- Panel Notes sheet (R2): Customer = **"Vitalis"**, Attn = Jacob Vanzella.
- RFQ Project Info: Contractor = **"Classic Refrigeration"**, Contact = Jacob Vanzella.
- Panel Notes R6 email text: "This will be a standard **Classic** build with a system manager, 65kA SCCR..."

Most likely reading: Vitalis is the end-user / store owner (Northgate Markets brand maps to Vitalis?), Classic Refrigeration is the contractor doing the install, Jacob Vanzella is the same human contact. But this is worth flagging because the two sheets disagree on the customer name and a parts inventory file titled "**Vitalis** Control Parts Inventory" sits alongside.

### MS165 sizing disagreement (flag — important)

This is a concrete contradiction between two artifacts:

- Main BOM (R19): **MS165-65** (52–65 A range) for MT compressors, qty 4
- Motor_Protection_Selections_NG49-53-54.xlsx Selections Summary R5–R8: **MS165-54** (40.0–54.0 A range) for the same MT1-MT4 compressors
- The Motor Protection BOM tab (R7) also lists **MS165-54 qty 4** for NG49

Same panel, same motors, two different MMP selections. With an FLA of 51.1 A, the MS165-54 (range 40–54) is the tighter / lower-overhead fit, but lands the FLA at the very top of its band; the MS165-65 (range 52–65) gives headroom but puts FLA below the bottom of the band — also questionable. Worth flagging as a possible engineering inconsistency between two human authors of two artifacts in the same packet.

### Empty downstream artifacts

- **Clean BOM** has only the header row populated. This is the published/submittal-grade BOM and it's empty — the BOM workflow stops at SCP-01 in this packet.
- **IO - Control Panel** has channel numbers 1–96+ enumerated for DI and DO columns but every Description, Signal Type, and Voltage cell is blank. The IO map is a blank shell at this stage.
- **Drawings/** folder is empty.

### Load Calc shape

Standard load-calc table starting with 208 VAC / 3Φ section. R5–R6 list two transformers (1 kVA 208/120, 500 VA 208/24). Real rows ~58. This sheet feeds FLA/MCA/MOCP that appear up in RFQ Project Info.

## Naming conventions observed

- Sheet names mix " - " and " - " separators ("BOM - SCP-01") with title case. Spelling consistent within this workbook.
- "SCP-01" — Single Control Panel #01, presumably. The proposal docx calls the same panel "RCP-01" (Roxsta-Control-Panel? Rack-Control-Panel?). **The BOM tab and the proposal use different panel codes for what appears to be the same panel** — another mild flag.
- Part #, Tag, Description columns standard; PO#, PO Date, Ship Date, Supplier columns reflect purchasing workflow (live, in-progress).
- Category column values match the Categories sheet enum exactly except for the two "header" rows R10–R11 above the purple bar that have a Category value but no Part # — these are the discardable section labels.

## Summary

Main workbook is **well-formed for the BOM tab and partially formed for everything downstream**. BOM is the source of truth; Clean BOM, IO, and Drawings are placeholder shells. Bar logic is honored cleanly: 70 real BOM rows between R12 (purple) and R84 (red), ~30 fudge/labor/total rows excluded below. Two cross-artifact contradictions worth tracking (MS165 sizing, panel code SCP-01 vs RCP-01, customer name Vitalis vs Classic).
