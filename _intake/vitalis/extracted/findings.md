# Vitalis Cross-Job Findings — Drift, Mismatches, Open Questions

Cross-job synthesis flags across **E1392, E1395, E1399, E1404**. All four
intake packets are human-produced: errors are real, this document logs them,
nothing is silently reconciled. Citations point to per-job prior-analysis
files under `_intake/vitalis/extracted/prior-analyses/<job>/`.

## How to read

Findings are grouped by category. Each finding carries:
- **Job(s):** which sample job(s) the finding lives in.
- **Severity:** P0 = blocks a build / ship, P1 = needs human resolution
  before generalization, P2 = housekeeping / convention drift.
- **Evidence:** file + section anchor.

## 1. Panel-tag drift (one panel, multiple identifiers)

### 1.1 MB0217 vs MB0216 on E1392 PO Order Acknowledgement (P1)
- Evidence: `E1392/supplemental.md § Anomalies / observations` on `PO# P-37066 - Order Acknowledgement.xlsx` row 30 says `Job ID: MB0217` while every other artifact says MB0216.

### 1.2 SCP-01 vs RCP-01 on E1404 (P1)
- Evidence: `E1404/xlsx-profile.md § Customer naming inconsistency` — BOM sheet `BOM - SCP-01` vs proposal `RCP-01` for the same panel.

### 1.3 Vitalis vs Classic on E1404 (P2)
- Evidence: `E1404/xlsx-profile.md § Customer naming inconsistency` — Panel Notes "Vitalis", RFQ "Classic Refrigeration", Panel Notes R6 email body "standard Classic build".

### 1.4 Job-ID placeholders never substituted (P2)
- Evidence: E1399 RFQ filename `EXXXX RFQ XXXXX.xlsx` + cell `[JOB ID]` (`E1399/lifecycle.md § Stage 1`); E1404 `NG49 - MB0221 - EXXXX RFQ XXXXXX.xlsx`; E1395 Job Tag `PO# P-XXXXX` after P-38262 issued.

## 2. BOM-vs-proposal drift

### 2.1 E1392 sell price gap $45,615.96 (proposal) vs $43,751.25 (XLSX) — Δ $1,864.71 (P1)
- Evidence: `E1392/process-docs.md § 2. Panel Proposal` + `E1392/xlsx-profile.md § Anomalies`.

### 2.2 E1392 BOM "Notes" date cell holds the sell price 43751.249 (P2)
- Evidence: `E1392/xlsx-profile.md § Purple / red bar rule` row 3 — original-draft date unknown.

### 2.3 E1392 Rittal depth: 700 mm (BOM) vs 500 mm (proposal) (P1)
- Evidence: `E1392/feature-parts-association.md` row 31 — 200 mm enclosure-depth delta.

### 2.4 E1395 customer requested 100 kAIC, panel shipped 65 kAIC (P1)
- Evidence: `E1395/xlsx-profile.md § Panel Notes` — downgrade recorded only as strikethrough in pasted email body.

## 3. BOM-vs-drawing / BOM-vs-OA drift

### 3.1 E1395 Danfoss module swap (103A→101A) in wire-changes, BOM unchanged (P1)
- Evidence: `E1395/process-docs.md § 3. Danfoss Wire Changes.docx` + `E1395/feature-parts-association.md` — BOM still has 2× 103A and 1× 101A.

### 3.2 E1395 safety relay added in drawings but absent from BOM (P1)
- Evidence: `E1395/feature-parts-association.md § Features absent` — drawing rev L revision table says "ADDED IN SAFETY RELAY".

### 3.3 E1395 MMIGRS2 HMI in drawings + inventory but absent from BOM (P1)
- Evidence: `E1395/feature-parts-association.md` — drawing sheet 67 "HMI"; Danfoss Inventory qty 3.

### 3.4 E1395 EKE 1C superheat controllers in Danfoss Inventory but absent from BOM (P2)
- Evidence: `E1395/feature-parts-association.md § Features absent`.

### 3.5 VFD parts absent from BOM in all 4 jobs (P1)
- Evidence: every per-job feature-parts-association.md flags VFD absence despite Load Calc / RFQ VFD compressor count.

### 3.6 E1399 legend-plate count: 18 (BOM) vs 33 (Legend Plates sheet) (P1)
- Evidence: `E1399/feature-parts-association.md` + `E1399/part-feel.md`.

### 3.7 E1399 tag PC54071 reused on R15 (AK-OB 110) and R17 (AK-PC 782B) (P1)
- Evidence: `E1399/feature-parts-association.md` row PLC / controller.

### 3.8 E1399 live `=AI()` placeholder formulas in shipped BOM rows R31-R40 (P1)
- Evidence: `E1399/xlsx-profile.md § Real BOM Observations`.

### 3.9 E1395 Load Calc part-number drift CDS351B vs CDS301B on LT compressors (P2)
- Evidence: `E1395/xlsx-profile.md § Self-inconsistencies inside Load Calc`.

### 3.10 E1404 motor-protection BOM upsized vs supplemental — RESOLVED (Randall + Jones, 2026-05-24)

**Not a drift; deliberate engineering judgment.** The Motor Protection Selections supplemental was AI-generated and sized to bare motor FLA. Randall upsized the BOM per **UL508A SB4 120% rule** — the MMP's max adjustable trip rating must be ≥ motor FLA × 1.20 (20% headroom for transients, harmonics, aging). Math verified:

| Circuit | FLA | × 1.20 | Supplemental MMP | Max trip | UL508A | BOM MMP | Max trip | UL508A |
|---|---|---|---|---|---|---|---|---|
| MT | 51.1 A | 61.32 A | MS165-54 | 54 A | ❌ fails | **MS165-65** | 65 A | ✓ passes |
| LT NG49 | 9.84 A | 11.81 A | MS132-10 | 10 A | ❌ fails | **MS132-16** | 16 A | ✓ passes |

Contactor frame upgrades (AF65, AF16) follow the MMP frame to match line-side rating. The AI supplemental cannot be authoritative for motor-protection sizing without enforcing UL508A.

**Implication:** `selection-rules.yaml` axis 4 (`motor_protection_branch_topology`) updated to encode the 120% rule as the sizing input rather than "frame matched to FLA."

- Evidence: `E1404/part-feel.md § Cross-check vs Motor Protection supplemental` (the discrepancy itself) + Randall confirmation (2026-05-24) + UL508A SB4.

### 3.11 E1404 CA4-10 aux block count differs between artifacts (P2)
- Evidence: `E1404/part-feel.md § Cross-check` — BOM qty 12 single row vs supplemental 9 split rows with trailing-space hacks.

### 3.12 E1392 BOM row "RHE XT5 F/P STAND. RETURNED" with non-zero qty (P2)
- Evidence: `E1392/feature-parts-association.md` row 37.

## 4. BOM-vs-Load-Calc drift

### 4.1 E1392 MPW100 qty 3 vs 2 across-the-line MT1 compressors (P2)
- Evidence: `E1392/feature-parts-association.md` row 40 + § Open questions.

### 4.2 E1392 CR7071/CR7072 qty 3 for 2 listed tags (P2)
- Evidence: `E1392/feature-parts-association.md` row 59.

### 4.3 E1395 MT1-2 trip 250 A vs MT3-4 trip 200 A, same FLA (P1)
- Evidence: `E1395/feature-parts-association.md` row MT compressor circuits + `E1395/part-feel.md § MT trip-current mystery`.

### 4.4 E1392 FLA totals 286.4 A (RFQ) vs 293.4 A (dC Load Calc) — 2.4% discrepancy (P2)
- Evidence: `E1392/supplemental.md § Anomalies / observations`.

## 5. Incomplete process docs

### 5.1 No Fab Packet, no QC results, no As-Built BOM in any of the 4 jobs (P1)
- Evidence: per-job `process-docs.md` + `lifecycle.md`.

### 5.2 E1392 QC checklist describes a different panel — DOWNGRADED to P1 (Randall, 2026-05-24)

**Wrong checklist file got attached to the job folder — housekeeping bug, not a process failure.** QC was run against a different doc or by memory; the file on record is just the wrong file. Treat as P1 housekeeping going forward (still worth resolving because the file-on-record is misleading, but not a build-block).

- Evidence: `E1392/supplemental.md § 3. QC Program` — 460V/9comp/75HP/Danfoss/XT6 700A vs E1392's 208V/5comp/84.6A/Copeland/XT5N 400A.

### 5.3 E1404 Vitalis Parts Inventory is NOT a master parts list (P1)
- Evidence: `E1404/supplemental.md § 1. Vitalis Control Parts Inventory` — 11 stock rows, only Danfoss+Copeland, references E-1395/E-1399 (not E-1404).

### 5.4 IO sheet empty in all 4 jobs while drawings claim to match it (P1)
- Evidence: per-job `xlsx-profile.md § IO - Control Panel`.

### 5.5 Photo-count drift between sister SOPs (E1395) (P2)
- Evidence: `E1395/process-docs.md § Cross-cutting observations` — Fab Packet 2 photos vs QC Program 7 photos.

### 5.6 Daily drawing revisions with no textual changelog (P2)
- Evidence: `E1392/lifecycle.md § Drawings` (0→K in 30 days); `E1399/lifecycle.md § Stage 4` (A→G in 8 days).

### 5.7 Customer redlines arriving as iPhone photos (E1392) (P2)
- Evidence: `E1392/lifecycle.md § Stage 5` — `Drawings/Red lines/IMG_0331..0336.HEIC`.

### 5.8 UPS small-parcel label for a 72x60x18 enclosure (E1399) (P2)
- Evidence: `E1399/lifecycle.md § Stage 5 Shipping`.

## 6. Ambiguous / low-confidence parts

### 6.1 All Wago small-TB rows are estimates per bedrock rules (P1)
- Evidence: every per-job `part-feel.md` flags rows 88-99 (E1392), r78-r83 (E1395), 14 rows (E1399), R76-R81 (E1404) as LOW-CONFIDENCE. Common SKUs: 249-117, 2002-3227, 2002-1201, 2002-3201, 2006-1201, 2002-3217, 210-112, 788-113.

### 6.2 Wago part qty/unit-cost null on PO data (P2)
- Evidence: `_intake/vitalis/extracted/po-summary.json` POs 1160, 1202, 1208 — Wago lines frequently null on qty/cost; PO 1208 qty=3201 and qty=3227 look like part-number suffixes leaking into the qty column.

### 6.3 Tag-collision and category-inconsistency on E1392 (P2)
- Evidence: `E1392/xlsx-profile.md § Anomalies / flags` — IB MPW100 tagged "Contactors", 709-591 drawer tagged "Hardware", DISC2011 tag repeats across rows 35-37.

### 6.4 CO2 sensor implicit in IO channel allocation (E1404) (P2)
- Evidence: `E1404/feature-parts-association.md § Notes & open questions`.

### 6.5 Finder LED light 230 V variant in a 120 V panel (P2)
- Evidence: `E1395/part-feel.md` row 49 — 7L.43.0.230.1100 in a 120 V control bus.

### 6.6 SPD absent from a 460 V industrial panel (E1399) (P2)
- Evidence: `E1399/feature-parts-association.md § Features looked for but NOT FOUND`.

## 7. PO-summary cross-checks

### 7.1 Reuse of common SKUs across jobs (informational)
- Evidence: `po-summary.json` parts_catalog — 2702324 (FL Switch) on POs 1158, 1188, 1203; 9070T50/T500D19 on POs 1170, 1188, 1203; UPS+battery on POs 1170, 1188, 1203; Littelfuse fuses on POs 1171, 1189, 1199, 1215.

### 7.2 PO 1189 (E1392) ordered TR50VA0 without price (P2)
- Evidence: `po-summary.json` PO 1189 line 3 — qty 5, unit_cost=null, amount=null.

### 7.3 PO 1217 (E1395) only has 3 line items vs the 71-row BOM (informational)
- Evidence: most of E1395 BOM ordered via cross-job consolidated POs (1171, 1188, 1197, 1199, 1203, 1208).

### 7.4 PO 1197 covers BOTH E1395 and E1399 enclosures (informational)
- Evidence: `po-summary.json` PO 1197 file name `PO#1197 - SCE - dC E1395 & E1399 042426.pdf`.

## 8. Topology-level open questions

### 8.1 Refrigeration controller family sample skewed 1:3 (synthesis caveat)
- E1392 = Copeland E3; E1395/E1399/E1404 = Danfoss AK. Copeland-side invariants are stuck at single-job confidence.

### 8.2 Pilot family correlates with voltage, not controller (synthesis observation)
- Schneider XB family in E1392 (208 V Copeland) AND E1395 (208 V Danfoss). ABB CL2/M2SS family in E1399/E1404 (both 460 V Danfoss). Pilot family may be voltage-driven, not controller-driven.

### 8.3 Enclosure brand 3:1 Saginaw:Rittal (synthesis observation)
- E1392 is the only Rittal job. Either customer-specific (Canada location?) or sourcing-driven.

### 8.4 ABB vs WEG motor-protection topology 1:3 and clustered (synthesis observation)
- Only E1404 uses ABB; clustered with NG53/NG54 via cluster supplemental. ABB topology may be a specific contract feature.

### 8.5 Compressor count drives 80% of BOM quantity variance (synthesis observation)
- E1392: 5 / 78 rows; E1395: 7 / 71; E1399: 9 / 74; E1404: 6 / 70. "2 A workhorse breaker = qty 16" in 3 of 4 jobs.

### 8.6 RFQ FLA vs dC Load Calc FLA — which is authoritative? (synthesis observation)
- See § 4.4.

### 8.7 E1399 pre-purple stray rows R11-R12 look like leftover scratch (P2)
- Evidence: `E1399/xlsx-profile.md § BOM bar rule applied` — entries above purple bar; per rule ignored.

## 9. Bedrock-rule compliance audit

All 4 prior analyses honored the bedrock rules (purple/red bar, Wago low-confidence, log-don't-fix, fab packets are shells). This synthesis honors the same rules.

## 10. Gaps where more source docs would unblock further synthesis

1. A second Copeland-controller job.
2. The cluster-level `MMP_Contactor_Type_1_Coordination` spreadsheet that E1404's supplemental references.
3. A populated IO sheet for any job (would convert sel-rules axes 4 and 9 from descriptive to derivable).
4. An actual As-Built BOM for any job.
5. Per-PO job tagging for `po-summary.json` (to compute per-job material totals and close § 2.1).
6. RFQ Panel Options toggle values in machine-readable form per job.
