# OCPM Builder Assistant

A multi-stage AI-assisted pipeline for building Celonis Object-Centric Process Mining (OCPM) models from raw business inputs.

## Overview

This project contains a modular set of AI assistant prompts that work in sequence, each corresponding to a stage in a Celonis implementation:

| Stage | Module | Prompt File | Status |
| :--- | :--- | :--- | :--- |
| 0 | **Design Guidelines** | `Tools/0_Design_Guidelines.md` | Active |
| 1 | **Requirements Gathering** | `Tools/1_Requirements.md` | Active |
| 2 | **OCPM Builder** | `Tools/2_OCPM_Builder.md` | Active |
| 3 | **Knowledge Model** | `Tools/3_Knowledge_Model.md` | Planned |
| 4 | **Apps** | `Tools/4_Apps.md` | Planned |

Stage 0 is not an executable stage — it is a reference document consumed by Stage 1 and Stage 2 to enforce consistent naming conventions, ID construction, relationship patterns, and modeling standards.

## Project Structure

```
.
├── app/                              <- Python automation app
│   ├── llm/
│   │   ├── base.py                   <- Abstract LLM interface
│   │   └── anthropic.py              <- Claude adapter (swap for other providers)
│   ├── config.py                     <- Configuration loader
│   ├── tools.py                      <- File I/O and validation tools
│   ├── orchestrator.py               <- Multi-stage pipeline engine
│   └── run.py                        <- CLI entry point
├── Tools/                            <- Prompt instructions for each module
│   ├── 0_Design_Guidelines.md        <- Design guidelines & modeling standards
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
├── config.yaml                       <- App configuration (LLM provider, model, paths)
├── requirements.txt                  <- Python dependencies
└── README.md
```

---

## Stage 0: Design Guidelines (Reference)

**File:** `Tools/0_Design_Guidelines.md`

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

## Stage 1: Requirements Gathering

**Prompt file:** `Tools/1_Requirements.md`

### What it does

Converts raw, unstructured business inputs into a standardized OCPM requirements document that the Builder can consume. It acts as the "analyst" that interprets your project materials and translates them into a formal specification, enforcing the naming conventions and modeling standards defined in `Tools/0_Design_Guidelines.md`.

### Input

Place all your project files in `Input/Project input files/`. The assistant accepts any combination of:

- Text / Markdown / CSV files (process descriptions, data schemas, field mappings)
- JSON files (table definitions, API schemas, data dictionaries)
- Images (Figma boards, ERDs, process flow diagrams)
- PDFs (technical documentation, architecture docs)
- Meeting transcripts / notes (workshop outputs, stakeholder interviews)

### Output

A Markdown file saved to `Output/1_Requirements/<ProcessName>_Requirements.md` containing:

| Section | Description |
| :--- | :--- |
| 0. Process Overview & Source System Context | Business problem, source system type, source tables summary |
| 1. Core Object Definitions | Business entities with attributes, data types, and primary keys |
| 2. Event Log Definitions | Activities/milestones with timestamps and foreign key linkages |
| 3. Relationship Modeling | Object-to-Object and Object-to-Event relationships with cardinality |
| 4. Data Transformation Logic | SQL/PQL extraction logic for objects and events |
| 5. Data Connection Technical IDs | UUID mappings for Celonis data connections (to be filled by consultant) |

### Usage

1. Drop your project files into `Input/Project input files/`.
2. Open a new AI chat session and load `Tools/1_Requirements.md` as the system prompt.
3. The assistant will scan the input folder, read all files, and generate the requirements document in `Output/1_Requirements/`.

---

## Stage 2: OCPM Builder

**Prompt file:** `Tools/2_OCPM_Builder.md`

### What it does

Takes the structured requirements specification (from Stage 1) and generates a complete, import-ready set of Celonis OCPM JSON configuration files. It also validates all output against the reference template in `Input/TEMPLATE/` to ensure format compliance.

### Input

The Markdown requirements file generated by Stage 1 (or a manually authored equivalent) containing:

- Business problem / process description
- Data schema (tables, columns, types, relationships)
- Source system type

### Output

A full Celonis OCPM package written to `Output/2_OCPM_Builder/` with this folder structure:

| Folder | Files | Description |
| :--- | :--- | :--- |
| `catalog_processes/` | `catalog_processes_<Process>.json` | Process catalog metadata |
| `data_sources/` | `data_sources_<Name>.json` | Data connection definitions |
| `environments/` | `environments_develop.json`, `environments_production.json` | Environment configs |
| `events/` | `event_<EventName>.json` | Event/activity definitions |
| `factories/` | `factories_<Entity>.json` | Data transformation configurations |
| `objects/` | `object_<ObjectName>.json` | Business object definitions |
| `perspectives/` | `perspective_<Process>.json` | Analytical view definitions |
| `processes/` | `process_<Process>.json` | Process groupings of objects and events |
| `sql_statements/` | `sql_statement_<Entity>.json` | SQL/PQL transformation logic |
| `categories/` | *(empty)* | Reserved |
| `parameters/` | *(empty)* | Reserved |
| `template_factories/` | *(empty)* | Reserved |
| `templates/` | *(empty)* | Reserved |

### Validation

After generating all files, the Builder runs a validation step that checks:

- **Folder structure** matches the 13 subfolders in `Input/TEMPLATE/`
- **File naming** uses the correct prefixes (`object_`, `event_`, `factories_`, etc.)
- **JSON schema** for each file type has all required keys matching the template structure
- **Mandatory fields** exist (e.g., `ID` on objects, `ID` + `Time` on events)
- **Cross-file consistency** (relationships reference existing objects, factory IDs match, counts are accurate)

### Usage

1. Ensure the requirements Markdown file is ready (either from Stage 1 or manually created).
2. Open a new AI chat session and load `Tools/2_OCPM_Builder.md` as the system prompt.
3. Provide the requirements file as input.
4. The assistant generates all JSON files in `Output/2_OCPM_Builder/` and runs validation against the template.

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
Input/Project input files/     Stage 1: Requirements       Output/1_Requirements/
  (transcripts, schemas,   -->   Gathering              -->   <Process>_Requirements.md
   ERDs, Figma, docs...)

Output/1_Requirements/          Stage 2: OCPM            Output/2_OCPM_Builder/
  <Process>_Requirements.md -->   Builder              -->   objects/, events/, factories/,
                                                              sql_statements/, processes/, ...

Output/2_OCPM_Builder/          Stage 3: Knowledge       Output/3_Knowledge_Model/
  (OCPM JSON files)         -->   Model (planned)      -->   (KPIs, filters, variables, ...)

Output/3_Knowledge_Model/       Stage 4: Apps            Output/4_Apps/
  (KM config files)         -->   (planned)            -->   views/, dashboards/, actions/, ...
```

## Running with the Python App (Automated)

The `app/` folder provides a CLI tool that automates the full pipeline. The LLM layer is isolated behind an adapter pattern, so the provider can be swapped by editing `config.yaml`.

### First-Time Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your API key
export ANTHROPIC_API_KEY="sk-ant-..."

# 3. (Optional) Edit config.yaml to change model or provider
```

### Running the Pipeline

```bash
# Full pipeline: Stage 1 + Stage 2 + Validation
python app/run.py

# Only Stage 1 (analyze inputs, generate requirements)
python app/run.py --stage 1

# Only Stage 2 (generate JSON files from existing requirements)
python app/run.py --stage 2

# Only validate existing Output/2_OCPM_Builder/ against the template (no LLM calls)
python app/run.py --validate-only
```

### Typical Consultant Workflow

| Step | Action | Command |
| :--- | :--- | :--- |
| 1 | Drop project files into `Input/Project input files/` | *(manual)* |
| 2 | Run the full pipeline | `python app/run.py` |
| 3 | Review `Output/1_Requirements/<Process>_Requirements.md` | *(manual)* |
| 4 | Fill in Data Connection Technical IDs (Section 5) if not auto-detected | *(manual)* |
| 5 | If requirements need edits, fix the `.md` file and re-run Stage 2 | `python app/run.py --stage 2` |
| 6 | Zip `Output/2_OCPM_Builder/` contents and import into Celonis | *(manual)* |

### Switching LLM Provider

The LLM is configured in `config.yaml`:

```yaml
llm:
  provider: anthropic                # Change to: openai, google, ollama
  model: claude-sonnet-4-5-20250929  # Model ID for the chosen provider
  api_key: ${ANTHROPIC_API_KEY}      # Environment variable reference
```

To add a new provider, create a new adapter file in `app/llm/` that implements the `LLMBase` interface from `app/llm/base.py`, and register it in `app/llm/__init__.py`.

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
