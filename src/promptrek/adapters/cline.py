"""
Cline (terminal-based AI assistant) adapter implementation.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

import click

from ..core.exceptions import ValidationError
from ..core.models import UniversalPrompt
from .base import EditorAdapter


class ClineAdapter(EditorAdapter):
    """Adapter for Cline terminal-based AI assistant."""

    _description = "Cline (.cline-rules/default-rules.md)"
    _file_patterns = [".cline-rules/default-rules.md"]

    def __init__(self):
        super().__init__(
            name="cline",
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
        """Generate Cline rules file."""

        # Apply variable substitution if supported
        processed_prompt = self.substitute_variables(prompt, variables)

        # Process conditionals if supported
        conditional_content = self.process_conditionals(processed_prompt, variables)

        # Create content
        content = self._build_content(processed_prompt, conditional_content)

        # Determine output path - Cline uses .cline-rules/default-rules.md
        cline_rules_dir = output_dir / ".cline-rules"
        output_file = cline_rules_dir / "default-rules.md"

        if dry_run:
            click.echo(f"  📁 Would create directory: {cline_rules_dir}")
            click.echo(f"  📁 Would create: {output_file}")
            if verbose:
                click.echo("  📄 Content preview:")
                preview = content[:200] + "..." if len(content) > 200 else content
                click.echo(f"    {preview}")
        else:
            # Create .cline-rules directory if it doesn't exist
            cline_rules_dir.mkdir(parents=True, exist_ok=True)
            
            # Create default-rules.md file
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(content)
            click.echo(f"✅ Generated: {output_file}")

        return [output_file]

    def validate(self, prompt: UniversalPrompt) -> List[ValidationError]:
        """Validate prompt for Cline."""
        errors = []

        # Cline works well with clear instructions and context
        if not prompt.instructions or not prompt.instructions.general:
            errors.append(
                ValidationError(
                    field="instructions.general",
                    message=("Cline needs clear general instructions for coding tasks"),
                )
            )

        return errors

    def supports_variables(self) -> bool:
        """Cline supports variable substitution."""
        return True

    def supports_conditionals(self) -> bool:
        """Cline supports conditional configuration."""
        return True

    def _build_content(
        self,
        prompt: UniversalPrompt,
        conditional_content: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Build Cline rules content in markdown format."""
        lines = []

        # Header
        lines.append(f"# {prompt.metadata.title}")
        lines.append("")
        lines.append("## Project Overview")
        lines.append(prompt.metadata.description)
        lines.append("")

        # Project Information
        if prompt.context:
            lines.append("## Project Context")
            if prompt.context.project_type:
                lines.append(f"- **Project Type:** {prompt.context.project_type}")
            if prompt.context.technologies:
                lines.append(
                    f"- **Technologies:** {', '.join(prompt.context.technologies)}"
                )
            if prompt.context.description:
                lines.append(f"- **Details:** {prompt.context.description}")
            lines.append("")

        # Collect all instructions (original + conditional)
        all_general_instructions = []
        if prompt.instructions and prompt.instructions.general:
            all_general_instructions.extend(prompt.instructions.general)

        # Add conditional general instructions
        if (
            conditional_content
            and "instructions" in conditional_content
            and "general" in conditional_content["instructions"]
        ):
            all_general_instructions.extend(
                conditional_content["instructions"]["general"]
            )

        # General instructions
        if all_general_instructions:
            lines.append("## Coding Guidelines")
            for instruction in all_general_instructions:
                lines.append(f"- {instruction}")
            lines.append("")

        # Code style instructions
        if prompt.instructions and prompt.instructions.code_style:
            lines.append("## Code Style")
            for guideline in prompt.instructions.code_style:
                lines.append(f"- {guideline}")
            lines.append("")

        # Testing instructions if available
        if (
            prompt.instructions
            and hasattr(prompt.instructions, "testing")
            and prompt.instructions.testing
        ):
            lines.append("## Testing Standards")
            for test_rule in prompt.instructions.testing:
                lines.append(f"- {test_rule}")
            lines.append("")

        # Examples if available
        if prompt.examples:
            lines.append("## Code Examples")
            lines.append("")
            for name, example in prompt.examples.items():
                lines.append(f"### {name.replace('_', ' ').title()}")
                lines.append("```")
                lines.append(example)
                lines.append("```")
                lines.append("")

        return "\n".join(lines)
