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
