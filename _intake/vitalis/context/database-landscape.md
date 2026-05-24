# dERP Database Landscape

**Current state as of 2026-05-23.** Permanent reference for PostgreSQL 16 schema, EF Core 8 entity mapping, migration history, and data-shape governance.

## Overview

dERP is a .NET 8 / EF Core 8 / PostgreSQL 16 service with intentional data silos. Schema governance is anchored in ADR-0016 (data domain architecture) and flows through task-specific ADRs (ADR-0013, 0014, 0015, 0017, 0020, 0024, 0026, 0033, etc.). The three-layer rule is enforced: Core records ≠ EF entities ≠ API contracts. All migrations are checked into source at `src/dERP.Data/Migrations/`; none have been edited post-application.

**Stack:**
- PostgreSQL 16 (Npgsql provider)
- EF Core 8 DbContext (dERPDbContext)
- .NET 8 minimal API (dERP.Api)
- Soft-delete support: bom_lines.deleted_at only (ADR-0013, 0020)
- Jsonb sidecar patterns: feel, criteria_snapshot, config_payload, image_urls, bill_to_address, ship_to_address, site_address, external_id_map.qbo_ids
- Append-only tables: pricing.price_history, catalog.part_lifecycle_events, project.bom_lines (supersession chain)

---

## Schemas at a Glance

| Schema | Purpose | Silos / Phases | Table Count |
|--------|---------|---|---|
| **catalog** | Canonical parts, categories, substitutes, lifecycle, enrichment | Phase 1–2 (ADR-0002) + Phase 0 enrichment (ADR-0034) | 9 |
| **procurement** | Vendors, purchase orders, receipts, line-item mapping to parts | Phase 2 (vendors) + Phase 0 (PO/receipt/QBO) (ADR-0016 II.3, 0026) | 8 |
| **pricing** | Price observation history append-only log | Phase 3 (ADR-0005, 0016 II.5) | 1 |
| **project** | Projects, panels, BOM (bill of material), soft-delete lift | Phase 4–5 metadata (ADR-0002, 0020, 0024) | 3 |
| **sales** | Quotes, invoices, submittals, payments, idempotency log | ADR-0028 (QBO write-through) | 8 |
| **identity** | Unified party model, contacts, addresses by role | ADR-0016 II.1 (Wave 2 / Phase 0) | 3 |
| **fab** | Stock locations, build tasks, stock movements | ADR-0016 II.7 (Wave 4) + ADR-0026 §1 | 3 |
| **audit** | Single append-only domain-event log across all silos | ADR-0016 IV.1 | 1 |
| **integration** | QBO ID mapping (eight-silo integration decoupler) | ADR-0030 | 1 |
| **public** | Manufacturer, UOM conversion, UL reference tables (legacy namespace) | Phase 2–3 | 4 |

---

## Canonical Foreign-Key Bridges

Four intra-silo or cross-silo FK bridges to `catalog.parts.id` (all ON DELETE RESTRICT per brief):

| From Table | From Schema | To Table | To Schema | Defined In | ADR |
|---|---|---|---|---|---|
| `po_lines.part_id` | procurement | `parts.id` | catalog | dERPDbContext line 1356–1363 | ADR-0016 §III.B.2 |
| `vendor_parts.part_id` | procurement | `parts.id` | catalog | dERPDbContext line 1181–1203 | ADR-0016 §III.B.1 |
| `quote_lines.part_id` | sales | `parts.id` | catalog | dERPDbContext line 541–569 | ADR-0016 §III.B.2 |
| `bom_lines.part_id` | project | `parts.id` | catalog | dERPDbContext line 1123–1162 | ADR-0016 §III.B.3 (ADR-0020 §1) |

**Bridge semantics:** Cross-silo FKs only on these four points. All other inter-silo refs are string-ID columns with no constraint (e.g., `projects.billed_to_party_id` → identity.parties, but NOT a Postgres FK).

---

## Catalog Schema (Phases 1–2, 0)

**Purpose:** Canonical parts, categories, substitutes, lifecycle, enrichment sidecars.  
**ADRs:** 0002 (phased rollout), 0013 (soft-delete stub), 0014 (PartCategory expansion), 0034 (enrichment sidecar).

### Tables

| Table | PK | Key Columns | Purpose | Governing ADR | Migration |
|---|---|---|---|---|---|
| `parts` | `id` (uuid) | `part_number` (unique), `category_id` FK, `manufacturer_id`, `feel` (jsonb), `lifecycle_status`, `ul_file_number`, `ul_listing_category`, `ul_standard`, `rohs_compliant`, `reach_compliant` | Core parts catalog with flat lifecycle status + profile columns (dimensions, weight, URLs). Soft-delete: none (ADR-0013 deferral). Feel carries category-typed criteria (ADR-0017). | ADR-0002, 0008, 0014, 0017 | 20260513145303_InitialCreate |
| `part_categories` | `id` (int, ValueGeneratedNever) | `name` (unique), `feel_schema` (jsonb), `is_active` | Category typology (Breaker, Contactor, Motor Protector, …); feel_schema defines jsonb structure for typed criteria matching. Added as seeded rows in Phase 2. | ADR-0002, 0014, 0017 | 20260519031849_Category_LookupTable |
| `part_substitutes` | `(part_id, substitute_part_id)` | `substitute_part_id` (FK, RESTRICT) | Commutative substitution graph: "part X can be swapped with substitute X". Both IDs FK back to parts.id. | ADR-0002, 0007 | 20260513145303_InitialCreate |
| `part_inventory` | `(part_id, location_id)` | `on_hand`, `reserved`, `reorder_point`, `last_movement_at` | Rollup: stock levels at each location. PK moved to composite (part_id, location_id) per ADR-0026 §1.4. Intra-silo FK to parts (CASCADE), cross-silo FK to fab.stock_locations (RESTRICT). | ADR-0002, 0026 | 20260513175115_Phase3and4_VendorPartsAndInventory |
| `part_lifecycle_events` | `id` (uuid) | `part_id` (FK, CASCADE), `old_status`, `new_status`, `transitioned_at`, `transitioned_by` | Append-only audit trail: one row per lifecycle state change. OldStatus nullable (first transition). Indexed (part_id, transitioned_at DESC). | ADR-0002 | 20260519102059_Part_LifecycleHistory |
| `part_enrichments` | `part_id` (uuid) | `image_urls` (jsonb), `last_fetched_at`, `fetch_status` (Pending, Stale, Complete) | 1:1 sidecar to parts for machine-authored enrichment metadata (images). Cascade-delete on owner. Indexed by fetch_status + last_fetched_at for worker drain. | ADR-0034 | 20260520192740_Part_EnrichmentSidecar |
| `ul_listing_category_reference` | `code` (string, max 8) | `description` | Enumeration table: UL listing categories (e.g., CULUS, CSA). | ADR-0004 | 20260513145303_InitialCreate |
| `ul_standard_reference` | `code` (string, max 40) | `description` | Enumeration table: UL standards (e.g., UL508, UL60950-1). | ADR-0004 | 20260513145303_InitialCreate |
| `manufacturers` | `id` (uuid) | `name` (unique), `code` (unique, nullable, partial index), `notes`, `is_active` | Manufacturer/OEM master data. Referenced by parts.manufacturer_id (nullable, SetNull on delete). | ADR-0002 | 20260513164227_Phase2_ManufacturersVendorsLifecycle |

**Key Constraints:**
- `parts.part_number`: UNIQUE
- `part_categories.name`: UNIQUE, partial index where is_active = true
- `manufacturers.name`: UNIQUE
- `manufacturers.code`: UNIQUE (partial on code IS NOT NULL)
- `part_categories.feel_schema`: optional; null until category taxonomy is populated (ADR-0017)
- `parts.feel`: optional; null until criteria data is ingested

**Indexes:**
- `ix_parts_part_number` (unique)
- `ix_parts_category_id`
- `ix_parts_manufacturer_id`
- `ix_parts_lifecycle_status`
- `ix_parts_ul_file_number`, `ix_parts_ul_listing_category`
- `ix_part_lifecycle_events_part_transitioned_at_desc` (part_id, transitioned_at DESC)
- `ix_part_enrichments_fetch_status`, `ix_part_enrichments_last_fetched_at`

**Soft-Delete Status:**
- No soft-delete on catalog.parts (ADR-0013 acknowledges the gap; deferral until phase 5 or later).
- Soft-delete is implemented ONLY on project.bom_lines.deleted_at (ADR-0020 §3).

---

## Procurement Schema (Phase 2 + Phase 0)

**Purpose:** Vendors, vendor parts, purchase orders, receipts, and QBO integration.  
**ADRs:** ADR-0016 §II.3 (Wave 4), ADR-0033 (vendor data cleanup), ADR-0026 (receive pipeline).

### Tables

| Table | PK | Key Columns | Purpose | Governing ADR | Migration |
|---|---|---|---|---|---|
| `vendors` | `id` (uuid) | `display_name`, `party_id` (string, NO FK), `terms`, `created_by` | Procurement-owned vendor master (replaces legacy public.vendors per ADR-0033). party_id is a string-ID into identity.parties (not a Postgres FK, per ADR-0016 §III.B). | ADR-0016 II.3, 0033 | 20260520230012_Procurement_Silo |
| `vendor_parts` | `id` (uuid) | `vendor_id` (FK, CASCADE), `part_id` (FK, RESTRICT), `vendor_sku`, `unit_cost_cents`, `currency`, `last_seen_at` | Vendor offering: which vendors sell which parts at what cost. Composite UNIQUE (vendor_id, vendor_sku). Two FK-bridges: intra-silo to vendors (CASCADE), cross-silo to catalog.parts (RESTRICT). | ADR-0016 II.3, 0033 | 20260513175115_Phase3and4_VendorPartsAndInventory |
| `purchase_orders` | `id` (uuid) | `po_number` (unique), `issuer_party_id`, `ship_to_address_party_id`, `end_customer_party_id`, `bill_to_party_id`, `status` (draft, sent, received, cancelled), `project_id`, `total_cents` | Purchase order header. All party_ids are strings (NO FKs to identity.parties). project_id is a string-ID to project.projects (NO FK). Status enum with CHECK constraint. | ADR-0016 II.3, V.6 | 20260520230012_Procurement_Silo |
| `po_lines` | `id` (uuid) | `po_id` (FK, CASCADE), `line_no`, `part_id` (FK, RESTRICT), `qty`, `unit_price_cents`, `tax_cents`, `freight_cents` | PO line item. Composite UNIQUE (po_id, line_no). FK-bridge 2/4 to catalog.parts.id. | ADR-0016 II.3, III.B.2 | 20260520230012_Procurement_Silo |
| `po_revisions` | `id` (uuid) | `po_id` (FK, CASCADE), `revision_no`, `revision_date`, `reason` | Revision history: tracks PO amendments. Append-only. | ADR-0023 (implicit) | 20260520230012_Procurement_Silo |
| `receipts` | `id` (uuid) | `external_ref` (unique), `vendor_id`, `purchase_order_id` (FK, SET NULL), `location_id`, `received_at`, `received_by` | Goods receipt header. external_ref is an idempotency nonce (ADR-0026 §6). Optional FK to po (SET NULL so archiving a PO doesn't cascade-delete receipts). | ADR-0026 | 20260521150000_Receive_Pipeline |
| `receipt_lines` | `id` (uuid) | `receipt_id` (FK, CASCADE), `line_no`, `part_id` (FK, RESTRICT, nullable), `vendor_part_number`, `qty`, `location_id`, `po_line_id` (FK, SET NULL), `status` (posted, unresolved) | Receipt line item. Composite UNIQUE (receipt_id, line_no). FK-bridge to catalog.parts (RESTRICT, nullable — null = unresolved). | ADR-0026 | 20260521150000_Receive_Pipeline |
| `po_receipts` | `id` (uuid) | `po_id` (FK, RESTRICT), `receipt_id` (FK, RESTRICT) | Thin PO-scoped receipt (feature-vkJFuUHjGsPsTYYRwv8l). Maps PO header to receipt header. | vkJFuUHjGsPsTYYRwv8l-impl | 20260522100000_PoReceipt |

**Key Constraints:**
- `purchase_orders.po_number`: UNIQUE
- `vendor_parts`: UNIQUE (vendor_id, vendor_sku)
- `receipts.external_ref`: UNIQUE
- `receipt_lines`: UNIQUE (receipt_id, line_no)
- `po_lines`: UNIQUE (po_id, line_no)

**Indexes:**
- `ix_vendor_parts_part` (part_id)
- `ix_receipts_external_ref` (external_ref, unique)
- `ix_receipts_vendor` (vendor_id, received_at DESC)
- `ix_receipts_po` (purchase_order_id, partial: WHERE po_id IS NOT NULL)
- `ix_receipt_lines_receipt` (receipt_id, line_no, unique)
- `ix_receipt_lines_unresolved` (status, partial: WHERE status = 'unresolved')

**String-ID Pattern:**
- `vendors.party_id` → identity.parties (NO Postgres FK)
- `purchase_orders.issuer_party_id`, `ship_to_address_party_id`, `end_customer_party_id`, `bill_to_party_id` → identity.parties (NO Postgres FK)
- `purchase_orders.project_id` → project.projects (NO Postgres FK)

**Legacy Vendor Data (ADR-0033):**
- Old `public.vendors` and `public.vendor_parts` tables were dropped by migration 20260522225907_PathD_VendorDataCleanup.
- Data migrated: INSERT…SELECT from public.* → procurement.* with unit_cost_cents conversion.
- `pricing.price_history.vendor_part_id` FK was dropped (orphan table gone).

---

## Pricing Schema (Phase 3)

**Purpose:** Append-only price observation history.  
**ADRs:** ADR-0005 (feel/enrichment), ADR-0016 §II.5 (silo isolation).

### Tables

| Table | PK | Key Columns | Purpose | Governing ADR | Migration |
|---|---|---|---|---|---|
| `price_history` | `id` (uuid) | `vendor_part_id`, `unit_price` (numeric 14,4), `observed_date`, `source_po_extract_id` (nullable, FK reserved for PoLineExtract), `created_utc` | Append-only price observation ledger. No app-side update or delete (defense-in-depth BEFORE UPDATE/DELETE triggers on Postgres). Indexed (vendor_part_id, observed_date DESC) for "newest-first" current-price lookup. | ADR-0005, 0016 II.5 | 20260519031815_Pricing_History |

**Constraints:**
- No UPDATE or DELETE (Postgres triggers enforce; EF Core routes through insert-only code paths).
- Composite index: (vendor_part_id, observed_date DESC).

**Indexes:**
- `ix_price_history_vendor_part_observed_date_desc` (vendor_part_id, observed_date DESC)

**Notes:**
- Pricing silo is separate from catalog (ADR-0016 §II.5) because price has different access pattern (time-windowed range), update cadence, and consumer set (quote builder, PO issuance).
- `source_po_extract_id` FK deferred until PoLineExtract table exists (feature pFx3rqcvDOK7pByRznrE scope).

---

## Project Schema (Phase 4–5 metadata)

**Purpose:** Projects (estimation containers), panels (product sub-assemblies), BOM (bill of material with soft-delete supersession).  
**ADRs:** ADR-0016 §II.2 (Wave 2), ADR-0020 (BOM relational lift), ADR-0024 (FK slot expansion).

### Tables

| Table | PK | Key Columns | Purpose | Governing ADR | Migration |
|---|---|---|---|---|---|
| `projects` | `id` (uuid) | `project_code` (unique), `billed_to_party_id`, `end_customer_party_id`, `contractor_party_id`, `title`, `status` (quote, active, complete, cancelled), `owner_email`, `site_address` (jsonb), `estimate_number`, `customer_po_number`, `estimate_drive_url`, `customer_po_drive_url`, `received_at` | Project header: estimation container. project_code is the natural key (QBO E-number). All three party_ids are string-ID (NO Postgres FKs). site_address is jsonb snapshot. Status enum with CHECK. Metadata columns added piecemeal: ADR-0019 (estimate/PO), ADR-0024 (role-typed parties). | ADR-0002, 0016 II.2, 0019, 0024 | 20260520223000_Project_Silo |
| `panels` | `id` (uuid) | `project_id` (FK, CASCADE), `sequence_no`, `name`, `status` (config, build, test, shipped), `config_payload` (jsonb) | Panel (sub-assembly). Per-project ordinal (sequence_no). config_payload is jsonb. Status enum with CHECK. | ADR-0002, 0020 | 20260520223000_Project_Silo |
| `bom_lines` | `id` (uuid) | `panel_id` (FK, CASCADE), `line_ordinal`, `part_id` (FK, RESTRICT, nullable), `criteria_snapshot` (jsonb, nullable), `qty`, `ref_des`, `notes`, `supersedes_line_id` (self-FK, SET NULL), `deleted_at` | BOM line item. Soft-delete: deleted_at IS NOT NULL marks a line as removed. XOR CHECK: (part_id IS NOT NULL AND criteria_snapshot IS NULL) OR (part_id IS NULL AND criteria_snapshot IS NOT NULL). Partial UNIQUE (panel_id, line_ordinal) WHERE deleted_at IS NULL (ADR-0013, 0020 §3). Self-FK supersedes_line_id for amendment chain (SET NULL on delete). | ADR-0013, 0016 III.B.3, 0020 | 20260521142225_Bom_RelationalLift |

**Key Constraints:**
- `projects.project_code`: UNIQUE
- `panels`: UNIQUE (project_id, sequence_no)
- `bom_lines`: XOR (part_id XOR criteria_snapshot) + qty > 0 (CHECK constraints)
- `bom_lines`: Soft-delete-filtered UNIQUE (panel_id, line_ordinal) WHERE deleted_at IS NULL

**Indexes:**
- `ix_projects_billed_to_party` (billed_to_party_id, partial: WHERE IS NOT NULL)
- `ix_projects_end_customer_party` (end_customer_party_id, partial: WHERE IS NOT NULL)
- `ix_panels_project` (project_id)
- `uq_bom_lines_panel_ordinal_active` (panel_id, line_ordinal, unique, partial: WHERE deleted_at IS NULL)

**String-ID Pattern:**
- `projects.billed_to_party_id`, `end_customer_party_id`, `contractor_party_id` → identity.parties (NO Postgres FK)

---

## Sales Schema (ADR-0028)

**Purpose:** Quotes, quote lines, invoices, invoice lines, payments, submittals, idempotency log.  
**ADRs:** ADR-0016 §II.6 (Wave 4 / subtask 4C84IhBzqyLayKdOBAzD), ADR-0028 (QBO write-through).

### Tables

| Table | PK | Key Columns | Purpose | Governing ADR | Migration |
|---|---|---|---|---|---|
| `quotes` | `id` (uuid) | `quote_number` (unique), `project_id`, `customer_party_id`, `status` (draft, sent, accepted, rejected, expired), `priced_total_cents`, `valid_until`, `bill_to_address` (jsonb), `ship_to_address` (jsonb), `ship_via`, `ship_date`, `expiration_date`, `accepted_by`, `accepted_date`, `store_id`, `online_payments_enabled`, `payment_instructions`, `note_to_customer`, `memo`, `deposit_request_cents`, `qbo_estimate_id`, `qbo_sync_token`, `qbo_synced_at`, `qbo_sync_state` (synced, pending, failed), `qbo_sync_error`, `external_ref` (unique), `created_by` | Quote header. project_id and customer_party_id are string-IDs (NO Postgres FKs). Address snapshots are jsonb (ADR-0028 §1.2). QBO state: qbo_estimate_id + qbo_sync_token + qbo_sync_state + qbo_sync_error (ADR-0028 §1.4–1.5). external_ref is idempotency key (ADR-0028 §6.2). Status enum with CHECK. | ADR-0016 II.6, 0028 | 20260520225934_Sales_SchemaCreate |
| `quote_lines` | `id` (uuid) | `quote_id` (FK, CASCADE), `line_no`, `part_id` (FK, RESTRICT, nullable), `qty`, `unit_price_cents`, `description` | Quote line item. Composite UNIQUE (quote_id, line_no). FK-bridge 3/4 to catalog.parts (RESTRICT, nullable). Filtered index on part_id. | ADR-0016 II.6, III.B.2 | 20260520225934_Sales_SchemaCreate |
| `quote_patch_idempotency` | `id` (uuid) | `quote_id` (FK, CASCADE), `external_ref`, `applied_at` | ADR-0028 §3: PATCH idempotency table. Composite UNIQUE (quote_id, external_ref). Records applied ExternalRef values so replayed PATCHes return current state without re-applying. Cascade-delete with parent quote. | ADR-0028 | 20260522042642_AddQuotesQboColumns |
| `submittals` | `id` (uuid) | `project_id`, `revision_no`, `status` (draft, sent, approved, revision_requested, rejected), `pdf_url`, `sent_at`, `approved_at` | Submittal (bid submission). Composite UNIQUE (project_id, revision_no). Status enum with CHECK. | ADR-0016 II.6 | 20260520225934_Sales_SchemaCreate |
| `invoices` | `id` (uuid) | `invoice_number` (unique), `project_id`, `quote_id` (FK, RESTRICT), `bill_to_party_id`, `status` (draft, sent, paid, void), `total_cents`, `due_at`, `issued_at` | Invoice header. project_id and bill_to_party_id are string-IDs (NO Postgres FKs). quote_id is an optional intra-silo FK (RESTRICT: can't delete a quote that has invoices). | ADR-0016 II.6 | 20260520225934_Sales_SchemaCreate |
| `invoice_lines` | `id` (uuid) | `invoice_id` (FK, CASCADE), `line_no`, `quote_line_id` (FK, SET NULL), `qty`, `unit_price_cents`, `description` | Invoice line item. Composite UNIQUE (invoice_id, line_no). Optional intra-silo FK to quote_lines (SET NULL: invoice line survives if quote line is deleted, per ADR-0028 §II.6). Filtered index on quote_line_id. | ADR-0016 II.6 | 20260520225934_Sales_SchemaCreate |
| `payments` | `id` (uuid) | `invoice_id` (FK, RESTRICT), `amount_cents`, `paid_at`, `method`, `reference_no` | Payment receipt. Intra-silo FK (RESTRICT: can't void an invoice that has payments). Indexed (invoice_id, paid_at DESC) for aging-and-history scan. | ADR-0016 II.6 | 20260520225934_Sales_SchemaCreate |

**Key Constraints:**
- `quotes.quote_number`: UNIQUE
- `quotes.external_ref`: UNIQUE (ADR-0028 §6.2)
- `quote_lines`: UNIQUE (quote_id, line_no)
- `quote_patch_idempotency`: UNIQUE (quote_id, external_ref)
- `submittals`: UNIQUE (project_id, revision_no)
- `invoices.invoice_number`: UNIQUE
- `invoice_lines`: UNIQUE (invoice_id, line_no)

**Status Enums (CHECK):**
- `quotes.status`: draft, sent, accepted, rejected, expired
- `quotes.qbo_sync_state`: synced, pending, failed
- `submittals.status`: draft, sent, approved, revision_requested, rejected
- `invoices.status`: draft, sent, paid, void

**Indexes:**
- `ix_quote_lines_part` (part_id, partial: WHERE part_id IS NOT NULL)
- `ix_invoice_lines_quote_line` (quote_line_id, partial: WHERE quote_line_id IS NOT NULL)
- `ix_payments_invoice_paid` (invoice_id, paid_at DESC)

**String-ID Pattern:**
- `quotes.project_id`, `customer_party_id` → project.projects, identity.parties (NO Postgres FK)
- `invoices.project_id`, `bill_to_party_id` → project.projects, identity.parties (NO Postgres FK)
- `submittals.project_id` → project.projects (NO Postgres FK)

---

## Identity Schema (Wave 2, Phase 0)

**Purpose:** Unified parties (customers, vendors, contractors), contacts, addresses by role.  
**ADRs:** ADR-0016 §II.1 (Wave 2).

### Tables

| Table | PK | Key Columns | Purpose | Governing ADR | Migration |
|---|---|---|---|---|---|
| `parties` | `id` (uuid) | `display_name`, `is_customer`, `is_vendor`, `is_contractor`, `tax_id`, `notes`, `external_ref` (unique, nullable, partial index WHERE NOT NULL), `created_by` | Unified party model: one row per unique entity (customer, vendor, contractor, or combinations). Role flags (is_customer, is_vendor, is_contractor) are booleans. external_ref is an optional idempotency key (ADR-0028 §6.2). | ADR-0016 II.1, 0028 | 20260520222837_Identity_Silo |
| `contacts` | `id` (uuid) | `party_id` (FK, CASCADE), `name`, `email`, `phone`, `role` | Contact person attached to a party. Multiple contacts per party. Indexed (party_id) for fetch-a-party's-contacts lookup. | ADR-0016 II.1 | 20260520222837_Identity_Silo |
| `party_addresses` | `id` (uuid) | `party_id` (FK, CASCADE), `role` (PoIssuer, ShipTo, EndCustomer, BilledTo), `street1`, `street2`, `city`, `region`, `postal_code`, `country`, `is_primary` | Address by role. Composite index (party_id, role). Role enum with CHECK constraint. | ADR-0016 II.1, III | 20260520222837_Identity_Silo |

**Key Constraints:**
- `parties.external_ref`: UNIQUE (partial: WHERE external_ref IS NOT NULL)
- `party_addresses.role`: PoIssuer, ShipTo, EndCustomer, BilledTo (CHECK)

**Indexes:**
- `ix_contacts_party` (party_id)
- `ix_party_addresses_party_role` (party_id, role)

**No Cross-Silo FKs:**
- Identity tables have NO FKs out to other silos (Article III.A enforced by what we don't declare).
- All inter-silo refs to identity tables (e.g., `projects.billed_to_party_id`, `purchase_orders.issuer_party_id`) are string-ID columns.

---

## Fab Schema (Wave 4)

**Purpose:** Stock locations, build tasks, stock movements (realized by ADR-0026).  
**ADRs:** ADR-0016 §II.7 (Wave 4 / subtask TSwM0ojG1FoKj1HTS7oa), ADR-0026 (receive pipeline).

### Tables

| Table | PK | Key Columns | Purpose | Governing ADR | Migration |
|---|---|---|---|---|---|
| `stock_locations` | `id` (uuid) | `code` (unique), `name`, `is_active` | Location master: warehouse, bin, etc. Referenced by part_inventory and receipts. | ADR-0026 | 20260521150000_Receive_Pipeline |
| `stock_movements` | `id` (uuid) | `location_id`, `part_id`, `movement_type`, `qty`, `reference_type`, `reference_id`, `created_at` | Stock ledger: one row per movement (inbound, outbound, adjustment). part_inventory rollup is derived from this ledger. | ADR-0016 II.7 | 20260520225000_Fab_Silo |
| `build_tasks` | `id` (uuid) | `panel_id`, `task_name`, `status`, `assigned_to`, `due_at` | Build instruction task attached to a panel. | ADR-0016 II.7 | 20260520225000_Fab_Silo |

**Indexes:**
- `uq_stock_locations_code` (code, unique)

**Cross-Silo FK:**
- `part_inventory.location_id` → fab.stock_locations.id (RESTRICT)
- `stock_movements.location_id` → fab.stock_locations (implied, not yet modeled as FK in PartInventoryEntity)

---

## Audit Schema

**Purpose:** Single append-only domain-event log across all silos for change tracking.  
**ADRs:** ADR-0016 §IV.1 (AuditSaveChangesInterceptor).

### Tables

| Table | PK | Key Columns | Purpose | Governing ADR | Migration |
|---|---|---|---|---|---|
| `domain_event_log` | `event_id` (uuid) | `occurred_at`, `actor`, `silo` (derived from entity schema), `entity_type`, `entity_id`, `op` (insert, update, delete, soft_delete, restore, qbo_pull_insert, …), `payload` (jsonb), `txn_id` | Append-only audit trail: one row per write. Populated by AuditSaveChangesInterceptor inside the same Postgres txn as the business write. Op enum with CHECK. Indexed (silo, occurred_at DESC), (entity_type, entity_id, occurred_at DESC), (actor, partial WHERE actor <> 'system'). | ADR-0016 IV.1 | 20260520220231_Audit_DomainEventLog |

**Op Enum (CHECK):**
- insert, update, delete, soft_delete, restore
- qbo_pull_insert, qbo_pull_update, qbo_pull_skipped, qbo_pull_item_ignored, qbo_pull_dep_missing
- qbo_endcustomer_tag_deferred

**Indexes:**
- `ix_audit_silo_occurred` (silo, occurred_at DESC)
- `ix_audit_entity_lookup` (entity_type, entity_id, occurred_at DESC)
- `ix_audit_actor` (actor, partial: WHERE actor <> 'system')

**Notes:**
- Single audit table across all silos (not one per silo) per ADR-0016 §IV.1.
- AuditSaveChangesInterceptor reads schema metadata (`IEntityType.GetSchema()`) to derive the silo column value.
- QBO-specific ops (qbo_pull_*) added by later migrations as QBO integration expanded.

---

## Integration Schema (ADR-0030)

**Purpose:** QBO ID mapping (integration decoupler).  
**ADRs:** ADR-0030 (eight-silo integration decoupler).

### Tables

| Table | PK | Key Columns | Purpose | Governing ADR | Migration |
|---|---|---|---|---|---|
| `qbo_external_id_map` | `id` (uuid) | `dERP_entity_type`, `dERP_id`, `qbo_entity_type`, `qbo_ids` (jsonb), `synced_at`, `sync_error` | Mapping table: keeps seven business silos free of integration concerns. Stores dERP ↔ QBO ID pairs. qbo_ids is jsonb for multiple/future QBO reference types. | ADR-0030 | 20260521220215_Integration_QboExternalIdMap |

**Notes:**
- Eighth silo (integration) is isolated from business logic by design (ADR-0030 §3.5).
- qbo_ids field carries multiple QBO reference types in a single jsonb object (e.g., estimate_id, invoice_id, etc.).

---

## Public Schema (Legacy namespace)

**Purpose:** Manufacturer, UOM conversion, UL reference (legacy; mostly superseded by catalog).  
**ADRs:** ADR-0004 (UL listing as part attribute), ADR-0002 (phased rollout).

### Tables

| Table | PK | Key Columns | Purpose | Governing ADR | Migration |
|---|---|---|---|---|---|
| `manufacturers` | `id` (uuid) | `name` (unique), `code` (unique, nullable), `notes`, `is_active` | See catalog schema (duplicated here, may be consolidated). | ADR-0002 | 20260513164227_Phase2_ManufacturersVendorsLifecycle |
| `uom_conversions` | `id` (uuid) | `from_uom`, `to_uom`, `factor` (numeric 20,10) | Unit-of-measure conversion factors (e.g., 1 dozen = 12 units). | ADR-0002 | 20260519033910_UoM_Conversion |
| `ul_listing_category_reference` | `code` (string, max 8) | `description` | See catalog schema (legacy; may be consolidated). | ADR-0004 | 20260513145303_InitialCreate |
| `ul_standard_reference` | `code` (string, max 40) | `description` | See catalog schema (legacy; may be consolidated). | ADR-0004 | 20260513145303_InitialCreate |

---

## Entity → Table Mapping

### Catalog Silo

| Entity Class | File Path | Entity Namespace | Table | Schema | EF Configuration | Migration(s) |
|---|---|---|---|---|---|---|
| PartEntity | dERP.Data/Entities/PartEntity.cs | dERP.Data.Entities | parts | catalog | dERPDbContext l.96–149 | InitialCreate, Part_ProfileColumns, Part_FeelColumn, Part_DropCriteriaColumns, Catalog_SchemaConsolidation |
| PartCategoryEntity | dERP.Data/Entities/PartCategoryEntity.cs | dERP.Data.Entities | part_categories | catalog | dERPDbContext l.151–162 | Category_LookupTable, Category_AuxContactRow, AddPartCategoryExpansionAdr0014 |
| PartSubstituteEntity | dERP.Data/Entities/PartSubstituteEntity.cs | dERP.Data.Entities | part_substitutes | catalog | dERPDbContext l.180–198 | InitialCreate |
| PartInventoryEntity | dERP.Data/Entities/PartInventoryEntity.cs | dERP.Data.Entities | part_inventory | catalog | dERPDbContext l.309–335 | Phase3and4_VendorPartsAndInventory, Receive_Pipeline |
| PartLifecycleEventEntity | dERP.Data/Entities/PartLifecycleEventEntity.cs | dERP.Data.Entities | part_lifecycle_events | catalog | dERPDbContext l.278–307 | Part_LifecycleHistory |
| PartEnrichmentEntity | dERP.Data/Entities/PartEnrichmentEntity.cs | dERP.Data.Entities | part_enrichments | catalog | dERPDbContext l.368–417 | Part_EnrichmentSidecar |
| ManufacturerEntity | dERP.Data/Entities/ManufacturerEntity.cs | dERP.Data.Entities | manufacturers | public | dERPDbContext l.200–213 | Phase2_ManufacturersVendorsLifecycle |
| UlListingCategoryReferenceEntity | dERP.Data/Entities/UlListingCategoryReferenceEntity.cs | dERP.Data.Entities | ul_listing_category_reference | public | dERPDbContext l.164–170 | InitialCreate |
| UlStandardReferenceEntity | dERP.Data/Entities/UlStandardReferenceEntity.cs | dERP.Data.Entities | ul_standard_reference | public | dERPDbContext l.172–178 | InitialCreate |

### Procurement Silo

| Entity Class | File Path | Entity Namespace | Table | Schema | EF Configuration | Migration(s) |
|---|---|---|---|---|---|---|
| ProcurementVendorEntity | dERP.Data/Entities/Procurement/ProcurementVendorEntity.cs | dERP.Data.Entities.Procurement | vendors | procurement | dERPDbContext l.851–864 | Procurement_Silo, PathD_VendorDataCleanup |
| ProcurementVendorPartEntity | dERP.Data/Entities/Procurement/ProcurementVendorPartEntity.cs | dERP.Data.Entities.Procurement | vendor_parts | procurement | dERPDbContext l.1172–1204 | Phase3and4_VendorPartsAndInventory, PathD_VendorDataCleanup |
| PurchaseOrderEntity | dERP.Data/Entities/Procurement/PurchaseOrderEntity.cs | dERP.Data.Entities.Procurement | purchase_orders | procurement | dERPDbContext l.1317–1346 | Procurement_Silo |
| PoLineEntity | dERP.Data/Entities/Procurement/PoLineEntity.cs | dERP.Data.Entities.Procurement | po_lines | procurement | dERPDbContext l.1348–1373 | Procurement_Silo |
| PoRevisionEntity | dERP.Data/Entities/Procurement/PoRevisionEntity.cs | dERP.Data.Entities.Procurement | po_revisions | procurement | dERPDbContext l. (line# TBD) | Procurement_Silo |
| PoReceiptEntity | dERP.Data/Entities/Procurement/PoReceiptEntity.cs | dERP.Data.Entities.Procurement | po_receipts | procurement | dERPDbContext (not shown in truncated output) | PoReceipt |
| ReceiptEntity | dERP.Data/Entities/Procurement/ReceiptEntity.cs | dERP.Data.Entities.Procurement | receipts | procurement | dERPDbContext l.1226–1263 | Receive_Pipeline |
| ReceiptLineEntity | dERP.Data/Entities/Procurement/ReceiptLineEntity.cs | dERP.Data.Entities.Procurement | receipt_lines | procurement | dERPDbContext l.1265–1315 | Receive_Pipeline |

### Pricing Silo

| Entity Class | File Path | Entity Namespace | Table | Schema | EF Configuration | Migration(s) |
|---|---|---|---|---|---|---|
| PriceHistoryEntity | dERP.Data/Entities/PriceHistoryEntity.cs | dERP.Data.Entities | price_history | pricing | dERPDbContext l.224–276 | Pricing_History, Pricing_Silo |

### Project Silo

| Entity Class | File Path | Entity Namespace | Table | Schema | EF Configuration | Migration(s) |
|---|---|---|---|---|---|---|
| ProjectEntity | dERP.Data/Entities/Project/ProjectEntity.cs | dERP.Data.Entities.Project | projects | project | dERPDbContext l.866–949 | Project_Silo, Project_Metadata_CustomerPO, 0024_ProjectFkSlotExpansion |
| PanelEntity | dERP.Data/Entities/Project/PanelEntity.cs | dERP.Data.Entities.Project | panels | project | dERPDbContext l.1013–1048 | Project_Silo |
| BomLineEntity | dERP.Data/Entities/Project/BomLineEntity.cs | dERP.Data.Entities.Project | bom_lines | project | dERPDbContext l.1073–1170 | Bom_RelationalLift |

### Sales Silo

| Entity Class | File Path | Entity Namespace | Table | Schema | EF Configuration | Migration(s) |
|---|---|---|---|---|---|---|
| QuoteEntity | dERP.Data/Entities/Sales/QuoteEntity.cs | dERP.Data.Entities.Sales | quotes | sales | dERPDbContext l.441–530 | Sales_SchemaCreate, AddQuotesQboColumns, AddQuotesExternalRef |
| QuoteLineEntity | dERP.Data/Entities/Sales/QuoteLineEntity.cs | dERP.Data.Entities.Sales | quote_lines | sales | dERPDbContext l.532–570 | Sales_SchemaCreate |
| QuotePatchIdempotencyEntity | dERP.Data/Entities/Sales/QuotePatchIdempotencyEntity.cs | dERP.Data.Entities.Sales | quote_patch_idempotency | sales | dERPDbContext l.579–605 | AddQuotesQboColumns |
| SubmittalEntity | dERP.Data/Entities/Sales/SubmittalEntity.cs | dERP.Data.Entities.Sales | submittals | sales | dERPDbContext l.607–622 | Sales_SchemaCreate |
| InvoiceEntity | dERP.Data/Entities/Sales/InvoiceEntity.cs | dERP.Data.Entities.Sales | invoices | sales | dERPDbContext l.624–649 | Sales_SchemaCreate |
| InvoiceLineEntity | dERP.Data/Entities/Sales/InvoiceLineEntity.cs | dERP.Data.Entities.Sales | invoice_lines | sales | dERPDbContext l.651–685 | Sales_SchemaCreate |
| PaymentEntity | dERP.Data/Entities/Sales/PaymentEntity.cs | dERP.Data.Entities.Sales | payments | sales | dERPDbContext l.687–715 | Sales_SchemaCreate |

### Identity Silo

| Entity Class | File Path | Entity Namespace | Table | Schema | EF Configuration | Migration(s) |
|---|---|---|---|---|---|---|
| PartyEntity | dERP.Data/Entities/Identity/PartyEntity.cs | dERP.Data.Entities.Identity | parties | identity | dERPDbContext l.806–832 | Identity_Silo, Identity_PartyExternalRef |
| ContactEntity | dERP.Data/Entities/Identity/ContactEntity.cs | dERP.Data.Entities.Identity | contacts | identity | dERPDbContext l.951–972 | Identity_Silo |
| PartyAddressEntity | dERP.Data/Entities/Identity/PartyAddressEntity.cs | dERP.Data.Entities.Identity | party_addresses | identity | dERPDbContext l.974–1011 | Identity_Silo |

### Fab Silo

| Entity Class | File Path | Entity Namespace | Table | Schema | EF Configuration | Migration(s) |
|---|---|---|---|---|---|---|
| LocationEntity | dERP.Data/Entities/Fab/LocationEntity.cs | dERP.Data.Entities.Fab | stock_locations | fab | dERPDbContext l.1210–1224 | Receive_Pipeline |
| BuildTaskEntity | dERP.Data/Entities/Fab/BuildTaskEntity.cs | dERP.Data.Entities.Fab | build_tasks | fab | dERPDbContext l. (line# TBD) | Fab_Silo |
| StockMovementEntity | dERP.Data/Entities/Fab/StockMovementEntity.cs | dERP.Data.Entities.Fab | stock_movements | fab | dERPDbContext l. (line# TBD) | Fab_Silo |

### Audit & Integration

| Entity Class | File Path | Entity Namespace | Table | Schema | EF Configuration | Migration(s) |
|---|---|---|---|---|---|---|
| DomainEventLogEntity | dERP.Data/Entities/DomainEventLogEntity.cs | dERP.Data.Entities | domain_event_log | audit | dERPDbContext l.717–781 | Audit_DomainEventLog, Audit_QboOps_ConstraintExpansion, Audit_S4Ops_ConstraintExpansion |
| EntityChangeOutboxEntity | dERP.Data/Entities/EntityChangeOutboxEntity.cs | dERP.Data.Entities | entity_change_outbox | public | dERPDbContext l.349–366 | Entity_ChangeOutbox |
| QboExternalIdMapEntity | dERP.Data/Entities/Integration/QboExternalIdMapEntity.cs | dERP.Data.Entities.Integration | qbo_external_id_map | integration | dERPDbContext l.92 | Integration_QboExternalIdMap |

### UOM Conversion (Legacy/Public)

| Entity Class | File Path | Entity Namespace | Table | Schema | EF Configuration | Migration(s) |
|---|---|---|---|---|---|---|
| UomConversionEntity | dERP.Data/Entities/UomConversionEntity.cs | dERP.Data.Entities | uom_conversions | public | dERPDbContext l.337–347 | UoM_Conversion |

---

## Migration Chronology

Migrations are listed in apply order. **Never edit a migration after it has been applied to any environment** (CLAUDE.md rule 4).

### Initial Schema (May 13, 2026)

| Migration Name | Timestamp | Purpose | Tables Added | ADR Ref |
|---|---|---|---|---|
| InitialCreate | 20260513145303 | Parts, categories, substitutes, UL references, manufacturers, UOM, UL standard | parts, part_categories, part_substitutes, manufacturers, ul_listing_category_reference, ul_standard_reference, uom_conversions | ADR-0002 (Phase 1) |
| Phase2_ManufacturersVendorsLifecycle | 20260513164227 | Vendor/manufacturer master, lifecycle status, price history structure | vendors (public), manufacturer table consolidation | ADR-0002 (Phase 2), 0005 |
| Phase3and4_VendorPartsAndInventory | 20260513175115 | Vendor parts catalog, part inventory, pricing initial seeding | vendor_parts, part_inventory | ADR-0002 (Phase 3–4) |

### Profile & Schema Split (May 18–20, 2026)

| Migration Name | Timestamp | Purpose | Tables Affected | ADR Ref |
|---|---|---|---|---|
| Parts_TrgmSearchIndex | 20260518120000 | Full-text search index on parts (trigram) | parts | ADR-0008 (implicit) |
| Part_ProfileColumns | 20260519031534 | Add profile columns (dimensions, weight, UL file#, etc.) | parts (ADD columns) | ADR-0008 |
| Pricing_History | 20260519031815 | Create price_history append-only log (without schema yet) | price_history (public schema TBD) | ADR-0005 |
| Category_LookupTable | 20260519031849 | Create part_categories with feel_schema (jsonb) | part_categories | ADR-0017 |
| Part_FeelColumn | 20260519031938 | Add feel (jsonb) column to parts | parts (ADD feel) | ADR-0008, 0017 |
| UoM_Conversion | 20260519033910 | UOM lookup table | uom_conversions | ADR-0002 |
| Part_LifecycleHistory | 20260519102059 | Create part_lifecycle_events audit table | part_lifecycle_events | ADR-0002, 0013 |
| Entity_ChangeOutbox | 20260519102922 | Outbox pattern for change events | entity_change_outbox | ADR-0016 (implicit) |
| Part_DropCriteriaColumns | 20260520120248 | Drop legacy flat criteria columns; rely on feel (jsonb) | parts (DROP columns) | ADR-0008 |
| Part_EnrichmentSidecar | 20260520192740 | Create part_enrichments 1:1 sidecar | part_enrichments | ADR-0034 |

### Silo Reorganization (May 20, 2026)

| Migration Name | Timestamp | Purpose | Tables Affected | ADR Ref |
|---|---|---|---|---|
| Audit_DomainEventLog | 20260520220231 | Create audit schema + domain_event_log table | domain_event_log (audit) | ADR-0016 IV.1 |
| Identity_Silo | 20260520222837 | Create identity schema + parties/contacts/addresses | parties, contacts, party_addresses (identity) | ADR-0016 II.1 |
| Catalog_SchemaConsolidation | 20260520223000 | Move parts & related tables into catalog schema | parts, part_categories, part_substitutes, part_lifecycle_events, part_enrichments, part_inventory (catalog) | ADR-0016 II.4 |
| Project_Silo | 20260520223000 | Create project schema + projects/panels | projects, panels (project) | ADR-0016 II.2 |
| Pricing_Silo | 20260520224000 | Move price_history into pricing schema; add triggers | price_history (pricing schema) | ADR-0016 II.5 |
| Fab_Silo | 20260520225000 | Create fab schema + build_tasks/stock_movements | build_tasks, stock_movements (fab) | ADR-0016 II.7 |
| Sales_SchemaCreate | 20260520225934 | Create sales schema + quotes/quote_lines/invoices/submittals/payments | quotes, quote_lines, submittals, invoices, invoice_lines, payments (sales) | ADR-0016 II.6 |
| Procurement_Silo | 20260520230012 | Create procurement schema + vendors/vendor_parts/PO tables | vendors, vendor_parts, purchase_orders, po_lines, po_revisions (procurement) | ADR-0016 II.3 |

### Feature-Specific (May 21–22, 2026)

| Migration Name | Timestamp | Purpose | Tables Affected | ADR Ref |
|---|---|---|---|---|
| Category_AuxContactRow | 20260521141200 | Seed PartCategory rows (Breaker, Contactor, MotorProtector, …) | part_categories (INSERT) | ADR-0014 |
| Project_Metadata_CustomerPO | 20260521142100 | Add project metadata: estimate_number, customer_po_number, drive URLs, received_at | projects (ADD columns) | ADR-0019 |
| Bom_RelationalLift | 20260521142225 | Create bom_lines with soft-delete + XOR constraint | bom_lines (project) | ADR-0020 |
| Receive_Pipeline | 20260521150000 | Create fab.stock_locations, procurement.receipts/receipt_lines | stock_locations, receipts, receipt_lines (fab/procurement) | ADR-0026 |
| Integration_QboExternalIdMap | 20260521220215 | Create integration schema + qbo_external_id_map | qbo_external_id_map (integration) | ADR-0030 |
| AddQuotesQboColumns | 20260522042642 | Add QBO columns to quotes: qbo_estimate_id, qbo_sync_state, etc.; create quote_patch_idempotency | quotes (ADD columns), quote_patch_idempotency (sales) | ADR-0028 |
| AddPartCategoryExpansionAdr0014 | 20260522043253 | Insert additional category rows (FuseHolder, etc.) with idempotency | part_categories (INSERT…ON CONFLICT) | ADR-0014, 0049 |
| Audit_QboOps_ConstraintExpansion | 20260522044950 | Expand domain_event_log.op enum to include QBO pull ops | domain_event_log (CHECK constraint) | ADR-0030 (implicit) |
| Audit_S4Ops_ConstraintExpansion | 20260522051410 | Expand domain_event_log.op enum for S4 ops | domain_event_log (CHECK constraint) | ADR-0030 (implicit) |
| AddQuotesExternalRef | 20260522051615 | Add external_ref idempotency key to quotes | quotes (ADD external_ref, UNIQUE) | ADR-0028 |
| Identity_PartyExternalRef | 20260522080000 | Add external_ref idempotency key to parties | parties (ADD external_ref, UNIQUE partial) | ADR-0028 |
| 0024_ProjectFkSlotExpansion | 20260522090000 | Add end_customer_party_id, contractor_party_id to projects | projects (ADD columns) | ADR-0024 |
| PoReceipt | 20260522100000 | Create po_receipts thin receive record | po_receipts (procurement) | vkJFuUHjGsPsTYYRwv8l-impl |
| PathD_VendorDataCleanup | 20260522225907 | Migrate public.vendors → procurement.vendors, drop legacy tables + FK | vendors (public → procurement via INSERT…SELECT), drop public.vendors, drop public.vendor_parts, drop FK pricing.price_history.vendor_part_id | ADR-0033 |

---

## Cross-Silo Relationships

### Foreign-Key Bridges (Postgres FKs)

| From | To | Type | OnDelete | Defined In |
|---|---|---|---|---|
| **procurement.po_lines.part_id** | **catalog.parts.id** | Cross-silo | RESTRICT | dERPDbContext l.1356–1373, Procurement_Silo migration |
| **procurement.vendor_parts.part_id** | **catalog.parts.id** | Cross-silo | RESTRICT | dERPDbContext l.1181–1203, Procurement_Silo migration |
| **sales.quote_lines.part_id** | **catalog.parts.id** | Cross-silo | RESTRICT | dERPDbContext l.541–569, Sales_SchemaCreate migration |
| **project.bom_lines.part_id** | **catalog.parts.id** | Cross-silo | RESTRICT | dERPDbContext l.1123–1162, Bom_RelationalLift migration |
| **catalog.part_inventory.location_id** | **fab.stock_locations.id** | Cross-silo | RESTRICT | dERPDbContext l.331–334 |
| **procurement.receipts.purchase_order_id** | **procurement.purchase_orders.id** | Intra-silo | SET NULL | dERPDbContext l.1259–1262, Receive_Pipeline migration |
| **procurement.receipt_lines.receipt_id** | **procurement.receipts.id** | Intra-silo | CASCADE | dERPDbContext l.1298–1301 |
| **procurement.receipt_lines.po_line_id** | **procurement.po_lines.id** | Intra-silo | SET NULL | dERPDbContext l.1311–1314 |
| **sales.quote_lines.quote_id** | **sales.quotes.id** | Intra-silo | CASCADE | dERPDbContext l.548–551 |
| **sales.invoice_lines.invoice_id** | **sales.invoices.id** | Intra-silo | CASCADE | dERPDbContext l.667–670 |
| **sales.invoice_lines.quote_line_id** | **sales.quote_lines.id** | Intra-silo | SET NULL | dERPDbContext l.676–679 |
| **sales.invoices.quote_id** | **sales.quotes.id** | Intra-silo | RESTRICT | dERPDbContext l.645–648 |
| **sales.payments.invoice_id** | **sales.invoices.id** | Intra-silo | RESTRICT | dERPDbContext l.703–706 |
| **project.panels.project_id** | **project.projects.id** | Intra-silo | CASCADE | dERPDbContext l.1044–1047 |
| **project.bom_lines.panel_id** | **project.panels.id** | Intra-silo | CASCADE | dERPDbContext l.1150–1153 |
| **project.bom_lines.supersedes_line_id** | **project.bom_lines.id** | Self | SET NULL | dERPDbContext l.1166–1169 |
| **identity.contacts.party_id** | **identity.parties.id** | Intra-silo | CASCADE | dERPDbContext l.968–971 |
| **identity.party_addresses.party_id** | **identity.parties.id** | Intra-silo | CASCADE | dERPDbContext l.1007–1010 |
| **procurement.vendors.party_id** | **identity.parties.id** | **NO Postgres FK** (string-ID) | — | dERPDbContext l.859 |
| **procurement.po_lines.po_id** | **procurement.purchase_orders.id** | Intra-silo | CASCADE | dERPDbContext l.1369–1372 |

### String-ID References (No Postgres FK)

| From Table | Column | Target Silo | Target Table | Reason | ADR |
|---|---|---|---|---|---|
| projects | billed_to_party_id, end_customer_party_id, contractor_party_id | identity | parties | ADR-0016 §III.B (no cross-silo FK) | ADR-0016, 0024 |
| projects | project_id (implicit) | project | projects | Self-reference (implicit in string context) | ADR-0024 |
| purchase_orders | issuer_party_id, ship_to_address_party_id, end_customer_party_id, bill_to_party_id | identity | parties | ADR-0016 §III.B | ADR-0016 |
| purchase_orders | project_id | project | projects | ADR-0016 §III.B | ADR-0016 |
| quotes | project_id, customer_party_id | project, identity | projects, parties | ADR-0016 §III.B | ADR-0016 |
| submittals | project_id | project | projects | ADR-0016 §III.B | ADR-0016 |
| invoices | project_id, bill_to_party_id | project, identity | projects, parties | ADR-0016 §III.B | ADR-0016 |
| receipts | vendor_id | procurement | vendors | Implicit in schema (not enforced) | ADR-0026 |
| vendors | party_id | identity | parties | ADR-0016 §II.3 (optional mapping) | ADR-0016, 0033 |

**Rationale:** Cross-silo FKs (Postgres-level constraints) exist only at the four canonical bridges to catalog.parts. All other inter-silo refs are handled at the application layer to decouple silos and enable independent evolution (ADR-0016 §III.B).

---

## Indexes Summary

### High-Value Indexes

| Index Name | Table | Columns | Type | Filter | Purpose | Migration |
|---|---|---|---|---|---|---|
| `ix_parts_part_number` | parts | part_number | unique | — | Quick lookup by part number | InitialCreate |
| `ix_parts_category_id` | parts | category_id | — | — | Fetch parts by category | InitialCreate |
| `ix_parts_manufacturer_id` | parts | manufacturer_id | — | — | Fetch parts by manufacturer | InitialCreate |
| `ix_parts_lifecycle_status` | parts | lifecycle_status | — | — | Filter parts by status | InitialCreate |
| `ix_part_lifecycle_events_part_transitioned_at_desc` | part_lifecycle_events | (part_id, transitioned_at DESC) | — | — | Newest-first history lookup | Part_LifecycleHistory |
| `ix_part_enrichments_fetch_status` | part_enrichments | fetch_status | — | — | Worker drain (Pending/Stale) | Part_EnrichmentSidecar |
| `ix_part_enrichments_last_fetched_at` | part_enrichments | last_fetched_at | — | — | Stale-sweep query | Part_EnrichmentSidecar |
| `ix_vendor_parts_part` | vendor_parts | part_id | — | — | "Which vendors sell part X" lookup | Phase3and4_VendorPartsAndInventory |
| `ix_receipts_external_ref` | receipts | external_ref | unique | — | Idempotency nonce (ADR-0026 §6) | Receive_Pipeline |
| `ix_receipts_vendor` | receipts | (vendor_id, received_at DESC) | — | — | Recent receipts by vendor | Receive_Pipeline |
| `ix_receipt_lines_receipt` | receipt_lines | (receipt_id, line_no) | unique | — | Line-number uniqueness within receipt | Receive_Pipeline |
| `ix_receipt_lines_unresolved` | receipt_lines | status | — | status='unresolved' | Unresolved receipt lines query | Receive_Pipeline |
| `ix_price_history_vendor_part_observed_date_desc` | price_history | (vendor_part_id, observed_date DESC) | — | — | Newest-first current-price lookup | Pricing_History |
| `ix_quote_lines_part` | quote_lines | part_id | — | part_id IS NOT NULL | Part-based quote lookup (filtered) | Sales_SchemaCreate |
| `ix_invoice_lines_quote_line` | invoice_lines | quote_line_id | — | quote_line_id IS NOT NULL | Quote line back-ref (filtered) | Sales_SchemaCreate |
| `ix_payments_invoice_paid` | payments | (invoice_id, paid_at DESC) | — | — | Aging-and-history scan (newest first) | Sales_SchemaCreate |
| `ix_projects_billed_to_party` | projects | billed_to_party_id | — | billed_to_party_id IS NOT NULL | Lookup projects by billed-to party | Project_Silo |
| `ix_projects_end_customer_party` | projects | end_customer_party_id | — | end_customer_party_id IS NOT NULL | Lookup projects by end-customer (ADR-0024) | 0024_ProjectFkSlotExpansion |
| `ix_panels_project` | panels | project_id | — | — | Fetch panels for a project | Project_Silo |
| `uq_bom_lines_panel_ordinal_active` | bom_lines | (panel_id, line_ordinal) | unique | deleted_at IS NULL | Active BOM line uniqueness (soft-delete filter, ADR-0020 §3) | Bom_RelationalLift |
| `ix_contacts_party` | contacts | party_id | — | — | Fetch party's contacts | Identity_Silo |
| `ix_party_addresses_party_role` | party_addresses | (party_id, role) | — | — | Lookup party's address by role | Identity_Silo |
| `uq_sales_quotes_external_ref` | quotes | external_ref | unique | — | Idempotency nonce (ADR-0028 §6.2) | AddQuotesExternalRef |
| `uq_parties_external_ref` | parties | external_ref | unique | external_ref IS NOT NULL | Idempotency nonce (ADR-0028 §6.2) | Identity_PartyExternalRef |
| `ix_audit_silo_occurred` | domain_event_log | (silo, occurred_at DESC) | — | — | Audit by silo, newest first | Audit_DomainEventLog |
| `ix_audit_entity_lookup` | domain_event_log | (entity_type, entity_id, occurred_at DESC) | — | — | Audit by entity, newest first | Audit_DomainEventLog |
| `ix_audit_actor` | domain_event_log | actor | — | actor <> 'system' | Human-only audit queries (partial) | Audit_DomainEventLog |
| `uq_stock_locations_code` | stock_locations | code | unique | — | Warehouse/bin code lookup | Receive_Pipeline |

---

## Soft-Delete & Supersession

**Current Status:** Soft-delete is implemented **only** on `project.bom_lines.deleted_at` per ADR-0013 and ADR-0020 §3.

### bom_lines Soft-Delete Pattern (ADR-0020 §3)

```sql
-- Active BOM lines: WHERE deleted_at IS NULL
-- Deleted (tombstoned): WHERE deleted_at IS NOT NULL
-- Partial UNIQUE on active rows: (panel_id, line_ordinal) WHERE deleted_at IS NULL
```

**Supersession Chain:** bom_lines.supersedes_line_id is a self-FK (SET NULL) allowing amendment history without requiring a full rewrite of the BOM. A new line with supersedes_line_id=<old_line_id> replaces the old line logically.

**No Soft-Delete Elsewhere:** 
- catalog.parts: no soft-delete (ADR-0013 acknowledges gap; deferred to phase 5+).
- All other tables: hard DELETE via FK CASCADE or RESTRICT.

---

## Jsonb Columns (Dynamic Schema)

| Table | Column | Purpose | ADR | Constraints |
|---|---|---|---|---|
| **catalog.parts** | `feel` | Category-typed criteria (Breaker feel schema: poles, max_amps, etc.) | ADR-0008, 0017 | Null until data populated. Schema defined in part_categories.feel_schema. |
| **catalog.part_categories** | `feel_schema` | Jsonb schema definition for a category's criteria structure (e.g., BreakerFeelSchema) | ADR-0017 | Null until category typology is populated (ADR-0014). |
| **catalog.part_enrichments** | `image_urls` | Array of machine-authored image URLs. Postgres default: '[]'::jsonb. | ADR-0034 | Required (NOT NULL). Migration sets default; CLR default [] for EnsureCreated. |
| **project.panels** | `config_payload` | Panel configuration (CAD model spec, etc.). Required. | ADR-0002 | Required (NOT NULL). |
| **project.bom_lines** | `criteria_snapshot` | Jsonb snapshot of PartCriteria (for criteria-based lines where part_id is NULL). | ADR-0020 §1 | XOR with part_id: exactly one is non-null. |
| **sales.quotes** | `bill_to_address`, `ship_to_address` | Address snapshots (jsonb). Nullable. | ADR-0028 §1.2 | Nullable (optional). Migration sets Postgres default (jsonb-only); CLR default null for EnsureCreated. |
| **project.projects** | `site_address` | Site address snapshot (jsonb). Required. | ADR-0016 II.2 | Required (NOT NULL). CLR default "{}"; migration sets Postgres default '{}':jsonb. |
| **integration.qbo_external_id_map** | `qbo_ids` | Map of QBO reference types to IDs (e.g., {estimate_id, invoice_id}). | ADR-0030 | Jsonb object (schema varies by QBO entity type). |
| **audit.domain_event_log** | `payload` | Jsonb snapshot of the changed entity state (old/new values). | ADR-0016 IV.1 | Required (NOT NULL). Migration default '{}':jsonb; CLR uses implicit null → EF Core handles. |

---

## Migrations & Phase Rollout

### By Phase (ADR-0002)

| Phase | Scope | Migrations | Tables | ADRs |
|---|---|---|---|---|
| **1** | Core parts catalog + substitutes | InitialCreate (parts, categories, substitutes, UL refs) | parts, part_categories, part_substitutes, ul_*_reference | ADR-0002 |
| **2** | Vendors + manufacturers + lifecycle | Phase2_ManufacturersVendorsLifecycle + Part_LifecycleHistory | manufacturers, vendor_parts, part_lifecycle_events | ADR-0002, 0013 |
| **3** | Pricing | Pricing_History + Pricing_Silo | price_history | ADR-0002, 0005 |
| **4** | Inventory + stock | Phase3and4_VendorPartsAndInventory + Receive_Pipeline | part_inventory, stock_locations, receipts, receipt_lines | ADR-0002, 0026 |
| **5** | Cloud Run + Cloud SQL + auth | (deferred; not yet started) | — | ADR-0002, 0012 |

### By ADR (Data-Shape Governance)

| ADR | Title | Scope | Migrations | Status |
|---|---|---|---|---|
| **0013** | Soft-delete on part | Soft-delete infrastructure stub; deferred implementation | Part_LifecycleHistory (deferred to parts) | Proposed (partial: only bom_lines) |
| **0014** | PartCategory expansion | Add PartCategory rows (Breaker, Contactor, MotorProtector, …); feel_schema structure | Category_LookupTable, Category_AuxContactRow, AddPartCategoryExpansionAdr0014 | Approved |
| **0015** | PartCriteria expansion | PartCriteria column shape expansion (reserved, unused in phase 1) | (implicit in Part_FeelColumn via feel) | Approved |
| **0017** | PartCriteria per-category typed | Typology: feel_schema on PartCategory governs criteria shape per category | Part_FeelColumn, Category_LookupTable, Category_AuxContactRow | Approved |
| **0020** | BOM relational lift | BOM as relational table (bom_lines) with soft-delete + supersession | Bom_RelationalLift | Approved |
| **0024** | Project FK slot expansion | Add end_customer_party_id + contractor_party_id to projects | 0024_ProjectFkSlotExpansion | Approved |
| **0033** | Path D vendor data cleanup | Migrate public.vendors → procurement.vendors; drop legacy tables + FK | PathD_VendorDataCleanup | Approved |
| **0034** | Part enrichment sidecar | 1:1 sidecar to parts for machine-authored metadata (images) | Part_EnrichmentSidecar | Approved |

---

## ADR Governance Matrix

| ADR | Category | Status | Scope | Schema Touches | Key Constraint |
|---|---|---|---|---|---|
| **0002** | Phased rollout | Approved | Five-phase ERP rollout roadmap | All (by phase) | Don't pre-bake schemas for later phases. |
| **0005** | Feel + enrichment | Approved | Jsonb feel schema + enrichment metadata | parts.feel, part_enrichments.* | Feel carries typed criteria; enrichment is machine-authored. |
| **0008** | Part profile + feel split | Approved | Profile columns separate from feel (criteria) | parts (ADD columns, ADD feel, DROP old criteria) | Feel is immutable domain record; profile is metadata. |
| **0013** | Soft-delete on part | Proposed | Soft-delete infrastructure | part_lifecycle_events (ready), bom_lines.deleted_at (live) | Deferred to phase 5+; only bom_lines implemented. |
| **0014** | PartCategory expansion | Approved | Seeded category rows + feel_schema | part_categories (INSERT rows + feel_schema) | Categories define typology; feel_schema defines criteria shape. |
| **0015** | PartCriteria expansion | Approved | PartCriteria column shape expansion | parts.feel (jsonb, shape varies by category) | Reserved; expansion is additive, not breaking. |
| **0016** | Data domain (eight silos) | Approved | Schema organization by silo + audit | ALL (schema assignment, FK bridges, NO cross-silo FKs except 4) | Single silo per table. Four FK-bridges to catalog.parts. String-ID refs elsewhere. |
| **0017** | PartCriteria per-category typed | Approved | Category-specific feel schema | part_categories.feel_schema, parts.feel | Each category has its own feel typology (Breaker, Contactor, etc.). |
| **0019** | Project metadata (customer PO) | Approved | Project estimate/PO metadata | projects (ADD estimate_number, customer_po_number, URLs, received_at) | Customer PO metadata is optional; project is still valid. |
| **0020** | BOM relational lift | Approved | BOM as relational table with soft-delete + supersession | bom_lines (new table, soft-delete on deleted_at, self-FK on supersedes_line_id) | XOR (part_id XOR criteria_snapshot). Soft-delete on active rows only. |
| **0024** | Project FK slot expansion | Approved | Add role-typed party slots to projects | projects (ADD end_customer_party_id, contractor_party_id) | Additive; no breaking changes. |
| **0026** | Receive parts pipeline | Approved | Goods receipt + line-item traceability | stock_locations, receipts, receipt_lines (new tables) | External_ref idempotency. Receipt lines map to catalog.parts + po_lines. |
| **0028** | Quotes + QBO write-through | Approved | Quote CRUD + QBO bidirectional sync | quotes (ADD QBO columns), quote_patch_idempotency (new table), payments (new table) | external_ref idempotency. qbo_sync_state enum. Address snapshots (jsonb). |
| **0030** | QBO pull integration (eight-silo decoupler) | Approved | QBO ID mapping isolated from business silos | integration schema + qbo_external_id_map (new table) | integration silo is orthogonal; no FKs out to business silos. |
| **0033** | Path D vendor data cleanup | Approved | Vendor data migration + legacy table removal | procurement schema (INSERT…SELECT), public.vendors/vendor_parts DROP, pricing.price_history FK-drop | One-way migration. Old tables are gone. String-ID in procurement.vendors. |
| **0034** | Part enrichment sidecar | Approved | Machine-authored enrichment (images) as 1:1 sidecar | part_enrichments (new 1:1 table to parts) | Cascade-delete on owner. image_urls is required (jsonb array default []). |

---

## Naming Conventions

- **Schemas:** lowercase (catalog, procurement, pricing, project, sales, identity, fab, audit, integration, public).
- **Tables:** lowercase, snake_case (parts, part_categories, purchase_orders, po_lines, stock_movements, etc.).
- **Columns:** lowercase, snake_case (part_number, category_id, on_hand, created_utc, last_fetched_at, etc.).
- **Indexes:** 
  - Standard: `ix_<table>_<columns>` (e.g., `ix_parts_part_number`, `ix_vendor_parts_part`).
  - Unique: `uq_<table>_<columns>` or implicit (e.g., `uq_bom_lines_panel_ordinal_active`).
  - Partial: suffix `_<descriptor>` (e.g., `ix_projects_billed_to_party`).
- **Constraints:**
  - PK: implicit `<table>_pkey` (Postgres default).
  - FK: implicit `fk_<from_table>_<to_table>_<column>` (Postgres default) or explicit in migration.
  - CHECK: `ck_<schema>_<table>_<constraint_name>` (e.g., `ck_project_bom_lines_qty`, `ck_sales_quotes_status`).
  - Unique: `uq_<schema>_<table>_<constraint_name>` (e.g., `uq_sales_quotes_external_ref`).

---

## Open & Proposed ADRs

| ADR | Title | Status | Impact | Notes |
|---|---|---|---|---|
| **0049** | PartCategory.FuseHolder add | Proposed | ADD new category (FuseHolder) with feel_schema + ranking spec | dCAD ADR-0032 driver; requires ADR-0017 erratum (MaxAmps to FuseHolderCriteria binding gap). |
| **0050** | Auto-classification engine (PartNumberPattern) | Proposed | PartNumberPattern table + synchronous classifier in ReceiptRepository.CreateAsync | Six seed patterns (HDL/HJL/EDB, 1SAM*, 100-C*, 193-*). Composes with ADR-0026 §4 unresolved-queue fallback. |
| **0051** | Database landscape snapshot | In progress | Permanent reference doc for dERP schema (this file). | Not a data-shape ADR; purely reference. |

---

## Constraints Verification

### Primary Keys
All tables have a single PK (either uuid auto-generated or composite key where noted):
- UUID tables: use `ValueGeneratedOnAdd` (Postgres gen_random_uuid(), Sqlite guid default).
- Composite PK: part_substitutes (part_id, substitute_part_id), part_inventory (part_id, location_id), quote_lines (quote_id, line_no), etc.
- Manual PK: part_categories.id (ValueGeneratedNever, seeded row IDs).

### Foreign Keys
Four FK-bridges to catalog.parts (all RESTRICT); intra-silo FKs (CASCADE or SET NULL per design); self-FKs (e.g., bom_lines.supersedes_line_id SET NULL).

### Unique Constraints
- part_number, part_categories.name, manufacturers.name/code
- Composite: (vendor_id, vendor_sku), (po_id, line_no), (receipt_id, line_no), (panel_id, line_ordinal, DELETE_FILTER)
- Partial: parts.code (WHERE code IS NOT NULL), external_ref columns (WHERE NOT NULL)

### Check Constraints
- Status enums (draft, sent, accepted, etc.) on quotes, projects, invoices, submittals, etc.
- qty > 0 on bom_lines.
- XOR (part_id XOR criteria_snapshot) on bom_lines.
- op enum on domain_event_log.
- role enum on party_addresses.
- qbo_sync_state enum on quotes.

### Append-Only Tables (Defense-in-Depth)
- **pricing.price_history:** BEFORE UPDATE / BEFORE DELETE triggers (Postgres); EF Core routes through insert-only paths.
- **catalog.part_lifecycle_events:** append-only by design; no update paths.
- **audit.domain_event_log:** append-only by design.

---

## Test & Seed Data

- `data/seed_db.py` initializes the database with seed data (manufacturers, categories, parts, vendors, pricing, etc.) for local dev.
- Seed script writes directly to Postgres (bypasses EF Core) — uses procurement.vendors, procurement.vendor_parts, pricing.price_history (not legacy public.* tables).
- Integration tests run against a local Postgres instance (docker compose up -d postgres).
- Sqlite-backed sandbox tests use EnsureCreated (no migration replay) so certain Postgres-only literals (gen_random_uuid(), now(), CHECK constraints with enums) are handled with CLR defaults or portable patterns.

---

## Known Issues & Open Work

| Issue | Scope | ADR / Branch | Status |
|---|---|---|---|
| Soft-delete on catalog.parts | Deferred; only bom_lines has soft-delete today. | ADR-0013 (proposed) | Deferred to phase 5+ |
| PoLineExtract + source_po_extract_id FK | pricing.price_history.source_po_extract_id FK reserved (column present, FK deferred). | Feature pFx3rqcvDOK7pByRznrE (proposed) | Blocked; PoLineExtract table not yet created. |
| FuseHolder category + MaxAmps binding gap | ADR-0049 lands category row; ADR-0017 erratum needed for PartCriteria binding. | ADR-0049 (proposed), ADR-0017 erratum | Proposed |
| dPART selector for FuseHolder | dPART needs its own ADR for FuseHolderSelector composition. | Out-of-scope (dPART repo) | Proposed follow-on |
| Legacy public.vendors foreign tables (Postgres) | Old public.vendors / public.vendor_parts were dropped by ADR-0033 migration; orphan status confirmed. | ADR-0033 (approved) | Done (PathD_VendorDataCleanup migration) |

---

## Cross-Repo Contracts

**dWEB (direct R/W consumer per ADR-0012):**
- API surface: Any change to write endpoints or admin-facing contracts affects dWEB immediately.
- Coordinate via dERP → dWEB cross-ref events.
- Key ADRs: 0028 (Quotes + QBO), 0020 (BOM lift), 0024 (Project party slots).

**dPART (read-only consumer per ADR-0012):**
- Selection logic depends on PartCriteria shape + feel_schema per category.
- Key ADRs: 0017 (per-category typed criteria), 0014 (category expansion), 0011 (motor protection selection).

**dCAD (upstream; drives requirements):**
- ADR-0032 (FuseHolder) drivers ADR-0049 (category add).
- Coordinate via VitalisCAD-Web/docs/ECOSYSTEM.md.

---

## Glossary & ADR Index

| ADR | Link | Title | Category | Status |
|---|---|---|---|---|
| 0001 | docs/decisions/0001-stack-and-hosting.md | Stack and hosting (Heroku → Cloud Run) | Architecture | Approved |
| 0002 | docs/decisions/0002-phased-erp-rollout.md | Phased ERP rollout (five phases) | Roadmap | Approved |
| 0003 | docs/decisions/0003-cloud-run-and-api-key.md | Cloud Run & API key | Infrastructure | Approved |
| 0004 | docs/decisions/0004-ul-listing-as-part-attribute.md | UL listing as part attribute | Catalog | Approved |
| 0005 | docs/decisions/0005-feel-and-enrichment-schema.md | Feel & enrichment schema | Catalog | Approved |
| 0006 | docs/decisions/0006-ul-data-backfill-source.md | UL data backfill source | Catalog | Approved |
| 0007 | docs/decisions/0007-ul-substitution-semantics.md | UL substitution semantics | Catalog | Approved |
| 0008 | docs/decisions/0008-part-profile-feel-criteria-split.md | Part profile ↔ feel ↔ criteria split | Catalog | Approved |
| 0009 | docs/decisions/0009-contactor-feel-schema.md | Contactor feel schema | Catalog | Approved |
| 0010 | docs/decisions/0010-overload-feel-schema.md | Overload feel schema | Catalog | Approved |
| 0011 | docs/decisions/0011-motor-protection-selection.md | Motor protection selection | Selection | Approved |
| 0012 | docs/decisions/0012-derp-headless-dual-consumer.md | dERP headless + dual consumer (dWEB, dPART) | Architecture | Approved |
| 0013 | docs/decisions/0013-soft-delete-on-part.md | Soft-delete on part | Catalog | Proposed |
| 0014 | docs/decisions/0014-partcategory-expansion.md | PartCategory expansion | Catalog | Approved |
| 0015 | docs/decisions/0015-partcriteria-expansion.md | PartCriteria expansion | Catalog | Approved |
| 0016 | docs/decisions/0016-derp-data-domain.md | dERP data domain (eight silos, bridges) | Architecture | Approved |
| 0017 | docs/decisions/0017-partcriteria-per-category-typed.md | PartCriteria per-category typed | Catalog | Approved |
| 0018 | docs/decisions/0018-partcategory-auxcontact-add.md | PartCategory aux contact add | Catalog | Approved |
| 0019 | docs/decisions/0019-project-metadata-customer-po.md | Project metadata (customer PO) | Project | Approved |
| 0020 | docs/decisions/0020-bom-relational-lift.md | BOM relational lift + soft-delete | Project | Approved |
| 0021 | docs/decisions/0021-customer-endpoint-surface.md | Customer endpoint surface | API | Approved |
| 0022 | docs/decisions/0022-project-write-surface.md | Project write surface | API | Approved |
| 0023 | docs/decisions/0023-purchase-order-read-surface.md | Purchase order read surface | API | Approved |
| 0024 | docs/decisions/0024-project-fk-slot-expansion.md | Project FK slot expansion (role-typed parties) | Project | Approved |
| 0025 | docs/decisions/0025-part-categories-api-surface.md | Part categories API surface | API | Approved |
| 0026 | docs/decisions/0026-receive-parts-pipeline.md | Receive parts pipeline | Procurement | Approved |
| 0027 | docs/decisions/0027-receive-parts-gap-fill.md | Receive parts gap fill | Procurement | Approved |
| 0028 | docs/decisions/0028-quotes-api-qbo-writethrough.md | Quotes API + QBO write-through | Sales | Approved |
| 0029 | docs/decisions/0029-project-read-write-surface.md | Project read/write surface | API | Approved |
| 0030 | docs/decisions/0030-quickbooks-pull-integration.md | QBO pull integration (eight-silo decoupler) | Integration | Approved |
| 0033 | docs/decisions/0033-path-d-vendor-data-cleanup.md | Path D vendor data cleanup | Procurement | Approved |
| 0034 | docs/decisions/0034-part-enrichment-sidecar.md | Part enrichment sidecar | Catalog | Approved |
| 0049 | docs/decisions/0049-partcategory-fuseholder-add.md | PartCategory.FuseHolder add | Catalog | Proposed |
| 0050 | docs/decisions/0050-auto-classification-po-ingest.md | Auto-classification engine (PartNumberPattern) | Procurement | Proposed |
| 0051 | docs/landscape/database-landscape.md | Database landscape snapshot | Reference | In progress |

---

## Quick Reference: Table Counts by Schema

| Schema | Table Count | Silo | Phases Covered |
|---|---|---|---|
| catalog | 9 | Catalog | 1–2, 0 |
| procurement | 8 | Procurement | 2, 0 |
| pricing | 1 | Pricing | 3 |
| project | 3 | Project | 4–5, 0 |
| sales | 8 | Sales | 0 (ADR-0028) |
| identity | 3 | Identity | 0 (Wave 2) |
| fab | 3 | Fab | 0 (Wave 4) |
| audit | 1 | Audit | 0 (Wave 2 onward) |
| integration | 1 | Integration | 0 (ADR-0030) |
| public | 4 | Legacy | 1–3 |

**Total: 41 tables** across 10 schemas (9 business + 1 legacy).

---

**Last updated:** 2026-05-23 (migration PathD_VendorDataCleanup, commit cd411fb).
