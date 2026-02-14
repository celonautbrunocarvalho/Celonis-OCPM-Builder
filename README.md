# OCPM Builder Assistant

A multi-stage AI-assisted pipeline for building Celonis Object-Centric Process Mining (OCPM) models from raw business inputs.

## Overview

This project contains a modular set of AI assistant prompts that work in sequence, each corresponding to a stage in a Celonis implementation:

| Stage | Module | Prompt File | Status |
| :--- | :--- | :--- | :--- |
| 0 | **Design Guidelines** | `Tools/Libraries/0_Design_Guidelines.md` | Active |
| 1 | **Requirements Gathering** | `Tools/1_Requirements.md` | Active |
| 2 | **OCPM Builder** | `Tools/2_OCPM_Builder.md` | Active |
| 3 | **Knowledge Model** | `Tools/3_Knowledge_Model.md` | Planned |
| 4 | **Apps** | `Tools/4_Apps.md` | Planned |

Stage 0 is not an executable stage — it is a reference document consumed by Stage 1 and Stage 2 to enforce consistent naming conventions, ID construction, relationship patterns, and modeling standards.

## Project Structure

```
.
├── Tools/                            <- Prompt instructions for each module
│   ├── Libraries/                    <- Supporting reference documents
│   │   ├── 0_Design_Guidelines.md    <- Design guidelines & modeling standards
│   │   └── 1_OCPM_API_Reference.md   <- BL API reference for programmatic OCPM management
│   ├── 1_Requirements.md             <- Stage 1: Requirements Gathering
│   ├── 2_OCPM_Builder.md             <- Stage 2: OCPM JSON Builder
│   ├── 3_Knowledge_Model.md          <- Stage 3: Knowledge Model (planned)
│   └── 4_Apps.md                     <- Stage 4: Apps (planned)
├── Input/
│   ├── Project input files/          <- Place your raw project files here
│   ├── References/                   <- Modeling guidelines and catalog reference
│   │   ├── Catalog Guidelines & Modeling Best Practices V1.0.pdf
│   │   └── CATALOG_CORE_REFERENCE/   <- Celonis catalog export (objects, events, SQL, etc.)
│   └── TEMPLATE/                     <- Reference template (valid Celonis OCPM export)
├── Output/                           <- All generated outputs, organized by module
│   ├── 1_Requirements/               <- Requirements spec (Markdown)
│   ├── 2_OCPM_Builder/               <- OCPM JSON config files
│   ├── 3_Knowledge_Model/            <- Knowledge Model configs (planned)
│   └── 4_Apps/                       <- App configs (planned)
│       ├── views/
│       ├── components/
│       ├── dashboards/
│       ├── actions/
│       └── assets/
└── README.md
```

---

## Stage 0: Design Guidelines (Reference)

**File:** `Tools/Libraries/0_Design_Guidelines.md`

### What it is

A consolidated reference document containing all OCPM design principles, naming conventions, and modeling standards. It was derived from two authoritative sources:

- **Catalog Guidelines & Modeling Best Practices V1.0** (PDF) — Celonis official guidelines covering catalog taxonomy (Core/Extension/SSDM), discovery and modeling principles, event modeling complexities, attribute naming conventions, relationship rules, and perspective strategies.
- **CATALOG_CORE_REFERENCE** (catalog export) — Real-world patterns extracted from the current Celonis catalog deployment, including 43+ objects, 62+ events, 102+ factories, and 102+ SQL statements.

### Key Contents

| Section | Covers |
| :--- | :--- |
| Catalog Taxonomy | Core vs Extension vs SSDM decision framework |
| General Design Principles | Discovery principles, modeling principles (#1–#5) |
| Object Naming | PascalCase rules, attribute suffix table, categories, color coding |
| Event Naming | Verb+Object pattern, mandatory fields, event type patterns |
| ID Construction | `::` delimiter, `<%=sourceSystem%>` parameter, composite key patterns |
| Relationships | Cardinality rules, `mapped_by` convention, M:N with explicit multilink objects |
| Perspectives | LINK vs EMBED strategies, lead object selection, projections |
| SQL Standards | Table prefixes (`o_`, `e_`, `c_`, `r_`, `x_`, `y_`), common transformation patterns |
| Factory Standards | Display name conventions, `data_connection_id` patterns |
| Deployment & Validation | Bottom-up validation checklist, source table type recommendations |
| Process Organization | Standard processes with their objects and events |

### How it's used

- **Stage 1** (`1_Requirements.md`) references the design guidelines to ensure requirements output follows correct naming conventions, ID patterns, and relationship structures.
- **Stage 2** (`2_OCPM_Builder.md`) uses the same standards when generating JSON configuration files.
- Both stages include validation checks against these guidelines.

---

## Libraries: OCPM API Reference

**File:** `Tools/Libraries/1_OCPM_API_Reference.md`

### What it is

A comprehensive reference document for the Celonis Business Landscape (BL) API that enables programmatic creation, reading, updating, and deletion of OCPM entities (objects, events, SQL factories, perspectives). This document is designed for LLM agents that need to interact with Celonis data pools programmatically via REST API calls.

### Key Contents

| Section | Covers |
| :--- | :--- |
| Prerequisites | API token requirements, workspace ID, environment parameters |
| API Endpoints | Full endpoint map for objects, events, SQL factories, perspectives, relationships |
| JSON Schema: Objects | Complete request/response schemas with real examples (PurchaseOrder) |
| JSON Schema: Events | Event-specific schemas with mandatory fields (CreatePurchaseDocument) |
| JSON Schema: SQL Factories | Factory creation/update payloads, SQL embedding, validation modes |
| JSON Schema: Perspectives | Perspective definitions with projections, LINK/EMBED strategies |
| Enums & Data Types | DataType, Cardinality, ResourceKind, SaveMode enums |
| Common Patterns | Namespace conventions, pagination, error handling, V1/V2 API selection |
| End-to-End Examples | Complete workflows for adding objects, events, factories, and perspectives |

### How it's used

- **LLM agents** that need to programmatically manage OCPM models can use this as a complete reference for API operations.
- **Stage 2 extensions** that generate and deploy OCPM configs directly to Celonis without manual import.
- **Automation scripts** that need to create or modify objects, events, transformations, or perspectives via the BL API.

This reference is based on the `export-import-ocpm` toolset and documents the V2 BL API endpoints (`/bl/api/v2/workspaces/{workspace_id}/...`).

---

## Stage 1: Requirements Gathering

**Prompt file:** `Tools/1_Requirements.md`

### What it does

Converts raw, unstructured business inputs into a standardized OCPM requirements document that the Builder can consume. It acts as the "analyst" that interprets your project materials and translates them into a formal specification, enforcing the naming conventions and modeling standards defined in `Tools/Libraries/0_Design_Guidelines.md`.

### Input

The user provides project materials directly to the LLM (paste text, upload files, provide context). Accepted input formats:

- Text / Markdown / CSV content (pasted process descriptions, data schemas, field mappings)
- JSON content (pasted table definitions, API schemas, data dictionaries)
- Uploaded files: Images (Figma boards, ERDs, process flow diagrams), PDFs (technical documentation, architecture docs)
- Audio transcripts / meeting notes (workshop outputs, stakeholder interviews)

### Output

A Markdown document named `<ProcessName>_Requirements.md` containing:

| Section | Description |
| :--- | :--- |
| 0. Process Overview & Source System Context | Business problem, source system type, source tables summary |
| 1. Core Object Definitions | Business entities with attributes, data types, and primary keys |
| 2. Event Log Definitions | Activities/milestones with timestamps and foreign key linkages |
| 3. Relationship Modeling | Object-to-Object and Object-to-Event relationships with cardinality |
| 4. Data Transformation Logic | SQL/PQL extraction logic for objects and events |
| 5. Data Connection Technical IDs | UUID mappings for Celonis data connections (to be filled by consultant) |

### Usage

1. Open a new AI chat session and load `Tools/1_Requirements.md` as the system prompt.
2. Provide your project materials (paste text, upload files, or provide context).
3. The assistant will process the materials and generate the requirements document.
   - **Local environments (Claude Code):** Saves to `Output/1_Requirements/<ProcessName>_Requirements.md`
   - **Cloud LLMs (Gemini Gems, ChatGPT):** Outputs the document in the conversation for you to save locally

---

## Stage 2: OCPM Builder

**Prompt file:** `Tools/2_OCPM_Builder.md`

### What it does

Takes the structured requirements specification (from Stage 1) and **deploys the OCPM model directly to Celonis** via the Business Landscape (BL) API. It programmatically creates objects, events, SQL transformations, and perspectives in the target Data Pool, eliminating the need for manual ZIP imports.

### Input

**Required inputs:**

1. **Requirements document** from Stage 1 containing:
   - Process overview, source system type
   - Object definitions (attributes, data types)
   - Event definitions (mandatory fields, foreign keys)
   - Relationships (O:O, O:E linkages, cardinality)
   - SQL transformations

2. **Celonis connection parameters:**
   - Team URL (e.g., `https://dev.eu-1.celonis.cloud`)
   - API Key (with "Edit Data Pool" permission)
   - Workspace ID (Data Pool UUID)
   - Environment (`develop` or `production`)
   - Data Connection ID mappings per source system

### How to obtain connection parameters

| Parameter | Where to find it |
| :--- | :--- |
| **Team URL** | Your Celonis platform URL (address bar when logged in) |
| **API Key** | Celonis Platform → Admin & Settings → API Keys → Create New Key (ensure "Edit Data Pool" permission) |
| **Workspace ID** | Data Integration → Data Pools → Select data pool → Settings → Copy UUID from URL or panel |
| **Environment** | Use `develop` for dev/test, `production` for live |
| **Data Connection IDs** | Data Integration → Data Connections → Select connection → Copy UUID from settings |

### Output

The OCPM model is deployed **directly to your Celonis Data Pool** via API calls. No local files are generated.

**Entities created:**

- **Objects** (business entities with attributes and relationships)
- **Events** (activities/milestones with timestamps)
- **SQL Transformations** (data extraction logic linked to objects/events)
- **Perspectives** (analytical views with projections)

**Progress reporting:**

The assistant provides real-time progress updates:

```
✓ Connected to https://dev.eu-1.celonis.cloud
✓ Data Pool: a1b2c3d4-e5f6-7890-abcd-ef1234567890
✓ Created Object: PurchaseOrder (ID: ...)
✓ Created Event: CreatePurchaseOrder (ID: ...)
✓ Created factory shell for: PurchaseOrder
✓ Updated transformation for: PurchaseOrder (SQL loaded)
✓ Created Perspective: Procurement
✓ OCPM Model Deployment Complete! (15 objects, 23 events, 38 transformations, 1 perspective)
```

### Execution Order

The Builder follows the correct dependency order:

1. **Connection validation** → Test API connectivity
2. **Objects** (3-pass approach to handle circular dependencies)
3. **Events** → Created after all objects exist
4. **Factories & SQL Transformations** → Object transformations first, then events
5. **Perspectives** → Created last after all entities exist

### Usage

1. Open a new AI chat session and load `Tools/2_OCPM_Builder.md` as the system prompt.
2. Provide the connection parameters (Team URL, API Key, Workspace ID, Environment, Data Connection mappings).
3. The assistant validates the connection and confirms it can proceed.
4. Provide the requirements document from Stage 1.
5. The assistant deploys the OCPM model directly to Celonis and reports progress for each entity created.

---

## Stage 3: Knowledge Model (Planned)

**Prompt file:** `Tools/3_Knowledge_Model.md`

Generates the Celonis Knowledge Model layer (KPIs, filters, variables, records, scopes) on top of the OCPM model. Output goes to `Output/3_Knowledge_Model/`.

> This module is under development.

---

## Stage 4: Apps (Planned)

**Prompt file:** `Tools/4_Apps.md`

Generates Celonis application configurations (views, dashboards, action flows) using the Knowledge Model and OCPM model. Output goes to `Output/4_Apps/`.

> This module is under development. The internal folder structure (`views/`, `components/`, `dashboards/`, `actions/`, `assets/`) will be refined in a future iteration.

---

## End-to-End Workflow

```
User-provided materials         Stage 1: Requirements       <Process>_Requirements.md
  (transcripts, schemas,   -->   Gathering              -->   (Markdown document)
   ERDs, Figma, docs...)

<Process>_Requirements.md       Stage 2: OCPM                Celonis Data Pool
  + Connection parameters   -->   Builder              -->   (Objects, Events, Factories,
  (Team URL, API Key, etc.)       (API-based execution)       SQL Transformations, Perspectives
                                                              deployed directly via BL API)

Celonis Data Pool               Stage 3: Knowledge           Output/3_Knowledge_Model/
  (OCPM entities)           -->   Model (planned)      -->   (KPIs, filters, variables, ...)

Output/3_Knowledge_Model/       Stage 4: Apps                Output/4_Apps/
  (KM config files)         -->   (planned)            -->   (views/, dashboards/, actions/, ...)
```

## Usage

This project is designed to be used with any LLM interface that supports system prompts and file operations (e.g., Claude Code, Google Gemini Gems, ChatGPT with Code Interpreter, GitHub Copilot Workspace, etc.).

### Typical Consultant Workflow

| Step | Action | How |
| :--- | :--- | :--- |
| 1 | Prepare project materials | Gather process descriptions, data schemas, ERDs, technical docs |
| 2 | Run Stage 1 (Requirements Gathering) | Load `Tools/1_Requirements.md` as system prompt, provide project materials |
| 3 | Review generated requirements document | *(manual review)* |
| 4 | Gather Celonis connection parameters | Obtain Team URL, API Key, Workspace ID, Environment, Data Connection IDs |
| 5 | Run Stage 2 (OCPM Builder) | Load `Tools/2_OCPM_Builder.md` as system prompt, provide connection params + requirements document |
| 6 | Monitor deployment progress | Watch real-time progress as entities are created in Celonis |
| 7 | Verify deployment in Celonis UI | Data Integration → Data Pool → Verify objects, events, transformations, perspectives exist |
| 8 | Load data into data pool | Execute factories to populate objects and events with actual data |

### Using with External LLM Tools

**Option 1: Claude Code**
```bash
# Clone or sync this repository
# Open in VS Code with Claude Code extension
# Load the desired stage prompt (Tools/1_Requirements.md or Tools/2_OCPM_Builder.md)
# The assistant will automatically read files from Input/ and write to Output/
```

**Option 2: Google Gemini Gems**
```
# Create a new Gem
# Copy the contents of Tools/1_Requirements.md as the Gem's instruction set
# Upload project files or provide links to the Input/ folder
# The Gem will generate the requirements document
```

**Option 3: ChatGPT / Claude.ai Web Interface**
```
# Start a new conversation
# Copy/paste the full contents of Tools/1_Requirements.md
# Upload your project files (transcripts, schemas, diagrams)
# Copy the generated output to Output/1_Requirements/<Process>_Requirements.md
```

**Option 4: GitHub Copilot Workspace / VS Code**
```
# Open this repository in VS Code
# Use Copilot Chat with the workspace context
# Reference the stage prompt file: "@workspace Tools/1_Requirements.md"
# The assistant will use the prompt as guidance and access Input/ files
```

### Integrating with Custom Automation

The prompts in `Tools/` are designed to be consumed programmatically. You can:

- **Clone this repository** into your automation environment (CI/CD, Zapier, Make, etc.)
- **Reference prompts via git URLs** for version-controlled instructions
- **Build custom integrations** using the BL API reference in `Tools/Libraries/1_OCPM_API_Reference.md`
- **Embed in Gemini Gems, Custom GPTs, or Claude Projects** for reusable AI assistants

---

## Reference Materials

### Template (`Input/TEMPLATE/`)

A complete, valid Celonis OCPM export (SAP ECC Procurement, Accounts Payable, Order Management, etc.). It serves two purposes:

1. **Format reference** for the Builder to understand the expected JSON structure
2. **Validation baseline** to verify generated output matches the platform's expected format

### References (`Input/References/`)

Source materials used to build the Design Guidelines:

- **Catalog Guidelines & Modeling Best Practices V1.0.pdf** — Official Celonis document covering catalog taxonomy, naming conventions, event modeling complexities, relationship patterns, perspective strategies, and deployment practices.
- **CATALOG_CORE_REFERENCE/** — Extracted Celonis catalog export containing 346 JSON files across objects, events, factories, SQL statements, processes, perspectives, categories, and more. Used to derive real-world naming patterns and structural conventions.
