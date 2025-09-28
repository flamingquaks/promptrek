"""Unit tests for UPF parser."""

import pytest
import yaml

from promptrek.core.exceptions import UPFFileNotFoundError, UPFParsingError
from promptrek.core.models import UniversalPrompt
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
            "metadata": {"title": "Project 1", "description": "First project", "version": "1.0", "author": "Test Author"},
            "instructions": {"general": ["Rule 1", "Rule 2"]},
            "context": {"technologies": ["python"]},
            "targets": ["editor1"]
        }
        file1 = tmp_path / "first.promptrek.yaml"
        file1.write_text(yaml.dump(data1))

        # Create second file
        data2 = {
            "schema_version": "1.0.0",
            "metadata": {"title": "Project 2", "description": "Second project", "version": "1.0", "author": "Test Author"},
            "instructions": {"general": ["Rule 3"], "code_style": ["Style 1"]},
            "context": {"technologies": ["javascript"]},
            "targets": ["editor2"]
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
            "metadata": {"title": "Base Project", "version": "1.0", "author": "Test Author"},
            "instructions": {"general": ["Base rule"]},
            "targets": ["editor1"]
        }
        (tmp_path / "base.promptrek.yaml").write_text(yaml.dump(data1))

        data2 = {
            "schema_version": "1.0.0",
            "metadata": {"title": "Additional Project", "version": "1.0", "author": "Test Author"},
            "instructions": {"general": ["Additional rule"]},
            "targets": ["editor2"]
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
            "metadata": {"title": "Base", "version": "1.0", "author": "Test Author"},
            "instructions": {"general": ["Base rule"], "testing": ["Test base"]},
            "context": {"technologies": ["python"], "project_type": "api"},
            "variables": {"VAR1": "base_value"},
            "targets": ["editor1"]
        }
        base_prompt = UniversalPrompt(**base_data)

        # Create additional prompt
        additional_data = {
            "schema_version": "1.0.0",
            "metadata": {"title": "Enhanced", "version": "1.0", "author": "Test Author", "description": "Enhanced version"},
            "instructions": {"general": ["Additional rule"], "code_style": ["Style rule"]},
            "context": {"technologies": ["javascript"], "description": "Full stack app"},
            "variables": {"VAR1": "new_value", "VAR2": "additional_value"},
            "targets": ["editor2"]
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
        assert merged.context.description == "Full stack app"  # Additional takes precedence

        # Test variables merging
        assert merged.variables["VAR1"] == "new_value"  # Additional takes precedence
        assert merged.variables["VAR2"] == "additional_value"

        # Test targets merging
        assert len(merged.targets) == 2
        assert "editor1" in merged.targets
        assert "editor2" in merged.targets
