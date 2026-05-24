# E1404 — Part-Feel Pre-Pass

First-pass attribute guesses for each BOM row (R13–R83 of `BOM - SCP-01`, within the purple/red bars). For each, the major attributes that likely drove selection. Where the Motor Protection supplemental gives an explicit selection-basis, cross-checked. Confidence column: **H** high, **M** medium, **L** low.

Reminder per data rules: Wago parts outside relays/PSUs (small TBs, end stops, marking, DIN rail) are noted as **estimates** by upstream practice — confidence is **L** for those by definition.

| Row | Part | Mfr | Qty | Category | Attributes Driving Selection | Confidence |
|---|---|---|---|---|---|---|
| R13 | SCE-724818FSD | Saginaw | 1 | Enclosure | Outer enclosure size 72"H × 48"W × 18"D, Type 3R rating (per RFQ), FSD = full-side-door | H |
| R14 | SCE-72P48F1 | Saginaw | 1 | Enclosure | Full back-subpanel sized 60"H × 44"W × 0.88"D to fit the FSD enclosure | H |
| R15 | SCE-72SMP14 | Saginaw | 1 | Enclosure | Side-mount subpanel 60"H × 14"W — extra real estate for terminal blocks / I/O | H |
| R16 | XT5HU330ABFF000XXX | ABB | 1 | Protection Devices | Main CB — 300 A trip, XT5 frame (XT4 caps at 250 A), 65 kAIC matches panel SCCR, TMA thermal-magnetic, FF front terminals. **Confirmed by Motor_Protection Main Breaker tab.** | H |
| R17 | KXT5CUAL2X500K-3PC | ABB | 1 | Protection Devices | Main CB load-side lug kit, Cu/Al, 2/0–500 kcmil — ampacity check vs 300 A @ 75 °C NEC = need 350 kcmil Cu / 500 kcmil Al. Confirmed match. | H |
| R18 | KXT5RHESTFP | ABB | 1 | Protection Devices | Rotary handle with door interlock and padlock — required for door-mounted disconnect on a panel. Depth 500 mm matches enclosure depth | H |
| R19 | MS165-65 | ABB | 4 | Protection Devices | MT compressor MMP. **FLAGGED**: 52–65 A range. MT FLA 51.1 A sits below the band's low end. Motor Protection supplemental specifies MS165-**54** (40–54 A). Disagreement between artifacts. | L |
| R20 | HKF1-11 | ABB | 4 | Protection Devices | MMP front-mount aux for MT branch — 1NO + 1NC, used to signal Off/Tripped state of the MMP handle. Standard pairing for MS132/MS165 | H |
| R21 | AF65-30-00-13 | ABB | 4 | Contactors | MT compressor contactor. **Frame size differs from Motor Protection (AF52)**. AF65 = larger frame, ~65 A continuous; -13 suffix = 100–250 V AC/DC coil (matches 120 VAC); -00 = no built-in aux. Likely chasing the MS165-65 sizing change | M |
| R22 | CA4-10 | ABB | 12 | Protection Devices | Contactor front-mount aux block, 1NO. 3 per non-VFD MT contactor (3 contactors × 3 ea = 9 ... but qty here is 12; suggests counted for BOTH MT non-VFD set (3×3=9) and LT non-VFD set (1×3=3) → 12 total). | M |
| R23 | BEA65-4 | ABB | 4 | Protection Devices | Connecting link / coupler between MS165 MMP and AF40–AF65 contactor. Required mechanical link | H |
| R24 | MS132-16 | ABB | 2 | Protection Devices | LT compressor MMP. **FLAGGED**: 10–16 A range. Motor Protection supplemental says NG49 LT uses **MS132-10** (6.3–10 A) because LT FLA is 9.84 A. Another disagreement. | L |
| R25 | HKF1-11 | ABB | 2 | Protection Devices | MMP aux for NG49 LT branch — duplicated row from R20 because BOM groups by panel feature not by part | H |
| R26 | AF16-30-10-13 | ABB | 2 | Contactors | LT compressor contactor. **-10** suffix here indicates 1NO built-in aux block (vs **-00** = none). Description text says "AF09 frame" but the part # is AF16. Description/part mismatch. | L |
| R27 | BEA16-4 | ABB | 2 | Protection Devices | Connecting link MS132 to AF9–AF16. Matches LT motor contactor | H |
| R28 | AK-OB 110 | Danfoss | 1 | IO Devices | Tag PC54071. Analog output module for Pack Controller — likely VFD reference / valve drive | M |
| R29 | AK-PS 250 | Danfoss | 2 | Power Supplies | Tag PWS5151. 24 V DC power supply for Danfoss control bus — qty 2 = N+1 redundancy | M |
| R30 | AK-PC 782B | Danfoss | 1 | Controllers | Tag PC54071. **The pack controller** — primary refrigeration rack controller. Drives the whole rack. | H |
| R31 | AK-CM 101C | Danfoss | 1 | IO Devices | Tag CM60071. LonWorks communication module — pack-to-system-manager fieldbus | M |
| R32 | AK-XM 205A | Danfoss | 1 | IO Devices | Tag XM61071. I/O module — 8 AI + 8 DO | M |
| R33 | AK-SM 850A | Danfoss | 1 | Controllers | Tag SM62111. **The System Manager** — site-level supervisory controller (matches RFQ "Interface = System Manager"). One of the most expensive single line items. | H |
| R34 | AK-XM 103A | Danfoss | 2 | IO Devices | Tags XM55071, XM56071. 4 AI + 4 AO — analog expansion. Qty 2 for channel count | M |
| R35 | AK-XM-101A | Danfoss | 1 | IO Devices | Tag XM57071. 8 AI sensor inputs | M |
| R36 | AK-XM 205A | Danfoss | 1 | IO Devices | Tag XM58071. Second 205A — note R32 also has 205A qty 1. **Possible duplicate row pattern**: same part appearing twice with different tags rather than one row qty 2. | M |
| R37 | AK-XM-208C | Danfoss | 1 | IO Devices | Tag XM59071. 8 AI + 4 EEV-style driver outputs | M |
| R38 | UD-400A | nVent | 3 | Terminal Blocks | Tags PDB1/2/3. Single-pole power distribution block, 335 A. Three of them = 3-phase main power distribution (one PDB per phase) | H |
| R39 | 7T.81.0.000.2303 | Finder | 1 | Panel AC & Heating | Panel thermostat — controls fan/heater inside enclosure | H |
| R40 | 7L.43.0.230.1100 | Finder | 1 | Buttons & Lights | LED panel light inside enclosure (service light) — 230 V coil | H |
| R41 | 7F.21.8.120.3100 | Finder | 1 | Panel AC & Heating | Filter fan, 120 V — pulls air through filter. Pairs with R42 exhaust filter | H |
| R42 | 7F.02.0.000.3000 | Finder | 1 | Panel AC & Heating | Exhaust filter — paired with fan above | H |
| R43 | LA-500-1 | Penn Union | 1 | Protection Devices | Tag GND. Mechanical ground lug — bonds enclosure to building ground | H |
| R44 | LPSC0002Z | Littelfuse | 3 | Protection Devices | Tags FU4121/4171/2151. 600 V CC POWR-SAFE fuse holder, 30 A 2-pole. Holds the three downstream control fuses | H |
| R45 | KLKR015 | Littelfuse | 4 | Protection Devices | Tag FU412 + spares. 15 A Class CC fast-acting — control transformer primary protection. Qty 4 = 1 + 3 spares | H |
| R46 | KLKR003 | Littelfuse | 4 | Protection Devices | Tag FU4171 + spares. 3 A — secondary / branch protection. Qty 4 same logic | H |
| R47 | KLKR001 | Littelfuse | 4 | Protection Devices | Tag FU2151 + spares. 1 A — very small control circuit | H |
| R48 | RM22TR33 | Schneider | 1 | Protection Devices | Phase-control monitoring relay, 380–480 VAC. Detects phase loss / sequence / undervoltage on incoming 3-phase | H |
| R49 | 9070T500D19 | Schneider | 1 | Transformers | Tag T4191. 500 VA, 208/240/277/380/480 → 24 V control transformer. Multi-tap primary | H |
| R50 | 9070FSC23 | Schneider | 1 | Transformers | Finger-safe terminal cover for the T4191 transformer — code-required touch-safe | H |
| R51 | 1415758 | Phoenix Contact | 1 | Hardware | Tag RECP5061. Convenience outlet + RJ45 — service receptacle on subpanel/door | H |
| R52 | 2702324 | Phoenix Contact | 1 | Networking | FL Switch 2000 series, 8-port managed industrial Ethernet switch — Modbus/IP backbone | H |
| R53 | 2320283 | Phoenix Contact | 1 | Power Supplies | Tag UPS6021. QUINT4-UPS/1AC/1AC/1KVA — UPS for controller / network ride-through | H |
| R54 | 1274118 | Phoenix Contact | 2 | Power Supplies | Tags BAT6031. VRLA-AGM battery module 24 V 7 Ah, paired with UPS. Qty 2 for double the runtime or required cabinet build | H |
| R55 | CL2-513C | ABB | 6 | Buttons & Lights | Tags LT14131..LT37131. Clear pilot lights, 120 V — six = six motor "run" indicators (4 MT + 2 LT) | H |
| R56 | CL2-513R | ABB | 6 | Buttons & Lights | Red pilot lights, 120 V — six = six motor "fault" indicators | H |
| R57 | M2SS2-10B | ABB | 6 | Buttons & Lights | Selector switch (Hand-Off-Auto presumably) — six = one per motor | H |
| R58 | MCBH-00 | ABB | 6 | Buttons & Lights | Contact-holder mounting for selector switches | H |
| R59 | MCB-10 | ABB | 6 | Buttons & Lights | NO contact for selector — one per selector | H |
| R60 | M9F42102 | ABB | 16 | Protection Devices | 16 mini-CBs. Tags span CB5042..CB53011 — control/door/load branch breakers. 16 = many small 120 V control circuits | M |
| R61 | ST201M-C15 | ABB | 1 | Protection Devices | Tag CB5062. 15 A miniature CB | M |
| R62 | ST201M-C1 | ABB | 1 | Protection Devices | Tag CB5021. 1 A mini-CB | M |
| R63 | ST201M-C4 | ABB | 1 | Protection Devices | Tag CB5151. 4 A mini-CB | M |
| R64 | ST201M-C6 | ABB | 7 | Protection Devices | Tags CB11071..CB39071. 6 A mini-CBs — likely VFD / drive feeder branches | M |
| R65 | ST201M-C32 | ABB | 1 | Protection Devices | Tag CB412. 32 A mini-CB — likely 120 V control transformer secondary | M |
| R66 | TGK12A | ABB | 1 | Protection Devices | Mini-CB connecting / busbar (TGK = horizontal bus link) for the ST201M row | H |
| R67 | CPTW3K0-GSC | WEG | 1 | Transformers | Tag T413. 3 kVA 480→120 V control power transformer (matches RFQ R34) | H |
| R68 | CWCA0-31-00V18 | WEG | 3 | Contactors | Mini-contactor — 3 of them. Likely auxiliary load contactors (lighting, condenser-fan circuit etc.) | M |
| R69 | 709-591 | Wago | 1 | Hardware | Tag SPARE FUSES. **Wago non-relay/PSU = estimate.** DIN-rail mount drawer for spare fuse storage | L |
| R70 | 2587-2144 | Wago | 1 | Power Supplies | Tag PWS615. 5 A base power supply — secondary 24 V DC supply (separate from Danfoss bus). Relays/PSU exempt from estimate caveat | H |
| R71 | 788-515 | Wago | 13 | Relays | 115 VAC, 2 changeover contacts — general-purpose interposing relays. 13 = many interlocks | H |
| R72 | 857-357 | Wago | 3 | Relays | 115 V AC/DC, 1 changeover | H |
| R73 | 858-158 | Wago | 2 | Relays | 120 VAC, 4 changeover — multi-pole timing / sequence relay | H |
| R74 | 857-304 | Wago | 3 | Relays | 24 VDC, 1 changeover — for the 24 V DC relay logic | H |
| R75 | 788-512 | Wago | 3 | Relays | 24 VAC, 2 changeover | H |
| R76 | 249-117 | Wago | 67 | Terminal Blocks | **Wago end-stop = estimate.** 10 mm DIN end-stops. Qty 67 is unusually high — suggests rough-count by terminal segments | L |
| R77 | 2002-3227 | Wago | 84 | Terminal Blocks | **Estimate.** TOPJOB-S triple-deck TB — main interface block. 84 = rough count for the I/O wiring | L |
| R78 | 2002-1201 | Wago | 14 | Terminal Blocks | **Estimate.** Feedthrough 2-conductor TB | L |
| R79 | 2002-3201 | Wago | 37 | Terminal Blocks | **Estimate.** Triple-deck through TB | L |
| R80 | 210-112 | Wago | 6 | Hardware | **Estimate.** DIN rail, 35×7.5 mm, 2 m long — 6 × 2 m = 12 m total rail | L |
| R81 | 249-116 | Wago | 8 | Terminal Blocks | **Estimate.** 6 mm screwless end-stop. Different from R76 (10 mm) — different rail segments | L |
| R82 | 1631 | Carolina Laser | 18 | Labeling | 22 mm rectangular plastic legend plate, 3 lines — engraved nameplates. 18 = approx. one per motor circuit + selector | M |

## Confidence distribution

- **H**: 36 rows. Mostly the major engineered components (CBs, contactors, controllers, transformers, UPS, switches, lights, fans, filters, ground lug, relays).
- **M**: 18 rows. Selection rationale plausible but not anchored to a supplemental (Danfoss I/O channel-count guesses, ST201M mini-CB sizing, WEG mini-contactor purpose).
- **L**: 16 rows. Two reasons: (1) MS165-65, MS132-16, AF16-30-10-13 conflict with the Motor Protection supplemental (these should be H but the disagreement makes them low-confidence); (2) Wago non-relay/PSU rows are estimates per data rules.

## Cross-check vs Motor Protection supplemental

Concrete delta the Motor Protection doc lets us land:

| Item | Main BOM | Motor Protection Selections | Verdict |
|---|---|---|---|
| MT MMP | MS165-65 (52–65 A) | MS165-54 (40–54 A) | Disagreement; MT FLA 51.1 A favors MS165-54 per band |
| MT contactor | AF65-30-00-13 | AF52-30-00-13 | Disagreement; AF52 matches the MS165-54 sizing |
| LT MMP (NG49) | MS132-16 (10–16 A) | MS132-10 (6.3–10 A) | Disagreement; LT FLA 9.84 A favors MS132-10 |
| LT contactor (NG49) | AF16-30-10-13 (with built-in aux) | AF09-30-00-13 (no aux) | Disagreement; frame size + aux convention both differ |
| BEA coupler | BEA65-4 + BEA16-4 | BEA65-4 + BEA16-4 | Match |
| CA4-10 aux blocks | qty 12 | 9 NG49-only (3 per non-VFD × 3) | Quantity differs |
| Main CB | XT5HU330ABFF000XXX | XT5HU330ABFF000XXX | Match |
| HKF1-11 MMP aux | qty 4 + 2 = 6 | NG49 alone = 4 + 2 = 6 | Match |

The motor-protection branch of the BOM looks like it may have been **manually upsized** away from the supplemental's recommendation — possibly intentional, possibly an error in copy-paste from an earlier rev. Not repaired; flagged.

## First-pass, not gospel

This is a single agent's read on physical-build intent. Any agent doing the wire-up should re-validate Danfoss I/O channel utilization against the IO sheet (currently blank) and the MMP/contactor sizing against the customer-confirmed motor nameplate.
