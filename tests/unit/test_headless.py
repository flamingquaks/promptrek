"""
Unit tests for headless bootstrap utility.
"""

import pytest

from promptrek.utils.headless import (
    generate_bootstrap_content,
    generate_inline_bootstrap_marker,
)


class TestGenerateBootstrapContent:
    """Test bootstrap content generation."""

    def test_basic_bootstrap_generation(self):
        """Test basic bootstrap file generation."""
        content = generate_bootstrap_content(
            editor_name="claude",
            editor_display_name="Claude Code",
            generated_file_paths=[".claude/claude.md"],
            promptrek_version="0.6.0",
        )

        # Check YAML frontmatter
        assert content.startswith("---")
        assert "auto_execute: true" in content
        assert 'editor: "claude"' in content

        # Check main content
        assert "Claude Code" in content
        assert "PrompTrek" in content
        assert ".claude/claude.md" in content
        assert "promptrek generate" in content
        assert "0.6.0" in content  # Version appears in footer

    def test_bootstrap_with_custom_message(self):
        """Test bootstrap generation with custom message."""
        custom_msg = (
            "This project uses special configuration. Run tests after generation."
        )
        content = generate_bootstrap_content(
            editor_name="cursor",
            editor_display_name="Cursor",
            generated_file_paths=[".cursor/rules/main.mdc"],
            custom_message=custom_msg,
            promptrek_version="0.6.0",
        )

        assert custom_msg in content
        # Check for project-specific section (may vary in exact wording)
        assert "Project" in content or "project" in content

    def test_bootstrap_with_multiple_files(self):
        """Test bootstrap with multiple generated files."""
        files = [
            ".claude/claude.md",
            ".claude/agents/researcher.md",
            ".claude/commands/test.md",
        ]
        content = generate_bootstrap_content(
            editor_name="claude",
            editor_display_name="Claude Code",
            generated_file_paths=files,
            promptrek_version="0.6.0",
        )

        # All files should be listed
        for file_path in files:
            assert file_path in content

    def test_bootstrap_yaml_frontmatter_format(self):
        """Test YAML frontmatter is properly formatted."""
        content = generate_bootstrap_content(
            editor_name="cline",
            editor_display_name="Cline",
            generated_file_paths=[".clinerules/default-rules.md"],
            promptrek_version="0.6.0",
        )

        lines = content.split("\n")
        assert lines[0] == "---"

        # Find closing ---
        closing_index = None
        for i, line in enumerate(lines[1:], 1):
            if line == "---":
                closing_index = i
                break

        assert closing_index is not None, "YAML frontmatter not properly closed"
        assert closing_index > 1, "YAML frontmatter is empty"

    def test_bootstrap_contains_preflight_checks(self):
        """Test bootstrap includes pre-flight checks."""
        content = generate_bootstrap_content(
            editor_name="windsurf",
            editor_display_name="Windsurf",
            generated_file_paths=[".windsurf/rules/main.md"],
            promptrek_version="0.6.0",
        )

        assert "Pre-flight Check" in content or "preflight" in content.lower()
        assert "project.promptrek.yaml" in content

    def test_bootstrap_contains_generation_steps(self):
        """Test bootstrap includes generation instructions."""
        content = generate_bootstrap_content(
            editor_name="continue",
            editor_display_name="Continue",
            generated_file_paths=[".continue/rules/main.md"],
            promptrek_version="0.6.0",
        )

        assert "promptrek generate" in content
        assert "project.promptrek.yaml" in content

    def test_bootstrap_different_editors(self):
        """Test bootstrap generation for different editors."""
        editors = [
            ("claude", "Claude Code"),
            ("copilot", "GitHub Copilot"),
            ("cursor", "Cursor"),
            ("continue", "Continue"),
            ("windsurf", "Windsurf"),
            ("cline", "Cline"),
            ("kiro", "Kiro"),
            ("amazon-q", "Amazon Q"),
            ("jetbrains", "JetBrains AI"),
        ]

        for editor_name, display_name in editors:
            content = generate_bootstrap_content(
                editor_name=editor_name,
                editor_display_name=display_name,
                generated_file_paths=[f".{editor_name}/test.md"],
                promptrek_version="0.6.0",
            )

            assert editor_name in content
            assert display_name in content
            assert "PrompTrek" in content

    def test_bootstrap_version_included(self):
        """Test PrompTrek version is included in bootstrap."""
        version = "1.2.3"
        content = generate_bootstrap_content(
            editor_name="claude",
            editor_display_name="Claude Code",
            generated_file_paths=[".claude/claude.md"],
            promptrek_version=version,
        )

        assert version in content


class TestGenerateInlineBootstrapMarker:
    """Test inline bootstrap marker generation."""

    def test_html_comment_style(self):
        """Test HTML comment style marker."""
        marker = generate_inline_bootstrap_marker(
            editor_name="copilot",
            editor_display_name="GitHub Copilot",
            comment_style="html",
        )

        assert marker.startswith("<!--")
        assert "-->" in marker  # Ends with closing comment (may have trailing newline)
        assert "PROMPTREK" in marker or "PrompTrek" in marker
        assert "promptrek generate" in marker

    def test_hash_comment_style(self):
        """Test hash comment style marker."""
        marker = generate_inline_bootstrap_marker(
            editor_name="test",
            editor_display_name="Test Editor",
            comment_style="hash",
        )

        lines = marker.split("\n")
        for line in lines:
            if line.strip():  # Skip empty lines
                assert line.startswith("#")

    def test_yaml_comment_style(self):
        """Test YAML comment style marker."""
        marker = generate_inline_bootstrap_marker(
            editor_name="test",
            editor_display_name="Test Editor",
            comment_style="yaml",
        )

        lines = marker.split("\n")
        for line in lines:
            if line.strip():  # Skip empty lines
                assert line.startswith("#")

    def test_inline_marker_contains_key_info(self):
        """Test inline marker contains essential information."""
        marker = generate_inline_bootstrap_marker(
            editor_name="copilot",
            editor_display_name="GitHub Copilot",
            comment_style="html",
        )

        assert "PROMPTREK" in marker or "PrompTrek" in marker
        assert "promptrek generate" in marker
        # HTML style doesn't include editor name/project file in all comment styles

    def test_inline_marker_different_editors(self):
        """Test inline markers for different editors."""
        editors = [
            ("copilot", "GitHub Copilot"),
            ("claude", "Claude Code"),
        ]

        for editor_name, display_name in editors:
            marker = generate_inline_bootstrap_marker(
                editor_name=editor_name,
                editor_display_name=display_name,
                comment_style="html",
            )

            assert editor_name in marker or display_name in marker
            assert "PrompTrek" in marker


class TestBootstrapEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_file_list(self):
        """Test with empty generated files list."""
        content = generate_bootstrap_content(
            editor_name="claude",
            editor_display_name="Claude Code",
            generated_file_paths=[],
            promptrek_version="0.6.0",
        )

        # Should still generate valid content
        assert content.startswith("---")
        assert "PrompTrek" in content

    def test_special_characters_in_custom_message(self):
        """Test custom message with special characters."""
        custom_msg = "Use `npm test` and ensure $ENV_VAR is set!"
        content = generate_bootstrap_content(
            editor_name="claude",
            editor_display_name="Claude Code",
            generated_file_paths=[".claude/claude.md"],
            custom_message=custom_msg,
            promptrek_version="0.6.0",
        )

        assert custom_msg in content

    def test_long_file_paths(self):
        """Test with very long file paths."""
        long_path = "a" * 200 + "/file.md"
        content = generate_bootstrap_content(
            editor_name="claude",
            editor_display_name="Claude Code",
            generated_file_paths=[long_path],
            promptrek_version="0.6.0",
        )

        assert long_path in content

    def test_unicode_in_custom_message(self):
        """Test unicode characters in custom message."""
        custom_msg = "注意：このプロジェクトは特別な設定が必要です 🚀"
        content = generate_bootstrap_content(
            editor_name="claude",
            editor_display_name="Claude Code",
            generated_file_paths=[".claude/claude.md"],
            custom_message=custom_msg,
            promptrek_version="0.6.0",
        )

        assert custom_msg in content
