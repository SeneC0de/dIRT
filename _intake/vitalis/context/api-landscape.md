# dERP API Landscape

**Current state snapshot:** May 2026 | ADR-0051 input document | dERP headless architecture per ADR-0012

## What is dERP

dERP is the authoritative source for **parts catalog, vendor data, pricing, and inventory** in the dApp Controls ecosystem. It is a **headless, HTTP-only API** serving two direct consumers:

| Consumer | Role | Access | Implementation |
|---|---|---|---|
| **dPART** | Automated part selection from stock based on criteria (amps, voltage, poles, etc.) | Read-only | Calls catalog + selection endpoints; no mutation |
| **dWEB** | Human interface to the ERP — create parts, edit vendors, manage pricing, review inventory | Read/write | Full CRUD; all admin pages live here (dERP.Admin retired per ADR-0012) |

**Architecture rule (CLAUDE.md §1):** The HTTP boundary is real. Even locally, consumers go through `dERP.Client` → HTTP → `dERP.Api`. No embedded data layer. On Cloud Run (Phase 5), this becomes a deployment detail, not a rewrite.

### Tech Stack
- **.NET 8** | ASP.NET Core 8 minimal API (`dERP.Api`)
- **EF Core 8** + **Npgsql** + **PostgreSQL 16**
- **Deployment:** Google Cloud Run (`derp-api`) + Cloud SQL for Postgres (`derp-db`)
- **Local dev:** Postgres via `docker compose`

---

## Endpoint Inventory

All endpoints live on `dERP.Api` with base path `/api` (plus two non-`/api` QBO OAuth endpoints noted below). Minimal API groups by domain area.

### Health & System (no auth required)

| Endpoint | HTTP | Purpose | Request | Response | Phase | ADR | Source |
|---|---|---|---|---|---|---|---|
| `/health` | GET | Liveness probe | — | `{"status":"ok"}` | v1 | — | HealthEndpoints.cs:11 |
| `/ready` | GET | Readiness check (tests DB connectivity) | — | `{"status":"ok"}` + 503 on DB fail | v1 | — | HealthEndpoints.cs:13 |

### Parts (Catalog)

**Group:** `/api/parts` | **Tag:** `Parts` | **Auth:** `X-Api-Key` | **Phase 1** | **ADR:** 0004 (UL), 0008 (profile split), 0002 (phased)

| Endpoint | HTTP | Purpose | Request DTO | Response DTO | Notes | Source |
|---|---|---|---|---|---|---|
| `/api/parts` | GET | Paged list, optional category filter | Query: `categoryId`, `category`, `page`, `pageSize` | `PagedResponse<PartDto>` | Filters via FK (`categoryId`) or name shim (`category`); search index via pg_trgm | PartsEndpoints.cs:31 |
| `/api/parts/search` | GET | Trigram similarity search by part_number + description | Query: `q` (min 2 chars), `minSimilarity` (0–1, def 0.3), pagination | `PagedResponse<PartDto>` | Index-backed GIN search; page size default 20 (not 50) | PartsEndpoints.cs:76 |
| `/api/parts/{id:guid}` | GET | Fetch single part with profile | Path: `{id}` | `PartDto` (with profile) | Returns 404 if not found | PartsEndpoints.cs:112 |
| `/api/parts/by-number/{partNumber}` | GET | Fetch by human-readable part number | Path: `{partNumber}` | `PartDto` (with profile) | Natural-key lookup; 404 if not found | PartsEndpoints.cs:128 |
| `/api/parts` | POST | Create new part | `CreatePartRequestDto` | `PartDto` (201 Created) | Includes optional `Profile` (FEEL/selection criteria); returns 201 w/ Location header | PartsEndpoints.cs:144 |
| `/api/parts/{id:guid}` | PUT | Update part + profile | Path: `{id}` | Request: `UpdatePartRequestDto` | 204 No Content on success; 404 if not found; validates Profile | PartsEndpoints.cs:175 |
| `/api/parts/{id:guid}` | DELETE | Soft-delete part (ADR-0013) | Path: `{id}` | 204 No Content | Mark deleted; preserve FK integrity | PartsEndpoints.cs:199 |
| `/api/parts/import` | POST | Bulk CSV ingest | Multipart form-data (single file, any field name) | `PartsCsvImportResult` on success; errors on 400 | Strict validation-first; idempotent by merge logic; see parts-csv-import-schema-v1 docs | PartsEndpoints.cs:224 |
| `/api/parts/select` | POST | Part selection engine (pure logic, no DB state change) | `PartSelectionRequestDto` | `PartSelectionResultDto` | Calls `IPartSelector` (dERP.Selection, no EF, pure); takes `PartCriteria` → returns best match | PartsEndpoints.cs:259 |

#### Part Contracts & Key Classes
- **Core record:** `dERP.Core.Parts.Part` (immutable domain record)
- **Wire DTO:** `PartDto` + `PartProfileDto` (dERP.Client.Contracts)
- **Request DTOs:** `CreatePartRequestDto`, `UpdatePartRequestDto`, `PartSelectionRequestDto`
- **Profiles:** FEEL (motor/aux contact criteria) split per ADR-0008; stored in `parts.part_profile` JSON column
- **Mapping:** `PartContractMapper` in dERP.Api.Mapping

#### Part Categories

**Endpoint group:** `/api/part-categories` | **Auth:** `X-Api-Key` | **Phase 1** | **ADR:** 0025 (FK surface), 0018 (aux contact add), 0014 (expansion)

| Endpoint | HTTP | Purpose | Request | Response | Notes | Source |
|---|---|---|---|---|---|---|
| `/api/part-categories` | GET | Enumerate all categories + active flag | Query: `activeOnly` (bool) | `List<PartCategoryDto>` | No pagination (~30 rows seeded); used by dropdown filters | PartCategoriesEndpoints.cs:15 |

---

### Vendors & Manufacturers

#### Manufacturers

**Group:** `/api/manufacturers` | **Auth:** `X-Api-Key` | **Phase 2** | **ADR:** 0002 (phased)

| Endpoint | HTTP | Purpose | Request | Response | Phase | Source |
|---|---|---|---|---|---|---|
| `/api/manufacturers` | GET | Paged list | Query: `activeOnly` (bool), pagination | `PagedResponse<ManufacturerDto>` | 2 | ManufacturersEndpoints.cs:15 |
| `/api/manufacturers/{id:guid}` | GET | Single manufacturer | Path: `{id}` | `ManufacturerDto` | 2 | ManufacturersEndpoints.cs:23 |
| `/api/manufacturers` | POST | Create | `CreateManufacturerRequestDto` | `ManufacturerDto` (201) | 2 | ManufacturersEndpoints.cs:31 |
| `/api/manufacturers/{id:guid}` | PUT | Update | Path: `{id}`, body: `UpdateManufacturerRequestDto` | 204 | 2 | ManufacturersEndpoints.cs:39 |
| `/api/manufacturers/{id:guid}` | DELETE | Soft-delete | Path: `{id}` | 204 | 2 | ManufacturersEndpoints.cs:47 |

#### Vendors (Procurement Schema)

**Group:** `/api/vendors` | **Auth:** `X-Api-Key` | **Phase 2** | **ADR:** 0033 (PathD schema cleanup), 0002 (phased)

After ADR-0033, vendors moved from `public.vendors` to `procurement.vendors`. `VendorEntity` / `VendorPartEntity` in public schema deleted; now use `ProcurementVendorEntity`.

| Endpoint | HTTP | Purpose | Request | Response | Notes | Source |
|---|---|---|---|---|---|---|
| `/api/vendors` | GET | Paged list | Query: `activeOnly` (bool), pagination | `PagedResponse<VendorDto>` | Backed by `procurement.vendors` | VendorsEndpoints.cs:15 |
| `/api/vendors/{id:guid}` | GET | Single vendor | Path: `{id}` | `VendorDto` | 404 if not found | VendorsEndpoints.cs:27 |
| `/api/vendors` | POST | Create | `CreateVendorRequestDto` | `VendorDto` (201) | 201 w/ Location header | VendorsEndpoints.cs:33 |
| `/api/vendors/{id:guid}` | PUT | Update | Path: `{id}`, body: `UpdateVendorRequestDto` | 204 | 404 if not found | VendorsEndpoints.cs:43 |
| `/api/vendors/{id:guid}` | DELETE | Soft-delete | Path: `{id}` | 204 | 404 if not found | VendorsEndpoints.cs:56 |

#### Vendor Parts (Catalog Cross-References)

**Route:** `/api/vendor-parts` (and `/api/parts/{partId:guid}/vendor-parts`) | **Auth:** `X-Api-Key` | **Phase 2** | **ADR:** 0033

| Endpoint | HTTP | Purpose | Request | Response | Notes | Source |
|---|---|---|---|---|---|---|
| `/api/vendor-parts` | GET | Paged list | Query: `activeOnly`, pagination | `PagedResponse<VendorPartDto>` | 404 if not found | VendorPartsEndpoints.cs:15 |
| `/api/vendor-parts/{id:guid}` | GET | Single vendor-part record | Path: `{id}` | `VendorPartDto` | Junction record (part ↔ vendor) | VendorPartsEndpoints.cs:27 |
| `/api/vendor-parts` | POST | Create | `CreateVendorPartRequestDto` | `VendorPartDto` (201) | Links part to vendor's offering | VendorPartsEndpoints.cs:34 |
| `/api/vendor-parts/{id:guid}` | PUT | Update | Path: `{id}`, body: `UpdateVendorPartRequestDto` | 204 | 404 if not found | VendorPartsEndpoints.cs:43 |
| `/api/vendor-parts/{id:guid}` | DELETE | Soft-delete | Path: `{id}` | 204 | 404 if not found | VendorPartsEndpoints.cs:56 |
| `/api/parts/{partId:guid}/vendor-parts` | GET | Vendor offerings for a specific part | Path: `{partId}` | `List<VendorPartDto>` | Convenience route; no pagination | VendorPartsEndpoints.cs:67 |

---

### Pricing

**Group:** `/api/parts/{partId:guid}/price-history` | **Auth:** `X-Api-Key` | **Phase 3** | **ADR:** 0002 (phased), 0033 (PathD cleanup)

After ADR-0033, price history points to `procurement.vendors` (not `public.vendors`). Pricing records observational history (cost per vendor over time).

| Endpoint | HTTP | Purpose | Request | Response | Notes | Source |
|---|---|---|---|---|---|---|
| `/api/parts/{partId:guid}/price-history` | GET | Price observations for a part across vendors | Path: `{partId}` | `List<PriceHistoryEntryDto>` | Read-only; ordered by vendor, then date descending | PriceHistoryEndpoints.cs:10 |

---

### Inventory & Stock

**Routes:** `/api/parts/{partId:guid}/inventory`, `/api/inventory/below-reorder-point` | **Auth:** `X-Api-Key` | **Phase 4** | **ADR:** 0002 (phased)

| Endpoint | HTTP | Purpose | Request | Response | Phase | Source |
|---|---|---|---|---|---|---|
| `/api/parts/{partId:guid}/inventory` | GET | On-hand counts by location for a part | Path: `{partId}` | `PartInventoryDto` | 4 | InventoryEndpoints.cs:8 |
| `/api/parts/{partId:guid}/inventory` | PUT | Update part inventory (qty + lead time + reorder point) | Path: `{partId}`, body: inventory update | 204 | 4 | InventoryEndpoints.cs:32 |
| `/api/inventory/below-reorder-point` | GET | Parts across all locations where on_hand < reorder_point | Query: pagination | `PagedResponse<PartInventoryDto>` | Alert endpoint for ops; no filter by location | InventoryEndpoints.cs:56 |

---

### Lifecycle History

**Route:** `/api/parts/{partId:guid}/lifecycle-history` | **Auth:** `X-Api-Key` | **Phase 2** | **ADR:** 0002 (phased)

| Endpoint | HTTP | Purpose | Request | Response | Notes | Source |
|---|---|---|---|---|---|---|
| `/api/parts/{partId:guid}/lifecycle-history` | GET | Event log of part status changes (active → NRND → obsolete) | Path: `{partId}` | `List<PartLifecycleEventDto>` | Audit trail; read-only | LifecycleHistoryEndpoints.cs:10 |

---

### Locations (Inventory Storage)

**Route:** `/api/locations` | **Auth:** `X-Api-Key` | **Phase 4** | **ADR:** 0002 (phased), 0026 (receive pipeline)

| Endpoint | HTTP | Purpose | Request | Response | Notes | Source |
|---|---|---|---|---|---|---|
| `/api/locations` | GET | Enumerate all warehouse locations | Query: pagination (optional) | `List<LocationDto>` | No filtering; small cardinality (~10–20 locations) | LocationEndpoints.cs:10 |

---

### Parties (End Customers, Vendors, Manufacturers)

**Group:** `/api/parties` | **Auth:** `X-Api-Key` | **Phase 1** | **ADR:** 0021 (customer surface)

Unified party table for vendors, customers, manufacturers — distinguished by `is_vendor`, `is_customer`, `is_manufacturer` flags.

| Endpoint | HTTP | Purpose | Request | Response | Notes | Source |
|---|---|---|---|---|---|---|
| `/api/parties` | GET | Paged list, filterable by type | Query: `vendorOnly`, `customerOnly`, pagination | `PagedResponse<PartyDto>` | Can combine filters (AND logic) | PartiesEndpoints.cs:15 |
| `/api/parties/{id:guid}` | GET | Single party | Path: `{id}` | `PartyDto` (with nested addresses, contacts) | 404 if not found | PartiesEndpoints.cs:29 |
| `/api/parties/{id:guid}/addresses` | GET | Mailing addresses for a party | Path: `{id}` | `List<PartyAddressDto>` | No pagination | PartiesEndpoints.cs:46 |
| `/api/parties/{id:guid}/contacts` | GET | Contact records (email, phone) for a party | Path: `{id}` | `List<PartyContactDto>` | No pagination | PartiesEndpoints.cs:62 |
| `/api/parties` | POST | Create new party | `CreatePartyRequest` | `PartyDto` (201) | Must specify role flags (vendor, customer, mfg) | PartiesEndpoints.cs:78 |

#### End Customers (Specialty)

**Route:** `/api/customers` | **Auth:** `X-Api-Key` | **Phase 1** | **ADR:** 0021

Convenience endpoint; equivalent to `GET /api/parties?customerOnly=true`.

| Endpoint | HTTP | Purpose | Request | Response | Source |
|---|---|---|---|---|---|
| `/api/customers` | GET | List all parties with `is_customer=true` | Query: pagination | `PagedResponse<PartyDto>` | Shorthand for `?customerOnly=true` | EndCustomersEndpoints.cs:15 |

---

### Projects (BOM + Quoting)

**Group:** `/api/project/projects` | **Auth:** `X-Api-Key` | **Phase 1** | **ADR:** 0019 (metadata + Drive URL), 0022 (write surface), 0029 (read/write expansion)

Projects group electrical panels (BOM context) for customers. Code format: `E` + 4–5 digits (e.g., `E1234`, `E12345`).

| Endpoint | HTTP | Purpose | Request | Response | Notes | Phase | Source |
|---|---|---|---|---|---|---|---|
| `/api/project/projects` | GET | List projects, filterable by status | Query: `status` (open/all/other), Drive URL deriver applied | `List<ProjectDto>` | Default: `open` status; includes panel_count computed inline | 1 | ProjectsEndpoints.cs:51 |
| `/api/project/projects/{eNumber}` | GET | Fetch single project by natural key (code) | Path: `{eNumber}` (e.g., E1234) | `ProjectDto` (full) | Drive URL resolution applied per ADR-0019 §3 | 1 | ProjectsEndpoints.cs:102 |
| `/api/project/projects/{eNumber}/full` | GET | Full detail (includes all nested BOM lines, customer PO attachments) | Path: `{eNumber}` | `ProjectDto` with expanded panels + lines | Detail shape; ADR-0019 §5 | 1 | ProjectsEndpoints.cs:119 |
| `/api/project/projects` | POST | Create new project | `CreateProjectRequest` (code, customer_party_id, status, Drive URL override) | `ProjectDto` (201) | Requires `X-Actor-Email` header (ADR-0019 §2.3) | 1 | ProjectsEndpoints.cs:145 |
| `/api/project/projects/{eNumber}` | PATCH | Sparse update (status, customer_party_id, Drive URL override, metadata) | Path: `{eNumber}`, body: `PatchProjectRequest` | 204 | Requires `X-Actor-Email` (audit columns). Never updates code. | 1 | ProjectsEndpoints.cs:190 |

#### Bill of Materials (BOM) Lines

**Group:** `/api/project/projects/{eNumber}/panels/{panelId:guid}/lines` | **Auth:** `X-Api-Key` | **Phase 1** | **ADR:** 0020 (relational lift)

| Endpoint | HTTP | Purpose | Request | Response | Notes | Source |
|---|---|---|---|---|---|---|
| `/api/project/projects/{eNumber}/panels/{panelId:guid}/lines` | GET | List BOM lines for a panel | Path: eNumber + panelId | `List<BomLineDto>` | No pagination | BomLinesEndpoints.cs:15 |
| `/api/project/projects/{eNumber}/panels/{panelId:guid}/lines` | POST | Create BOM line (add part to panel) | `CreateBomLineRequest` (part_id, qty, notes) | `BomLineDto` (201) | Requires `X-Actor-Email` | BomLinesEndpoints.cs:36 |
| `/api/project/projects/{eNumber}/panels/{panelId:guid}/lines/{lineId:guid}` | DELETE | Remove BOM line from panel | Path: eNumber, panelId, lineId | 204 | Soft-delete; preserves audit trail | BomLinesEndpoints.cs:68 |
| `/api/project/projects/{eNumber}/panels/{panelId:guid}/lines` | PATCH | Bulk update (swap parts, adjust qty) | Path: eNumber, panelId | `List<BomLineDto>` | Idempotent; Requires `X-Actor-Email` | BomLinesEndpoints.cs:87 |

---

### Purchase Orders & Receipts

#### Purchase Orders (Read-Only)

**Group:** `/api/purchase-orders` | **Auth:** `X-Api-Key` | **Phase 3** | **ADR:** 0023 (read surface)

Customers emit POs; dERP reads them for inventory planning + receipt matching.

| Endpoint | HTTP | Purpose | Request | Response | Notes | Source |
|---|---|---|---|---|---|---|
| `/api/purchase-orders` | GET | List POs, filterable by unassigned + customer | Query: `unassigned` (bool), `customerPartyId`, pagination (def 25, max 200) | `PagedResponse<PoSummaryDto>` | Summary shape (8 fields per ADR-0023 §2.4); detail shape is future | PurchaseOrdersEndpoints.cs:49 |
| `/api/purchase-orders/{id:guid}` | GET | Single PO | Path: `{id}` | `PoSummaryDto` | 404 if not found; same summary shape as list | PurchaseOrdersEndpoints.cs:86 |

#### Receipts (Receive Parts Pipeline)

**Group:** `/api/receipts` | **Auth:** `X-Api-Key` + `X-Actor-Email` (writes) | **Phase 3** | **ADR:** 0026 (receive pipeline), 0027 (gap fill)

Atomic receive pipeline: on arrival, create Receipt record, post inventory transactions, mark lines resolved (ADR-0026 §3).

| Endpoint | HTTP | Purpose | Request | Response | Notes | Source |
|---|---|---|---|---|---|---|
| `/api/receipts` | POST | Create receipt + lines (atomic); idempotent by ExternalRef | `CreateReceiptRequest` (vendor_id, po_id, location_id, lines[]) | `ReceiptDto` (201); 200 on ExternalRef replay | Requires `X-Actor-Email` header; ReceivedAt defaults to now | ReceiptEndpoints.cs:33 |
| `/api/receipts/{id:guid}` | GET | Single receipt with all lines | Path: `{id}` | `ReceiptDto` | 404 if not found | ReceiptEndpoints.cs:79 |
| `/api/receipts` | GET | Filtered list (vendor, date range, unresolved lines) | Query: `vendorId`, `from`, `to`, `unresolved=true`, pagination | `PagedResponse<ReceiptDto>` | Convenience for dWEB receipt search | ReceiptEndpoints.cs:96 |
| `/api/receipts/{id:guid}/lines/{lineId:guid}/resolve` | POST | Mark a receipt line as resolved (inventory posted) | Path: id + lineId | 204; 200 on idempotent replay | Idempotent; once resolved, line won't re-post inventory | ReceiptEndpoints.cs:120 |

#### PO-Scoped Receipts (Gap Fill)

**Routes:** `/api/po/{poId:guid}/receipts` | **Auth:** `X-Api-Key` | **Phase 3** | **ADR:** 0027 (gap fill)

Convenience endpoints to group receipts by PO (dWEB's PO detail page uses these).

| Endpoint | HTTP | Purpose | Request | Response | Notes | Source |
|---|---|---|---|---|---|---|
| `/api/po/{poId:guid}/receipts` | POST | Create receipt within a specific PO context | Path: `{poId}`, body: `CreatePoReceiptRequest` | `PoReceiptDto` (201) | Auto-links to PO; shorthand for POST /receipts + setting po_id | PoReceiptsEndpoints.cs:33 |
| `/api/po/{poId:guid}/receipts` | GET | Receipts for a single PO | Path: `{poId}`, pagination | `PagedResponse<PoReceiptDto>` | Filtered by po_id; no other filters | PoReceiptsEndpoints.cs:60 |

---

### Quotes & Sales

**Group:** `/api/quotes` | **Auth:** `X-Api-Key` (all) + `X-Actor-Email` (POST/PATCH) | **Phase 3** | **ADR:** 0028 (QBO write-through), 0029 (read/write expansion)

Quotes are estimates sent to customers for approval. Created here, synced to QuickBooks (with retry queue on 5xx). On acceptance, creates a Project record.

| Endpoint | HTTP | Purpose | Request | Response | Status Codes | Notes | Source |
|---|---|---|---|---|---|---|---|
| `/api/quotes` | POST | Create quote + lines, QBO write-through | `CreateQuoteRequest` (customer_party_id, external_ref, lines[]) | `QuoteDto` (201) with qbo_sync_state | 201 (created + QBO OK); 202 (created, QBO 5xx pending); 207 (created, QBO 4xx fail); 200 (ExternalRef replay) | Atomic Postgres tx: quote_number = next, INSERT, call IQboEstimateGateway. Requires `X-Actor-Email`. | QuoteEndpoints.cs:44 |
| `/api/quotes/{eNumber}` | GET | Fetch quote by natural key (quote_number, e.g., `E1234-1`) | Path: `{eNumber}` | `QuoteDto` | 404 if not found | eNumber format: `E<project>-<seq>` (e.g., E1234-1) | QuoteEndpoints.cs:176 |
| `/api/quotes/{eNumber}` | PATCH | Sparse update (customer, line qty/price, notes, QBO-propagated fields) | Path: `{eNumber}`, body: patch dict | 204 | 404 if not found | Requires `X-Actor-Email`. Updates QBO if qbo_sync_state is not 'failed'. | QuoteEndpoints.cs:229 |
| `/api/quotes/{eNumber}/accept` | POST | Accept quote (move to Accepted state, create Project record) | Path: `{eNumber}` | `QuoteDto` (with Project link) | 200 OK; 400 if quote not in Quotable state; 404 if not found | Idempotent; replayed accept returns existing Project. Requires `X-Actor-Email`. | QuoteEndpoints.cs:301 |

**Quote Sync States (per ADR-0028 §4.4):**
- `pending`: Created; awaiting first QBO sync attempt.
- `synced`: Successfully pushed to QBO.
- `pending_retry`: QBO 5xx on initial attempt; retry queued.
- `failed`: QBO 4xx (client error); no retry.

---

### QuickBooks Integration

#### QBO Pull (On-Demand Sync)

**Route:** `/api/qbo/pull/{entity}/{qboId}` | **Auth:** `X-Api-Key` | **Phase 0 (experimental)** | **ADR:** 0030 §2 (pull integration substrate)

On-demand refresh: fetch a specific QBO entity (Customer, Estimate, Bill) and merge into dERP.

| Endpoint | HTTP | Purpose | Request | Response | Config | Source |
|---|---|---|---|---|---|---|
| `/api/qbo/pull/{entity}/{qboId}` | POST | Fetch and merge a QBO entity | Path: `{entity}` (Customer/Estimate/Bill), `{qboId}` | Sync result (merged record summary) | Requires `Qbo:Pull:RealmId` env var (sandbox only per OQ-1) | QboPullEndpoints.cs:26 |

#### QBO OAuth (Non-API Auth Flow)

**Routes:** `/qbo/auth/connect`, `/qbo/auth/callback` | **Auth:** none (browser flow) | **Phase 5 (roadmap)** | **ADR:** 0029 (OAuth placeholder)

Outside `/api/*` — no API key required. Browser-based OAuth 2.0 consent flow (production path per ADR-0029).

| Endpoint | HTTP | Purpose | Notes | Source |
|---|---|---|---|---|
| `/qbo/auth/connect` | GET | Initiate OAuth consent | Returns redirect to QBO login | QboAuthEndpoints.cs |
| `/qbo/auth/callback` | GET | OAuth callback handler | Stores access token; redirects to dWEB | QboAuthEndpoints.cs |

**Current state (ADR-0029):** Sandbox token in config; production OAuth is a future story. See TODO(ADR-0029-OAuth) comments in codebase.

---

## Contracts & Versioning

### Namespaces

| Assembly | Namespace | Purpose | Versioning |
|---|---|---|---|
| `dERP.Client` | `dERP.Client.Contracts` | Wire DTOs (shared across dPART + dWEB) | No explicit versioning; breaking changes require coordinated rollout |
| `dERP.Api` | `dERP.Api.Contracts` | Internal API contracts (mappers, request DTOs, responses) | Internal; evolves with endpoints |
| `dERP.Core` | `dERP.Core.*` | Immutable domain records (Parts, Vendors, etc.) | Internal; never exposed on wire |
| `dERP.Data` | `dERP.Data.*` | EF entities + migrations | Internal; schema controls migrations |

### Versioning Strategy

**Current:** No explicit API versioning (v1 in Swagger title only). **All consumers on same version.**

- Wire format breaking changes → must be coordinated cross-repo (dERP ↔ dPART ↔ dWEB).
- `PartCriteria`, `PartCategory` taxonomy, `PartDto` shape — **any change affects dPART selection logic.** See cross-repo doc: `../VitalisCAD-Web/docs/ECOSYSTEM.md`.
- Contract bumps are not unilateral; flag via ADR + cross-ref to downstream consumers.

### Key DTO Classes

**All in `dERP.Client.Contracts`:**

| DTO | Purpose | Immutable | Consumers |
|---|---|---|---|
| `PartDto` | Part catalog entry (id, number, description, mfg, status, profile) | Yes | dPART (read), dWEB (read) |
| `PartProfileDto` | Selection criteria (FEEL: overload, starting method, UL profile, contractor feel, etc.) | Yes | dPART (read), dWEB (read/write) |
| `VendorDto`, `VendorPartDto` | Vendor + vendor's offering (part cross-reference) | Yes | dWEB (read/write), dPART (read) |
| `PriceHistoryEntryDto` | Cost observation (vendor, date, unit_cost_cents) | Yes | dWEB (read) |
| `PartInventoryDto` | On-hand by location, lead time, reorder point | Yes | dWEB (read/write), planning (read) |
| `PartyDto` | Party record (vendor/customer/mfg) with nested addresses + contacts | Yes | dWEB (read/write), dPART (read) |
| `ProjectDto` | BOM context (code, customer, status, Drive URL, panels) | Yes | dWEB (read/write), dCAD (read via dPART) |
| `BomLineDto` | Part + qty on a panel | Yes | dWEB (read/write), dCAD (read) |
| `QuoteDto` | Estimate (quote_number, lines, customer, qbo_sync_state, project link) | Yes | dWEB (read/write), QBO (write) |
| `PoSummaryDto` | PO snapshot (8 summary fields; detail shape TBD) | Yes | dWEB (read) |
| `ReceiptDto` | Receipt + lines (arrival log) | Yes | dWEB (read/write) |
| `PagedResponse<T>` | Envelope for list endpoints (items, page, pageSize, total) | — | All list consumers |

---

## Authentication & Authorization

### Current Auth Surface (Phase 5 Placeholder)

| Mechanism | Applies To | Status | ADR |
|---|---|---|---|
| `X-Api-Key` header | **All** endpoints (required) | Implemented | 0003 (API key + Cloud Run) |
| `X-Actor-Email` header | Write endpoints (POST/PATCH/DELETE) + quotes + receipts + projects | Implemented (for audit) | 0019 §2.3 (project audit), 0026 §3 (receipt audit), 0028 §7 (quote audit) |
| `X-Correlation-Id` | All endpoints (optional; auto-generated if absent) | Implemented | — |
| Google Identity-Aware Proxy (IAP) | Future; Phase 5 deployment | Roadmap | 0003 (Cloud Run auth path) |

### Per-Caller Identity

**Current:** All authenticated requesters (dPART + dWEB) seen as equivalent. No role-based authorization yet.

- `PartCriteria` carries optional `ContractorId` slot (ADR-0015 §5) but **not used in matching** — stubbed for future contractor-aware selection.
- Write operations audit the `X-Actor-Email` for compliance, not access control.

**Roadmap (ADR-0003 future):** Identity-aware routing (e.g., dPART gets read-only; dWEB gets full access) via middleware or Claims principal.

---

## Phase Rollout Status

**Current state:** Phases 1–4 endpoints live. Phase 5 (deployment) is infrastructure.

| Phase | Focus | Endpoints | Status | ADR |
|---|---|---|---|---|
| **1** | Parts catalog + selection + BOM + projects + quoting | `/api/parts/*`, `/api/part-categories/*`, `/api/project/*`, `/api/quotes/*` | ✓ Live | 0002, 0008, 0020, 0028 |
| **2** | Vendors/manufacturers + lifecycle status | `/api/vendors/*`, `/api/manufacturers/*`, `/api/parties/*`, lifecycle history | ✓ Live | 0002, 0033 |
| **3** | Pricing + PO + receipts | `/api/parts/{id}/price-history`, `/api/purchase-orders/*`, `/api/receipts/*` | ✓ Live | 0002, 0023, 0026, 0027 |
| **4** | Inventory / stock | `/api/parts/{id}/inventory`, `/api/inventory/below-reorder-point`, `/api/locations` | ✓ Live | 0002 |
| **5** | Cloud Run + Cloud SQL + auth (IAP) | Deployment infra | 🔄 Roadmap | 0003, 0012 |

---

## Open ADRs (Proposed / Under Review)

| ADR | Title | Status | Consumer Impact | Link |
|---|---|---|---|---|
| 0034 | Part Enrichment Sidecar | Accepted | New `/api/parts/{id}/enrichment` read + write + refresh endpoints | `docs/decisions/0034-part-enrichment-sidecar.md` |
| 0035 | QBO Server-Side Bill Ingestion | Draft | New bill ingest endpoint + sync state tracking | Draft |
| 0041 | Vendor Quote PDF Generation | Draft | New quote PDF retrieval endpoint | Draft |
| 0050 | Auto-Classification Engine (PartNumberPattern) | Draft | PO line item auto-matching to parts | Draft |

---

## Cross-Repo Touchpoints

### dWEB (Direct R/W Consumer)

dWEB directly consumes `dERP.Client` over HTTP. All admin pages (create part, edit vendor, manage pricing, review inventory) live in dWEB, not dERP.

**ADR-0012 consequence:** dWEB has the dERP API key as a secret. Changes to write endpoints directly affect dWEB's forms.

**Cross-repo docs:** `../VitalisCAD-Web/docs/ECOSYSTEM.md`

### dPART (Read-Only Automated Consumer)

dPART calls dERP selection endpoints (`POST /api/parts/select`) + catalog reads to pick the right part based on motor criteria (amps, voltage, poles, etc.).

**ADR-0015 consequence:** Any change to `PartCriteria` shape or `PartCategory` taxonomy requires coordinated rollout.

### dCAD (Indirect Consumer via dPART)

dCAD never reaches dERP directly. dPART intermediates: dCAD sends criteria → dPART selects → returns part. dERP is transparent to dCAD.

---

## Quick Reference: Endpoint Filing

### By HTTP Verb

| Verb | Typical Use | Count |
|---|---|---|
| **GET** | Fetch (single or list), search | ~30 |
| **POST** | Create, select, ingest, sync | ~15 |
| **PUT** | Full replace | ~10 |
| **PATCH** | Sparse update | ~5 |
| **DELETE** | Soft-delete | ~10 |

### By Auth Header

| Header | Required? | Endpoints |
|---|---|---|
| `X-Api-Key` | **Always** (except `/health`, `/ready`) | All `/api/*` |
| `X-Actor-Email` | **Writes** (POST/PUT/PATCH/DELETE on projects, quotes, receipts) + some reads | Projects, quotes, receipts, BOM |
| `X-Correlation-Id` | Optional (auto-generated) | All endpoints |

### By Pagination

| Behavior | Endpoint Group | Defaults | Cap |
|---|---|---|---|
| **Paged list** (v2 surface) | Parts, vendors, manufacturers, POs, receipts, quotes | page=1, pageSize=25–50 | 200–500 |
| **Unpaged list** | Categories, locations, vendor-parts, lifecycle history | — | ~30–50 rows max |
| **No list** | Single-fetch by ID | — | N/A |

---

## Schema & Migrations

Migrations live in `src/dERP.Data/Migrations/` (checked into source). Never edit an applied migration; add a new one instead.

**Key tables (after Phase 4 + ADR-0033):**
- `parts.parts` (catalog)
- `parts.part_categories` (taxonomy)
- `parts.manufacturers` (legacy but retained)
- `procurement.vendors` (moved from public per ADR-0033)
- `procurement.vendor_parts` (cross-reference)
- `procurement.purchase_orders` (customer POs)
- `procurement.receipts`, `procurement.receipt_lines` (inbound)
- `pricing.price_history` (cost observations)
- `project.projects`, `project.panels`, `project.bom_lines` (BOM context)
- `sales.quotes`, `sales.quote_lines` (estimates)
- `parties.parties`, `parties.party_address`, `parties.party_contact` (unified party record)
- `inventory.on_hand` (stock counts by location)

See `docs/landscape/database-landscape.md` for detailed schema.

---

## Where to Read the Source

For any endpoint, the source file follows the pattern:

```
src/dERP.Api/Endpoints/<Domain>Endpoints.cs
```

**Example:** To read the parts `/select` endpoint logic, open:
- **File:** `src/dERP.Api/Endpoints/PartsEndpoints.cs`
- **Line:** ~259 (`group.MapPost("/select", ...)`)

**Mapping layer** (Core ↔ Wire DTO):
```
src/dERP.Api/Mapping/<Domain>ContractMapper.cs
```

**Request/response contracts:**
```
src/dERP.Client/Contracts/<Domain>Dto.cs
```

**Core domain records** (immutable):
```
src/dERP.Core/<Domain>/<Entity>.cs
```

**Repositories & data layer:**
```
src/dERP.Data/Repositories/<Domain>/I<Domain>Repository.cs
```

---

## Glossary & Key References

### ADRs by Domain

| ADR | Title | Section |
|---|---|---|
| **0002** | Phased ERP Rollout | Phase Rollout Status |
| **0003** | Cloud Run + API Key | Auth Surface |
| **0004** | UL Listing as Part Attribute | Parts (FEEL) |
| **0008** | Part Profile / FEEL Criteria Split | Parts (Profile) |
| **0012** | dERP Headless; dWEB + dPART Consumers | What is dERP |
| **0013** | Soft Delete on Part | Parts (DELETE) |
| **0014** | PartCategory Expansion | Part Categories |
| **0015** | PartCriteria Expansion | Parts (Criteria stub) |
| **0016** | dERP Data Domain (HTTP boundary) | Architecture rule |
| **0017** | PartCriteria Per-Category Typed | Parts (Criteria) |
| **0018** | PartCategory AuxContact Add | Part Categories |
| **0019** | Project Metadata + Customer PO + Drive URL | Projects |
| **0020** | BOM Relational Lift | BOM Lines |
| **0021** | Customer Endpoint Surface | Parties |
| **0022** | Project Write Surface | Projects |
| **0023** | Purchase Order Read Surface | Purchase Orders |
| **0025** | Part Categories API Surface | Part Categories |
| **0026** | Receive Parts Pipeline | Receipts |
| **0027** | Receive Parts Gap Fill | PO-Scoped Receipts |
| **0028** | Quotes API + QBO Write-Through | Quotes |
| **0029** | Project Read/Write Surface | Projects |
| **0030** | QuickBooks Pull Integration | QBO Pull |
| **0033** | PathD Vendor Data Cleanup | Vendors |
| **0034** | Part Enrichment Sidecar | Open ADRs |

### Key Concepts

| Term | Definition |
|---|---|
| **PartCriteria** | Structured selection input: category, amps, voltage, poles, FEEL profile, contractor, etc. dPART sends this; dERP.Selection returns best match. Stub contractor awareness (ADR-0015). |
| **PartProfile (FEEL)** | Function Evaluation Electrical Library — criteria stored in `parts.part_profile` JSON column. Includes overload, starting method, UL reference, contractor feel, etc. Soft-validated on write. |
| **ETag** | HTTP caching via `If-None-Match` header. Middleware implements for GET/HEAD `/api/*` to reduce payload. 304 Not Modified on cache hit. |
| **ExternalRef** | Idempotency key for receipts, quotes. Resending same ExternalRef returns 200 (idempotent), not 201 (new). |
| **Drive URL Deriver** | Per ADR-0019: resolves project's estimate + customer PO download links. Per-project override > deriver > null. Deriver reads Google Drive folder config. |
| **QBO Sync State** | Quote lifecycle tracking: pending → synced / failed / pending_retry. IQboEstimateGateway writes estimates; retry queue picks up 5xx cases. |

---

## Testing & Local Dev

**No integration tests for API endpoints are checked into this document.** See `src/dERP.Api.Tests/` for endpoint integration tests (requires local Postgres via `docker compose up -d postgres`).

**Build verification per CLAUDE.md:**
```bash
dotnet build
dotnet test --filter Category!=Integration  # Unit tests (always)
dotnet test                                   # Full suite (when Postgres is up)
```

---

## Document Metadata

- **Source repo:** `dapp-controls/dERP`
- **Last updated:** 2026-05-23 (snapshot at ADR-0051 task creation)
- **Scope:** Read-only landscape summary; for implementation details, consult source files and ADRs
- **Audience:** New contributors, cross-repo maintainers (dWEB, dPART), API consumers
- **Maintenance:** Update when new endpoints added, phases completed, ADRs accepted, or consumer contracts change

---

**End of API Landscape Document**
