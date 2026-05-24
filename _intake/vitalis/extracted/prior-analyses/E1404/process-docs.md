# E1404 — Process Docs

## Verdict

**N/A — no process docs in this job beyond the customer-facing proposal.**

The director's special charter for E1404 anticipated this could be the case ("Fab packets are mostly incomplete shells — E1404 may have none"). Confirmed.

## What was searched

The full job folder was walked. Documents found that could conceivably be classified as process docs:

| Candidate | Verdict | Notes |
|---|---|---|
| `E1404 - Northgate 49 MB0221 Panel Proposal 050126.docx` | **Customer proposal, not a process doc.** | 27 short paragraphs + 1 table with a single line item. Standard T&Cs boilerplate (payment, quotations, shipments, warranty, limitation of liability, functional liability, order cancellation). No internal process narrative. |
| `Proposals/...Panel Proposal...pdf` | Same content as the docx, PDF export. | Not a process doc. |
| `Drawings/` folder | **Empty.** | No fab drawings, no wiring diagrams, no panel layouts. |
| Internal change-log / wire-change history | **Absent.** | The closest thing is a one-row entry on the BOM sheet itself (R3): Initials "MB", Date "2026-05-01", Notes "Original genuine draft". That is the entire change history of the job — a single row indicating the current draft. |
| QC program / checklist | **Absent.** | |
| Fab packet / assembly instructions | **Absent.** | |
| IO list (descriptive) | Present as a shell only. | `IO - Control Panel` tab in main workbook lists DI/DO channel numbers 1–96+ but every Description, Signal Type, and Voltage cell is blank. Not a process doc — a placeholder. |
| Panel Notes sheet email request | Adjacent to a process doc. | R6 of Panel Notes contains the customer's email RFQ verbatim ("As discussed, I'm looking for a quote on this Northgate 49 (MB0221). This will be a standard Classic build with a system manager, 65kA SCCR, door mounted lights and switches, CO2 sensor, plus the spare I/O board. Please ensure that the switches and lights for LT are above the MT on the door. Please ensure that the lights and switches are laid out on the door as RUN LIGHT - FAULT LIGHT - SWITCH from left to right."). This is a captured customer-intent snippet — informal, useful as a record of the "as ordered" intent, not a process narrative. |

## Why this is consistent with job state

E1404 is **arrested at the proposal stage** (see `lifecycle.md`). Fab packets, QC checklists, wire change logs, and assembly drawings would typically be authored AFTER a PO is received and the panel goes into the build cycle. None of that has happened for E1404 yet.

## What I'd expect to find if the job advanced

For comparison with other jobs in the corpus, the process docs that would normally accumulate from this point forward:
- Fab packet (panel layout, assembly drawings, nameplate schedule, wire schedule).
- Wire-change / engineering-change log capturing field deviations.
- QC inspection checklist + sign-off.
- UL nameplate documentation (panel SCCR / type rating sticker spec).
- Shipping / final acceptance docs.

None present for E1404. Noting absence, not flagging it as a defect.
