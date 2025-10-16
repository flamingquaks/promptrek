"""
Migrate command implementation.

Handles migration from v1 schema to v2 schema.
"""

from pathlib import Path
from typing import Optional

import click

from ...core.exceptions import CLIError, UPFParsingError
from ...core.models import UniversalPrompt, UniversalPromptV2, UniversalPromptV3
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

    # Check schema version and determine migration path
    if isinstance(prompt, UniversalPromptV3):
        # Already v3, check if using deprecated nested structure
        if (
            hasattr(prompt, "plugins")
            and prompt.plugins
            and isinstance(prompt.plugins, dict)
        ):
            click.echo(
                f"ℹ️  {input_file} is v3.0 but uses deprecated nested plugins structure"
            )
            click.echo("   Migration not needed - parser auto-promotes fields")
        else:
            click.echo(f"ℹ️  {input_file} is already v3.0 format, no migration needed")
        return
    elif isinstance(prompt, UniversalPromptV2):
        # Check if v2.1
        if prompt.schema_version.startswith("2.1"):
            # Migrate v2.1 → v3.0
            click.echo(f"ℹ️  Migrating from v{prompt.schema_version} to v3.0.0...")
            v3_prompt = _convert_v21_to_v3(prompt, verbose)
            old_version = prompt.schema_version
            new_version = "3.0.0"
        else:
            # Migrate v2.0 → v3.0 (skip v2.1)
            click.echo(f"ℹ️  Migrating from v{prompt.schema_version} to v3.0.0...")
            v3_prompt = _convert_v2_to_v3(prompt, verbose)
            old_version = prompt.schema_version
            new_version = "3.0.0"
    else:
        # Convert v1 → v3.0 (modern format)
        click.echo("ℹ️  Migrating from v1.0.0 to v3.0.0...")
        v3_prompt = _convert_v1_to_v3(prompt, verbose)
        old_version = "1.0.0"
        new_version = "3.0.0"

    # Determine output path
    if not output_file:
        # Default: replace .promptrek.yaml with .v3.promptrek.yaml
        output_file = input_file.parent / f"{input_file.stem}.v3{input_file.suffix}"

    # Check if output file exists
    if output_file.exists() and not force:
        raise CLIError(
            f"Output file {output_file} already exists. Use --force to overwrite."
        )

    # Write v3.0 file
    v3_dict = v3_prompt.model_dump(exclude_none=True)
    write_promptrek_yaml(v3_dict, output_file)

    click.echo(f"✅ Migrated {input_file} → {output_file}")
    click.echo(f"   Schema version: {old_version} → {new_version}")
    if verbose:
        click.echo(f"   Content length: {len(v3_prompt.content)} characters")
        if v3_prompt.documents:
            click.echo(f"   Documents: {len(v3_prompt.documents)}")
        if v3_prompt.mcp_servers:
            click.echo(f"   MCP Servers: {len(v3_prompt.mcp_servers)}")
        if v3_prompt.commands:
            click.echo(f"   Commands: {len(v3_prompt.commands)}")
        if v3_prompt.agents:
            click.echo(f"   Agents: {len(v3_prompt.agents)}")
        if v3_prompt.hooks:
            click.echo(f"   Hooks: {len(v3_prompt.hooks)}")


def _convert_v21_to_v3(
    prompt: UniversalPromptV2, verbose: bool = False
) -> UniversalPromptV3:
    """
    Convert a v2.1 UniversalPromptV2 to v3.0 UniversalPromptV3.

    Promotes nested plugins.* fields to top-level.

    Args:
        prompt: v2.1 UniversalPromptV2 to convert
        verbose: Enable verbose output

    Returns:
        UniversalPromptV3 with top-level plugin fields
    """
    if verbose:
        click.echo("   Promoting nested plugins fields to top-level...")

    # Extract plugin fields from nested structure
    mcp_servers = None
    commands = None
    agents = None
    hooks = None

    if prompt.plugins:
        if prompt.plugins.mcp_servers:
            mcp_servers = prompt.plugins.mcp_servers
            if verbose:
                click.echo(f"   Moved {len(mcp_servers)} MCP servers to top-level")
        if prompt.plugins.commands:
            commands = prompt.plugins.commands
            if verbose:
                click.echo(f"   Moved {len(commands)} commands to top-level")
        if prompt.plugins.agents:
            agents = prompt.plugins.agents
            if verbose:
                click.echo(f"   Moved {len(agents)} agents to top-level")
        if prompt.plugins.hooks:
            hooks = prompt.plugins.hooks
            if verbose:
                click.echo(f"   Moved {len(hooks)} hooks to top-level")

    return UniversalPromptV3(
        schema_version="3.0.0",
        metadata=prompt.metadata,
        content=prompt.content,
        documents=prompt.documents,
        variables=prompt.variables,
        mcp_servers=mcp_servers,
        commands=commands,
        agents=agents,
        hooks=hooks,
        plugins=None,  # Repurposed for marketplace entries in v3
    )


def _convert_v2_to_v3(
    prompt: UniversalPromptV2, verbose: bool = False
) -> UniversalPromptV3:
    """
    Convert a v2.0 UniversalPromptV2 to v3.0 UniversalPromptV3.

    Args:
        prompt: v2.0 UniversalPromptV2 to convert
        verbose: Enable verbose output

    Returns:
        UniversalPromptV3
    """
    if verbose:
        click.echo("   Upgrading v2.0 to v3.0 schema...")

    return UniversalPromptV3(
        schema_version="3.0.0",
        metadata=prompt.metadata,
        content=prompt.content,
        documents=prompt.documents,
        variables=prompt.variables,
        mcp_servers=None,  # v2.0 doesn't have plugins
        commands=None,
        agents=None,
        hooks=None,
        plugins=None,
    )


def _convert_v1_to_v3(
    prompt: UniversalPrompt, verbose: bool = False
) -> UniversalPromptV3:
    """
    Convert a v1 UniversalPrompt to v3.0 UniversalPromptV3.

    Args:
        prompt: v1 UniversalPrompt to convert
        verbose: Enable verbose output

    Returns:
        UniversalPromptV3 with markdown content
    """
    # Build markdown content from v1 structured fields
    content = _build_markdown_from_v1(prompt)

    if verbose:
        click.echo("   Converting structured fields to markdown...")
        if prompt.targets:
            click.echo(
                f"   Note: v3 format works with all editors (removed targets: {', '.join(prompt.targets)})"
            )

    # Preserve metadata
    metadata = prompt.metadata

    # Preserve variables if present
    variables = prompt.variables if prompt.variables else None

    return UniversalPromptV3(
        schema_version="3.0.0",
        metadata=metadata,
        content=content,
        documents=None,  # v1 doesn't have multi-document structure
        variables=variables,
        mcp_servers=None,  # v1 doesn't have plugins
        commands=None,
        agents=None,
        hooks=None,
        plugins=None,
    )


def _convert_v1_to_v2(
    prompt: UniversalPrompt, verbose: bool = False
) -> UniversalPromptV2:
    """
    Convert a v1 UniversalPrompt to v2 UniversalPromptV2.

    DEPRECATED: Use _convert_v1_to_v3 instead for new migrations.

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
        schema_version="2.1.0",
        metadata=metadata,
        content=content,
        documents=None,  # v1 doesn't have multi-document structure
        variables=variables,
        plugins=None,  # v2.1.0 field (optional)
    )


def _upgrade_v2_to_v21(
    prompt: UniversalPromptV2, verbose: bool = False
) -> UniversalPromptV2:
    """
    Upgrade a v2.0.0 UniversalPromptV2 to v2.1.0.

    Args:
        prompt: v2.0.0 UniversalPromptV2 to upgrade
        verbose: Enable verbose output

    Returns:
        UniversalPromptV2 with v2.1.0 schema
    """
    if verbose:
        click.echo("   Upgrading to v2.1.0 schema (adds plugin support)...")

    return UniversalPromptV2(
        schema_version="2.1.0",
        metadata=prompt.metadata,
        content=prompt.content,
        documents=prompt.documents,
        variables=prompt.variables,
        plugins=None,  # Empty plugins field for v2.1.0
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
            if condition.then:
                # Handle then instructions
                if "instructions" in condition.then:
                    lines.append("Then apply these instructions:")
                    instructions = condition.then["instructions"]
                    if isinstance(instructions, dict):
                        for category, inst_list in instructions.items():
                            lines.append(f"**{category.replace('_', ' ').title()}:**")
                            for inst in inst_list:
                                lines.append(f"- {inst}")
                    else:
                        for inst in instructions:
                            lines.append(f"- {inst}")
                # Handle then examples
                if "examples" in condition.then:
                    lines.append("")
                    lines.append("Examples:")
                    for name, example in condition.then["examples"].items():
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
