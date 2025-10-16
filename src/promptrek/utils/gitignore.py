"""
Utility functions for managing .gitignore file.

Provides functionality to add editor-specific file patterns to .gitignore
and to run git commands to untrack previously committed files.
"""

import subprocess
from pathlib import Path
from typing import List, Optional, Set

import click


def get_editor_file_patterns() -> List[str]:
    """
    Get list of all editor file patterns that should be ignored.

    Returns:
        List of file patterns for editor-specific files
    """
    return [
        # GitHub Copilot
        ".github/copilot-instructions.md",
        ".github/instructions/*.instructions.md",
        ".github/prompts/*.prompt.md",
        # Cursor
        ".cursor/rules/*.mdc",
        ".cursor/rules/index.mdc",
        "AGENTS.md",
        # Continue
        ".continue/rules/*.md",
        # Windsurf
        ".windsurf/rules/*.md",
        # Cline
        ".clinerules",
        ".clinerules/*.md",
        # Claude
        ".claude/CLAUDE.md",
        ".claude-context.md",
        # Amazon Q
        ".amazonq/rules/*.md",
        ".amazonq/cli-agents/*.json",
        # JetBrains
        ".assistant/rules/*.md",
        # Kiro
        ".kiro/steering/*.md",
        # Tabnine
        ".tabnine_commands",
        # MCP configs
        ".vscode/mcp.json",
    ]


def read_gitignore(gitignore_path: Path) -> Set[str]:
    """
    Read and parse .gitignore file, returning set of patterns.

    Args:
        gitignore_path: Path to .gitignore file

    Returns:
        Set of patterns found in .gitignore
    """
    if not gitignore_path.exists():
        return set()

    patterns = set()
    try:
        with open(gitignore_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if line and not line.startswith("#"):
                    patterns.add(line)
    except Exception:
        pass

    return patterns


def add_patterns_to_gitignore(
    gitignore_path: Path, patterns: List[str], comment: Optional[str] = None
) -> int:
    """
    Add patterns to .gitignore file if they don't already exist.

    Args:
        gitignore_path: Path to .gitignore file
        patterns: List of patterns to add
        comment: Optional comment to add before patterns

    Returns:
        Number of patterns added
    """
    existing_patterns = read_gitignore(gitignore_path)

    # Filter out patterns that already exist
    new_patterns = [p for p in patterns if p not in existing_patterns]

    if not new_patterns:
        return 0

    # Prepare content to add
    lines_to_add = []

    # Add comment if provided
    if comment:
        lines_to_add.append(f"\n# {comment}\n")
    elif not gitignore_path.exists():
        lines_to_add.append("")

    # Add new patterns
    for pattern in new_patterns:
        lines_to_add.append(f"{pattern}\n")

    # Write to file
    try:
        mode = "a" if gitignore_path.exists() else "w"
        with open(gitignore_path, mode, encoding="utf-8") as f:
            # Ensure existing file ends with newline
            if mode == "a" and gitignore_path.stat().st_size > 0:
                # Read last char to check if we need a newline
                with open(gitignore_path, "rb") as check_f:
                    check_f.seek(-1, 2)
                    last_char = check_f.read(1)
                    if last_char != b"\n":
                        f.write("\n")

            # Write new content
            for line in lines_to_add:
                f.write(line)

        return len(new_patterns)
    except Exception as e:
        click.echo(f"⚠️  Could not update .gitignore: {e}", err=True)
        return 0


def remove_cached_files(patterns: List[str], project_dir: Path) -> List[str]:
    """
    Remove files matching patterns from git cache using git rm --cached.

    Args:
        patterns: List of file patterns to remove from cache
        project_dir: Project directory (git repository root)

    Returns:
        List of files that were successfully removed from cache
    """
    removed_files = []

    # Check if we're in a git repository
    git_dir = project_dir / ".git"
    if not git_dir.exists():
        click.echo("⚠️  Not a git repository - skipping git rm --cached", err=True)
        return removed_files

    for pattern in patterns:
        try:
            # Use git ls-files to find matching files that are tracked
            result = subprocess.run(
                ["git", "ls-files", pattern],
                cwd=project_dir,
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode == 0 and result.stdout.strip():
                # Files exist and are tracked
                files = result.stdout.strip().split("\n")

                # Remove them from git cache
                for file in files:
                    rm_result = subprocess.run(
                        ["git", "rm", "--cached", file],
                        cwd=project_dir,
                        capture_output=True,
                        text=True,
                        check=False,
                    )

                    if rm_result.returncode == 0:
                        removed_files.append(file)

        except Exception:
            # Silently continue if git command fails
            pass

    return removed_files


def configure_gitignore(
    project_dir: Path,
    add_editor_files: bool = True,
    remove_cached: bool = False,
    custom_patterns: Optional[List[str]] = None,
) -> dict:
    """
    Configure .gitignore with editor file patterns.

    Args:
        project_dir: Project directory
        add_editor_files: Whether to add editor file patterns
        remove_cached: Whether to remove cached files from git
        custom_patterns: Optional custom patterns to add

    Returns:
        Dictionary with results including patterns_added and files_removed
    """
    gitignore_path = project_dir / ".gitignore"
    results = {"patterns_added": 0, "files_removed": []}

    patterns_to_add = []

    # Add editor file patterns if requested
    if add_editor_files:
        patterns_to_add.extend(get_editor_file_patterns())

    # Add custom patterns
    if custom_patterns:
        patterns_to_add.extend(custom_patterns)

    # Add patterns to .gitignore
    if patterns_to_add:
        comment = "PrompTrek editor-specific files (generated, not committed)"
        patterns_added = add_patterns_to_gitignore(
            gitignore_path, patterns_to_add, comment
        )
        results["patterns_added"] = patterns_added

        if patterns_added > 0:
            click.echo(f"📝 Added {patterns_added} pattern(s) to .gitignore")

    # Remove cached files if requested
    if remove_cached and patterns_to_add:
        removed_files = remove_cached_files(patterns_to_add, project_dir)
        results["files_removed"] = removed_files

        if removed_files:
            click.echo(
                f"🗑️  Removed {len(removed_files)} file(s) from git cache:\n   "
                + "\n   ".join(removed_files)
            )
            click.echo(
                "💡 Remember to commit these changes to complete the un-tracking"
            )

    return results
