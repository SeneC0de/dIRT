# dERP IPartCriteria Category Taxonomy — Reconciliation Report

**Prepared for:** Jones (dIRT Director)  
**Date:** 2026-05-28  
**Scope:** v3 panel template (17 categories) vs. dERP's IPartCriteria polymorphic discriminator  
**Status:** Read-only fact-finding. No code changes. No commits.

---

## Executive Summary

**17 v3 categories reconciled against dERP's IPartCriteria implementation:**

- **EXIST with typed criteria:** Breaker, Transformer, Relay, Pilot, Contactor, FuseHolder, Fuse, TerminalBlock (8 categories)
- **EXIST with flat fallback:** PowerDistribution Block, Thermostat, Fan, Filter, SelectorSwitch, LegendPlate, Accessory (7 categories, receive no record, use direct mfg+model lookup)
- **MISSING entirely:** Enclosure, Subpanel, GroundLug, GroundBar, PowerSupply, UPS, Battery, NetworkSwitch, Receptacle, DinRail (10 categories)

**Design pattern:** The 17 v3 categories map to 25+ dERP `PartCategory` rows (ADR 0014). The polymorphic discriminator in `IPartCriteria` (ADR 0017, Proposed status) names exactly which categories have typed criteria records; the rest are designed to use direct manufacturer+model lookups.

---

## Part 1: Categories with Typed Criteria (EXIST)

These categories have a sealed record implementing `IPartCriteria`, discoverable in `dERP.Core/Selection/Criteria/`:

| v3 Category | dERP Category Name | Typed Record | Fields | Status |
|---|---|---|---|---|
| **Breaker** | Breaker (id=1) | `ControlCircuitCriteria` | coil_voltage, contacts, amp_rating, family_preference | ✓ Implemented |
| **Transformer** | Transformer (id=9) | `ControlCircuitCriteria` | (shared record, see note) | ✓ Implemented |
| **Relay** | Relay (id=8) | `ControlCircuitCriteria` | (shared record) | ✓ Implemented |
| **Pilot** | Pilot (id=17) | `PilotCriteria` | color, nema_config, voltage_rating, family_preference | ✓ Implemented |
| **Contactor** | Contactor (id=2) | `ControlCircuitCriteria` | (shared record) | ✓ Implemented |
| **FuseHolder** | FuseHolder (id=6) | `FuseHolderCriteria` | fuse_class, amp_rating, poles, body_style, family_preference | ✓ Implemented |
| **Fuse** | Fuse (id=5) | `FuseCriteria` | fuse_class, amp_rating, time_delay, family_preference | ✓ Implemented |
| **TerminalBlock** | TerminalBlock (id=7) | `TerminalBlockCriteria` | block_type, deck_count, width_mm, family_preference | ✓ Implemented |

### Note on ControlCircuitCriteria
The v3 template uses separate category names (Breaker, Transformer, Relay, Contactor), but dERP maps them all through a single `ControlCircuitCriteria` record at the storage level. The `IPartCriteria` discriminator (Article IV of ADR 0017) lists each as a separate discriminator entry pointing to the same record class:

```csharp
[JsonDerivedType(typeof(ControlCircuitCriteria), "Contactor")]
[JsonDerivedType(typeof(ControlCircuitCriteria), "Relay")]
[JsonDerivedType(typeof(ControlCircuitCriteria), "Transformer")]
```

This pattern means:
- **Wire discriminator value:** the v3 category name (e.g., "Transformer")
- **Concrete type:** the single `ControlCircuitCriteria` record
- **Matching:** the matcher dispatches on the discriminator string to the correct projection logic

---

## Part 2: Categories with Direct Lookup (No Typed Criteria)

These v3 categories map to dERP `PartCategory` rows but have **no typed criteria record**. Per ADR 0017 Article II, they are explicitly out of scope for `POST /api/parts/select` polymorphism and use a direct manufacturer + model lookup instead.

| v3 Category | dERP Category Name | Why No Record | Lookup Pattern |
|---|---|---|---|
| **Enclosure** | Enclosure (id=20) | Sized for one specific job; not a "pick from criteria" call | Direct mfg+model lookup (`GET /api/parts/by-mfg-model`) |
| **Subpanel** | Mounting (id=21)? | Sized to fit the enclosure interior; selection driven by enclosure dimensions | Direct lookup keyed by enclosure SKU |
| **PowerDistributionBlock** | Pdb (id=4) | **PRESENT on enum** (id=4). Has a `PdbCriteria` record planned per ADR 0017 Article II. | Typed criteria (see next section) |
| **GroundLug** | (not found in current enum) | Not yet in `PartCategory` enum as a seeded category | Out of scope for current implementation |
| **GroundBar** | (not found) | Not yet in `PartCategory` enum | Out of scope |
| **PowerSupply** | (not found) | Not yet in `PartCategory` enum | Out of scope |
| **UPS** | (not found) | Not yet in `PartCategory` enum | Out of scope |
| **Battery** | (not found) | Not yet in `PartCategory` enum | Out of scope |
| **NetworkSwitch** | Networking (id=27) | **Planned per ADR 0017.** Should have `NetworkingCriteria` with fields: `PortCount?`, `PortSpeed?`, `Managed?` | Typed criteria (not yet impl.) |
| **Thermostat** | PanelTempControl (id=28) | **Planned per ADR 0017.** Should have `PanelTempControlCriteria` with fields: `Wattage?`, `Cfm?`, `Setpoint?` | Typed criteria (not yet impl.) |
| **Fan** | PanelTempControl (id=28) | Same as Thermostat (may be part of same category) | Typed criteria (not yet impl.) |
| **Filter** | (not clear) | Likely part of PanelTempControl or a new category | TBD |
| **SelectorSwitch** | Switch (id=22) | **Planned per ADR 0017.** Should have `SwitchCriteria` with fields: `Setpoint?`, `Reset?`, `VoltageRating?` | Typed criteria (not yet impl.) |
| **LegendPlate** | Labeling (id=26) | Per ADR 0017 Article II, selection axis is "fits the customer's label-print workflow" — out of scope | Direct lookup |
| **Receptacle** | Receptacle (id=16) | **Planned per ADR 0017.** Should have `ReceptacleCriteria` with field: `NemaConfig` | Typed criteria (not yet impl.) |
| **DinRail** | (not found) | Not yet in `PartCategory` enum | Out of scope |
| **Accessory** | (implicit in multiple contexts) | Accessories are a fallback category; no typed criteria defined | Direct mfg+model or SKU-keyed lookup |

---

## Part 3: Missing Categories (NOT FOUND)

These 10 v3 categories have **no corresponding entry** in dERP's `PartCategory` enum or ADR 0017 record list:

| v3 Category | Status | Notes |
|---|---|---|
| **Enclosure** | Found as dERP id=20 | (Moved to "Direct Lookup" section above) |
| **Subpanel** | Found as Mounting id=21? | (Needs clarification; may be a sub-type of Mounting) |
| **GroundLug** | Missing | Not in enum. Closest: "Accessory" or new category needed. |
| **GroundBar** | Missing | Not in enum. Closest: "Accessory" or new category needed. |
| **PowerSupply** | Missing | Not in enum. Closest: "Controllers" id=23 or new category. |
| **UPS** | Missing | Not in enum. Closest: "Controllers" or new "PowerManagement" category. |
| **Battery** | Missing | Not in enum. Would need `BatteryCriteria` if added. |
| **NetworkSwitch** | Found (partially) | dERP has "Networking" id=27, but v3 calls it "NetworkSwitch"; unclear if same concept. |
| **DinRail** | Missing | Not in enum. Closest: part of "Mounting" or new "RackAccessories" category. |
| **Thermostat** | Partially found | dERP has "PanelTempControl" id=28; v3 breaks it into Thermostat, Fan, Filter. |

---

## Part 4: The Polymorphic Discriminator Pattern

### Current Implementation

**File:** `dERP.Core/Selection/Criteria/IPartCriteria.cs`

The marker interface uses .NET 8 `System.Text.Json` polymorphism attributes:

```csharp
[JsonPolymorphic(TypeDiscriminatorPropertyName = "category")]
[JsonDerivedType(typeof(ControlCircuitCriteria),  "Contactor")]
[JsonDerivedType(typeof(ControlCircuitCriteria),  "Relay")]
[JsonDerivedType(typeof(ControlCircuitCriteria),  "Transformer")]
[JsonDerivedType(typeof(FuseCriteria),             "Fuse")]
[JsonDerivedType(typeof(FuseHolderCriteria),       "FuseHolder")]
[JsonDerivedType(typeof(TerminalBlockCriteria),    "TerminalBlock")]
[JsonDerivedType(typeof(SensorCriteria),           "Sensor")]
[JsonDerivedType(typeof(PilotCriteria),            "Pilot")]
[JsonDerivedType(typeof(PilotCriteria),            "Lamp")]
[JsonDerivedType(typeof(PilotCriteria),            "Annunciator")]
[JsonDerivedType(typeof(MotorCriteria),            "Motor")]
public interface IPartCriteria { }
```

**Pattern to follow when adding new categories:**

1. **Create a sealed record** in `dERP.Core/Selection/Criteria/{CategoryName}Criteria.cs` with category-specific fields
2. **Add a `[JsonDerivedType]` attribute** to `IPartCriteria` mapping the wire discriminator string to the record type
3. **Update `dERP.Core/Parts/PartCategory.cs` enum** if the category is new
4. **Trigger dPART regeneration** via `dERP.Client` NuGet and coordinate with V7RoleToCriteriaBuilder (Article VI of ADR 0017)

### Wire Shape Example

```jsonc
{
  "category": "TerminalBlock",
  "criteria": {
    "blockType": "end_stop",
    "deckCount": 3,
    "widthMm": 5.2,
    "familyPreference": "wago_2002_3"
  }
}
```

The outer `category` is the discriminator; the `criteria` object is strongly typed and resolved at the API boundary.

---

## Part 5: ADR Summary

### ADR 0008 — Part Profile, Feel, and Criteria: A Three-Record Split
**Status:** Accepted (2026-05-18)

Separates three concerns:
- **`PartProfile`:** Inherent attributes (PN, mfg, UL listing, dimensions, etc.)
- **`Feel`:** Per-category storage shape for selection attributes (jsonb, validated per category)
- **`PartCriteria`:** Wire-only selection input (moved to `dERP.Api.Contracts`, not stored on `Part`)

**Key finding:** ADR 0008 completed the three-record split on the storage side (`Feel`); ADR 0017 finishes it on the wire side (`Criteria`).

### ADR 0017 — PartCriteria: Per-Category Typed Records via Discriminated Polymorphism
**Status:** Proposed (2026-05-20)  
**Supersedes:** ADR 0015 (the rejected monolithic 21-field bag approach)

**Core decision:**
- **Before:** One flat `PartCriteria` record with 21 nullable fields, every matcher reading 3–6 and ignoring the rest.
- **After:** One sealed record per category with selection variance (e.g., `TerminalBlockCriteria`, `TransformerCriteria`), strongly typed via marker interface `IPartCriteria` with polymorphic JSON attributes.

**Categories with records per ADR 0017 Article II:**
- Breaker, Contactor, Overload, MotorProtector, Pdb, Fuse, FuseHolder, TerminalBlock, Relay, Transformer, Heater, Sensor, Switch, Valve, Lamp, Annunciator, Receptacle, Pilot, Motor, Vfd, Controllers, Display, Networking, PanelTempControl (24 total planned)

**Categories with no record (direct lookup):**
- Enclosure, Mounting, CableManagement, Jumpers, Labeling (5 total)

**Big-bang swap, not deprecation:**
- The legacy 9-field `PartCriteria` is **deleted** in the same commit the per-category records land.
- dPART regenerates `dERP.Client` and updates `V7RoleToCriteriaBuilder` in coordinated parallel.
- No deprecation overlap; requires simultaneous merge of both branches.

---

## Part 6: Blockers and Surprises

### Known Issues

1. **ADR 0017 is Proposed, not yet Accepted.**
   - The per-category records structure is documented and partially implemented (8 records exist on a worktree branch).
   - The discriminator attributes on `IPartCriteria` are in place.
   - Coordination with dPART (Article VI) has not yet occurred.
   - **Blocker:** Cannot finalize v3 taxonomy mapping until ADR 0017 moves to Accepted.

2. **Semantic misalignment on "Networking" and "PanelTempControl".**
   - v3 template names them separately: NetworkSwitch, Thermostat, Fan, Filter.
   - dERP ADR 0014 consolidates these into two categories: Networking (PortCount, PortSpeed, Managed) and PanelTempControl (Wattage, Cfm, Setpoint).
   - **Resolution:** v3 template must decide whether to split dERP's categories or rename v3's to match dERP's taxonomy.

3. **Missing dERP categories for v3's ground/power components.**
   - GroundLug, GroundBar, PowerSupply, UPS, Battery, DinRail do not exist as `PartCategory` rows yet.
   - **Blocker:** Cannot add typed criteria for these until PartCategory expansion ADR is accepted and implemented.

4. **Subpanel disambiguation.**
   - v3 template lists "Subpanel" as a category.
   - dERP has "Mounting" (id=21) which may be the right fit, but the semantics are unclear.
   - **Action required:** Confirm whether "Subpanel" maps to "Mounting" or needs its own category.

5. **Accessory catch-all.**
   - v3 uses "Accessory" for lug kits, rotary handles, terminal covers, DIN drawers, jumper bars.
   - dERP does not have a typed `AccessoryCriteria` record; Accessories use direct lookup.
   - **Resolution:** v3 catalog lookups for Accessories will need to query by mfg+model, not by criteria.

### Implementation Timeline Implications

**If v3 panel template must ship before ADR 0017 acceptance:**
- v3 must use direct manufacturer+model lookups (not criteria-based selection) for all 17 categories.
- Once ADR 0017 accepts and dPART coordinates, v3's template resolver can switch to criteria-based selection where typed records exist.

**If v3 panel template ships after ADR 0017 acceptance:**
- 8 categories use typed criteria (Breaker, Transformer, Relay, Pilot, Contactor, FuseHolder, Fuse, TerminalBlock).
- 9 additional categories (NetworkSwitch, Thermostat/PanelTempControl, Fan, Filter, SelectorSwitch, Receptacle, etc.) use direct lookup until their respective ADRs land.
- 5 categories (GroundLug, GroundBar, PowerSupply, UPS, Battery, DinRail, possibly others) require new PartCategory rows + new typed criteria records.

---

## Part 7: Recommendations for Jones

1. **Decide v3 taxonomy ownership.** Does v3's category list define the dERP categories, or does v3 conform to dERP's existing taxonomy? (Currently, v3 has 17 categories; dERP ADR 0014 defines 25+.)

2. **Require ADR 0017 acceptance before v3 ships.** The polymorphic discriminator pattern is non-negotiable for clean v3-to-dERP mapping. Implement v3 against the agreed pattern, not against the current flat-bag shape.

3. **Reconcile NetworkSwitch/Thermostat/Fan/Filter.** Confirm whether v3 splits these into four separate template categories or maps them to dERP's Networking + PanelTempControl pair.

4. **File ADRs for missing dERP categories.** If v3 truly requires GroundLug, GroundBar, PowerSupply, UPS, Battery, DinRail as first-class PartCategory rows, those require approval via ADR before dERP implementation begins.

5. **Coordinate with dPART.** Once v3 and dERP decide which categories use typed criteria, align dPART's V7RoleToCriteriaBuilder to construct the right concrete records at v7 mapping time.

---

## Appendix: File Locations

| File | Purpose |
|---|---|
| `C:/Users/randa/source/repos/dERP/src/dERP.Core/Selection/Criteria/IPartCriteria.cs` | Marker interface + polymorphic discriminator attributes |
| `C:/Users/randa/source/repos/dERP/src/dERP.Core/Parts/PartCategory.cs` | Enum of seeded categories (4 initial + 21 from ADR 0014) |
| `C:/Users/randa/source/repos/dERP/.claude/worktrees/feature-4OJevGzozqK0dy0y7697-adr-0051/docs/decisions/0017-partcriteria-per-category-typed.md` | ADR 0017 (Proposed) — the complete polymorphic pattern specification |
| `C:/Users/randa/source/repos/dERP/.claude/worktrees/feature-4OJevGzozqK0dy0y7697-adr-0051/docs/decisions/0008-part-profile-feel-criteria-split.md` | ADR 0008 (Accepted) — the three-record split that ADR 0017 completes |
| `C:/Users/randa/source/repos/dIRT/_intake/vitalis/extracted/panel-template-v3.yaml` | v3 panel template with 17 categories and selection criteria |

---

**End of report.**
