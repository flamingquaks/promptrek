"""Tests for import system."""

from pathlib import Path

import pytest

from promptrek.core.models import (
    ImportConfig,
    Instructions,
    PromptMetadata,
    UniversalPrompt,
)
from promptrek.core.parser import UPFParser
from promptrek.utils.imports import ImportProcessor


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
            instructions=Instructions(general=["Test"]),
        )

        result = processor.process_imports(prompt, tmp_path)

        assert result == prompt

    def test_process_imports_with_import(self, processor, tmp_path):
        """Test processing prompt with imports."""
        # Create an imported file
        imported_file = tmp_path / "imported.promptrek.yaml"
        imported_file.write_text(
            """schema_version: 1.0.0
metadata:
  title: Imported
  description: Imported prompt
targets:
  - claude
instructions:
  general:
    - Imported instruction
"""
        )

        # Create main prompt with import
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Main", description="Main"),
            targets=["claude"],
            instructions=Instructions(general=["Main instruction"]),
            imports=[ImportConfig(path="imported.promptrek.yaml")],
        )

        result = processor.process_imports(prompt, tmp_path)

        # Result should have merged instructions
        assert len(result.instructions.general) > 1

    def test_process_imports_with_prefix(self, processor, tmp_path):
        """Test processing imports with prefix."""
        # Create an imported file
        imported_file = tmp_path / "imported.promptrek.yaml"
        imported_file.write_text(
            """schema_version: 1.0.0
metadata:
  title: Imported
  description: Imported prompt
targets:
  - claude
instructions:
  general:
    - Imported instruction
"""
        )

        # Create main prompt with import that has prefix
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Main", description="Main"),
            targets=["claude"],
            instructions=Instructions(general=["Main instruction"]),
            imports=[ImportConfig(path="imported.promptrek.yaml", prefix="[IMPORTED]")],
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
            imports=[ImportConfig(path="nonexistent.promptrek.yaml")],
        )

        # Should raise an error
        with pytest.raises(Exception):
            processor.process_imports(prompt, tmp_path)

    def test_process_imports_with_examples(self, processor, tmp_path):
        """Test processing imports with examples."""
        # Create an imported file with examples
        imported_file = tmp_path / "imported.promptrek.yaml"
        imported_file.write_text(
            """schema_version: 1.0.0
metadata:
  title: Imported
  description: Imported prompt
targets:
  - claude
examples:
  example1: "Code example 1"
  example2: "Code example 2"
"""
        )

        # Create main prompt with import
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Main", description="Main"),
            targets=["claude"],
            instructions=Instructions(general=["Main instruction"]),
            imports=[ImportConfig(path="imported.promptrek.yaml")],
        )

        result = processor.process_imports(prompt, tmp_path)

        # Result should have merged examples
        assert result.examples is not None
        assert "example1" in result.examples
        assert "example2" in result.examples

    def test_process_imports_with_examples_and_prefix(self, processor, tmp_path):
        """Test processing imports with examples and prefix."""
        # Create an imported file with examples
        imported_file = tmp_path / "imported.promptrek.yaml"
        imported_file.write_text(
            """schema_version: 1.0.0
metadata:
  title: Imported
  description: Imported prompt
targets:
  - claude
examples:
  example1: "Code example 1"
"""
        )

        # Create main prompt with import and prefix
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Main", description="Main"),
            targets=["claude"],
            instructions=Instructions(general=["Main instruction"]),
            imports=[ImportConfig(path="imported.promptrek.yaml", prefix="imported")],
        )

        result = processor.process_imports(prompt, tmp_path)

        # Result should have prefixed examples
        assert result.examples is not None
        assert "imported_example1" in result.examples

    def test_process_imports_with_variables(self, processor, tmp_path):
        """Test processing imports with variables."""
        # Create an imported file with variables
        imported_file = tmp_path / "imported.promptrek.yaml"
        imported_file.write_text(
            """schema_version: 1.0.0
metadata:
  title: Imported
  description: Imported prompt
targets:
  - claude
variables:
  VAR1: "value1"
  VAR2: "value2"
"""
        )

        # Create main prompt with import
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Main", description="Main"),
            targets=["claude"],
            instructions=Instructions(general=["Main instruction"]),
            imports=[ImportConfig(path="imported.promptrek.yaml")],
        )

        result = processor.process_imports(prompt, tmp_path)

        # Result should have merged variables
        assert result.variables is not None
        assert "VAR1" in result.variables
        assert "VAR2" in result.variables

    def test_process_imports_with_variables_and_prefix(self, processor, tmp_path):
        """Test processing imports with variables and prefix."""
        # Create an imported file with variables
        imported_file = tmp_path / "imported.promptrek.yaml"
        imported_file.write_text(
            """schema_version: 1.0.0
metadata:
  title: Imported
  description: Imported prompt
targets:
  - claude
variables:
  VAR1: "value1"
"""
        )

        # Create main prompt with import and prefix
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Main", description="Main"),
            targets=["claude"],
            instructions=Instructions(general=["Main instruction"]),
            variables={"EXISTING_VAR": "existing"},
            imports=[ImportConfig(path="imported.promptrek.yaml", prefix="imported")],
        )

        result = processor.process_imports(prompt, tmp_path)

        # Result should have prefixed variables
        assert result.variables is not None
        assert "imported_VAR1" in result.variables
        assert "EXISTING_VAR" in result.variables

    def test_merge_instructions_with_new_category(self, processor, tmp_path):
        """Test merging instructions with new category."""
        # Create an imported file with new instruction category
        imported_file = tmp_path / "imported.promptrek.yaml"
        imported_file.write_text(
            """schema_version: 1.0.0
metadata:
  title: Imported
  description: Imported prompt
targets:
  - claude
instructions:
  security:
    - Security instruction 1
"""
        )

        # Create main prompt without security instructions
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Main", description="Main"),
            targets=["claude"],
            instructions=Instructions(general=["Main instruction"]),
            imports=[ImportConfig(path="imported.promptrek.yaml")],
        )

        result = processor.process_imports(prompt, tmp_path)

        # Result should have security category
        assert result.instructions.security is not None
        assert len(result.instructions.security) == 1

    def test_import_v2_file_error(self, processor, tmp_path):
        """Test importing v2 file raises error."""
        # Create a v2 format file
        v2_file = tmp_path / "v2.promptrek.yaml"
        v2_file.write_text(
            """schema_version: 2.0.0
metadata:
  title: V2 File
  description: V2 format
content: |
  # V2 Content
  This is v2 format
"""
        )

        # Create v1 file that tries to import v2
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Main", description="Main"),
            targets=["claude"],
            imports=[ImportConfig(path="v2.promptrek.yaml")],
        )

        from promptrek.core.exceptions import UPFParsingError

        with pytest.raises(UPFParsingError, match="Cannot import v2/v3"):
            processor.process_imports(prompt, tmp_path)

    def test_recursive_imports(self, processor, tmp_path):
        """Test recursive import processing."""
        # Create a chain: main -> level1 -> level2
        level2 = tmp_path / "level2.promptrek.yaml"
        level2.write_text(
            """schema_version: 1.0.0
metadata:
  title: Level2
  description: Level2
targets:
  - claude
instructions:
  general:
    - Level2 instruction
"""
        )

        level1 = tmp_path / "level1.promptrek.yaml"
        level1.write_text(
            """schema_version: 1.0.0
metadata:
  title: Level1
  description: Level1
targets:
  - claude
instructions:
  general:
    - Level1 instruction
imports:
  - path: level2.promptrek.yaml
"""
        )

        # Main file imports level1
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Main", description="Main"),
            targets=["claude"],
            instructions=Instructions(general=["Main instruction"]),
            imports=[ImportConfig(path="level1.promptrek.yaml")],
        )

        result = processor.process_imports(prompt, tmp_path)

        # Should have all three levels merged
        assert len(result.instructions.general) == 3

    def test_import_creates_empty_instruction_category(self, processor, tmp_path):
        """Test that importing creates empty category when base has None."""
        # Create an imported file
        imported_file = tmp_path / "imported.promptrek.yaml"
        imported_file.write_text(
            """schema_version: 1.0.0
metadata:
  title: Imported
  description: Imported prompt
targets:
  - claude
instructions:
  testing:
    - Imported test instruction
"""
        )

        # Create main prompt with instructions but testing = None
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Main", description="Main"),
            targets=["claude"],
            instructions=Instructions(general=["Main"]),
            imports=[ImportConfig(path="imported.promptrek.yaml")],
        )

        result = processor.process_imports(prompt, tmp_path)

        # Should have both general and testing instructions
        assert len(result.instructions.general) == 1
        assert result.instructions.testing is not None
        assert len(result.instructions.testing) == 1

    def test_circular_import_detection(self, processor, tmp_path):
        """Test that circular imports are detected."""
        # Create a simple file
        simple_file = tmp_path / "simple.promptrek.yaml"
        simple_file.write_text(
            """schema_version: 1.0.0
metadata:
  title: Simple
  description: Simple
targets:
  - claude
instructions:
  general:
    - Simple instruction
"""
        )

        from promptrek.core.exceptions import UPFParsingError

        # Manually add the same file to _processed_files to simulate circular import
        import_path = simple_file.resolve()
        processor._processed_files.add(import_path)

        # Now try to import it again - should detect circular import
        import_config = ImportConfig(path="simple.promptrek.yaml")

        with pytest.raises(UPFParsingError, match="Circular import"):
            processor._process_single_import(import_config, tmp_path)

    def test_import_new_instruction_category_when_base_has_no_category(
        self, processor, tmp_path
    ):
        """Test importing new category when base instructions exist but category doesn't."""
        # Create an imported file with security instructions
        imported_file = tmp_path / "imported.promptrek.yaml"
        imported_file.write_text(
            """schema_version: 1.0.0
metadata:
  title: Imported
  description: Imported prompt
targets:
  - claude
instructions:
  performance:
    - Performance instruction
"""
        )

        # Create main prompt with general but no performance
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Main", description="Main"),
            targets=["claude"],
            instructions=Instructions(general=["Main"]),
            imports=[ImportConfig(path="imported.promptrek.yaml")],
        )

        result = processor.process_imports(prompt, tmp_path)

        # Should have both general and performance
        assert result.instructions.general is not None
        assert result.instructions.performance is not None
        assert len(result.instructions.performance) == 1

    def test_import_when_base_has_no_instructions_field(self, processor, tmp_path):
        """Test importing instructions when base has no instructions field at all."""
        # Create an imported file with instructions
        imported_file = tmp_path / "imported.promptrek.yaml"
        imported_file.write_text(
            """schema_version: 1.0.0
metadata:
  title: Imported
  description: Imported prompt
targets:
  - claude
instructions:
  general:
    - Imported instruction
"""
        )

        # Create main prompt without instructions (model_construct to avoid validation)
        prompt = UniversalPrompt.model_construct(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Main", description="Main"),
            targets=["claude"],
            instructions=None,  # Explicitly None
            imports=[ImportConfig(path="imported.promptrek.yaml")],
        )

        result = processor.process_imports(prompt, tmp_path)

        # Should have instructions from import
        assert result.instructions is not None
        assert result.instructions.general is not None
        assert len(result.instructions.general) == 1

    def test_import_context_when_base_has_none(self, processor, tmp_path):
        """Test importing context field when base has context=None."""
        # Create an imported file with context
        imported_file = tmp_path / "imported.promptrek.yaml"
        imported_file.write_text(
            """schema_version: 1.0.0
metadata:
  title: Imported
  description: Imported prompt
targets:
  - claude
context:
  project_type: web_application
  technologies:
    - Python
    - FastAPI
"""
        )

        # Create main prompt without context
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Main", description="Main"),
            targets=["claude"],
            instructions=Instructions(general=["Main"]),
            imports=[ImportConfig(path="imported.promptrek.yaml")],
        )

        result = processor.process_imports(prompt, tmp_path)

        # Should have context from import
        assert result.context is not None
        assert result.context.project_type == "web_application"
        assert "Python" in result.context.technologies
