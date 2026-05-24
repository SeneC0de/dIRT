# VitalisCAD — Project Continuation Roadmap

## What this is

VitalisCAD is an AutoCAD Electrical (ACADE) 2025 .NET plugin that
generates refrigeration panel drawings for Danfoss + Copeland controller
platforms. It's loaded via NETLOAD and registers `[CommandMethod]`
entry points (notably `VITALISCAD` for the form UI and `VITALISGEN`
for circuit generation).

Live work happens on `refactor/layered-architecture`. The master branch
is behind; do not merge until this roadmap is closer to done and a
Windows-side build + NETLOAD verification has signed off the full state.

## Layered architecture (do not violate)

```
Configuration  ──┐
Common         ──┼─ pure C#, no ACE
Rules          ──┤
PartMaster     ──┘
AceInterop       ─── ALL AutoCAD API calls live here
Renderers.*      ─── drawing orchestration
AcePlugin        ─── NETLOAD entry + WinForms + [CommandMethod]
```

Pure projects build and test in sandbox (Linux/macOS). AceInterop +
Renderers + AcePlugin require Windows + AutoCAD 2025 + ACADE; verify
on the Windows dev box before push.

## Where we are (Phase F complete)

**Schema v4** — mappings live at `<project>/mappings/<Section>.json`.
v1/v2/v3 files are rejected by `MappingStore.Load` with a "re-save
the form" message.

**Components** (ComponentRef vocabulary):
- `CB`, `Contactor`, `Vfd`, `Motor`, `TerminalBlock`, `Coil`, `Cable`, `PdbTb`
- Logical (Role, Instance) identity; physical tags derived at render time
- TerminalNumber distinguishes positions within a strip / phase within a PDB

**Connections** — reference components by (Role, Instance, Pin). Carry
optional `CableInstance` pointing at the owning Cable component.

**Rules** (in `VitalisCAD.Rules`):
- `Layout.RungAllocator` — places sections on sheets via a 1-19 rung grid
  (rungs 1-4 = title-block header). VFD footprint=10, non-VFD=5.
- `Tagging.TagRule` — `{family}{sheet}{rung:D2}{instance}` produces
  `CB2071` / `M13081` / etc.
- `Cabling.CableTagRule` — `CBL{sheet:D2}{seq:D2}`
- `BreakerSizing.BreakerSizeRule`, `WireSizing.WireSizeRule`, `WireSizing.LayerNameRule`

**Rendered today on a 3-phase distribution sheet** (per section):
- 3× PdbTb on the bus rails (X=4.3082/5.3082/6.3082, calibrated from
  title block measurement)
- PdbTb→CB wires with semicircular jump arcs (single Polyline per wire
  to keep AEWIRENO from auto-numbering each segment); "1L1/1L2/1L3"
  rendered as DBText (wd_putwnxyf doesn't attach to polylines)
- CB (3-pole stack) + Contactor (3-pole stack with shared coil tag)
- VFD with 6-terminal signal strip
- Motor with 3 phase stubs
- Cables as first-class components (3 per VFD section, 1 per non-VFD)
- Color labels on the 6-conductor signal cable (ORG/YEL/RED/BRN/WHT/BLK)
- Cable break markers + CBL#### cable-tag labels centered on each cable

**Multi-sheet rendering** — `VITALISGEN` allocates all sections,
sideloads each distribution sheet via `SideloadedDatabaseHelper`
(swaps `HostApplicationServices.WorkingDatabase`), renders each
section there. Active sheet uses the live Document's Database.

**Deferred** (carry forward; do not rebuild from scratch):
- PDB summary table on the last 3-ph sheet
- Coil insertion (placeholder +1/+3 sheet offset; awaiting real rules)
- Cable color codes for the three 3-phase power cables (only the
  6-conductor signal cable has colors today)

**Sandbox tests**: 298 pure-project tests pass (Configuration 146 +
Common 38 + Rules 114). AceInterop / Renderers / AcePlugin are
not sandbox-testable.

## Roadmap to completion

Order is suggested but not strict — call out priority shifts as you
go. Phases follow the same "single commit per phase with internal
[X.Y] Editor.WriteMessage checkpoints" cadence the project has used.

### Phase G — Block catalog + component categories

- Inventory every ACADE library block used in the shop's reference
  DWGs (HCB*, HMS*, HMO*, HT*, HCNTL*, HRELAY*, HFUSE*, HXFMR*,
  HPLC*, plus any non-H-prefixed blocks).
- Map each block name to a component category. Categories at minimum:
  `PDB`, `Terminal`, `CB`, `Fuse`, `Relay`, `Contactor`, `MotorStarter`,
  `Motor`, `VFD`, `Transformer`, `PLC`, `IOModule`, `Indicator`, `Switch`.
- CSV-driven catalog under `data/block-catalog.csv` consumed by a new
  `VitalisCAD.Configuration.BlockCatalog` class.
- Categories drive: rendering (which insertion helper to call), BOM
  (line-item grouping), wire-list (signal-type inference), schematic
  creation (which sections support which component categories).
- Acceptance: every block in the reference DWG set has a catalog entry;
  ComponentRef.Role extended (or aliased) to align with categories.

### Phase H — PLC and IO channel tracking

- New `PLC` component with N IO channels; each channel has signal
  type (DI/DO/AI/AO), polarity, terminal address.
- IO channel allocation rule: when a device needs to wire to a PLC,
  allocate the next free channel of the right signal type.
- Each device connected to a PLC IO channel tracks (deviceTag, channelId,
  signalType) — surfaces in IO list reports.
- Connections from devices to PLC become first-class entries in the
  mapping; not lumped into "general control wiring."
- This is also the natural unblock for **off-page wire handling** —
  most PLC-bound wires cross sheets.

### Phase I — Off-page wire handling

- Cross-sheet wire connectors (the "go to sheet X line Y" markers
  ACADE provides via `WD_xxxX` blocks).
- Partial precedent: Coil↔Contactor already crosses pages via the
  shared-tag xref mechanism — IsInternal=false in ConnectionRef.
- New connector blocks need to be inserted on each side, with their
  cross-reference attributes (`SHEET`, `WIRENO`) populated so
  `c:wd_xref_doit` can resolve them.
- Priority because PLC wiring (Phase H), coil cross-references, and
  control wiring all need this.

### Phase J — Sections-with-specific-circuitry

- You have a separate doc listing the panel's logical sections (e.g.
  3-phase distribution, control, safety chain, alarm, PLC, etc.).
- Each section type has a known circuit pattern (which components,
  which connections, which wiring conventions).
- Refactor `DefaultMappingBuilder` from "one-size compressor section
  builder" into a dispatch table keyed by section type. Each section
  type has its own builder function.
- `SystemMapping.Section` becomes a *section type* identifier; the
  current per-compressor section identity moves into a separate
  `CompressorTag` or similar field on the mapping.
- Likely the biggest schema change still ahead — bump to v5.

### Phase K — External web UI

- Move the VITALISCAD WinForms config UI out of ACADE entirely.
- Web app (React/whatever — separate repo) generates the mapping JSON
  files. ACADE plugin only reads JSON and renders.
- The current `MappingEditorDialog` (per-section JSON textbox) becomes
  legacy / removed; the in-ACADE UI shrinks to "Import mappings,
  show project status, run VITALISGEN."
- Benefits: decouples UI iteration from ACADE rebuild cycle, opens up
  multi-user / cloud collaboration, version-controllable schema.
- The mapping schema stays the contract between the web UI and ACADE
  — keep it stable and document it for the web team.

### Phase L — Production outputs

- Wire tracking owned by us (not ACADE's wire list). Walk every
  ConnectionRef in every section, emit:
  - **Wire list** — from/to, gauge, length (computed from WCS coords
    plus path overhead), wire-number label, layer.
  - **Cable list** — CBL#### + conductor count + endpoint components
    + run length.
  - **BOM** — parts grouped by category, quantities, catalog numbers.
    Driven by Phase G's block catalog.
  - **QC checklist** — per-panel must-pass items derived from the
    mapping (e.g. "every motor has FLA recorded", "every breaker
    rating ≥ derived breaker amps", "every cable has a tag").
  - **Labeling output** — printable labels for terminals, cables,
    devices (CSV / Brady-compatible formats).
- Job document package — bundle the above per panel build.
- This work pulls in `VitalisCAD.Renderers.Bom` (currently has the
  legacy `DryCADBOMTemplate` to be rewritten).

### Cross-cutting

- **Schema migrations** — bumping the version currently forces full
  regenerate. For production-ready use, implement migrations between
  versions so existing project files don't lose data.
- **Test coverage** — pure-project tests are solid. Renderer/inserter
  tests are missing because they need AutoCAD. Investigate a fake-DB
  test harness (mocked Database/Transaction) for at least the pin
  resolution + wire-routing logic.
- **CompressorSectionData phase-out** — partially obsolete (sheet
  hints decoupled in v2). The `SavePerCompressorAttributes` and
  `WireLayerCommand` paths still use it; refactor when section types
  land (Phase J).
- **Track wires ourselves** — current model relies on ACADE's wire
  list for some downstream consumers. Phase L explicitly moves wire
  ownership into us; coordinate with Phase G's block catalog so wire
  endpoints are typed properly.

## How to continue (operational)

- Pick up on `refactor/layered-architecture`. Read the latest commits
  end-to-end before adding code — recent commits document
  non-obvious decisions (eWrongDatabase fix, wd_putwnxyf polyline
  failure, rail X calibration, etc.).
- Cadence: one commit per phase (or sub-phase), `[X.Y]`
  `Editor.WriteMessage` checkpoints inside the rendering code so the
  user can see what code path fired on each VITALISGEN run.
- Sandbox build pure projects + run their tests before every commit.
  Full-solution build + NETLOAD verification happens on the Windows
  dev box; commit messages must explicitly note "Sandbox: N tests
  pass; full-solution build deferred to Windows."
- Iterate visuals via VITALISMEASURE — the user can dump a block's
  InsertionPoint + Extents to calibrate constants. Constants live in
  `CompressorCircuitLayout`; do not hardcode WCS values elsewhere.
- Tag styling convention: device tags (TAG1, TAG2, TAGSTRIP) render
  in AutoCAD ColorIndex 5 (blue) via `AceBlockInserter.SetAttributeColor`
  after each insert. Description / rating text stays default color.
