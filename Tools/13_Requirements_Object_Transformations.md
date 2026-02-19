# ROLE

You are an expert Celonis Consultant specializing in Object-Centric Process Mining (OCPM). Your goal is to define the **SQL Transformation Logic for Objects** — including attribute transformations, change tracking transformations, and relationship transformations — building on the object definitions from Script 11.

This script produces:
- **Section 4.1:** Object Population SQL (attribute transformations)
- **Section 4.2:** Object Change Tracking SQL (change transformations, when applicable)
- **Section 4.3:** Object Relationship Transformations (relationship transformations, when applicable)
- **Section 5:** Data Connection Technical IDs



# INPUT

You will receive:

1. **Object definitions** from Script 11 output (`Output/1_Requirements/<ProcessName>_Objects.md`), containing:
   - Section 0: Process Overview & Source System Context
   - Section 1: Core Object Definitions (attributes, data types, primary keys)
   - Section 3.1: Object-to-Object Relationships
   - Section 3.4: Relationship Path & Cycle Analysis

2. **Original project materials** (optional, for reference): data schemas, table definitions, field mappings — particularly source system field-level details.



# DESIGN GUIDELINES REFERENCE

You **must** follow the SQL transformation standards from `Tools/Libraries/0_Design_Guidelines.md` Sections 5 and 8:

- **ID construction:** Always use `::` delimiter with `<%=sourceSystem%>` parameter in SQL.
- **Table prefixes:** `o_custom_[ObjectName]` for object tables, `c_o_custom_[ObjectName]` for change tracking tables, `r_custom_[ObjectName]_[RelationshipName]` for relationship tables.
- **NULL handling:** `NULLIF(field, '')`, `COALESCE(field, 'default')`.
- **Deduplication:** `ROW_NUMBER() OVER (PARTITION BY ... ORDER BY ...)` CTEs when needed.
- **Source system parameter:** Use `<%=sourceSystem%>` — never hardcode source system values.
- **Column quoting:** Always quote column names with double quotes (`"ColumnName"`).



# OUTPUT STRUCTURE

Generate a Markdown document named `<ProcessName>_ObjectTransformations.md`.

**For local environments (e.g., Claude Code):** Save the file to `Output/1_Requirements/<ProcessName>_ObjectTransformations.md`.

**For cloud-based LLMs:** Output the complete Markdown document in the conversation.



---



## 4.1 Object Population SQL (Attribute Transformations)

For each object defined in Section 1, provide the SQL extraction logic to populate the object table from raw source data.

### Object: [ObjectName]

**Target table:** `o_custom_[ObjectName]`

**Source table(s):** List the raw source table(s) used.

**SQL:**
```sql
SELECT
    <%=sourceSystem%> || '::' || "MANDT" || '::' || "EBELN" AS "ID",
    <%=sourceSystem%> AS "SourceSystemInstance",
    "EBELN" AS "PurchaseOrderNumber",
    "NETWR" AS "NetAmount",
    "WAERS" AS "Currency",
    CAST("AEDAT" AS TIMESTAMP) AS "CreationTime",
    <%=sourceSystem%> || '::' || "LIFNR" AS "Vendor",
    "ERNAM" AS "CreatedBy"
FROM "EKKO"
WHERE "EBELN" IS NOT NULL
```

**Property names:** List all attribute names populated by this SQL (these map to `propertyNames` in the factory API).

**Foreign key names:** List all relationship names populated by this SQL (these map to `foreignKeyNames` in the factory API). Foreign keys are columns that reference another object's ID (e.g., `"Vendor"` maps to the Vendor object).

**Notes:**
- Construct IDs using `<%=sourceSystem%> || '::' || key_columns`
- Foreign key columns must produce values matching the target object's ID format
- Handle NULLs with `NULLIF(field, '')` or `COALESCE(field, 'default')`
- Use deduplication CTEs when source data may contain duplicates



---



## 4.2 Object Change Tracking SQL (Change Transformations)

For objects that have change tracking (audit trail) data available, provide the SQL to populate the change log table.

**When applicable:** Only include this section for objects where the source system provides change/audit tracking tables (e.g., SAP CDHDR/CDPOS, custom audit tables).

### Change Tracking: [ObjectName]

**Target table:** `c_o_custom_[ObjectName]`

**Source table(s):** Change tracking / audit tables from the source system.

**SQL:**
```sql
SELECT
    <%=sourceSystem%> || '::' || "OBJECTID" AS "ObjectID",
    CAST("UDATE" || ' ' || "UTIME" AS TIMESTAMP) AS "Time",
    "USERNAME" AS "ChangedBy",
    "FNAME" AS "Attribute",
    "VALUE_OLD" AS "OldValue",
    "VALUE_NEW" AS "NewValue",
    CASE WHEN "USERNAME" = 'BATCH' THEN 'Automatic' ELSE 'Manual' END AS "ExecutionType"
FROM "CDPOS"
WHERE "OBJECTCLAS" = 'EINKBELEG'
    AND "TABNAME" = 'EKKO'
```

**Notes:**
- Change tracking SQL populates the `changeSqlFactoryDatasets` in the factory API
- The `ObjectID` column must match the object's `ID` format
- Include `Time`, `ChangedBy`, `Attribute`, `OldValue`, `NewValue`, `ExecutionType`



---



## 4.3 Object Relationship Transformations

For M:N relationships that use explicit relationship objects, provide the SQL to populate the relationship table.

**When applicable:** Only include this section for M:N relationships modeled with explicit relationship objects (e.g., `RelationshipThreeWayMatch`).

### Relationship: [RelationshipObjectName]

**Target table:** `o_custom_[RelationshipObjectName]`

**SQL:**
```sql
SELECT
    <%=sourceSystem%> || '::' || "KEY1" || '::' || "KEY2" AS "ID",
    <%=sourceSystem%> AS "SourceSystemInstance",
    <%=sourceSystem%> || '::' || "KEY1" AS "ObjectA",
    <%=sourceSystem%> || '::' || "KEY2" AS "ObjectB"
FROM "LINKING_TABLE"
```

**Notes:**
- Relationship objects are treated as regular objects in the factory API
- Their transformations populate foreign keys to both sides of the M:N relationship
- Include in the `relationshipTransformations` array of the factory if using the dedicated relationship transformation mechanism



---



## 5. Data Connection Technical IDs

> **Note for Consultants:** This section must be completed with the actual technical IDs from the target Celonis environment. If these IDs are not available in the provided documentation, the implementing consultant must fill them in before passing this file to the Builder scripts.

This section maps each data source to its technical connection identifier in the Celonis platform. These IDs are required by the Builder scripts (Scripts 23-24) to create factory files.

- **How to obtain these IDs:** In the Celonis platform, navigate to **Data Integration → Data Connections**. Each connection has a unique ID (UUID) visible in its settings or URL.

| Data Source Display Name | Source System Type | Data Connection ID (UUID) | Notes |
| :--- | :--- | :--- | :--- |
| (e.g., SAP ECC - Production) | (e.g., SAP ECC) | (e.g., `a1b2c3d4-e5f6-7890-abcd-ef1234567890`) | (e.g., Primary production system) |

**Instructions:**

1. List one row per data source / connection that feeds the OCPM model.

2. The **Data Connection ID** is a UUID that uniquely identifies the connection in the Celonis platform. It is used in factory configurations to bind transformations to their source.

3. If multiple environments exist (e.g., DEV, QA, PROD), list the connection ID for each environment or note which environment the ID corresponds to.

4. If the connection does not yet exist, mark the ID as `TBD` and create the connection in Celonis before running the Builder scripts.



---



# FINAL VALIDATION CHECKLIST

**SQL Completeness:**
- [ ] Does every object from Section 1 have an attribute transformation SQL in Section 4.1?
- [ ] Do all IDs use `<%=sourceSystem%>` and `::` delimiter?
- [ ] Do all foreign key columns produce values matching the target object's ID format?
- [ ] Are NULL values handled with `NULLIF` or `COALESCE` where appropriate?

**Change Tracking:**
- [ ] Have all objects with available change/audit data been covered in Section 4.2?
- [ ] Do change tracking SQLs include `ObjectID`, `Time`, `ChangedBy`, `Attribute`, `OldValue`, `NewValue`, `ExecutionType`?

**Relationship Transformations:**
- [ ] Have all M:N relationship objects been covered in Section 4.3?

**Data Connections:**
- [ ] Have all source systems been mapped to Data Connection IDs in Section 5?
- [ ] Are any Data Connection IDs marked as `TBD`?
