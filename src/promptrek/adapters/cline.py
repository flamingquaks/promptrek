"""
Cline (terminal-based AI assistant) adapter implementation.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

import click

from ..core.exceptions import ValidationError
from ..core.models import UniversalPrompt
from .base import EditorAdapter
from .sync_mixin import MarkdownSyncMixin


class ClineAdapter(MarkdownSyncMixin, EditorAdapter):
    """Adapter for Cline terminal-based AI assistant."""

    _description = "Cline (.clinerules, .clinerules/*.md)"
    _file_patterns = [".clinerules", ".clinerules/*.md"]

    def __init__(self) -> None:
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
        headless: bool = False,
    ) -> List[Path]:
        """Generate Cline rules files - supports both single file and directory formats."""

        # Apply variable substitution if supported
        processed_prompt = self.substitute_variables(prompt, variables)

        # Process conditionals if supported
        conditional_content = self.process_conditionals(processed_prompt, variables)

        created_files = []

        # Determine generation mode based on project size/complexity
        use_directory_format = self._should_use_directory_format(processed_prompt)

        if use_directory_format:
            # Generate multiple files in .clinerules/ directory
            created_files = self._generate_directory_format(
                processed_prompt, conditional_content, output_dir, dry_run, verbose
            )
        else:
            # Generate single .clinerules file
            created_files = self._generate_single_file_format(
                processed_prompt, conditional_content, output_dir, dry_run, verbose
            )

        return created_files

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

        # Validate that we have meaningful content to generate rules
        if not prompt.metadata or not prompt.metadata.title:
            errors.append(
                ValidationError(
                    field="metadata.title",
                    message=("Cline rules need a clear project title"),
                )
            )

        return errors

    def supports_variables(self) -> bool:
        """Cline supports variable substitution."""
        return True

    def supports_conditionals(self) -> bool:
        """Cline supports conditional configuration."""
        return True

    def parse_files(self, source_dir: Path) -> UniversalPrompt:
        """Parse Cline files back into a UniversalPrompt."""
        return self.parse_markdown_rules_files(
            source_dir=source_dir,
            rules_subdir=".clinerules",
            file_extension="md",
            editor_name="Cline",
        )

    def _generate_rule_files(
        self,
        prompt: UniversalPrompt,
        conditional_content: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, str]:
        """Generate multiple rule files for modular organization."""
        rule_files = {}

        # 1. Main project overview file
        rule_files["01-project-overview.md"] = self._build_project_overview(prompt)

        # 2. Coding guidelines file
        coding_content = self._build_coding_guidelines(prompt, conditional_content)
        if coding_content:
            rule_files["02-coding-guidelines.md"] = coding_content

        # 3. Code style file
        style_content = self._build_code_style(prompt)
        if style_content:
            rule_files["03-code-style.md"] = style_content

        # 4. Testing standards file
        testing_content = self._build_testing_standards(prompt)
        if testing_content:
            rule_files["04-testing-standards.md"] = testing_content

        # 5. Examples file
        examples_content = self._build_examples(prompt)
        if examples_content:
            rule_files["05-examples.md"] = examples_content

        return rule_files

    def _build_project_overview(self, prompt: UniversalPrompt) -> str:
        """Build project overview content."""
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

        return "\n".join(lines)

    def _build_coding_guidelines(
        self,
        prompt: UniversalPrompt,
        conditional_content: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Build coding guidelines content."""
        lines = []

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
            lines.append("# Coding Guidelines")
            lines.append("")
            lines.append("## General Instructions")
            for instruction in all_general_instructions:
                lines.append(f"- {instruction}")
            lines.append("")

        return "\n".join(lines) if lines else ""

    def _build_code_style(self, prompt: UniversalPrompt) -> str:
        """Build code style content."""
        lines = []

        # Code style instructions
        if prompt.instructions and prompt.instructions.code_style:
            lines.append("# Code Style Guidelines")
            lines.append("")
            lines.append("## Style Rules")
            for guideline in prompt.instructions.code_style:
                lines.append(f"- {guideline}")
            lines.append("")

        return "\n".join(lines) if lines else ""

    def _build_testing_standards(self, prompt: UniversalPrompt) -> str:
        """Build testing standards content."""
        lines = []

        # Testing instructions if available
        if (
            prompt.instructions
            and hasattr(prompt.instructions, "testing")
            and prompt.instructions.testing
        ):
            lines.append("# Testing Standards")
            lines.append("")
            lines.append("## Testing Requirements")
            for test_rule in prompt.instructions.testing:
                lines.append(f"- {test_rule}")
            lines.append("")

        return "\n".join(lines) if lines else ""

    def _build_examples(self, prompt: UniversalPrompt) -> str:
        """Build examples content."""
        lines = []

        # Examples if available
        if prompt.examples:
            lines.append("# Code Examples")
            lines.append("")
            for name, example in prompt.examples.items():
                lines.append(f"## {name.replace('_', ' ').title()}")
                lines.append("```")
                lines.append(example)
                lines.append("```")
                lines.append("")

        return "\n".join(lines) if lines else ""

    def _should_use_directory_format(self, prompt: UniversalPrompt) -> bool:
        """Determine if directory format should be used based on complexity."""
        complexity_score = 0

        # Count different types of content
        if prompt.instructions and prompt.instructions.general:
            complexity_score += len(prompt.instructions.general)
        if prompt.instructions and prompt.instructions.code_style:
            complexity_score += len(prompt.instructions.code_style)
        if (
            prompt.instructions
            and hasattr(prompt.instructions, "testing")
            and prompt.instructions.testing
        ):
            complexity_score += len(prompt.instructions.testing)
        if prompt.examples:
            complexity_score += len(prompt.examples)

        # Use directory format for complex projects (>8 items) or multiple categories
        has_multiple_categories = (
            sum(
                [
                    bool(prompt.instructions and prompt.instructions.general),
                    bool(prompt.instructions and prompt.instructions.code_style),
                    bool(
                        prompt.instructions
                        and hasattr(prompt.instructions, "testing")
                        and prompt.instructions.testing
                    ),
                    bool(prompt.examples),
                ]
            )
            > 2
        )

        return complexity_score > 8 or has_multiple_categories

    def _generate_directory_format(
        self,
        prompt: UniversalPrompt,
        conditional_content: Optional[Dict[str, Any]],
        output_dir: Path,
        dry_run: bool,
        verbose: bool,
    ) -> List[Path]:
        """Generate multiple files in .clinerules/ directory."""
        clinerules_dir = output_dir / ".clinerules"
        created_files = []

        # Generate multiple rule files based on content
        rule_files = self._generate_rule_files(prompt, conditional_content)

        if dry_run:
            click.echo(f"  📁 Would create directory: {clinerules_dir}")
            for filename, content in rule_files.items():
                output_file = clinerules_dir / filename
                click.echo(f"  📄 Would create: {output_file}")
                if verbose:
                    click.echo("      Content preview:")
                    preview = content[:200] + "..." if len(content) > 200 else content
                    click.echo(f"      {preview}")
                created_files.append(output_file)
        else:
            # Create .clinerules directory if it doesn't exist
            clinerules_dir.mkdir(parents=True, exist_ok=True)

            # Create rule files
            for filename, content in rule_files.items():
                output_file = clinerules_dir / filename
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(content)
                click.echo(f"✅ Generated: {output_file}")
                created_files.append(output_file)

        return created_files

    def _generate_single_file_format(
        self,
        prompt: UniversalPrompt,
        conditional_content: Optional[Dict[str, Any]],
        output_dir: Path,
        dry_run: bool,
        verbose: bool,
    ) -> List[Path]:
        """Generate single .clinerules file."""
        output_file = output_dir / ".clinerules"

        # Create unified content for single file
        content = self._build_unified_content(prompt, conditional_content)

        if dry_run:
            click.echo(f"  📄 Would create: {output_file}")
            if verbose:
                click.echo("      Content preview:")
                preview = content[:200] + "..." if len(content) > 200 else content
                click.echo(f"      {preview}")
        else:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(content)
            click.echo(f"✅ Generated: {output_file}")

        return [output_file]

    def _build_unified_content(
        self,
        prompt: UniversalPrompt,
        conditional_content: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Build unified content for single .clinerules file."""
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
