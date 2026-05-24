# Supplemental XLSXs — E1392 / 4S Ranch

The job folder contains three XLSXs beyond the main `E1392 - 4S Ranch.xlsx`. Schema, purpose, and reusable-master assessment for each.

## 1. `RFQ/Classic 4S Ranch - EXXXX RFQ 031626.xlsx` (1.3 MB)

**Purpose:** customer's RFQ workbook (Classic Refrigeration → dC). Note filename retains placeholder "EXXXX" — predates assignment of E1392.

**Sheets (8 total):**

| Sheet | Rows × Cols | Populated | Purpose |
|---|---|---|---|
| Project Info | 35 × 29 | 159 | The actual RFQ form — contact, brand (Copeland), interface (E3), customer (Classic Refrigeration), date 03/16/26, panel tag MB0216, location San Diego CA, incoming 208V 3ph+E, SCCR 65 kAIC, NEMA 3R sheet-steel, FLA 286.41, MCA 307.56, MOCP 392.16, largest motor FLA 84.6. Plus a per-motor list: MT1 (VFD), MT2, MT3 across-the-line, MT4 disabled; LT1 (VFD), LT2 across, LT3/LT4 disabled. Plus transformer roster: 3 kVA 120 + 500 VA 24 + 5× 50 VA 120/24. Toggle flags: UPS = TRUE, 6"legs/18"D = FALSE, Energy Meter w/ Rogowski = TRUE, Ethernet Switch = TRUE, Machine Stop Button = FALSE. |
| Input Power List | 4 × 2 | 3 | Drop-down values: 460V, 208V, 575V 3-phase. |
| Logos | 992 × 3 | 14 | Image placement sheet (mostly empty rows). |
| FLA Reference Material | 1003 × 26 | 510 | UL Table 50.1 transcription — FLA by HP and voltage (1/10 HP up). **Reusable master — generic reference data, not job-specific.** |
| MCA Reference Material | 22 × 16 | 3 | Header only. Empty reference shell. |
| MOCP Reference Material | 31 × 7 | 2 | Header only. Empty reference shell. |
| NEC 240.6A | 27 × 1 | 27 | NEC 240.6(A) standard fuse ampere ratings list. **Reusable master.** |
| Wire Ampacity | 1000 × 26 | 181 | Copper wire ampacity table (NEC 310-style) — AWG, mm², 60°C/75°C/90°C, MOCP, conductor size. **Reusable master.** |

**Anomalies / observations:**
- The Project Info sheet has multiple `#VALUE!` errors at cells A2, B2, C2, E3, E7, E9, A10, C12, A17 — broken formulas. The customer workbook ships with errors.
- Filename still says "EXXXX" — customer-side RFQ template hasn't been renamed once the dC estimate # was assigned.
- The customer-side total FLA 286.41 vs dC Load Calc (main XLSX) 293.40 — small difference (~7 A or 2.4 %) suggesting either rounded transformer math or one extra small load on the dC side. **Flagged.**
- Largest motor FLA 84.6 matches main XLSX.
- This is the upstream "spec" — every parameter on Panel Notes derives from this sheet.

**Reusable-master rating:** **HIGH** for the three reference sheets (FLA Reference / Wire Ampacity / NEC 240.6A) — these are generic engineering tables and could be lifted into a project-wide reference dataset. The Project Info sheet is per-job and not reusable.

---

## 2. `PO/PO# P-37066 - Order Acknowledgement.xlsx` (17 KB)

**Purpose:** order-ack form sent back to customer after PO received. The PDF (`PO# P-37066 - Order Acknowledgement.pdf`) is the printable version of this sheet.

**Sheets (1 total):**

| Sheet | Rows × Cols | Populated | Purpose |
|---|---|---|---|
| Purchase order | 34 × 9 | 56 | One-page order-ack form. Header line "Order Acknowledgement", date 04/01/26, estimate E1392, job "4S Ranch Roxsta G6", PO P-37066, ship date 05/14/26, terms NET 30, ship via Ex-works, FOB Point of Origin (Freight Collect). Vendor: dAPP Controls 2450 Freedom Pkwy Cumming GA 30041, ph 717-668-7879. Ship-to: **Vitalis Plant 3, Velocity, 3488 Velocity Ave, Kelowna BC V1V 3C2, Canada**. Line 1: SCP-01 Roxsta G6 Rack Control Panel, qty 1, $45,615.96. |

**Anomalies / observations:**
- **Job ID line at row 30 says "Job ID: MB0217"** — but the panel tag throughout every other doc is **MB0216**. Off by one. Either this order-ack was based on the next sequential job, or someone fat-fingered "16" → "17". **Flagged as a finding.**
- "Attention to: Marjorie Liesch" appears at row 32 — customer contact name on this artifact differs from "Jacob Vanzella" in the RFQ and proposal. Likely the purchasing contact vs the engineering contact, but still worth noting.
- Ship date 05/14/26 in the order-ack, actual ship/invoice date 05/13/26 — one day early.
- Address: Vitalis Plant 3 is in **Kelowna, BC, Canada**. International shipment. Affects shipping/freight/customs treatment.
- Scope bullet list matches the proposal almost exactly, including "Additional Copeland 88 I/O board wired to spare terminals" — but adds "with battery backup" wording and renames "Energy Meter" line slightly.

**Reusable-master rating:** **None.** Job-specific form.

---

## 3. `QC/QC_Checklist_VITALIS.xlsx` (70 KB)

**Purpose:** customer-branded final pre-ship QC checklist, "Rev E (5/8/2026)". The .pdf is the printed version.

**Sheets (14 total):**

| Sheet | Rows × Cols | Populated | Purpose |
|---|---|---|---|
| 00_Cover | 33 × 2 | 52 | Cover with panel specs, instructions, philosophy, legend. |
| 00_All_Items | 292 × 12 | 2589 | Master list — every individual P2P (point-to-point) check across all categories. AutoFilter-ready. |
| 01_Power_Main_SCCR | 20 × 11 | 134 | 15 checks — main breaker, lugs, PE bus, SCCR docs, phase rotation. |
| 02_Motor_Branch_Power | 69 × 11 | 528 | 64 checks — per-compressor branch wiring (×9 compressors). |
| 03_Control_Power | 24 × 11 | 166 | 19 checks — control xfmrs, PSUs, UPS. |
| 04_Safety_Chain | 86 × 11 | 664 | 81 checks — per-compressor 4-sheet safety pattern. |
| 05_Machine_Safety | 11 × 11 | 64 | 6 machine-wide safety / general controls. |
| 06_VFD_Signals | 45 × 11 | 336 | 40 checks — VFD signal circuits, 4 VFDs × 6-term X-strip. |
| 07_Sensors | 26 × 11 | 172 | 21 sensor / transducer / level probe checks. |
| 08_Valves_Pumps | 20 × 11 | 129 | 15 valve/actuator/pump checks. |
| 09_Controllers | 18 × 11 | 120 | 13 checks — **Danfoss AK-PC-782B + expansion modules**. |
| 10_Alarms | 9 × 11 | 45 | 4 alarms / Motor Room checks. |
| 11_Door_Layout | 16 × 11 | 104 | 11 door/enclosure/layout checks. |
| 99_Sign_Off | 28 × 6 | 99 | Live counts per category + signature lines. |

**Critical anomaly — this QC checklist is for a DIFFERENT panel:**

| Spec | This QC checklist | E1392 actuals |
|---|---|---|
| Power input | **3Ø+PE, 460 VAC, 60 Hz** | 3Ø+PE, **208 VAC**, 60 Hz |
| FLA | 577 A | 293.4 A (Load Calc) / 286.4 A (RFQ) |
| MCA | 596 A | 314.6 A / 307.6 A |
| MOCP | 673 A | 399.2 A / 392.2 A |
| Largest motor | 75 HP | 84.6 FLA (~25 HP @ 208 V 3ph) |
| Compressor count | **9** (5 MT + 4 LT) | **5** (3 MT + 2 LT) |
| Main breaker | **ABB XT6 700 A** (CB2031, XT6HU3800EFF000XXX) | ABB XT5N 400 A (DISC2011, XT5NU330ABFF000XXX) |
| Controller | **Danfoss AK-PC-782B** | **Copeland E3 RX** |
| Drawing page count | 84 pages | 80 pages |
| Section prefix list | B0/B1–B5, G0/G1–G4, L1, M0/M1, P1, R1, S1, S2, MR | B0, G0, M1, R1, S1, S2 (no B5, no G4, no L1, no P1, no MR) |
| VFD compressor list | B1, B2, G1, G2 (4 VFDs) | B1-2U1, G1-2U1 (2 VFDs per Load Calc) |

This is a Rev-E (dated 5/8/2026) QC document for a much larger panel — possibly another Vitalis job. The fact that the QC file lives in the E1392 folder while clearly describing a different panel is a strong signal that:

(a) `QC_Checklist_VITALIS.xlsx` is a **per-customer master template** kept in every Vitalis job folder, but it was last edited / customized for a different job (the 460 V 9-compressor one), or
(b) E1392 was meant to be QC-checked against a different / blank version of this template and the wrong copy was placed in this folder.

**Either way, this QC checklist as-shipped does not match E1392.** No data was filled in (all P/F/N-A columns blank, totals show 289 outstanding / 0 pass/fail). **Flagged as a finding.**

The internal philosophy and structure of the checklist is sound (CRIT / HIGH / MED / LOW, ACADE wire convention `<sheet><line><wire>`, per-compressor 4-sheet safety pattern, VFD 6-position X-strip rule) and could be a great basis for an E1392-specific version — but as filed it would mislead anyone who pulled it as authoritative.

**Reusable-master rating:** **VERY HIGH** for the underlying *structure* — the checklist's category schema and severity-coded point-to-point format is a strong template across jobs. But the **content** must be regenerated per job; the current copy is from a different panel and is misleading in this folder.

---

## Summary

| File | Type | Job-specific? | Reusable master? |
|---|---|---|---|
| Classic 4S Ranch RFQ | Customer RFQ (Classic Refrigeration) | Partially — Project Info per-job, reference sheets (FLA / Wire Ampacity / NEC 240.6A) are generic | YES for the 3 reference sheets |
| PO# P-37066 Order Ack | dC order acknowledgement | Yes (per-job) | No |
| QC Checklist VITALIS | QC checklist template (currently populated with content from a DIFFERENT panel — 460 V 9-comp) | No — file is mis-keyed: lives in E1392 folder, describes a different panel | Structure: YES. Current content: NO. |

**Flagged findings emitted via events:**

1. Job ID mismatch on PO Order Ack — says **MB0217** while every other artifact says **MB0216**.
2. QC checklist describes a 460 V 9-compressor 75-HP panel with Danfoss controllers and ABB XT6 700 A main — completely different machine from E1392 (208 V, 5 comp, 84.6 A largest, Copeland E3, ABB XT5 400 A). Filed in the wrong folder or the wrong template was branded "VITALIS" without regenerating for this job.
3. RFQ Project Info sheet ships with several `#VALUE!` formula errors.
4. FLA totals: customer RFQ 286.4 A vs dC Load Calc 293.4 A — 7 A / 2.4 % discrepancy.
