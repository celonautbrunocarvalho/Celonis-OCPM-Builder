"""Tool functions for file I/O and validation.

These are pure Python functions with ZERO LLM dependency.
They are exposed to the LLM as callable tools via function calling.
"""

import json
import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Tool registry — maps tool names to functions
# ---------------------------------------------------------------------------
TOOL_REGISTRY: dict = {}


def tool(func):
    """Decorator to register a function as a callable tool."""
    TOOL_REGISTRY[func.__name__] = func
    return func


# ---------------------------------------------------------------------------
# Path configuration (set by orchestrator before tools are called)
# ---------------------------------------------------------------------------
_paths = {
    "input_files": None,
    "template": None,
    "output": None,
}


def configure_paths(input_files: Path, template: Path, output: Path):
    """Set the base paths for all tool operations."""
    _paths["input_files"] = Path(input_files)
    _paths["template"] = Path(template)
    _paths["output"] = Path(output)


# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------

@tool
def scan_inputs() -> str:
    """List all files in the project input files folder."""
    input_dir = _paths["input_files"]
    if not input_dir.exists():
        return json.dumps({"error": f"Input directory not found: {input_dir}"})

    files = []
    for root, _, filenames in os.walk(input_dir):
        for fname in sorted(filenames):
            if fname.startswith("."):
                continue
            full_path = Path(root) / fname
            rel_path = full_path.relative_to(input_dir)
            files.append({
                "path": str(rel_path),
                "size_bytes": full_path.stat().st_size,
            })

    if not files:
        return json.dumps({
            "files": [],
            "message": (
                "No input files found. Please place your project files in: "
                f"{input_dir}\n"
                "Accepted file types: text, markdown, CSV, JSON, images, PDFs, "
                "meeting transcripts."
            ),
        })

    return json.dumps({"files": files, "count": len(files)})


@tool
def read_file(path: str) -> str:
    """Read a file from the project input files folder.

    Args:
        path: Relative path within the input files folder.
    """
    input_dir = _paths["input_files"]
    full_path = (input_dir / path).resolve()

    # Safety: ensure the path is within the input directory
    if not str(full_path).startswith(str(input_dir.resolve())):
        return json.dumps({"error": "Path traversal not allowed."})

    if not full_path.exists():
        return json.dumps({"error": f"File not found: {path}"})

    try:
        content = full_path.read_text(encoding="utf-8")
        return json.dumps({"path": path, "content": content})
    except UnicodeDecodeError:
        return json.dumps({
            "path": path,
            "error": "Binary file — cannot read as text.",
            "size_bytes": full_path.stat().st_size,
        })


@tool
def write_file(path: str, content: str) -> str:
    """Write a file to the Output folder.

    Args:
        path: Relative path within the Output folder (e.g., "objects/object_PurchaseOrder.json").
        content: The file content to write.
    """
    output_dir = _paths["output"]
    full_path = (output_dir / path).resolve()

    # Safety: ensure the path is within the output directory
    if not str(full_path).startswith(str(output_dir.resolve())):
        return json.dumps({"error": "Path traversal not allowed."})

    # Create parent directories as needed
    full_path.parent.mkdir(parents=True, exist_ok=True)

    full_path.write_text(content, encoding="utf-8")
    return json.dumps({"status": "ok", "path": path, "bytes_written": len(content.encode("utf-8"))})


@tool
def create_directory(path: str) -> str:
    """Create a subdirectory inside the Output folder.

    Args:
        path: Relative directory path within Output (e.g., "objects").
    """
    output_dir = _paths["output"]
    full_path = (output_dir / path).resolve()

    if not str(full_path).startswith(str(output_dir.resolve())):
        return json.dumps({"error": "Path traversal not allowed."})

    full_path.mkdir(parents=True, exist_ok=True)
    return json.dumps({"status": "ok", "path": path})


@tool
def list_template_folders() -> str:
    """List all subfolders in the reference template."""
    template_dir = _paths["template"]
    if not template_dir.exists():
        return json.dumps({"error": f"Template directory not found: {template_dir}"})

    folders = []
    for item in sorted(template_dir.iterdir()):
        if item.is_dir():
            file_count = sum(1 for f in item.iterdir() if f.is_file() and not f.name.startswith("."))
            folders.append({"name": item.name, "file_count": file_count})

    return json.dumps({"folders": folders, "count": len(folders)})


@tool
def read_template_file(path: str) -> str:
    """Read a file from the reference template folder.

    Args:
        path: Relative path within the template folder (e.g., "objects/object_PurchaseOrder.json").
    """
    template_dir = _paths["template"]
    full_path = (template_dir / path).resolve()

    if not str(full_path).startswith(str(template_dir.resolve())):
        return json.dumps({"error": "Path traversal not allowed."})

    if not full_path.exists():
        return json.dumps({"error": f"Template file not found: {path}"})

    try:
        content = full_path.read_text(encoding="utf-8")
        return json.dumps({"path": path, "content": content})
    except UnicodeDecodeError:
        return json.dumps({"path": path, "error": "Binary file — cannot read as text."})


@tool
def validate_output() -> str:
    """Validate the Output folder against the reference template.

    Checks folder structure, file naming, JSON schemas, mandatory fields,
    and cross-file consistency.
    """
    output_dir = _paths["output"]
    template_dir = _paths["template"]
    errors = []
    warnings = []

    # --- 1. Folder structure ---
    expected_folders = {
        item.name for item in template_dir.iterdir() if item.is_dir()
    }
    actual_folders = {
        item.name for item in output_dir.iterdir()
        if item.is_dir() and not item.name.startswith(".")
    }

    missing_folders = expected_folders - actual_folders
    extra_folders = actual_folders - expected_folders

    for f in sorted(missing_folders):
        errors.append(f"Missing folder: {f}/")
    for f in sorted(extra_folders):
        warnings.append(f"Unexpected folder: {f}/")

    # --- 2. File naming prefixes ---
    prefix_rules = {
        "objects": "object_",
        "events": "event_",
        "factories": "factories_",
        "sql_statements": "sql_statement_",
        "processes": "process_",
        "catalog_processes": "catalog_processes_",
        "perspectives": "perspective_",
        "data_sources": "data_sources_",
        "environments": "environments_",
    }

    for folder, prefix in prefix_rules.items():
        folder_path = output_dir / folder
        if not folder_path.exists():
            continue
        for f in folder_path.iterdir():
            if f.name.startswith("."):
                continue
            if not f.name.startswith(prefix):
                errors.append(f"Bad file name: {folder}/{f.name} (expected prefix '{prefix}')")
            if not f.name.endswith(".json"):
                errors.append(f"Not a JSON file: {folder}/{f.name}")

    # --- 3. JSON schema validation ---
    object_required_keys = {
        "categories", "change_date", "changed_by", "color", "created_by",
        "creation_date", "description", "fields", "id", "managed",
        "multi_link", "name", "namespace", "relationships", "tags",
    }
    event_required_keys = {
        "categories", "change_date", "changed_by", "created_by",
        "creation_date", "description", "fields", "id", "name",
        "namespace", "relationships", "tags",
    }
    factory_entry_keys = {
        "change_date", "changed_by", "created_by", "creation_date",
        "data_connection_id", "disabled", "display_name", "factory_id",
        "has_overwrites", "name", "namespace", "target",
        "user_factory_template_reference", "validation_status",
    }
    sql_entry_keys = {
        "change_date", "changed_by", "created_by", "creation_date",
        "data_connection_id", "description", "disabled", "display_name",
        "draft", "factory_id", "factory_validation_status",
        "has_user_template", "local_parameters", "namespace", "target",
        "transformations",
    }
    process_required_keys = {"name", "columns", "objects", "events"}
    catalog_required_keys = {
        "change_date", "changed_by", "created_by", "creation_date",
        "data_source_connections", "description", "display_name",
        "enable_date", "enabled", "event_count", "name", "object_count",
    }
    perspective_required_keys = {
        "base_ref", "categories", "change_date", "changed_by", "created_by",
        "creation_date", "default_projection", "description", "events",
        "id", "name", "namespace", "objects", "projections", "tags",
    }
    environment_required_keys = {
        "change_date", "changed_by", "content_tag", "created_by",
        "creation_date", "display_name", "id", "name", "package_key",
        "package_version", "readonly",
    }
    datasource_required_keys = {"data_source_id", "data_source_type", "display_name"}

    schema_checks = {
        "objects": ("object", object_required_keys, False),
        "events": ("object", event_required_keys, False),
        "factories": ("array", factory_entry_keys, True),
        "sql_statements": ("array", sql_entry_keys, True),
        "processes": ("object", process_required_keys, False),
        "catalog_processes": ("object", catalog_required_keys, False),
        "perspectives": ("object", perspective_required_keys, False),
        "environments": ("object", environment_required_keys, False),
        "data_sources": ("object", datasource_required_keys, False),
    }

    all_objects = set()
    all_events = set()

    for folder, (json_type, required_keys, is_array) in schema_checks.items():
        folder_path = output_dir / folder
        if not folder_path.exists():
            continue

        for f in sorted(folder_path.iterdir()):
            if f.name.startswith(".") or not f.name.endswith(".json"):
                continue

            rel = f"{folder}/{f.name}"
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
            except json.JSONDecodeError as e:
                errors.append(f"Invalid JSON: {rel} — {e}")
                continue

            # Check array vs object type
            if is_array:
                if not isinstance(data, list):
                    errors.append(f"Expected JSON array: {rel}")
                    continue
                if not data:
                    warnings.append(f"Empty array: {rel}")
                    continue
                check_target = data[0]
            else:
                if not isinstance(data, dict):
                    errors.append(f"Expected JSON object: {rel}")
                    continue
                check_target = data

            # Check required keys
            actual_keys = set(check_target.keys())
            missing_keys = required_keys - actual_keys
            if missing_keys:
                errors.append(f"Missing keys in {rel}: {sorted(missing_keys)}")

            # Track objects and events for cross-ref
            if folder == "objects" and "name" in check_target:
                all_objects.add(check_target["name"])
            if folder == "events" and "name" in check_target:
                all_events.add(check_target["name"])

    # --- 4. Mandatory fields ---
    objects_dir = output_dir / "objects"
    if objects_dir.exists():
        for f in sorted(objects_dir.iterdir()):
            if f.name.startswith(".") or not f.name.endswith(".json"):
                continue
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                field_names = {fld.get("name") for fld in data.get("fields", [])}
                if "ID" not in field_names:
                    errors.append(f"Missing mandatory 'ID' field: objects/{f.name}")
            except (json.JSONDecodeError, AttributeError):
                pass

    events_dir = output_dir / "events"
    if events_dir.exists():
        for f in sorted(events_dir.iterdir()):
            if f.name.startswith(".") or not f.name.endswith(".json"):
                continue
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                field_names = {fld.get("name") for fld in data.get("fields", [])}
                if "ID" not in field_names:
                    errors.append(f"Missing mandatory 'ID' field: events/{f.name}")
                if "Time" not in field_names:
                    errors.append(f"Missing mandatory 'Time' field: events/{f.name}")
            except (json.JSONDecodeError, AttributeError):
                pass

    # --- 5. Cross-file consistency ---
    # Check that event relationships reference existing objects
    if events_dir.exists():
        for f in sorted(events_dir.iterdir()):
            if f.name.startswith(".") or not f.name.endswith(".json"):
                continue
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                for rel in data.get("relationships", []):
                    target_name = rel.get("target", {}).get("object_ref", {}).get("name")
                    if target_name and target_name not in all_objects:
                        warnings.append(
                            f"Event {f.name} references non-existent object '{target_name}'"
                        )
            except (json.JSONDecodeError, AttributeError):
                pass

    # Check factory/SQL statement pairs
    factories_dir = output_dir / "factories"
    sql_dir = output_dir / "sql_statements"
    if factories_dir.exists() and sql_dir.exists():
        factory_names = {
            f.name.replace("factories_", "").replace(".json", "")
            for f in factories_dir.iterdir()
            if f.name.endswith(".json") and not f.name.startswith(".")
        }
        sql_names = {
            f.name.replace("sql_statement_", "").replace(".json", "")
            for f in sql_dir.iterdir()
            if f.name.endswith(".json") and not f.name.startswith(".")
        }
        for name in factory_names - sql_names:
            warnings.append(f"Factory without SQL statement: {name}")
        for name in sql_names - factory_names:
            warnings.append(f"SQL statement without factory: {name}")

    # --- Build result ---
    result = {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "summary": {
            "folders_checked": len(actual_folders),
            "errors_found": len(errors),
            "warnings_found": len(warnings),
            "objects_found": len(all_objects),
            "events_found": len(all_events),
        },
    }
    return json.dumps(result, indent=2)


# ---------------------------------------------------------------------------
# Tool definitions for the LLM (provider-agnostic JSON schema format)
# ---------------------------------------------------------------------------

TOOL_DEFINITIONS = [
    {
        "name": "scan_inputs",
        "description": "List all files in the Input/Project input files/ folder. Returns file names and sizes.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "read_file",
        "description": "Read a file from the Input/Project input files/ folder. Use the relative path from scan_inputs.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Relative path within the input files folder.",
                },
            },
            "required": ["path"],
        },
    },
    {
        "name": "write_file",
        "description": (
            "Write a file to the Output/ folder. Use for generating requirements markdown "
            "or JSON configuration files. Parent directories are created automatically."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Relative path within Output/ (e.g., 'objects/object_PurchaseOrder.json').",
                },
                "content": {
                    "type": "string",
                    "description": "The full file content to write.",
                },
            },
            "required": ["path", "content"],
        },
    },
    {
        "name": "create_directory",
        "description": "Create a subdirectory inside the Output/ folder.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Relative directory path within Output/ (e.g., 'objects').",
                },
            },
            "required": ["path"],
        },
    },
    {
        "name": "list_template_folders",
        "description": "List all subfolders in the Input/TEMPLATE/ reference folder with file counts.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "read_template_file",
        "description": (
            "Read a file from the Input/TEMPLATE/ reference folder. "
            "Use this to check the expected JSON structure for a file type."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Relative path within the template folder (e.g., 'objects/object_PurchaseOrder.json').",
                },
            },
            "required": ["path"],
        },
    },
    {
        "name": "validate_output",
        "description": (
            "Validate the Output/ folder against the Input/TEMPLATE/ reference. "
            "Checks folder structure, file naming, JSON schemas, mandatory fields, "
            "and cross-file consistency. Call this after generating all files."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
]
