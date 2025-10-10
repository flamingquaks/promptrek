"""
Migrate command implementation.

Handles migration from v1 schema to v2 schema.
"""

from pathlib import Path
from typing import Optional

import click

from ...core.exceptions import CLIError, UPFParsingError
from ...core.models import UniversalPrompt, UniversalPromptV2
from ...core.parser import UPFParser
from ..yaml_writer import write_promptrek_yaml


def migrate_command(
    ctx: click.Context,
    input_file: Path,
    output_file: Optional[Path],
    force: bool,
) -> None:
    """
    Migrate a v1 .promptrek.yaml file to v2 format.

    Args:
        ctx: Click context
        input_file: Path to v1 .promptrek.yaml file
        output_file: Path for v2 output file (optional)
        force: Overwrite output file if it exists
    """
    verbose = ctx.obj.get("verbose", False)

    # Parse input file
    parser = UPFParser()
    try:
        prompt = parser.parse_file(input_file)
        if verbose:
            click.echo(f"✅ Parsed {input_file}")
    except UPFParsingError as e:
        raise CLIError(f"Failed to parse {input_file}: {e}")

    # Check if already v2
    if isinstance(prompt, UniversalPromptV2):
        click.echo(f"ℹ️  {input_file} is already v2 format, no migration needed")
        return

    # Convert to v2
    v2_prompt = _convert_v1_to_v2(prompt, verbose)

    # Determine output path
    if not output_file:
        # Default: replace .promptrek.yaml with .v2.promptrek.yaml
        output_file = input_file.parent / f"{input_file.stem}.v2{input_file.suffix}"

    # Check if output file exists
    if output_file.exists() and not force:
        raise CLIError(
            f"Output file {output_file} already exists. Use --force to overwrite."
        )

    # Write v2 file
    v2_dict = v2_prompt.model_dump(exclude_none=True)
    write_promptrek_yaml(v2_dict, output_file)

    click.echo(f"✅ Migrated {input_file} → {output_file}")
    click.echo("   Schema version: 1.0.0 → 2.0.0")
    if verbose:
        click.echo(f"   Content length: {len(v2_prompt.content)} characters")
        if v2_prompt.documents:
            click.echo(f"   Documents: {len(v2_prompt.documents)}")


def _convert_v1_to_v2(
    prompt: UniversalPrompt, verbose: bool = False
) -> UniversalPromptV2:
    """
    Convert a v1 UniversalPrompt to v2 UniversalPromptV2.

    Args:
        prompt: v1 UniversalPrompt to convert
        verbose: Enable verbose output

    Returns:
        UniversalPromptV2 with markdown content
    """
    # Build markdown content from v1 structured fields
    content = _build_markdown_from_v1(prompt)

    if verbose:
        click.echo("   Converting structured fields to markdown...")
        if prompt.targets:
            click.echo(
                f"   Note: v2 format works with all editors (removed targets: {', '.join(prompt.targets)})"
            )

    # Preserve metadata (update schema_version will be done by model)
    metadata = prompt.metadata

    # Preserve variables if present
    variables = prompt.variables if prompt.variables else None

    return UniversalPromptV2(
        schema_version="2.0.0",
        metadata=metadata,
        content=content,
        documents=None,  # v1 doesn't have multi-document structure
        variables=variables,
    )


def _build_markdown_from_v1(prompt: UniversalPrompt) -> str:
    """
    Build markdown content from v1 structured fields.

    Uses a generic structure that preserves all v1 information.
    """
    lines = []

    # Header
    lines.append(f"# {prompt.metadata.title}")
    lines.append("")
    lines.append(prompt.metadata.description)
    lines.append("")

    # Project context
    if prompt.context:
        lines.append("## Project Details")
        if prompt.context.project_type:
            lines.append(f"**Project Type:** {prompt.context.project_type}")
        if prompt.context.technologies:
            lines.append(f"**Technologies:** {', '.join(prompt.context.technologies)}")
        if prompt.context.description:
            lines.append("")
            lines.append("**Description:**")
            lines.append(prompt.context.description)
        lines.append("")

    # Instructions
    if prompt.instructions:
        lines.append("## Development Guidelines")
        lines.append("")

        if prompt.instructions.general:
            lines.append("### General Principles")
            for instruction in prompt.instructions.general:
                lines.append(f"- {instruction}")
            lines.append("")

        if prompt.instructions.code_style:
            lines.append("### Code Style Requirements")
            for guideline in prompt.instructions.code_style:
                lines.append(f"- {guideline}")
            lines.append("")

        if prompt.instructions.architecture:
            lines.append("### Architecture Guidelines")
            for guideline in prompt.instructions.architecture:
                lines.append(f"- {guideline}")
            lines.append("")

        if prompt.instructions.testing:
            lines.append("### Testing Standards")
            for guideline in prompt.instructions.testing:
                lines.append(f"- {guideline}")
            lines.append("")

        if prompt.instructions.security:
            lines.append("### Security Requirements")
            for guideline in prompt.instructions.security:
                lines.append(f"- {guideline}")
            lines.append("")

        if prompt.instructions.performance:
            lines.append("### Performance Guidelines")
            for guideline in prompt.instructions.performance:
                lines.append(f"- {guideline}")
            lines.append("")

    # Examples
    if prompt.examples:
        lines.append("## Code Examples")
        lines.append("")
        for name, example in prompt.examples.items():
            lines.append(f"### {name.replace('_', ' ').title()}")
            lines.append(example)
            lines.append("")

    # Conditions (if present)
    if prompt.conditions:
        lines.append("## Conditional Instructions")
        lines.append("")
        lines.append("*Note: Conditional instructions from v1 are preserved below:*")
        lines.append("")
        for i, condition in enumerate(prompt.conditions, 1):
            lines.append(f"**Condition {i}:** If `{condition.if_condition}`")
            lines.append("")
            if condition.then_instructions:
                lines.append("Then apply these instructions:")
                for inst in condition.then_instructions:
                    lines.append(f"- {inst}")
            if condition.then_examples:
                lines.append("")
                lines.append("Examples:")
                for name, example in condition.then_examples.items():
                    lines.append(f"**{name}:**")
                    lines.append(example)
            lines.append("")

    # AI Assistant instructions (generic footer)
    lines.append("## AI Assistant Instructions")
    lines.append("")
    lines.append("When working on this project:")
    lines.append("- Follow the established patterns and conventions shown above")
    lines.append("- Maintain consistency with the existing codebase")
    lines.append("- Consider the project context and requirements in all suggestions")
    lines.append("- Prioritize code quality, maintainability, and best practices")

    return "\n".join(lines)
