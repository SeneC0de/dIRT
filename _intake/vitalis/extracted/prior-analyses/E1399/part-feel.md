# E1399 — Part-Feel Pre-Pass

First-pass guesses at the attributes that likely drove each BOM-row's selection. Covers the 74 real BOM rows (between purple R14 and red R89). Confidence is gut-feel, not gospel.

| Part | Category | Attributes Driving Selection | Confidence |
|---|---|---|---|
| AK-OB 110 | Danfoss AK analog output | Compatible with AK-PC 782B controller bus; output stage for the pack | high |
| AK-PS 250 (×2) | Danfoss AK power supply | Voltage rail required by Danfoss AK family; pair for redundancy or split load | high |
| AK-PC 782B | Danfoss AK pack controller | Specific to CO2 rack/pack control (Roxsta-class); customer-specified | high |
| AK-CM 101C | Danfoss AK communications module | Modbus/Lon gateway for the controller; standard AK accessory | high |
| AK-XM 205A (qty 1 + another qty 1) | Danfoss AK I/O 8AI+8DO | I/O channel count needed for compressors + sensors; spare set | high |
| AK-SM 850A | Danfoss System Manager | Top-of-stack HMI+supervisory; required when AK-SM is the user interface | high |
| AK-XM 103A (×2) | Danfoss AK 4AI+AO | Pressure-loop control output channels | high |
| AK-XM 101A | Danfoss AK 8AI sensor | Temperature-sensor count; cabled to remote sensors | high |
| AK-XM 208C | Danfoss AK 8AI + 4 driver outputs | Valve-driver outputs (steppers/PWM) for EEVs / regulators | med |
| SCE-726018FSD | Enclosure | Size needed for the rack-control content (60 W subpanel); NEMA 3R/12/13; outdoor-rated bezel | high |
| SCE-72P60F1 | Subpanel | Matched to enclosure SKU; full-size mounting | high |
| XT6HU3800EFF000XXX | ABB MCB | Frame sized to MOCP 656 A (Load Calc); 800 A XT6 frame, F-trip; UL 489 | high |
| KXT6CUAL2X750KCC-3 | XT6 lugs | Wire size from MOCP / NEC ampacity → 750 kcmil double-lug; CuAl bimetal | high |
| KXT6RHESTFP | XT6 rotary shaft / handle | Door-mounted operator needed for a service-disconnect on the FSD enclosure | high |
| UD6C500AL (×6) | Power distribution block | 380 A single-pole, 6 outgoing tap-offs (per phase), aluminum bus — sized to MCA | high |
| IB MPW100 (×5) | WEG insulating plate | Side-shield safety for adjacent MPW100 motor protectors | med |
| MPW100-3-U075 / U090 (×1 + ×4) | WEG manual motor protector | FLA per compressor (77.1 A range from Load Calc) → U090 frame; U075 for the smaller one | high |
| CWM95-11-30V18 (×5) | WEG contactor | Sized to compressor FLA (77 A class), 120 VAC coil ("V18" suffix), 1NO+1NC aux | high |
| TSB SC-11 MPW100 (×5) | WEG trip-signaling block | Trip status feedback to the AK controller (digital input back to PLC) | high |
| ECCMP-80B80 (×4) | WEG connector kit | Mechanical link between MPW100 and CWM95 (direct-mount kit) | high |
| MPW80-3-U040 / U065 (×1 + ×3) | WEG manual motor protector | LT-side FLA (35-49 A); U040 for the 35 A VFD'd unit | high |
| CWB50-11-30D15 (×1) / CWB80-11-30D15 (×3) | WEG contactor | LT-side compressor FLA; "D15" suffix = 240/277 VAC coil — verify against Load Calc | med |
| TSB (qty 4) | WEG trip-signaling block | Pairs with the LT manual motor protectors | med |
| LST65 (×4) | WEG terminal connector | Incoming-power TB at the LT motor-protector cluster | med |
| LPSC0002Z (×2) | Littelfuse CC fuse holder | 30 A 600V Class CC — sized for the 120/24 VAC control transformer primaries | high |
| KLDR015 (×2 + ×2 spare) | Littelfuse 15 A CC fuse | Time-delay (KDLR); transformer primary protection | high |
| HCLR03 (×2 + ×2 spare) | Littelfuse 3 A CC fuse | Non-indicating; small-load control branch protection | high |
| 7T.81 (Finder) | Panel thermostat | Activates filter-fan above setpoint; cabinet-cooling control | high |
| 7L.43 (Finder) | Panel LED light | Service light inside enclosure | high |
| 7F.02 (Finder) | Panel exhaust filter | Mated to the 7F.21 fan as exhaust path | high |
| 7F.21 (Finder) | Panel filter fan | Sized for enclosure volume + thermal load (Finder catalog selection) | high |
| E214-16-101 (×9) | ABB group switch | Door-mount 16 A 1CO selector; one per compressor / mode HOA | high |
| CL2-513C (×9 clear) | ABB pilot light | "Running" indication, 110-130 VAC LED, color-coded clear | high |
| CL2-513R (×9 red) | ABB pilot light | "Fault" indication, 110-130 VAC LED, color-coded red | high |
| 3209578 PT 2.5-QUATTRO (×2) | Phoenix Contact 4-conductor TB | Quattro = 2-in / 2-out feedthrough — likely for a shared neutral or comms ground bus | low |
| 1415758 HEAVYPORT (×1) | Phoenix combo outlet+RJ45 | Door-mount service outlet + ethernet drop (RECP5061 tag) | high |
| 2702324 FL Switch 2000 (×1) | Phoenix Contact managed switch | Pre-checked TRUE in RFQ Panel Options; 8-port managed required by Vitalis network spec | high |
| CPTW3K0-GSC (×1) | WEG 3 kVA 480/120 transformer | T5031 in Load Calc; sized for 120 VAC control + door-light loads | high |
| 9070T500D19 (×1) | Schneider 500 VA T-series | T5071 in Load Calc; 208/24 VAC for Danfoss AK control voltage | high |
| 9070FSC23 (×1) | Schneider terminal cover | Required UL accessory for 9070T series finger-safe | high |
| XB5AS8444 (×1) | Schneider mushroom E-stop | Pre-checked TRUE in RFQ; 22 mm, 2NC, latching twist-release | high |
| RM22TR33 (×1) | Schneider 3-phase monitor relay | Phase-loss / unbalance / sequence on 460 V incoming; trips control coil | high |
| ST201M-C6 (×9) | ABB UL1077 MCB | Each 120 VAC sub-feed (e.g. compressor control circuits) at 6 A | high |
| ST201M-C15 (×2) | ABB UL1077 MCB | Larger 120 VAC branches (door lighting + outlet ckt?) | med |
| ST201M-C20 (×2) | ABB UL1077 MCB | RECP outlet circuit (typical 20 A) + one heater branch | med |
| ST201M-C2 (×19) | ABB UL1077 MCB | The bulk — small-coil and 24 V branch protection; one per sensor branch typical | high |
| ST201M-C1 (×2) | ABB UL1077 MCB | AK-PS 250 primary protection | med |
| ST201M-C32 (×1) | ABB UL1077 MCB | Single larger 120 VAC tap — likely the 7F.21 fan circuit or interior service feed | med |
| PK12GTA (×1) | Schneider ground-bar kit | Earth-bus termination | high |
| 709-591 (×1) | WAGO spare-fuse drawer | Carrier for the spare KLDR + HCLR fuses (`SPARE FUSES` tag) | high |
| 788-515 (×14) | WAGO 115 VAC interposing relay | Coil voltage match to 120 VAC control bus; 2 changeover @ 8 A — workhorse interposing relay | high |
| 857-304 (×3) | WAGO 24 VDC interposing relay | Coil match to Danfoss DO voltage; 1 CO, low-current loads | high |
| 788-512 (×3) | WAGO 24 VAC interposing relay | Coil match to T5071 secondary; 2 CO | high |
| 2006-1207 (×9) | WAGO ground TB (7.5 mm) | Field-ground returns; sized to wire-pitch on the matching 2006-1201 feedthrough | low (estimate) |
| 249-117 (×25) | WAGO end stop (10 mm) | One per rail break (typical 2-3 per rail); 25 implies ~10 rail segments | low (estimate) |
| 2002-3227 (×51) | WAGO triple-deck TB | Three-conductor per slot — heavy sensor termination block | low (estimate) |
| 2002-1207 (×2) | WAGO ground TB (5.2 mm) | Mate to 2002-1201 series | low (estimate) |
| 2002-1201 (×10) | WAGO feedthrough TB (5.2 mm) | Smallest pitch; signal-level | low (estimate) |
| 2002-3201 (×33) | WAGO triple-deck L/L/L | Power-distribution within control bus | low (estimate) |
| 2016-1201 (×3) | WAGO feedthrough TB (12 mm) | Larger pitch; sized for heavier branches | low (estimate) |
| 2016-1207 (×1) | WAGO ground TB (12 mm) | Mate to 2016-1201 | low (estimate) |
| 2002-3217 (×13) | WAGO triple-deck PE/N/L | Combined ground/neutral/line block — useful at sensor headers | low (estimate) |
| 2006-1201 (×35) | WAGO feedthrough TB (7.5 mm) | Workhorse pitch; bulk of the field-terminal field | low (estimate) |
| 788-113 (×15) | WAGO jumper bar | Pos 1 & 3 — common-rail bridging across relay outputs | low (estimate) |
| 210-112 (×5) | WAGO DIN rail (2 m) | Rail count proportional to subpanel size | low (estimate) |
| 2587-2144 (×1) | WAGO 5 A power supply | Secondary 24 V rail for low-current loads (likely sensor excitation) | med |
| 1631 (×18) | Carolina Laser legend plate | One per door-mount device (selectors + pilot lights + E-stop + outlet+ethernet group) — 9 switches + 9 lights wouldn't tally; 18 may = 9 switches + 9 paired lights consolidated. **18 ≠ 33 Legend-Plates sheet rows — discrepancy noted.** | med |
| LA-500-1 (×1) | Penn Union mechanical lug | Main grounding lug; sized for 4 AWG to 500 MCM | high |

## First-pass takeaways
- The two highest-confidence drivers are **Load Calc ampacity → frame sizes** (MCB, lugs, distribution blocks, motor-protector frames) and **voltage-rail matching** (120 VAC vs 24 VAC vs 24 VDC dictates contactor and relay coil suffixes).
- The lowest-confidence cluster is the WAGO field-TB pile: per charter these are estimates, and the qty pattern (35 / 51 / 33 / 25) is round-ish in a way that suggests rule-of-thumb sizing.
- A few `=AI()` placeholder formulas survive in the desc and manufacturer columns for the WEG motor-protection rows (R31-R40) — the author tried to AI-fill metadata at build time and the formulas never resolved.
- One **probable tag-collision** to verify: tag `PC54071` appears on both R15 (AK-OB 110) and R17 (AK-PC 782B).

NOT GOSPEL — first pass only.
