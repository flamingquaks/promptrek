"""
Generate command implementation.

Handles generation of editor-specific prompts from universal prompt files.
"""

import click
from pathlib import Path
from typing import Optional

from ...core.parser import UPFParser
from ...core.validator import UPFValidator
from ...core.exceptions import UPFParsingError, CLIError, AdapterNotFoundError


def generate_command(
    ctx: click.Context, 
    file: Path, 
    editor: Optional[str], 
    output: Optional[Path], 
    dry_run: bool, 
    all_editors: bool
) -> None:
    """
    Generate editor-specific prompts from universal prompt file.
    
    Args:
        ctx: Click context
        file: Path to the UPF file
        editor: Target editor name
        output: Output directory path
        dry_run: Whether to show what would be generated without creating files
        all_editors: Whether to generate for all target editors
    """
    verbose = ctx.obj.get('verbose', False)
    
    # Parse the file
    parser = UPFParser()
    try:
        prompt = parser.parse_file(file)
        if verbose:
            click.echo(f"✅ Parsed {file}")
    except UPFParsingError as e:
        raise CLIError(f"Failed to parse {file}: {e}")
    
    # Validate first
    validator = UPFValidator()
    result = validator.validate(prompt)
    if result.errors:
        raise CLIError(f"Validation failed: {'; '.join(result.errors)}")
    
    # Determine target editors
    if all_editors:
        target_editors = prompt.targets
    elif editor:
        if editor not in prompt.targets:
            raise CLIError(f"Editor '{editor}' not in targets: {', '.join(prompt.targets)}")
        target_editors = [editor]
    else:
        raise CLIError("Must specify either --editor or --all")
    
    # Set default output directory
    if not output:
        output = Path.cwd()
    
    if dry_run:
        click.echo("🔍 Dry run mode - showing what would be generated:")
    
    # Generate for each target editor
    for target_editor in target_editors:
        try:
            _generate_for_editor(prompt, target_editor, output, dry_run, verbose)
        except AdapterNotFoundError:
            click.echo(f"⚠️ Editor '{target_editor}' not yet implemented - skipping")
        except Exception as e:
            if verbose:
                raise
            raise CLIError(f"Failed to generate for {target_editor}: {e}")


def _generate_for_editor(prompt, editor: str, output_dir: Path, dry_run: bool, verbose: bool) -> None:
    """Generate prompts for a specific editor."""
    
    # For now, implement basic Copilot support as proof of concept
    if editor == 'copilot':
        _generate_copilot(prompt, output_dir, dry_run, verbose)
    elif editor == 'cursor':
        _generate_cursor(prompt, output_dir, dry_run, verbose)
    elif editor == 'continue':
        _generate_continue(prompt, output_dir, dry_run, verbose)
    else:
        raise AdapterNotFoundError(f"Editor '{editor}' adapter not implemented yet")


def _generate_copilot(prompt, output_dir: Path, dry_run: bool, verbose: bool) -> None:
    """Generate GitHub Copilot instructions."""
    
    # Create content
    content = _build_copilot_content(prompt)
    
    # Determine output path
    github_dir = output_dir / '.github'
    output_file = github_dir / 'copilot-instructions.md'
    
    if dry_run:
        click.echo(f"  📁 Would create: {output_file}")
        if verbose:
            click.echo("  📄 Content preview:")
            preview = content[:200] + "..." if len(content) > 200 else content
            click.echo(f"    {preview}")
    else:
        # Create directory and file
        github_dir.mkdir(exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        click.echo(f"✅ Generated: {output_file}")


def _generate_cursor(prompt, output_dir: Path, dry_run: bool, verbose: bool) -> None:
    """Generate Cursor rules."""
    
    # Create content
    content = _build_cursor_content(prompt)
    
    # Determine output path
    output_file = output_dir / '.cursorrules'
    
    if dry_run:
        click.echo(f"  📁 Would create: {output_file}")
        if verbose:
            click.echo("  📄 Content preview:")
            preview = content[:200] + "..." if len(content) > 200 else content
            click.echo(f"    {preview}")
    else:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        click.echo(f"✅ Generated: {output_file}")


def _generate_continue(prompt, output_dir: Path, dry_run: bool, verbose: bool) -> None:
    """Generate Continue configuration."""
    
    # Create content
    content = _build_continue_content(prompt)
    
    # Determine output path
    continue_dir = output_dir / '.continue'
    output_file = continue_dir / 'config.json'
    
    if dry_run:
        click.echo(f"  📁 Would create: {output_file}")
        if verbose:
            click.echo("  📄 Content preview:")
            preview = content[:200] + "..." if len(content) > 200 else content
            click.echo(f"    {preview}")
    else:
        # Create directory and file
        continue_dir.mkdir(exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        click.echo(f"✅ Generated: {output_file}")


def _build_copilot_content(prompt) -> str:
    """Build GitHub Copilot instructions content."""
    lines = []
    
    # Header
    lines.append(f"# {prompt.metadata.title}")
    lines.append("")
    lines.append(prompt.metadata.description)
    lines.append("")
    
    # Project Information
    if prompt.context:
        lines.append("## Project Information")
        if prompt.context.project_type:
            lines.append(f"- Type: {prompt.context.project_type}")
        if prompt.context.technologies:
            lines.append(f"- Technologies: {', '.join(prompt.context.technologies)}")
        if prompt.context.description:
            lines.append(f"- Description: {prompt.context.description}")
        lines.append("")
    
    # Instructions
    if prompt.instructions:
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
        
        if prompt.instructions.testing:
            lines.append("## Testing Guidelines")
            for guideline in prompt.instructions.testing:
                lines.append(f"- {guideline}")
            lines.append("")
    
    # Examples
    if prompt.examples:
        lines.append("## Examples")
        for name, example in prompt.examples.items():
            lines.append(f"### {name.title()}")
            lines.append(example)
            lines.append("")
    
    return "\n".join(lines)


def _build_cursor_content(prompt) -> str:
    """Build Cursor rules content."""
    lines = []
    
    lines.append(f"# {prompt.metadata.title}")
    lines.append("")
    lines.append(prompt.metadata.description)
    lines.append("")
    
    # Instructions
    if prompt.instructions:
        lines.append("## Instructions")
        
        for category, instructions in [
            ("General", prompt.instructions.general),
            ("Code Style", prompt.instructions.code_style),
            ("Testing", prompt.instructions.testing),
        ]:
            if instructions:
                lines.append(f"### {category}")
                for instruction in instructions:
                    lines.append(f"- {instruction}")
                lines.append("")
    
    return "\n".join(lines)


def _build_continue_content(prompt) -> str:
    """Build Continue configuration content."""
    import json
    
    config = {
        "models": [],
        "systemMessage": f"{prompt.metadata.title}\n\n{prompt.metadata.description}",
        "completionOptions": {},
        "allowAnonymousTelemetry": False
    }
    
    # Add instructions to system message
    if prompt.instructions and prompt.instructions.general:
        config["systemMessage"] += "\n\nGeneral Instructions:\n"
        for instruction in prompt.instructions.general:
            config["systemMessage"] += f"- {instruction}\n"
    
    return json.dumps(config, indent=2)