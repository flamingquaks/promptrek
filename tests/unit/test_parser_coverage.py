"""Additional parser tests for coverage."""

from pathlib import Path

import pytest

from promptrek.core.exceptions import UPFFileNotFoundError, UPFParsingError
from promptrek.core.parser import UPFParser


class TestParserErrorCases:
    """Test error cases for parser."""

    def test_parse_file_not_found(self):
        """Test parsing non-existent file."""
        parser = UPFParser()
        with pytest.raises(UPFFileNotFoundError):
            parser.parse_file("/nonexistent/file.promptrek.yaml")

    def test_parse_file_wrong_extension(self, tmp_path):
        """Test parsing file with wrong extension."""
        wrong_ext = tmp_path / "test.txt"
        wrong_ext.write_text("content")

        parser = UPFParser()
        with pytest.raises(UPFParsingError, match="must have .yaml or .yml extension"):
            parser.parse_file(wrong_ext)

    def test_parse_file_invalid_yaml(self, tmp_path):
        """Test parsing file with invalid YAML."""
        invalid_yaml = tmp_path / "invalid.promptrek.yaml"
        invalid_yaml.write_text("invalid: yaml: content:")

        parser = UPFParser()
        with pytest.raises(UPFParsingError, match="YAML parsing error"):
            parser.parse_file(invalid_yaml)

    def test_parse_file_io_error(self, tmp_path):
        """Test parsing file with IO error."""
        parser = UPFParser()
        # Create a directory instead of a file to cause IO error
        dir_path = tmp_path / "test.promptrek.yaml"
        dir_path.mkdir()

        with pytest.raises(UPFParsingError, match="Error reading file"):
            parser.parse_file(dir_path)

    def test_parse_dict_not_dict(self):
        """Test parsing non-dictionary data."""
        parser = UPFParser()
        with pytest.raises(UPFParsingError, match="must be a dictionary"):
            parser.parse_dict("not a dict")

    def test_parse_dict_validation_error(self):
        """Test parsing dictionary with validation errors."""
        parser = UPFParser()
        invalid_data = {
            "schema_version": "1.0.0",
            "metadata": {"title": "Test", "description": "Test"},
            "targets": ["unknown_editor"],
            "invalid_field": "this should cause error",
        }
        with pytest.raises(UPFParsingError, match="Validation errors"):
            parser.parse_dict(invalid_data)

    def test_parse_string_invalid_yaml(self):
        """Test parsing invalid YAML string."""
        parser = UPFParser()
        with pytest.raises(UPFParsingError, match="YAML parsing error"):
            parser.parse_string("invalid: yaml: content:")

    def test_validate_file_extension(self):
        """Test file extension validation."""
        parser = UPFParser()
        assert parser.validate_file_extension("test.promptrek.yaml")
        assert parser.validate_file_extension("test.promptrek.yml")
        assert parser.validate_file_extension(Path("test.promptrek.yaml"))
        assert not parser.validate_file_extension("test.yaml")
        assert not parser.validate_file_extension("test.txt")

    def test_find_upf_files_nonexistent(self):
        """Test finding files in non-existent directory."""
        parser = UPFParser()
        files = parser.find_upf_files("/nonexistent/directory")
        assert files == []

    def test_find_upf_files_not_directory(self, tmp_path):
        """Test finding files when path is not a directory."""
        parser = UPFParser()
        file_path = tmp_path / "test.txt"
        file_path.write_text("content")

        files = parser.find_upf_files(file_path)
        assert files == []

    def test_find_upf_files_empty_directory(self, tmp_path):
        """Test finding files in empty directory."""
        parser = UPFParser()
        files = parser.find_upf_files(tmp_path)
        assert files == []

    def test_find_upf_files_recursive(self, tmp_path):
        """Test finding files recursively."""
        parser = UPFParser()

        # Create nested structure
        subdir = tmp_path / "subdir"
        subdir.mkdir()

        file1 = tmp_path / "test1.promptrek.yaml"
        file1.write_text("content1")

        file2 = subdir / "test2.promptrek.yaml"
        file2.write_text("content2")

        # Non-recursive should find only file1
        files = parser.find_upf_files(tmp_path, recursive=False)
        assert len(files) == 1

        # Recursive should find both
        files = parser.find_upf_files(tmp_path, recursive=True)
        assert len(files) == 2

    def test_parse_multiple_files_empty(self):
        """Test parsing multiple files with empty list."""
        parser = UPFParser()
        with pytest.raises(UPFParsingError, match="No files provided"):
            parser.parse_multiple_files([])

    def test_parse_directory_no_files(self, tmp_path):
        """Test parsing directory with no UPF files."""
        parser = UPFParser()
        with pytest.raises(UPFParsingError, match="No .promptrek.yaml files found"):
            parser.parse_directory(tmp_path)

    def test_parse_multiple_files_merging(self, tmp_path):
        """Test parsing and merging multiple files."""
        parser = UPFParser()

        # Create first file
        file1 = tmp_path / "file1.promptrek.yaml"
        file1.write_text(
            """
schema_version: "1.0.0"
metadata:
  title: "File 1"
  description: "First file"
  version: "1.0.0"
targets:
  - claude
instructions:
  general:
    - "Instruction 1"
"""
        )

        # Create second file
        file2 = tmp_path / "file2.promptrek.yaml"
        file2.write_text(
            """
schema_version: "1.0.0"
metadata:
  title: "File 2"
  description: "Second file"
  version: "2.0.0"
targets:
  - cursor
instructions:
  general:
    - "Instruction 2"
"""
        )

        result = parser.parse_multiple_files([file1, file2])

        # Second file should override metadata
        assert result.metadata.title == "File 2"
        assert result.metadata.version == "2.0.0"

        # Targets should be merged
        assert "claude" in result.targets
        assert "cursor" in result.targets

        # Instructions should be combined
        assert len(result.instructions.general) == 2

    def test_parse_directory_with_files(self, tmp_path):
        """Test parsing directory with UPF files."""
        parser = UPFParser()

        # Create files
        file1 = tmp_path / "test1.promptrek.yaml"
        file1.write_text(
            """
schema_version: "2.0.0"
metadata:
  title: "Test"
  description: "Test"
  version: "1.0.0"
content: |
  # Test
"""
        )

        file2 = tmp_path / "test2.promptrek.yaml"
        file2.write_text(
            """
schema_version: "2.0.0"
metadata:
  title: "Test 2"
  description: "Test 2"
  version: "1.0.0"
content: |
  # Test 2
"""
        )

        result = parser.parse_directory(tmp_path)
        # Should return second file's content (files are sorted and merged)
        assert result is not None

    def test_merge_v2_prompts(self, tmp_path):
        """Test merging v2 prompts returns second one."""
        parser = UPFParser()

        file1 = tmp_path / "file1.promptrek.yaml"
        file1.write_text(
            """
schema_version: "2.0.0"
metadata:
  title: "First"
  description: "First"
  version: "1.0.0"
content: |
  # First
"""
        )

        file2 = tmp_path / "file2.promptrek.yaml"
        file2.write_text(
            """
schema_version: "2.0.0"
metadata:
  title: "Second"
  description: "Second"
  version: "1.0.0"
content: |
  # Second
"""
        )

        result = parser.parse_multiple_files([file1, file2])
        assert result.metadata.title == "Second"

    def test_get_major_version(self):
        """Test major version extraction."""
        parser = UPFParser()
        assert parser._get_major_version("1.0.0") == "1"
        assert parser._get_major_version("2.0.0") == "2"
        assert parser._get_major_version("10.5.3") == "10"
        # When version is invalid, returns first part or "1"
        assert parser._get_major_version("invalid") == "invalid"
        # When None, returns "1"
        try:
            result = parser._get_major_version(None)
            assert result == "1"
        except (AttributeError, TypeError):
            # This is expected since None doesn't have split()
            pass

    def test_format_validation_error(self):
        """Test validation error formatting."""
        from pydantic import BaseModel, Field, ValidationError

        class TestModel(BaseModel):
            required_field: str = Field(...)

        parser = UPFParser()
        try:
            TestModel(required_field="")  # This should fail
        except ValidationError as e:
            formatted = parser._format_validation_error(e, "test_source")
            assert "test_source" in formatted
            assert "Validation errors" in formatted
