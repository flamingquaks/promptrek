"""
Kiro (AI-powered assistance) adapter implementation.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import click

from ..core.exceptions import ValidationError
from ..core.models import UniversalPrompt
from .base import EditorAdapter


class KiroAdapter(EditorAdapter):
    """Adapter for Kiro AI-powered assistance."""

    _description = "Kiro (AI-powered assistance)"
    _file_patterns = [".kiro/config.json", ".kiro/prompts.md"]

    def __init__(self):
        super().__init__(
            name="kiro",
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
        """Generate Kiro configuration files."""

        # Apply variable substitution if supported
        processed_prompt = self.substitute_variables(prompt, variables)

        # Process conditionals if supported
        conditional_content = self.process_conditionals(processed_prompt, variables)

        # Create configuration content
        config_content = self._build_config(processed_prompt)

        # Create prompts content
        prompts_content = self._build_prompts(processed_prompt, conditional_content)

        # Determine output paths
        kiro_dir = output_dir / ".kiro"
        config_file = kiro_dir / "config.json"
        prompts_file = kiro_dir / "prompts.md"

        created_files = []

        if dry_run:
            click.echo(f"  📁 Would create: {config_file}")
            click.echo(f"  📁 Would create: {prompts_file}")
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
            kiro_dir.mkdir(exist_ok=True)
            with open(config_file, "w", encoding="utf-8") as f:
                f.write(config_content)
            created_files.append(config_file)
            click.echo(f"✅ Generated: {config_file}")

            with open(prompts_file, "w", encoding="utf-8") as f:
                f.write(prompts_content)
            created_files.append(prompts_file)
            click.echo(f"✅ Generated: {prompts_file}")

        return created_files or [config_file, prompts_file]

    def validate(self, prompt: UniversalPrompt) -> List[ValidationError]:
        """Validate prompt for Kiro."""
        errors = []

        # Kiro works well with structured instructions
        if not prompt.instructions:
            errors.append(
                ValidationError(
                    field="instructions",
                    message="Kiro benefits from detailed instructions for AI assistance",
                    severity="warning",
                )
            )

        return errors

    def supports_variables(self) -> bool:
        """Kiro supports variable substitution."""
        return True

    def supports_conditionals(self) -> bool:
        """Kiro supports conditional configuration."""
        return True

    def _build_config(self, prompt: UniversalPrompt) -> str:
        """Build Kiro configuration content."""
        config = {
            "name": prompt.metadata.title,
            "description": prompt.metadata.description,
            "version": prompt.metadata.version,
            "settings": {
                "auto_suggest": True,
                "context_aware": True,
                "smart_completions": True,
                "learning_mode": True,
            },
            "prompts_file": "prompts.md",
        }

        # Add project context
        if prompt.context:
            config["project"] = {}
            if prompt.context.project_type:
                config["project"]["type"] = prompt.context.project_type
            if prompt.context.technologies:
                config["project"]["technologies"] = prompt.context.technologies
                config["settings"]["language_specific"] = True

        # Add editor-specific configuration
        if prompt.editor_specific and "kiro" in prompt.editor_specific:
            kiro_config = prompt.editor_specific["kiro"]
            if hasattr(kiro_config, "settings"):
                config["settings"].update(kiro_config.settings)

        return json.dumps(config, indent=2)

    def _build_prompts(
        self,
        prompt: UniversalPrompt,
        conditional_content: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Build Kiro prompts markdown content."""
        lines = []

        # Header
        lines.append(f"# {prompt.metadata.title} - Kiro AI Prompts")
        lines.append("")
        lines.append("## Project Overview")
        lines.append(prompt.metadata.description)
        lines.append("")

        # Context section
        if prompt.context:
            lines.append("## Project Context")
            if prompt.context.project_type:
                lines.append(f"**Type:** {prompt.context.project_type}")
            if prompt.context.technologies:
                lines.append(
                    f"**Technologies:** {', '.join(prompt.context.technologies)}"
                )
            if prompt.context.description:
                lines.append("")
                lines.append("**Description:**")
                lines.append(prompt.context.description)
            lines.append("")

        # AI Assistant Instructions
        lines.append("## AI Assistant Instructions")
        lines.append("")

        if prompt.instructions:
            if prompt.instructions.general:
                lines.append("### General Guidelines")
                for instruction in prompt.instructions.general:
                    lines.append(f"- {instruction}")
                lines.append("")

            if prompt.instructions.code_style:
                lines.append("### Code Style Guidelines")
                for guideline in prompt.instructions.code_style:
                    lines.append(f"- {guideline}")
                lines.append("")

            if prompt.instructions.testing:
                lines.append("### Testing Guidelines")
                for guideline in prompt.instructions.testing:
                    lines.append(f"- {guideline}")
                lines.append("")

        # Smart Suggestions
        lines.append("## Smart Suggestions")
        lines.append("")
        lines.append("Kiro should provide intelligent suggestions for:")
        lines.append("- Code completion based on project patterns")
        lines.append("- Refactoring opportunities")
        lines.append("- Best practice recommendations")
        lines.append("- Performance optimizations")
        if prompt.context and prompt.context.technologies:
            tech_list = ", ".join(prompt.context.technologies)
            lines.append(f"- {tech_list}-specific improvements")
        lines.append("")

        # Examples if available
        if prompt.examples:
            lines.append("## Code Examples")
            lines.append("")
            lines.append("Use these examples as reference patterns:")
            lines.append("")

            for name, example in prompt.examples.items():
                lines.append(f"### {name.replace('_', ' ').title()}")
                lines.append(example)
                lines.append("")

        return "\n".join(lines)
