#!/usr/bin/env python3
"""CLI entry point for the OCPM Builder Assistant.

Usage:
    python app/run.py                    # Run full pipeline (Stage 1 + 2 + validation)
    python app/run.py --stage 1          # Run only Requirements Gathering
    python app/run.py --stage 2          # Run only OCPM Builder (requires existing requirements)
    python app/run.py --validate-only    # Only validate Output/2_OCPM_Builder/ against template
"""

import argparse
import os
import sys

# Ensure the project root is on the Python path so `app.*` imports work
# regardless of where the script is invoked from.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import load_config
from app.llm import create_llm
from app.orchestrator import run_stage_1, run_stage_2, run_validation
from app.tools import configure_paths


def main():
    parser = argparse.ArgumentParser(
        description="OCPM Builder Assistant — Generate Celonis OCPM models from business inputs.",
    )
    parser.add_argument(
        "--stage",
        type=int,
        choices=[1, 2],
        default=None,
        help="Run a specific stage only (1=Requirements Gathering, 2=OCPM Builder).",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate existing Output/2_OCPM_Builder/ against the template (no LLM calls).",
    )
    parser.add_argument(
        "--requirements",
        type=str,
        default=None,
        help="Path to a specific requirements .md file for Stage 2 (auto-detected if omitted).",
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Path to the config file (default: config.yaml).",
    )

    args = parser.parse_args()

    # Load configuration
    try:
        config = load_config(args.config)
    except (FileNotFoundError, EnvironmentError) as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate-only mode (no LLM needed)
    if args.validate_only:
        configure_paths(
            input_files=config.paths.input_files,
            template=config.paths.template,
            output=config.paths.output_builder,
        )
        valid = run_validation(config)
        sys.exit(0 if valid else 1)

    # Create LLM adapter
    try:
        llm = create_llm(
            provider=config.llm.provider,
            model=config.llm.model,
            api_key=config.llm.api_key,
            max_tokens=config.llm.max_tokens,
        )
    except ValueError as e:
        print(f"LLM error: {e}", file=sys.stderr)
        sys.exit(1)

    print("=" * 60)
    print("  OCPM Builder Assistant")
    print(f"  Provider: {config.llm.provider} | Model: {config.llm.model}")
    print("=" * 60)
    print()

    # Run the requested stage(s)
    if args.stage == 1:
        run_stage_1(llm, config)
    elif args.stage == 2:
        run_stage_2(llm, config, requirements_path=args.requirements)
        run_validation(config)
    else:
        # Full pipeline: Stage 1 → Stage 2 → Validation
        run_stage_1(llm, config)
        print()
        run_stage_2(llm, config, requirements_path=args.requirements)
        print()
        run_validation(config)

    print()
    print("Done.")


if __name__ == "__main__":
    main()
