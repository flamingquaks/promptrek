"""
Kiro (AI-powered assistance) adapter implementation.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import click

from ..core.exceptions import DeprecationWarnings, ValidationError
from ..core.models import (
    DocumentConfig,
    PromptMetadata,
    UniversalPrompt,
    UniversalPromptV2,
    UniversalPromptV3,
)
from .base import EditorAdapter
from .mcp_mixin import MCPGenerationMixin
from .sync_mixin import MarkdownSyncMixin


class KiroAdapter(MCPGenerationMixin, MarkdownSyncMixin, EditorAdapter):
    """Adapter for Kiro AI-powered assistance."""

    _description = "Kiro (.kiro/steering/)"
    _file_patterns = [".kiro/steering/*.md"]

    def __init__(self) -> None:
        super().__init__(
            name="kiro",
            description=self._description,
            file_patterns=self._file_patterns,
        )

    def get_mcp_config_strategy(self) -> Dict[str, Any]:
        """Get MCP configuration strategy for Kiro adapter."""
        return {
            "supports_project": True,
            "project_path": ".kiro/settings/mcp.json",
            "system_path": None,  # Kiro only supports project-level
            "requires_confirmation": False,
            "config_format": "json",
        }

    def generate(
        self,
        prompt: Union[UniversalPrompt, UniversalPromptV2, UniversalPromptV3],
        output_dir: Path,
        dry_run: bool = False,
        verbose: bool = False,
        variables: Optional[Dict[str, Any]] = None,
        headless: bool = False,
    ) -> List[Path]:
        """Generate Kiro configuration files."""

        # V3: Always use plugin generation (handles steering docs + plugins)
        if isinstance(prompt, UniversalPromptV3):
            return self._generate_plugins(
                prompt, output_dir, dry_run, verbose, variables
            )

        # V2.1: Handle plugins if present
        if isinstance(prompt, UniversalPromptV2) and prompt.plugins:
            return self._generate_plugins(
                prompt, output_dir, dry_run, verbose, variables
            )

        # V2: Use documents field for multi-file steering (no plugins)
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
        prompt: Union[UniversalPromptV2, UniversalPromptV3],
        output_dir: Path,
        dry_run: bool,
        verbose: bool,
        variables: Optional[Dict[str, Any]] = None,
    ) -> List[Path]:
        """Generate Kiro files from v2/v3 schema (using documents for steering docs)."""
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

    def _generate_plugins(
        self,
        prompt: Union[UniversalPromptV2, UniversalPromptV3],
        output_dir: Path,
        dry_run: bool,
        verbose: bool,
        variables: Optional[Dict[str, Any]] = None,
    ) -> List[Path]:
        """Generate Kiro files from v2.1/v3.0 schema with plugin support."""
        created_files = []

        # First, generate the regular v2/v3 steering docs
        steering_files = self._generate_v2(
            prompt, output_dir, dry_run, verbose, variables
        )
        created_files.extend(steering_files)

        # Then, extract and handle MCP servers from either v3 top-level or v2.1 nested structure
        mcp_servers = None

        if isinstance(prompt, UniversalPromptV3):
            # V3: Check top-level field
            mcp_servers = prompt.mcp_servers
        elif isinstance(prompt, UniversalPromptV2) and prompt.plugins:
            # V2.1: Use nested plugins structure (deprecated)
            if prompt.plugins.mcp_servers:
                click.echo(
                    DeprecationWarnings.v3_nested_plugin_field_warning("mcp_servers")
                )
                mcp_servers = prompt.plugins.mcp_servers

        # Generate MCP config if we have MCP servers
        if mcp_servers:
            mcp_files = self._generate_mcp_config(
                mcp_servers,
                output_dir,
                dry_run,
                verbose,
                variables,
            )
            created_files.extend(mcp_files)

        return created_files

    def _generate_mcp_config(
        self,
        mcp_servers: list,
        output_dir: Path,
        dry_run: bool,
        verbose: bool,
        variables: Optional[Dict[str, Any]] = None,
    ) -> List[Path]:
        """Generate MCP configuration for Kiro (project-only)."""
        strategy = self.get_mcp_config_strategy()
        created_files = []

        # Kiro only supports project-level
        if strategy["supports_project"] and strategy["project_path"]:
            project_config_path = output_dir / strategy["project_path"]

            # Build MCP servers config (uses standard MCP format)
            mcp_config = self.build_mcp_servers_config(
                mcp_servers, variables, format_style="standard"
            )

            # Check if config already exists
            existing_config = self.read_existing_mcp_config(project_config_path)

            if existing_config:
                # Merge with existing config
                if verbose:
                    click.echo("  ℹ️  Merging MCP servers with existing Kiro config")
                merged_config = self.merge_mcp_config(
                    existing_config, mcp_config, format_style="standard"
                )
            else:
                merged_config = mcp_config

            # Write the config
            if self.write_mcp_config_file(
                merged_config, project_config_path, dry_run, verbose
            ):
                created_files.append(project_config_path)

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
        self, prompt: Union[UniversalPrompt, UniversalPromptV2, UniversalPromptV3]
    ) -> List[ValidationError]:
        """Validate prompt for Kiro."""
        errors = []

        # V2/V3 validation: check content exists
        if isinstance(prompt, (UniversalPromptV2, UniversalPromptV3)):
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
    ) -> Union[UniversalPrompt, UniversalPromptV2, UniversalPromptV3]:
        """Parse Kiro files back into a UniversalPromptV2 or UniversalPromptV3."""
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
