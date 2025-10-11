"""
Tabnine adapter implementation.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import click

from ..core.exceptions import ValidationError
from ..core.models import (
    Instructions,
    ProjectContext,
    PromptMetadata,
    UniversalPrompt,
    UniversalPromptV2,
)
from .base import EditorAdapter


class TabnineAdapter(EditorAdapter):
    """Adapter for Tabnine."""

    _description = "Tabnine (.tabnine_commands)"
    _file_patterns = [".tabnine_commands"]

    def __init__(self) -> None:
        super().__init__(
            name="tabnine",
            description=self._description,
            file_patterns=self._file_patterns,
        )

    def generate(
        self,
        prompt: Union[UniversalPrompt, UniversalPromptV2],
        output_dir: Path,
        dry_run: bool = False,
        verbose: bool = False,
        variables: Optional[Dict[str, Any]] = None,
        headless: bool = False,
    ) -> List[Path]:
        """Generate Tabnine configuration files."""

        # V2: Convert markdown content to comment-based format
        if isinstance(prompt, UniversalPromptV2):
            return self._generate_v2(prompt, output_dir, dry_run, verbose, variables)

        # V1: Apply variable substitution if supported
        processed_prompt = self.substitute_variables(prompt, variables)
        assert isinstance(
            processed_prompt, UniversalPrompt
        ), "V1 path should have UniversalPrompt"

        # Process conditionals if supported
        conditional_content = self.process_conditionals(processed_prompt, variables)

        # Create commands content
        commands_content = self._build_commands_file(
            processed_prompt, conditional_content
        )

        # Determine output path
        commands_file = output_dir / ".tabnine_commands"

        if dry_run:
            click.echo(f"  📁 Would create: {commands_file}")
            if verbose:
                click.echo("  📄 Commands preview:")
                preview = (
                    commands_content[:200] + "..."
                    if len(commands_content) > 200
                    else commands_content
                )
                click.echo(f"    {preview}")
            return [commands_file]
        else:
            with open(commands_file, "w", encoding="utf-8") as f:
                f.write(commands_content)
            click.echo(f"✅ Generated: {commands_file}")
            return [commands_file]

    def _generate_v2(
        self,
        prompt: UniversalPromptV2,
        output_dir: Path,
        dry_run: bool,
        verbose: bool,
        variables: Optional[Dict[str, Any]] = None,
    ) -> List[Path]:
        """Generate Tabnine file from v2 schema (convert markdown to comment format)."""
        # Apply variable substitution
        content = prompt.content
        if variables:
            for var_name, var_value in variables.items():
                placeholder = "{{{ " + var_name + " }}}"
                content = content.replace(placeholder, var_value)

        # Convert markdown content to comment-based format
        # Simple conversion: prefix each line with # if not already
        lines = []
        for line in content.split("\n"):
            if line.strip() and not line.startswith("#"):
                lines.append(f"# {line}")
            else:
                lines.append(line)

        commands_content = "\n".join(lines)
        commands_file = output_dir / ".tabnine_commands"

        if dry_run:
            click.echo(f"  📁 Would create: {commands_file}")
            if verbose:
                preview = (
                    commands_content[:200] + "..."
                    if len(commands_content) > 200
                    else commands_content
                )
                click.echo(f"    {preview}")
            return [commands_file]
        else:
            with open(commands_file, "w", encoding="utf-8") as f:
                f.write(commands_content)
            click.echo(f"✅ Generated: {commands_file}")
            return [commands_file]

    def validate(
        self, prompt: Union[UniversalPrompt, UniversalPromptV2]
    ) -> List[ValidationError]:
        """Validate prompt for Tabnine."""
        errors = []

        # V2 validation: check content exists
        if isinstance(prompt, UniversalPromptV2):
            if not prompt.content or not prompt.content.strip():
                errors.append(
                    ValidationError(
                        field="content",
                        message="Tabnine requires content",
                        severity="error",
                    )
                )
            return errors

        # V1 validation: Tabnine works well with clear instructions
        if not prompt.instructions:
            errors.append(
                ValidationError(
                    field="instructions",
                    message="Tabnine benefits from clear coding guidelines",
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

    def parse_files(
        self, source_dir: Path
    ) -> Union[UniversalPrompt, UniversalPromptV2]:
        """Parse Tabnine files back into a UniversalPrompt."""
        commands_file = source_dir / ".tabnine_commands"

        if not commands_file.exists():
            raise FileNotFoundError(f"Tabnine commands file not found: {commands_file}")

        # Initialize parsed data
        metadata = PromptMetadata(
            title="Tabnine Commands",
            description="Configuration parsed from Tabnine commands file",
            version="1.0.0",
            author="PrompTrek Sync",
            created=datetime.now().isoformat(),
            updated=datetime.now().isoformat(),
            tags=["tabnine", "synced"],
        )

        instructions = Instructions()
        technologies = []

        with open(commands_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Parse comment-based format
        current_section = None
        general_instructions = []
        code_style_instructions = []
        testing_instructions = []

        for line in content.split("\n"):
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Detect section headers
            if line.startswith("## "):
                section_name = line[3:].strip()
                if "Coding Guidelines" in section_name or "General" in section_name:
                    current_section = "general"
                elif "Code Style" in section_name:
                    current_section = "code_style"
                elif "Testing" in section_name:
                    current_section = "testing"
                elif "Technology" in section_name:
                    current_section = "technology"
                else:
                    current_section = None
                continue

            # Extract title from first header
            if line.startswith("# ") and metadata.title == "Tabnine Commands":
                title = line[2:].strip()
                if "Tabnine Commands for " in title:
                    metadata.title = title.replace("Tabnine Commands for ", "")
                continue

            # Extract technologies from comment
            if "Technologies:" in line:
                tech_str = line.split("Technologies:", 1)[1].strip()
                technologies = [t.strip() for t in tech_str.split(",")]
                continue

            # Extract instructions (lines starting with #)
            if line.startswith("# ") and current_section:
                instruction = line[2:].strip()
                # Skip generic headers and usage notes
                if any(
                    skip in instruction
                    for skip in [
                        "This file provides",
                        "Tabnine will use",
                        "Usage",
                        "Type:",
                        "Technologies:",
                    ]
                ):
                    continue

                if current_section == "general":
                    general_instructions.append(instruction)
                elif current_section == "code_style":
                    code_style_instructions.append(instruction)
                elif current_section == "testing":
                    testing_instructions.append(instruction)

        # Set instructions
        if general_instructions:
            instructions.general = general_instructions
        if code_style_instructions:
            instructions.code_style = code_style_instructions
        if testing_instructions:
            instructions.testing = testing_instructions

        # Create context if technologies were found
        context = None
        if technologies:
            context = ProjectContext(
                project_type="application",
                technologies=technologies,
                description=f"Project using {', '.join(technologies)}",
            )

        return UniversalPrompt(
            schema_version="1.0.0",
            metadata=metadata,
            targets=["tabnine"],
            context=context,
            instructions=instructions,
        )

    def _build_commands_file(
        self,
        prompt: UniversalPrompt,
        conditional_content: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Build .tabnine_commands file content."""
        lines = []

        # Header
        lines.append(f"# Tabnine Commands for {prompt.metadata.title}")
        lines.append("")
        lines.append(f"# {prompt.metadata.description}")
        lines.append("")

        # Project Context
        if prompt.context:
            lines.append("## Project Context")
            if prompt.context.project_type:
                lines.append(f"# Type: {prompt.context.project_type}")
            if prompt.context.technologies:
                lines.append(
                    f"# Technologies: {', '.join(prompt.context.technologies)}"
                )
            lines.append("")

        # Coding Guidelines as Commands
        if prompt.instructions:
            lines.append("## Coding Guidelines")
            lines.append("")

            # Collect all instructions
            all_instructions = []
            if prompt.instructions.general:
                all_instructions.extend(prompt.instructions.general)
            if (
                conditional_content
                and "instructions" in conditional_content
                and "general" in conditional_content["instructions"]
            ):
                all_instructions.extend(conditional_content["instructions"]["general"])

            if all_instructions:
                for instruction in all_instructions:
                    lines.append(f"# {instruction}")
                lines.append("")

            # Code Style
            if prompt.instructions.code_style:
                lines.append("## Code Style")
                lines.append("")
                for guideline in prompt.instructions.code_style:
                    lines.append(f"# {guideline}")
                lines.append("")

            # Testing
            if prompt.instructions.testing:
                lines.append("## Testing")
                lines.append("")
                for guideline in prompt.instructions.testing:
                    lines.append(f"# {guideline}")
                lines.append("")

        # Technology-Specific Guidance
        if prompt.context and prompt.context.technologies:
            lines.append("## Technology Guidelines")
            lines.append("")
            for tech in prompt.context.technologies:
                lines.append(
                    f"# {tech.title()}: Follow {tech} best practices and idioms"
                )
            lines.append("")

        # Footer
        lines.append("## Usage")
        lines.append(
            "# This file provides context to Tabnine for better code completions"
        )
        lines.append(
            "# Tabnine will use these guidelines to suggest more relevant code"
        )

        return "\n".join(lines)
