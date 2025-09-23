"""
Validate command implementation.

Handles validation of universal prompt files.
"""

import click
from pathlib import Path

from ...core.parser import UPFParser
from ...core.validator import UPFValidator
from ...core.exceptions import UPFParsingError, UPFValidationError


def validate_command(ctx: click.Context, file: Path, strict: bool) -> None:
    """
    Validate a universal prompt file.
    
    Args:
        ctx: Click context
        file: Path to the UPF file to validate
        strict: Whether to treat warnings as errors
    """
    verbose = ctx.obj.get('verbose', False)
    
    click.echo(f"🔍 Validating {file}...")
    
    # Parse the file
    parser = UPFParser()
    try:
        prompt = parser.parse_file(file)
        if verbose:
            click.echo(f"✅ File parsed successfully")
    except UPFParsingError as e:
        click.echo(f"❌ Parsing failed: {e}", err=True)
        ctx.exit(1)
    
    # Validate the parsed content
    validator = UPFValidator()
    result = validator.validate(prompt)
    
    # Report results
    if result.errors:
        click.echo(f"❌ Validation failed with {len(result.errors)} error(s):", err=True)
        for error in result.errors:
            click.echo(f"  • {error}", err=True)
    
    if result.warnings:
        symbol = "⚠️" if not strict else "❌"
        level = "warning" if not strict else "error"
        click.echo(f"{symbol} Found {len(result.warnings)} {level}(s):")
        for warning in result.warnings:
            click.echo(f"  • {warning}")
    
    # Exit with appropriate code
    if result.errors or (strict and result.warnings):
        ctx.exit(1)
    elif result.warnings:
        click.echo("✅ Validation passed with warnings")
    else:
        click.echo("✅ Validation passed")
    
    # Show summary if verbose
    if verbose:
        _show_summary(prompt)


def _show_summary(prompt) -> None:
    """Show a summary of the prompt configuration."""
    click.echo("\n📋 Summary:")
    click.echo(f"  Title: {prompt.metadata.title}")
    click.echo(f"  Version: {prompt.metadata.version}")
    click.echo(f"  Targets: {', '.join(prompt.targets)}")
    
    if prompt.context and prompt.context.technologies:
        click.echo(f"  Technologies: {', '.join(prompt.context.technologies)}")
    
    instruction_count = 0
    if prompt.instructions:
        for field in ['general', 'code_style', 'architecture', 'testing', 'security', 'performance']:
            field_value = getattr(prompt.instructions, field, None)
            if field_value:
                instruction_count += len(field_value)
    
    click.echo(f"  Instructions: {instruction_count} total")
    
    if prompt.examples:
        click.echo(f"  Examples: {len(prompt.examples)}")
    
    if prompt.variables:
        click.echo(f"  Variables: {len(prompt.variables)}")