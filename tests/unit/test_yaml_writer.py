"""
Tests for YAML writer utility.

Validates that YAML files are written with proper formatting including
literal block scalars for multi-line content.
"""

import tempfile
from pathlib import Path

import pytest

from promptrek.cli.yaml_writer import write_promptrek_yaml


def test_write_yaml_with_literal_block_scalar():
    """Test that multi-line strings use literal block scalar (|) format."""
    data = {
        "schema_version": "2.0.0",
        "metadata": {
            "title": "Test Config",
            "description": "A test configuration",
        },
        "content": "# Test\n\nThis is a multi-line\ncontent field\nwith several lines",
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "test.yaml"
        write_promptrek_yaml(data, output_path)

        # Read the file and check the formatting
        with open(output_path, "r", encoding="utf-8") as f:
            yaml_content = f.read()

        # Should use literal block scalar (|- or |)
        assert "content: |" in yaml_content or "content: |-" in yaml_content
        # Should NOT have escaped newlines
        assert "\\n" not in yaml_content
        # Should have actual newlines in the content
        assert "# Test" in yaml_content
        assert "This is a multi-line" in yaml_content
        assert "with several lines" in yaml_content


def test_write_yaml_single_line_string():
    """Test that single-line strings use regular format."""
    data = {
        "schema_version": "2.0.0",
        "metadata": {
            "title": "Test Config",
            "description": "Single line description",
        },
        "simple_field": "No newlines here",
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "test.yaml"
        write_promptrek_yaml(data, output_path)

        # Read the file
        with open(output_path, "r", encoding="utf-8") as f:
            yaml_content = f.read()

        # Single-line strings should not use literal block scalar
        assert "description: Single line description" in yaml_content
        assert "simple_field: No newlines here" in yaml_content


def test_write_yaml_v2_content_field():
    """Test v2 schema with large content field."""
    content = """# My Project

## Overview
This is a test project with multiple lines.

## Guidelines
- Follow best practices
- Write tests
- Document code

## Examples

```python
def example():
    return "test"
```
"""

    data = {
        "schema_version": "2.0.0",
        "metadata": {
            "title": "My Project",
        },
        "content": content,
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "test.yaml"
        write_promptrek_yaml(data, output_path)

        # Read and verify
        with open(output_path, "r", encoding="utf-8") as f:
            yaml_content = f.read()

        # Must use literal block scalar
        assert "content: |" in yaml_content
        # Content should be readable
        assert "# My Project" in yaml_content
        assert "## Overview" in yaml_content
        assert "def example():" in yaml_content
        # Should not have escape sequences
        assert "\\n" not in yaml_content


def test_write_yaml_preserves_structure():
    """Test that nested structures are preserved correctly."""
    data = {
        "schema_version": "2.0.0",
        "metadata": {
            "title": "Test",
            "tags": ["tag1", "tag2", "tag3"],
        },
        "variables": {
            "VAR1": "value1",
            "VAR2": "value2",
        },
        "content": "Multi-line\ncontent\nhere",
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "test.yaml"
        write_promptrek_yaml(data, output_path)

        # Read back and verify structure
        with open(output_path, "r", encoding="utf-8") as f:
            yaml_content = f.read()

        # Check structure is preserved
        assert "metadata:" in yaml_content
        assert "tags:" in yaml_content
        assert "- tag1" in yaml_content
        assert "variables:" in yaml_content
        assert "VAR1: value1" in yaml_content
        # Content should use literal block
        assert "content: |" in yaml_content


def test_write_yaml_unicode_support():
    """Test that Unicode characters are handled correctly."""
    data = {
        "schema_version": "2.0.0",
        "content": "Unicode test: ✅ 🚀 中文\nMultiple lines\nwith unicode",
        "metadata": {
            "title": "Test with émojis and açcénts",
        },
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "test.yaml"
        write_promptrek_yaml(data, output_path)

        # Read and verify
        with open(output_path, "r", encoding="utf-8") as f:
            yaml_content = f.read()

        # Unicode should be preserved
        assert "✅" in yaml_content
        assert "🚀" in yaml_content
        assert "中文" in yaml_content
        assert "émojis" in yaml_content
        assert "açcénts" in yaml_content
