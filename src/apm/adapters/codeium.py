"""
Codeium adapter implementation.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import click

from ..core.exceptions import ValidationError
from ..core.models import UniversalPrompt
from .base import EditorAdapter


class CodeiumAdapter(EditorAdapter):
    """Adapter for Codeium AI assistant."""

    _description = "Codeium (context-based)"
    _file_patterns = [".codeium/context.json", ".codeiumrc"]

    def __init__(self):
        super().__init__(
            name="codeium",
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
        """Generate Codeium configuration files."""

        # Apply variable substitution if supported
        processed_prompt = self.substitute_variables(prompt, variables)

        # Process conditionals if supported
        conditional_content = self.process_conditionals(processed_prompt, variables)

        # Create context content (JSON format for Codeium)
        context_content = self._build_context_json(processed_prompt, conditional_content)

        # Create RC file content
        rc_content = self._build_rc_file(processed_prompt)

        # Determine output paths
        codeium_dir = output_dir / ".codeium"
        context_file = codeium_dir / "context.json"
        rc_file = output_dir / ".codeiumrc"

        created_files = []

        if dry_run:
            click.echo(f"  📁 Would create: {context_file}")
            click.echo(f"  📁 Would create: {rc_file}")
            if verbose:
                click.echo("  📄 Context preview:")
                preview = (
                    context_content[:200] + "..."
                    if len(context_content) > 200
                    else context_content
                )
                click.echo(f"    {preview}")
        else:
            # Create directory and context file
            codeium_dir.mkdir(exist_ok=True)
            with open(context_file, "w", encoding="utf-8") as f:
                f.write(context_content)
            created_files.append(context_file)
            click.echo(f"✅ Generated: {context_file}")

            # Create RC file
            with open(rc_file, "w", encoding="utf-8") as f:
                f.write(rc_content)
            created_files.append(rc_file)
            click.echo(f"✅ Generated: {rc_file}")

        return created_files or [context_file, rc_file]

    def validate(self, prompt: UniversalPrompt) -> List[ValidationError]:
        """Validate prompt for Codeium."""
        errors = []

        # Codeium works well with technology context
        if not prompt.context or not prompt.context.technologies:
            errors.append(
                ValidationError(
                    field="context.technologies",
                    message="Codeium works best with specified technologies for better completions",
                    severity="warning",
                )
            )

        return errors

    def supports_variables(self) -> bool:
        """Codeium supports variable substitution."""
        return True

    def supports_conditionals(self) -> bool:
        """Codeium supports conditional configuration."""
        return True

    def _build_context_json(self, prompt: UniversalPrompt, conditional_content: Optional[Dict[str, Any]] = None) -> str:
        """Build Codeium context JSON content."""
        context = {
            "project": {
                "name": prompt.metadata.title,
                "description": prompt.metadata.description,
                "version": prompt.metadata.version,
            },
            "guidelines": [],
            "patterns": [],
            "preferences": {
                "style": "consistent",
                "verbosity": "medium",
                "suggestions": "contextual",
            },
        }

        # Add project context
        if prompt.context:
            if prompt.context.project_type:
                context["project"]["type"] = prompt.context.project_type
            if prompt.context.technologies:
                context["project"]["technologies"] = prompt.context.technologies
                # Add technology-specific preferences
                context["preferences"]["languages"] = prompt.context.technologies

        # Add guidelines from instructions
        if prompt.instructions:
            if prompt.instructions.general:
                context["guidelines"].extend(
                    [
                        {"category": "general", "rule": instruction}
                        for instruction in prompt.instructions.general
                    ]
                )

            if prompt.instructions.code_style:
                context["guidelines"].extend(
                    [
                        {"category": "style", "rule": guideline}
                        for guideline in prompt.instructions.code_style
                    ]
                )

            if prompt.instructions.testing:
                context["guidelines"].extend(
                    [
                        {"category": "testing", "rule": guideline}
                        for guideline in prompt.instructions.testing
                    ]
                )

        # Add conditional instructions
        if conditional_content and "instructions" in conditional_content:
            cond_instructions = conditional_content["instructions"]
            if "general" in cond_instructions:
                context["guidelines"].extend(
                    [
                        {"category": "general", "rule": instruction}
                        for instruction in cond_instructions["general"]
                    ]
                )
            if "code_style" in cond_instructions:
                context["guidelines"].extend(
                    [
                        {"category": "style", "rule": guideline}
                        for guideline in cond_instructions["code_style"]
                    ]
                )
            if "testing" in cond_instructions:
                context["guidelines"].extend(
                    [
                        {"category": "testing", "rule": guideline}
                        for guideline in cond_instructions["testing"]
                    ]
                )

        # Add patterns from examples
        if prompt.examples:
            for name, example in prompt.examples.items():
                context["patterns"].append(
                    {
                        "name": name,
                        "description": f"Example {name.replace('_', ' ')}",
                        "example": (
                            example[:500] + "..." if len(example) > 500 else example
                        ),
                    }
                )

        return json.dumps(context, indent=2)

    def _build_rc_file(self, prompt: UniversalPrompt) -> str:
        """Build .codeiumrc configuration file."""
        lines = []

        lines.append(f"# Codeium configuration for {prompt.metadata.title}")
        lines.append("")

        # Basic settings
        lines.append("[settings]")
        lines.append("enable_suggestions=true")
        lines.append("enable_completions=true")
        lines.append("suggestion_delay=100")
        lines.append("")

        # Language preferences
        if prompt.context and prompt.context.technologies:
            lines.append("[languages]")
            for tech in prompt.context.technologies:
                tech_lower = tech.lower()
                lines.append(f"{tech_lower}_enabled=true")
            lines.append("")

        # Style preferences from instructions
        if prompt.instructions:
            lines.append("[style]")
            lines.append("consistent_formatting=true")
            lines.append("follow_project_conventions=true")

            if prompt.instructions.code_style:
                lines.append("# Code style guidelines:")
                for guideline in prompt.instructions.code_style:
                    # Convert to comment format
                    lines.append(f"# - {guideline}")
            lines.append("")

        # Context file reference
        lines.append("[context]")
        lines.append("context_file=.codeium/context.json")
        lines.append("auto_load_context=true")

        return "\n".join(lines)
