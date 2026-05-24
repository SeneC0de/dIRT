# E1399 — Supplemental XLSXs

Two XLSX files exist beyond the main engineering workbook:

## 1. `RFQ/YCH Roxsta G6 MB0206 - EXXXX RFQ XXXXX.xlsx` (319 KB)

The dAPP project-intake template. **9 sheets**:

| Sheet | What it is |
|---|---|
| Project Info | Customer + brand + interface + contractor capture. **Still has `[JOB ID]` and `#VALUE!` cells — never resolved to E1399.** |
| Panel Options | Add-on toggles (UPS, energy meter, ethernet switch, machine-stop, spare 8/8 IO). For this job: **Ethernet Switch = TRUE, Machine-Stop = TRUE; UPS = FALSE.** |
| Input Power List | Validation list — 3 voltage choices (460/208/575 VAC 60 Hz). |
| Logos | Brand-logo cross-reference for the cover sheet (Danfoss, Copeland, Vitalis Std, Classic Ref). |
| FLA Reference Material | UL Table 50.1 full-load amps lookup, 237 rows. Static reference. |
| MCA Reference Material | Two-row stub referencing UL 1995. |
| MOCP Reference Material | Two-row stub referencing UL 1995. |
| NEC 240.6A | Standard fuse/breaker amp ratings list. Static reference. |
| Wire Ampacity | AWG-to-ampacity / OCP lookup, 233 rows. Static reference. |

**Verdict:** intake-form-as-spreadsheet. The interesting data (Panel Options TRUE/FALSE flags) drives downstream BOM selection (Ethernet Switch FL-2000 → BOM row 57; Machine-Stop XB5AS8444 → BOM row 61). The placeholder leakage in filename and `Estimate #` field is the seam.

## 2. `PO/PO# P-38256 - Order Acknowledgement.xlsx` (17 KB)

dAPP-generated PO acknowledgement. **1 sheet** ("Purchase order"), single line item, $42,535.42. Mirrors `Purchase Order - P-38256.pdf` content. PO date 2026-05-04, ship date 2026-05-21, NET 30, FOB Cumming GA Ex-works, ship-to Vitalis Plant 3 Kelowna BC.

**Verdict:** standard ack template. Useful as the canonical source of {PO#, panel tag MB0206, estimate # E1399, contact Pouya Yazdchi, ship date}.

## Nothing else
No supplemental BOM, no submittal worksheet, no costing breakdown, no IO map, no test data XLSX. The main workbook + these two are the entirety of structured data for E1399.
