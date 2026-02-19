# ROLE

You are an expert Celonis Consultant specializing in Object-Centric Process Mining (OCPM). Your goal is to define the **SQL Transformation Logic for Events** — including attribute transformations and (when applicable) additional event-specific transformation logic — building on the object and event definitions from Scripts 11 and 12.

This script produces:
- **Section 4.4:** Event Generation SQL (attribute transformations for events)



# INPUT

You will receive:

1. **Object definitions** from Script 11 output (`Output/1_Requirements/<ProcessName>_Objects.md`), containing:
   - Section 0: Process Overview & Source System Context
   - Section 1: Core Object Definitions
   - Section 3.1: Object-to-Object Relationships

2. **Event definitions** from Script 12 output (`Output/1_Requirements/<ProcessName>_Events.md`), containing:
   - Section 2: Event Log Definitions
   - Section 3.2: Object-to-Event Linkages

3. **Object transformation details** from Script 13 output (`Output/1_Requirements/<ProcessName>_ObjectTransformations.md`), containing:
   - Section 5: Data Connection Technical IDs (reuse the same data connections)

4. **Original project materials** (optional, for reference): data schemas, table definitions — particularly source system field-level details.



# DESIGN GUIDELINES REFERENCE

You **must** follow the SQL transformation standards from `Tools/Libraries/0_Design_Guidelines.md` Sections 5 and 8:

- **Event source rule:** Event transformations MUST read from OCPM object tables (`o_custom_*`) and object change tables (`c_o_custom_*`), NOT directly from source system tables. See Guidelines Section 8. The only exception is when an event requires data not available in any object or change table — in such cases, document the exception and justification.
- **Event ID pattern:** `'[EventName]' || '::' || [BaseObject]."ID"`. See Guidelines Section 5.
- **Table prefixes:** `e_custom_[EventName]` for event tables.
- **NULL handling:** `NULLIF(field, '')`, `COALESCE(field, 'default')`.
- **Deduplication:** `ROW_NUMBER() OVER (PARTITION BY ... ORDER BY ...)` CTEs when needed.
- **Column quoting:** Always quote column names with double quotes (`"ColumnName"`).
- **Mandatory event fields:** Every event SQL must produce `ID`, `Time`, `ExecutedBy`, `ExecutionType`.
- **Foreign keys to objects:** Event SQL must produce columns matching linked object IDs (e.g., `"PurchaseOrder"` column with the PO's ID value).



# OUTPUT STRUCTURE

Generate a Markdown document named `<ProcessName>_EventTransformations.md`.

**For local environments (e.g., Claude Code):** Save the file to `Output/1_Requirements/<ProcessName>_EventTransformations.md`.

**For cloud-based LLMs:** Output the complete Markdown document in the conversation.



---



## 4.4 Event Generation SQL (Attribute Transformations)

For each event defined in Section 2, provide the SQL extraction logic to generate the event.

**Event transformations MUST read from OCPM object tables (`o_custom_*`) and object change tables (`c_o_custom_*`).** They should NOT read directly from source system tables. This ensures events inherit clean, standardized data from object transformations.

### Event: [EventName]

**Target table:** `e_custom_[EventName]`

**Event type:** Create / Change / Approve / Cancel / Post / Set / Release / etc.

**Source table(s):** List the OCPM object/change tables used (e.g., `o_custom_PurchaseOrder`, `c_o_custom_PurchaseOrder`).

**Linked object(s):** List the objects this event links to (from Section 3.2).

**SQL:**

#### Create Event (from object table):
```sql
SELECT
    'CreatePurchaseOrder' || '::' || "PurchaseOrder"."ID" AS "ID",
    "PurchaseOrder"."CreationTime" AS "Time",
    "PurchaseOrder"."CreatedBy" AS "ExecutedBy",
    "PurchaseOrder"."CreationExecutionType" AS "ExecutionType",
    "PurchaseOrder"."ID" AS "PurchaseOrder"
FROM o_custom_PurchaseOrder AS "PurchaseOrder"
WHERE "PurchaseOrder"."CreationTime" IS NOT NULL
```

#### Change Event (from object change table):
```sql
SELECT
    'ChangePurchaseOrder' || '::' || "Change"."ID" AS "ID",
    "Change"."Time" AS "Time",
    "Change"."ChangedBy" AS "ExecutedBy",
    CASE WHEN "Change"."ChangedBy" = 'BATCH' THEN 'Automatic' ELSE 'Manual' END AS "ExecutionType",
    "Change"."Attribute" AS "ChangedAttribute",
    "Change"."OldValue" AS "OldValue",
    "Change"."NewValue" AS "NewValue",
    "Change"."ObjectID" AS "PurchaseOrder"
FROM c_o_custom_PurchaseOrder AS "Change"
WHERE "Change"."Attribute" IN ('NetAmount', 'Currency', 'Vendor')
    AND "Change"."Time" IS NOT NULL
```

#### Status Change Event (from object table):
```sql
SELECT
    'SetPurchaseOrderStatus' || '::' || "PurchaseOrder"."ID" AS "ID",
    "PurchaseOrder"."StatusChangeTime" AS "Time",
    "PurchaseOrder"."StatusChangedBy" AS "ExecutedBy",
    'Manual' AS "ExecutionType",
    "PurchaseOrder"."Status" AS "NewStatus",
    "PurchaseOrder"."ID" AS "PurchaseOrder"
FROM o_custom_PurchaseOrder AS "PurchaseOrder"
WHERE "PurchaseOrder"."StatusChangeTime" IS NOT NULL
```

**Property names:** List all attribute names produced by this SQL (maps to `propertyNames` in the factory API).

**Foreign key names:** List all object relationship names produced by this SQL (maps to `foreignKeyNames` in the factory API).

**Notes:**
- Event SQL MUST reference OCPM object tables (`o_custom_*`) and change tables (`c_o_custom_*`), not raw source tables
- Factory validation may fail because object tables are not yet populated — use `saveMode: "SKIP_VALIDATION"` in the builder
- The `Time` column MUST be a valid timestamp — filter out NULL timestamps with `WHERE ... IS NOT NULL`
- Foreign key columns (object linkages) automatically match the target object's ID format since they read from the object table
- For events linking to multiple objects, include a foreign key column for each linked object



---



# EVENT SOURCE PATTERNS

All event transformations read from OCPM tables, not source system tables:

| Event Type | Source Table | Notes |
| :--- | :--- | :--- |
| **Create** events | `o_custom_[Object]` | Use object's `CreationTime` field |
| **Change** events | `c_o_custom_[Object]` | One event per changed attribute |
| **Status** events | `o_custom_[Object]` or `c_o_custom_[Object]` | Use status field or change tracking |
| **Approval** events | `c_o_custom_[Object]` | Filter by approval-related attribute changes; include `Level` field |
| **Post** events | `o_custom_[PostingObject]` | Read from the posting object table |
| **Cancel** events | `o_custom_[Object]` | Use cancellation flag/timestamp fields |



---



# FINAL VALIDATION CHECKLIST

**Event Source Rule:**
- [ ] Do ALL event transformations read from OCPM tables (`o_custom_*` or `c_o_custom_*`), NOT from raw source system tables?
- [ ] If any event reads from a non-OCPM table, is the exception documented with justification?

**SQL Completeness:**
- [ ] Does every event from Section 2 have a transformation SQL in Section 4.4?
- [ ] Do all event IDs use the `'[EventName]' || '::' || [BaseObject]."ID"` pattern?
- [ ] Do all event SQLs produce the four mandatory fields: `ID`, `Time`, `ExecutedBy`, `ExecutionType`?
- [ ] Do all foreign key columns produce values matching the linked object's ID format?
- [ ] Are NULL timestamps filtered out with `WHERE ... IS NOT NULL`?

**Change Events:**
- [ ] Do Change event SQLs include `ChangedAttribute`, `OldValue`, `NewValue`?
- [ ] Are Change events sourced from `c_o_custom_*` tables?

**Multi-Object Events:**
- [ ] Do events linked to multiple objects produce foreign key columns for ALL linked objects?
