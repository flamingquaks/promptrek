#!/usr/bin/env python3
"""
Unit tests for the determine_labels.py script.
"""

import sys
from pathlib import Path

# Add the script directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from determine_labels import determine_labels


def test_adapter_files():
    """Test that adapter files are correctly labeled."""
    files = [
        "src/promptrek/adapters/cline.py",
        "src/promptrek/adapters/claude.py",
        "src/promptrek/adapters/cursor.py",
    ]
    labels = determine_labels(files)
    assert "Editor:Cline" in labels
    assert "Editor:ClaudeCode" in labels
    assert "Editor:Cursor" in labels
    assert len(labels) == 3


def test_test_files():
    """Test that test files are correctly labeled."""
    files = [
        "tests/unit/adapters/test_cline.py",
        "tests/unit/adapters/test_claude.py",
        "tests/unit/adapters/test_cursor_comprehensive.py",
    ]
    labels = determine_labels(files)
    assert "Editor:Cline" in labels
    assert "Editor:ClaudeCode" in labels
    assert "Editor:Cursor" in labels


def test_editor_directories():
    """Test that editor-specific directories are correctly labeled."""
    files = [
        ".claude/agents/test.md",
        ".continue/config.yaml",
        ".cursor/rules/index.mdc",
        ".windsurf/rules/example.md",
        ".clinerules/custom.md",
        ".kiro/steering/guide.md",
        ".amazonq/rules/rules.md",
        ".assistant/rules/jetbrains.md",
        ".github/copilot-instructions.md",
    ]
    labels = determine_labels(files)
    assert "Editor:ClaudeCode" in labels
    assert "Editor:Continue" in labels
    assert "Editor:Cursor" in labels
    assert "Editor:Windsurf" in labels
    assert "Editor:Cline" in labels
    assert "Editor:Kiro" in labels
    assert "Editor:AmazonQ" in labels
    assert "Editor:JetBrainsAI" in labels
    assert "Editor:Copilot" in labels


def test_documentation_files():
    """Test that documentation files are correctly labeled."""
    files = [
        "docs/editors/cline.md",
        "docs/adapters/claude-code.md",
        "examples/advanced/cursor-example.yaml",
    ]
    labels = determine_labels(files)
    assert "Editor:Cline" in labels
    assert "Editor:ClaudeCode" in labels
    assert "Editor:Cursor" in labels


def test_non_editor_files():
    """Test that non-editor files don't get labeled."""
    files = [
        "README.md",
        "pyproject.toml",
        "src/promptrek/core/parser.py",
        "tests/unit/core/test_validator.py",
    ]
    labels = determine_labels(files)
    assert len(labels) == 0


def test_mixed_files():
    """Test a mix of editor and non-editor files."""
    files = [
        "src/promptrek/adapters/amazon_q.py",
        "README.md",
        "tests/unit/adapters/test_windsurf.py",
        "pyproject.toml",
        ".continue/config.yaml",
    ]
    labels = determine_labels(files)
    assert "Editor:AmazonQ" in labels
    assert "Editor:Windsurf" in labels
    assert "Editor:Continue" in labels
    assert len(labels) == 3


def test_case_insensitive():
    """Test that pattern matching is case-insensitive."""
    files = [
        "src/promptrek/adapters/CLINE.py",  # Unlikely but should still match
        "TESTS/unit/adapters/test_claude.py",
    ]
    labels = determine_labels(files)
    assert "Editor:Cline" in labels
    assert "Editor:ClaudeCode" in labels


def test_continue_adapter_variations():
    """Test that Continue adapter file variations are matched."""
    files = [
        "src/promptrek/adapters/continue_adapter.py",
        "tests/unit/adapters/test_continue_comprehensive.py",
    ]
    labels = determine_labels(files)
    assert "Editor:Continue" in labels


def test_copilot_template():
    """Test that Copilot template files are labeled."""
    files = [
        "src/promptrek/templates/copilot/instructions.md.j2",
    ]
    labels = determine_labels(files)
    assert "Editor:Copilot" in labels


def test_all_editors():
    """Test that we can detect all editor types."""
    files = [
        "src/promptrek/adapters/amazon_q.py",
        "src/promptrek/adapters/cline.py",
        "src/promptrek/adapters/kiro.py",
        "src/promptrek/adapters/claude.py",
        "src/promptrek/adapters/continue_adapter.py",
        "src/promptrek/adapters/copilot.py",
        "src/promptrek/adapters/windsurf.py",
        "src/promptrek/adapters/jetbrains.py",
        "src/promptrek/adapters/cursor.py",
    ]
    labels = determine_labels(files)
    expected_labels = {
        "Editor:AmazonQ",
        "Editor:Cline",
        "Editor:Kiro",
        "Editor:ClaudeCode",
        "Editor:Continue",
        "Editor:Copilot",
        "Editor:Windsurf",
        "Editor:JetBrainsAI",
        "Editor:Cursor",
    }
    assert labels == expected_labels


if __name__ == "__main__":
    # Run all tests
    test_functions = [
        test_adapter_files,
        test_test_files,
        test_editor_directories,
        test_documentation_files,
        test_non_editor_files,
        test_mixed_files,
        test_case_insensitive,
        test_continue_adapter_variations,
        test_copilot_template,
        test_all_editors,
    ]

    print("Running tests for determine_labels.py...")
    failed = []

    for test_func in test_functions:
        try:
            test_func()
            print(f"✓ {test_func.__name__}")
        except AssertionError as e:
            print(f"✗ {test_func.__name__}: {e}")
            failed.append(test_func.__name__)
        except Exception as e:
            print(f"✗ {test_func.__name__}: Unexpected error: {e}")
            failed.append(test_func.__name__)

    print(f"\n{len(test_functions) - len(failed)}/{len(test_functions)} tests passed")

    if failed:
        print(f"\nFailed tests: {', '.join(failed)}")
        sys.exit(1)
    else:
        print("\nAll tests passed!")
        sys.exit(0)
