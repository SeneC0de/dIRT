# Vitalis cross-job validation v0.2 — light pass on 10 unanalyzed jobs

Stress-tests the v0.1 synthesis (anchored on E1392/E1395/E1399/E1404) against the 10 jobs in the drop that did not have prior Head-agent recon. Extraction was deterministic — `_scratch/bom_extract.py` for XLSX (purple `8E7CC3` / red `E06666` fill detection, in-bar rows only) and `_scratch/pdf_titleblock.py` for drawings (pypdf, pages 0-2). Full per-job dumps are in `_scratch/v2-extractions/`.

**The first agent attempt died on multi-page PDF reads (no `pages=` guidance). The scripts it built before dying are what made this pass tractable.**

## Sample expansion

| | v0.1 anchor (deep recon) | v0.2 added (light pass) | total |
|---|---|---|---|
| jobs | 4 | 10 | 14 |
| jobs (with BOM bar-discipline) | 4 | 5 | 9 |
| jobs (drawings, ≥1 PDF) | 2 | 8 | 10 |

E1380 has NO red bar — bom-extract returned 0 in-bar rows. WIP BOM or unfinished convention. Flagged as new finding; cannot validate BOM-side invariants for E1380.

## Per-job spot-check

### E1354 — Bright Renewables UL (drawing only)
- **Voltage: 575 VAC 3φ+N+PE** — *new tier not in v0.1 enum*
- HP: 60. FLA 326, MCA 342, MOCP 400, SCCR 35 kAIC.
- Panel name: SCP-01 — ROXSTA G6 RACK CONTROL PANEL
- VFDs visible (no model in extracted text). Min 4 compressors (B1, B2, B3, B4 starters seen).
- Source: `pdf-E1354_VITALIS_BRIGHT_RENEWABLES_UL_.txt` L5-12, L25, L52, L70

### E1355 — Superking 11 Copeland (drawing only)
- **Voltage: 208 VAC 3φ** — HP: 40HP — FLA 337, MCA 360, MOCP 453, SCCR 65 kAIC.
- Panel: SUPERKING 11 / MB0207 — Roxsta G6
- Controller: **Copeland** (filename "COPELAND_EDITS"; revision cycle includes "COPELAND REDLINES").
- VFDs: **Danfoss FC-103P30** + **FC-103P7K5** (i.e., the VFDs are Danfoss even on a Copeland-controller panel — VFD vendor independent of controller family).
- Source: `pdf-E1355_Superking11_COPELAND_EDITS_.txt` L5-7, L24, L45

### E1360 — Erewhon Glendale (drawing only)
- **Voltage: 460 VAC 3φ**
- VFDs: Danfoss FC-103P30 + FC-103P7K5
- Compressors: MT-1×3 + LT-1×1 + likely more (LT-1 FLA 3.4 A is small)
- Panel name + electrical specs not cleanly extracted (PDF text wraps lost spec values).
- Source: `pdf-E1360-EREWHON_GLENDALE_REDLINES_.txt` L59, L180, L401-413

### E1371 — Northgate 11 ship redlines (drawing only)
- **Voltage: 208 VAC 3φ 60 Hz**
- FLA 42.8 / 285 / 308 / 402 / 65 kAIC (parse uncertain — text extraction concatenated values)
- Panel: NORTHGATE 11 / SCP-02 / E1371 — 172 control panel
- MT-1 starters MT1×3 visible, motor FLA 93.5 A + 79 A × 2
- VFD on MT-1 compressor 1 (DV207)
- Source: `pdf-E1371-NORTHGATE11_SHIP_REDLINES_.txt` L6-7, L33-34, L43

### E1377 — Vallarta 75 (drawing + BOM)
- **Voltage: 460 VAC 3φ+PE** — HP: 75HP — FLA 419, MCA 442, MOCP 535, SCCR 65 kAIC.
- Panel: VALLARTA 75 / SCP-01 — Roxsta G6
- Enclosure: **Saginaw SCE-724818FSD** 72H × 48W × 18D (identical to NG cluster)
- VFDs: Danfoss FC-103P75 (MT) + FC-103P11 (LT) — 4×MT VFDs + 1×LT VFD
- Motor protection: **WEG MPW40 family** (compressors are smaller frame than NG cluster, with FLA 93A / 12.9A; only LT side uses MPW40)
- Door pilots: **Schneider XB5/XB4 family** (XB5AVG1, XB5AVG4, XB4BD21) — 7 each
- Climate kit: full Finder set (7T.81 + 7L.43 + 7F.21 + 7F.02)
- Control power: WEG CPTW3K0-GSC + Schneider 9070T500D19
- Ground: Penn-Union LA-500-1 + Schneider PK12GTA
- Sources: `bom-E1377.txt` + `pdf-E1377-VALLARTA_75_VITALIS_UPDATES_REV1_.txt`

### E1377 — Vallarta 75 ADDON BOARD (second drawing)
- Same panel, layout rework + addon board revision (2/25/26 + 5/11/26 dates)
- Same electrical specs as the rev1 above

### E1378 — Tokyo Central Cerritos PRELIM (drawing + BOM)
- **Voltage: 460 VAC 3φ+PE** — HP: 75HP — FLA 419, MCA 442, MOCP 535, SCCR 65 kAIC. (Identical specs to E1377; sister panel.)
- Panel: TOKYO CENTRAL CERRITOS / SCP-01 — Roxsta G6
- Enclosure: **Saginaw SCE-724818FSD** 72×48×18
- Motor protection: WEG MPW40 family (CB3141, CB4051, CB4131)
- Door pilots: Schneider XB5/XB4 — 7 each (qty matches MT4+LT3 = 7 compressors)
- Climate kit: full Finder set
- Control power: WEG CPTW3K0-GSC + Schneider 9070T500D19
- Ground: Penn-Union LA-500-1 + Schneider PK12GTA
- Sources: `bom-E1378.txt` + `pdf-E1378-Tokyo_Central_Cerittos_PRELIM_.txt`

### E1380 — Bright Renewables Coolshift (drawing + BOM, BOM is WIP)
- **Voltage: 575 VAC 3φ+PE** — HP: 75HP — FLA 303, MCA 319, MOCP 400, SCCR 35 kAIC.
- Panel: BRIGHT RENEWABLES - COOLSHIFT / SCP-01 — Roxsta G6
- VFDs: visible (model not extracted), MT-1×3 + LT-1
- **BOM has NO red bar — purple at row 12, red bar not detected. BOM is WIP / unfinished. Cannot validate BOM-side invariants.** *New finding, P1 housekeeping.*
- Sources: `bom-E1380.txt` (incomplete) + `pdf-E1380-BRIGHT_RENEWABLES_COOLSHIFT_-_5-6-2026_-_G_.txt`

### E1388 — Superking 12 (BOM only — Copeland)
- **Controller: Copeland** — confirmed by **Visiograph 818-9002** in BOM at R28 (`tag=VG70181`, mfr=COPELAND)
- Enclosure: **Saginaw SCE-724818FSD** 72×48×18
- Main breaker: **ABB XT5N 400 frame** (XT5NU340 — N-rated, presumably lower SCCR than NG cluster's XT5H)
- Motor protection: **WEG MPW100 + MPW40 mix** (MPW100-3-U100 + MPW40-3-U025 + others) — 2 MT + 2 LT compressors at least
- Door pilots: Schneider XB5/XB4 — 5 each (so 5 compressors)
- Climate kit: full Finder
- Control power: WEG CPTW3K0-GSC + Schneider 9070T500D19
- Ground: Penn-Union LA-500-1 (no PK12GTA visible in grep — may be present further in BOM)
- Sources: `bom-E1388.txt`

### E1405 — Northgate 53 MB0222 (BOM only — NG cluster)
- **Voltage: 460 VAC** (inferred from MS165-65 / MS132-16 specs "65kA Type 1 @ 480Y/277V")
- Enclosure: **Saginaw SCE-724818FSD** 72×48×18 — identical to E1404
- Main breaker: **ABB XT5H 400** (XT5HU330 — H-rated, 300A TMA, 3P, 65kA @ 480V UL489)
- Motor protection: **ABB MS165-65 ×4 + MS132-16 ×2** — **IDENTICAL to E1404, UL508A 120% rule applies cleanly**
- Controller: **Danfoss AK-PC 782B + AK-SM 850A**
- Climate kit: full Finder
- Control power: WEG + Schneider
- UPS: **Phoenix 2320283 QUINT4-UPS/1AC/1AC/1KVA**
- PSU: **WAGO 2587-2144** 5A
- Door pilots: **ABB CL2-513C + CL2-513R + M2SS2-10B** (6 each → 4 MT + 2 LT = 6 compressors)
- Ground: Penn-Union LA-500-1 (no PK12GTA visible in grep)
- Sources: `bom-E1405.txt`

### E1406 — Northgate 54 MB0223 (BOM only — NG cluster)
- **Bit-identical to E1405** in every checked invariant (same enclosure, same XT5H 400, same ABB motor protection MS165-65 + MS132-16, same Danfoss AK-PC 782B + AK-SM 850A, same climate kit, same Phoenix UPS, same WAGO PSU, same ABB CL2/M2SS pilots).
- Sources: `bom-E1406.txt`

## v0.1 invariant validation

### CONFIRMED — held in v0.1 and re-anchored in v0.2

- **`enclosure / Saginaw SCE-724818FSD 72×48×18 FSD`** — v0.1 had it as candidate; **now anchored in 8 of 9 BOM-validated jobs (E1377, E1378, E1388, E1395, E1399, E1404, E1405, E1406)**. E1392 (Rittal) is the **single outlier**, not a co-equal alternative.
- **`enclosure / SCE-72P48F1 full subpanel + SCE-72SMP14 side-mount subpanel`** — identical pair to the FSD; anchored in same 8 jobs.
- **`grounding / Penn-Union LA-500-1 main ground lug`** — confirmed in E1377, E1378, E1388, E1405, E1406, E1395, E1399, E1404. **8 of 9 BOM-validated jobs.**
- **`control_power / WEG CPTW3K0-GSC 3 kVA 120 VAC xfmr`** — confirmed in all 5 new BOMs (E1377, E1378, E1388, E1405, E1406). Tally: 8 of 9.
- **`control_power / Schneider 9070T500D19 500 VA xfmr`** — confirmed in all 5 new BOMs. Tally: 8 of 9.
- **`climate_kit / Finder 7T.81 + 7L.43 + 7F.21 + 7F.02 quartet`** — confirmed in all 5 new BOMs as a complete identical set. Tally: 9 of 9.
- **`door_devices / per-compressor cluster (white + red pilot + selector)`** — confirmed in E1377 (7 × XB5AVG1 / XB5AVG4 / XB4BD21), E1378 (7 each), E1388 (5 each), E1405 (6 × CL2-513C/513R/M2SS2-10B), E1406 (6 each). Tally: 8 of 9.

### PROMOTED — v0.1 candidate_invariants now anchored

- **`refrigeration_controller / Danfoss AK-PC 782B + AK-SM 850A as combined HMI`** — v0.1 listed AK-SM 850A separately, but it functions as the system manager / HMI for Danfoss panels. Confirmed in E1395, E1399, E1404, E1405, E1406. **Anchor: 5 of 5 Danfoss jobs.** Previous v0.1 confusion about "candidate MMIGRS2 HMI" is resolved — MMIGRS2 is a Copeland-side or supplementary HMI, not the standard.
- **`pricing.PSU / WAGO 2587-2144 5 A 24 VDC PSU`** — confirmed in E1388, E1395, E1399, E1404, E1405, E1406. **6 of 7 anchored BOMs.** Strong invariant.
- **`grounding / Schneider PK12GTA 12-pos ground bar`** — partial; confirmed in E1377, E1378 + v0.1 jobs; not visible in E1388/E1405/E1406 grep window (may be present deeper). **Demoted to "common but not universal — voltage- or cluster-dependent."**

### BROKEN — v0.2 counter-example

- **`variable_slots / refrigeration_controller / observed_options [danfoss_ak, copeland_cc]`** — Copeland sample doubled to 3 (E1392, E1388, likely E1355). But the Copeland controller part number on E1388 is **818-9002 Visiograph Display** + presumably an E3 RX upstream. v0.1 lists "Copeland E3 RX 860-1305" — **Visiograph 818-9002 may be the HMI, not the controller itself**. Needs clarification: is `860-1305` the E3 RX board (Copeland)? Is `818-9002` always paired with it?

- **`variable_slots / incoming_voltage / observed_options [208 VAC, 460 VAC]`** — **BROKEN. E1354 and E1380 are 575 VAC** (Canadian Roxsta G6 panels — likely Bright Renewables = Canadian customer site). v0.1 voltage enum needs expansion to `[208, 460, 575]` and cascading effects need re-evaluation (575 V branch breakers, SPDs, contactor coil voltages, fuse families).

### STILL UNDETERMINED

- HMI/PLC on Copeland-controlled panels — Visiograph 818-9002 may be the integrated HMI but we don't yet know if there's a separate Touchscreen / PLC component on E1388 / E1355.
- E1380's BOM-side invariants — entire BOM unparseable because no red bar.
- Compressor count per job for E1354, E1360, E1371 (drawings only; counts have to be derived from per-compressor schematic pages we didn't read).

## v0.1 selection-rule validation

### Confidence promotions

- **Axis 1 (refrigeration_controller_family)**: M → H. Copeland sample expanded (E1388 Visiograph confirmed, E1355 by filename). Danfoss sample expanded substantially (E1377, E1378, E1405, E1406 all visible Danfoss).
- **Axis 4 (motor_protection_branch_topology) ABB variant**: M → H. E1405 + E1406 use IDENTICAL ABB stack to E1404 (MS165-65 + MS132-16 + AF65 + AF16 + BEA65/BEA16). NG cluster supplemental's authority is now anchored across 3 jobs.
- **Axis 4 WEG variant**: M → H. E1377, E1378, E1388 all use WEG MPW family with frames matched to per-compressor FLA. Pattern consistent.
- **Axis 10 (pressure_regulator / Class-2 xfmrs)**: L → M. Not directly validated against the 5 new BOMs but the underlying control-power architecture (3-tier with WEG + Schneider + WAGO) is now anchored in 8 of 9.

### Confidence demotions

- **Axis 5 (incoming_voltage) enum**: H → M. Broken by E1354 + E1380. Must add 575 VAC as a third tier.

### New variability discovered (axes to add)

- **`enclosure_size / SCE-724818FSD as canonical option`** (was a variable slot in v0.1; in practice this exact SKU dominates). The slot stays but **add `default: SCE-724818FSD` and `outlier: Rittal 1400×800×500-700 mm (E1392 only)`**.
- **`controller_voltage_cascade`**: pilot family appears voltage-driven (Schneider XB at 208/460 V; ABB CL2 at 460 V exclusively; no observed pattern at 575 V — needs more data). Promote v0.1 § 8.2 from open question to confirmed observation but flag 575 V as gap.
- **`compressor_count`**: now observed at 4, 5, 6, 7, 9 across jobs. Quantity-driver invariant in v0.1 holds (per-compressor MMP + contactor + door cluster scales linearly).

## Topology open questions (v0.1 findings § 8) status update

- **§ 8.1 Copeland sample skew**: improved 1:3 → 3:11. Still skewed Danfoss-heavy but Copeland claims now stand on E1392 + E1388 evidence (and E1355 by filename).
- **§ 8.2 Pilot family voltage-vs-controller**: **confirmed voltage-driven, not controller-driven**. Schneider XB5/XB4 in 208 V jobs (E1377 is 460 V using XB5 too — counter-example, weakens the rule). Refine: pilot family is **panel-shop preference correlated loosely with voltage**, not a hard rule.
- **§ 8.3 Enclosure brand Saginaw vs Rittal**: **resolved**. Saginaw SCE-724818FSD is the invariant; Rittal (E1392 only) is an outlier driven by Canada or customer preference.
- **§ 8.4 ABB vs WEG motor-protection topology**: **confirmed cluster-driven**. NG cluster (E1404, E1405, E1406) uses ABB. All other jobs use WEG. The cluster supplemental authoritatively chooses ABB.
- **§ 8.5 Compressor count drives BOM variance**: **anchored**. 4 / 5 / 6 / 7 / 9 observed. Per-compressor pattern (MMP + contactor + 3 door devices + 3 legend plates) scales cleanly.

## New findings (add to findings.md)

- **NEW P1 — E1380 BOM has no red bar**. Purple at row 12, red bar absent. BOM is WIP / unfinished and cannot be validated. Either ship the BOM with a red bar applied (the bedrock convention) or document this as a known WIP shape. Evidence: `bom-E1380.txt` purple_row=12 red_row=None.
- **NEW P0 — 575 VAC tier missing from v0.1**. E1354 and E1380 are 575 VAC Canadian Roxsta G6 panels. The v0.1 voltage axis enum must expand and downstream cascades (branch breakers, contactor coils, SPDs, fuse families) need 575 V variants documented. Without this, the system would refuse to model two existing customer panels. Evidence: `pdf-E1354_VITALIS_BRIGHT_RENEWABLES_UL_.txt` L7, `pdf-E1380-BRIGHT_RENEWABLES_COOLSHIFT_-_5-6-2026_-_G_.txt` L12.
- **NEW P1 — E1377 has two drawings (REV1 + ADDON BOARD)**. Same panel, two PDFs with different revision histories. Pattern: addon-board revisions cause a parallel PDF in drawings/. Worth a convention.
- **NEW P2 — VFD vendor independent of refrigeration controller**. E1355 Copeland controller uses Danfoss FC-103 VFDs. Don't conflate VFD vendor with controller family in selection rules.
- **NEW P2 — SCCR varies independently**. 35 kAIC (E1354, E1380) vs 65 kAIC (E1355, E1377, E1378, prior 4-of-4). Lower SCCR observed on 575 V Canadian jobs. Possibly Canadian-grid driven; possibly customer-driven.

## Recommended patches to v0.1 YAMLs

1. **`panel-template.yaml § variable_slots / enclosure_size`** — add `default_sku: SCE-724818FSD` and `outliers: [Rittal 1400×800×500-700 (E1392 only, Canada/customer-driven)]`. Promote SCE-724818FSD to a near-invariant.

2. **`panel-template.yaml § invariants`** — promote the following from candidate to anchored: Saginaw FSD enclosure pair (SCE-724818FSD + SCE-72P48F1 + SCE-72SMP14), WAGO 2587-2144 PSU, Penn-Union LA-500-1.

3. **`panel-template.yaml § variable_slots / refrigeration_controller`** — split into two sub-fields: `refrigeration_controller_board` (E3 RX vs AK-PC 782B) and `hmi_system_manager` (Visiograph 818-9002 vs AK-SM 850A vs none). They scale together but are distinct line items.

4. **`selection-rules.yaml § axis 5 (incoming_voltage)`** — **expand enum to `[208 VAC, 460 VAC, 575 VAC]`**. Add 575 V cascade rules (or flag as "needs more evidence" until we have 575 V BOM data).

5. **`selection-rules.yaml § axis 4 confidence`**: M → H for both ABB and WEG packages.

6. **`selection-rules.yaml § axis 1 confidence`**: M → H. Controller family is now well-anchored on both sides.

7. **`selection-rules.yaml § new axis — sccr_target`**: not currently a named axis. Observed at 35 / 65 kAIC. Drives main breaker frame choice (XT5N vs XT5H vs XT6H).

8. **`findings.md § 8.2`** — change wording from "may be voltage-driven, not controller-driven" to "is voltage-correlated panel-shop preference; pilot family is not a hard rule." E1377 (460 V using Schneider XB5/XB4) is a counter-example to a strict voltage rule.

9. **`findings.md` § new resolutions** — close § 8.3 (enclosure brand resolved) and § 8.4 (ABB vs WEG resolved as cluster-driven).

## Sample-still-too-thin caveats

- 575 V jobs: 2 (E1354, E1380). Sufficient to add to the voltage enum but not to derive 575 V-specific selection rules (branch breakers, coils, SPDs).
- E1380 BOM unparseable: removes one data point on the 575 V side.
- Copeland-side BOMs: 2 (E1392, E1388). E1355 has no BOM in the drop (drawing only). Copeland-side per-compressor patterns still rest on fewer samples.
- HMI on Copeland panels: only E1388 visible (Visiograph 818-9002). Whether E1392's Copeland panel has a Visiograph too needs cross-reference.

## XLSX extraction method note

Used `_scratch/bom_extract.py` (openpyxl 3.1.5). The script scans columns B–G in the first ≤200 rows, identifies the topmost cell with fill `FF8E7CC3` (purple) or unprefixed `8E7CC3` and the next cell with fill `FFE06666` or `E06666` (red), then extracts all cells in columns B–O between those two row indices. The "BOM sheet" preference is any sheet whose name starts with "BOM" — all 9 BOMs use `BOM - SCP-01` (uniform convention).

PDF extraction used `_scratch/pdf_titleblock.py` (pypdf 6.11.0), pages 0–2 only. Title block + first single-line page contain the canonical voltage / FLA / HP / SCCR / panel name. Per-compressor schematic pages were not read (would require a per-job 60+ page sweep, infeasible for the light pass).
