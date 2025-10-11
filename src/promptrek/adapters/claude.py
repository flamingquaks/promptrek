"""
Claude Code adapter implementation.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import click

from ..core.exceptions import ValidationError
from ..core.models import UniversalPrompt, UniversalPromptV2
from .base import EditorAdapter
from .sync_mixin import SingleFileMarkdownSyncMixin


class ClaudeAdapter(SingleFileMarkdownSyncMixin, EditorAdapter):
    """Adapter for Claude Code."""

    _description = "Claude Code (context-based)"
    _file_patterns = [".claude/CLAUDE.md", ".claude-context.md"]

    def __init__(self) -> None:
        super().__init__(
            name="claude",
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
        """Generate Claude Code context files."""

        # Determine output path
        claude_dir = output_dir / ".claude"
        output_file = claude_dir / "CLAUDE.md"

        # Check if this is v2 (simplified) or v1 (complex)
        if isinstance(prompt, UniversalPromptV2):
            # V2: Direct markdown output (lossless!)
            content = prompt.content

            # Apply variable substitution if variables provided
            if variables:
                for var_name, var_value in variables.items():
                    # Replace {{{ VAR_NAME }}} with value
                    placeholder = "{{{ " + var_name + " }}}"
                    content = content.replace(placeholder, var_value)
        else:
            # V1: Build content from structured fields
            processed_prompt = self.substitute_variables(prompt, variables)
            assert isinstance(
                processed_prompt, UniversalPrompt
            ), "V1 path should have UniversalPrompt"
            conditional_content = self.process_conditionals(processed_prompt, variables)
            content = self._build_content(processed_prompt, conditional_content)

        if dry_run:
            click.echo(f"  📁 Would create: {output_file}")
            if verbose:
                click.echo("  📄 Content preview:")
                preview = content[:200] + "..." if len(content) > 200 else content
                click.echo(f"    {preview}")
        else:
            # Create directory and file
            claude_dir.mkdir(exist_ok=True)
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(content)
            click.echo(f"✅ Generated: {output_file}")

        return [output_file]

    def generate_multiple(
        self,
        prompt_files: List[Tuple[Union[UniversalPrompt, UniversalPromptV2], Path]],
        output_dir: Path,
        dry_run: bool = False,
        verbose: bool = False,
        variables: Optional[Dict[str, Any]] = None,
        headless: bool = False,
    ) -> List[Path]:
        """Generate separate Claude context files for each prompt file."""

        claude_dir = output_dir / ".claude"
        generated_files = []

        for prompt, source_file in prompt_files:
            # Only support v1 prompts in generate_multiple (for now)
            # V2 prompts should use the main generate() method
            if isinstance(prompt, UniversalPromptV2):
                click.echo(
                    f"⚠️  Skipping v2 prompt from {source_file} (use generate() instead)"
                )
                continue

            # Apply variable substitution if supported
            processed_prompt = self.substitute_variables(prompt, variables)
            assert isinstance(
                processed_prompt, UniversalPrompt
            ), "V1 path should have UniversalPrompt"

            # Process conditionals if supported
            conditional_content = self.process_conditionals(processed_prompt, variables)

            # Create content
            content = self._build_content(processed_prompt, conditional_content)

            # Generate filename based on source file name
            # Remove .promptrek.yaml and add .md extension
            base_name = source_file.stem
            if base_name.endswith(".promptrek"):
                base_name = base_name.removesuffix(
                    ".promptrek"
                )  # Remove .promptrek suffix
            output_file = claude_dir / f"{base_name}.md"

            if dry_run:
                click.echo(f"  📁 Would create: {output_file}")
                if verbose:
                    click.echo("  📄 Content preview:")
                    preview = content[:200] + "..." if len(content) > 200 else content
                    click.echo(f"    {preview}")
            else:
                # Create directory and file
                claude_dir.mkdir(exist_ok=True)
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(content)
                click.echo(f"✅ Generated: {output_file}")

            generated_files.append(output_file)

        return generated_files

    def validate(
        self, prompt: Union[UniversalPrompt, UniversalPromptV2]
    ) -> List[ValidationError]:
        """Validate prompt for Claude."""
        errors = []

        # V2 validation: just check content exists
        if isinstance(prompt, UniversalPromptV2):
            if not prompt.content or not prompt.content.strip():
                errors.append(
                    ValidationError(
                        field="content",
                        message="Content cannot be empty",
                        severity="error",
                    )
                )
            return errors

        # V1 validation: check context and examples
        if not prompt.context:
            errors.append(
                ValidationError(
                    field="context",
                    message=(
                        "Claude works best with detailed project context " "information"
                    ),
                    severity="warning",
                )
            )

        if not prompt.examples:
            errors.append(
                ValidationError(
                    field="examples",
                    message=(
                        "Claude benefits from code examples for better " "understanding"
                    ),
                    severity="warning",
                )
            )

        return errors

    def supports_variables(self) -> bool:
        """Claude supports variable substitution."""
        return True

    def supports_conditionals(self) -> bool:
        """Claude supports conditional instructions."""
        return True

    def parse_files(
        self, source_dir: Path
    ) -> Union[UniversalPrompt, UniversalPromptV2]:
        """
        Parse Claude Code files back into a UniversalPrompt.

        Uses v2 format by default for lossless sync.
        """
        file_path = ".claude/CLAUDE.md"
        # Use v2 sync for lossless roundtrip
        return self.parse_single_markdown_file_v2(
            source_dir=source_dir,
            file_path=file_path,
            editor_name="Claude Code",
        )

    def _build_content(
        self,
        prompt: UniversalPrompt,
        conditional_content: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Build Claude Code context content."""
        lines = []

        # Header with clear context
        lines.append(f"# {prompt.metadata.title}")
        lines.append("")
        lines.append("## Project Overview")
        lines.append(prompt.metadata.description)
        lines.append("")

        # Project context is crucial for Claude
        if prompt.context:
            lines.append("## Project Details")
            if prompt.context.project_type:
                lines.append(f"**Project Type:** {prompt.context.project_type}")
            if prompt.context.technologies:
                lines.append(
                    f"**Technologies:** {', '.join(prompt.context.technologies)}"
                )
            if prompt.context.description:
                lines.append("")
                lines.append("**Description:**")
                lines.append(prompt.context.description)
            lines.append("")

        # Instructions organized for Claude's understanding
        if prompt.instructions or (
            conditional_content and "instructions" in conditional_content
        ):
            lines.append("## Development Guidelines")

            # Combine original and conditional instructions
            all_instructions = prompt.instructions if prompt.instructions else None

            if all_instructions and all_instructions.general:
                lines.append("### General Principles")
                for instruction in all_instructions.general:
                    lines.append(f"- {instruction}")

                # Add conditional general instructions
                if (
                    conditional_content
                    and "instructions" in conditional_content
                    and "general" in conditional_content["instructions"]
                ):
                    for instruction in conditional_content["instructions"]["general"]:
                        lines.append(f"- {instruction}")
                lines.append("")
            elif (
                conditional_content
                and "instructions" in conditional_content
                and "general" in conditional_content["instructions"]
            ):
                lines.append("### General Principles")
                for instruction in conditional_content["instructions"]["general"]:
                    lines.append(f"- {instruction}")
                lines.append("")

            if all_instructions and all_instructions.code_style:
                lines.append("### Code Style Requirements")
                for guideline in all_instructions.code_style:
                    lines.append(f"- {guideline}")
                lines.append("")

            if all_instructions and all_instructions.testing:
                lines.append("### Testing Standards")
                for guideline in all_instructions.testing:
                    lines.append(f"- {guideline}")
                lines.append("")

            # Add architecture guidelines if present
            if (
                all_instructions
                and hasattr(all_instructions, "architecture")
                and all_instructions.architecture
            ):
                lines.append("### Architecture Guidelines")
                for guideline in all_instructions.architecture:
                    lines.append(f"- {guideline}")
                lines.append("")

        # Examples are very useful for Claude
        examples_to_show = {}
        if prompt.examples:
            examples_to_show.update(prompt.examples)

        # Add conditional examples
        if conditional_content and "examples" in conditional_content:
            examples_to_show.update(conditional_content["examples"])

        if examples_to_show:
            lines.append("## Code Examples")
            lines.append("")
            lines.append(
                "The following examples demonstrate the expected code patterns "
                "and style:"
            )
            lines.append("")

            for name, example in examples_to_show.items():
                lines.append(f"### {name.replace('_', ' ').title()}")
                lines.append(example)
                lines.append("")

        # Claude-specific instructions
        lines.append("## AI Assistant Instructions")
        lines.append("")
        lines.append("When working on this project:")
        lines.append("- Follow the established patterns and conventions shown above")
        lines.append("- Maintain consistency with the existing codebase")
        lines.append(
            "- Consider the project context and requirements in all " "suggestions"
        )
        lines.append("- Prioritize code quality, maintainability, and best practices")
        if prompt.context and prompt.context.technologies:
            tech_list = ", ".join(prompt.context.technologies)
            lines.append(f"- Leverage {tech_list} best practices and idioms")

        return "\n".join(lines)
