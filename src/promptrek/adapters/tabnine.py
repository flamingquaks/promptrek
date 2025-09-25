"""
Tabnine (team configurations) adapter implementation.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import click

from ..core.exceptions import ValidationError
from ..core.models import UniversalPrompt
from .base import EditorAdapter


class TabnineAdapter(EditorAdapter):
    """Adapter for Tabnine team configurations."""

    _description = "Tabnine (team configurations)"
    _file_patterns = [".tabnine/config.json", ".tabnine/team.yaml"]

    def __init__(self):
        super().__init__(
            name="tabnine",
            description=self._description,
            file_patterns=self._file_patterns,
        )

    def generate(
        self,
        prompt: UniversalPrompt,
        output_dir: Path,
        dry_run: bool = False,
        verbose: bool = False,
        variables: Optional[Dict[str, Any]] = None,
    ) -> List[Path]:
        """Generate Tabnine configuration files."""

        # Apply variable substitution if supported
        processed_prompt = self.substitute_variables(prompt, variables)

        # Create configuration content
        config_content = self._build_config(processed_prompt)

        # Create team configuration content
        team_content = self._build_team_config(processed_prompt)

        # Determine output paths
        tabnine_dir = output_dir / ".tabnine"
        config_file = tabnine_dir / "config.json"
        team_file = tabnine_dir / "team.yaml"

        created_files = []

        if dry_run:
            click.echo(f"  📁 Would create: {config_file}")
            click.echo(f"  📁 Would create: {team_file}")
            if verbose:
                click.echo("  📄 Config preview:")
                preview = (
                    config_content[:200] + "..."
                    if len(config_content) > 200
                    else config_content
                )
                click.echo(f"    {preview}")
        else:
            # Create directory and files
            tabnine_dir.mkdir(exist_ok=True)
            with open(config_file, "w", encoding="utf-8") as f:
                f.write(config_content)
            created_files.append(config_file)
            click.echo(f"✅ Generated: {config_file}")

            with open(team_file, "w", encoding="utf-8") as f:
                f.write(team_content)
            created_files.append(team_file)
            click.echo(f"✅ Generated: {team_file}")

        return created_files or [config_file, team_file]

    def validate(self, prompt: UniversalPrompt) -> List[ValidationError]:
        """Validate prompt for Tabnine."""
        errors = []

        # Tabnine works well with team-based coding standards
        if not prompt.instructions or not prompt.instructions.code_style:
            errors.append(
                ValidationError(
                    field="instructions.code_style",
                    message="Tabnine benefits from clear code style guidelines for team consistency",
                    severity="warning",
                )
            )

        return errors

    def supports_variables(self) -> bool:
        """Tabnine supports variable substitution."""
        return True

    def supports_conditionals(self) -> bool:
        """Tabnine supports conditional configuration."""
        return True

    def _build_config(self, prompt: UniversalPrompt) -> str:
        """Build Tabnine configuration content."""
        config = {
            "version": "1.0",
            "project": {
                "name": prompt.metadata.title,
                "description": prompt.metadata.description,
                "version": prompt.metadata.version,
            },
            "settings": {
                "enabled": True,
                "auto_import": True,
                "deep_completions": True,
                "team_training": True,
                "semantic_completion": True,
            },
            "team_config_file": "team.yaml",
        }

        # Add language settings
        if prompt.context and prompt.context.technologies:
            config["languages"] = {}
            for tech in prompt.context.technologies:
                tech_lower = tech.lower()
                config["languages"][tech_lower] = {
                    "enabled": True,
                    "completion_level": "advanced",
                    "team_patterns": True,
                }

        # Add project type specific settings
        if prompt.context and prompt.context.project_type:
            config["project"]["type"] = prompt.context.project_type
            if prompt.context.project_type in ["web_application", "api_service"]:
                config["settings"]["web_framework_support"] = True

        return json.dumps(config, indent=2)

    def _build_team_config(self, prompt: UniversalPrompt) -> str:
        """Build Tabnine team configuration YAML content."""
        lines = []

        # Header
        lines.append(f"# Tabnine Team Configuration for {prompt.metadata.title}")
        lines.append("")

        # Team settings
        lines.append("team:")
        lines.append(f'  name: "{prompt.metadata.title}"')
        lines.append(f'  description: "{prompt.metadata.description}"')
        if prompt.metadata.author:
            lines.append(f'  contact: "{prompt.metadata.author}"')
        lines.append("")

        # Code standards
        lines.append("standards:")
        if prompt.instructions:
            if prompt.instructions.general:
                lines.append("  general:")
                for instruction in prompt.instructions.general:
                    lines.append(f'    - "{instruction}"')
                lines.append("")

            if prompt.instructions.code_style:
                lines.append("  code_style:")
                for guideline in prompt.instructions.code_style:
                    lines.append(f'    - "{guideline}"')
                lines.append("")

            if prompt.instructions.testing:
                lines.append("  testing:")
                for guideline in prompt.instructions.testing:
                    lines.append(f'    - "{guideline}"')
                lines.append("")

        # Project patterns
        lines.append("patterns:")
        if prompt.context and prompt.context.technologies:
            lines.append("  technologies:")
            for tech in prompt.context.technologies:
                lines.append(f"    - {tech}")
            lines.append("")

        # Training preferences
        lines.append("training:")
        lines.append("  local_patterns: true")
        lines.append("  team_learning: true")
        lines.append("  code_consistency: high")
        lines.append("  suggestion_confidence: medium")
        lines.append("")

        # Completion preferences
        lines.append("completions:")
        lines.append("  max_suggestions: 5")
        lines.append("  context_aware: true")
        lines.append("  multi_line: true")
        lines.append("  function_signatures: true")
        if prompt.context and prompt.context.technologies:
            lines.append("  language_specific:")
            for tech in prompt.context.technologies:
                tech_lower = tech.lower()
                lines.append(f"    {tech_lower}:")
                lines.append("      advanced_completion: true")
                lines.append("      framework_aware: true")

        return "\n".join(lines)
