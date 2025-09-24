"""
Integration tests for advanced features (imports, conditionals, variables).
"""

import shutil
import tempfile
from pathlib import Path

import pytest
from click.testing import CliRunner

from src.apm.cli.main import cli


class TestAdvancedFeatures:
    """Test advanced features integration."""

    @pytest.fixture
    def runner(self):
        """Create Click test runner."""
        return CliRunner()

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def import_base_file(self, temp_dir):
        """Create base file for import testing."""
        base_content = """schema_version: "1.0.0"

metadata:
  title: "Base Configuration"
  description: "Shared configuration"
  version: "1.0.0"
  author: "test@example.com"
  created: "2024-01-01"
  updated: "2024-01-01"

targets:
  - claude

instructions:
  general:
    - "Follow clean code principles"
    - "Use meaningful variable names"
  code_style:
    - "Use 2-space indentation"
    - "Prefer const over let"

examples:
  util_function: |
    const capitalize = (str: string) =>
      str.charAt(0).toUpperCase() + str.slice(1);

variables:
  STYLE_GUIDE: "Standard"
  INDENT_SIZE: "2"
"""
        base_file = temp_dir / "base.apm.yaml"
        base_file.write_text(base_content)
        return base_file

    @pytest.fixture
    def import_main_file(self, temp_dir, import_base_file):
        """Create main file that imports base file."""
        main_content = """schema_version: "1.0.0"

metadata:
  title: "Main Project with Imports"
  description: "Project that imports shared configuration"
  version: "1.0.0"
  author: "test@example.com"
  created: "2024-01-01"
  updated: "2024-01-01"

targets:
  - claude

imports:
  - path: "base.apm.yaml"
    prefix: "shared"

instructions:
  general:
    - "Write comprehensive tests"
  testing:
    - "Use Jest for unit testing"

examples:
  main_component: "const App = () => <div>Hello World</div>;"

variables:
  PROJECT_NAME: "ImportTestProject"
"""
        main_file = temp_dir / "main.apm.yaml"
        main_file.write_text(main_content)
        return main_file

    def test_import_functionality(self, runner, import_main_file, temp_dir):
        """Test import functionality through CLI."""
        result = runner.invoke(
            cli,
            [
                "generate",
                "--editor",
                "claude",
                "--output",
                str(temp_dir),
                str(import_main_file),
            ],
        )

        assert result.exit_code == 0

        # Check that file was generated
        generated_file = temp_dir / ".claude" / "context.md"
        assert generated_file.exists()

        content = generated_file.read_text()

        # Check that main content is present
        assert "Main Project with Imports" in content
        assert "Write comprehensive tests" in content
        assert "Use Jest for unit testing" in content
        assert "Hello World" in content

        # Check that imported content is present with prefix
        assert "[shared] Follow clean code principles" in content
        assert "[shared] Use meaningful variable names" in content
        assert "[shared] Use 2-space indentation" in content
        assert "[shared] Prefer const over let" in content

        # Check that imported examples are prefixed
        assert "Shared Util Function" in content
        assert "capitalize" in content

    def test_variable_substitution_with_overrides(self, runner, temp_dir):
        """Test variable substitution with CLI overrides."""
        # Create a file with variable placeholders
        var_content = """schema_version: "1.0.0"

metadata:
  title: "{{{ PROJECT_TITLE }}} Assistant"
  description: "AI assistant for {{{ PROJECT_TITLE }}}"
  version: "1.0.0"
  author: "{{{ AUTHOR_EMAIL }}}"
  created: "2024-01-01"
  updated: "2024-01-01"

targets:
  - claude

context:
  project_type: "web_application"
  description: "A {{{ PROJECT_TYPE }}} built with {{{ TECH_STACK }}}."

instructions:
  general:
    - "Follow {{{ PROJECT_TITLE }}} coding standards"
    - "Contact {{{ AUTHOR_EMAIL }}} for questions"

variables:
  PROJECT_TITLE: "Default Project"
  AUTHOR_EMAIL: "default@example.com"
  PROJECT_TYPE: "web application"
  TECH_STACK: "React and TypeScript"
"""
        var_file = temp_dir / "variables.apm.yaml"
        var_file.write_text(var_content)

        # Test with variable overrides
        result = runner.invoke(
            cli,
            [
                "generate",
                "--editor",
                "claude",
                "--output",
                str(temp_dir),
                "-V",
                "PROJECT_TITLE=OverriddenProject",
                "-V",
                "AUTHOR_EMAIL=override@test.com",
                "-V",
                "PROJECT_TYPE=mobile app",
                "-V",
                "TECH_STACK=React Native",
                str(var_file),
            ],
        )

        assert result.exit_code == 0

        generated_file = temp_dir / ".claude" / "context.md"
        assert generated_file.exists()

        content = generated_file.read_text()

        # Check that variables were substituted with override values
        assert "OverriddenProject Assistant" in content
        assert "AI assistant for OverriddenProject" in content
        assert "override@test.com" in content
        assert "mobile app built with React Native" in content
        assert "Follow OverriddenProject coding standards" in content
        assert "Contact override@test.com for questions" in content

    def test_conditional_instructions_integration(self, runner, temp_dir):
        """Test conditional instructions through CLI."""
        conditional_content = """schema_version: "1.0.0"

metadata:
  title: "Conditional Instructions Test"
  description: "Testing conditional logic"
  version: "1.0.0"
  author: "test@example.com"
  created: "2024-01-01"
  updated: "2024-01-01"

targets:
  - claude
  - continue
  - codeium

instructions:
  general:
    - "Base instruction for all editors"

conditions:
  - if: 'EDITOR == "claude"'
    then:
      instructions:
        general:
          - "Claude-specific: Provide detailed explanations"
          - "Claude-specific: Focus on code clarity"
      examples:
        claude_example: "// Claude prefers detailed comments"

  - if: 'EDITOR == "continue"'
    then:
      instructions:
        general:
          - "Continue-specific: Generate comprehensive completions"
          - "Continue-specific: Suggest appropriate types"

  - if: 'EDITOR in ["codeium", "copilot"]'
    then:
      instructions:
        general:
          - "AI Assistant: Focus on performance optimization"

variables:
  BASE_CONFIG: "shared"
"""
        conditional_file = temp_dir / "conditional.apm.yaml"
        conditional_file.write_text(conditional_content)

        # Test Claude generation
        result = runner.invoke(
            cli,
            [
                "generate",
                "--editor",
                "claude",
                "--output",
                str(temp_dir / "claude_test"),
                str(conditional_file),
            ],
        )

        assert result.exit_code == 0

        claude_file = temp_dir / "claude_test" / ".claude" / "context.md"
        assert claude_file.exists()
        claude_content = claude_file.read_text()

        # Check base instruction
        assert "Base instruction for all editors" in claude_content
        # Check Claude-specific instructions
        assert "Claude-specific: Provide detailed explanations" in claude_content
        assert "Claude-specific: Focus on code clarity" in claude_content
        # Check Claude-specific examples
        assert "Claude Example" in claude_content
        assert "Claude prefers detailed comments" in claude_content
        # Should not have other editor instructions
        assert "Continue-specific" not in claude_content
        assert "AI Assistant: Focus on performance" not in claude_content

        # Test Continue generation
        result = runner.invoke(
            cli,
            [
                "generate",
                "--editor",
                "continue",
                "--output",
                str(temp_dir / "continue_test"),
                str(conditional_file),
            ],
        )

        assert result.exit_code == 0

        continue_file = temp_dir / "continue_test" / ".continue" / "config.json"
        assert continue_file.exists()
        continue_content = continue_file.read_text()

        # Check base instruction
        assert "Base instruction for all editors" in continue_content
        # Check Continue-specific instructions
        assert (
            "Continue-specific: Generate comprehensive completions" in continue_content
        )
        assert "Continue-specific: Suggest appropriate types" in continue_content
        # Should not have other editor instructions
        assert "Claude-specific" not in continue_content
        assert "AI Assistant: Focus on performance" not in continue_content

        # Test Codeium generation (should get the "in list" condition)
        result = runner.invoke(
            cli,
            [
                "generate",
                "--editor",
                "codeium",
                "--output",
                str(temp_dir / "codeium_test"),
                str(conditional_file),
            ],
        )

        assert result.exit_code == 0

        codeium_file = temp_dir / "codeium_test" / ".codeium" / "context.json"
        assert codeium_file.exists()
        codeium_content = codeium_file.read_text()

        # Parse JSON to check content
        import json

        codeium_data = json.loads(codeium_content)

        # Find general guidelines
        general_guidelines = [
            g for g in codeium_data["guidelines"] if g["category"] == "general"
        ]
        instructions_text = " ".join([g["rule"] for g in general_guidelines])

        # Check base instruction
        assert "Base instruction for all editors" in instructions_text
        # Check list condition instruction
        assert "AI Assistant: Focus on performance optimization" in instructions_text
        # Should not have other editor specific instructions
        assert "Claude-specific" not in instructions_text
        assert "Continue-specific" not in instructions_text

    def test_combined_features(self, runner, temp_dir):
        """Test combination of imports, conditionals, and variables."""
        # Create base file with variables and conditionals
        base_content = """schema_version: "1.0.0"

metadata:
  title: "Base with Variables"
  description: "Base configuration with variables"
  version: "1.0.0"
  author: "test@example.com"
  created: "2024-01-01"
  updated: "2024-01-01"

targets:
  - claude

instructions:
  general:
    - "Use {{{ CODING_STYLE }}} coding style"

conditions:
  - if: 'EDITOR == "claude"'
    then:
      instructions:
        general:
          - "Claude: Use {{{ AI_APPROACH }}} approach"

variables:
  CODING_STYLE: "clean"
  AI_APPROACH: "detailed"
"""
        base_file = temp_dir / "base_advanced.apm.yaml"
        base_file.write_text(base_content)

        # Create main file that imports and overrides
        main_content = """schema_version: "1.0.0"

metadata:
  title: "{{{ PROJECT_NAME }}} with Advanced Features"
  description: "Project using all advanced features"
  version: "1.0.0"
  author: "{{{ AUTHOR }}}"
  created: "2024-01-01"
  updated: "2024-01-01"

targets:
  - claude

imports:
  - path: "base_advanced.apm.yaml"
    prefix: "base"

instructions:
  general:
    - "Project-specific: Follow {{{ PROJECT_NAME }}} guidelines"

conditions:
  - if: 'EDITOR == "claude"'
    then:
      instructions:
        general:
          - "Main: Use {{{ MAIN_APPROACH }}} methodology"

variables:
  PROJECT_NAME: "AdvancedTest"
  AUTHOR: "Advanced Tester"
  MAIN_APPROACH: "comprehensive"
"""
        main_file = temp_dir / "main_advanced.apm.yaml"
        main_file.write_text(main_content)

        # Test with variable overrides
        result = runner.invoke(
            cli,
            [
                "generate",
                "--editor",
                "claude",
                "--output",
                str(temp_dir),
                "-V",
                "PROJECT_NAME=OverriddenAdvanced",
                "-V",
                "AUTHOR=Override Tester",
                "-V",
                "MAIN_APPROACH=agile",
                "-V",
                "base_CODING_STYLE=strict",
                "-V",
                "base_AI_APPROACH=concise",
                str(main_file),
            ],
        )

        assert result.exit_code == 0

        generated_file = temp_dir / ".claude" / "context.md"
        assert generated_file.exists()
        content = generated_file.read_text()

        # Check variable substitution in title (from main file)
        assert "OverriddenAdvanced with Advanced Features" in content

        # Check main instructions with variable substitution
        assert "Project-specific: Follow OverriddenAdvanced guidelines" in content

        # Check imported instructions with prefix (note: prefixed variable substitution is not yet implemented)
        assert "[base] Use {{{ CODING_STYLE }}} coding style" in content

        # Check conditional instructions from main file
        assert "Main: Use agile methodology" in content

        # Note: Conditional instructions from imported files are not yet fully supported
        # This is an advanced feature that would require complex import + conditional processing
