# E1395 — Part-Feel Pre-Pass

First-pass guesses about what attributes drove each BOM selection. **NOT GOSPEL** — these are observations from descriptions, tags, and adjacency on the BOM. Cross-reference required for any of these to harden into a decision rule.

Confidence legend: **H** = description names the spec directly, **M** = inferable from context (tag, adjacent items, load calc), **L** = guesswork (especially Wago small-TB/end-stop/marking per caveat #3).

| Row | Part # | Category | Attributes Driving Selection | Confidence |
|---:|---|---|---|---|
| 14 | SCE-726018FSD (SAGINAW) | Enclosure | 72"H × 60"W × 18"D; FSD style (free-standing disconnect); width drives subpanel width and HOA layout; depth drives wire-tray clearance + Danfoss module stack | **H** |
| 15 | SCE-72P60F1 (SAGINAW) | Enclosure | Full subpanel sized to 14 enclosure (60"H × 56"W); F1 = full-coverage | **H** |
| 16 | UD2C9C1250AL (nVent) | Terminal Blocks (PDB) | 950 A rating; **single-pole**, line-to-9-loads × **3 phases** (qty 3 → A/B/C phases); aluminum; sized for 882 A MOCP from Load Calc | **H** |
| 17 | AK-OB 110 (DANFOSS) | IO Devices | Analog output expansion for AK-PC controller; AO count requirement | **M** |
| 18 | AK-PS 250 (DANFOSS, qty 2) | Power Supplies | 24 VDC Danfoss bus power; redundancy + load (2 supplies for module count) | **M** |
| 19 | AK-PC 782B (DANFOSS) | Controllers | **Pack controller** for CO2 compressor pack — selected for the Roxsta G6 platform (4 MT + 3 LT compressors) | **H** |
| 20 | AK-CM 101C (DANFOSS) | IO Devices | RS-485 comm module — needed for HMI / system-manager comms | **M** |
| 21 | AK-XM 205A (DANFOSS) | IO Devices | 8 AI + 8 DO module — picked because IO mix needs both | **H** |
| 22 | AK-SM 850A (DANFOSS) | Controllers | System manager (site head-end) — required by Vitalis Roxsta architecture | **H** |
| 23 | AK-XM 103A (DANFOSS, qty 2) | IO Devices | 4 AI + 4 AO — driver/valve outputs. **Note:** Danfoss Wire Changes doc says swap one 103A → 101A; BOM still shows 2 of 103A. Possible drift. | **M** |
| 24 | AK-XM 101A (DANFOSS) | IO Devices | 8 AI for sensor inputs (suction temp/press, discharge, etc.) | **H** |
| 25 | AK-XM 205A (DANFOSS) | IO Devices | 8 AI + 8 DO — second instance (tags XM63071, XM66071); covers door/aux IO | **M** |
| 26 | AK-XM 208C (DANFOSS) | IO Devices | 8 AI + 4 stepper-driver outputs — for electronic-expansion-valve steppers on each compressor circuit | **H** |
| 27 | XT7HU310DFFF000XXX (ABB) | Protection Devices | **Main disconnect breaker** — 1000A frame (XT7 = Tmax 7), 100% rated. Note D4 has "awaiting quote from SC for ABB breaker" comment — was a sourcing risk | **H** |
| 28 | KXT7CUAL4X500K-3PC (ABB) | Protection Devices | Lugs for the main breaker (cu/al 500 MCM × 4 cables × 3 poles); sized to 2/0 power feed × 4 from Load Calc | **H** |
| 29 | KXT7RHEST (ABB) | Protection Devices | Extended rotary shaft for main breaker (through-door operating handle) — **F**SD enclosure choice forces this | **H** |
| 30 | MPW40-3-U016 (WEG, qty 3) | Protection Devices | **Motor protection breaker**, 10-16 A range × 3-pole, for LT1-3 compressors. Trip range matches CDS351B FLA 15.2 A | **H** |
| 31 | CWB18-11-30D15 (WEG, qty 3) | Protection Devices | Contactor for LT1-3 (CWB18 = 18 A AC-3 rating, coil 24 VDC?). 1NO+1NC aux per descriptor "11"; size matched to LT compressor FLA 15.2 A | **H** |
| 32 | ECCMP-40B38 (WEG, qty 3) | Protection Devices | Connector — between LT contactor and motor wiring. Description "Connectors" — paired with the CWB18 line | **M** |
| 33 | TSB (WEG, qty 2) | (blank) | "LT 2-3 CB Aux" — auxiliary contact block on LT breakers 2 and 3. Why qty 2 (not 3)? LT 1 is the **VFD** circuit (no aux needed?). **Flag.** | **L** |
| 34 | LST25 (WEG, qty 3) | (blank) | "LT 1-3 Terminals" — likely line-side fingersafe terminal covers for LT breakers | **L** |
| 35 | DWB250PE250-3DF (WEG, qty 2) | (blank) | MT1-2 CB — **250 A frame, 250 A trip, 3-pole, DF = adjustable thermal**; sized to 156 A FLA × 1.25 service factor → ~200-250 A trip; pole-2 matches because MT1 is VFD (heavier trip rating expected on VFD lines) — but **both MT1 and MT2 get 250 A trip** which is one bracket high (see flag) | **H** |
| 36 | DWB250PE200-3DF (WEG, qty 2) | (blank) | MT3-4 CB — **250 A frame, 200 A trip**, sized to 156 A FLA × 1.25 = 195 A → 200 A trip is the nearest available. Difference between 250 A (MT1-2) vs 200 A (MT3-4) trip suggests MT1 needed higher because of VFD inrush — but **MT2 is not VFD per the customer email** — flag. | **M** |
| 37 | PC DWB250 3P (WEG, qty 8) | (blank) | Lugs for the four MT CBs (2 lugs × 4 CBs) | **H** |
| 38 | CWM180-22-30E10 (WEG, qty 4) | (blank) | **Main MT contactors** — CWM180 (200 A AC-3) for the four MT compressors; size matched to MT FLA 156 A | **H** |
| 39 | BCXML11 (WEG, qty 3) | (blank) | "contactor aux 1/1" — aux contact 1 NO + 1 NC for 3 of the 4 MT contactors. **Qty 3 not 4** because MT1 is VFD (the VFD's IO replaces the aux contact's status function). | **M** |
| 40 | BMP CWM180 (WEG, qty 4) | (blank) | Terminal cover for CWM180 contactors — fingersafe accessory | **H** |
| 41 | LW2-S300 (WEG, qty 8) | (blank) | Contactor lugs (2 per contactor × 4 contactors) — 300 MCM rated for 156 A FLA | **H** |
| 42 | BC-1 DWB (WEG, qty 3) | (blank) | "CB Aux Off/Tripped" for MT breakers — aux for breaker status, qty 3 again (MT1 maybe handled by VFD signal) | **L** |
| 43 | CWCA0-31-00V18 (WEG, qty 2) | Contactors | Mini-contactor, 3 NO + 1 NC, 18 VDC coil — likely for door fans / heater control loops | **L** |
| 44 | CPTW3K0-GSC (WEG) | Transformers | **3 kVA 480/208 → 120 VAC** control transformer; sized in Load Calc (15 A primary at 208 V) | **H** |
| 45 | LPSC0002Z (LITTELFUSE, qty 2) | Protection Devices | **30 A Class CC fuse holders**, 2-pole — for control transformer primary side; tags FU5021, FU5071 | **H** |
| 46 | KLKR005 (LITTELFUSE, qty 4) | Protection Devices | **5 A Class CC fast-acting** fuses; tag FU4171 + spares — likely 24 VAC secondary protection (matches Load Calc 5 A) | **H** |
| 47 | KLDR015 (LITTELFUSE, qty 4) | Protection Devices | **15 A Class CC time-delay** fuses; tag FU4121 + spares — 120 VAC distribution branch protection | **H** |
| 48 | 7T.81.0.000.2303 (FINDER) | Panel AC & Heating | Panel thermostat — controls exhaust fan / heater | **H** |
| 49 | 7L.43.0.230.1100 (FINDER) | Buttons & Lights | Panel interior LED — 230 V (but panel is 120 V control). **Voltage drift?** Could be the 230 V is the broadest variant; verify. | **M** |
| 50 | 7F.21.8.120.3100 (FINDER) | Panel AC & Heating | **120 V exhaust fan + filter**, reverse-flow style — paired with thermostat | **H** |
| 51 | 7F.02.0.000.3000 (FINDER) | Panel AC & Heating | Exhaust filter (sized to match the fan) | **H** |
| 52 | LA-500-1 (PENN UNION) | Protection Devices | **Main ground lug**, 500 MCM, 1 hole; box-type AL9CU rated — sized to 600 V service | **H** |
| 53 | 1415758 (PHOENIX CONTACT) | Hardware | Heavyport convenience outlet + RJ45 — installed in door for laptop / service | **H** |
| 54 | 2702324 (PHOENIX CONTACT) | Networking | 8-port managed Ethernet switch (FL Switch 2000) — connects AK-SM 850A, AK-PC 782B, HMI, convenience outlet, etc. | **H** |
| 55 | RM22TR31 (SCHNEIDER) | Protection Devices | 3-phase **voltage monitoring relay** (under/over-voltage), 200-240 V — main grid monitor | **H** |
| 56 | 9070T500D19 (SCHNEIDER) | Transformers | **500 VA 208→24 V** control transformer; sized in Load Calc (T2: 2.4 A primary, 20.8 A secondary) | **H** |
| 57 | 9070FSC23 (SCHNEIDER) | Transformers | Fingersafe terminal cover for 9070T500D19 | **H** |
| 58 | XB5AVG1 (SCHNEIDER, qty 7) | Buttons & Lights | **White pilot light**, 22 mm, 120 VAC — 7 instances (tags LT14131, LT18131, ...) matching 4 MT + 3 LT compressors | **H** |
| 59 | XB5AVG4 (SCHNEIDER, qty 7) | Buttons & Lights | **Red pilot light** — paired with the white ones for "running / fault" pairs per compressor | **H** |
| 60 | XB4BD21 (SCHNEIDER, qty 7) | Buttons & Lights | **2-position maintained selector switches**, 1 NO — one per compressor (HOA / on-off) | **H** |
| 61 | M9F42102 (SCHNEIDER, qty 16) | Protection Devices | **2-pole 2 A MCB** — qty 16; the heaviest single circuit-breaker count — branch protection for individual loads | **H** |
| 62 | M9F42115 (SCHNEIDER) | Protection Devices | 2-pole **15 A** MCB | **H** |
| 63 | M9F42101 (SCHNEIDER) | Protection Devices | 2-pole **1 A** MCB — likely PLC bus protection | **H** |
| 64 | M9F42104 (SCHNEIDER) | Protection Devices | 2-pole **4 A** MCB | **H** |
| 65 | M9F42120 (SCHNEIDER, qty 2) | Protection Devices | 2-pole **20 A** MCB — tags CB5061, CB7011 (the 5021 vs 5061 numbering suggests page-5 power dist) | **H** |
| 66 | M9F42106 (SCHNEIDER, qty 7) | Protection Devices | 2-pole **6 A** MCB — qty 7, matches the 7 compressor circuits (likely contactor coil supply) | **H** |
| 67 | M9F42130 (SCHNEIDER) | Protection Devices | 2-pole **30 A** MCB — tag CB412 (transformer secondary breaker per Load Calc) | **H** |
| 68 | PK12GTA (SCHNEIDER) | Protection Devices | 12-terminal ground bar kit | **H** |
| 69 | 2320283 (PxC) | Power Supplies | **QUINT4 UPS 1 kVA 1AC/1AC** — sized for 1 kVA load. Per Fab Packet Note: UPS sized per customer request. | **H** |
| 70 | 1274118 (PxC, qty 2) | Power Supplies | **24 VDC 7 Ah AGM batteries** for QUINT UPS — IQ-comm style | **H** |
| 71 | 709-591 (WAGO) | Hardware | "Spare fuses drawer" — DIN-rail drawer for spare-fuse storage. **Estimate per caveat #3.** | **L** |
| 72 | 2587-2144 (WAGO) | Power Supplies | **5 A 24 VDC** Wago base power supply. Note: Wago power supplies *should* still be reliable per caveat #3 (caveat applies to TBs/end-stops/marking, not PSUs). | **H** |
| 73 | 788-515 (WAGO, qty 13) | Relays | **115 VAC, 2 CO, 8 A interface relays** — for switching loads from PLC outputs at AC voltage. Wago relays = full confidence per caveat #3. | **H** |
| 74 | 857-357 (WAGO, qty 3) | Relays | 115 V AC/DC, 1 CO, 6 A — single-pole interface | **H** |
| 75 | 858-158 (WAGO, qty 2) | Relays | **120 VAC, 4 CO, 5 A**, manual operation — basic 4PDT for special functions | **H** |
| 76 | 857-304 (WAGO, qty 3) | Relays | **24 VDC, 1 CO, 6 A** — DC-side interface | **H** |
| 77 | 788-512 (WAGO, qty 3) | Relays | **24 VAC, 2 CO, 8 A** | **H** |
| 78 | 249-117 (WAGO, qty 67) | Terminal Blocks | **10 mm end stops** — high count = many DIN rails of TBs. **Caveat #3: estimate**, may not be exact | **L** |
| 79 | 2002-3227 (WAGO, qty 84) | Terminal Blocks | TOPJOB-S triple-deck TB — qty 84 = highest. **Caveat #3: estimate** | **L** |
| 80 | 2002-1201 (WAGO, qty 14) | Terminal Blocks | TOPJOB-S feedthrough TB. **Caveat #3: estimate** | **L** |
| 81 | 2002-3201 (WAGO, qty 37) | Terminal Blocks | TOPJOB-S triple-deck (L/L/L) TB. **Caveat #3: estimate** | **L** |
| 82 | 210-112 (WAGO, qty 6) | Hardware | Steel DIN rail, 2 m long × 6 = 12 m total. **Caveat #3: estimate** | **L** |
| 83 | 249-116 (WAGO, qty 8) | Terminal Blocks | 6 mm end stops. **Caveat #3: estimate** | **L** |
| 84 | 1631 (CAROLINA LASER, qty 21) | Labeling | 22 mm legend plates, 3-line. 21 plates → likely 7 compressors × 3 lines (compressor name + HOA + status pair), or some near multiple. | **M** |

## Patterns

- **High-confidence items dominate** (47 / 71 ≈ 66%): voltages, ratings, and counts are usually inferable directly from the description.
- **Low-confidence cluster = Wago TBs/end-stops/rail/drawer** (rows 71, 78-83) — explicitly flagged per caveat #3. **8 rows** are estimates.
- **Compressor-count signature shows everywhere**: qty 7 (= 4 MT + 3 LT) for pilot lights white/red, selector switches, 6A breakers; qty 4 (= MT only) for CWM180 contactors + lugs + covers; qty 3 (= LT or MT-minus-VFD) for LT breakers/contactors/connectors/terminals + BCXML11 aux + BC-1 aux. That's the single strongest pattern in the BOM — **a part-quantity-from-circuit-count derivation rule could be inferred**.
- **VFD asymmetry**: MT1 has a VFD and so the 4-of (CWM180, lugs, covers) reduces to 3-of for aux contacts (BCXML11, BC-1 DWB). Likewise LT1 has a VFD, so TSB (LT aux) is qty 2 not 3. This is **inferable design logic**, not stated anywhere.
- **MT trip-current mystery**: MT1-2 get 250 A trip but MT3-4 get 200 A trip. Customer email says all 4 MT compressors are identical FLA. The 250 A on MT2 (which has no VFD) is one bracket above what FLA × 1.25 suggests. **Flag.**

## Findings to escalate

1. **MT1-2 vs MT3-4 trip-rating mismatch** — same FLA but different breakers. Either an engineering decision (e.g., MT1 VFD + MT2 lead compressor for inrush handling) or an error.
2. **Danfoss Wire Changes doc says swap one AK-XM 103A → 101A**, but BOM shows 2 × 103A and 1 × 101A. If the swap is meant to be in this delivered BOM, qty is wrong; if the swap is forward-looking for the next revision, no problem. **Worth flagging.**
3. **Voltage drift on FINDER 7L.43 panel light** — 230 V variant in a 120 V panel. May be acceptable (LEDs often universal), but worth confirming.
