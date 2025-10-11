"""
Kiro (AI-powered assistance) adapter implementation.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import click

from ..core.exceptions import ValidationError
from ..core.models import (
    DocumentConfig,
    PromptMetadata,
    UniversalPrompt,
    UniversalPromptV2,
)
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
        prompt: Union[UniversalPrompt, UniversalPromptV2],
        output_dir: Path,
        dry_run: bool = False,
        verbose: bool = False,
        variables: Optional[Dict[str, Any]] = None,
        headless: bool = False,
    ) -> List[Path]:
        """Generate Kiro configuration files."""

        # V2: Use documents field for multi-file steering
        if isinstance(prompt, UniversalPromptV2):
            return self._generate_v2(prompt, output_dir, dry_run, verbose, variables)

        # V1: Apply variable substitution if supported
        processed_prompt = self.substitute_variables(prompt, variables)
        assert isinstance(
            processed_prompt, UniversalPrompt
        ), "V1 path should have UniversalPrompt"

        # Process conditionals if supported
        conditional_content = self.process_conditionals(processed_prompt, variables)

        # Always generate core steering documents
        steering_files = self._generate_steering_documents(
            processed_prompt, conditional_content, output_dir, dry_run, verbose
        )

        return steering_files

    def _generate_v2(
        self,
        prompt: UniversalPromptV2,
        output_dir: Path,
        dry_run: bool,
        verbose: bool,
        variables: Optional[Dict[str, Any]] = None,
    ) -> List[Path]:
        """Generate Kiro files from v2 schema (using documents for steering docs)."""
        steering_dir = output_dir / ".kiro" / "steering"
        created_files = []

        # If documents field is present, generate separate steering files
        if prompt.documents:
            for doc in prompt.documents:
                # Apply variable substitution
                content = doc.content
                if variables:
                    for var_name, var_value in variables.items():
                        placeholder = "{{{ " + var_name + " }}}"
                        content = content.replace(placeholder, var_value)

                # Generate filename from document name
                filename = (
                    f"{doc.name}.md" if not doc.name.endswith(".md") else doc.name
                )
                output_file = steering_dir / filename

                if dry_run:
                    click.echo(f"  📁 Would create: {output_file}")
                    if verbose:
                        preview = (
                            content[:200] + "..." if len(content) > 200 else content
                        )
                        click.echo(f"    {preview}")
                    created_files.append(output_file)
                else:
                    steering_dir.mkdir(parents=True, exist_ok=True)
                    with open(output_file, "w", encoding="utf-8") as f:
                        f.write(content)
                    click.echo(f"✅ Generated: {output_file}")
                    created_files.append(output_file)
        else:
            # No documents, use main content as project steering
            content = prompt.content
            if variables:
                for var_name, var_value in variables.items():
                    placeholder = "{{{ " + var_name + " }}}"
                    content = content.replace(placeholder, var_value)

            output_file = steering_dir / "project.md"

            if dry_run:
                click.echo(f"  📁 Would create: {output_file}")
                if verbose:
                    preview = content[:200] + "..." if len(content) > 200 else content
                    click.echo(f"    {preview}")
                created_files.append(output_file)
            else:
                steering_dir.mkdir(parents=True, exist_ok=True)
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(content)
                click.echo(f"✅ Generated: {output_file}")
                created_files.append(output_file)

        return created_files

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

    def validate(
        self, prompt: Union[UniversalPrompt, UniversalPromptV2]
    ) -> List[ValidationError]:
        """Validate prompt for Kiro."""
        errors = []

        # V2 validation: check content exists
        if isinstance(prompt, UniversalPromptV2):
            if not prompt.content or not prompt.content.strip():
                errors.append(
                    ValidationError(
                        field="content",
                        message="Kiro requires content",
                        severity="error",
                    )
                )
            return errors

        # V1 validation: Kiro works well with structured instructions
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

    def parse_files(
        self, source_dir: Path
    ) -> Union[UniversalPrompt, UniversalPromptV2]:
        """Parse Kiro files back into a UniversalPromptV2."""
        # Parse markdown files from .kiro/steering/
        steering_dir = source_dir / ".kiro" / "steering"

        if not steering_dir.exists():
            # Fallback to v1 parsing
            return self.parse_markdown_rules_files(
                source_dir=source_dir,
                rules_subdir=".kiro/steering",
                file_extension="md",
                editor_name="Kiro",
            )

        # V2: Parse each markdown file as a document
        documents = []
        main_content_parts = []

        for md_file in sorted(steering_dir.glob("*.md")):
            try:
                with open(md_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Create document for this file
                doc_name = md_file.stem  # Remove .md extension
                documents.append(
                    DocumentConfig(
                        name=doc_name,
                        content=content.strip(),
                    )
                )

                # Also add to main content
                main_content_parts.append(
                    f"## {doc_name.replace('-', ' ').title()}\n\n{content}"
                )

            except Exception as e:
                click.echo(f"Warning: Could not parse {md_file}: {e}")

        # Create metadata
        metadata = PromptMetadata(
            title="Kiro AI Assistant",
            description="Configuration synced from Kiro steering documents",
            version="1.0.0",
            author="PrompTrek Sync",
            created=datetime.now().isoformat(),
            updated=datetime.now().isoformat(),
            tags=["kiro", "synced"],
        )

        # Build main content from all documents
        main_content = (
            "\n\n".join(main_content_parts)
            if main_content_parts
            else "# Kiro AI Assistant\n\nNo steering docs found."
        )

        return UniversalPromptV2(
            schema_version="2.0.0",
            metadata=metadata,
            content=main_content,
            documents=documents if documents else None,
            variables={},
        )
