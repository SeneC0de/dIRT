# Panel-Feature → BOM Parts Association — E1392 / 4S Ranch

Source: rows 23..100 of `BOM - SCP-01` (between the purple bar at row 22 and the red bar at row 101).
Panel: 208VAC 3ph+E, SCCR 65 kAIC, single Rittal enclosure (1400×800×500 S/D).

Tag convention reminder: `<TYPE><PAGE><LINE>` — the digit string is "drawing page, line on page". `MT1` group = Medium-Temp rack (compressors B1–B3); `LT1` group = Low-Temp rack (compressors G1–G2); `HR` = heat reclaim; `S2` = subcooler / refrigerant collect.

Confidence flag in the Notes column: any row dominated by small WAGO TBs / end stops / marking is **LOW-CONFIDENCE** quantities per project rule.

## Master association table

| Panel Feature | Part Numbers (BOM row) | Qty | Notes |
|---|---|---|---|
| **Main service disconnect (DISC2011)** — incoming 208V 3ph | `XT5NU330ABFF000XXX` (35), `KXT5CUAL2X500K-3PC` (36), `KXT5RHESTFP` (37) | 1+1+1 | ABB XT5N 400 A 3-pole thermal-magnetic w/ Cu/Al 500 MCM lug kit and a rotary handle (RHE F/P standard). One disconnect, three line items. Row 37 description literally says "RETURNED" — ambiguous, flagged. |
| **Power distribution / main ground bar** | `PK12GTA` (38), `LA-500-1` (62) | 1+1 | Schneider 12-terminal ground-bar kit (Load-center accessory) + Penn-Union 500 MCM mechanical lug for the main GND landing. |
| **Power distribution blocks (PDB)** | `UD6C500AL` (39) | 3 | nVent 500 MCM 6-pole PDBs ×3 — one per phase + neutral / or per circuit-group, fed from disconnect. |
| **Compressor 1 motor protection (MT1 B1-2U1, VFD-fed)** | (covered under "VFD compressor branch" — VFD itself is customer-furnished) | — | Per Load Calc, B1-2U1 is a VFD-driven 4FTE-20K compressor (84.6 FLA). The BOM does not include the VFD — that's customer-furnished or treated as a separate spec; the BOM only carries the panel-side gear. |
| **Compressor 2 & 3 across-the-line (MT1, contactor-fed)** | `MPW100-3-U100` (40), `CWM105-11-30V18` (41), `TSB SC-11 MPW100` (42), `IB MPW100` (43) | 3, 3, 2, 6 | WEG motor protector 100 A frame (3 units = 1 per across-the-line compressor: B2-2M1, B3-2M1 — and a 3rd suggests it also covers B1 protective bypass or a spare). WEG contactor 105 A AC3 with 24VDC coil ×3. Trip-signal block ×2 + 6 insulating plates. **Quantity of 3 motor protectors vs the Load Calc which shows 2 across-the-line MT1 compressors is a minor mismatch — flagged.** |
| **Small compressor protection (LT1 G2-2U1 — across-the-line)** | `MPW40-3-U016` (44), `LST25` (45), `ECCMP-40B38` (46), `CWB18-11-30D15` (47) | 2, 2, 2, 2 | WEG 40 A frame motor protectors ×2 (LT1 has two 2ESL-4K compressors at 11.1 FLA each per Load Calc) + companion connectors + WEG 18 A contactors ×2. |
| **Control relays — small mini-contactors** | `CWCA0-31-00V18` (48) | 4 | Tagged `CR7051, CR14081, CR27051, CR33081` — four pages span MT1 (14), LT1 (27,33), and a general (7) location. WEG mini-contactor 24 VDC coil, 3 NO + 1 NC. |
| **Control power transformer (T4131, 3 kVA)** | `CPTW3K0-GSC` (49) | 1 | WEG 208/120 VAC 3 kVA transformer for the 120 VAC control bus. Matches Load Calc T5031 line item. |
| **24 VAC transformer (T4191, 500 VA)** | `9070T500D19` (50), `9070FSC23` (51) | 1+1 | Schneider 500 VA multi-tap (208/240/277/380/480 → 24V) + finger-safe terminal cover. Per Load Calc this is the 24 VAC supply for valve coils / instrument power. |
| **Local 120/24 VAC class-2 transformers (T6111..T6191)** | `TR50VA005` (64) | 5 | RIB 50 VA class-2 120/24 VAC transformers ×5, one per evaporator/control circuit (page 61, 61, 61, 61, 61 — the T61xx tagging suggests page 61 area / med-press regs). One per pressure-reg circuit or compressor section. |
| **Panel cooling & climate** | `7T.81.0.000.2303` (52) `7L.43.0.230.1100` (53) `7F.02.0.000.3000` (54) `7F.21.8.120.3100` (55) | 1, 1, 1, 1 | Finder thermostat (`TAS5041`) + LED enclosure light (`WLT5021`) + exhaust filter + reverse-flow filter fan (`MTR5041`). Single climate-control kit for the enclosure. |
| **3-phase monitor relay** | `RM22TR31` (56) | 1 | Schneider Harmony 3-phase control relay `CR2031`, 8 A 2CO, overvoltage/undervoltage detection at 200..240 VAC. Tied to the 208 V incoming bus. |
| **Pilot lights — RUNNING (white)** | `XB5AVG1` (57) | 5 | Tagged `LT14131, LT18131, LT22131, LT33131, LT37131` — pages 14, 18, 22, 33, 37. White RUN indicators for MT1-C1, MT1-C2, MT1-C3, LT1-C1, LT1-C2 (five compressors total). Matches Legend Plates entries `LT14131 MT1 COMPRESSOR 1 RUNNING` etc. |
| **Pilot lights — FAILURE (red)** | `XB5AVG4` (58) | 5 | Tagged `LT14181, LT18181, LT22181, LT33181, LT37181`. Red FAULT indicators for the same five compressors. |
| **Selector switches — Auto/Off/Manual per compressor** | `XB4BD21` (87) | 5 | Tagged `SS14061, SS18061, SS22061, SS33061, SS37061`. Schneider Harmony 2-position maintained 22 mm switch, 1 NO. One per compressor (same pages as pilot lights). |
| **Legend plate strip (door labels)** | `1631` (61) | 15 | Carolina Laser textured plastic 22 mm legend plate, 3-line. 15 plates ≈ 5 lights white + 5 lights red + 5 selector switches = 15. Counts line up. |
| **Door-mounted convenience outlet + RJ45** | `1415759` (65) | 1 | Phoenix Contact combined outlet + RJ45 jack — tagged `RECP5061`. Located on page 50/61 area. |
| **Ethernet switch (Copeland bus)** | `2702324` (66) | 1 | Phoenix Contact FL Switch 2000 series 8-port managed industrial Ethernet (10/100). Matches the proposal scope ("Ethernet switch"). Untagged. |
| **UPS (control power back-up)** | `2320283` (67), `1274118` (68) | 1 + 2 | Phoenix Contact QUINT4-UPS/1AC/1AC/1kVA (`UPS6021`) + 2× 7 Ah VRLA-AGM 24 VDC battery modules (`BAT6031, BAT6032`). Matches proposal scope ("UPS w/ battery backup"). |
| **24 VDC power supply (panel-wide)** | `2587-2144` (100) | 1 | WAGO 5 A 24 VDC base supply — note: lives *exactly on* the red-bar boundary (row 100 = last real BOM row). For the Copeland Visiograph, IO cards, relays. |
| **Energy meter w/ Rogowski coils (PM5011)** | `2908307` (69) | 1 | Phoenix Contact `PM5011` — single line, description blank in the BOM but proposal scope explicitly calls out "Energy meter w/ Rogowski coils". |
| **Energy-meter Rogowski coils (3-phase)** | `2910322` (70) | 3 | Phoenix Contact `RC5011/CBL5011, RC5031/CBL5031, RC5051/CBL5051` — three Rogowski coil + cable kits, one per phase, matching the energy meter. |
| **Copeland controller stack (CUSTOMER-FURNISHED per proposal)** | `860-1305` (23) `638-4880` (24) `810-3065` (25) `810-3066` (26) `818-9010` (27) `818-5003` (28) `810-3064` (29) `818-9002` (30) | 1,1,1,1,1,2,1,1 | E3 controller, E2E plug-in DIO card, MultiFlex 168A0 (`C55071`), MultiFlex 168 (`C56071`), iPro CO2 high-press controller (`IP57051`), 2× XEV20D dual stepper kits w/ cables (`VA58051, VA59061`), 88 I/O board (`MF73061`), Visiograph display (`VG70181`). PO column = "FI" / "stock" / "backordered" — these are pulled from internal stock or "FI" (furnished items), prices zero. **Proposal says "Copeland E3 controller and I/O provided by Vitalis"** — so these BOM rows are tracking the parts but not pricing them. |
| **Branch-circuit breakers — 1P, various** | `UMBW-4C2-1` (72), `M9F42103` (73), `M9F42115` (74), `M9F42120` (75), `M9F42102` (76), `M9F42101` (77), `M9F42106` (78), `M9F42130` (79) | 5, 5, 1, 2, 16, 2, 6, 1 | A mix of WEG `UMBW-4C2-1` (CB6111, CB6131, CB6151, CB6171, CB6191 → page 61 area, med-press) + Schneider M9F4 family (Multi9 mini CBs): qty 16 of M9F42102 dominates and serves many tags. **Per the page numbers in the tag list — these breakers fan out across MT1 fans (C111/C131…), LT1 (C5042, CB31011…), pressure-regs (CB6111 family). Treat as the secondary distribution.** |
| **Class-CC fused disconnects (xfmr primary protection)** | `LPSC0002Z` (80) | 2 | Littelfuse `FU4121` — 600 V Class CC POWR-SAFE 2-pole fused holder. Matches Load Calc "30a Primary Protection, cc fuses" callout for the 3 kVA xfmr. |
| **CC fuses 15 A** | `KLDR015` (81) | 2 | Littelfuse `FU4121` 15 A Class CC time-delay fuses. Pair them with the LPSC holders above. |
| **CC fuses 5 A (24 VAC xfmr)** | `KLDR005` (82) | 2 | Littelfuse `FU4181` — 5 A Class CC time-delay. Matches Load Calc "5a Primary Protection" for 500 VA xfmr. |
| **Spare-fuses drawer + spares** | `709-591` (83), `KLDR015` (84), `KLDR005` (85) | 1, 2, 2 | WAGO DIN-rail switchgear drawer holding spare 15 A and 5 A CC fuses (2 of each). Tagged "SPARE FUSES" — function tag, not device tag. |
| **115 V control relays — coil from interlocks** | `788-515` (71) | 14 | WAGO 115 VAC, 2CO, 8 A relay modules. Tagged `CR12141, CR13161, CR16121, CR17161, CR20121, CR21161, CR31141, CR32081, CR35121, CR36161, CR43101, CR43181, CR44151` (13 tags). 14 quantity — one spare. Page numbers span MT1 + LT1 compressor circuits + oil-sep page 43. **Wago relay modules — quantity is high-confidence per project rule (relays + PSU Wagos are accurate).** |
| **24 VAC control relays** | `788-512` (60) | 3 | WAGO 24 VAC, 2CO, 8 A. Tagged `CR38081, CR53091, CR38201` — heat-reclaim / S2-area circuits (pages 38, 53). |
| **24 VDC control relays** | `857-304` (59) | 3 | WAGO 24 VDC, 1CO. Tagged ` CR7071, CR7072` — only two tags listed for qty 3 (one extra unbilled? or spare?). Page 7 is 120 VAC distribution. |
| **Resistor — line-termination / current-sense** | `594-SFR25H1201%TR` (86) | 2 | Mouser 120 Ω 1/2 W 1 % metal-film resistors. Tagged `RES56101, RES59171` — pages 56 and 59 (gas-cooler and HP reg sections). Likely 120 Ω end-of-line termination for modbus/RS485 between Copeland controllers and the regulator stations. |
| **Terminal blocks — ground (TOPJOB-S, 7.5 mm)** | `2006-1207` (88) | 9 | WAGO TOPJOB-S 2-conductor ground TB, 7.5 mm wide, green-yellow. **LOW-CONFIDENCE qty (small-TB rule).** |
| **End stops (DIN rail)** | `249-117` (89) | 25 | WAGO 10 mm screwless end stop. **LOW-CONFIDENCE qty (estimate per project rule).** |
| **TOPJOB-S triple-deck through (5.2 mm)** | `2002-3227` (90) | 51 | WAGO triple-deck feedthrough TB. **LOW-CONFIDENCE.** |
| **Ground TB 5.2 mm** | `2002-1207` (91) | 2 | WAGO ground TB green-yellow. **LOW-CONFIDENCE.** |
| **Feedthrough TB 5.2 mm** | `2002-1201` (92) | 10 | WAGO gray 5.2 mm feedthrough. **LOW-CONFIDENCE.** |
| **TOPJOB-S triple-deck (L/L/L)** | `2002-3201` (93) | 33 | WAGO L/L/L triple-deck. **LOW-CONFIDENCE.** |
| **Feedthrough TB 12 mm** | `2016-1201` (94) | 3 | WAGO 12 mm gray feedthrough. **LOW-CONFIDENCE.** |
| **Ground TB 12 mm** | `2016-1207` (95) | 1 | WAGO 12 mm green-yellow ground. **LOW-CONFIDENCE.** |
| **TOPJOB-S triple-deck PE/N/L** | `2002-3217` (96) | 13 | WAGO PE/N/L triple-deck. **LOW-CONFIDENCE.** |
| **Feedthrough TB 7.5 mm** | `2006-1201` (97) | 35 | WAGO 7.5 mm gray feedthrough. **LOW-CONFIDENCE.** |
| **Jumpers** | `788-113` (98) | 15 | WAGO Pos. 1 & 3 jumpers. **LOW-CONFIDENCE** (marking/jumper estimates). |
| **DIN rail (35×7.5 mm)** | `210-112` (99) | 5 | WAGO 35×7.5 mm steel carrier rail, 2 m, slotted. **LOW-CONFIDENCE.** |
| **Feedthrough heavy TB (2.5 mm² quattro)** | `3209578` (63) | 2 | Phoenix Contact PT 2.5-QUATTRO — labelled `TBC`. Used for splitting one wire to multiple devices. Marked "stock". **Note: PHX TBs outside the small-Wago rule may be more accurate; but tag = TBC suggests common bus and qty 2 is plausible.** |
| **Rittal enclosure + mech accessories** | `8845500` (31), `8145235` (32), `8614650` (33), `8614850` (34) | 1, 1, 2, 2 | 1400×800×700 (mm) S/D enclosure + side panels (1400×500h) + 500×400 partial mounting plates ×2 + 700×400 partial mounting plates ×2. (Note: proposal says depth 500 mm but BOM says 700 mm — flagged.) |

## Cross-cutting groupings

### Per-compressor parts (5 compressors total: 3 MT1 + 2 LT1)

| Compressor | Pilot RUN | Pilot FAULT | Selector SS | Motor protector | Contactor | Branch CB |
|---|---|---|---|---|---|---|
| MT1 C1 (B1-2U1, VFD-fed) | LT14131 (XB5AVG1) | LT14181 (XB5AVG4) | SS14061 (XB4BD21) | (VFD-side, not in BOM as MPR) | (VFD) | (in VFD) |
| MT1 C2 (B2-2M1) | LT18131 | LT18181 | SS18061 | MPW100-3-U100 | CWM105-11-30V18 | — |
| MT1 C3 (B3-2M1) | LT22131 | LT22181 | SS22061 | MPW100-3-U100 | CWM105-11-30V18 | — |
| LT1 C1 (G1-2U1, VFD-fed) | LT33131 | LT33181 | SS33061 | MPW40-3-U016 | CWB18-11-30D15 | — |
| LT1 C2 (G2-2U1) | LT37131 | LT37181 | SS37061 | MPW40-3-U016 | CWB18-11-30D15 | — |

This is a clean pattern — 5 of every door-device per compressor (15 legend plates = 5×3 = matches qty). The motor-protector / contactor counts (3 + 2 = 5) align almost — but qty of MPW100-3-U100 is **3** in the BOM while the across-the-line MT1 compressors number **2** (per Load Calc). Possibilities: spare unit, used for the heat-reclaim circuit elsewhere, or a count error. **Flagged as a finding.**

### Per-pressure-regulator parts (page 61–63 = T61xx tagging area)

- 5× `TR50VA005` 50 VA local 120/24 xfmrs (T6111, T6131, T6151, T6171, T6191)
- 5× `UMBW-4C2-1` WEG 1-pole CBs (CB6111, CB6131, CB6151, CB6171, CB6191)
- 5× `M9F42103` Schneider 1-pole CBs (CB6112, CB6132, CB6152, CB6172, CB6192)

Two breakers per regulator (one for the xfmr primary feed, one for the 24V secondary or solenoid). 5 regulators × 2 CBs + 1 xfmr each. Consistent.

### Control bus

- Copeland E3 + I/O cards + Visiograph display (rows 23–30) — customer-furnished
- WAGO 24 VDC base PSU (row 100)
- Phoenix Contact UPS + 2 batteries (rows 67–68)
- 14× 115 VAC + 3× 24 VAC + 3× 24 VDC WAGO relay modules (rows 59–60, 71)

### Spares / consumables outside the bars

(See `xlsx-profile.md`) — Wire, ground bar kit (extra), 4× 2.25×3 wire duct, panel CNC cutouts, labels, hardware, and labor estimates. Excluded from this association per the project rule.

## Open questions & inconsistencies

1. **MPW100-3-U100 qty 3** vs **2 across-the-line MT1 compressors** in Load Calc. Off by one — possible spare or unaccounted use.
2. **Rittal depth: 700 mm in BOM (8845500) vs 500 mm in proposal text.** Could be a proposal typo or a depth-change between proposal and final BOM.
3. **Copeland items priced at $0.** Consistent with the proposal's "provided by Vitalis" clause but worth verifying these aren't accidentally omitted from cost roll-up.
4. **Row 37 description `RHE XT5 F/P STAND. RETURNED`.** Ambiguous — "RETURNED" as a vendor-return note carried through, or a literal return that should be removed? Not in zero-qty section so currently counted.
5. **Small-WAGO TB counts (rows 88–99) are estimates per the project rule.** Every quantity on those 12 rows should be considered indicative, not authoritative.
6. **CR7071, CR7072 (qty 3 for 2 tags).** Off by one — extra relay unaccounted or extra-spare.
