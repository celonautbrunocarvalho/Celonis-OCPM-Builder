# OCPM Design Guidelines & Modeling Standards

> **Source:** Consolidated from *Catalog Guidelines & Modeling Best Practices V1.0* and analysis of the *CATALOG_CORE_REFERENCE* export. This document provides the design principles, naming conventions, and structural standards that must be followed when defining OCPM requirements and building object-centric data models.

---

## 1. Catalog Taxonomy

Before modeling, determine where your content belongs:

| Content Type | When to Use | Best Practice |
| :--- | :--- | :--- |
| **Core** | Enhancing a business process data model with system-agnostic content that overlaps across at least two source systems. | "Simplicity, speed, and scalability over completeness." Start small, grow over time. Avoid breaking changes. |
| **Extension** | Adding source-system-specific attributes, objects, events, or relationships on top of an existing Core. | "Aim for completeness without sacrificing simplicity." Maintain alignment with the Core. |
| **SSDM** | Modeling a completely new process or system where Core/Extension cannot satisfy requirements. | "Accommodate the source system, but build with future integration in mind." Assess for transition to Core/Extension regularly. |

---

## 2. General Design Principles

### Discovery Principles
- **Keep the value in mind:** All modeling decisions should directly support specific analyses, use cases, or KPIs. Avoid adding unnecessary elements "just in case."
- **Events first:** Start by identifying relevant events with business users, then determine which objects participate in those events, and finally identify other relevant objects.
- **Focus on a specific KPI:** Use a particular KPI or use case to guide selection of relevant events and objects.
- **Start fast, visualize, and iterate:** Begin with a small scope, build a test analysis to validate, then expand iteratively. Avoid over-engineering.

### Modeling Principles
1. **Focus on relevant tables and consider exceptions:** Understand the type of source table (transactional, audit/change tracking, master data, reference/config, staging/interface) and model accordingly.
2. **Create objects from transactional tables:** An object represents a real-world entity with unique identity and attributes.
3. **Focus on understanding, value, and avoid complexity:** Name objects so the underlying business concept is clear. Model relevant objects and relationships so KPIs can be calculated without excessive binds or joins.
4. **Leverage existing content:** Always cross-reference existing Core, Extensions, and SSDMs for related systems or processes.
5. **Use common sense:** Balance competing principles. When facing uncertainty, consider using Extensions to address specific requirements.

---

## 3. Object Naming Conventions

### Object Names
- **PascalCase**, singular, business-readable (e.g., `PurchaseOrder`, `CustomerInvoice`, `SalesOrderScheduleLine`)
- Never use source system table names (e.g., use `PurchaseOrder` not `EKKO`)
- Use compound words for specificity (e.g., `CustomerInvoiceLine`, `MaterialMasterPlant`)

### Standard Object Fields
Every object **must** include:
| Field | Data Type | Description |
| :--- | :--- | :--- |
| `ID` | `CT_UTF8_STRING` | Unique identifier (primary key) — always required |
| `SourceSystemInstance` | `CT_UTF8_STRING` | Source system parameter value (e.g., `SAP_ECC`) |

### Attribute Naming Conventions
PascalCase with semantic suffixes. No underscores in field names (e.g., `MaterialText` not `Material_Text`).

| Suffix | Description | Data Type | Correct Example | Incorrect Example |
| :--- | :--- | :--- | :--- | :--- |
| `_ID` | Auto-added by system for foreign keys — do not add manually | varchar | — | Adding `_ID` manually |
| `SourceSystemInstance` | Source system parameter reference | varchar | `<%=sourceSystem%>` | Typing `'SAP_'` directly |
| `_Name` | Translation/full name of another attribute | varchar | `CompanyCodeName` | `CompanyCodeDescription` |
| `_Quantity` / `_Weight` / `_Volume` | Measurable quantities | float | `MaterialWeight` | `Weight` (without object context) |
| `_QuantityUnit` / `_WeightUnit` / `_VolumeUnit` | Unit of measurement | varchar | `BaseQuantityUnit` | `Quantity` without `QuantityUnit` |
| `_Amount` | Monetary value | float | `NetAmount`, `NetUnitPrice` | `OrderAmount`, `EKPO.NETPR` |
| `Currency` | Currency code (standalone or with prefix) | varchar | `Currency`, `DocumentCurrency` | `$` symbol instead of `USD` |
| `_Percentage#` | Percentage values (numbered if multiple) | float | `CashDiscountPercentage1` | `Percentage1` (unclear) |
| `_Date` | General dates (no time precision) | timestamp | `BaselineDate` | `BaselineTime` (wrong suffix) |
| `_Time` | Timestamps with time precision | timestamp | `CreationTime` | `CreationDate` (wrong suffix) |
| `_ExecutionType` | Only two values: `Automatic` and `Manual` | varchar | `CreationExecutionType` | `auto`, `by_user` |
| `Is[FlagName]` | Boolean flags | boolean | `IsDeleted`, `IsBlockedForPayment` | `Flag1`, `DeletedFlag` |
| `[Object]Line` | Line item number within parent | varchar | `InvoiceLine`, `PurchaseOrderLine` | `ItemNumber` |
| `Number` | Source system reference number | varchar | `AccountingDocumentNumber` | Raw source field name |

### Object Categories (from Catalog Reference)
Objects are classified using structured categories:
- **Metadata** category with value `MasterData` — for master data objects (Customer, Material, Vendor, User)
- **Processes** category — tags objects to business processes (e.g., `OrderManagement`, `Procurement`, `AccountsPayable`, `AccountsReceivable`, `InventoryManagement`)
- **Hierarchy** category with values `parent` / `child` — for header/line-item relationships (e.g., `CustomerInvoice` = parent, `CustomerInvoiceLine` = child)

### Color Coding (from Catalog Reference)
Objects in the catalog use hex color codes for UI visualization:
- `#1832DE` (blue) — Customer, Delivery, ReceivableItem
- `#4608B3` (purple) — Material, GoodsReceipt, Vendor, PurchaseOrder, VendorInvoice
- `#4D00BA` (dark purple) — Delivery variants

### Namespace
All custom objects use `namespace: "custom"`.

---

## 4. Event Naming Conventions

### Event Names
- **Verb + Object** pattern in PascalCase (e.g., `CreatePurchaseOrder`, `ApprovePurchaseDocument`, `PostGoodsReceipt`)
- Common action verbs: `Create`, `Cancel`, `Change`, `Apply`, `Approve`, `Post`, `Set`, `Release`, `Execute`, `Sign`, `Enter`

### Standard Event Fields
Every event **must** include:
| Field | Data Type | Description |
| :--- | :--- | :--- |
| `ID` | `CT_UTF8_STRING` | Unique event identifier |
| `Time` | `CT_INSTANT` | Timestamp when event occurred |
| `ExecutedBy` | `CT_UTF8_STRING` | User who executed the event |
| `ExecutionType` | `CT_UTF8_STRING` | `Automatic` or `Manual` |

### Event-Specific Field Patterns
| Event Type | Additional Fields |
| :--- | :--- |
| **Create** events | `DocumentCategory` |
| **Approval** events | `Level`, `DocumentCategory` |
| **Change** events | `ChangedAttribute`, `OldValue`, `NewValue` |
| **Block/Release** events | `BlockType`, `BlockReason` |
| **Cancellation** events | `CancellationType`, `[EntityType]Type` |

### Event Modeling Complexities

**Concurrent Events:**
- Model the lowest-level CRUD events as distinct entries (do not flatten into a single event)
- Use Event Grouping to roll system events up into Real-World Events and Business Phases
- Three hierarchy levels: Level 3 (System Events) → Level 2 (Real-Life Events) → Level 1 (Process Phases)

**Unbounded Events:**
- Events with variable attribute values (e.g., "Change Purchase Order - Quantity", "Change Purchase Order - Price")
- Use the event name concatenation feature (Dynamic Events)

**Static Events:**
- Date-times that represent notable points in time but not actual activities (e.g., "Due Date")
- If a static event changes the nature of a real event, reflect it in the real event's naming or attributes
- Avoid encoding customer-specific business logic directly into event transformations — handle in the Knowledge Model

### Event Grouping by Process (from Catalog Reference)
| Process | Example Events |
| :--- | :--- |
| **Order Management** | CreateSalesOrder, CreateDelivery, CreateCustomerInvoice, PostGoodsIssue, CancelCustomerInvoice |
| **Procurement** | CreatePurchaseDocument, ApprovePurchaseDocument, PostGoodsReceipt, EnterVendorInvoice |
| **Accounts Payable** | PostPayableItem, SetPaymentBlock, ReleasePaymentBlock, ClearPayableItem |
| **Accounts Receivable** | ApplyCustomerInvoiceLine, CancelCustomerInvoice |

---

## 5. ID Construction

### Delimiter
Always use `::` to separate ID components. Never use `_` or other delimiters.

### Source System Parameter
Use `<%=sourceSystem%>` data pool parameter for source system identification. Feed it with specific values:
- `SAP_ECC`, `SAP_S4_HANA`, `Oracle_EBS`, `Oracle_Fusion`, `Coupa`, etc.
- Never use generic values like `SAP` or `Oracle`
- For systems with clients (e.g., SAP), append the client: `<%=sourceSystem%> || '::' || "EKKO"."MANDT"`

### Object ID Pattern
```sql
<%=sourceSystem%> || '::' || [key_column_1] || '::' || [key_column_2] || ...
```

**Examples:**
```sql
-- Simple: Single key column
<%=sourceSystem%> || '::' || "EKPO"."MANDT" || '::' || "EKPO"."EBELN"

-- Composite: Multiple key columns
<%=sourceSystem%> || '::' || "MANDT" || '::' || "MATNR" || '::' || "WERKS"
```

### Event ID Pattern
```sql
'[EventName]' || '::' || [BaseObject]."ID"
```

**Examples:**
```sql
-- Event ID derived from object ID
'CreatePurchaseDocument' || '::' || "PurchaseDocument"."ID"
'ApplyCustomerInvoiceLine' || '::' || "CustomerInvoiceLine"."ID"
'PostGoodsReceipt' || '::' || "GoodsReceipt"."ID"
```

---

## 6. Relationship Guidelines

### Object-to-Object Relationships
Relationships in OCPM are bidirectional. Supported cardinalities:
- **Many-to-One (n:1):** Many instances of A related to one instance of B. Foreign key on the "many" side.
- **One-to-Many (1:n):** One instance of A related to many instances of B.
- **One-to-One (1:1):** Not directly supported. Represent via the "1" side owning all attributes.
- **Many-to-Many (n:m):** Use explicit relationship objects (multilink) rather than implicit `r_` tables.

### Relationship JSON Structure (from Catalog Reference)
```json
{
  "cardinality": "HAS_ONE",       // or "HAS_MANY"
  "name": "Customer",
  "namespace": "custom",
  "target": {
    "mapped_by": null,              // null for HAS_ONE (child → parent)
    "mapped_by_namespace": null,
    "object_ref": { "name": "Customer", "namespace": "custom" }
  }
}
```

**`mapped_by` Convention:**
- `HAS_ONE` (child → parent): `mapped_by: null` — the owning side holds the foreign key
- `HAS_MANY` (parent → children): `mapped_by: "[ParentFieldName]"` — points to the field on the child that references back

### Many-to-Many Best Practices
- Always use **explicit relationship objects** (e.g., `RelationshipThreeWayMatch`, `RelationshipBillOfMaterials`)
- Explicit objects allow adding attributes (e.g., `LinkageTimestamp`, `LinkageReason`)
- Explicit objects are visible in perspectives and result in simpler PQL
- Implicit `r_` tables are auto-generated but not visible in perspectives and lead to complex PQL

### Multilink Objects
- Set `multi_link: true` on objects that serve as relationship bridges
- Named with `Relationship` prefix (e.g., `RelationshipOrderToInvoice`, `RelationshipBillOfMaterials`)
- Connected with `HAS_MANY` from both participating objects

### Circular / Loop Relationships
- **Object-level loops ARE permitted.** It is valid for objects to form cycles in their relationship definitions (e.g., WorkOrder → Operation → EPD → WorkOrder). Define all relationships regardless of cycles. The object model should represent the complete real-world data structure.
- **Perspective-level loops are NOT permitted.** When assembling a perspective, break every cycle by switching one relationship in the cycle from LINK to EMBED. See Section 7 for details.
- **Choosing which to EMBED:** Prefer embedding the master-data or less-granular side of the cycle. If both sides are transactional, embed the side that is less central to the analytical question being answered by the perspective.

### Relationship Exhaustiveness
- For each object, examine ALL its attributes that reference other objects (e.g., PlantCode, MaterialNumber, VendorNumber). Each such attribute should have a corresponding O:O relationship.
- Enumerate ALL relationship paths between objects, not just the primary hierarchical ones. Include:
  - Direct parent-child relationships (e.g., WorkOrder → WorkOrderItem)
  - Master data lookups (e.g., WorkOrder → Plant via PlantCode)
  - Cross-process links (e.g., EPD → WorkOrder)
  - Alternative paths between the same pair of objects

### Best Practices
- Avoid unnecessary connections — only include relationships relevant to the analysis
- Hierarchical relationships should only go one level deep (Header → Item, not Header → Item → ScheduleLine without the middle step)
- Master data should be linked minimally — use embedding in perspectives for context
- Relationships should be agnostic and reusable across source systems (Core level)

---

## 7. Perspective Guidelines

### Structure
A perspective includes objects, events, relationships, and projections for a specific process or use case.

### Linking Strategies
| Strategy | When to Use | Example |
| :--- | :--- | :--- |
| **LINK** (`Include relationship`) | For transactional objects — creates lookup/reference relationship | SalesOrder LINK Customer, Delivery LINK Material |
| **EMBED** | For master data objects — includes data inline to avoid cyclic relationships | PurchaseDocument EMBED CreatedBy, PurchaseRequisitionLine EMBED Material |

### Key Rules
- **Use LINK** for transactional objects (standard, ~90% of relationships)
- **Use EMBED** for master data objects to avoid cyclic relationships and ensure PQL compatibility
- **Never EMBED** transactional objects (leads to data redundancy and performance issues)
- **Resolve cyclic relationships** using EMBED on one side, or use multilink relationship objects

### Cycle-Free Requirement
- **Perspectives MUST NOT contain relationship cycles when using LINK strategy.** If a path A → B → C → A exists where all relationships are LINK, the perspective will fail or produce incorrect results.
- If the underlying object model has cycles (which is allowed — see Section 6), break them in the perspective by switching one relationship in each cycle to EMBED.
- Document which relationships were switched from LINK to EMBED to break cycles and why.
- When choosing which relationship to EMBED: prefer the master-data side; if both are transactional, embed the side less central to the perspective's analytical question.

### Required Perspective Components
Each perspective definition must include:
1. **Objects** — each object listed with its specific relationships and a per-relationship LINK/EMBED strategy
2. **Events** — all events relevant to this analytical view
3. **Projections** — each with a lead object and an event list defining which events are visible in that analytical cut
4. **Default projection** — the name of the primary analytical view

### Projections
- **Lead object** sets the analysis granularity — usually a line-item level object
  - Order Management: `SalesOrderScheduleLine` (projection: `SalesOrderScheduleLineActivities`)
  - Procurement: `PurchaseDocumentLine`
- Event breakdowns enable dimensional filtering via `breakdown_attributes`

### Exhaustiveness in Perspectives
- Every transactional object that has events should appear in at least one perspective
- Every event should appear in at least one projection
- Master data objects should appear as EMBED'd relationships within other objects, not as standalone entries

### Best Practices
- Start with the lead object and incrementally add objects and events relevant to the use case
- Do not create perspectives with large numbers of objects upfront without a clear focus
- Leverage UI visualization (Process Explorer, Case Explorer) to validate after publishing to development
- When connecting multiple processes, identify the events that constitute the end of one process and the start of the next

---

## 8. SQL Transformation Standards

### Table Naming Conventions
| Prefix | Table Type | Example |
| :--- | :--- | :--- |
| `o_` | Object tables | `o_custom_Customer`, `o_custom_PurchaseOrder` |
| `e_` | Event tables | `e_custom_CreatePurchaseDocument` |
| `c_` | Change/audit tables | `c_o_custom_CustomerInvoiceLine` |
| `r_` | Relationship tables (M:N) | `r_o_custom_CustomerInvoiceLine__SalesOrderScheduleLines` |
| `x_` | Object field extensions | `x_o_custom_[ObjectName]` |
| `y_` | Event field extensions | `y_e_custom_[EventName]` |

### SQL Dataset Structure
```json
{
  "id": "[DatasetName]",
  "type_": "SQL_FACTORY_DATA_SET",
  "complete_overwrite": false,
  "disabled": false,
  "materialise_cte": false,
  "overwrite": null,
  "sql": "[SQL_QUERY]"
}
```

### Event Transformation Source Rule

**Event transformations MUST read from OCPM object tables (`o_custom_*`) and object change tables (`c_o_custom_*`), NOT directly from source system tables.** This ensures:
- Events inherit the clean, standardized data produced by object transformations (correct IDs, NULL handling, deduplication)
- Foreign key columns automatically match the target object's ID format
- Changes to object transformations propagate to events without requiring event SQL updates
- A clear separation of concerns: object transformations handle source-system-specific logic, event transformations handle event derivation logic

**The only exception** is when an event requires data that is not available in any object or change table (e.g., a dedicated workflow/audit table with no corresponding object). In such cases, document the exception and the justification.

### Common SQL Patterns

**Simple Event Creation (from object table):**
```sql
SELECT
    'CreatePurchaseDocument' || '::' || "PurchaseDocument"."ID" AS "ID",
    "PurchaseDocument"."CreationTime" AS "Time",
    "PurchaseDocument"."CreatedBy_ID" AS "ExecutedBy",
    "PurchaseDocument"."CreationExecutionType" AS "ExecutionType"
FROM o_custom_PurchaseDocument AS "PurchaseDocument"
WHERE "PurchaseDocument"."CreationTime" IS NOT NULL
```

**Change Tracking Event (from audit tables):**
```sql
SELECT
    'ChangePurchaseOrderLine' || '::' || "Change"."ID" AS "ID",
    "Change"."Time" AS "Time",
    "Change"."ChangedBy" AS "ExecutedBy",
    "Change"."ChangedAttribute" AS "ChangedAttribute",
    "Change"."OldValue" AS "OldValue",
    "Change"."NewValue" AS "NewValue"
FROM c_o_custom_PurchaseOrderLine AS "Change"
WHERE "Change"."Attribute" = 'SpecificAttribute'
```

**Deduplication with CTE:**
```sql
WITH "CTE_Sort" AS (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY "ObjectID" ORDER BY "Time" ASC) AS "rn"
    FROM [source_table]
)
SELECT * FROM "CTE_Sort" WHERE "rn" = 1
```

### NULL Handling
```sql
NULLIF(field, '') IS NULL     -- Treat empty string as NULL
NULLIF(field, '') IS NOT NULL -- Non-empty check
COALESCE(field, 'default')   -- Default value fallback
```

### Source System Parameters
```json
{"name": "sourceSystem", "value": "'SAP_S4_HANA'"},
{"name": "sourceSystem", "value": "'SAP_ECC'"},
{"name": "sourceSystem", "value": "'Oracle_EBS'"},
{"name": "sourceSystem", "value": "'Oracle_Fusion'"},
{"name": "LanguageKey", "value": "'US'"}
```

---

## 9. Factory & Data Connection Standards

### Factory Structure
```json
{
  "display_name": "[EntityName] - [number]",
  "name": "[EntityName] - [number]",
  "factory_id": "[UUID]",
  "data_connection_id": "[UUID]",
  "namespace": "custom",
  "target": {
    "entity_ref": {"name": "[EntityName]", "namespace": "custom"},
    "kind": "EVENT"  // or "OBJECT"
  },
  "validation_status": "VALID",
  "transformations": [...]
}
```

### Naming Conventions
- Display name: `[EntityName] - [number]` (e.g., `Customer - 1`, `CreatePurchaseDocument - 2`)
- Template factory instances: `[EntityName] - [SourceSystem]` (e.g., `Customer - SAP ECC`, `Customer - SAP S4 HANA`)

### Data Connection ID
- Default/placeholder: `00000000-0000-0000-0000-000000000000`
- Actual connections use UUIDs from the Celonis platform
- Multiple factories per entity are allowed for different source systems

---

## 10. Deployment & Validation

### Deployment Guidelines
1. **Test First, Deploy Second:** Always deploy to development first. Never deploy directly to production.
2. **Full Deployment:** Deploying pushes the entire current version. You cannot selectively deploy individual changes.
3. **One Direction:** Changes move from development to test/production only.

### Validation Checklist (Bottom-Up)
1. **Individual Objects:** Verify attribute definitions, data volumes, and value correctness.
2. **Events for a Single Object:** Check default event log, frequency, sequence, and completeness.
3. **Relationships Between Objects:** Verify matching percentages, no missing relationships, shared events in MOPE.
4. **Combined Event Log (E2E):** Verify displayed events cover the process end-to-end, check frequency, sequence, and merging at shared events.

### Source Table Types and Modeling Recommendations
| Table Type | Purpose | Modeling Recommendation |
| :--- | :--- | :--- |
| **Transactional** | Operational transactions (invoices, orders, payments) | Model as one or multiple objects with at least one event |
| **Audit & Change Tracking** | Track changes to data | Model as events related to transactional objects |
| **Master Data** | Key business entities providing context | Model as one object; embed in perspectives |
| **Reference & Configuration** | System settings, configurations, standardized values | Integrate into objects providing additional context |
| **Staging & Interface** | Temporary storage for incoming/outgoing data | Use as sources for relationship objects or connecting tables |

---

## 11. Process Organization (from Catalog Reference)

### Standard Processes
| Process | Key Objects | Key Events |
| :--- | :--- | :--- |
| **Order Management** | SalesOrder, SalesOrderScheduleLine, Customer, Delivery, DeliveryLine, CustomerInvoice, CustomerInvoiceLine, GoodsIssue, Material | CreateSalesOrder, CreateDelivery, CreateCustomerInvoice, PostGoodsIssue, CancelCustomerInvoice |
| **Procurement** | PurchaseDocument, PurchaseDocumentLine, PurchaseRequisitionLine, PurchaseScheduleLine, Vendor, VendorInvoice, VendorInvoiceLine, GoodsReceipt, Material | CreatePurchaseDocument, ApprovePurchaseDocument, PostGoodsReceipt, EnterVendorInvoice |
| **Accounts Payable** | PayableItem, VendorInvoice, VendorInvoiceLine, Vendor | PostPayableItem, SetPaymentBlock, ReleasePaymentBlock, ClearPayableItem |
| **Accounts Receivable** | ReceivableItem, CustomerInvoice, CustomerInvoiceLine, Customer | ApplyCustomerInvoiceLine, CancelCustomerInvoice |
| **Inventory Management** | Material, MaterialMasterPlant, GoodsReceipt, GoodsIssue, Delivery | PostGoodsReceipt, PostGoodsIssue |

### Shared Objects Across Processes
- **Master data** objects appear in multiple processes: `Material`, `Customer`, `Vendor`, `User`, `CurrencyConversion`, `Plant`
- **Relationship objects** appear only in their target process: `RelationshipOrderToInvoice`, `RelationshipThreeWayMatch`

---

## Quick Reference Summary

| Aspect | Convention |
| :--- | :--- |
| Object naming | PascalCase, singular, business-readable |
| Event naming | Verb + Object, PascalCase |
| Attribute naming | PascalCase with semantic suffixes |
| ID delimiter | `::` (always) |
| Source system param | `<%=sourceSystem%>` with specific values |
| Namespace | `custom` |
| Boolean fields | `Is[FlagName]` pattern |
| ExecutionType values | `Automatic` or `Manual` only |
| Table prefixes | `o_`, `e_`, `c_`, `r_`, `x_`, `y_` |
| Relationship strategy | LINK for transactional, EMBED for master data |
| M:N relationships | Explicit relationship objects (not implicit `r_` tables) |
| Perspective lead object | Line-item level (e.g., PurchaseDocumentLine) |
