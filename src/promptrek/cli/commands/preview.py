"""
Preview command implementation.

Shows what would be generated without creating files.
"""

from pathlib import Path
from typing import Optional

import click

from ...adapters import registry
from ...core.exceptions import AdapterNotFoundError, CLIError
from ...core.models import UniversalPrompt
from ...core.parser import UPFParser
from ...core.validator import UPFValidator


def preview_command(
    ctx: click.Context,
    file: Path,
    editor: str,
    variables: Optional[dict] = None,
) -> None:
    """
    Preview editor-specific prompts without creating files.

    Args:
        ctx: Click context
        file: UPF file path
        editor: Target editor name
        variables: Variable overrides
    """
    verbose = ctx.obj.get("verbose", False)

    # Parse and validate file
    parser = UPFParser()
    try:
        prompt = parser.parse_file(file)
        if verbose:
            click.echo(f"✅ Parsed {file}")
    except Exception as e:
        raise CLIError(f"Failed to parse {file}: {e}")

    validator = UPFValidator()
    result = validator.validate(prompt)
    if result.errors:
        raise CLIError(f"Validation failed: {'; '.join(result.errors)}")

    # Check if editor is in targets (V1 only)
    if (
        isinstance(prompt, UniversalPrompt)
        and prompt.targets
        and editor not in prompt.targets
    ):
        click.echo(
            f"⚠️  Warning: '{editor}' not in targets for this file: {', '.join(prompt.targets)}"
        )

    # Get adapter
    try:
        adapter = registry.get(editor)
    except AdapterNotFoundError:
        raise CLIError(
            f"Editor '{editor}' not available. Use 'promptrek list-editors' to see available editors."
        )

    # Preview header
    click.echo("=" * 80)
    click.echo(f"Preview for: {editor}")
    click.echo(f"Source file: {file}")
    click.echo("=" * 80)
    click.echo()

    # Generate with dry_run mode
    try:
        import sys
        from io import StringIO

        # Capture output
        old_stdout = sys.stdout
        captured_output = StringIO()
        try:
            sys.stdout = captured_output

            # Run generation in dry-run mode
            output_dir = Path.cwd()
            files = adapter.generate(
                prompt, output_dir, dry_run=True, verbose=True, variables=variables
            )
        finally:
            sys.stdout = old_stdout
        # Show captured output
        output_text = captured_output.getvalue()
        if output_text:
            click.echo(output_text)

        # Show file list
        if files:
            click.echo()
            click.echo(f"Would create {len(files)} file(s):")
            for file_path in files:
                click.echo(f"  📄 {file_path}")
        else:
            click.echo("No files would be created.")

    except Exception as e:
        raise CLIError(f"Preview failed: {e}")

    click.echo()
    click.echo("=" * 80)
    click.echo("Preview complete. No files were created.")
    click.echo("Run 'promptrek generate' to create files.")
    click.echo("=" * 80)
