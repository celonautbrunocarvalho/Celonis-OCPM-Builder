# Celonis Builder Assistant

A multi-stage AI-assisted pipeline for building Celonis Object-Centric Process Mining (OCPM) models from raw business inputs.

## Overview

This project contains a modular set of AI assistant prompts organized in a two-tier pipeline:

- **1x series — Requirements Builders:** Gather requirements from the user and produce structured requirements Markdown files
- **2x series — API Builders:** Read requirements and deploy entities to Celonis via the BL API
- **3x series — KM & Views Requirements:** Define Knowledge Model and View requirements
- **4x series — KM & Views Builders:** Deploy Knowledge Model and Views to Celonis

| Script | Module | Prompt File | Status |
| :--- | :--- | :--- | :--- |
| 0 | **Design Guidelines** | `Tools/Libraries/0_Design_Guidelines.md` | Active |
| — | **API Reference** | `Tools/Libraries/1_OCPM_API_Reference.md` | Active |
| 11 | **Requirements: Objects** | `Tools/11_Requirements_Objects.md` | Active |
| 12 | **Requirements: Events** | `Tools/12_Requirements_Events.md` | Active |
| 13 | **Requirements: Object Transformations** | `Tools/13_Requirements_Object_Transformations.md` | Active |
| 14 | **Requirements: Event Transformations** | `Tools/14_Requirements_Event_Transformations.md` | Active |
| 15 | **Requirements: Perspectives** | `Tools/15_Requirements_Perspectives.md` | Active |
| 21 | **Builder: Objects** | `Tools/21_Objects_Builder.md` | Active |
| 22 | **Builder: Events** | `Tools/22_Events_Builder.md` | Active |
| 23 | **Builder: Object Transformations** | `Tools/23_Object_Transformations_Builder.md` | Active |
| 24 | **Builder: Event Transformations** | `Tools/24_Event_Transformations_Builder.md` | Active |
| 25 | **Builder: Perspectives** | `Tools/25_Perspective_Builder.md` | Active |
| 31 | **Requirements: Knowledge Model** | `Tools/31_Requirements_Knowledge_Model.md` | Planned |
| 32 | **Requirements: Views** | `Tools/32_Requirements_Views.md` | Planned |
| 41 | **Builder: Knowledge Model** | `Tools/41_Knowledge_Model_Builder.md` | Planned |
| 42 | **Builder: Views** | `Tools/42_Views_Builder.md` | Planned |

## Project Structure

```
.
├── Tools/                                          <- Prompt instructions for each module
│   ├── Libraries/                                  <- Supporting reference documents
│   │   ├── 0_Design_Guidelines.md                  <- Design guidelines & modeling standards
│   │   └── 1_OCPM_API_Reference.md                 <- BL API reference for programmatic OCPM management
│   ├── 11_Requirements_Objects.md                  <- Script 11: Objects requirements
│   ├── 12_Requirements_Events.md                   <- Script 12: Events requirements
│   ├── 13_Requirements_Object_Transformations.md   <- Script 13: Object transformation requirements
│   ├── 14_Requirements_Event_Transformations.md    <- Script 14: Event transformation requirements
│   ├── 15_Requirements_Perspectives.md             <- Script 15: Perspective requirements
│   ├── 21_Objects_Builder.md                       <- Script 21: Deploy objects to Celonis
│   ├── 22_Events_Builder.md                        <- Script 22: Deploy events to Celonis
│   ├── 23_Object_Transformations_Builder.md        <- Script 23: Deploy object SQL factories
│   ├── 24_Event_Transformations_Builder.md         <- Script 24: Deploy event SQL factories
│   ├── 25_Perspective_Builder.md                   <- Script 25: Deploy perspectives to Celonis
│   ├── 31_Requirements_Knowledge_Model.md          <- Script 31: Knowledge Model requirements (planned)
│   ├── 32_Requirements_Views.md                    <- Script 32: Views requirements (planned)
│   ├── 41_Knowledge_Model_Builder.md               <- Script 41: Deploy Knowledge Model (planned)
│   └── 42_Views_Builder.md                         <- Script 42: Deploy Views (planned)
├── Input/
│   ├── Project input files/                        <- Place your raw project files here
│   ├── References/                                 <- Modeling guidelines and catalog reference
│   │   ├── Catalog Guidelines & Modeling Best Practices V1.0.pdf
│   │   └── CATALOG_CORE_REFERENCE/                 <- Celonis catalog export
│   └── TEMPLATE/                                   <- Reference template (valid Celonis OCPM export)
├── Output/                                         <- All generated outputs, organized by module
│   ├── 1_Requirements/                             <- Requirements specs (Markdown)
│   ├── 2_OCPM_Builder/                             <- Deployed via API (no local files)
│   ├── 3_Knowledge_Model/                          <- Knowledge Model configs (planned)
│   └── 4_Apps/                                     <- App configs (planned)
└── README.md
```

---

## Libraries

### Design Guidelines (Reference)

**File:** `Tools/Libraries/0_Design_Guidelines.md`

A consolidated reference document containing all OCPM design principles, naming conventions, and modeling standards. Derived from the *Catalog Guidelines & Modeling Best Practices V1.0* and the *CATALOG_CORE_REFERENCE* export. Consumed by all scripts to enforce consistent naming, ID construction, relationship patterns, and modeling standards.

### OCPM API Reference

**File:** `Tools/Libraries/1_OCPM_API_Reference.md`

A comprehensive reference for the Celonis Business Landscape (BL) API. Covers complete JSON schemas for objects, events, SQL factories, and perspectives. Used by all Builder scripts (2x series) for programmatic deployment.

---

## 1x Series: Requirements Builders

These scripts gather requirements from the user and produce structured Markdown specification files.

### Script 11: Requirements — Objects

**File:** `Tools/11_Requirements_Objects.md` | **Output:** `Output/1_Requirements/<ProcessName>_Objects.md`

Converts raw business inputs into object definitions (Section 0: Process Overview, Section 1: Core Object Definitions, Section 3.1: O:O Relationships, Section 3.4: Relationship Path & Cycle Analysis). Includes attributes, data types, primary keys, cardinality, and LINK/EMBED strategy recommendations.

### Script 12: Requirements — Events

**File:** `Tools/12_Requirements_Events.md` | **Output:** `Output/1_Requirements/<ProcessName>_Events.md`

**Input:** Script 11 output + original project materials.

Defines event log definitions (Section 2) and object-to-event linkages (Section 3.2). Ensures every transactional object has at least one event. Includes mandatory fields (ID, Time, ExecutedBy, ExecutionType) and event-specific attributes.

### Script 13: Requirements — Object Transformations

**File:** `Tools/13_Requirements_Object_Transformations.md` | **Output:** `Output/1_Requirements/<ProcessName>_ObjectTransformations.md`

**Input:** Script 11 output + source system details.

Defines SQL extraction logic for objects: attribute transformations (Section 4.1), change tracking SQL (Section 4.2), relationship transformations (Section 4.3), and data connection mappings (Section 5).

### Script 14: Requirements — Event Transformations

**File:** `Tools/14_Requirements_Event_Transformations.md` | **Output:** `Output/1_Requirements/<ProcessName>_EventTransformations.md`

**Input:** Scripts 11, 12, 13 outputs.

Defines SQL extraction logic for events (Section 4.4): create events, change events, status events, approval events, etc. Covers events sourced from raw tables and from OCPM object tables.

### Script 15: Requirements — Perspectives

**File:** `Tools/15_Requirements_Perspectives.md` | **Output:** `Output/1_Requirements/<ProcessName>_Perspectives.md`

**Input:** Scripts 11, 12 outputs.

Defines perspective definitions (Section 6): objects with per-relationship LINK/EMBED strategies, events, projections with lead objects, and custom event logs. Enforces cycle-free validation.

---

## 2x Series: API Builders

These scripts read the requirements Markdown files and deploy entities to Celonis via the BL API.

### Script 21: Builder — Objects

**File:** `Tools/21_Objects_Builder.md`

**Input:** Script 11 output + Celonis connection parameters.

Deploys objects to Celonis using the 3-pass approach (create without relationships → add relationships → handle M:N).

### Script 22: Builder — Events

**File:** `Tools/22_Events_Builder.md`

**Input:** Script 12 output + Celonis connection parameters. **Requires:** Script 21 completed.

Deploys events to Celonis with foreign key linkages to objects.

### Script 23: Builder — Object Transformations

**File:** `Tools/23_Object_Transformations_Builder.md`

**Input:** Script 13 output + Celonis connection parameters + Data Connection mappings. **Requires:** Script 21 completed.

Creates SQL factories for objects and loads attribute SQL, change tracking SQL, and relationship transformations.

### Script 24: Builder — Event Transformations

**File:** `Tools/24_Event_Transformations_Builder.md`

**Input:** Script 14 output + Celonis connection parameters + Data Connection mappings. **Requires:** Scripts 21-22 completed, Script 23 recommended.

Creates SQL factories for events and loads event generation SQL.

### Script 25: Builder — Perspectives

**File:** `Tools/25_Perspective_Builder.md`

**Input:** Script 15 output + Celonis connection parameters. **Requires:** Scripts 21-22 completed.

Deploys perspectives with objects (LINK/EMBED strategies), events, and projections.

---

## 3x-4x Series: Knowledge Model & Views (Planned)

### Script 31: Requirements — Knowledge Model

**File:** `Tools/31_Requirements_Knowledge_Model.md` | Defines KPIs, filters, variables, records, and scopes.

### Script 32: Requirements — Views

**File:** `Tools/32_Requirements_Views.md` | Defines views, dashboards, components, and action flows.

### Script 41: Builder — Knowledge Model

**File:** `Tools/41_Knowledge_Model_Builder.md` | Deploys Knowledge Model to Celonis.

### Script 42: Builder — Views

**File:** `Tools/42_Views_Builder.md` | Deploys application views and dashboards.

> These modules are under development.

---

## End-to-End Workflow

```
                    REQUIREMENTS (1x)                              BUILDERS (2x)
                    ─────────────────                              ─────────────

User inputs    ──→  Script 11: Objects        ──→  Script 21: Objects Builder        ──→  Celonis
(transcripts,       ↓                                                                     Data Pool
 schemas,      ──→  Script 12: Events         ──→  Script 22: Events Builder         ──→  (Objects,
 images,            ↓                                                                      Events)
 docs)         ──→  Script 13: Obj. Transforms──→  Script 23: Obj. Transform Builder ──→  (SQL
               ──→  Script 14: Evt. Transforms──→  Script 24: Evt. Transform Builder ──→   Factories)
               ──→  Script 15: Perspectives   ──→  Script 25: Perspective Builder    ──→  (Perspectives)

                    ANALYTICS (3x-4x)
                    ─────────────────

               ──→  Script 31: KM Requirements──→  Script 41: KM Builder             ──→  (Knowledge
               ──→  Script 32: View Reqs      ──→  Script 42: Views Builder          ──→   Model, Apps)
```

### Execution Order

The pipeline must be executed in order due to dependencies:

| Step | Script | Prerequisites |
| :--- | :--- | :--- |
| 1 | Script 11 (Objects Requirements) | User input materials |
| 2 | Script 12 (Events Requirements) | Script 11 output |
| 3 | Script 13 (Object Transformations Requirements) | Script 11 output |
| 4 | Script 14 (Event Transformations Requirements) | Scripts 11, 12, 13 outputs |
| 5 | Script 15 (Perspectives Requirements) | Scripts 11, 12 outputs |
| 6 | Script 21 (Objects Builder) | Script 11 output + connection params |
| 7 | Script 22 (Events Builder) | Script 12 output + Script 21 deployed |
| 8 | Script 23 (Object Transformations Builder) | Script 13 output + Script 21 deployed |
| 9 | Script 24 (Event Transformations Builder) | Script 14 output + Scripts 21-22 deployed |
| 10 | Script 25 (Perspective Builder) | Script 15 output + Scripts 21-22 deployed |
| 11 | Script 31 (KM Requirements) | Scripts 11, 12, 15 outputs |
| 12 | Script 32 (View Requirements) | Script 31 output |
| 13 | Script 41 (KM Builder) | Script 31 output + Scripts 21-25 deployed |
| 14 | Script 42 (Views Builder) | Script 32 output + Script 41 deployed |

**Note:** Scripts 13 and 15 can run in parallel (both depend only on Script 11/12). Scripts 23 and 25 can also run in parallel after Script 21 is deployed.

---

## Usage

This project is designed to be used with any LLM interface that supports system prompts and file operations (e.g., Claude Code, Google Gemini Gems, ChatGPT with Code Interpreter, GitHub Copilot Workspace, etc.).

### Typical Consultant Workflow

| Step | Action | How |
| :--- | :--- | :--- |
| 1 | Prepare project materials | Gather process descriptions, data schemas, ERDs, technical docs |
| 2 | Run Script 11 (Objects) | Load prompt, provide project materials |
| 3 | Run Script 12 (Events) | Load prompt, provide Script 11 output + materials |
| 4 | Run Scripts 13-15 | Load prompts, provide previous outputs |
| 5 | Review all requirements | Manual review of generated Markdown files |
| 6 | Gather Celonis connection params | Team URL, API Key, Workspace ID, Environment, Data Connection IDs |
| 7 | Run Scripts 21-25 | Load prompts, provide connection params + requirements |
| 8 | Monitor deployment progress | Watch real-time progress as entities are created in Celonis |
| 9 | Verify in Celonis UI | Data Integration → Data Pool → Verify entities |
| 10 | Load data | Execute factories to populate objects and events |

### Using with External LLM Tools

**Option 1: Claude Code**
```bash
# Clone or sync this repository
# Open in VS Code with Claude Code extension
# Load the desired script prompt (e.g., Tools/11_Requirements_Objects.md)
# The assistant will automatically read files from Input/ and write to Output/
```

**Option 2: Google Gemini Gems**
```
# Create a new Gem per script
# Copy the contents of the script file as the Gem's instruction set
# Upload project files or provide previous script outputs
```

**Option 3: ChatGPT / Claude.ai Web Interface**
```
# Start a new conversation per script
# Copy/paste the full contents of the script prompt
# Upload your project files or previous outputs
# Copy the generated output to Output/1_Requirements/
```

---

## Reference Materials

### Template (`Input/TEMPLATE/`)

A complete, valid Celonis OCPM export (SAP ECC Procurement, Accounts Payable, Order Management, etc.) used as format reference and validation baseline.

### References (`Input/References/`)

Source materials used to build the Design Guidelines:
- **Catalog Guidelines & Modeling Best Practices V1.0.pdf** — Official Celonis document
- **CATALOG_CORE_REFERENCE/** — Extracted Celonis catalog export (346 JSON files)
