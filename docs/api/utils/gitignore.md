# Gitignore Utility

The gitignore utility module provides functions for managing `.gitignore` files and handling editor-specific file patterns.

## Overview

PrompTrek generates editor-specific configuration files that should not be committed to version control. The gitignore utility helps manage this by:

- **Pattern management**: Add editor file patterns to `.gitignore`
- **Deduplication**: Avoid adding patterns that already exist
- **Git cache cleanup**: Remove previously committed files from git tracking
- **Automated workflow**: Integrate gitignore updates into generation process
- **Editor file patterns**: Pre-defined patterns for all supported editors

The module provides simple functions that can be used standalone or integrated into adapters and CLI commands.

## API Reference

::: promptrek.utils.gitignore
    options:
      show_root_heading: true
      show_source: true
      members_order: source
      docstring_style: google
      show_if_no_docstring: false

## Usage Examples

### Getting Editor File Patterns

Get all editor file patterns that should be ignored:

```python
from promptrek.utils.gitignore import get_editor_file_patterns

patterns = get_editor_file_patterns()

print(f"Total patterns: {len(patterns)}")
print("\nEditor file patterns:")
for pattern in patterns:
    print(f"  {pattern}")

# Example output:
#   .github/copilot-instructions.md
#   .cursor/rules/*.mdc
#   .continue/config.yaml
#   .claude/CLAUDE.md
#   .amazonq/rules/*.md
#   ... etc
```

### Adding Patterns to Gitignore

Add patterns to `.gitignore` file:

```python
from pathlib import Path
from promptrek.utils.gitignore import add_patterns_to_gitignore

gitignore_path = Path(".gitignore")

patterns = [
    ".cursor/rules/*.mdc",
    ".claude/CLAUDE.md",
    ".continue/config.yaml"
]

# Add patterns with comment
added = add_patterns_to_gitignore(
    gitignore_path,
    patterns,
    comment="PrompTrek editor-specific files (generated, not committed)"
)

print(f"Added {added} new patterns to .gitignore")
```

### Reading Existing Gitignore

Read and parse `.gitignore` file:

```python
from pathlib import Path
from promptrek.utils.gitignore import read_gitignore

gitignore_path = Path(".gitignore")

# Read existing patterns
patterns = read_gitignore(gitignore_path)

print(f"Existing patterns: {len(patterns)}")
for pattern in sorted(patterns):
    print(f"  {pattern}")

# Returns empty set if file doesn't exist
if not gitignore_path.exists():
    print("No .gitignore file found")
```

### Removing Cached Files from Git

Remove files from git cache (untrack without deleting):

```python
from pathlib import Path
from promptrek.utils.gitignore import remove_cached_files

patterns = [
    ".cursor/rules/*.mdc",
    ".claude/CLAUDE.md"
]

# Remove from git tracking
removed = remove_cached_files(patterns, project_dir=Path("."))

if removed:
    print(f"Removed {len(removed)} files from git cache:")
    for file in removed:
        print(f"  {file}")
    print("\nRemember to commit these changes!")
else:
    print("No tracked files match the patterns")
```

### Complete Gitignore Configuration

Configure `.gitignore` with all options:

```python
from pathlib import Path
from promptrek.utils.gitignore import configure_gitignore

results = configure_gitignore(
    project_dir=Path("."),
    add_editor_files=True,      # Add editor file patterns
    remove_cached=True,          # Remove cached files from git
    custom_patterns=[            # Additional custom patterns
        ".promptrek/user-config.promptrek.yaml",
        ".promptrek/last-generation.yaml"
    ]
)

print(f"Patterns added: {results['patterns_added']}")
print(f"Files removed from cache: {len(results['files_removed'])}")

if results['files_removed']:
    print("\nFiles removed:")
    for file in results['files_removed']:
        print(f"  {file}")
```

### Checking for Existing Patterns

Avoid adding duplicate patterns:

```python
from pathlib import Path
from promptrek.utils.gitignore import (
    read_gitignore,
    add_patterns_to_gitignore
)

gitignore_path = Path(".gitignore")

# Read existing
existing = read_gitignore(gitignore_path)

# Patterns to add
new_patterns = [
    ".cursor/rules/*.mdc",
    ".claude/CLAUDE.md",
    "*.log"  # Custom pattern
]

# Filter out duplicates
to_add = [p for p in new_patterns if p not in existing]

if to_add:
    added = add_patterns_to_gitignore(gitignore_path, to_add)
    print(f"Added {added} new patterns")
else:
    print("All patterns already in .gitignore")
```

### Creating Gitignore if Missing

Create `.gitignore` file if it doesn't exist:

```python
from pathlib import Path
from promptrek.utils.gitignore import add_patterns_to_gitignore

gitignore_path = Path(".gitignore")

# Function creates file if it doesn't exist
patterns = [
    "*.pyc",
    "__pycache__/",
    ".env",
    ".cursor/rules/*.mdc"
]

added = add_patterns_to_gitignore(
    gitignore_path,
    patterns,
    comment="Project-specific ignores"
)

print(f"Created .gitignore with {added} patterns")
```

### Working with Git Status

Check which files are tracked before removing:

```python
from pathlib import Path
import subprocess

def check_tracked_files(patterns):
    """Check which files matching patterns are tracked."""
    tracked = []

    for pattern in patterns:
        result = subprocess.run(
            ["git", "ls-files", pattern],
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode == 0 and result.stdout.strip():
            files = result.stdout.strip().split("\n")
            tracked.extend(files)

    return tracked

patterns = [
    ".cursor/rules/*.mdc",
    ".claude/CLAUDE.md"
]

tracked = check_tracked_files(patterns)

if tracked:
    print("These files are currently tracked:")
    for file in tracked:
        print(f"  {file}")
    print("\nUse remove_cached_files() to untrack them")
else:
    print("No tracked files match the patterns")
```

### Adding Custom Editor Patterns

Add patterns for custom or unlisted editors:

```python
from pathlib import Path
from promptrek.utils.gitignore import configure_gitignore

# Add standard patterns plus custom ones
results = configure_gitignore(
    project_dir=Path("."),
    add_editor_files=True,       # Standard editor patterns
    remove_cached=False,
    custom_patterns=[            # Custom editor patterns
        ".myeditor/config.json",
        ".myeditor/rules/*.md",
        ".myeditor/cache/",
        ".another-editor/settings.yaml"
    ]
)

print(f"Total patterns added: {results['patterns_added']}")
```

### Organizing Gitignore Sections

Add patterns with descriptive comments:

```python
from pathlib import Path
from promptrek.utils.gitignore import add_patterns_to_gitignore

gitignore_path = Path(".gitignore")

# Add different sections
sections = [
    {
        "comment": "Python",
        "patterns": ["*.pyc", "__pycache__/", "*.pyo", "*.egg-info/"]
    },
    {
        "comment": "Node.js",
        "patterns": ["node_modules/", "npm-debug.log", "package-lock.json"]
    },
    {
        "comment": "PrompTrek editor files",
        "patterns": [
            ".cursor/rules/*.mdc",
            ".claude/CLAUDE.md",
            ".continue/config.yaml"
        ]
    }
]

for section in sections:
    added = add_patterns_to_gitignore(
        gitignore_path,
        section["patterns"],
        comment=section["comment"]
    )
    print(f"{section['comment']}: {added} patterns added")
```

### Handling Git Errors

Handle cases where git is not available:

```python
from pathlib import Path
from promptrek.utils.gitignore import remove_cached_files

patterns = [".cursor/rules/*.mdc"]

# Check if in git repository first
git_dir = Path(".git")
if not git_dir.exists():
    print("Not a git repository - skipping cache removal")
else:
    removed = remove_cached_files(patterns, Path("."))
    print(f"Removed {len(removed)} files from cache")
```

### Complete Workflow Example

Full workflow for managing editor files:

```python
from pathlib import Path
from promptrek.utils.gitignore import (
    get_editor_file_patterns,
    read_gitignore,
    add_patterns_to_gitignore,
    remove_cached_files,
    configure_gitignore
)

project_dir = Path(".")
gitignore_path = project_dir / ".gitignore"

print("Step 1: Check current .gitignore")
existing = read_gitignore(gitignore_path)
print(f"  Existing patterns: {len(existing)}")

print("\nStep 2: Get editor file patterns")
editor_patterns = get_editor_file_patterns()
print(f"  Editor patterns: {len(editor_patterns)}")

print("\nStep 3: Add to .gitignore")
added = add_patterns_to_gitignore(
    gitignore_path,
    editor_patterns,
    comment="PrompTrek editor-specific files"
)
print(f"  Added: {added} new patterns")

print("\nStep 4: Remove cached files")
removed = remove_cached_files(editor_patterns, project_dir)
print(f"  Removed from cache: {len(removed)} files")

if removed:
    print("\n⚠️  Files removed from git cache:")
    for file in removed:
        print(f"    - {file}")
    print("\n  Run 'git commit' to complete the un-tracking")

print("\n✓ Gitignore configuration complete")
```

### Integrating with Adapters

Use in adapter generation:

```python
from pathlib import Path
from typing import List
from promptrek.adapters.base import EditorAdapter
from promptrek.utils.gitignore import configure_gitignore

class MyAdapter(EditorAdapter):
    """Adapter with gitignore integration."""

    def generate(self, prompt, output_dir, **kwargs) -> List[Path]:
        """Generate files and update gitignore."""
        generated_files = []

        # Generate editor files
        config_file = output_dir / ".myeditor" / "config.yaml"
        # ... generate config ...
        generated_files.append(config_file)

        # Update gitignore if not in dry run
        if not kwargs.get('dry_run', False):
            # Add editor patterns to gitignore
            configure_gitignore(
                project_dir=output_dir,
                add_editor_files=True,
                remove_cached=True,
                custom_patterns=[".myeditor/config.yaml"]
            )

        return generated_files
```

### CLI Integration Example

Use in CLI commands:

```python
import click
from pathlib import Path
from promptrek.utils.gitignore import configure_gitignore

@click.command()
@click.option('--remove-cached', is_flag=True, help='Remove cached files from git')
def setup_gitignore(remove_cached):
    """Set up .gitignore for PrompTrek."""

    click.echo("Configuring .gitignore...")

    results = configure_gitignore(
        project_dir=Path.cwd(),
        add_editor_files=True,
        remove_cached=remove_cached
    )

    if results['patterns_added'] > 0:
        click.echo(f"✓ Added {results['patterns_added']} patterns to .gitignore")
    else:
        click.echo("✓ .gitignore already up to date")

    if results['files_removed']:
        click.echo(f"\n⚠️  Removed {len(results['files_removed'])} files from git cache")
        click.echo("   Remember to commit these changes:")
        click.echo("   git commit -m 'Update .gitignore and untrack editor files'")

if __name__ == "__main__":
    setup_gitignore()
```

## Gitignore Patterns

### Standard Editor Patterns

PrompTrek includes patterns for all supported editors:

```python
# GitHub Copilot
".github/copilot-instructions.md"
".github/instructions/*.instructions.md"
".github/prompts/*.prompt.md"

# Cursor
".cursor/rules/*.mdc"
".cursor/rules/index.mdc"
"AGENTS.md"

# Continue
".continue/config.yaml"
".continue/mcpServers/*.yaml"
".continue/prompts/*.md"
".continue/rules/*.md"

# Windsurf
".windsurf/rules/*.md"

# Cline
".clinerules"
".clinerules/*.md"

# Claude
".claude/CLAUDE.md"
".claude-context.md"
".claude/commands/*.md"
".claude/agents/*.md"
".claude/hooks.yaml"
".mcp.json"

# Amazon Q
".amazonq/rules/*.md"
".amazonq/prompts/*.md"
".amazonq/cli-agents/*.json"
".amazonq/mcp.json"

# JetBrains
".assistant/rules/*.md"

# Kiro
".kiro/steering/*.md"

# MCP configs
".vscode/mcp.json"
```

### PrompTrek Internal Files

Additional patterns for PrompTrek:

```python
# User-specific (never commit)
".promptrek/user-config.promptrek.yaml"
".promptrek/variables.promptrek.yaml"
".promptrek/last-generation.yaml"

# Legacy locations
"variables.promptrek.yaml"  # Old location
```

## Best Practices

### When to Update Gitignore

1. **After first generation**: Add patterns after first `promptrek generate`
2. **When adding editors**: Update when targeting new editors
3. **Custom patterns**: Add custom patterns as needed
4. **Team sync**: Ensure team's `.gitignore` includes these patterns

### When to Remove Cached Files

1. **Already committed**: Files were committed before adding to `.gitignore`
2. **Migration**: Moving from manual to PrompTrek-managed files
3. **Cleanup**: Removing old editor files from git history

### Commit Messages

Good commit messages for gitignore changes:

```bash
# Initial setup
git commit -m "Add PrompTrek editor files to .gitignore"

# With cache removal
git commit -m "Update .gitignore and untrack editor-specific files"

# Adding custom patterns
git commit -m "Add custom editor patterns to .gitignore"
```

## See Also

- [Generate Command](../../cli/generate.md) - Automatic gitignore updates
- [Configuration Guide](../../user-guide/configuration.md) - Project setup
- [Version Control Guide](../../user-guide/version-control.md) - Git best practices
