# E1404 — Panel-Feature → BOM Parts Association

Grouping of the 70 real BOM rows (R13–R83, between purple and red bars) by panel feature. Tag prefixes carry most of the signal (CB=circuit breaker, FU=fuse, PC=pack controller, XM=expansion module, SM=system manager, CM=comm module, PWS=power supply, T=transformer, UPS=ups, BAT=battery, LT=light, PDB=power distribution block, GND=ground lug, RECP=receptacle).

Reminder: Wago parts outside relays/PSUs (small TBs, end stops, marking, DIN rail) are **estimates** per data rules.

| Panel Feature | Part Numbers | Qty | Notes |
|---|---|---|---|
| **Enclosure & subpanels** | SCE-724818FSD (R13), SCE-72P48F1 (R14), SCE-72SMP14 (R15) | 1 / 1 / 1 | 72×48×18 outer (Type 3R per RFQ), full back-subpanel, side-mount subpanel. Saginaw set. |
| **Main disconnect / Main breaker** | XT5HU330ABFF000XXX (R16), KXT5CUAL2X500K-3PC (R17), KXT5RHESTFP (R18) | 1 / 1 / 1 | Tag CB2041. 300 A ABB XT5, load-side lug kit, rotary handle w/ interlock+padlock. Matches Motor Protection Main Breaker tab. |
| **MT compressor branches (4 motors, MT1–MT4)** | MS165-65 (R19), HKF1-11 (R20), AF65-30-00-13 (R21), CA4-10 (part of R22), BEA65-4 (R23) | 4 / 4 / 4 / 9 of 12 / 4 | One MMP + aux + contactor + 3 aux blocks (non-VFD) + coupler per MT motor. MT1 is VFD-driven and gets 0 CA4-10 (3 non-VFD MTs × 3 = 9). **FLAGGED**: MS165-65 here vs MS165-54 in Motor Protection supplemental; AF65 here vs AF52 in supplemental. |
| **LT compressor branches (2 motors, LT1–LT2)** | MS132-16 (R24), HKF1-11 (R25), AF16-30-10-13 (R26), CA4-10 (part of R22), BEA16-4 (R27) | 2 / 2 / 2 / 3 of 12 / 2 | One MMP + aux + contactor + 3 aux blocks (LT2 non-VFD only) + coupler per LT motor. LT1 is VFD-driven. **FLAGGED**: MS132-16 here vs MS132-10 in supplemental for NG49 LT; AF16-30-10 (built-in aux) vs AF09-30-00 in supplemental. |
| **Refrigeration pack controller (Danfoss core)** | AK-PC 782B (R30), AK-OB 110 (R28) | 1 / 1 | Tag PC54071. Primary refrigeration controller + 1 AO module. |
| **System Manager (site supervisor)** | AK-SM 850A (R33), AK-CM 101C (R31) | 1 / 1 | Tag SM62111. Matches RFQ Interface = System Manager. Plus comm module CM60071. |
| **Danfoss I/O expansion bank** | AK-XM 205A (R32 + R36), AK-XM 103A (R34), AK-XM 101A (R35), AK-XM 208C (R37) | 1 + 1 / 2 / 1 / 1 | 6 expansion modules total. Tags XM55..XM61. Mix of AI / AO / DO / EEV-driver capacity. Note: AK-XM 205A appears in two rows with different tags (XM61071, XM58071) rather than qty 2 on one row. |
| **Danfoss 24 V DC bus power** | AK-PS 250 (R29) | 2 | Tag PWS5151. Two of them = N+1 redundancy for Danfoss control bus. |
| **Phase / power quality monitoring** | RM22TR33 (R48) | 1 | Schneider phase-loss/sequence/UV relay on 480 VAC incoming. |
| **3-phase power distribution** | UD-400A (R38) | 3 | Tags PDB1, PDB2, PDB3 — one nVent block per phase, 335 A rated. |
| **Ground & bonding** | LA-500-1 (R43) | 1 | Tag GND. Penn-Union mechanical ground lug. |
| **Control transformer (480 → 120 V, 3 kVA)** | CPTW3K0-GSC (R67), CB412 ST201M-C32 (R65), TGK12A (R66, bus) | 1 / 1 / 1 | Tag T413. WEG 3 kVA, protected by 32 A mini-CB on primary. |
| **Control transformer secondary (24 V, 500 VA)** | 9070T500D19 (R49), 9070FSC23 (R50) | 1 / 1 | Tag T4191. Schneider 500 VA multi-tap → 24 V. Finger-safe cover. |
| **Control fuses (with spares)** | LPSC0002Z (R44), KLKR015 (R45), KLKR003 (R46), KLKR001 (R47) | 3 / 4 / 4 / 4 | Tags FU4121/4171/2151. Fuse holders + 15 A / 3 A / 1 A control fuses; qty 4 each = 1 active + 3 spares pattern. |
| **UPS for controller/network** | 2320283 (R53), 1274118 (R54) | 1 / 2 | Tag UPS6021 + BAT6031. Phoenix QUINT4-UPS 1 kVA + 2 × VRLA-AGM battery modules. |
| **Industrial Ethernet network** | 2702324 (R52) | 1 | Phoenix FL Switch 2000, 8-port managed. Modbus-IP backbone. |
| **Service receptacle** | 1415758 (R51) | 1 | Tag RECP5061. Conv outlet + RJ45. |
| **Door-mounted indicators (per motor)** | CL2-513C clear (R55), CL2-513R red (R56) | 6 / 6 | Tags LT14131..LT37131. 6 motors × (run + fault) lights = 12 pilot lights. RFQ specified RUN-FAULT-SWITCH layout. |
| **Door-mounted selector switches (per motor)** | M2SS2-10B (R57), MCBH-00 (R58), MCB-10 (R59) | 6 / 6 / 6 | Off/Auto selector + contact-holder + NO contact = 6 sets (one per motor). RFQ confirms door switches required, LT above MT. |
| **Door-mounted nameplates** | 1631 (R82) | 18 | Carolina Laser 22 mm rectangular legend plates. 18 = motors + selectors + main + spares. |
| **Branch / control breakers (120 V mini-CBs)** | M9F42102 (R60), ST201M-C15 (R61), ST201M-C1 (R62), ST201M-C4 (R63), ST201M-C6 (R64) | 16 / 1 / 1 / 1 / 7 | Tags span CB5042–CB53011 + named branches. M9F42102 in qty 16 is the majority of 120 V control branch protection. ST201M-C6 (6 A) ×7 likely matches VFD logic-feeder / pack branches. |
| **Secondary 24 V DC supply (Wago)** | 2587-2144 (R70), 709-591 (R69) | 1 / 1 | Tag PWS615. Wago 5 A 24 V DC PSU + spare-fuse drawer. PSU is exempt from estimate caveat; drawer is hardware. |
| **Interposing relays (115 VAC)** | 788-515 (R71), 857-357 (R72), 858-158 (R73) | 13 / 3 / 2 | Wago relays — relays/PSU exempt from estimate caveat. Bulk 13 ×788-515 = main interlock pool; 858-158 4-pole likely a sequence or door-light relay. |
| **Interposing relays (24 V)** | 857-304 (R74, 24 VDC), 788-512 (R75, 24 VAC) | 3 / 3 | 24 V relay logic for Danfoss / sensor side. |
| **Auxiliary mini-contactors** | CWCA0-31-00V18 (R68) | 3 | WEG mini-contactors — likely panel lights, condenser fan, or one-off load. |
| **Panel HVAC (enclosure climate)** | 7T.81 thermostat (R39), 7F.21 filter fan 120 V (R41), 7F.02 exhaust filter (R42), 7L.43 panel light (R40) | 1 / 1 / 1 / 1 | Finder set — fan + filter + thermostat + service light. |
| **Terminal blocks & DIN rail (Wago — ESTIMATES)** | 249-117 (R76), 2002-3227 (R77), 2002-1201 (R78), 2002-3201 (R79), 210-112 (R80), 249-116 (R81) | 67 / 84 / 14 / 37 / 6 / 8 | **Low confidence per data rules.** End stops, TOPJOB-S triple-deck and feedthrough TBs, 2m DIN rail segments. Quantities rough-counted. |

## Notes & open questions

1. The **CA4-10** aux blocks (R22) are a single line item with qty 12 covering both MT and LT motor branches. The Motor Protection supplemental BOM splits them into separate rows per branch with trailing-space hacks. Both intents are reconcilable but the formats differ — flag for any downstream tooling that joins these two artifacts.
2. **VFD-driven motors (MT1, LT1)** are present but no VFD parts are in the BOM. The RFQ Project Info marks MT1 and LT1 as VFD=True but the actual drives don't appear among the 70 rows — possibly supplied by Danfoss as part of the pack controller bundle (AK-PC 782B), or possibly outside the panel scope and supplied separately. **Open question — flagged as event.**
3. **CO2 sensor** mentioned in the customer email (Panel Notes R6) — not visible as a discrete BOM line. Likely lives on the inputs of an AK-XM 101A (R35, 8 AI sensor inputs). Customer-intent item that ends up implicit in the I/O channel allocation.
4. **Spare I/O board** also requested in the email — that matches one of the doubled AK-XM 205A rows (R36 has a distinct tag XM58071 vs R32 XM61071). Plausible mapping.
5. The **18 legend plates** (R82) vs the actual count of door-mounted features (6 selectors + 12 lights = 18) matches perfectly — a useful sanity-check passing point.
