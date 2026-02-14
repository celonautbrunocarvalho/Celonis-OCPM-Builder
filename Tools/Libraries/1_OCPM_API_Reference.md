# OCPM API Reference

This document provides an LLM agent with the complete instructions needed to programmatically create, read, update, and delete Objects, Events, SQL Factories (Transformations), and Perspectives in a Celonis OCPM data model via the Business Landscape (BL) API.

For naming conventions, ID construction, and modeling standards, refer to `0_Design_Guidelines.md`.



---



## 1. Prerequisites

| Parameter | Description | How to Obtain |
| :--- | :--- | :--- |
| `api_token` | Celonis API token with **Edit Data Pool** permission | Celonis Platform → Admin → API Keys |
| `workspace_id` | UUID of the target workspace (data pool) | URL path or Data Integration → Data Pool settings |
| `environment` | Target environment name | Typically `DEVELOPMENT` or `PRODUCTION` |
| `data_connection_id` | UUID of the data connection for SQL factories | Data Integration → Data Connections → connection settings or URL |

**Authentication:** All requests require the header `Authorization: Bearer {api_token}`.

**Base URL:** `https://{celonis_url}/bl/api/v2/workspaces/{workspace_id}`

> **V1 vs V2:** The API supports both V1 and V2 endpoints. V2 includes `workspace_id` in the path and is the current standard. V1 endpoints omit `workspace_id` (`/bl/api/v1/...`) and are only used when the `integration.ocdm-per-data-pool` feature flag is disabled. Always prefer V2.



---



## 2. API Endpoints

All endpoints below use the V2 base path. Append `?environment={environment}` as a query parameter to all requests.

### 2.1 Objects

| Method | Path | Description |
| :--- | :--- | :--- |
| GET | `/types/objects?page={n}` | List all object types (paginated, page starts at 0) |
| POST | `/types/objects` | Create a new object type |
| PUT | `/types/objects/{object_type_id}` | Update an existing object type |
| DELETE | `/types/objects/{object_type_id}` | Delete an object type |

### 2.2 Events

| Method | Path | Description |
| :--- | :--- | :--- |
| GET | `/types/events?page={n}` | List all event types (paginated) |
| POST | `/types/events` | Create a new event type |
| PUT | `/types/events/{event_type_id}` | Update an existing event type |
| DELETE | `/types/events/{event_type_id}` | Delete an event type |

### 2.3 SQL Factories (Transformations)

| Method | Path | Description |
| :--- | :--- | :--- |
| GET | `/factories/sql?requestMode=ALL&includeUserTemplateTransformations=true&page={n}` | List all SQL factories (paginated) |
| GET | `/factories/sql/{factory_id}` | Get a specific SQL factory with its transformations |
| POST | `/factories/sql` | Create a new SQL factory |
| PUT | `/factories/sql/{factory_id}` | Update an existing SQL factory |
| DELETE | `/factories/sql/{factory_id}` | Delete a SQL factory |

### 2.4 Perspectives

| Method | Path | Description |
| :--- | :--- | :--- |
| GET | `/perspectives?requestMode=ALL` | List all perspectives |
| POST | `/perspectives` | Create a new perspective |
| PUT | `/perspectives/{perspective_id}` | Update an existing perspective |
| DELETE | `/perspectives/{perspective_id}` | Delete a perspective |

### 2.5 Object Relationships

| Method | Path | Description |
| :--- | :--- | :--- |
| POST | `/types/objects/relationships` | Create an object-to-object relationship |

### 2.6 Global Parameters

| Method | Path | Description |
| :--- | :--- | :--- |
| GET | `/factories/parameters?page={n}` | List all global parameters (paginated) |
| POST | `/factories/parameters` | Create a global parameter |
| PUT | `/factories/parameters/{parameter_id}` | Update a global parameter |



---



## 3. JSON Schema: Objects

### 3.1 Request Body (POST / PUT)

```json
{
    "name": "PurchaseOrder",
    "namespace": "custom",
    "description": "A specific type of Purchasing Document...",
    "color": "#4608B3",
    "fields": [
        {
            "name": "ID",
            "namespace": "custom",
            "dataType": "CT_UTF8_STRING"
        },
        {
            "name": "SourceSystemInstance",
            "namespace": "custom",
            "dataType": "CT_UTF8_STRING"
        },
        {
            "name": "PurchaseOrganizationName",
            "namespace": "custom",
            "dataType": "CT_UTF8_STRING"
        },
        {
            "name": "CreationTime",
            "namespace": "custom",
            "dataType": "CT_INSTANT"
        },
        {
            "name": "IsCanceled",
            "namespace": "custom",
            "dataType": "CT_BOOLEAN"
        }
    ],
    "relationships": [
        {
            "name": "CreatedBy",
            "namespace": "custom",
            "cardinality": "HAS_ONE",
            "target": {
                "objectRef": {
                    "name": "User",
                    "namespace": "custom"
                },
                "mappedBy": null,
                "mappedByNamespace": null
            }
        },
        {
            "name": "PurchaseOrderLine",
            "namespace": "custom",
            "cardinality": "HAS_MANY",
            "target": {
                "objectRef": {
                    "name": "PurchaseOrderLine",
                    "namespace": "custom"
                },
                "mappedBy": "Header",
                "mappedByNamespace": "custom"
            }
        }
    ],
    "categories": [
        {
            "metadata": {
                "name": "Processes",
                "namespace": "celonis"
            },
            "values": [
                {
                    "name": "Procurement",
                    "namespace": "celonis"
                }
            ]
        }
    ],
    "tags": ["Procurement"]
}
```

### 3.2 Field Reference

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `name` | string | Yes | PascalCase object name (e.g., `PurchaseOrder`) |
| `namespace` | string | Yes | Always `"custom"` for user-created objects |
| `description` | string | No | Business description of the object |
| `color` | string | No | Hex color code for UI display |
| `fields` | array | Yes | List of attribute definitions (see below) |
| `relationships` | array | No | List of relationships to other objects (see below) |
| `categories` | array | No | Category assignments for process grouping |
| `tags` | array | No | String tags for filtering |
| `changeDate` | number | No | Epoch timestamp in milliseconds |

### 3.3 Field Definition

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `name` | string | Yes | Attribute name in PascalCase |
| `namespace` | string | Yes | Always `"custom"` |
| `dataType` | string | Yes | One of: `CT_UTF8_STRING`, `CT_DOUBLE`, `CT_BOOLEAN`, `CT_INSTANT`, `CT_LONG` |

> **Mandatory:** Every object must include a field named `ID` with type `CT_UTF8_STRING`.

### 3.4 Relationship Definition

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `name` | string | Yes | Relationship name (typically the target object name) |
| `namespace` | string | Yes | Always `"custom"` |
| `cardinality` | string | Yes | `"HAS_ONE"` (N:1) or `"HAS_MANY"` (1:N) |
| `target.objectRef.name` | string | Yes | Target object name |
| `target.objectRef.namespace` | string | Yes | Target object namespace |
| `target.mappedBy` | string | No | Inverse relationship name on the target object (required for `HAS_MANY`) |
| `target.mappedByNamespace` | string | No | Namespace of the inverse relationship |

### 3.5 Category Definition

| Field | Type | Description |
| :--- | :--- | :--- |
| `metadata.name` | string | Category name (e.g., `"Processes"`, `"hierarchy"`) |
| `metadata.namespace` | string | `"celonis"` for standard categories, `"custom"` for custom ones |
| `values[].name` | string | Category value name (e.g., `"Procurement"`, `"child"`) |
| `values[].namespace` | string | Namespace of the category value |



---



## 4. JSON Schema: Events

### 4.1 Request Body (POST / PUT)

```json
{
    "name": "CreatePurchaseDocument",
    "namespace": "custom",
    "description": "Represents the event when a Purchase Document is entered in the system.",
    "fields": [
        {
            "name": "ID",
            "namespace": "custom",
            "dataType": "CT_UTF8_STRING"
        },
        {
            "name": "Time",
            "namespace": "custom",
            "dataType": "CT_INSTANT"
        },
        {
            "name": "ExecutedBy",
            "namespace": "custom",
            "dataType": "CT_UTF8_STRING"
        },
        {
            "name": "ExecutionType",
            "namespace": "custom",
            "dataType": "CT_UTF8_STRING"
        },
        {
            "name": "DocumentCategory",
            "namespace": "custom",
            "dataType": "CT_UTF8_STRING"
        }
    ],
    "relationships": [
        {
            "name": "PurchaseDocument",
            "namespace": "custom",
            "cardinality": "HAS_ONE",
            "target": {
                "objectRef": {
                    "name": "PurchaseDocument",
                    "namespace": "custom"
                },
                "mappedBy": null,
                "mappedByNamespace": null
            }
        },
        {
            "name": "PurchaseOrder",
            "namespace": "custom",
            "cardinality": "HAS_ONE",
            "target": {
                "objectRef": {
                    "name": "PurchaseOrder",
                    "namespace": "custom"
                },
                "mappedBy": null,
                "mappedByNamespace": null
            }
        }
    ],
    "categories": [
        {
            "metadata": {
                "name": "Processes",
                "namespace": "celonis"
            },
            "values": [
                {
                    "name": "Procurement",
                    "namespace": "celonis"
                }
            ]
        }
    ],
    "tags": ["Procurement"]
}
```

### 4.2 Field Reference

The event schema is identical to the object schema (Section 3.2) with these differences:

- Events do not have a `color` field.
- Events do not have a `multiLink` flag.

### 4.3 Mandatory Event Fields

Every event **must** include these four fields:

| Field Name | Data Type | Description |
| :--- | :--- | :--- |
| `ID` | `CT_UTF8_STRING` | Unique event identifier. Pattern: `'[EventName]' \|\| '::' \|\| [BaseObject]."ID"` |
| `Time` | `CT_INSTANT` | Precise execution timestamp |
| `ExecutedBy` | `CT_UTF8_STRING` | User who performed the action |
| `ExecutionType` | `CT_UTF8_STRING` | `Automatic` or `Manual` |

### 4.4 Event-Type-Specific Fields

| Event Type | Additional Fields |
| :--- | :--- |
| Change | `ChangedAttribute`, `OldValue`, `NewValue` |
| Approval | `Level` |
| Block | `BlockType`, `BlockReason` |
| Status Change | `OldStatus`, `NewStatus` |

### 4.5 Event Relationships

Events connect to objects via `HAS_ONE` relationships. The relationship `name` is typically the object name. An event can relate to multiple objects (e.g., a `CreatePurchaseDocument` event links to both `PurchaseDocument` and `PurchaseOrder`).



---



## 5. JSON Schema: SQL Factories & Transformations

### 5.1 Creating a New Factory (POST)

To create a factory, send a POST request with this structure:

```json
{
    "factoryId": "",
    "namespace": "custom",
    "dataConnectionId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "target": {
        "entityRef": {
            "name": "ApprovePurchaseDocument",
            "namespace": "custom"
        },
        "kind": "EVENT"
    },
    "draft": true,
    "localParameters": [],
    "displayName": "ApprovePurchaseDocument",
    "userTemplateName": null
}
```

> **Note:** Set `factoryId` to an empty string for new factories — the server generates the UUID. Set `draft: true` to create in draft mode initially.

### 5.2 Updating a Factory with SQL (PUT)

After creating a factory, update it with the full transformation payload:

```json
{
    "dataConnectionId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "displayName": "ApprovePurchaseDocument - 2",
    "namespace": "custom",
    "target": {
        "entityRef": {
            "name": "ApprovePurchaseDocument",
            "namespace": "custom"
        },
        "kind": "EVENT"
    },
    "transformations": [
        {
            "namespace": "custom",
            "propertyNames": [
                "DocumentCategory",
                "ExecutedBy",
                "ExecutionType",
                "ID",
                "Level",
                "Time"
            ],
            "foreignKeyNames": [
                "PurchaseDocument",
                "PurchaseOrder"
            ],
            "propertySqlFactoryDatasets": [
                {
                    "id": "ApprovePurchaseDocumentAttributes",
                    "type": "SQL_FACTORY_DATA_SET",
                    "completeOverwrite": false,
                    "disabled": false,
                    "materialiseCte": false,
                    "overwrite": null,
                    "sql": "SELECT \n    'ApprovePurchaseDocument' || '::' || \"PurchaseDocument_Changes\".\"ID\"     AS \"ID\",\n    \"PurchaseDocument\".\"ID\"                                                  AS \"PurchaseDocument\",\n    \"PurchaseDocument\".\"DocumentCategory\"                                    AS \"DocumentCategory\",\n    \"PurchaseDocument\".\"ID\"                                                  AS \"PurchaseOrder\",\n    \"PurchaseDocument_Changes\".\"Time\"                                        AS \"Time\",\n    \"PurchaseDocument_Changes\".\"ChangedBy\"                                   AS \"ExecutedBy\",\n    \"PurchaseDocument_Changes\".\"NewValue\"                                    AS \"Level\",\n    \"PurchaseDocument_Changes\".\"ExecutionType\"                               AS \"ExecutionType\"\nFROM \"o_custom_PurchaseDocument\" AS \"PurchaseDocument\"\n    LEFT JOIN \"c_o_custom_PurchaseDocument\" AS \"PurchaseDocument_Changes\"\n        ON \"PurchaseDocument\".\"ID\" = \"PurchaseDocument_Changes\".\"ObjectID\"\nWHERE \"PurchaseDocument_Changes\".\"Attribute\" = 'ApprovalLevel'\n    AND \"PurchaseDocument_Changes\".\"Time\" IS NOT NULL"
                }
            ],
            "changeSqlFactoryDatasets": [],
            "relationshipTransformations": []
        }
    ],
    "localParameters": [],
    "saveMode": "VALIDATE"
}
```

### 5.3 Factory Field Reference

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `dataConnectionId` | string (UUID) | Yes | Data connection UUID. Use `"00000000-0000-0000-0000-000000000000"` for the standard OCPM schema connection |
| `displayName` | string | Yes | Human-readable factory name |
| `namespace` | string | Yes | Always `"custom"` |
| `target.entityRef.name` | string | Yes | Name of the target object or event |
| `target.entityRef.namespace` | string | Yes | Namespace of the target entity |
| `target.kind` | string | Yes | `"OBJECT"` or `"EVENT"` |
| `transformations` | array | Yes | List of transformation definitions |
| `localParameters` | array | No | Factory-specific parameters |
| `saveMode` | string | No | `"VALIDATE"` (default), `"SKIP_VALIDATION"`, or `"FORCE_SAVE"` |
| `disabled` | boolean | No | Whether the factory is disabled |
| `draft` | boolean | No | Whether the factory is in draft mode |

### 5.4 Transformation Definition

| Field | Type | Description |
| :--- | :--- | :--- |
| `namespace` | string | Always `"custom"` |
| `propertyNames` | array of strings | List of attribute names populated by this transformation |
| `foreignKeyNames` | array of strings | List of relationship names (foreign keys) populated by this transformation |
| `propertySqlFactoryDatasets` | array | SQL datasets for attribute population |
| `changeSqlFactoryDatasets` | array | SQL datasets for change log population (same structure as property datasets) |
| `relationshipTransformations` | array | Relationship-specific transformations |

### 5.5 SQL Factory Dataset

| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | string | Dataset identifier (e.g., `"PurchaseOrderAttributes"`) |
| `type` | string | Always `"SQL_FACTORY_DATA_SET"` |
| `sql` | string | The SQL statement to execute |
| `completeOverwrite` | boolean | If `true`, replaces all existing data on each run |
| `disabled` | boolean | If `true`, this dataset is skipped during execution |
| `materialiseCte` | boolean | If `true`, materializes CTEs for performance |
| `overwrite` | object or null | Overwrite configuration for incremental loads |

### 5.6 SQL Validation Fallback

When updating a factory, if SQL validation fails (e.g., referenced tables don't exist yet), automatically retry with `saveMode: "SKIP_VALIDATION"`. This allows saving transformations before the underlying tables are loaded.

### 5.7 SQL Table Naming Conventions

| Prefix | Purpose | Example |
| :--- | :--- | :--- |
| `o_custom_` | Object table | `o_custom_PurchaseOrder` |
| `e_custom_` | Event table | `e_custom_CreatePurchaseOrder` |
| `c_o_custom_` | Object change log | `c_o_custom_PurchaseDocument` |
| `r_custom_` | Relationship table | `r_custom_PurchaseOrderLine_Header` |
| `x_custom_` | Object extension | `x_custom_PurchaseOrder_ExtField` |
| `y_custom_` | Event extension | `y_custom_CreatePurchaseOrder_ExtField` |



---



## 6. JSON Schema: Perspectives

### 6.1 Request Body (POST / PUT)

```json
{
    "name": "Procurement",
    "namespace": "custom",
    "description": null,
    "defaultProjection": "PurchaseDocumentLine",
    "objects": [
        {
            "name": "PurchaseDocument",
            "namespace": "custom",
            "entityMetadata": {
                "name": "PurchaseDocument",
                "namespace": "custom"
            },
            "defaultAlias": "Purchase Document",
            "customAlias": null,
            "originRef": {
                "name": "Procurement",
                "namespace": "custom"
            },
            "relationships": [
                {
                    "name": "CreatedBy",
                    "namespace": "custom",
                    "originRef": {
                        "name": "Procurement",
                        "namespace": "custom"
                    },
                    "strategy": "EMBED"
                },
                {
                    "name": "Vendor",
                    "namespace": "custom",
                    "originRef": {
                        "name": "Procurement",
                        "namespace": "custom"
                    },
                    "strategy": "LINK"
                }
            ]
        }
    ],
    "events": [
        {
            "name": "CreatePurchaseDocument",
            "namespace": "custom",
            "entityMetadata": {
                "name": "CreatePurchaseDocument",
                "namespace": "custom"
            },
            "defaultAlias": "Create Purchase Document",
            "customAlias": null
        }
    ],
    "projections": [
        {
            "name": "PurchaseDocument",
            "leadObject": {
                "name": "PurchaseDocument",
                "namespace": "custom"
            },
            "events": [
                {
                    "name": "CreatePurchaseDocument",
                    "namespace": "custom"
                },
                {
                    "name": "ApprovePurchaseDocument",
                    "namespace": "custom"
                }
            ],
            "eventList": [],
            "originRef": {
                "name": "Procurement",
                "namespace": "custom"
            }
        }
    ],
    "categories": [],
    "tags": []
}
```

### 6.2 Field Reference

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `name` | string | Yes | Perspective name (typically the process name, e.g., `"Procurement"`) |
| `namespace` | string | Yes | Always `"custom"` |
| `description` | string | No | Business description |
| `defaultProjection` | string | Yes | Name of the default projection (lead object for the primary view) |
| `objects` | array | Yes | List of objects included in this perspective |
| `events` | array | No | List of events included in this perspective |
| `projections` | array | Yes | List of projections (analytical views) |
| `categories` | array | No | Category assignments |
| `tags` | array | No | String tags |

### 6.3 Perspective Object

| Field | Type | Description |
| :--- | :--- | :--- |
| `name` | string | Object name |
| `namespace` | string | Object namespace |
| `entityMetadata` | object | `{ "name": "...", "namespace": "..." }` — metadata reference |
| `defaultAlias` | string | Human-readable display name (spaces between PascalCase words) |
| `customAlias` | string or null | Custom override alias |
| `originRef` | object | `{ "name": "...", "namespace": "..." }` — perspective that defines this inclusion |
| `relationships` | array | List of relationship strategy overrides |

### 6.4 Relationship Strategy

Each relationship within a perspective object specifies how the related data is joined:

| Field | Type | Description |
| :--- | :--- | :--- |
| `name` | string | Relationship name (must match a relationship on the object) |
| `namespace` | string | Relationship namespace |
| `strategy` | string | `"LINK"` or `"EMBED"` |
| `originRef` | object | Perspective metadata reference |

**Strategy rules:**
- **`LINK`** — Used for transactional objects. Creates a foreign key join. Use for objects like `Vendor`, `Material` when they are shared across processes.
- **`EMBED`** — Used for master data. Denormalizes the related data into the parent. Use for objects like `User`, `CompanyCode` when they are lookup dimensions.

### 6.5 Projection

A projection defines an analytical view centered on a lead object.

| Field | Type | Description |
| :--- | :--- | :--- |
| `name` | string | Projection name (typically the lead object name) |
| `leadObject` | object | `{ "name": "...", "namespace": "..." }` — the central object for this view |
| `events` | array | List of `{ "name": "...", "namespace": "..." }` event references |
| `eventList` | array | Additional event ordering configuration (usually empty) |
| `originRef` | object | Perspective metadata reference |



---



## 7. Enums & Data Types

### 7.1 DataType

| Value | Description |
| :--- | :--- |
| `CT_UTF8_STRING` | Text / string values |
| `CT_DOUBLE` | Floating-point numbers (amounts, quantities) |
| `CT_BOOLEAN` | True/false flags |
| `CT_INSTANT` | Timestamps (ISO 8601 compatible) |
| `CT_LONG` | Integer values |

### 7.2 EntityRelationshipCardinality

| Value | Meaning | Description |
| :--- | :--- | :--- |
| `HAS_ONE` | N:1 | This entity has one related entity (many-to-one) |
| `HAS_MANY` | 1:N | This entity has many related entities (one-to-many). Requires `mappedBy` on the target |

### 7.3 ResourceKind (Factory Target)

| Value | Description |
| :--- | :--- |
| `OBJECT` | Factory targets an object type |
| `EVENT` | Factory targets an event type |
| `FIELD_EXTENSION` | Factory targets a field extension |
| `CATEGORY` | Factory targets a category |
| `CATEGORY_EXTENSION` | Factory targets a category extension |
| `PERSPECTIVE` | Factory targets a perspective |

### 7.4 SaveMode (Factory Validation)

| Value | Description |
| :--- | :--- |
| `VALIDATE` | Validate SQL before saving (default) |
| `SKIP_VALIDATION` | Skip SQL validation — use when source tables don't exist yet |
| `FORCE_SAVE` | Force save regardless of validation errors |



---



## 8. Common Patterns

### 8.1 Namespace Convention

- **`"custom"`** — All user-created entities (objects, events, factories, perspectives, fields, relationships).
- **`"celonis"`** — Celonis-provided catalog entities. Do not create entities in the `celonis` namespace.

### 8.2 Pagination

All list endpoints (GET) return paginated results. Use `page=0`, `page=1`, etc. Continue fetching until the response indicates no more pages (empty content array or `last: true` in the page metadata).

### 8.3 Entity IDs

- When creating entities (POST), the server generates a UUID.
- When updating entities (PUT), you must provide the server-generated UUID in the URL path.
- To update an existing entity, first GET all entities to find the target UUID, then PUT with the UUID.

### 8.4 Error Handling

- **409 Conflict:** Entity with the same name already exists. Use PUT to update instead.
- **400 Bad Request:** Invalid schema or missing required fields. Check field names and types.
- **422 Validation Error:** SQL validation failed. Retry with `saveMode: "SKIP_VALIDATION"`.
- **404 Not Found:** Entity or workspace does not exist. Verify `workspace_id` and entity UUID.

### 8.5 Workflow: Create a Complete Entity

The typical workflow for adding a new entity to the model:

1. **Create the type** — POST object or event type definition (fields, relationships, categories).
2. **Create the factory** — POST a new SQL factory targeting the entity (returns `factory_id`).
3. **Update the factory with SQL** — PUT the factory with the full transformation payload (SQL statement, property names, foreign key names).
4. **Update the perspective** — GET the existing perspective, add the new entity to the objects/events/projections arrays, PUT back.

### 8.6 OCPM Schema Data Connection

For factories that use the standard OCPM schema (e.g., referencing `o_custom_*` tables produced by other factories), use the data connection ID:

```
00000000-0000-0000-0000-000000000000
```

This is the built-in OCPM schema connection — not a real external data source.



---



## 9. End-to-End Example: Adding a New Object with Event

This example creates a `Supplier` object, a `CreateSupplier` event, their SQL factories, and adds them to an existing perspective.

### Step 1: Create the Object Type

**POST** `/types/objects?environment=DEVELOPMENT`

```json
{
    "name": "Supplier",
    "namespace": "custom",
    "description": "Represents a vendor/supplier in the procurement process.",
    "color": "#4608B3",
    "fields": [
        { "name": "ID", "namespace": "custom", "dataType": "CT_UTF8_STRING" },
        { "name": "SourceSystemInstance", "namespace": "custom", "dataType": "CT_UTF8_STRING" },
        { "name": "SupplierName", "namespace": "custom", "dataType": "CT_UTF8_STRING" },
        { "name": "Country", "namespace": "custom", "dataType": "CT_UTF8_STRING" },
        { "name": "CreationTime", "namespace": "custom", "dataType": "CT_INSTANT" },
        { "name": "IsBlocked", "namespace": "custom", "dataType": "CT_BOOLEAN" }
    ],
    "relationships": [],
    "categories": [
        {
            "metadata": { "name": "Processes", "namespace": "celonis" },
            "values": [{ "name": "Procurement", "namespace": "celonis" }]
        }
    ],
    "tags": ["Procurement"]
}
```

### Step 2: Create the Event Type

**POST** `/types/events?environment=DEVELOPMENT`

```json
{
    "name": "CreateSupplier",
    "namespace": "custom",
    "description": "Represents the creation of a new supplier record.",
    "fields": [
        { "name": "ID", "namespace": "custom", "dataType": "CT_UTF8_STRING" },
        { "name": "Time", "namespace": "custom", "dataType": "CT_INSTANT" },
        { "name": "ExecutedBy", "namespace": "custom", "dataType": "CT_UTF8_STRING" },
        { "name": "ExecutionType", "namespace": "custom", "dataType": "CT_UTF8_STRING" }
    ],
    "relationships": [
        {
            "name": "Supplier",
            "namespace": "custom",
            "cardinality": "HAS_ONE",
            "target": {
                "objectRef": { "name": "Supplier", "namespace": "custom" },
                "mappedBy": null,
                "mappedByNamespace": null
            }
        }
    ],
    "categories": [
        {
            "metadata": { "name": "Processes", "namespace": "celonis" },
            "values": [{ "name": "Procurement", "namespace": "celonis" }]
        }
    ],
    "tags": ["Procurement"]
}
```

### Step 3: Create the Object Factory

**POST** `/factories/sql?environment=DEVELOPMENT`

```json
{
    "factoryId": "",
    "namespace": "custom",
    "dataConnectionId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "target": {
        "entityRef": { "name": "Supplier", "namespace": "custom" },
        "kind": "OBJECT"
    },
    "draft": true,
    "localParameters": [],
    "displayName": "Supplier",
    "userTemplateName": null
}
```

**Response** returns `factory_id` (e.g., `"f1a2b3c4-d5e6-7890-abcd-ef1234567890"`).

### Step 4: Update the Object Factory with SQL

**PUT** `/factories/sql/f1a2b3c4-d5e6-7890-abcd-ef1234567890?environment=DEVELOPMENT`

```json
{
    "dataConnectionId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "displayName": "Supplier",
    "namespace": "custom",
    "target": {
        "entityRef": { "name": "Supplier", "namespace": "custom" },
        "kind": "OBJECT"
    },
    "transformations": [
        {
            "namespace": "custom",
            "propertyNames": ["Country", "CreationTime", "ID", "IsBlocked", "SourceSystemInstance", "SupplierName"],
            "foreignKeyNames": [],
            "propertySqlFactoryDatasets": [
                {
                    "id": "SupplierAttributes",
                    "type": "SQL_FACTORY_DATA_SET",
                    "completeOverwrite": false,
                    "disabled": false,
                    "materialiseCte": false,
                    "overwrite": null,
                    "sql": "SELECT\n    <%=sourceSystem%> || '::' || \"MANDT\" || '::' || \"LIFNR\"  AS \"ID\",\n    <%=sourceSystem%>                                          AS \"SourceSystemInstance\",\n    \"NAME1\"                                                    AS \"SupplierName\",\n    \"LAND1\"                                                    AS \"Country\",\n    CAST(\"ERDAT\" AS TIMESTAMP)                                 AS \"CreationTime\",\n    CASE WHEN \"SPERR\" = 'X' THEN TRUE ELSE FALSE END           AS \"IsBlocked\"\nFROM \"LFA1\""
                }
            ],
            "changeSqlFactoryDatasets": [],
            "relationshipTransformations": []
        }
    ],
    "localParameters": [],
    "saveMode": "VALIDATE"
}
```

### Step 5: Create the Event Factory

Repeat Steps 3–4 for the event, targeting `"kind": "EVENT"` and `"name": "CreateSupplier"`:

**SQL for the event factory dataset:**

```sql
SELECT
    'CreateSupplier' || '::' || <%=sourceSystem%> || '::' || "MANDT" || '::' || "LIFNR"  AS "ID",
    <%=sourceSystem%> || '::' || "MANDT" || '::' || "LIFNR"                               AS "Supplier",
    CAST("ERDAT" AS TIMESTAMP)                                                             AS "Time",
    "ERNAM"                                                                                AS "ExecutedBy",
    'Automatic'                                                                            AS "ExecutionType"
FROM "LFA1"
WHERE "ERDAT" IS NOT NULL
```

### Step 6: Update the Perspective

**GET** `/perspectives?requestMode=ALL&environment=DEVELOPMENT` → find the Procurement perspective UUID.

**PUT** `/perspectives/{perspective_id}?environment=DEVELOPMENT` → add `Supplier` to `objects` array and `CreateSupplier` to `events` array. Add a new projection with `Supplier` as lead object if needed.
