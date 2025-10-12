"""Tests for import system."""

import pytest
from pathlib import Path
from promptrek.utils.imports import ImportProcessor
from promptrek.core.parser import UPFParser
from promptrek.core.models import UniversalPrompt, PromptMetadata, Instructions, ImportConfig


class TestImportProcessor:
    """Test import processing functionality."""

    @pytest.fixture
    def processor(self):
        return ImportProcessor()

    def test_process_imports_no_imports(self, processor, tmp_path):
        """Test processing prompt with no imports."""
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["claude"],
            instructions=Instructions(general=["Test"])
        )

        result = processor.process_imports(prompt, tmp_path)

        assert result == prompt

    def test_process_imports_with_import(self, processor, tmp_path):
        """Test processing prompt with imports."""
        # Create an imported file
        imported_file = tmp_path / "imported.promptrek.yaml"
        imported_file.write_text("""schema_version: 1.0.0
metadata:
  title: Imported
  description: Imported prompt
targets:
  - claude
instructions:
  general:
    - Imported instruction
""")

        # Create main prompt with import
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Main", description="Main"),
            targets=["claude"],
            instructions=Instructions(general=["Main instruction"]),
            imports=[
                ImportConfig(path="imported.promptrek.yaml")
            ]
        )

        result = processor.process_imports(prompt, tmp_path)

        # Result should have merged instructions
        assert len(result.instructions.general) > 1


    def test_process_imports_with_prefix(self, processor, tmp_path):
        """Test processing imports with prefix."""
        # Create an imported file
        imported_file = tmp_path / "imported.promptrek.yaml"
        imported_file.write_text("""schema_version: 1.0.0
metadata:
  title: Imported
  description: Imported prompt
targets:
  - claude
instructions:
  general:
    - Imported instruction
""")

        # Create main prompt with import that has prefix
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Main", description="Main"),
            targets=["claude"],
            instructions=Instructions(general=["Main instruction"]),
            imports=[
                ImportConfig(path="imported.promptrek.yaml", prefix="[IMPORTED]")
            ]
        )

        result = processor.process_imports(prompt, tmp_path)

        # Result should have prefixed instructions
        assert any("[IMPORTED]" in str(inst) for inst in result.instructions.general)

    def test_process_imports_file_not_found(self, processor, tmp_path):
        """Test importing non-existent file."""
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Main", description="Main"),
            targets=["claude"],
            instructions=Instructions(general=["Main instruction"]),
            imports=[
                ImportConfig(path="nonexistent.promptrek.yaml")
            ]
        )

        # Should raise an error
        with pytest.raises(Exception):
            processor.process_imports(prompt, tmp_path)
