# E1395 — Process Document Deep Read

Four docs deep-read here. The reminder from caveat #4 stands: **fab packets are mostly incomplete shells**. E1395 *is* one of the more filled-out packets in this corpus, but it is still a checklist scaffolding, not a procedure. Gaps are called out explicitly per doc.

---

## 1. `E1395 Fabrication Packet.docx`

**Structure (table of contents):**
1. Pre-Fab Checklist
2. Pre-Wiring Checklist
3. Wago Rail Exports
4. Fab Checklist
5. Testing and I/O Checks
6. Packaging Checklist
7. Notes

**Implicit shop flow distilled from the bullets:**

*Pre-Fab (parts arrive, drawings in hand):*
- Print BOM and pick parts
- Prep customer TB rail
- Print the fabrication drawing set
- Confirm door cutouts, back panel layout, side panel layout, rail detail views, PLC location, bus rails

*Pre-Wiring (label preparation):*
- Prep wire labels, TB labels, device labels, UL508A labeling

*Fab — backplane phase:*
- Fab backplane
- Install devices, wire tray, device labels
- Power wiring: PDB → devices, torque per MFG spec, clean tight crisp bends, sticky-backs where applicable, heat-shrink power-wire labels after run
- Wire per schematics, dC wire-color spec, transformers wired, neutrals wired, fuses installed, SF CB bridge, ground lug installed
- Quality gates: labeling + heat shrink, no "cat whiskers", all terminations pass tug test

*Fab — door phase:*
- Install bulkheads, run conductors through heat shrink tube, install ferrules on wire ends, install exhaust fan + filter
- Install HOAs, lights, HMI in door
- **Explicit warning:** "Verify the hole pattern in the drawings for the HMI with the actual device BEFORE cutting hole in door." → encoded prior burn.
- Install back plane, breaker disconnect, engraved labels (bulkheads, HOAs, E-Stop, lights)
- Wire door (HMI, pilot lights)

*Testing and I/O Checks:*
- Apply UL508A labeling
- Apply UL508A sticker
- Apply dC logo

*Packaging:*
- Add desiccant
- Add drawings
- Package
- Photograph panel interior and exterior

*Notes:*
- "UPS and Battery not in BOM because we are sizing them per customer requests."

**Gaps (this is a shell):**
- The "Wago Rail Exports" heading exists but has **no content beneath it.** Should hold the Wago-rail .smartdesigner export or screenshots. Empty.
- "Testing and I/O Checks" has 3 bullets total — apply label, sticker, logo. **No actual test procedure.** A real test plan would have channel-by-channel verification (consistent with the QC SOP saying every IO point must be documented before shipping).
- No torque values. ("Per MFG spec" — acceptable, but compare against having a torque table in line.)
- No reference to the drawing set's revision letter — fab against rev L vs rev K matters.
- No PO number, no panel tag, no job-specific dimensions. The doc is **boilerplate** with no E1395-specific cells filled in beyond the title.
- Photograph step refers to interior + exterior, but the QC SOP says **7 photos** (inside panel, inside door, outside door, left, right, top, back). Fab packet underspecifies.

---

## 2. `E1395 dC Quality Control Program.docx`

**Structure:**
1. Defined Terms (empty)
2. Introduction/Overview (1 paragraph; ends mid-sentence — "...with a" then heading break)
3. Calibration (one sentence — IMTE annually calibrated, certs kept 1 year minimum)
4. Testing and I/O Checks (3 bullets — references **SOP-QC-0001** and **F-QC-0001**, but those docs are not present in the job folder)
5. System Setup & Configuration (placeholder paragraphs: "Setup is done by access level…", "Configuration stuff for service/admin…")
6. **Generating As-Built BOM** — the most substantive section
7. System/Equipment Operation (placeholder)
8. Warnings & Shutdowns (placeholder)
9. Appendix ("Control flow diagrams!!" — literally with two exclamation marks; clearly a TODO marker)

**The As-Built BOM section is the only operationalized one. The procedure:**

1. Take 7 photos: inside of panel, inside of door, outside of door, left side, right side, top, back. Save in `As Built/Photos`.
2. Print the inside-of-panel and inside-of-door photos.
3. Justify the drawing BOM against every component. Check: items on back panel, wire tray, rail, terminal, marking, jumpers, end plates, mounting hardware, ship-loose parts, ferrules, grounding hardware, weave/installation hardware, wire labeling, device labeling, door-mounted items, aux contacts, comms/memory cards.
4. **Blue check** = item present per BOM (mark printed BOM, cross item out in photo).
5. **Red** = changes — cross out removed items, edit quantities, note added/changed part numbers.
6. Use the redlined printed copy to generate a digital As-Built BOM saved to `As Built/` folder of the job.

**Gaps:**
- Most sections are placeholder text never replaced. The doc was clearly meant to be customized per job but wasn't.
- Cross-references to SOP-QC-0001 and F-QC-0001 (the I/O Validation Report form) — these governing docs are **not in the job folder**. They may exist organization-wide but the link is broken from a fresh reader's perspective.
- No `As Built/` folder yet exists in the job dir → either the As-Built step was never executed, or the artifacts live elsewhere.
- "Generating As-Built BOM" uses a Clean BOM-like worksheet implicitly (digital As-Built BOM) but doesn't name `Clean BOM` sheet in the XLSX. The shop is doing a paper-then-digital workflow; the digital target file format isn't specified.

---

## 3. `Danfoss Wire Changes.docx`

**Format:** 23 single-line entries, each: `<wire #> from Module X (terminal) to Module Y (terminal)`.

**Decoded:**

| From (module/term) | To (module/term) | Wire # |
|---|---|---|
| Module 3 (17) | Module 1 (AO1 −) | 49091 |
| Module 3 (18) | Module 1 (AO1 +) | 49101 |
| Module 3 (19) | Module 1 (AO2 −) | 48141 |
| Module 3 (20) | Module 1 (AO2 +) | 48151 |
| (special) | (special) | "Swap Module 3 (103A) to (101A)" |
| Module 6 (9..16) | Module 3 (17..24) | 64013..6401A (8 wires) |
| Module 4 (21..24) | Module 6 (9..12) | 62141..62144 (4 wires) |
| Module 7 (1..4) | Module 4 (17..20) | 66041..66044 (4 wires) |
| Module 2 (19) | Module 2 (17) | 2091 |
| Module 2 (20) | Module 2 (18) | 2101 |

**Inferred process:**

- This is an **engineering re-balance redline applied after the initial drawing pass.** A Danfoss AK-XM 103A is being swapped to an AK-XM 101A (cf. Danfoss Inventory sheet in the XLSX: 103A = 4 AI + 4 AO, 101A = 8 AI). That swap forces all the AO signals previously on module 3 to move to module 1; in turn, module 6 takes ownership of the AI signals that used to be on 3; module 4 hands signals to 6; module 7 hands signals to 4. It is a cascading IO move.
- The drawing revision table comments include "MOVED DANFOSS WIRING TO MATCH IO LIST" — this doc is the line-item record of that move.
- **Why this doc is rich:** it's the cleanest example in the corpus of an engineering decision (swap an AO-capable module for an AI-only module) propagating through wire-number assignments. If anything in this corpus is "the seam where automation slots in," this is.
- "Swap Module 3 (103A) to (101A)" is a **board-swap instruction** mixed inline with wire-move instructions. The doc is not split between *what to physically swap* vs *what to re-label*. Risk: an installer reads top-down and either swaps the module first (correct) or starts moving wires before swapping (wrong).

**Gaps:**
- No date stamps. No engineer initials inside the doc body. No reason given for the swap (presumably IO-count rebalancing, but unstated).
- No drawing-sheet cross-reference per wire. An installer holding this doc has to mentally cross-reference to the schematic to know which drawing sheet a wire lives on.
- "Module 1, 2, 3, 4, 6, 7" — module 5 isn't mentioned. Either intentionally untouched or omitted. Not flagged in the doc.
- "Module 1 (AO1 −)" vs "Module 3 (17)" — two different terminal-naming conventions in the same doc (functional vs numeric). The reader has to mentally map them.

---

## 4. `E1395 - dC Job Tag for Traveler.docx`

**Two title pages (one each for PARTS and FABRICATION).**

Content of both pages, verbatim:
```
PARTS                                  FABRICATION
E1395 - Lazy Acres                     E1395 - Lazy Acres
Roxsta G6                              Roxsta G6
PARTS                                  FABRICATION
PO# P-XXXXX                            PO# P-XXXXX
```

**Implicit purpose:** physical traveler tags that get printed and stapled to the parts bin and the fab cart so the floor knows which job a tote belongs to.

**Gaps:**
- `PO# P-XXXXX` is the **placeholder** — actual PO is P-38262 (per the PO folder). The traveler was never substituted. Either it's printed and hand-written on the floor, or this template is stale.
- "Roxsta G6" — a product line / model name that doesn't appear elsewhere in the job XLSX. Worth asking what Roxsta G6 is (likely the underlying Vitalis cooling-system platform that Lazy Acres is built on); contextually it fits with the Danfoss-controlled CO2 refrigeration rack the BOM/Load Calc describes.
- No revision number on the doc — if drawings rev L was used to build, the traveler doesn't say so.

---

## 5. `Changelog.xlsx` (rich-doc treatment)

See `supplemental.md` for the schema. Summary here: **the filename is misleading**. It's not a per-job change log — it's a *parameter-driver inventory* per drawing sheet (SH2..SH5 = drawing sheets 2-5). It documents which dimensions of the design vary between jobs, sheet-by-sheet, so the engineer can systematically review the master drawing set when adapting it to a new customer. It is the most explicit evidence in this corpus of a partial design-parameterization effort that never became fully templated.

---

## Cross-cutting observations

1. **Three quality gates exist but no closure**: Fab Packet checklist (filled by floor), QC As-Built BOM (filled by QC reviewer), I/O Validation Report F-QC-0001 (referenced but absent). For E1395 the second is implied unfinished (no `As Built/` folder) and the third doc isn't even in the job dir.
2. **The Fab Packet and QC Program both reference photographs but specify different counts** (FP: "panel interior and exterior" = 2; QC: 7 specific shots). Drift between sister SOPs.
3. **The Job Tag traveler has the PO# placeholder** un-substituted. Floor either fills it in by hand or ignores. Cheap automation seam: substitute PO# at print time.
4. **Danfoss Wire Changes is the most technically informative doc in the packet.** It encodes a real engineering decision (module swap + IO rebalance) at the level of individual wire numbers. If anywhere in the corpus we want to study "engineering change propagation," this is the artifact to study.
5. **Wire-label naming convention** (e.g. `49091`, `64013`, `6401A`, `2091`, `66042`) — five-character alphanumeric with what looks like a sheet-prefix encoding. The leading digits (`4909`, `6401`, `6214`, etc.) likely encode page or module location; the trailing 1 looks like a wire suffix. Would be confirmed by cross-reading the drawings.
