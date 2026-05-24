# Part-Feel Pre-Pass — E1392 / 4S Ranch

First-pass intuition only. For each real BOM row (between purple bar at row 22 and red bar at row 101), guessed which attributes most likely drove the selection. Confidence: H = high (engineering math or vendor-typical), M = medium (judgement from context), L = low (Wago small-TB / marking / consumable estimate, or unfamiliar context). **Wago parts outside relays and power supplies are flagged Low per project rule.**

| Row | Part # | Category | Attributes Driving Selection | Conf |
|---|---|---|---|---|
| 23 | 860-1305 | Controller (Copeland E3) | Customer mandate (Copeland E3 RX). Compatible w/ refrigeration rack supervisory. Customer-furnished. | H |
| 24 | 638-4880 | Plug-in I/O card | Adds DIO to E3 controller; channel count matches a small set of local interlocks. Customer-furnished. | H |
| 25 | 810-3065 | Copeland MultiFlex 168A0 | 16 DI + 8 RO + 4 AO — count chosen to cover MT1 rack analog valve commands. Customer-furnished. | H |
| 26 | 810-3066 | Copeland MultiFlex 168 | 16 DI + 8 RO — covers LT1 rack digital interlocks. Customer-furnished. | H |
| 27 | 818-9010 | iPro CO2 HP controller | CO2 high-side application (Roxsta G6 = CO2 transcritical refrigeration). | H |
| 28 | 818-5003 | XEV20D dual stepper kit | Stepper-valve drivers for HP / MP regulators (page 58–63 areas). Two kits → 4 stepper channels. | H |
| 29 | 810-3064 | 88 I/O board | Expansion I/O — proposal scope explicitly adds it for "spare terminals". | H |
| 30 | 818-9002 | Visiograph display | iPro HMI / Visograph for the panel door. Customer-furnished. | H |
| 31 | 8845500 | Rittal 1400×800×700 S/D | Enclosure size driven by the device count & 5-compressor layout. Single-door. | M (depth conflicts w/ proposal 500 mm) |
| 32 | 8145235 | Rittal sidewalls 1400h × 500 | Closes the open sides of the chassis. Dimension keyed to row 31. | H |
| 33 | 8614650 | Rittal 500×400 partial MPL | Partial mounting plate for the chassis split. 2 panels = upper/lower or device-zone split. | M |
| 34 | 8614850 | Rittal 700×400 partial MPL | Partial MPL — pairs with row 33 to make full 700-depth MPL. | M |
| 35 | XT5NU330ABFF000XXX | ABB main breaker | Trip 300–3000 A adjustable on 400 A frame, MOCP from Load Calc = 399 A → 400 A frame. SCCR 65 kAIC needed. 3-pole. | H |
| 36 | KXT5CUAL2X500K-3PC | Lug kit 2×2/0–500 MCM | Cable size: feeder for ~400 A panel typically 2×500 MCM Cu/Al. | H |
| 37 | KXT5RHESTFP | Rotary handle for XT5 | Door-mounted disconnect handle. "STAND. RETURNED" word raises a flag. | M |
| 38 | PK12GTA | Schneider 12-pos ground bar | Number of ground landings (~12) drove choice. | M |
| 39 | UD6C500AL | nVent 500 MCM PDB | Distribution after the disconnect; 500 MCM landings to feed PDB. Three of them = three legs/phases or three feeder groups. | H |
| 40 | MPW100-3-U100 | WEG MPR 63–100 A | Motor protector sized for ~85 A FLA compressors (B2, B3); 100 A frame covers margin. Trip current matched to FLA. 3 units — one extra vs Load Calc. | H |
| 41 | CWM105-11-30V18 | WEG contactor 105 A AC3, 24VDC coil | AC3 rating ≥ comp FLA; coil voltage = panel control DC (24V). 3 units — across-the-line for B2/B3 + 1 spare/heat-reclaim? | H |
| 42 | TSB SC-11 MPW100 | WEG trip-signaling block | Spec accessory for MPW100; signals overload to PLC. 2 of 3 protectors have it (one without — flag). | M |
| 43 | IB MPW100 | WEG insulating plate | Phase-isolation between adjacent MPRs. 6 plates / 3 MPRs = 2 per (top + bottom). | M |
| 44 | MPW40-3-U016 | WEG MPR 10–16 A | LT1 compressors at 11.1 FLA → trip set inside 10–16 A. 40 A frame. | H |
| 45 | LST25 | WEG connector | Mechanical link/connector accessory. | L |
| 46 | ECCMP-40B38 | WEG connector | Companion accessory to MPW40. | L |
| 47 | CWB18-11-30D15 | WEG contactor 18 A AC3, 24V coil | AC3 ≥ 11.1 A. 18 A is the smallest CWB frame; coil voltage = panel DC. | H |
| 48 | CWCA0-31-00V18 | WEG mini-contactor 24 VDC coil | Auxiliary contactor for unloader/oil heater type loads. Coil V = 24 VDC. Tags suggest 4 different page locations. | M |
| 49 | CPTW3K0-GSC | WEG 3 kVA xfmr 208/120 | Sized from Load Calc 3 kVA primary 14.4 A. | H |
| 50 | 9070T500D19 | Schneider 500 VA xfmr | 208/240/277/380/480 → 24V multi-tap; 500 VA chosen from 24V load estimate (≈21 A secondary). | H |
| 51 | 9070FSC23 | Finger-safe cover | Safety accessory required for primary side terminals. | H |
| 52 | 7T.81.0.000.2303 | Finder panel thermostat | Cabinet heat control — enclosure thermal mgmt. NEMA 3R outdoor application drove ambient swing concern. | M |
| 53 | 7L.43.0.230.1100 | Finder LED panel light | Door-open service light, 230 V variant — but the panel is 208 V system; works on 100–230 range. | M |
| 54 | 7F.02.0.000.3000 | Finder exhaust filter | Pair with 7F.21 fan; size keyed to fan airflow. | H |
| 55 | 7F.21.8.120.3100 | Finder filter fan 120 V | Cabinet venting. 120 V power source (the control bus). Size driven by heat rejection of contactors + transformers. | H |
| 56 | RM22TR31 | Schneider 3-phase monitor | 208–240 V range; detects under/over voltage and phase loss on incoming. Required on NEMA 3R outdoor refrigeration panel. | H |
| 57 | XB5AVG1 | Schneider pilot light white | 120 V LED, 22 mm; matches Carolina Laser 22 mm legend plates. Color (white) = "running" convention. | H |
| 58 | XB5AVG4 | Schneider pilot light red | Same body, red = fault/alarm. | H |
| 59 | 857-304 | WAGO relay 24 VDC, 1CO | Coil voltage = control bus 24 VDC. Single contact, slim 6-mm module. Tagged on page 7 (120 VAC dist). | H (relay, high-conf per rule) |
| 60 | 788-512 | WAGO relay 24 VAC, 2CO | Coil V = 24 VAC (from 500 VA xfmr). 2 changeover for solenoid + status interlock. | H (relay) |
| 61 | 1631 | Carolina Laser legend plate | 3-line text, 22 mm rectangular — sized to the XB5/XB4 buttons & lights. 15 plates = sum of devices. | M |
| 62 | LA-500-1 | Penn-Union 500 MCM lug | Main ground landing size. 4 AWG–500 MCM range chosen so it can swallow ground from main feeder. | H |
| 63 | 3209578 | PHX PT 2.5-QUATTRO TB | 2.5 mm² wire, 4-way split — for common bus distribution (e.g. supply to several relays). | M |
| 64 | TR50VA005 | RIB 50 VA xfmr 120→24 VAC | Class 2 distributed power for pressure-reg control coils — one per regulator station. | H |
| 65 | 1415759 | PHX outlet + RJ45 | Service-tech door interface — convenience power + Ethernet drop. | H |
| 66 | 2702324 | PHX FL Switch 2000 8-port | Need ≥ 1 port per Copeland device + 1 customer uplink; 8-port covers the rack. Managed for VLANs / RSTP. | H |
| 67 | 2320283 | PHX QUINT4 UPS 1kVA | Sized to keep critical 24V + controller alive ≥ 10 min. 1 kVA matches the control-bus draw. | H |
| 68 | 1274118 | PHX 7 Ah VRLA battery | Runtime — 2× 7 Ah at 24 V for ~10 min hold-up. | H |
| 69 | 2908307 | PHX PM5011 energy meter | Proposal scope ("Energy meter w/ Rogowski coils"). 208 V 3-phase compatible. | H |
| 70 | 2910322 | PHX Rogowski coil + cable | Sized for ≥ 400 A primary (panel MOCP 399 A). Three coils = three phases. | H |
| 71 | 788-515 | WAGO relay 115 VAC, 2CO | Coil voltage = control bus 120 VAC. 8 A contact for control loads. Qty 14 with 13 tagged = 1 spare. | H (relay) |
| 72 | UMBW-4C2-1 | WEG mini CB 1P 2A C-curve | Branch protection for the local 50 VA xfmr primaries (T6111..T6191). 2 A trip ≈ primary current 0.5 A × headroom. | H |
| 73 | M9F42103 | Schneider Multi9 1P 3A C | Companion secondary CB on the same regulator circuit. 3 A. | M |
| 74 | M9F42115 | Schneider Multi9 1P 15A C | Tagged CB5062 — single 15 A circuit, likely the 24 VAC bus protection. | M |
| 75 | M9F42120 | Schneider Multi9 1P 20A C | 2 instances — CB6011 (page 60 area) + CB4182 (pg 41 oil-sep?). 20 A = receptacle / outlet / heater circuit. | M |
| 76 | M9F42102 | Schneider Multi9 1P 2A C | Workhorse CB — qty 16, used 14 times by tag. Small-load protection (relay coils, sensor loops). | H |
| 77 | M9F42101 | Schneider Multi9 1P 1A C | 2 instances tagged CB5021. Single-A protection for very small instrument loops. | M |
| 78 | M9F42106 | Schneider Multi9 1P 6A C | 6 instances for CB11071..CB39071 — page-7x area = 120 VAC distribution to compressor sections. 6 A = small fan or pilot circuit. | M |
| 79 | M9F42130 | Schneider Multi9 1P 30A C | Single 30 A CB (CB5021 — note tag conflict w/ row 77). Pump or convenience circuit. | M |
| 80 | LPSC0002Z | Littelfuse Class CC fused holder, 2-pole | Primary protection for the 3 kVA control xfmr (Load Calc: 30 A primary). | H |
| 81 | KLDR015 | Littelfuse 15 A Class CC fuse | Goes in LPSC holder. 15 A from Load Calc — primary current 14.4 A round up. | H |
| 82 | KLDR005 | Littelfuse 5 A Class CC fuse | For 500 VA xfmr primary (Load Calc: 5 A). | H |
| 83 | 709-591 | WAGO switchgear drawer | Spare-fuse storage drawer. Size = 35-rail mount. | L (consumable / hardware) |
| 84 | KLDR015 | Spare 15 A CC fuse | Stock 2 spares = one set of replacements. | M |
| 85 | KLDR005 | Spare 5 A CC fuse | Same logic. | M |
| 86 | 594-SFR25H1201%TR | Mouser 120 Ω 1% resistor | RS-485 / Modbus end-of-line termination on the long bus to the regulators. 1/2 W is overkill — typical for engineering margin. | M |
| 87 | XB4BD21 | Schneider Harmony selector 22 mm | 2-position maintained 1 NO — local manual override for each compressor. 600 V rated. | H |
| 88 | 2006-1207 | WAGO GND TB 7.5 mm | 7.5 mm wide = larger gauge (4–10 AWG) ground TBs. **Qty estimate per project rule.** | L |
| 89 | 249-117 | WAGO end stop 10 mm | DIN-rail end retention. **Qty estimate per project rule.** | L |
| 90 | 2002-3227 | WAGO triple-deck through 5.2 mm | High-density 3-tier (L/L/L) — common for sensor wiring. **Qty estimate per project rule.** | L |
| 91 | 2002-1207 | WAGO GND TB 5.2 mm | Small ground TB. **Qty estimate per project rule.** | L |
| 92 | 2002-1201 | WAGO feedthrough 5.2 mm | Standard signal TB. **Qty estimate per project rule.** | L |
| 93 | 2002-3201 | WAGO triple-deck L/L/L 5.2 mm | High-density. **Qty estimate per project rule.** | L |
| 94 | 2016-1201 | WAGO feedthrough 12 mm | Larger gauge (up to ~6 AWG). 24V power distribution. **Qty estimate per project rule.** | L |
| 95 | 2016-1207 | WAGO GND TB 12 mm | Larger ground TB. **Qty estimate per project rule.** | L |
| 96 | 2002-3217 | WAGO triple-deck PE/N/L | Combined ground/neutral/line in one block. Convenience for distributed power. **Qty estimate.** | L |
| 97 | 2006-1201 | WAGO feedthrough 7.5 mm | Mid-gauge signal/power TB. **Qty estimate per project rule.** | L |
| 98 | 788-113 | WAGO jumper Pos 1 & 3 | Bridges adjacent TBs for common rails. **Qty estimate.** | L |
| 99 | 210-112 | WAGO DIN rail 35×7.5 mm | Standard 35 mm DIN. **Qty estimate.** | L |
| 100 | 2587-2144 | WAGO 5 A 24 VDC PSU | 5 A × 24 V = 120 W. Sized for the Copeland controller stack + the 14 control relays. Lives on the red-bar row. | H (PSU, high-conf per rule) |

## Attribute frequencies (what drives part choice most)

- **Coil voltage matching to control bus** (24 VDC / 24 VAC / 120 VAC) — present on every relay & contactor row.
- **Trip rating tied to Load Calc FLA** — MPRs and CC fuses match the FLA / primary current numbers exactly. Load Calc is the authoritative input.
- **SCCR 65 kAIC** — drove the ABB XT5N main breaker frame choice.
- **22 mm pilot device family** — once XB5 was picked, every device on the door (pilot lights, selector switches, legend plates) is sized to the same 22 mm cutout.
- **DIN-rail mounting + 35 mm rail** — uniform across all small devices.
- **Class 2 / 50 VA xfmrs** — multiplied per pressure regulator (one per circuit, NEC class-2-style power split).
- **WAGO small-TB family** — convenience standard; quantities are eyeball estimates.

## Confidence summary

- **High confidence** (engineering math directly traceable): main disconnect, MPRs/contactors for compressors, control-power xfmrs, UPS, energy meter, Copeland controllers, control relays. ≈ 35 rows.
- **Medium** (sensible guesses): smaller breakers, enclosure accessories, finder climate kit, legend plates. ≈ 20 rows.
- **Low** (estimate per project rule, mostly small Wago TBs / consumables): rows 88–99 + a few minor accessories. ≈ 15 rows.
