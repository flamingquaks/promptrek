"""Tests for YAML writer."""

from pathlib import Path

import pytest

from promptrek.cli.yaml_writer import write_promptrek_yaml


class TestYAMLWriter:
    """Test YAML writer functionality."""

    def test_write_basic_dict(self, tmp_path):
        """Test writing basic dictionary."""
        data = {
            "schema_version": "2.0.0",
            "metadata": {"title": "Test", "description": "Test"},
            "content": "# Test",
        }

        output_file = tmp_path / "test.yaml"
        write_promptrek_yaml(data, output_file)

        assert output_file.exists()
        content = output_file.read_text()
        assert "schema_version" in content
        assert "Test" in content

    def test_write_with_nested_structures(self, tmp_path):
        """Test writing nested structures."""
        data = {
            "schema_version": "2.0.0",
            "metadata": {
                "title": "Test",
                "description": "Test",
                "tags": ["tag1", "tag2"],
            },
            "variables": {"VAR1": "value1", "VAR2": "value2"},
            "content": "# Test",
        }

        output_file = tmp_path / "test.yaml"
        write_promptrek_yaml(data, output_file)

        assert output_file.exists()
        content = output_file.read_text()
        assert "variables" in content
        assert "VAR1" in content

    def test_write_multiline_content(self, tmp_path):
        """Test writing multiline content."""
        data = {
            "schema_version": "2.0.0",
            "metadata": {"title": "Test", "description": "Test"},
            "content": "# Test\n\nMultiple lines\nOf content\nHere",
        }

        output_file = tmp_path / "test.yaml"
        write_promptrek_yaml(data, output_file)

        assert output_file.exists()
        content = output_file.read_text()
        assert "Multiple lines" in content

    def test_write_with_lists(self, tmp_path):
        """Test writing with list structures."""
        data = {
            "schema_version": "2.0.0",
            "metadata": {"title": "Test", "description": "Test"},
            "content": "# Test",
            "documents": [
                {"name": "doc1", "content": "Content 1"},
                {"name": "doc2", "content": "Content 2"},
            ],
        }

        output_file = tmp_path / "test.yaml"
        write_promptrek_yaml(data, output_file)

        assert output_file.exists()
        content = output_file.read_text()
        assert "documents" in content
        assert "doc1" in content

    def test_write_with_schema_header_comments(self, tmp_path):
        """Test that PrompTrek UPF header comments are added."""
        data = {
            "schema_version": "3.0.0",
            "metadata": {"title": "Test", "description": "Test"},
            "content": "# Test",
        }

        output_file = tmp_path / "test.yaml"
        write_promptrek_yaml(data, output_file)

        assert output_file.exists()
        content = output_file.read_text()

        # Check for yaml-language-server comment
        assert "# yaml-language-server: $schema=https://promptrek.ai/schema/v3.0.0.json" in content

        # Check for PrompTrek UPF comment
        assert "# PrompTrek Universal Prompt Format (UPF)" in content

        # Check for learn more link
        assert "# Learn more: https://promptrek.ai" in content

        # Verify comments appear at the beginning of the file
        lines = content.split('\n')
        assert lines[0].startswith("# yaml-language-server:")
        assert lines[1] == "# PrompTrek Universal Prompt Format (UPF)"
        assert lines[2] == "# Learn more: https://promptrek.ai"
