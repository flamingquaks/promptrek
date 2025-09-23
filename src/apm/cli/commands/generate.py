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
from ...adapters import registry


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
    """Generate prompts for a specific editor using the adapter system."""
    
    try:
        adapter = registry.get(editor)
        adapter.generate(prompt, output_dir, dry_run, verbose)
    except AdapterNotFoundError:
        raise AdapterNotFoundError(f"Editor '{editor}' adapter not implemented yet")

