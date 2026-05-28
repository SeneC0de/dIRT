# Panel template v3 — handoff

Decisions and open work from the 2026-05-28 session (Randall + Jones).

## Context

Walking the new-project / new-panel workflow end-to-end. Starting point: the v2 template invariants are noise — fake part numbers (`ABB-XT-FRAME`, `MCB-2A-DIN`), redundant `evidence` arrays, and DOC-only entries mixed in with part-producing invariants. Fix the template first, then talk about how dCAD/dPART/dERP resolves it.

## What landed

### Bug fix: panel template picker showed `(v0)` instead of real schema version
**File:** [`VitalisCAD-Web/api/dWEB.Api/DerpClient.cs:1843`](C:\Users\randa\source\repos\VitalisCAD-Web\api\dWEB.Api\DerpClient.cs)

`PanelTemplateDto` and nested records (`PanelInvariantDto`, `PanelBomLineDto`, `PanelEvidenceDto`, `PanelSlotDto`) had no `[JsonPropertyName]` attributes. `DerpClient.JsonOptions` uses `JsonNamingPolicy.CamelCase`, but dERP returns snake_case. Result: every snake_case field (`schema_version`, `template_id`, `customer_id`, `source_jobs`, `invariant_id`, `bom_lines`, `quantity_is_estimate`, `slot_id`, `allowed_values`, `default_value`) silently deserialized as default — `int → 0`, `string → null`, `List → null`.

Fix: added explicit `[JsonPropertyName]` pins to every field, matching the pattern `PanelConfigurationDto` already used correctly. Needs dWEB rebuild + redeploy.

### v3 template structure
**File:** [`dIRT/_intake/vitalis/extracted/panel-template-v3.yaml`](C:\Users\randa\source\repos\dIRT\_intake\vitalis\extracted\panel-template-v3.yaml)

Renamed `template_id: roxsta-v1`, `template_name: "Vitalis Roxsta Control Panel"`.

Top-level sections:
- `panel_defaults` — SCCR, control bus voltages. Injected into criteria by the resolver.
- `invariants` — part-producing, each with `selection_lines: [{role, category, quantity_formula, criteria}]`. Optional `condition` for slot-gated invariants (UPS, ethernet switch).
- `panel_documentation` — workflow/schema descriptors that don't produce parts (workbook_skeleton, bom_bar_convention, tag_convention, bom_column_schema, load_calc_sheet, legend_plates_sheet, proposal_lead_time).

Removed from invariants:
- `evidence` arrays
- Placeholder `bom_lines`
- DOC entries (moved to `panel_documentation`)
- `sccr_65kaic` (promoted to `panel_defaults.sccr_kaic`)

### MCB quantity formulas (corpus-validated)
The v2 entry `branch_circuit_breakers_120v` is a UL1077 MCB, NOT a UL489 branch breaker.

- **2A control branch MCB:** `quantity_formula = {compressor_count} * 2 + 3`. Fits corpus within ±3 (E1392 +3, E1395 −1, E1399 −2, E1404 +1). `quantity_is_estimate: false`.
- **6A compressor-coil branch MCB:** `quantity_formula = {compressor_count}`. Fits within ±1 across all four jobs.

### KAIC scope
`kaic_rating` only appears on UL489 selection lines (`main_disconnect`, and future MMP invariants). UL1077 MCBs do not carry it.

## Open questions (deferred)

1. **Formula grammar — "your call, do it right."**
   Three forms used in the v3 draft:
   - Arithmetic: `"{compressor_count} * 2 + 3"`
   - Ternary: `"{mocp_amps} > 600 ? 6 : 3"`, `"{rfq_panel_options.ups} == true"`
   - Slot dot-access: `"{enclosure_size.family}"`, `"{door_pilot_family.pilot_voltage}"`
   
   Dot-access implies slot values are **structured records**, not bare enums. Worth confirming the slot schema change before nailing down a single grammar.

2. **`family_preference` field** — ignored for now.

3. **Missing dERP part categories.** v3 uses categories that aren't in `IPartCriteria`'s polymorphic discriminator: `Enclosure`, `Subpanel`, `PowerDistributionBlock`, `GroundLug`, `GroundBar`, `PowerSupply`, `UPS`, `Battery`, `NetworkSwitch`, `Receptacle`, `Thermostat`, `Fan`, `Filter`, `SelectorSwitch`, `LegendPlate`, `DinRail`, `Accessory`. Existing taxonomy is from ADR-0008 (PartCriteria narrowing) and ADR-0017 (per-category typed criteria).
   
   **Next:** find/read the ADR that defined the category taxonomy, see which v3 categories already exist vs need to be added, and confirm whether new categories follow the `IPartCriteria` polymorphic pattern or fall back to flat `PartCriteria`.

4. **Back-references between selection lines** — explicit.
   When `main_disconnect.lug_kit.criteria.parent_frame = "{main_breaker.frame}"`, the resolver must know `main_breaker` resolves first. v3 currently uses implicit name reference; should add `depends_on: [<role-or-line-id>]` to the schema.

## Architecture chain (recap, so handoff knows where things live)

```
dIRT/_intake/vitalis/extracted/panel-template-v3.yaml   (authoring source)
        │
        ▼  (generate-panel-template-json.py — needs v3 update)
dCAD/data/panel-template.json                           (loaded by PanelTemplateStore)
        │
        ▼  (inlined as constant in an EF migration)
dERP project.panel_templates.invariants (jsonb)         (schema_version bumped)
        │
        ▼  (dERP REST: GET /api/panel-templates)
dWEB.Api/DerpClient → PanelTemplatesEndpoints           (proxy)
        │
        ▼  (React)
VitalisCAD-Web VitaliPanelModal.tsx                     (picker UI)
```

## Next steps

In order:

1. **Research the category-taxonomy ADR** (likely ADR-0008 + ADR-0017 in dERP). Reconcile v3 category names against `IPartCriteria` discriminator list. Decide whether to extend `PartCriteria` and `IPartCriteria` with the missing types, or use a generic catalog-lookup fallback.
2. **Pick a formula grammar** and commit. Update v3 file if grammar choice changes any expressions.
3. **Add explicit `depends_on` schema** for cross-line back-references; update `main_disconnect` and `control_transformer_24vac` accessory entries.
4. **Walk dCAD resolution path.** Once the template structure is final, design how dCAD reads v3, evaluates formulas, substitutes slot values, builds `POST /api/parts/select` payloads, and assembles the resolved BOM. `BomExpander.cs` is the likely home but needs significant rework — current implementation uses 12 axis rule tables, not template-driven selection.
5. **Update the YAML → JSON tool** ([`dCAD/tools/generate-panel-template-json.py`](C:\Users\randa\source\repos\dCAD\tools\generate-panel-template-json.py)) for v3 shape.
6. **Write the v3 EF migration** (`M0072d_SchemaV3SelectionLines` or similar) that bumps `schema_version` to 3 and rewrites the invariants jsonb.
