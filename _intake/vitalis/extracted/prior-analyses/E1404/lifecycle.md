# E1404 — Artifact Lifecycle Map

Job: **E1404 — Northgate 49, panel tag MB0221**. Client Classic Refrigeration, contact Jacob Vanzella. Date 2026-04-30, Rev 1.13. Brand Danfoss / System Manager interface.

## Folder tree (job root)

```
E1404 - Northgate 49 MB0221/
├── Drawings/                                         [EMPTY]
├── Proposals/
│   └── E1404 - Northgate 49 MB0221 Panel Proposal 050126.pdf
├── RFQ/
│   ├── DWG AUTOMATION.xlsx                           (blank RFQ template)
│   └── NG49 - MB0221 - EXXXX RFQ XXXXXX.xlsx         (filled-in RFQ)
├── E1404 - Northgate 49 MB0221.xlsx                  (main job workbook)
├── E1404 - Northgate 49 MB0221 Panel Proposal 050126.docx
├── Motor_Protection_Selections_NG49-53-54.xlsx       (supplemental, multi-job)
└── Vitalis Control Parts Inventory.xlsx              (supplemental, stockroom log)
```

## Lifecycle by stage

### Stage 1 — RFQ (intake)

| File | What it is | State |
|---|---|---|
| `DWG AUTOMATION.xlsx` | **Blank template** of the RFQ workbook (9 sheets: Project Info, Panel Options, Input Power List, Logos, FLA/MCA/MOCP Reference Material, NEC 240.6A, Wire Ampacity). Filename "DWG AUTOMATION" hints this is the template used to drive downstream drawings. | Present — but it's a template, not job content |
| `NG49 - MB0221 - EXXXX RFQ XXXXXX.xlsx` | **Filled-in RFQ** for this job. Project Info sheet populated: incoming power 3Ø+PE 460 VAC 60 Hz, SCCR 65 kAIC, TYPE 3R, 72"H × 48"W × 18"D sheet steel enclosure, four MT motors (51.1 A FLA), two LT motors (9.84 A FLA), 3 kVA + 500 VA transformers. FLA 231.58, MCA 244.36, MOCP 295.46, Disconnect 80% = 300 A. | Present |

Filename quirk: the RFQ file is still named **"EXXXX RFQ XXXXXX"** — placeholder estimate number and unfilled trailing slot — even though the job is now E1404. The placeholder filename was never renamed when the estimate # was assigned. Mild data-quality flag, common pattern.

### Stage 2 — Engineering / Main job workbook

| File | What it is | State |
|---|---|---|
| `E1404 - Northgate 49 MB0221.xlsx` | **Main panel design workbook**. Six sheets: Panel Notes, BOM - SCP-01 (1099 rows, the full BOM), Clean BOM (60 rows, the consolidated/published BOM), IO - Control Panel (1002 rows), Load Calc (997 rows), Categories. | Present, full |
| `Motor_Protection_Selections_NG49-53-54.xlsx` | Engineering selection doc for MMP / contactor / Main CB — explicitly multi-job (NG49 + NG53 + NG54). Three sheets, well-annotated with selection-basis notes and ABB catalog-number decode. | Present, rich |
| `Vitalis Control Parts Inventory.xlsx` | **Misnamed**. Not a parts master — it's a stockroom + missing-parts purchasing log scoped to jobs E-1395 and E-1399 (not E-1404). | Present but mis-shelved |

### Stage 3 — Proposal

| File | What it is | State |
|---|---|---|
| `E1404 - Northgate 49 MB0221 Panel Proposal 050126.docx` | One-page customer proposal dated May 1 2026. Single line item: "Qty 1 — RCP-01 — Roxsta G6 Rack Control — $39,921.81". 4–6 week lead time. Standard Terms & Conditions boilerplate. | Present, thin (one line item) |
| `Proposals/E1404 - Northgate 49 MB0221 Panel Proposal 050126.pdf` | Same proposal exported to PDF. | Present |

### Stage 4 — Drawings (build output)

`Drawings/` folder exists but is **EMPTY** — no schematics, panel layouts, wiring diagrams, or BOM exports. This is consistent with a job still in proposal / pre-fab state.

## What's MISSING vs richer packets

Compared to a "full" packet I'd expect for a delivered panel, E1404 is missing:

- **No Fab Packet** — no assembly drawings, no nameplate / label schedule, no wire schedule, no QC checklists.
- **No drawings at all** — `Drawings/` is an empty placeholder.
- **No changelog / wire-change history.**
- **No PO / order docs** — only the proposal is present.
- **Proposal is one-line** — no scope breakdown, no included/excluded list, no options pricing.
- **No internal engineering review record** beyond the Motor Protection selection doc.

## Status inference

E1404 looks like a job **arrested at the proposal stage**: RFQ in, engineering workbook built, motor protection selected, customer proposal sent — but no PO yet, so no drawings, no fab packet. The job folder is essentially the pre-build state.

## Lifecycle map summary

```
RFQ template (DWG AUTOMATION)  ─┐
                                 ├──► Filled RFQ (NG49 RFQ) ──► Main Workbook (E1404.xlsx)
                                 │                                   │
                                 │            Motor Protection ◄─────┤  (clustered with NG53/54)
                                 │            Vitalis Inventory ?    │  (mis-shelved purchasing log)
                                 │                                   │
                                 └──────────────────────► Proposal (docx + pdf)  ◄── stops here
                                                              │
                                                              ▼
                                                     Drawings/  [empty]
                                                     Fab packet [absent]
```
