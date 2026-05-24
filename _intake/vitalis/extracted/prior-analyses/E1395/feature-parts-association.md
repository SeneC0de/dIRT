# E1395 — Panel-Feature → BOM Parts Association

Groups the 71 in-bar BOM rows by panel feature. A few rows participate in more than one feature; in those cases the part is listed under its primary owner and cross-referenced with `(see also: <feature>)`.

Reminder: Wago small-TB / end-stop / rail / marking items in this table are **estimates** (caveat #3) — not exact counts. Wago relays and power supplies are full-confidence.

| Panel Feature | Part Numbers (row) | Qty | Notes |
|---|---|---:|---|
| **Enclosure** | SCE-726018FSD r14; SCE-72P60F1 r15 | 1; 1 | 72×60×18 FSD enclosure + matched full-coverage subpanel. Floor-stand panel (FSD = free-standing disconnect style). |
| **Main service / disconnect** | XT7HU310DFFF000XXX r27; KXT7CUAL4X500K-3PC r28; KXT7RHEST r29; LA-500-1 r52 | 1; 2; 1; 1 | ABB Tmax XT7 main breaker (~1000 A frame); two sets of large lugs; extended through-door rotary handle (forced by FSD); Penn-Union main ground lug 500 MCM. |
| **Power distribution block** | UD2C9C1250AL r16 | 3 | nVent 950 A 1-pole PDBs — one per phase. Tags PDB1/PDB2/PDB3. |
| **Grid / voltage monitor** | RM22TR31 r55 | 1 | Schneider 3-phase voltage monitoring relay 200-240 V. |
| **MT compressor circuits (×4 — MT1 VFD + MT2/3/4 contactor)** | DWB250PE250-3DF r35; DWB250PE200-3DF r36; PC DWB250 3P r37; CWM180-22-30E10 r38; BCXML11 r39; BMP CWM180 r40; LW2-S300 r41; BC-1 DWB r42 | 2; 2; 8; 4; 3; 4; 8; 3 | MT1-2 breakers 250 A trip; MT3-4 breakers 200 A trip (**flag — same FLA**). CB lugs 8 (2 per × 4 CBs). 4 contactors CWM180; covers 4; lugs 8 (2 per). Aux contacts qty 3 — VFD on MT1 likely substitutes the aux function. |
| **LT compressor circuits (×3 — LT1 VFD + LT2/3 contactor)** | MPW40-3-U016 r30; CWB18-11-30D15 r31; ECCMP-40B38 r32; TSB r33; LST25 r34 | 3; 3; 3; 2; 3 | LT motor protection breakers MPW40 sized 10-16 A for FLA 15.2 A. Contactor CWB18 with 1NO+1NC aux. Aux blocks TSB qty 2 (LT1 = VFD). Terminals LST25. |
| **Compressor HOA & indicators (×7 = 4 MT + 3 LT)** | XB5AVG1 r58 (white); XB5AVG4 r59 (red); XB4BD21 r60 (selector); 1631 r84 (legend plate) | 7; 7; 7; 21 | One run/fault pilot pair + one 2-pos selector per compressor. Legend plates 21 = 7 × 3 lines (likely compressor name, switch label, status). |
| **Control transformer T1 — 3 kVA 208→120 VAC** | CPTW3K0-GSC r44; LPSC0002Z r45; KLDR015 r47; M9F42120 r65 (partial) | 1; 2; 4; 1-of-2 | T1 primary protection = 30 A Class CC fuse holders (qty 2 for L1/L2). 15 A Class CC time-delay fuses for 120 V branch protection downstream. CB7011 (per Drawings rev L: "REPLACED FU7011 WITH CB 7011") shifted from fuse to MCB → uses one of the M9F42120 20 A 2-pole MCBs. |
| **Control transformer T2 — 500 VA 208→24 VAC** | 9070T500D19 r56; 9070FSC23 r57; KLKR005 r46; M9F42130 r67 | 1; 1; 4; 1 | Schneider T2; fingersafe cover; 5 A fast-acting fuses (FU4171 + spares) for secondary; CB412 30 A MCB for primary. |
| **120 VAC branch breakers (page-5 dist)** | M9F42102 r61; M9F42115 r62; M9F42101 r63; M9F42104 r64; M9F42120 r65; M9F42106 r66 | 16; 1; 1; 1; 2; 7 | M9F42102 (2 A) qty 16 — heaviest count, blanket protection for many low-current loads. M9F42106 (6 A) qty 7 → matches 7 compressor coils. M9F42115 (15 A), M9F42101 (1 A), M9F42104 (4 A) single instances → unique loads. M9F42120 qty 2 covers CB5061 + CB7011 (the latter ex-FU7011). |
| **Ground bus** | PK12GTA r68 | 1 | 12-position ground bar (separate from main ground lug r52). |
| **Convenience outlet & door network** | 1415758 r53 | 1 | Phoenix HEAVYPORT GFCI + RJ45 combo in door. |
| **Industrial network switch** | 2702324 r54 | 1 | Phoenix FL Switch 2000 8-port managed. Hosts AK-SM, AK-PC, HMI, convenience-outlet RJ45, door HMI Ethernet. |
| **UPS** | 2320283 r69; 1274118 r70 | 1; 2 | Phoenix QUINT4 1 kVA UPS + 2× 24 V 7 Ah batteries. **Sized per customer request** (per Fab Packet note P59). Tags UPS6021, BAT6031. |
| **Wago 5 A 24 VDC base PSU** | 2587-2144 r72 | 1 | Tag PWS615 — secondary 24 VDC bus power. |
| **Danfoss controllers** | AK-PC 782B r19; AK-SM 850A r22 | 1; 1 | Pack controller (compressor pack) + System Manager (site head). |
| **Danfoss IO/comm modules** | AK-OB 110 r17; AK-CM 101C r20; AK-XM 205A r21; AK-XM 103A r23; AK-XM-101A r24; AK-XM 205A r25; AK-XM-208C r26 | 1; 1; 1; 2; 1; 1; 1 | Module stack — AO expansion, RS-485 comm, 2× (8 AI + 8 DO) modules, 2× (4 AI + 4 AO), 1× 8 AI, 1× (8 AI + 4 stepper). **Danfoss Wire Changes doc says swap one 103A → 101A, BOM still shows 2× 103A — flag.** |
| **Danfoss PSU (24 VDC)** | AK-PS 250 r18 | 2 | Two Danfoss-specific PSUs for the module rack. |
| **Panel climate (heat/cool/vent)** | 7T.81.0.000.2303 r48; 7F.21.8.120.3100 r50; 7F.02.0.000.3000 r51 | 1; 1; 1 | FINDER panel thermostat + 120 V exhaust filter fan + matching filter. Tied to RECP / panel interior. |
| **Panel interior light** | 7L.43.0.230.1100 r49 | 1 | FINDER LED enclosure light. **230 V variant in 120 V panel — confidence drift, flag.** |
| **Door / control voltage relays (interface)** | 788-515 r73; 857-357 r74; 858-158 r75; 857-304 r76; 788-512 r77 | 13; 3; 2; 3; 3 | 115 VAC interface relays dominate (13× 788-515). Mix of 1 CO, 2 CO, 4 CO variants. 24 VDC and 24 VAC variants for low-voltage side. **Full confidence (Wago relays).** |
| **Compressor connectors (LT side)** | ECCMP-40B38 r32 (cross-listed) | 3 | Mfg-recommended connector between contactor and motor wiring for LT 1-3. |
| **Aux mini-contactors (purpose unclear)** | CWCA0-31-00V18 r43 | 2 | WEG mini-contactor 18 VDC coil. Likely fan/heater interlock or HOA-fed coil loop. Tag missing — could be tied to panel climate. |
| **Customer terminal block rail (door-out)** | 2002-3227 r79; 2002-1201 r80; 2002-3201 r81; 249-117 r78; 249-116 r83; 210-112 r82 | 84; 14; 37; 67; 8; 6 | Wago TOPJOB-S triple-deck (84) is the bulk; feedthroughs and L/L/L doubles fill gaps. **Caveat #3: all estimated quantities — counts may drift.** |
| **Spare fuses storage** | 709-591 r71 | 1 | Wago multi-color drawer that mounts on DIN rail to hold spare fuses (KLKR005 spares, KLDR015 spares). |
| **Labeling** | 1631 r84 (cross-listed under HOA & indicators) | 21 | 22 mm 3-line legend plates. Most likely consumed by the door HOA strip. |

## Coverage check

71 in-bar BOM rows. Every row is assigned to at least one feature. Crossovers / multi-feature parts:

- M9F42120 r65 (qty 2) — both T1 control feeder (CB7011, replacing FU7011) and an unidentified CB5061 (likely separate 120 V branch).
- ECCMP-40B38 r32 — assigned to LT circuits and to "Compressor connectors".
- 1631 r84 — under HOA & indicators and called out under labeling.

## Features absent / un-instantiated in this BOM

Several common panel features that the Fab Packet implies but aren't represented as distinct BOM lines:

- **No PLC chassis line item** — the Danfoss AK-PC 782B + module stack *is* the PLC. There's no separate Rockwell/Siemens PLC.
- **No VFDs in the BOM** — the customer email and Load Calc both reference VFDs on MT1 and LT1, but **no drive part numbers appear in the in-bar BOM**. Either VFDs are **customer-supplied** (consistent with the "UPS sized per customer" note suggesting customer-supplied power equipment) or this is a missing BOM line. **Worth flagging.**
- **No safety relay line in the BOM** — yet drawings rev L's revision table explicitly says "ADDED IN SAFETY RELAY". Implies a safety relay was added during revisions and may not have made it into the BOM. **Flag.**
- **No HMI line item** — but the Fab Packet and Drawings explicitly say HMI is door-mounted ("HMI" in drawing sheet 67). The Danfoss Inventory sheet shows MMIGRS2 (Danfoss HMI) qty 3, but **MMIGRS2 does not appear in the BOM rows 14-84**. **Flag.**
- **No Superheat Controllers (EKE 1C)** in BOM either — Danfoss Inventory shows qty 2; absent from BOM.
- **No Cable tray or wire-tray** in the in-bar BOM. The orange-fill rows below the red bar list `8000-099/000-4447` and `830-600/000-030` Wago wire-tray entries — these are the fudge rows (caveat #2) so they're excluded; but if wire-tray is consumed, the BOM under-counts it.
