# E1404 Supplemental XLSXs

This is the priority-1 subtask for E1404. Two supplementals were inspected: **Vitalis Control Parts Inventory.xlsx** (suspected master) and **Motor_Protection_Selections_NG49-53-54.xlsx** (multi-job suspected).

---

## 1. Vitalis Control Parts Inventory.xlsx — VERDICT: **NOT** a master parts list

The director's hypothesis was that this is the reusable "Plan of all Plans" — a master inventory feeding every job. **The evidence refutes that.** This file is a small, working **stockroom / purchasing log**, not a parts master.

### Schema

Two sheets, both tiny:

| Sheet | Real rows (non-empty) | Columns |
|---|---|---|
| PARTS IN STOCK | 11 part rows | Part #, Manufacturer, Qty, (blank) |
| MISSING PARTS | ~24 part rows (with 2 sub-sections) | Part #, Manufacturer, Qty, Status, Invoice Number, Job Number |

### Scope (what's actually in it)

- **PARTS IN STOCK** is a shelf-count of refrigeration controls only:
  - 3 Danfoss AK-XM/AK-CM I/O modules
  - 8 Copeland CoreSense / discharge-line sensor parts (800-, 638-, 818-, 810-, 501- series)
  - **Total: 11 SKUs.** This is two manufacturers and one product family (refrigeration rack controls). A true master would contain hundreds of SKUs across breakers, contactors, enclosures, TBs, relays, fuses, lugs, conduit, wire — nothing like that is present.

- **MISSING PARTS** is a per-job purchasing tracker. It is **organized by job**, with informal subsection headers (a stray "YCH" label at R25 followed by a second header row). Job numbers found in the file: **E-1395** and **E-1399** — and notably **NOT E-1404**. The file is shared/sitting in E1404's folder but the job it tracks is two jobs back.

### Signs of reuse vs. per-job copy

- The Job Number column proves intent of reuse — the schema imagines tracking across all jobs in one place.
- But the implementation looks abandoned-in-place: only two jobs ever populated, the most recent referenced job (E-1399) is the one before E1404, columns are inconsistently filled (Status, Invoice Number blank for many ABB rows), and there are no formulas or pivots tying it to anything.
- Most likely interpretation: **a person's personal "what did I order, what's still owed" workbook, copied into job folders for convenience.** It is NOT the source of truth for any panel BOM.

### Confidence

**High confidence** this file is not a master parts list. Size (11 + 24 rows), narrow manufacturer scope, and stale job references all point to a per-purchaser log rather than a corpus-wide master.

### Flag: confusion risk

The filename ("Vitalis Control **Parts Inventory**") is misleading. Without reading it, a person would absolutely assume it's a parts master. Recommend the corpus-wide naming convention treat this as `purchasing-log` rather than `parts-inventory` going forward — but flagged, not repaired.

---

## 2. Motor_Protection_Selections_NG49-53-54.xlsx — multi-job engineering selection doc

### Schema

Three sheets, well-formed:

| Sheet | Real rows | Purpose |
|---|---|---|
| Selections Summary | ~35 (R5–R22 data + R25–R35 notes) | Per-panel × per-motor MMP / contactor / aux selection table |
| Main Breaker | ~34 (R5–R7 data + decode + notes) | Main CB selection with full ABB catalog # decode |
| Bill of Materials | ~22 | Consolidated BOM with per-panel quantities and totals |

### Multi-job logic — why "NG49-53-54" in the filename

The file is **explicitly built to serve three jobs at once**: Northgate 49 (MB0221, this job), Northgate 53 (MB0222), and Northgate 54 (MB0223). The "Panel" column carries the job tag for every row, and the BOM sheet has separate `Qty NG49 | Qty NG53 | Qty NG54 | Total Qty` columns.

Why these three jobs:
- All three use the same electrical system: **460 VAC, 3Ø, 60 Hz, 65 kAIC SCCR**
- All three use the **same Main Breaker** (XT5HU330ABFF000XXX, 300 A) — that's the source of "single CB covers all three" logic in note 1 on the Main Breaker sheet.
- All three have **identical MT motor selections** (51.1 A FLA → MS165-54 + AF52-30-00-13). They differ only in LT motor sizing (NG49 = 9.84 A / MS132-10; NG53 & NG54 = 12.5 A / MS132-16).

This is **batch engineering** — a refrigeration designer doing three near-identical Northgate stores at once and avoiding triplicate paperwork.

### Engineering content quality

Genuinely high quality and well-documented:
- ABB Type 1 Coordination cited against UL File E345003.
- Catalog-number decode (XT5HU330ABFF000XXX broken down character-by-character).
- Selection-basis notes (10 numbered notes on Summary, 8 on Main Breaker) explain WHY each part was chosen — coil voltage suffix logic, VFD-vs-across-the-line aux block treatment, lug ampacity check vs NEC 75°C, frame-size step-up rationale (XT4 maxes at 250 A so XT5 is forced), alternative-trip-unit option (Ekip Touch LSI).
- BOM has a small but real data-quality wart: HKF1-11 appears 3 times with **trailing-space variants** ("HKF1-11", "HKF1-11 ", "HKF1-11  ") to keep them as distinct rows per branch. The note in R22 admits this and tells the reader to consolidate (12 + 2 + 4 = 18 total). Flag: this is exactly the kind of artisanal Excel hack that breaks downstream tooling. Same trick used for "CA4-10" and rows R19/R20 have description columns blank — that's an incomplete row.

### Signs of reuse

Strong evidence this **was** built as a per-multi-job artifact and likely templated from a prior NG-cluster:
- Notes reference "MMP_Contactor_Type_1_Coordination spreadsheet" as a separate authoritative reference — implying a **deeper, organization-level master** exists somewhere outside this folder (look for it).
- Citation of ABB UL File E345003 in panel header.
- "Verify with ABB at order time" caveats and "swap to XT5HU330ATFF000XXX if Ekip desired" suggest this is a working selection driven from a known catalog rule-set.

This is a reusable engineering pattern — the recipe — but it lives at the cluster-of-jobs level (NG49/53/54), not corpus-wide.

---

## Bottom-line answers to the special charter

| Question | Answer |
|---|---|
| Is Vitalis Parts Inventory a true master? | **No.** It is a stockroom/purchasing log scoped to one purchaser, 35 rows total, only 2 manufacturers in PARTS IN STOCK, only references jobs E-1395 and E-1399 (not E-1404). |
| Does a Plan of all Plans live in E1404 supplementals? | **Not here.** The Motor Protection doc is a 3-job batch engineering selection, not corpus-wide. It does *cite* an external `MMP_Contactor_Type_1_Coordination` spreadsheet as its source-of-truth coordination table — **that** is more likely to be the master, if it can be found in another job folder or shared drive. |
| What's the Motor Protection logic? | Three near-identical Northgate stores share a 460V/65kAIC panel platform; differences are limited to LT-motor amperage band. The file is one workbook serving three jobs because the engineering is genuinely the same. |
