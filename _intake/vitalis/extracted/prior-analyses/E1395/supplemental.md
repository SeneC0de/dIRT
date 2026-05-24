# E1395 — Supplemental XLSXs

Beyond the main `E1395 - Lazy Acres - MB0219.xlsx`, the job folder contains two supplemental XLSX files:

1. `Changelog.xlsx` (top of job folder)
2. `PO/PO# P-38262 - Order Acknowledgement.xlsx` (inside the PO subfolder)

## 1. `Changelog.xlsx`

**Schema:** 4 sheets, named after drawing sheet numbers — `SH2`, `SH3`, `SH4`, `SH5`. Each is a 2-column table:

| Col A | Col B |
|---|---|
| `Change N` | parameter description |

**Counts per sheet:**

| Sheet | Drawing sheets covered (inferred) | # parameters |
|---|---|---:|
| SH2 | 3-Phase pages | 35 |
| SH3 | 3-Phase continuation | 22 |
| SH4 | LT compressor pages | 34 |
| SH5 | Transformer / 120V dist | 34 |

**Total = 125 parameter entries across 4 sheets.**

**Sample (SH2):** Disconnect Amperage / Disconnect Part Number / Disconnect SCCR / Disconnect % Rating / PDB SCCR / PDB Manufacturer / PDB Part Number / PDB Style (One Block/3Units) / MT1C1 SCCR / MT1C1 Breaker Rating / MT1C1 FLA / MT1C1 Wire Sizing / MT1C1 VFD or not / MT1C1 Contactor Part Number / MT1C1 Contactor Manufacturer / MT1C1 Breaker Manufacturer / MT1C1 Breaker Part Number / MT1C1 Wire or Connector to Contactor / MT1C1 Connector Manufacturer - if True / MT1C1 Connector Part Number - if True / Grid Monitor Wire Size (Based on PDB) / Grid Monitor Manufacturer / Grid Monitor Part Number / Grid Monitor Voltage / [MT1C2 parameters repeat the pattern...]

**Purpose (inferred):**

Despite its filename, this is **not a per-job revision history**. It is a **parameter-driver catalog** — a list of *what varies between jobs* for each drawing sheet. There is no date column, no author, no before/after values. The columns are just an index of variable names.

Best interpretation: this file is the **manual outline of a not-yet-built template system**. When the engineer adapts the master drawing set to a new customer, this catalog tells them which knobs to inspect on each drawing sheet. The fact that "Connector Manufacturer - if True" appears as an entry suggests the catalog is conditional — some parameters apply only when an earlier toggle is set.

**Repetition pattern observed:** rows follow a near-identical 11-parameter block per compressor circuit:
- `<Ckt> SCCR`
- `<Ckt> Breaker Rating`
- `<Ckt> FLA`
- `<Ckt> Wire Sizing`
- `<Ckt> VFD or not`            *(only on the VFD-capable circuit, MT1C1/LT1C1)*
- `<Ckt> Contactor Part Number`
- `<Ckt> Contactor Manufacturer`
- `<Ckt> Breaker Manufacturer`
- `<Ckt> Breaker Part Number`
- `<Ckt> Wire or Connector to Contactor`
- `<Ckt> Connector Manufacturer - if True`
- `<Ckt> Connector Part Number - if True`

The same block repeats for MT1C1, MT1C2, MT1C3, MT1C4, LT1C1, LT1C2, LT1C3 — 7 compressors × ~11 parameters = 77 of the 125 entries. The remainder are: 4 disconnect params, 4 PDB params, 4 Grid Monitor params, and a 36-row transformer/fuse block on SH5 (T1 + T2 each have fuse holder, fuse, transformer body, and CB sub-blocks of ~8-9 params).

**No data values are filled in anywhere in this file.** It is a pure metadata file — just labels, no readings.

**Cross-job behavior (hypothesis):** because there are no values here, this file is **almost certainly identical across all 4 jobs in this corpus**. If true: it's not a job artifact at all — it's an org-wide template, mistakenly nested inside each job folder. Worth verifying against the other 3 jobs.

---

## 2. `PO/PO# P-38262 - Order Acknowledgement.xlsx`

Format: the dC-side order acknowledgement, mirror of the PO PDF. Not analyzed deeply — it's a transactional doc, not a design or process doc, and lives in the PO folder where lifecycle.md already locates it.

---

## Other XLSX in the job folder

`Clean BOM` sheet is **inside** the main XLSX, not a separate file. `Danfoss Inventory` likewise. `Categories` and `IO - Control Panel` and `Load Calc` and `Panel Notes` all live inside the main workbook.

No other standalone XLSX files exist beyond `Changelog.xlsx` and the PO acknowledgement.
