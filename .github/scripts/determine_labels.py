#!/usr/bin/env python3
"""
Determine which editor labels should be applied to a PR based on changed files.

This script analyzes the list of changed files and maps them to editor labels.
"""

import os
import re
import sys
from pathlib import Path
from typing import Set

# Mapping of file patterns to editor labels
EDITOR_PATTERNS = {
    "Editor:AmazonQ": [
        r"src/promptrek/adapters/amazon_q\.py",
        r"tests/.*test.*amazon.*q\.py",
        r"examples/.*amazon.*q",
        r"docs/.*amazon.*q",
        r"\.amazonq/",
    ],
    "Editor:Cline": [
        r"src/promptrek/adapters/cline\.py",
        r"tests/.*test.*cline\.py",
        r"examples/.*cline",
        r"docs/.*cline",
        r"\.clinerules/",
    ],
    "Editor:Kiro": [
        r"src/promptrek/adapters/kiro\.py",
        r"tests/.*test.*kiro\.py",
        r"examples/.*kiro",
        r"docs/.*kiro",
        r"\.kiro/",
    ],
    "Editor:ClaudeCode": [
        r"src/promptrek/adapters/claude\.py",
        r"tests/.*test.*claude\.py",
        r"examples/.*claude",
        r"docs/.*claude",
        r"\.claude/",
    ],
    "Editor:Continue": [
        r"src/promptrek/adapters/continue",
        r"tests/.*test.*continue",
        r"examples/.*continue",
        r"docs/.*continue",
        r"\.continue/",
    ],
    "Editor:Copilot": [
        r"src/promptrek/adapters/copilot\.py",
        r"src/promptrek/templates/copilot/",
        r"tests/.*test.*copilot",
        r"examples/.*copilot",
        r"docs/.*copilot",
        r"\.github/copilot",
    ],
    "Editor:Windsurf": [
        r"src/promptrek/adapters/windsurf\.py",
        r"tests/.*test.*windsurf",
        r"examples/.*windsurf",
        r"docs/.*windsurf",
        r"\.windsurf/",
    ],
    "Editor:JetBrainsAI": [
        r"src/promptrek/adapters/jetbrains\.py",
        r"tests/.*test.*jetbrains",
        r"examples/.*jetbrains",
        r"docs/.*jetbrains",
        r"\.assistant/",
    ],
    "Editor:Cursor": [
        r"src/promptrek/adapters/cursor\.py",
        r"tests/.*test.*cursor",
        r"examples/.*cursor",
        r"docs/.*cursor",
        r"\.cursor/",
    ],
}


def determine_labels(changed_files: list[str]) -> Set[str]:
    """
    Determine which editor labels should be applied based on changed files.

    Args:
        changed_files: List of file paths that were changed in the PR

    Returns:
        Set of label names to apply
    """
    labels = set()

    for file_path in changed_files:
        # Normalize path separators
        normalized_path = file_path.replace("\\", "/")

        # Check each editor pattern
        for label, patterns in EDITOR_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, normalized_path, re.IGNORECASE):
                    labels.add(label)
                    break  # Found a match for this editor, move to next

    return labels


def main():
    """Main entry point for the script."""
    if len(sys.argv) < 2:
        print("Usage: determine_labels.py <comma-separated-file-list>", file=sys.stderr)
        sys.exit(1)

    # Get changed files from command line argument
    files_arg = sys.argv[1]
    changed_files = [f.strip() for f in files_arg.split(",") if f.strip()]

    if not changed_files:
        print("No changed files provided", file=sys.stderr)
        # Set empty output for GitHub Actions
        if "GITHUB_OUTPUT" in os.environ:
            with open(os.environ["GITHUB_OUTPUT"], "a") as f:
                f.write("labels=\n")
        sys.exit(0)

    # Determine labels
    labels = determine_labels(changed_files)

    # Output for debugging
    print(f"Changed files: {len(changed_files)}", file=sys.stderr)
    print(
        f"Detected labels: {', '.join(sorted(labels)) if labels else 'none'}",
        file=sys.stderr,
    )

    # Set output for GitHub Actions
    labels_str = ",".join(sorted(labels))
    if "GITHUB_OUTPUT" in os.environ:
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            f.write(f"labels={labels_str}\n")
    else:
        # For local testing
        print(f"Labels: {labels_str}")

    sys.exit(0)


if __name__ == "__main__":
    main()
