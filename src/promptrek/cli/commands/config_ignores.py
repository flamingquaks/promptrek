"""
config-ignores command implementation.

Handles configuration of .gitignore for editor-specific files.
"""

from pathlib import Path
from typing import Optional

import click

from ...core.exceptions import CLIError
from ...core.parser import UPFParser
from ...utils.gitignore import configure_gitignore


def config_ignores_command(
    ctx: click.Context,
    config_file: Optional[Path],
    remove_cached: bool,
    dry_run: bool,
) -> None:
    """
    Configure .gitignore to exclude editor-specific files.

    This command:
    1. Adds editor file patterns to .gitignore
    2. Optionally runs git rm --cached on existing committed files
    3. Respects the ignore_editor_files setting in the config file

    Args:
        ctx: Click context
        config_file: Path to PrompTrek config file (auto-detects if None)
        remove_cached: Whether to remove cached files from git
        dry_run: Show what would be done without making changes
    """
    # Auto-detect config file if not provided
    if config_file is None:
        config_file = _find_config_file()
        if config_file is None:
            raise CLIError(
                "No PrompTrek config file found. "
                "Please specify with --config or run from a directory with a .promptrek.yaml file."
            )

    if not config_file.exists():
        raise CLIError(f"Config file not found: {config_file}")

    # Parse config file to check ignore_editor_files setting
    parser = UPFParser()
    try:
        prompt = parser.parse_file(config_file)
    except Exception as e:
        raise CLIError(f"Failed to parse config file: {e}")

    # Check if ignore_editor_files is explicitly disabled
    ignore_editor_files = getattr(prompt, "ignore_editor_files", None)
    if ignore_editor_files is False:
        click.echo(
            "⚠️  ignore_editor_files is set to False in config. "
            "Set it to True if you want to automatically exclude editor files."
        )
        if not click.confirm("Continue anyway?"):
            return

    project_dir = config_file.parent

    if dry_run:
        click.echo("🔍 Dry run mode - would perform the following actions:")
        click.echo(f"  • Add editor file patterns to {project_dir / '.gitignore'}")
        if remove_cached:
            click.echo("  • Remove matching files from git cache (git rm --cached)")
        return

    # Configure .gitignore
    click.echo(f"📝 Configuring .gitignore in {project_dir}...")
    results = configure_gitignore(
        project_dir, add_editor_files=True, remove_cached=remove_cached
    )

    if results["patterns_added"] == 0:
        click.echo("✅ All patterns already present in .gitignore")
    else:
        click.echo(f"✅ Added {results['patterns_added']} pattern(s) to .gitignore")

    if remove_cached:
        if results["files_removed"]:
            click.echo(
                f"🗑️  Removed {len(results['files_removed'])} file(s) from git cache"
            )
            click.echo(
                "💡 Remember to commit these changes to complete the un-tracking"
            )
        else:
            click.echo("ℹ️  No matching files found in git cache")


def _find_config_file() -> Optional[Path]:
    """
    Auto-detect PrompTrek config file in current directory.

    Returns:
        Path to config file if found, None otherwise
    """
    current_dir = Path.cwd()

    # Try common names
    candidates = [
        "project.promptrek.yaml",
        ".promptrek.yaml",
        "promptrek.yaml",
    ]

    for name in candidates:
        config_path = current_dir / name
        if config_path.exists():
            return config_path

    # Try finding any .promptrek.yaml file
    for file in current_dir.glob("*.promptrek.yaml"):
        return file

    return None
