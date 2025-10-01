"""
Kiro (AI-powered assistance) adapter implementation.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

import click

from ..core.exceptions import ValidationError
from ..core.models import UniversalPrompt
from .base import EditorAdapter
from .sync_mixin import MarkdownSyncMixin


class KiroAdapter(MarkdownSyncMixin, EditorAdapter):
    """Adapter for Kiro AI-powered assistance."""

    _description = "Kiro (.kiro/steering/)"
    _file_patterns = [".kiro/steering/*.md"]

    def __init__(self) -> None:
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
        headless: bool = False,
    ) -> List[Path]:
        """Generate Kiro configuration files."""

        # Apply variable substitution if supported
        processed_prompt = self.substitute_variables(prompt, variables)

        # Process conditionals if supported
        conditional_content = self.process_conditionals(processed_prompt, variables)

        # Always generate core steering documents
        steering_files = self._generate_steering_documents(
            processed_prompt, conditional_content, output_dir, dry_run, verbose
        )

        return steering_files

    def _generate_steering_documents(
        self,
        prompt: UniversalPrompt,
        conditional_content: Optional[Dict[str, Any]],
        output_dir: Path,
        dry_run: bool,
        verbose: bool,
    ) -> List[Path]:
        """Generate core .kiro/steering/ documents."""
        steering_dir = output_dir / ".kiro" / "steering"
        created_files = []

        # Generate main project steering document
        main_file = steering_dir / "project.md"
        main_content = self._build_project_steering(prompt, conditional_content)

        if dry_run:
            click.echo(f"  📁 Would create: {main_file}")
            if verbose:
                preview = (
                    main_content[:200] + "..."
                    if len(main_content) > 200
                    else main_content
                )
                click.echo(f"    {preview}")
            created_files.append(main_file)
        else:
            steering_dir.mkdir(parents=True, exist_ok=True)
            with open(main_file, "w", encoding="utf-8") as f:
                f.write(main_content)
            click.echo(f"✅ Generated: {main_file}")
            created_files.append(main_file)

        # Generate instruction category steering documents
        if prompt.instructions:
            instruction_data = prompt.instructions.model_dump()
            for category, instructions in instruction_data.items():
                if instructions:  # Only create files for non-empty categories
                    category_file = steering_dir / f"{category.replace('_', '-')}.md"
                    category_content = self._build_category_steering(
                        category, instructions, prompt
                    )

                    if dry_run:
                        click.echo(f"  📁 Would create: {category_file}")
                        if verbose:
                            preview = (
                                category_content[:200] + "..."
                                if len(category_content) > 200
                                else category_content
                            )
                            click.echo(f"    {preview}")
                        created_files.append(category_file)
                    else:
                        with open(category_file, "w", encoding="utf-8") as f:
                            f.write(category_content)
                        click.echo(f"✅ Generated: {category_file}")
                        created_files.append(category_file)

        return created_files

    def _build_project_steering(
        self, prompt: UniversalPrompt, conditional_content: Optional[Dict[str, Any]]
    ) -> str:
        """Build main project steering document."""
        lines = []

        lines.append("---")
        lines.append("inclusion: always")
        lines.append("---")
        lines.append("")
        lines.append(f"# {prompt.metadata.title}")
        lines.append("")
        lines.append(prompt.metadata.description)
        lines.append("")

        # Project Context
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

        # General instructions
        if prompt.instructions and prompt.instructions.general:
            lines.append("## Core Guidelines")
            for instruction in prompt.instructions.general:
                lines.append(f"- {instruction}")
            lines.append("")

        return "\n".join(lines)

    def _build_category_steering(
        self, category: str, instructions: List[str], prompt: UniversalPrompt
    ) -> str:
        """Build category-specific steering document."""
        lines = []

        # Frontmatter
        lines.append("---")
        lines.append("inclusion: always")
        lines.append("---")
        lines.append("")

        # Title
        category_title = category.replace("_", " ").title()
        lines.append(f"# {category_title}")
        lines.append("")

        # Instructions
        for instruction in instructions:
            lines.append(f"- {instruction}")
        lines.append("")

        # Add context if relevant
        if category in ["architecture", "code_style", "performance"]:
            lines.append("## Additional Context")
            if prompt.context and prompt.context.technologies:
                lines.append(
                    f"This project uses: {', '.join(prompt.context.technologies)}"
                )
                lines.append("")

        return "\n".join(lines)

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

    def parse_files(self, source_dir: Path) -> UniversalPrompt:
        """Parse Kiro files back into a UniversalPrompt."""
        return self.parse_markdown_rules_files(
            source_dir=source_dir,
            rules_subdir=".kiro/steering",
            file_extension="md",
            editor_name="Kiro",
        )
