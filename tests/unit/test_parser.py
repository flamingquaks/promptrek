"""Unit tests for UPF parser."""

import pytest
import yaml

from promptrek.core.exceptions import UPFFileNotFoundError, UPFParsingError
from promptrek.core.models import UniversalPrompt, UniversalPromptV2
from promptrek.core.parser import UPFParser


class TestUPFParser:
    """Test UPFParser functionality."""

    def test_parse_valid_file(self, sample_upf_file):
        """Test parsing a valid UPF file."""
        parser = UPFParser()
        prompt = parser.parse_file(sample_upf_file)

        assert isinstance(prompt, UniversalPrompt)
        assert prompt.metadata.title == "Test Project Assistant"
        assert len(prompt.targets) == 2

    def test_parse_nonexistent_file(self):
        """Test parsing a non-existent file raises error."""
        parser = UPFParser()
        with pytest.raises(UPFFileNotFoundError):
            parser.parse_file("nonexistent.promptrek.yaml")

    def test_parse_invalid_extension(self, tmp_path):
        """Test parsing file with invalid extension raises error."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("content")

        parser = UPFParser()
        with pytest.raises(UPFParsingError):
            parser.parse_file(file_path)

    def test_parse_invalid_yaml(self, tmp_path):
        """Test parsing invalid YAML raises error."""
        file_path = tmp_path / "invalid.promptrek.yaml"
        file_path.write_text("invalid: yaml: content: [")

        parser = UPFParser()
        with pytest.raises(UPFParsingError):
            parser.parse_file(file_path)

    def test_parse_dict(self, sample_upf_data):
        """Test parsing a dictionary."""
        parser = UPFParser()
        prompt = parser.parse_dict(sample_upf_data)

        assert isinstance(prompt, UniversalPrompt)
        assert prompt.metadata.title == "Test Project Assistant"

    def test_parse_invalid_dict(self):
        """Test parsing invalid dictionary raises error."""
        parser = UPFParser()
        with pytest.raises(UPFParsingError):
            parser.parse_dict("not a dict")

    def test_parse_string(self, sample_upf_data):
        """Test parsing YAML string."""
        yaml_content = yaml.dump(sample_upf_data)
        parser = UPFParser()
        prompt = parser.parse_string(yaml_content)

        assert isinstance(prompt, UniversalPrompt)
        assert prompt.metadata.title == "Test Project Assistant"

    def test_parse_invalid_string(self):
        """Test parsing invalid YAML string raises error."""
        parser = UPFParser()
        with pytest.raises(UPFParsingError):
            parser.parse_string("invalid: yaml: [")

    def test_validate_file_extension(self):
        """Test file extension validation."""
        parser = UPFParser()

        assert parser.validate_file_extension("test.promptrek.yaml") is True
        assert parser.validate_file_extension("test.promptrek.yml") is True
        assert parser.validate_file_extension("test.yaml") is False
        assert parser.validate_file_extension("test.txt") is False

    def test_find_upf_files(self, tmp_path, sample_upf_data):
        """Test finding UPF files in directory."""
        # Create test files
        (tmp_path / "project.promptrek.yaml").write_text(yaml.dump(sample_upf_data))
        (tmp_path / "config.promptrek.yml").write_text(yaml.dump(sample_upf_data))
        (tmp_path / "other.yaml").write_text("not upf")

        parser = UPFParser()
        upf_files = parser.find_upf_files(tmp_path)

        assert len(upf_files) == 2
        file_names = [f.name for f in upf_files]
        assert "project.promptrek.yaml" in file_names
        assert "config.promptrek.yml" in file_names

    def test_find_upf_files_recursive(self, tmp_path, sample_upf_data):
        """Test finding UPF files recursively."""
        # Create nested structure
        subdir = tmp_path / "subdir"
        subdir.mkdir()

        (tmp_path / "root.promptrek.yaml").write_text(yaml.dump(sample_upf_data))
        (subdir / "nested.promptrek.yaml").write_text(yaml.dump(sample_upf_data))

        parser = UPFParser()

        # Non-recursive should find only root file
        files = parser.find_upf_files(tmp_path, recursive=False)
        assert len(files) == 1

        # Recursive should find both files
        files = parser.find_upf_files(tmp_path, recursive=True)
        assert len(files) == 2

    def test_parse_multiple_files(self, tmp_path):
        """Test parsing and merging multiple UPF files."""
        # Create first file
        data1 = {
            "schema_version": "1.0.0",
            "metadata": {
                "title": "Project 1",
                "description": "First project",
                "version": "1.0",
                "author": "Test Author",
            },
            "instructions": {"general": ["Rule 1", "Rule 2"]},
            "context": {"technologies": ["python"]},
            "targets": ["editor1"],
        }
        file1 = tmp_path / "first.promptrek.yaml"
        file1.write_text(yaml.dump(data1))

        # Create second file
        data2 = {
            "schema_version": "1.0.0",
            "metadata": {
                "title": "Project 2",
                "description": "Second project",
                "version": "1.0",
                "author": "Test Author",
            },
            "instructions": {"general": ["Rule 3"], "code_style": ["Style 1"]},
            "context": {"technologies": ["javascript"]},
            "targets": ["editor2"],
        }
        file2 = tmp_path / "second.promptrek.yaml"
        file2.write_text(yaml.dump(data2))

        parser = UPFParser()
        merged_prompt = parser.parse_multiple_files([file1, file2])

        # Check that content was merged properly
        assert merged_prompt.metadata.title == "Project 2"  # Second takes precedence
        assert merged_prompt.metadata.description == "Second project"
        assert len(merged_prompt.instructions.general) == 3  # Combined rules
        assert "Rule 1" in merged_prompt.instructions.general
        assert "Rule 3" in merged_prompt.instructions.general
        assert merged_prompt.instructions.code_style == ["Style 1"]
        assert len(merged_prompt.context.technologies) == 2  # Combined technologies
        assert "python" in merged_prompt.context.technologies
        assert "javascript" in merged_prompt.context.technologies
        assert len(merged_prompt.targets) == 2  # Combined targets

    def test_parse_directory(self, tmp_path):
        """Test parsing all UPF files in a directory."""
        # Create multiple files
        data1 = {
            "schema_version": "1.0.0",
            "metadata": {
                "title": "Base Project",
                "description": "Base project description",
                "version": "1.0",
                "author": "Test Author",
            },
            "instructions": {"general": ["Base rule"]},
            "targets": ["editor1"],
        }
        (tmp_path / "base.promptrek.yaml").write_text(yaml.dump(data1))

        data2 = {
            "schema_version": "1.0.0",
            "metadata": {
                "title": "Additional Project",
                "description": "Additional project description",
                "version": "1.0",
                "author": "Test Author",
            },
            "instructions": {"general": ["Additional rule"]},
            "targets": ["editor2"],
        }
        (tmp_path / "additional.promptrek.yaml").write_text(yaml.dump(data2))

        parser = UPFParser()
        merged_prompt = parser.parse_directory(tmp_path)

        # Should find and merge both files
        assert merged_prompt.metadata.title == "Base Project"
        assert len(merged_prompt.instructions.general) == 2
        assert len(merged_prompt.targets) == 2

    def test_parse_directory_no_files(self, tmp_path):
        """Test parsing directory with no UPF files raises error."""
        parser = UPFParser()
        with pytest.raises(UPFParsingError, match="No .promptrek.yaml files found"):
            parser.parse_directory(tmp_path)

    def test_merge_prompts_complex(self):
        """Test complex prompt merging scenarios."""
        from promptrek.core.models import UniversalPrompt

        # Create base prompt
        base_data = {
            "schema_version": "1.0.0",
            "metadata": {
                "title": "Base",
                "description": "Base project",
                "version": "1.0",
                "author": "Test Author",
            },
            "instructions": {"general": ["Base rule"], "testing": ["Test base"]},
            "context": {"technologies": ["python"], "project_type": "api"},
            "variables": {"VAR1": "base_value"},
            "targets": ["editor1"],
        }
        base_prompt = UniversalPrompt(**base_data)

        # Create additional prompt
        additional_data = {
            "schema_version": "1.0.0",
            "metadata": {
                "title": "Enhanced",
                "version": "1.0",
                "author": "Test Author",
                "description": "Enhanced version",
            },
            "instructions": {
                "general": ["Additional rule"],
                "code_style": ["Style rule"],
            },
            "context": {
                "technologies": ["javascript"],
                "description": "Full stack app",
            },
            "variables": {"VAR1": "new_value", "VAR2": "additional_value"},
            "targets": ["editor2"],
        }
        additional_prompt = UniversalPrompt(**additional_data)

        parser = UPFParser()
        merged = parser._merge_prompts(base_prompt, additional_prompt)

        # Test metadata merging
        assert merged.metadata.title == "Enhanced"  # Additional takes precedence
        assert merged.metadata.version == "1.0"  # Base preserved
        assert merged.metadata.description == "Enhanced version"

        # Test instructions merging
        assert len(merged.instructions.general) == 2
        assert "Base rule" in merged.instructions.general
        assert "Additional rule" in merged.instructions.general
        assert merged.instructions.testing == ["Test base"]
        assert merged.instructions.code_style == ["Style rule"]

        # Test context merging
        assert len(merged.context.technologies) == 2
        assert merged.context.project_type == "api"  # Base preserved
        assert (
            merged.context.description == "Full stack app"
        )  # Additional takes precedence

        # Test variables merging
        assert merged.variables["VAR1"] == "new_value"  # Additional takes precedence
        assert merged.variables["VAR2"] == "additional_value"

        # Test targets merging
        assert len(merged.targets) == 2
        assert "editor1" in merged.targets
        assert "editor2" in merged.targets


class TestUPFParserV2:
    """Test UPFParser functionality for v2 schema."""

    def test_parse_v2_file(self, tmp_path):
        """Test parsing a v2 format file."""
        v2_data = {
            "schema_version": "2.0.0",
            "metadata": {
                "title": "V2 Test Project",
                "description": "Test v2 schema",
                "version": "1.0.0",
                "author": "Test Author",
                "tags": ["v2", "test"],
            },
            "content": "# V2 Test Project\n\n## Guidelines\n- Write clean code\n- Follow best practices",
            "variables": {"PROJECT_NAME": "v2-test"},
        }
        file_path = tmp_path / "v2.promptrek.yaml"
        file_path.write_text(yaml.dump(v2_data))

        parser = UPFParser()
        prompt = parser.parse_file(file_path)

        assert isinstance(prompt, UniversalPromptV2)
        assert prompt.schema_version == "2.0.0"
        assert prompt.metadata.title == "V2 Test Project"
        assert "Write clean code" in prompt.content
        assert prompt.variables["PROJECT_NAME"] == "v2-test"

    def test_parse_v2_with_documents(self, tmp_path):
        """Test parsing v2 file with documents field."""
        v2_data = {
            "schema_version": "2.0.0",
            "metadata": {
                "title": "Multi-Doc Project",
                "description": "Test with documents",
                "version": "1.0.0",
                "author": "Test",
            },
            "content": "# Main Content",
            "documents": [
                {
                    "name": "general",
                    "content": "# General Rules\n- Rule 1",
                },
                {
                    "name": "code-style",
                    "content": "# Code Style\n- Style 1",
                },
            ],
        }
        file_path = tmp_path / "multi-doc.promptrek.yaml"
        file_path.write_text(yaml.dump(v2_data))

        parser = UPFParser()
        prompt = parser.parse_file(file_path)

        assert isinstance(prompt, UniversalPromptV2)
        assert len(prompt.documents) == 2
        assert prompt.documents[0].name == "general"
        assert "Rule 1" in prompt.documents[0].content

    def test_parse_v2_minimal(self, tmp_path):
        """Test parsing minimal v2 file."""
        v2_data = {
            "schema_version": "2.0.0",
            "metadata": {
                "title": "Minimal V2",
                "description": "Minimal test",
                "version": "1.0.0",
                "author": "Test",
            },
            "content": "# Minimal content",
        }
        file_path = tmp_path / "minimal.promptrek.yaml"
        file_path.write_text(yaml.dump(v2_data))

        parser = UPFParser()
        prompt = parser.parse_file(file_path)

        assert isinstance(prompt, UniversalPromptV2)
        assert prompt.schema_version == "2.0.0"
        assert prompt.documents is None
        assert prompt.variables is None

    def test_parse_v2_vs_v1_detection(self, tmp_path):
        """Test parser correctly detects v1 vs v2 schema."""
        # Create v1 file
        v1_data = {
            "schema_version": "1.0.0",
            "metadata": {
                "title": "V1 Project",
                "description": "V1 test",
                "version": "1.0.0",
                "author": "Test",
            },
            "targets": ["claude"],
            "instructions": {"general": ["Rule 1"]},
        }
        v1_file = tmp_path / "v1.promptrek.yaml"
        v1_file.write_text(yaml.dump(v1_data))

        # Create v2 file
        v2_data = {
            "schema_version": "2.0.0",
            "metadata": {
                "title": "V2 Project",
                "description": "V2 test",
                "version": "1.0.0",
                "author": "Test",
            },
            "content": "# V2 content",
        }
        v2_file = tmp_path / "v2.promptrek.yaml"
        v2_file.write_text(yaml.dump(v2_data))

        parser = UPFParser()

        # Parse v1 file
        v1_prompt = parser.parse_file(v1_file)
        assert isinstance(v1_prompt, UniversalPrompt)
        assert v1_prompt.schema_version == "1.0.0"
        assert hasattr(v1_prompt, "targets")

        # Parse v2 file
        v2_prompt = parser.parse_file(v2_file)
        assert isinstance(v2_prompt, UniversalPromptV2)
        assert v2_prompt.schema_version == "2.0.0"
        assert not hasattr(v2_prompt, "targets")

    def test_parse_v2_string(self):
        """Test parsing v2 from YAML string."""
        v2_yaml = """schema_version: 2.0.0
metadata:
  title: String Test
  description: Test from string
  version: 1.0.0
  author: Test
content: |
  # String Test

  ## Guidelines
  - Rule 1
  - Rule 2
variables:
  VAR1: value1
"""
        parser = UPFParser()
        prompt = parser.parse_string(v2_yaml)

        assert isinstance(prompt, UniversalPromptV2)
        assert prompt.metadata.title == "String Test"
        assert "Rule 1" in prompt.content
        assert prompt.variables["VAR1"] == "value1"

    def test_parse_v2_dict(self):
        """Test parsing v2 from dictionary."""
        v2_dict = {
            "schema_version": "2.0.0",
            "metadata": {
                "title": "Dict Test",
                "description": "Test from dict",
                "version": "1.0.0",
                "author": "Test",
            },
            "content": "# Dict content",
            "variables": {"KEY": "value"},
        }
        parser = UPFParser()
        prompt = parser.parse_dict(v2_dict)

        assert isinstance(prompt, UniversalPromptV2)
        assert prompt.metadata.title == "Dict Test"
        assert prompt.variables["KEY"] == "value"

    def test_parse_v2_invalid_schema_version(self, tmp_path):
        """Test v2 file with wrong schema version."""
        invalid_data = {
            "schema_version": "1.5.0",  # Invalid version
            "metadata": {
                "title": "Invalid",
                "description": "Invalid version",
                "version": "1.0.0",
                "author": "Test",
            },
            "content": "# Content",
        }
        file_path = tmp_path / "invalid.promptrek.yaml"
        file_path.write_text(yaml.dump(invalid_data))

        parser = UPFParser()
        with pytest.raises(UPFParsingError):
            parser.parse_file(file_path)

    def test_parse_v2_missing_content(self, tmp_path):
        """Test v2 file without content field."""
        invalid_data = {
            "schema_version": "2.0.0",
            "metadata": {
                "title": "No Content",
                "description": "Missing content",
                "version": "1.0.0",
                "author": "Test",
            },
        }
        file_path = tmp_path / "no-content.promptrek.yaml"
        file_path.write_text(yaml.dump(invalid_data))

        parser = UPFParser()
        with pytest.raises(UPFParsingError):
            parser.parse_file(file_path)

    def test_parse_multiple_files_v2(self, tmp_path):
        """Test parsing and merging multiple v2 files."""
        file1 = tmp_path / "file1.promptrek.yaml"
        file1.write_text(
            """
schema_version: "2.0.0"
metadata:
  title: "File 1"
  description: "First file"
content: |
  # Content 1
"""
        )

        file2 = tmp_path / "file2.promptrek.yaml"
        file2.write_text(
            """
schema_version: "2.0.0"
metadata:
  title: "File 2"
  description: "Second file"
content: |
  # Content 2
"""
        )

        parser = UPFParser()
        merged = parser.parse_multiple_files([file1, file2])

        # Should return merged prompt
        assert isinstance(merged, UniversalPromptV2)
        assert "Content 1" in merged.content or "Content 2" in merged.content

    def test_parse_directory_v2(self, tmp_path):
        """Test parsing directory with v2 files."""
        (tmp_path / "file1.promptrek.yaml").write_text(
            """
schema_version: "2.0.0"
metadata:
  title: "File 1"
  description: "First"
content: "# Content"
"""
        )

        (tmp_path / "file2.promptrek.yaml").write_text(
            """
schema_version: "2.0.0"
metadata:
  title: "File 2"
  description: "Second"
content: "# Content"
"""
        )

        parser = UPFParser()
        merged = parser.parse_directory(tmp_path)

        # Should return merged prompt
        assert isinstance(merged, UniversalPromptV2)

    def test_parse_file_unexpected_error(self, tmp_path):
        """Test handling of unexpected errors during parsing."""
        # Create a file that will cause an unexpected error
        bad_file = tmp_path / "bad.promptrek.yaml"
        bad_file.write_text(
            "schema_version: 2.0.0\nmetadata: !invalid_tag\n  title: Test"
        )

        parser = UPFParser()
        with pytest.raises(UPFParsingError):
            parser.parse_file(bad_file)

    def test_parse_string_basic(self):
        """Test parsing from string."""
        parser = UPFParser()
        yaml_content = """
schema_version: "2.0.0"
metadata:
  title: "String Test"
  description: "Test"
content: "# Content"
"""
        prompt = parser.parse_string(yaml_content)

        assert isinstance(prompt, UniversalPromptV2)
        assert prompt.metadata.title == "String Test"

    def test_get_major_version_valid(self):
        """Test _get_major_version with valid input."""
        parser = UPFParser()

        # Should extract major version
        assert parser._get_major_version("2.0.0") == "2"
        assert parser._get_major_version("1.5.3") == "1"

    def test_get_major_version_invalid(self):
        """Test _get_major_version with invalid input."""
        parser = UPFParser()

        # None should trigger AttributeError and return "1"
        assert parser._get_major_version(None) == "1"

    def test_parse_dict_with_conditions(self):
        """Test parsing dict with conditions field."""
        parser = UPFParser()
        data = {
            "schema_version": "1.0.0",
            "metadata": {"title": "Test", "description": "Test"},
            "targets": ["claude"],
            "instructions": {"general": ["Test"]},
            "conditions": [
                {
                    "if": "EDITOR == 'claude'",
                    "then": {"instructions": {"general": ["Claude specific"]}},
                }
            ],
        }

        prompt = parser.parse_dict(data)

        assert isinstance(prompt, UniversalPrompt)
        assert prompt.conditions is not None

    def test_parse_dict_with_examples(self):
        """Test parsing dict with examples field."""
        parser = UPFParser()
        data = {
            "schema_version": "1.0.0",
            "metadata": {"title": "Test", "description": "Test"},
            "targets": ["claude"],
            "instructions": {"general": ["Test"]},
            "examples": {"python": "def test(): pass"},
        }

        prompt = parser.parse_dict(data)

        assert isinstance(prompt, UniversalPrompt)
        assert prompt.examples is not None
        assert "python" in prompt.examples

    def test_parse_dict_malformed_data(self):
        """Test parsing dict with data that causes unexpected errors."""
        parser = UPFParser()

        # Data that will pass YAML parsing but fail Pydantic validation in unexpected way
        bad_data = {
            "schema_version": "2.0.0",
            "metadata": {"title": 123, "description": 456},  # Wrong types
            "content": None,  # Wrong type
        }

        with pytest.raises(UPFParsingError):
            parser.parse_dict(bad_data)

    def test_format_validation_error(self):
        """Test validation error formatting."""
        parser = UPFParser()

        # Create a validation error by trying to parse invalid data
        bad_data = {
            "schema_version": "2.0.0",
            "metadata": {"title": "Test"},  # Missing required description
            "content": "# Test",
        }

        with pytest.raises(UPFParsingError) as exc_info:
            parser.parse_dict(bad_data)

        # Should contain formatted error message
        assert (
            "description" in str(exc_info.value).lower()
            or "missing" in str(exc_info.value).lower()
        )


class TestUPFParserV1Imports:
    """Test UPFParser functionality for v1 imports feature."""

    def test_parse_v1_with_imports(self, tmp_path):
        """Test parsing a v1 file with imports."""
        # Create a base file to import
        base_data = {
            "schema_version": "1.0.0",
            "metadata": {
                "title": "Base Project",
                "description": "Base configuration",
                "version": "1.0.0",
                "author": "Test",
            },
            "context": {
                "project_type": "web",
                "technologies": ["Python"],
            },
            "instructions": {
                "general": ["Write clean code"],
            },
            "targets": ["claude"],
        }
        base_file = tmp_path / "base.promptrek.yaml"
        base_file.write_text(yaml.dump(base_data))

        # Create a main file that imports the base
        main_data = {
            "schema_version": "1.0.0",
            "metadata": {
                "title": "Main Project",
                "description": "Main configuration with imports",
                "version": "1.0.0",
                "author": "Test",
            },
            "imports": [{"path": "base.promptrek.yaml"}],
            "instructions": {
                "general": ["Follow project guidelines"],
            },
            "targets": ["claude"],
        }
        main_file = tmp_path / "main.promptrek.yaml"
        main_file.write_text(yaml.dump(main_data))

        parser = UPFParser()
        prompt = parser.parse_file(main_file)

        assert isinstance(prompt, UniversalPrompt)
        assert prompt.metadata.title == "Main Project"
        # Check that imports were processed (base instructions should be included)
        assert len(prompt.instructions.general) >= 1

    def test_parse_dict_unexpected_error(self):
        """Test handling of unexpected error during parse_dict."""
        parser = UPFParser()

        # Create data that will cause an unexpected error during model initialization
        # Using a mock to force an unexpected exception
        import unittest.mock as mock

        with mock.patch("promptrek.core.parser.UniversalPrompt") as mock_model:
            mock_model.side_effect = RuntimeError("Unexpected error")

            data = {
                "schema_version": "1.0.0",
                "metadata": {"title": "Test", "description": "Test"},
                "targets": ["claude"],
                "instructions": {"general": ["Test"]},
            }

            with pytest.raises(UPFParsingError) as exc_info:
                parser.parse_dict(data)

            assert "Unexpected error" in str(exc_info.value)


class TestUPFParserV3:
    """Test UPFParser functionality for v3 schema."""

    def test_parse_v3_basic(self, tmp_path):
        """Test parsing a basic v3 file."""
        import yaml

        v3_data = {
            "schema_version": "3.0.0",
            "metadata": {
                "title": "V3 Test Project",
                "description": "Test v3 schema",
                "version": "1.0.0",
                "author": "Test Author",
            },
            "content": "# V3 Test\n\nContent here.",
        }
        file_path = tmp_path / "v3.promptrek.yaml"
        file_path.write_text(yaml.dump(v3_data))

        from promptrek.core.models import UniversalPromptV3
        from promptrek.core.parser import UPFParser

        parser = UPFParser()
        prompt = parser.parse_file(file_path)

        assert isinstance(prompt, UniversalPromptV3)
        assert prompt.schema_version == "3.0.0"
        assert prompt.metadata.title == "V3 Test Project"

    def test_parse_v3_with_mcp(self, tmp_path):
        """Test parsing v3 with MCP servers."""
        import yaml

        v3_data = {
            "schema_version": "3.0.0",
            "metadata": {"title": "V3 MCP", "description": "Test", "version": "1.0.0"},
            "content": "# Content",
            "mcp_servers": [{"name": "test", "command": "node", "args": ["server.js"]}],
        }
        file_path = tmp_path / "v3-mcp.promptrek.yaml"
        file_path.write_text(yaml.dump(v3_data))

        from promptrek.core.models import UniversalPromptV3
        from promptrek.core.parser import UPFParser

        parser = UPFParser()
        prompt = parser.parse_file(file_path)

        assert isinstance(prompt, UniversalPromptV3)
        assert prompt.mcp_servers is not None
        assert len(prompt.mcp_servers) == 1

    def test_parse_v3_with_nested_plugins_backward_compat(self, tmp_path):
        """Test parsing v3 with deprecated nested plugins structure."""
        import sys
        from io import StringIO

        import yaml

        v3_data = {
            "schema_version": "3.0.0",
            "metadata": {
                "title": "V3 Legacy",
                "description": "Test",
                "version": "1.0.0",
            },
            "content": "# Content",
            "plugins": {
                "mcp_servers": [{"name": "test", "command": "node"}],
                "commands": [
                    {"name": "test-cmd", "description": "Test", "prompt": "Test"}
                ],
            },
        }
        file_path = tmp_path / "v3-legacy.promptrek.yaml"
        file_path.write_text(yaml.dump(v3_data))

        from promptrek.core.models import UniversalPromptV3
        from promptrek.core.parser import UPFParser

        # Capture stderr to check for deprecation warning
        old_stderr = sys.stderr
        sys.stderr = StringIO()

        try:
            parser = UPFParser()
            prompt = parser.parse_file(file_path)

            # Check deprecation warning was emitted
            warning_output = sys.stderr.getvalue()
            assert "DEPRECATION WARNING" in warning_output
            assert "plugins.mcp_servers" in warning_output

            # Check that fields were auto-promoted
            assert isinstance(prompt, UniversalPromptV3)
            assert prompt.mcp_servers is not None
            assert len(prompt.mcp_servers) == 1
            assert prompt.commands is not None
            assert len(prompt.commands) == 1
        finally:
            sys.stderr = old_stderr

    def test_parse_v3_with_all_nested_plugins_backward_compat(self, tmp_path):
        """Test parsing v3 with all plugin types in nested structure."""
        import sys
        from io import StringIO

        import yaml

        v3_data = {
            "schema_version": "3.0.0",
            "metadata": {
                "title": "V3 Full Legacy",
                "description": "Test",
                "version": "1.0.0",
            },
            "content": "# Content",
            "plugins": {
                "mcp_servers": [{"name": "test-mcp", "command": "node"}],
                "commands": [
                    {"name": "test-cmd", "description": "Test", "prompt": "Test"}
                ],
                "agents": [
                    {
                        "name": "test-agent",
                        "description": "Test Agent",
                        "system_prompt": "You are a test",
                    }
                ],
                "hooks": [
                    {"name": "test-hook", "event": "pre-commit", "command": "pytest"}
                ],
            },
        }
        file_path = tmp_path / "v3-full-legacy.promptrek.yaml"
        file_path.write_text(yaml.dump(v3_data))

        from promptrek.core.models import UniversalPromptV3
        from promptrek.core.parser import UPFParser

        # Capture stderr to check for deprecation warning
        old_stderr = sys.stderr
        sys.stderr = StringIO()

        try:
            parser = UPFParser()
            prompt = parser.parse_file(file_path)

            # Check that all fields were auto-promoted
            assert isinstance(prompt, UniversalPromptV3)
            assert prompt.mcp_servers is not None
            assert len(prompt.mcp_servers) == 1
            assert prompt.commands is not None
            assert len(prompt.commands) == 1
            assert prompt.agents is not None
            assert len(prompt.agents) == 1
            assert prompt.hooks is not None
            assert len(prompt.hooks) == 1
        finally:
            sys.stderr = old_stderr

    def test_parse_v3_with_partial_nested_plugins(self, tmp_path):
        """Test parsing v3 with only some nested plugin fields."""
        import yaml

        # Test case where only agents and hooks are nested
        v3_data = {
            "schema_version": "3.0.0",
            "metadata": {
                "title": "Partial",
                "description": "Test",
                "version": "1.0.0",
            },
            "content": "# Content",
            "plugins": {
                "agents": [
                    {
                        "name": "agent1",
                        "description": "Test",
                        "system_prompt": "Test",
                    }
                ],
                "hooks": [
                    {"name": "hook1", "event": "pre-commit", "command": "test"}
                ],
            },
        }
        file_path = tmp_path / "v3-partial.promptrek.yaml"
        file_path.write_text(yaml.dump(v3_data))

        from promptrek.core.models import UniversalPromptV3
        from promptrek.core.parser import UPFParser

        parser = UPFParser()
        prompt = parser.parse_file(file_path)

        # Check that partial fields were promoted
        assert isinstance(prompt, UniversalPromptV3)
        assert prompt.agents is not None
        assert len(prompt.agents) == 1
        assert prompt.hooks is not None
        assert len(prompt.hooks) == 1
        assert prompt.mcp_servers is None  # Not provided
        assert prompt.commands is None  # Not provided
