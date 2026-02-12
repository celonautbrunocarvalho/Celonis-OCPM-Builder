"""Configuration loader for the OCPM Builder app."""

import os
from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class LLMConfig:
    provider: str
    model: str
    api_key: str
    max_tokens: int


@dataclass
class PathsConfig:
    input_files: Path
    template: Path
    output: Path
    prompt_requirements: Path
    prompt_builder: Path
    prompt_knowledge_model: Path
    prompt_apps: Path
    output_requirements: Path
    output_builder: Path
    output_knowledge_model: Path
    output_apps: Path


@dataclass
class AppConfig:
    llm: LLMConfig
    paths: PathsConfig


def _resolve_env_vars(value: str) -> str:
    """Resolve ${ENV_VAR} references in a string."""
    if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
        env_var = value[2:-1]
        resolved = os.environ.get(env_var)
        if resolved is None:
            raise EnvironmentError(
                f"Environment variable '{env_var}' is not set. "
                f"Set it with: export {env_var}=your-api-key"
            )
        return resolved
    return value


def load_config(config_path: str = "config.yaml") -> AppConfig:
    """Load and validate the app configuration from a YAML file."""
    project_root = Path(__file__).parent.parent

    config_file = project_root / config_path
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_file}")

    with open(config_file) as f:
        raw = yaml.safe_load(f)

    llm_raw = raw["llm"]
    paths_raw = raw["paths"]
    module_outputs = paths_raw.get("module_outputs", {})

    llm_config = LLMConfig(
        provider=llm_raw["provider"],
        model=llm_raw["model"],
        api_key=_resolve_env_vars(llm_raw["api_key"]),
        max_tokens=llm_raw.get("max_tokens", 4096),
    )

    output_base = project_root / paths_raw["output"]

    paths_config = PathsConfig(
        input_files=project_root / paths_raw["input_files"],
        template=project_root / paths_raw["template"],
        output=output_base,
        prompt_requirements=project_root / paths_raw["prompts"]["requirements"],
        prompt_builder=project_root / paths_raw["prompts"]["builder"],
        prompt_knowledge_model=project_root / paths_raw["prompts"]["knowledge_model"],
        prompt_apps=project_root / paths_raw["prompts"]["apps"],
        output_requirements=output_base / module_outputs.get("requirements", "1_Requirements"),
        output_builder=output_base / module_outputs.get("builder", "2_OCPM_Builder"),
        output_knowledge_model=output_base / module_outputs.get("knowledge_model", "3_Knowledge_Model"),
        output_apps=output_base / module_outputs.get("apps", "4_Apps"),
    )

    return AppConfig(llm=llm_config, paths=paths_config)
