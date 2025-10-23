"""
Unit tests for Continue adapter.
"""

from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from promptrek.adapters.continue_adapter import ContinueAdapter
from promptrek.core.models import PromptMetadata, UniversalPrompt

from .base_test import TestAdapterBase


class TestContinueAdapter(TestAdapterBase):
    """Test Continue editor adapter."""

    @pytest.fixture
    def adapter(self):
        """Create Continue adapter instance."""
        return ContinueAdapter()

    def test_init(self, adapter):
        """Test adapter initialization."""
        assert adapter.name == "continue"
        assert adapter.description == "Continue (.continue/rules/)"
        assert adapter.file_patterns == [".continue/rules/*.md"]

    def test_supports_variables(self, adapter):
        """Test variable support."""
        assert adapter.supports_variables() is True

    def test_supports_conditionals(self, adapter):
        """Test conditional support."""
        assert adapter.supports_conditionals() is True

    def test_validate_valid_prompt(self, adapter, sample_prompt):
        """Test validation of valid prompt."""
        errors = adapter.validate(sample_prompt)
        assert len(errors) == 0

    def test_validate_missing_description(self, adapter):
        """Test validation with missing description."""
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(
                title="Test",
                description="",  # Empty description
                version="1.0.0",
                author="test@example.com",
                created="2024-01-01",
                updated="2024-01-01",
            ),
            targets=["continue"],
        )
        errors = adapter.validate(prompt)
        assert len(errors) == 1
        assert errors[0].field == "metadata.description"

    @patch("builtins.open", new_callable=mock_open)
    @patch("pathlib.Path.mkdir")
    def test_generate_actual_files(self, mock_mkdir, mock_file, adapter, sample_prompt):
        """Test actual file generation."""
        output_dir = Path("/tmp/test")
        files = adapter.generate(sample_prompt, output_dir, dry_run=False)

        # Should generate multiple rules files in .continue/rules/
        assert len(files) >= 3  # At least general, code-style, testing
        # Use Path for cross-platform path checking
        file_names = [f.name for f in files]
        assert "general.md" in file_names
        assert "code-style.md" in file_names

        # Check that mkdir and file operations were called
        assert mock_mkdir.called
        assert mock_file.called

    def test_generate_dry_run(self, adapter, sample_prompt, capsys):
        """Test dry run generation."""
        output_dir = Path("/tmp/test")
        files = adapter.generate(sample_prompt, output_dir, dry_run=True)

        captured = capsys.readouterr()
        assert "Would create" in captured.out
        assert len(files) >= 1  # Should generate multiple files

    def test_parse_files_comprehensive(self, adapter, tmp_path):
        """Test comprehensive parsing of Continue files."""
        import yaml

        # Create comprehensive test data
        config_content = {
            "name": "Full Test Assistant",
            "version": "2.0.0",
            "systemMessage": "Full Test Assistant\n\nA comprehensive test configuration",
            "rules": [
                "Write comprehensive tests",
                "Use descriptive names",
                "Handle errors gracefully",
            ],
        }

        config_file = tmp_path / "config.yaml"
        with open(config_file, "w") as f:
            yaml.dump(config_content, f)

        # Create multiple rule files
        rules_dir = tmp_path / ".continue" / "rules"
        rules_dir.mkdir(parents=True)

        # General rules
        (rules_dir / "general.md").write_text(
            """# General Rules
- Use meaningful variable names
- Follow project conventions
- Document complex logic
"""
        )

        # Code style rules
        (rules_dir / "code-style.md").write_text(
            """# Code Style
- Consistent indentation
- Clear naming conventions
- Avoid magic numbers
"""
        )

        # Testing rules
        (rules_dir / "testing.md").write_text(
            """# Testing Guidelines
- Write unit tests for all functions
- Use descriptive test names
- Mock external dependencies
"""
        )

        # Security rules
        (rules_dir / "security.md").write_text(
            """# Security Guidelines
- Validate all inputs
- Use parameterized queries
- Encrypt sensitive data
"""
        )

        # Performance rules
        (rules_dir / "performance.md").write_text(
            """# Performance Guidelines
- Optimize database queries
- Use caching where appropriate
- Profile before optimizing
"""
        )

        # Architecture rules
        (rules_dir / "architecture.md").write_text(
            """# Architecture Guidelines
- Follow SOLID principles
- Use design patterns appropriately
- Maintain loose coupling
"""
        )

        # Technology-specific rules
        (rules_dir / "python-rules.md").write_text(
            """# Python Rules
- Use type hints
- Follow PEP 8
- Prefer list comprehensions
"""
        )

        # Unknown category should go to general
        (rules_dir / "custom.md").write_text(
            """# Custom Rules
- Custom rule one
- Custom rule two
"""
        )

        # Test parsing (now returns V3 schema)
        parsed = adapter.parse_files(tmp_path)

        # Verify it's V3 schema
        from promptrek.core.models import UniversalPromptV3

        assert isinstance(parsed, UniversalPromptV3)
        assert parsed.schema_version == "3.0.0"

        # Verify metadata
        assert parsed.metadata.title == "Continue AI Assistant"  # V3 uses default title
        assert parsed.metadata.version == "1.0.0"  # Default version for parsed

        # V3 uses documents instead of instructions
        assert parsed.documents is not None
        assert len(parsed.documents) > 0

        # Verify all the markdown files were parsed as documents
        doc_names = [doc.name for doc in parsed.documents]
        assert "architecture" in doc_names
        assert "code-style" in doc_names
        assert "custom" in doc_names
        assert "general" in doc_names
        assert "performance" in doc_names
        assert "python-rules" in doc_names
        assert "security" in doc_names
        assert "testing" in doc_names

        # Verify content from specific documents
        general_doc = next((d for d in parsed.documents if d.name == "general"), None)
        assert general_doc is not None
        assert "Use meaningful variable names" in general_doc.content

        testing_doc = next((d for d in parsed.documents if d.name == "testing"), None)
        assert testing_doc is not None
        assert "Write unit tests for all functions" in testing_doc.content

    def test_parse_files_invalid_yaml(self, adapter, tmp_path):
        """Test parsing with invalid YAML config."""
        # Create invalid YAML
        config_file = tmp_path / "config.yaml"
        config_file.write_text("invalid: yaml: content: [")

        # Should handle gracefully and continue with default values
        parsed = adapter.parse_files(tmp_path)
        assert parsed.metadata.title == "Continue AI Assistant"

    def test_parse_files_malformed_markdown(self, adapter, tmp_path):
        """Test parsing with malformed markdown files."""
        rules_dir = tmp_path / ".continue" / "rules"
        rules_dir.mkdir(parents=True)

        # Create a file that can't be read (simulate permission error)
        general_md = rules_dir / "general.md"
        general_md.write_text("# General\n- Valid rule")

        # Create another markdown file with unusual content
        weird_md = rules_dir / "weird.md"
        weird_md.write_text("No bullet points here\njust random text")

        # Should parse successfully into V3 schema with documents
        parsed = adapter.parse_files(tmp_path)
        from promptrek.core.models import UniversalPromptV3

        assert isinstance(parsed, UniversalPromptV3)

        # Check that both documents were parsed
        doc_names = [doc.name for doc in parsed.documents]
        assert "general" in doc_names
        assert "weird" in doc_names

        # Verify the general document has the expected content
        general_doc = next((d for d in parsed.documents if d.name == "general"), None)
        assert "Valid rule" in general_doc.content

    def test_build_rules_content(self, adapter):
        """Test building markdown rules content."""
        instructions = ["Rule one", "Rule two", "Rule three"]
        content = adapter._build_rules_content("Test Rules", instructions)

        assert "# Test Rules" in content
        assert "- Rule one" in content
        assert "- Rule two" in content
        assert "- Rule three" in content
        assert "## Additional Guidelines" in content

    def test_build_tech_rules_content(self, adapter, sample_prompt):
        """Test building technology-specific rules content."""
        content = adapter._build_tech_rules_content("python", sample_prompt)

        assert "# Python Rules" in content
        assert "## General Guidelines" in content
        assert "## Python Best Practices" in content
        assert (
            "Use strict TypeScript configuration" not in content
        )  # Should not have TS rules

    def test_build_tech_rules_typescript(self, adapter, sample_prompt):
        """Test building TypeScript-specific rules."""
        content = adapter._build_tech_rules_content("typescript", sample_prompt)

        assert "# Typescript Rules" in content
        assert "Use strict TypeScript configuration" in content
        assert "Prefer interfaces over types" in content

    def test_parse_markdown_file_edge_cases(self, adapter, tmp_path):
        """Test markdown parsing edge cases."""
        md_file = tmp_path / "edge_cases.md"
        content = """# Edge Cases

- Normal rule
-Malformed bullet (no space)
- Another normal rule

Not a bullet point

- Rule with trailing spaces
- Rule with "quotes" and symbols!@#

## Some section
Text that's not a bullet

- Final rule
"""
        md_file.write_text(content)

        instructions = adapter._parse_markdown_file(md_file)

        # Should only get properly formatted bullet points
        expected_rules = [
            "Normal rule",
            "Another normal rule",
            "Rule with trailing spaces",
            'Rule with "quotes" and symbols!@#',
            "Final rule",
        ]

        for rule in expected_rules:
            assert rule in instructions

        # Should not include malformed bullets
        assert "Malformed bullet (no space)" not in instructions

    def test_generate_individual_mcp_yaml_files_v3(self, adapter, tmp_path):
        """Test generating individual MCP server YAML files."""
        from promptrek.core.models import MCPServer, PromptMetadata, UniversalPromptV3

        # Create v3 prompt with MCP servers
        prompt = UniversalPromptV3(
            schema_version="3.0.0",
            metadata=PromptMetadata(
                title="Test Project",
                description="Test",
                version="1.0.0",
                author="test",
                created="2024-01-01",
                updated="2024-01-01",
            ),
            content="# Test Project",
            mcp_servers=[
                MCPServer(
                    name="filesystem",
                    command="npx",
                    args=["-y", "@modelcontextprotocol/server-filesystem", "/path"],
                    description="Filesystem access",
                ),
                MCPServer(
                    name="github",
                    command="npx",
                    args=["-y", "@modelcontextprotocol/server-github"],
                    env={"GITHUB_TOKEN": "{{{ GITHUB_TOKEN }}}"},
                    description="GitHub integration",
                ),
            ],
        )

        # Generate files
        files = adapter.generate(
            prompt, tmp_path, dry_run=False, variables={"GITHUB_TOKEN": "test-token"}
        )

        # Check that individual YAML files were created
        mcp_dir = tmp_path / ".continue" / "mcpServers"
        assert mcp_dir.exists()

        filesystem_yaml = mcp_dir / "filesystem.yaml"
        github_yaml = mcp_dir / "github.yaml"

        assert filesystem_yaml in files
        assert github_yaml in files
        assert filesystem_yaml.exists()
        assert github_yaml.exists()

        # Verify filesystem YAML content
        import yaml

        with open(filesystem_yaml, "r") as f:
            fs_content = yaml.safe_load(f)

        assert fs_content["name"] == "Filesystem MCP Server"
        assert fs_content["version"] == "0.0.1"
        assert fs_content["schema"] == "v1"
        assert "mcpServers" in fs_content
        assert len(fs_content["mcpServers"]) == 1
        assert fs_content["mcpServers"][0]["name"] == "filesystem"
        assert fs_content["mcpServers"][0]["command"] == "npx"

        # Verify GitHub YAML content with variable substitution
        with open(github_yaml, "r") as f:
            gh_content = yaml.safe_load(f)

        assert gh_content["name"] == "GitHub MCP Server"
        assert gh_content["mcpServers"][0]["env"]["GITHUB_TOKEN"] == "test-token"

    def test_generate_individual_prompt_markdown_files_v3(self, adapter, tmp_path):
        """Test generating individual prompt markdown files."""
        from promptrek.core.models import Command, PromptMetadata, UniversalPromptV3

        # Create v3 prompt with commands
        prompt = UniversalPromptV3(
            schema_version="3.0.0",
            metadata=PromptMetadata(
                title="Test Project",
                description="Test",
                version="1.0.0",
                author="test",
                created="2024-01-01",
                updated="2024-01-01",
            ),
            content="# Test Project",
            commands=[
                Command(
                    name="refactor",
                    description="Refactor code for better quality",
                    prompt="Refactor the selected code following these principles:\n1. Simplification\n2. Better naming",
                ),
                Command(
                    name="explain",
                    description="Explain how code works",
                    prompt="Provide a clear explanation with {{{ DETAIL_LEVEL }}} detail.",
                ),
            ],
        )

        # Generate files
        files = adapter.generate(
            prompt, tmp_path, dry_run=False, variables={"DETAIL_LEVEL": "high"}
        )

        # Check that individual markdown files were created
        prompts_dir = tmp_path / ".continue" / "prompts"
        assert prompts_dir.exists()

        refactor_md = prompts_dir / "refactor.md"
        explain_md = prompts_dir / "explain.md"

        assert refactor_md in files
        assert explain_md in files
        assert refactor_md.exists()
        assert explain_md.exists()

        # Verify refactor markdown content
        with open(refactor_md, "r") as f:
            refactor_content = f.read()

        assert "---" in refactor_content
        assert "name: refactor" in refactor_content
        assert "description: Refactor code for better quality" in refactor_content
        assert "invokable: true" in refactor_content
        assert "Refactor the selected code" in refactor_content

        # Verify explain markdown with variable substitution
        with open(explain_md, "r") as f:
            explain_content = f.read()

        assert "name: explain" in explain_content
        assert "high detail" in explain_content

    def test_generate_config_yaml_with_prompt_references(self, adapter, tmp_path):
        """Test generating config.yaml with prompt file references."""
        from promptrek.core.models import (
            Command,
            MCPServer,
            PromptMetadata,
            UniversalPromptV3,
        )

        # Create v3 prompt with both MCP servers and commands
        prompt = UniversalPromptV3(
            schema_version="3.0.0",
            metadata=PromptMetadata(
                title="Test Project",
                description="Test",
                version="1.0.0",
                author="test",
                created="2024-01-01",
                updated="2024-01-01",
            ),
            content="# Test Project",
            mcp_servers=[
                MCPServer(name="filesystem", command="npx", args=["-y", "test"]),
            ],
            commands=[
                Command(
                    name="refactor", description="Refactor", prompt="Refactor code"
                ),
                Command(name="explain", description="Explain", prompt="Explain code"),
            ],
        )

        # Generate files
        files = adapter.generate(prompt, tmp_path, dry_run=False)

        # Check that config.yaml was created
        config_yaml = tmp_path / ".continue" / "config.yaml"
        assert config_yaml in files
        assert config_yaml.exists()

        # Verify config.yaml content
        import yaml

        with open(config_yaml, "r") as f:
            config_content = yaml.safe_load(f)

        assert config_content["name"] == "PrompTrek Generated Configuration"
        assert config_content["version"] == "1.0.0"
        assert config_content["schema"] == "v1"
        assert "prompts" in config_content
        assert len(config_content["prompts"]) == 2

        # Verify prompt references
        prompt_refs = [p["uses"] for p in config_content["prompts"]]
        assert "file://.continue/prompts/refactor.md" in prompt_refs
        assert "file://.continue/prompts/explain.md" in prompt_refs

    def test_mcp_yaml_format_validation(self, adapter, tmp_path):
        """Test that generated MCP YAML files have correct Continue format."""
        from promptrek.core.models import MCPServer, PromptMetadata, UniversalPromptV3

        prompt = UniversalPromptV3(
            schema_version="3.0.0",
            metadata=PromptMetadata(
                title="Test",
                description="Test",
                version="1.0.0",
                author="test",
                created="2024-01-01",
                updated="2024-01-01",
            ),
            content="# Test",
            mcp_servers=[
                MCPServer(
                    name="test-server",
                    command="node",
                    args=["server.js"],
                    env={"API_KEY": "secret"},
                ),
            ],
        )

        adapter.generate(prompt, tmp_path, dry_run=False)

        # Read and validate YAML structure
        import yaml

        yaml_file = tmp_path / ".continue" / "mcpServers" / "test-server.yaml"
        with open(yaml_file, "r") as f:
            content = yaml.safe_load(f)

        # Verify required Continue fields
        assert "name" in content
        assert "version" in content
        assert "schema" in content
        assert "mcpServers" in content
        assert content["schema"] == "v1"
        assert content["version"] == "0.0.1"
        assert isinstance(content["mcpServers"], list)
        assert len(content["mcpServers"]) == 1

    def test_prompt_markdown_frontmatter_validation(self, adapter, tmp_path):
        """Test that generated prompt markdown files have correct frontmatter."""
        from promptrek.core.models import Command, PromptMetadata, UniversalPromptV3

        prompt = UniversalPromptV3(
            schema_version="3.0.0",
            metadata=PromptMetadata(
                title="Test",
                description="Test",
                version="1.0.0",
                author="test",
                created="2024-01-01",
                updated="2024-01-01",
            ),
            content="# Test",
            commands=[
                Command(
                    name="test-command",
                    description="Test command description",
                    prompt="This is the prompt content",
                ),
            ],
        )

        adapter.generate(prompt, tmp_path, dry_run=False)

        # Read and validate markdown frontmatter
        md_file = tmp_path / ".continue" / "prompts" / "test-command.md"
        with open(md_file, "r") as f:
            content = f.read()

        # Verify frontmatter structure
        import yaml

        parts = content.split("---")
        assert (
            len(parts) >= 3
        )  # Should have opening ---, frontmatter, closing ---, and content

        frontmatter = yaml.safe_load(parts[1])
        assert frontmatter["name"] == "test-command"
        assert frontmatter["description"] == "Test command description"
        assert frontmatter["invokable"] is True

        # Verify content after frontmatter
        assert "This is the prompt content" in content

    def test_multiple_mcp_servers_creates_multiple_files(self, adapter, tmp_path):
        """Test that multiple MCP servers create multiple YAML files."""
        from promptrek.core.models import MCPServer, PromptMetadata, UniversalPromptV3

        prompt = UniversalPromptV3(
            schema_version="3.0.0",
            metadata=PromptMetadata(
                title="Test",
                description="Test",
                version="1.0.0",
                author="test",
                created="2024-01-01",
                updated="2024-01-01",
            ),
            content="# Test",
            mcp_servers=[
                MCPServer(name="server1", command="cmd1", args=["arg1"]),
                MCPServer(name="server2", command="cmd2", args=["arg2"]),
                MCPServer(name="server3", command="cmd3", args=["arg3"]),
            ],
        )

        files = adapter.generate(prompt, tmp_path, dry_run=False)

        # Verify 3 separate YAML files created
        mcp_dir = tmp_path / ".continue" / "mcpServers"
        yaml_files = list(mcp_dir.glob("*.yaml"))
        assert len(yaml_files) == 3

        # Verify each file exists
        assert (mcp_dir / "server1.yaml").exists()
        assert (mcp_dir / "server2.yaml").exists()
        assert (mcp_dir / "server3.yaml").exists()

    def test_multiple_commands_creates_multiple_files(self, adapter, tmp_path):
        """Test that multiple commands create multiple markdown files."""
        from promptrek.core.models import Command, PromptMetadata, UniversalPromptV3

        prompt = UniversalPromptV3(
            schema_version="3.0.0",
            metadata=PromptMetadata(
                title="Test",
                description="Test",
                version="1.0.0",
                author="test",
                created="2024-01-01",
                updated="2024-01-01",
            ),
            content="# Test",
            commands=[
                Command(name="cmd1", description="Desc1", prompt="Prompt1"),
                Command(name="cmd2", description="Desc2", prompt="Prompt2"),
                Command(name="cmd3", description="Desc3", prompt="Prompt3"),
                Command(name="cmd4", description="Desc4", prompt="Prompt4"),
            ],
        )

        files = adapter.generate(prompt, tmp_path, dry_run=False)

        # Verify 4 separate markdown files created
        prompts_dir = tmp_path / ".continue" / "prompts"
        md_files = list(prompts_dir.glob("*.md"))
        assert len(md_files) == 4

        # Verify each file exists
        assert (prompts_dir / "cmd1.md").exists()
        assert (prompts_dir / "cmd2.md").exists()
        assert (prompts_dir / "cmd3.md").exists()
        assert (prompts_dir / "cmd4.md").exists()

    def test_sync_parses_mcp_servers_from_yaml_files(self, adapter, tmp_path):
        """Test that sync can parse MCP servers from individual YAML files."""
        from promptrek.core.models import MCPServer, PromptMetadata, UniversalPromptV3

        # Generate files first
        prompt = UniversalPromptV3(
            schema_version="3.0.0",
            metadata=PromptMetadata(
                title="Test",
                description="Test",
                version="1.0.0",
                author="test",
                created="2024-01-01",
                updated="2024-01-01",
            ),
            content="# Test",
            mcp_servers=[
                MCPServer(name="filesystem", command="npx", args=["-y", "fs-server"]),
                MCPServer(
                    name="github",
                    command="npx",
                    args=["-y", "gh-server"],
                    env={"TOKEN": "secret"},
                ),
            ],
        )

        adapter.generate(prompt, tmp_path, dry_run=False)

        # Now sync back
        synced = adapter.parse_files(tmp_path)

        # Verify MCP servers were parsed
        assert synced.mcp_servers is not None
        assert len(synced.mcp_servers) == 2
        assert synced.mcp_servers[0].name == "filesystem"
        assert synced.mcp_servers[0].command == "npx"
        assert synced.mcp_servers[1].name == "github"
        assert synced.mcp_servers[1].env["TOKEN"] == "secret"

    def test_sync_parses_commands_from_prompt_files(self, adapter, tmp_path):
        """Test that sync can parse commands from individual prompt markdown files."""
        from promptrek.core.models import Command, PromptMetadata, UniversalPromptV3

        # Generate files first
        prompt = UniversalPromptV3(
            schema_version="3.0.0",
            metadata=PromptMetadata(
                title="Test",
                description="Test",
                version="1.0.0",
                author="test",
                created="2024-01-01",
                updated="2024-01-01",
            ),
            content="# Test",
            commands=[
                Command(
                    name="refactor",
                    description="Refactor code",
                    prompt="Refactor this code",
                ),
                Command(
                    name="explain",
                    description="Explain code",
                    prompt="Explain how this works",
                ),
            ],
        )

        adapter.generate(prompt, tmp_path, dry_run=False)

        # Now sync back
        synced = adapter.parse_files(tmp_path)

        # Verify commands were parsed
        assert synced.commands is not None
        assert len(synced.commands) == 2

        # Commands may be in any order, so check by name
        command_names = {cmd.name for cmd in synced.commands}
        assert "refactor" in command_names
        assert "explain" in command_names

        refactor_cmd = next(cmd for cmd in synced.commands if cmd.name == "refactor")
        assert refactor_cmd.description == "Refactor code"
        assert refactor_cmd.prompt == "Refactor this code"

    def test_sync_roundtrip_preserves_all_data(self, adapter, tmp_path):
        """Test that generate → sync → generate preserves all data."""
        from promptrek.core.models import (
            Command,
            MCPServer,
            PromptMetadata,
            UniversalPromptV3,
        )

        # Create comprehensive prompt
        original = UniversalPromptV3(
            schema_version="3.0.0",
            metadata=PromptMetadata(
                title="Full Test",
                description="Complete test",
                version="1.0.0",
                author="test",
                created="2024-01-01",
                updated="2024-01-01",
            ),
            content="# Full Test Project",
            mcp_servers=[
                MCPServer(name="fs", command="npx", args=["fs"]),
                MCPServer(name="gh", command="npx", args=["gh"]),
            ],
            commands=[
                Command(name="cmd1", description="First", prompt="First command"),
                Command(name="cmd2", description="Second", prompt="Second command"),
            ],
        )

        # Generate
        adapter.generate(original, tmp_path, dry_run=False)

        # Sync back
        synced = adapter.parse_files(tmp_path)

        # Verify all data preserved
        assert synced.mcp_servers is not None
        assert len(synced.mcp_servers) == 2
        assert synced.commands is not None
        assert len(synced.commands) == 2
        assert synced.mcp_servers[0].name == "fs"
        assert synced.mcp_servers[1].name == "gh"
        assert synced.commands[0].name == "cmd1"
        assert synced.commands[1].name == "cmd2"
