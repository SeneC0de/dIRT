# E1399 — Panel-Feature → BOM Parts Association

Scope: BOM rows 15-88 only (between purple bar at R14 and red bar at R89). Wago parts outside relays and power supplies are flagged low-confidence ("estimate") per charter.

| Panel Feature | Part Numbers | Qty | Notes |
|---|---|---:|---|
| **Enclosure / mechanical** | SCE-726018FSD (Saginaw 72×60×18 FSD), SCE-72P60F1 (subpanel) | 1 + 1 | NEMA 3R/12/13 per PO; FSD = full-shroud-door. |
| **Main disconnect / incoming feeder** | XT6HU3800EFF000XXX (ABB MCB), KXT6CUAL2X750KCC-3 (lugs ×2), KXT6RHESTFP (shaft) | 1 + 2 + 1 | 800A frame XT6 sized to MOCP 656 A from Load Calc. |
| **Power distribution blocks** | UD6C500AL (nVent 380 A single-pole, 6-line, AL) | 6 | One per phase × two-bank split, typical L1/L2/L3. Tag `PDB1-6`. |
| **Compressor MT2-MT5 motor protection (active topology)** | MPW100-3-U075 (×1), MPW100-3-U090 (×4), CWM95-11-30V18 (×5), TSB SC-11 MPW100 (×5), IB MPW100 (×5), ECCMP-80B80 (×4) | 24 total | WEG package. 5 compressors total on MT1 stack. **R31-R36 have `=AI()` placeholder formulas in desc/manufacturer cells — sheet-author left auto-fill stubs live; low-confidence on text, qty values look correct.** |
| **Compressor LT2-LT4 motor protection** | MPW80-3-U040 (×1), MPW80-3-U065 (×3), CWB50-11-30D15 (×1), CWB80-11-30D15 (×3), TSB (×4), LST65 (×4) | 16 total | WEG package, smaller frames for the LT stack. R39-R40 also have `=AI()` placeholders. |
| **Control / branch fusing** | LPSC0002Z 30A CC fuse holder (×2), KLDR015 15A CC fuse (×2 active + ×2 spare), HCLR03 3A CC fuse (×2 active + ×2 spare) | 10 total | Spares booked as separate BOM rows (`SPARE FUSES` tag). Tags FU4121, FU4181. |
| **Panel HVAC (cooling/heating)** | 7T.81.0.000.2303 Finder thermostat, 7L.43.0.230.1100 Finder LED light, 7F.02.0.000.3000 Finder exhaust filter, 7F.21.8.120.3100 Finder reverse-flow filter fan | 1 + 1 + 1 + 1 | TAS5041 thermostat tag, WLT5021 lamp tag, MTR5041 fan tag — standard panel-environment kit. |
| **Operator interface (door-mount)** | E214-16-101 group switch (×9), CL2-513C clear pilot light (×9), CL2-513R red pilot light (×9) | 27 total | TG/LT tag prefixes span TG14, TG18, TG22, TG26, TG36, TG40; LT/LT14, LT18, LT22, LT33, LT37. One switch + 2 lights per circuit, ~9 circuits exposed at the door. |
| **Machine-stop button** | XB5AS8444 (Schneider Harmony 40 mm mushroom, 2NC) | 1 | Confirmed by Panel Options TRUE in RFQ XLSX. |
| **Phase-monitor relay** | RM22TR33 (Schneider 3-phase, 380-480V) | 1 | Tag CR2031. |
| **Convenience outlet + ethernet drop (door)** | 1415758 HEAVYPORT (PHX) | 1 | Tag RECP5061. |
| **Ethernet switch** | 2702324 FL Switch 2000 8-port managed (PHX) | 1 | Confirmed by Panel Options TRUE. |
| **Control transformer 1** | CPTW3K0-GSC (WEG 480→120 VAC 3 kVA) | 1 | Tag T413. Matches Load Calc T5031 row 6.52 A primary. |
| **Control transformer 2 (24 VAC)** | 9070T500D19 (Schneider 500 VA), 9070FSC23 (finger-safe cover) | 1 + 1 | Tag T4191. Feeds Danfoss AK-PS 250 PSUs. |
| **Branch circuit breakers (120 VAC distribution)** | ST201M-C6 (×9), ST201M-C15 (×2), ST201M-C20 (×2), ST201M-C2 (×19), ST201M-C1 (×2), ST201M-C32 (×1) | 35 total | ABB ST200M UL1077 supplemental. The 19× C2 is the bulk — feeds individual sensors / coils. |
| **Ground bar** | PK12GTA (Schneider 12-terminal QO/Homeline) | 1 | |
| **PLC / controller (Danfoss AK)** | AK-PC 782B (pack controller), AK-CM 101C (comm), AK-SM 850A (system manager), AK-XM 205A (×2 — I/O 8AI + 8DO), AK-XM 103A (×2 — 4AI + AO), AK-XM 101A (8AI sensors), AK-XM-208C (8AI + 4 drivers), AK-OB 110 (analog output) | 10 modules total | This is the controller stack. NB: PC54071 part-number tag is reused on R15 (AK-OB 110) and R17 (AK-PC 782B) — almost certainly a tag-collision typo. **Flag.** |
| **Danfoss AK power supply** | AK-PS 250 | 2 | Pair feeds the AK control stack. |
| **Interposing relays — 24 VAC 8 A 2-CO** | WAGO 788-512 | 3 | Tags CR38081, CR53091, CR38201. |
| **Interposing relays — 24 VDC 1-CO** | WAGO 857-304 | 3 | Tags CR7071, CR7072 (qty 3 but 2 tags listed — one position likely spare). |
| **Interposing relays — 115 VAC 2-CO 8 A** | WAGO 788-515 | 14 | 13 tags listed, qty 14 — one spare. The workhorse-relay block. |
| **Spare-fuse drawer** | WAGO 709-591 cabinet drawer | 1 | Tag `SPARE FUSES`. |
| **Terminal-block field — feedthrough (5.2 mm)** | WAGO 2002-1201 | 10 | Wago-non-relay — **estimate, low confidence.** |
| **Terminal-block field — feedthrough (7.5 mm)** | WAGO 2006-1201 | 35 | **estimate.** |
| **Terminal-block field — feedthrough (12 mm)** | WAGO 2016-1201 | 3 | **estimate.** |
| **Triple-deck TBs** | WAGO 2002-3227 (51), 2002-3201 (33), 2002-3217 PE/N/L (13) | 97 total | Heavy use of multi-deck — distribution-dense panel. **estimates.** |
| **Ground TBs** | WAGO 2006-1207 (×9), 2002-1207 (×2), 2016-1207 (×1) | 12 total | **estimates.** |
| **End stops** | WAGO 249-117 | 25 | **estimate.** |
| **Jumpers** | WAGO 788-113 (pos 1 & 3) | 15 | **estimate.** |
| **DIN rail** | WAGO 210-112 (35 × 7.5 mm, 2 m) | 5 | **estimate.** |
| **5A power supply (small)** | WAGO 2587-2144 | 1 | Auxiliary 24 V rail. |
| **Legend plates** | 1631 Carolina Laser textured plastic, 3-line | 18 | 18 plates → fewer than the 33 rows on the Legend Plates sheet. **Discrepancy worth a finding** — either some plates piggyback on others, or 15 legends are missing from the BOM. |
| **Main ground lug** | LA-500-1 (Penn Union 4 AWG-500 MCM) | 1 | Tag GND. |

## Features looked for but NOT FOUND in the BOM
- **UPS** — explicitly FALSE in RFQ Panel Options; absent. ✓ consistent.
- **Energy meter / Rogowski coils** — FALSE in RFQ; absent. ✓
- **VFD / soft-start hardware** — none in BOM despite Load Calc listing 3 VFD compressors (B1-2U1, B2-2M1 MT side; G1-2U1, G2-2U1 LT side). **Drives are likely customer-furnished / out-of-cabinet** (consistent with the rack-control-panel scope and PO note "Danfoss AK controller and I/O provided by Vitalis"). Worth confirming.
- **Defrost / condensate management** — none in BOM. Likely not in scope for this pack-control panel (these belong to the refrigeration case controllers).
- **HMI** — drawing page 75 is labeled `HMI.dwg`, but no panel-mount HMI part is in the BOM. The AK-SM 850A System Manager is its own touchscreen → that's the HMI. ✓
- **Lighting circuit (panel-interior)** — covered by Finder 7L.43 (1 lamp) + thermostat-switched. ✓
- **Surge protection / SPD** — **absent.** No SPD device in the BOM. Unusual for a 460 V industrial panel; could be intentional (upstream SPD on the building feed) or could be a gap.

## Reminders honored
Wago TBs / end stops / jumpers / DIN rail / ground TBs are flagged "estimate" — per charter, only relays (WAGO 788-512, 788-515, 857-304) and power supplies (2587-2144) are accurate Wago quantities.
