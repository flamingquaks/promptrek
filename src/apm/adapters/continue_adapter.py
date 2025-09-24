"""
Continue editor adapter implementation.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import click

from ..core.exceptions import ValidationError
from ..core.models import UniversalPrompt
from .base import EditorAdapter


class ContinueAdapter(EditorAdapter):
    """Adapter for Continue editor."""

    _description = "Continue (.continue/config.json)"
    _file_patterns = [".continue/config.json"]

    def __init__(self):
        super().__init__(
            name="continue",
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
        """Generate Continue configuration."""

        # Apply variable substitution if supported
        processed_prompt = self.substitute_variables(prompt, variables)

        # Process conditionals if supported
        conditional_content = self.process_conditionals(processed_prompt, variables)

        # Create content
        content = self._build_content(processed_prompt, conditional_content)

        # Determine output path
        continue_dir = output_dir / ".continue"
        output_file = continue_dir / "config.json"

        if dry_run:
            click.echo(f"  📁 Would create: {output_file}")
            if verbose:
                click.echo("  📄 Content preview:")
                preview = content[:200] + "..." if len(content) > 200 else content
                click.echo(f"    {preview}")
        else:
            # Create directory and file
            continue_dir.mkdir(exist_ok=True)
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(content)
            click.echo(f"✅ Generated: {output_file}")

        return [output_file]

    def validate(self, prompt: UniversalPrompt) -> List[ValidationError]:
        """Validate prompt for Continue."""
        errors = []

        # Continue requires a system message
        if not prompt.metadata.description:
            errors.append(
                ValidationError(
                    field="metadata.description",
                    message="Continue requires a description for the system message",
                )
            )

        return errors

    def supports_variables(self) -> bool:
        """Continue supports variable substitution."""
        return True

    def supports_conditionals(self) -> bool:
        """Continue supports conditional configuration."""
        return True

    def _build_content(
        self,
        prompt: UniversalPrompt,
        conditional_content: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Build Continue configuration content."""
        config = {
            "models": [],
            "systemMessage": (
                f"{prompt.metadata.title}\n\n{prompt.metadata.description}"
            ),
            "completionOptions": {},
            "allowAnonymousTelemetry": False,
        }

        # Collect all instructions (original + conditional)
        all_instructions = []
        if prompt.instructions and prompt.instructions.general:
            all_instructions.extend(prompt.instructions.general)

        # Add conditional general instructions
        if (
            conditional_content
            and "instructions" in conditional_content
            and "general" in conditional_content["instructions"]
        ):
            all_instructions.extend(conditional_content["instructions"]["general"])

        # Add instructions to system message
        if all_instructions:
            config["systemMessage"] += "\n\nGeneral Instructions:\n"
            for instruction in all_instructions:
                config["systemMessage"] += f"- {instruction}\n"

        return json.dumps(config, indent=2)
