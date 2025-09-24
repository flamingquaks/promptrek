"""Unit tests for UPF parser."""

import pytest
import yaml

from apm.core.exceptions import UPFFileNotFoundError, UPFParsingError
from apm.core.models import UniversalPrompt
from apm.core.parser import UPFParser


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
            parser.parse_file("nonexistent.apm.yaml")

    def test_parse_invalid_extension(self, tmp_path):
        """Test parsing file with invalid extension raises error."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("content")

        parser = UPFParser()
        with pytest.raises(UPFParsingError):
            parser.parse_file(file_path)

    def test_parse_invalid_yaml(self, tmp_path):
        """Test parsing invalid YAML raises error."""
        file_path = tmp_path / "invalid.apm.yaml"
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

        assert parser.validate_file_extension("test.apm.yaml") is True
        assert parser.validate_file_extension("test.apm.yml") is True
        assert parser.validate_file_extension("test.yaml") is False
        assert parser.validate_file_extension("test.txt") is False

    def test_find_upf_files(self, tmp_path, sample_upf_data):
        """Test finding UPF files in directory."""
        # Create test files
        (tmp_path / "project.apm.yaml").write_text(yaml.dump(sample_upf_data))
        (tmp_path / "config.apm.yml").write_text(yaml.dump(sample_upf_data))
        (tmp_path / "other.yaml").write_text("not upf")

        parser = UPFParser()
        upf_files = parser.find_upf_files(tmp_path)

        assert len(upf_files) == 2
        file_names = [f.name for f in upf_files]
        assert "project.apm.yaml" in file_names
        assert "config.apm.yml" in file_names

    def test_find_upf_files_recursive(self, tmp_path, sample_upf_data):
        """Test finding UPF files recursively."""
        # Create nested structure
        subdir = tmp_path / "subdir"
        subdir.mkdir()

        (tmp_path / "root.apm.yaml").write_text(yaml.dump(sample_upf_data))
        (subdir / "nested.apm.yaml").write_text(yaml.dump(sample_upf_data))

        parser = UPFParser()

        # Non-recursive should find only root file
        files = parser.find_upf_files(tmp_path, recursive=False)
        assert len(files) == 1

        # Recursive should find both files
        files = parser.find_upf_files(tmp_path, recursive=True)
        assert len(files) == 2
