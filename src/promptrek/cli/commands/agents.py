"""
Agents command implementation.

Handles generation of persistent agent instruction files that tell autonomous agents
to use PrompTrek and follow the generated instructions.
"""

import os
from pathlib import Path
from typing import Optional, Union

import click

from ...core.exceptions import CLIError, UPFParsingError
from ...core.models import UniversalPrompt, UniversalPromptV2
from ...core.parser import UPFParser


def agents_command(
    ctx: click.Context,
    prompt_file: Optional[Path],
    output_dir: Optional[Path],
    dry_run: bool,
    force: bool,
) -> None:
    """
    Generate persistent agent instruction files.

    Creates agent instruction files that persist in the repository and tell
    autonomous agents (like GitHub Copilot Agent, Claude, etc.) to run
    promptrek and follow the generated instructions.

    Args:
        ctx: Click context
        prompt_file: Path to the universal prompt file
        output_dir: Output directory for agent files
        dry_run: Whether to show what would be generated without creating files
        force: Whether to overwrite existing files
    """
    verbose = ctx.obj.get("verbose", False)

    # Find prompt file if not specified
    if not prompt_file:
        # Look for .promptrek.yaml files in current directory
        potential_files = list(Path.cwd().glob("*.promptrek.yaml"))
        if not potential_files:
            raise CLIError(
                "No prompt file specified and no .promptrek.yaml files found "
                "in current directory. Use 'promptrek init' to create one."
            )
        prompt_file = potential_files[0]
        if verbose:
            click.echo(f"Auto-discovered prompt file: {prompt_file}")

    # Convert to absolute path and check existence
    if not prompt_file.is_absolute():
        prompt_file = Path.cwd() / prompt_file

    if not prompt_file.exists():
        raise CLIError(f"Prompt file not found: {prompt_file}")

    # Resolve output directory
    if output_dir is None:
        output_dir = Path.cwd()
    elif not output_dir.is_absolute():
        output_dir = Path.cwd() / output_dir

    # Parse the prompt file
    try:
        parser = UPFParser()
        prompt = parser.parse_file(prompt_file)
        if verbose:
            click.echo(f"Parsed prompt file: {prompt_file}")
    except UPFParsingError as e:
        raise CLIError(f"Failed to parse prompt file: {e}")

    # Generate agent instruction files
    created_files = _generate_agent_files(prompt, output_dir, dry_run, verbose, force)

    # Summary
    if dry_run:
        click.echo(f"\n📋 Would create {len(created_files)} agent instruction files")
    else:
        click.echo(f"\n✅ Created {len(created_files)} agent instruction files")
        click.echo(
            "\n💡 These files will help autonomous agents understand your project:"
        )
        for file_path in created_files:
            click.echo(f"   • {file_path}")

        click.echo(
            "\n🚀 Next steps:"
            "\n   1. Commit these files to your repository"
            "\n   2. Autonomous agents will now use PrompTrek when working "
            "on your project"
            "\n   3. Run 'promptrek generate --all' to update editor-specific "
            "configs"
        )


def _generate_agent_files(
    prompt: Union[UniversalPrompt, UniversalPromptV2],
    output_dir: Path,
    dry_run: bool,
    verbose: bool,
    force: bool,
) -> list[Path]:
    """Generate persistent agent instruction files."""
    created_files = []

    # Generate general AGENTS.md file
    agents_file = output_dir / "AGENTS.md"
    agents_content = _build_agents_content(prompt)

    if _should_create_file(agents_file, force, dry_run):
        if dry_run:
            click.echo(f"  📁 Would create: {agents_file}")
            if verbose:
                preview = (
                    agents_content[:200] + "..."
                    if len(agents_content) > 200
                    else agents_content
                )
                click.echo(f"    {preview}")
        else:
            output_dir.mkdir(parents=True, exist_ok=True)
            with open(agents_file, "w", encoding="utf-8") as f:
                f.write(agents_content)
            click.echo(f"✅ Generated: {agents_file}")
        created_files.append(agents_file)

    # Generate .github/copilot-instructions.md for GitHub Copilot Agent
    github_dir = output_dir / ".github"
    copilot_file = github_dir / "copilot-instructions.md"
    copilot_content = _build_copilot_agent_content(prompt)

    if _should_create_file(copilot_file, force, dry_run):
        if dry_run:
            click.echo(f"  📁 Would create: {copilot_file}")
            if verbose:
                preview = (
                    copilot_content[:200] + "..."
                    if len(copilot_content) > 200
                    else copilot_content
                )
                click.echo(f"    {preview}")
        else:
            github_dir.mkdir(parents=True, exist_ok=True)
            with open(copilot_file, "w", encoding="utf-8") as f:
                f.write(copilot_content)
            click.echo(f"✅ Generated: {copilot_file}")
        created_files.append(copilot_file)

    # Generate .claude/CLAUDE.md for Claude agents
    claude_dir = output_dir / ".claude"
    claude_file = claude_dir / "CLAUDE.md"
    claude_content = _build_claude_agent_content(prompt)

    if _should_create_file(claude_file, force, dry_run):
        if dry_run:
            click.echo(f"  📁 Would create: {claude_file}")
            if verbose:
                preview = (
                    claude_content[:200] + "..."
                    if len(claude_content) > 200
                    else claude_content
                )
                click.echo(f"    {preview}")
        else:
            claude_dir.mkdir(parents=True, exist_ok=True)
            with open(claude_file, "w", encoding="utf-8") as f:
                f.write(claude_content)
            click.echo(f"✅ Generated: {claude_file}")
        created_files.append(claude_file)

    return created_files


def _should_create_file(file_path: Path, force: bool, dry_run: bool) -> bool:
    """Check if a file should be created based on existence and force flag."""
    if dry_run:
        return True

    if not file_path.exists():
        return True

    if force:
        return True

    # File exists and no force flag
    click.echo(f"⚠️  File already exists: {file_path} (use --force to overwrite)")
    return False


def _build_agents_content(prompt: Union[UniversalPrompt, UniversalPromptV2]) -> str:
    """Build content for the general AGENTS.md file."""
    lines = []

    lines.append(f"# {prompt.metadata.title} - Agent Instructions")
    lines.append("")
    lines.append(prompt.metadata.description)
    lines.append("")

    lines.append("## Important: Use PrompTrek for Consistent Configuration")
    lines.append("")
    lines.append(
        "This project uses **PrompTrek** for universal AI assistant configuration."
    )
    lines.append("Before making changes, please:")
    lines.append("")
    lines.append("1. **Run PrompTrek to get the latest instructions:**")
    lines.append("   ```bash")
    lines.append("   promptrek generate --all")
    lines.append("   ```")
    lines.append("")
    lines.append("2. **Follow the generated editor-specific instructions** in:")
    lines.append("   - `.github/copilot-instructions.md` (GitHub Copilot)")
    lines.append("   - `.cursor/rules/` (Cursor)")
    lines.append("   - `.continue/` (Continue)")
    lines.append("   - Other generated configuration files")
    lines.append("")
    lines.append("3. **If instructions seem outdated, regenerate them:**")
    lines.append("   ```bash")
    lines.append("   promptrek validate *.promptrek.yaml")
    lines.append("   promptrek generate --all --force")
    lines.append("   ```")
    lines.append("")

    # Project Context (V1 only)
    if isinstance(prompt, UniversalPrompt) and prompt.context:
        lines.append("## Project Context")
        if prompt.context.project_type:
            lines.append(f"**Project Type:** {prompt.context.project_type}")
        if prompt.context.technologies:
            lines.append(f"**Technologies:** {', '.join(prompt.context.technologies)}")
        if prompt.context.description:
            lines.append("")
            lines.append("**Project Description:**")
            lines.append(prompt.context.description)
        lines.append("")

    # High-level instructions (V1 only)
    if isinstance(prompt, UniversalPrompt) and prompt.instructions:
        lines.append("## High-Level Guidelines")
        lines.append("*(For detailed instructions, use PrompTrek as described above)*")
        lines.append("")

        if prompt.instructions.general:
            lines.append("### General Instructions")
            for instruction in prompt.instructions.general[:5]:  # Limit to first 5
                lines.append(f"- {instruction}")
            if len(prompt.instructions.general) > 5:
                count = len(prompt.instructions.general) - 5
                lines.append(f"- *...and {count} more (see generated files)*")
            lines.append("")

    lines.append("---")
    lines.append("*This file was generated by PrompTrek. Do not edit manually.*")
    lines.append(
        "*To update, modify the .promptrek.yaml file and run 'promptrek agents'*"
    )

    return "\n".join(lines)


def _build_copilot_agent_content(
    prompt: Union[UniversalPrompt, UniversalPromptV2],
) -> str:
    """Build content for GitHub Copilot Agent (.github/copilot-instructions.md)."""
    lines = []

    lines.append(f"# {prompt.metadata.title}")
    lines.append("")
    lines.append(prompt.metadata.description)
    lines.append("")

    lines.append("## PrompTrek Integration")
    lines.append("")
    lines.append(
        "This project uses PrompTrek for configuration management. "
        "Before making changes:"
    )
    lines.append("")
    lines.append("```bash")
    lines.append("# Generate the latest configuration")
    lines.append("promptrek generate --editor copilot")
    lines.append("```")
    lines.append("")

    # Project Information (V1 only)
    if isinstance(prompt, UniversalPrompt) and prompt.context:
        lines.append("## Project Information")
        if prompt.context.project_type:
            lines.append(f"- Type: {prompt.context.project_type}")
        if prompt.context.technologies:
            lines.append(f"- Technologies: {', '.join(prompt.context.technologies)}")
        if prompt.context.description:
            lines.append(f"- Description: {prompt.context.description}")
        lines.append("")

    # Instructions (V1 only)
    if isinstance(prompt, UniversalPrompt) and prompt.instructions:
        if prompt.instructions.general:
            lines.append("## General Instructions")
            for instruction in prompt.instructions.general:
                lines.append(f"- {instruction}")
            lines.append("")

        if prompt.instructions.code_style:
            lines.append("## Code Style Guidelines")
            for guideline in prompt.instructions.code_style:
                lines.append(f"- {guideline}")
            lines.append("")

    lines.append("---")
    lines.append("*Generated by PrompTrek. Run 'promptrek agents' to update.*")

    return "\n".join(lines)


def _build_claude_agent_content(
    prompt: Union[UniversalPrompt, UniversalPromptV2],
) -> str:
    """Build content for Claude agents (.claude/CLAUDE.md)."""
    lines = []

    lines.append(f"# {prompt.metadata.title} - Claude Context")
    lines.append("")
    lines.append(prompt.metadata.description)
    lines.append("")

    lines.append("## PrompTrek Configuration System")
    lines.append("")
    lines.append("This project uses PrompTrek to manage AI assistant configurations.")
    lines.append("To get the most up-to-date and complete instructions:")
    lines.append("")
    lines.append("```bash")
    lines.append("promptrek generate --editor claude")
    lines.append("```")
    lines.append("")
    lines.append(
        "This will generate detailed configuration files optimized for your work."
    )
    lines.append("")

    # Project Context (V1 only)
    if isinstance(prompt, UniversalPrompt) and prompt.context:
        lines.append("## Project Overview")
        if prompt.context.project_type:
            lines.append(f"**Type:** {prompt.context.project_type}")
        if prompt.context.technologies:
            lines.append(f"**Stack:** {', '.join(prompt.context.technologies)}")
        if prompt.context.description:
            lines.append("")
            lines.append("**Description:**")
            lines.append(prompt.context.description)
        lines.append("")

    # Key Instructions (V1 only)
    if (
        isinstance(prompt, UniversalPrompt)
        and prompt.instructions
        and prompt.instructions.general
    ):
        lines.append("## Key Guidelines")
        for instruction in prompt.instructions.general[:3]:  # Top 3 most important
            lines.append(f"- {instruction}")
        if len(prompt.instructions.general) > 3:
            lines.append("- *(Run PrompTrek for complete instructions)*")
        lines.append("")

    lines.append("## Working with This Project")
    lines.append("")
    lines.append("1. **Always run PrompTrek first** to get current instructions")
    lines.append(
        "2. **Check generated files** in .claude/ directory after running PrompTrek"
    )
    lines.append(
        "3. **Ask about PrompTrek** if you need to understand the configuration system"
    )
    lines.append("")

    lines.append("---")
    lines.append("*This context file was created by PrompTrek agent command.*")

    return "\n".join(lines)
