"""Multi-stage OCPM pipeline orchestrator.

Runs the agentic function-calling loop for each stage,
completely independent of which LLM provider is behind it.
"""

import json
import sys
from pathlib import Path

from app.config import AppConfig
from app.llm.base import LLMBase, LLMResponse
from app.tools import TOOL_DEFINITIONS, TOOL_REGISTRY, configure_paths, validate_output


def _log(stage: str, message: str):
    """Print a formatted progress message."""
    print(f"[{stage}] {message}", flush=True)


def _execute_tool(name: str, arguments: dict, stage: str) -> str:
    """Execute a registered tool and return the result as a string."""
    func = TOOL_REGISTRY.get(name)
    if func is None:
        return json.dumps({"error": f"Unknown tool: {name}"})

    try:
        result = func(**arguments)
    except Exception as e:
        result = json.dumps({"error": f"Tool '{name}' failed: {e}"})

    # Log file writes for visibility
    if name == "write_file" and "path" in arguments:
        _log(stage, f"  Written: {arguments['path']}")
    elif name == "scan_inputs":
        try:
            data = json.loads(result)
            count = data.get("count", 0)
            _log(stage, f"  Found {count} input file(s)")
        except (json.JSONDecodeError, TypeError):
            pass

    return result


def _run_agent_loop(
    llm: LLMBase,
    system_prompt: str,
    initial_message: str,
    tools: list[dict],
    stage: str,
    max_iterations: int = 200,
) -> str:
    """Run the agentic function-calling loop until the LLM stops.

    Args:
        llm: The LLM adapter.
        system_prompt: System instruction for the assistant.
        initial_message: The first user message to send.
        tools: Tool definitions to expose to the LLM.
        stage: Label for logging (e.g., "Stage 1", "Stage 2").
        max_iterations: Safety limit to prevent infinite loops.

    Returns:
        The final text response from the LLM.
    """
    messages = [{"role": "user", "content": initial_message}]

    for i in range(max_iterations):
        _log(stage, f"LLM call {i + 1}...")

        response: LLMResponse = llm.chat(system_prompt, messages, tools)

        if response.stop_reason == "end_turn":
            if response.text:
                _log(stage, "Complete.")
            return response.text or ""

        # Process tool calls
        # Build the assistant message with all content blocks
        assistant_content = []
        if response.text:
            assistant_content.append({"type": "text", "text": response.text})
        for tc in response.tool_calls:
            assistant_content.append({
                "type": "tool_use",
                "id": tc.id,
                "name": tc.name,
                "input": tc.arguments,
            })

        messages.append({"role": "assistant", "content": assistant_content})

        # Execute each tool call and collect results
        tool_results = []
        for tc in response.tool_calls:
            result_str = _execute_tool(tc.name, tc.arguments, stage)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tc.id,
                "content": result_str,
            })

        messages.append({"role": "user", "content": tool_results})

    _log(stage, f"WARNING: Reached max iterations ({max_iterations}). Stopping.")
    return ""


def run_stage_1(llm: LLMBase, config: AppConfig) -> str:
    """Stage 1: Requirements Gathering.

    Reads input files and produces a structured requirements Markdown file.
    """
    _log("Stage 1", "Starting Requirements Gathering...")

    # Point tools at the requirements output subfolder
    configure_paths(
        input_files=config.paths.input_files,
        template=config.paths.template,
        output=config.paths.output_requirements,
    )

    system_prompt = config.paths.prompt_requirements.read_text(encoding="utf-8")

    initial_message = (
        "Scan the project input files folder, read all files, and generate "
        "the OCPM requirements document as specified in your instructions. "
        "Use the scan_inputs tool to discover files, read_file to read them, "
        "and write_file to save the output Markdown to the Output/1_Requirements/ folder."
    )

    result = _run_agent_loop(
        llm=llm,
        system_prompt=system_prompt,
        initial_message=initial_message,
        tools=TOOL_DEFINITIONS,
        stage="Stage 1",
    )

    _log("Stage 1", "Requirements Gathering complete.")
    return result


def run_stage_2(llm: LLMBase, config: AppConfig, requirements_path: str | None = None) -> str:
    """Stage 2: OCPM Builder.

    Takes the requirements document and generates all JSON configuration files.
    """
    _log("Stage 2", "Starting OCPM Builder...")

    # Point tools at the builder output subfolder
    configure_paths(
        input_files=config.paths.input_files,
        template=config.paths.template,
        output=config.paths.output_builder,
    )

    system_prompt = config.paths.prompt_builder.read_text(encoding="utf-8")

    # Find the requirements file
    if requirements_path:
        req_file = Path(requirements_path)
    else:
        # Auto-discover: look for the first .md file in Output/1_Requirements/
        req_dir = config.paths.output_requirements
        md_files = sorted(req_dir.glob("*.md"))
        if not md_files:
            _log("Stage 2", "ERROR: No requirements .md file found in Output/1_Requirements/. Run Stage 1 first.")
            sys.exit(1)
        req_file = md_files[0]

    _log("Stage 2", f"Using requirements: {req_file.name}")
    requirements_content = req_file.read_text(encoding="utf-8")

    initial_message = (
        f"Here is the OCPM requirements specification:\n\n"
        f"---\n{requirements_content}\n---\n\n"
        f"Generate all OCPM JSON configuration files as specified in your instructions. "
        f"Use write_file to save each file to the Output/2_OCPM_Builder/ folder. "
        f"Use list_template_folders and read_template_file to reference the template "
        f"structure when needed. After generating all files, call validate_output "
        f"to verify correctness."
    )

    result = _run_agent_loop(
        llm=llm,
        system_prompt=system_prompt,
        initial_message=initial_message,
        tools=TOOL_DEFINITIONS,
        stage="Stage 2",
    )

    _log("Stage 2", "OCPM Builder complete.")
    return result


def run_validation(config: AppConfig):
    """Run standalone validation of the Output/2_OCPM_Builder/ folder against the template."""
    _log("Validation", "Validating output against template...")

    # Point tools at the builder output subfolder for validation
    configure_paths(
        input_files=config.paths.input_files,
        template=config.paths.template,
        output=config.paths.output_builder,
    )

    result_str = validate_output()
    result = json.loads(result_str)

    if result["valid"]:
        _log("Validation", "All checks passed.")
    else:
        _log("Validation", f"Found {result['summary']['errors_found']} error(s):")
        for err in result["errors"]:
            _log("Validation", f"  ERROR: {err}")

    if result["warnings"]:
        _log("Validation", f"Found {result['summary']['warnings_found']} warning(s):")
        for warn in result["warnings"]:
            _log("Validation", f"  WARN: {warn}")

    summary = result["summary"]
    _log("Validation", (
        f"Summary: {summary['objects_found']} objects, "
        f"{summary['events_found']} events, "
        f"{summary['folders_checked']} folders checked."
    ))

    return result["valid"]
