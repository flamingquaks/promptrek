"""Integration tests for v2.1.0 plugin generation.

Tests end-to-end workflows for MCP servers, commands, agents, and hooks.
"""

import json
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from promptrek.cli.main import cli


class TestPluginGeneration:
    """Test plugin file generation for v2.1.0 schema."""

    @pytest.fixture
    def v21_prompt_with_mcp(self, tmp_path):
        """Create a v2.1 prompt file with MCP servers."""
        upf_file = tmp_path / "test.promptrek.yaml"
        upf_file.write_text(
            """
schema_version: "2.1.0"
metadata:
  title: "MCP Test Project"
  description: "Test MCP server integration"
  version: "1.0.0"
  author: "Test Author"
  tags: ["test", "mcp"]
content: |
  # MCP Test Project

  ## Guidelines
  - Use MCP servers for external integrations

plugins:
  mcp_servers:
    - name: filesystem
      command: npx
      args:
        - "-y"
        - "@modelcontextprotocol/server-filesystem"
        - "/tmp"
      description: "Filesystem access"
      trust_metadata:
        trusted: true
        trust_level: partial
    - name: github
      command: npx
      args:
        - "-y"
        - "@modelcontextprotocol/server-github"
      env:
        GITHUB_TOKEN: "{{{ GITHUB_TOKEN }}}"
        GITHUB_OWNER: "testorg"
      description: "GitHub integration"
variables:
  GITHUB_TOKEN: "test-token-123"
"""
        )
        return upf_file

    @pytest.fixture
    def v21_prompt_with_commands(self, tmp_path):
        """Create a v2.1 prompt file with custom commands."""
        upf_file = tmp_path / "test.promptrek.yaml"
        upf_file.write_text(
            """
schema_version: "2.1.0"
metadata:
  title: "Commands Test Project"
  description: "Test custom slash commands"
  version: "1.0.0"
content: |
  # Commands Test Project

plugins:
  commands:
    - name: review-code
      description: "Review code for quality"
      prompt: |
        Review the code for:
        - Code quality
        - Best practices
        - Security issues
      output_format: markdown
      requires_approval: false
      system_message: "You are an expert code reviewer"
      examples:
        - "review-code --file=main.py"
        - "review-code --pr=123"
    - name: generate-docs
      description: "Generate documentation"
      prompt: |
        Generate comprehensive documentation including:
        - API reference
        - Usage examples
        - Configuration options
      requires_approval: false
"""
        )
        return upf_file

    @pytest.fixture
    def v21_prompt_with_agents(self, tmp_path):
        """Create a v2.1 prompt file with autonomous agents."""
        upf_file = tmp_path / "test.promptrek.yaml"
        upf_file.write_text(
            """
schema_version: "2.1.0"
metadata:
  title: "Agents Test Project"
  description: "Test autonomous agents"
  version: "1.0.0"
content: |
  # Agents Test Project

plugins:
  agents:
    - name: test-generator
      description: "Generate unit tests"
      system_prompt: |
        You are a test automation expert. Generate comprehensive tests that:
        - Cover normal operations
        - Test edge cases
        - Handle error conditions
      tools:
        - file_read
        - file_write
        - run_tests
      trust_level: partial
      requires_approval: true
      context:
        framework: pytest
        coverage_target: 80
    - name: bug-fixer
      description: "Automatically fix bugs"
      system_prompt: |
        You are a bug-fixing specialist. Identify and fix bugs while:
        - Understanding the root cause
        - Applying minimal changes
        - Adding tests to prevent regression
      tools:
        - file_read
        - file_write
        - git_commit
      trust_level: untrusted
      requires_approval: true
"""
        )
        return upf_file

    @pytest.fixture
    def v21_prompt_with_hooks(self, tmp_path):
        """Create a v2.1 prompt file with event hooks."""
        upf_file = tmp_path / "test.promptrek.yaml"
        upf_file.write_text(
            """
schema_version: "2.1.0"
metadata:
  title: "Hooks Test Project"
  description: "Test event-driven hooks"
  version: "1.0.0"
content: |
  # Hooks Test Project

plugins:
  hooks:
    - name: pre-commit
      event: pre-commit
      command: "npm test"
      description: "Run tests before commit"
      requires_reapproval: true
    - name: post-save
      event: post-save
      command: "promptrek generate --all"
      conditions:
        file_pattern: "*.promptrek.yaml"
      requires_reapproval: false
      description: "Auto-regenerate after save"
"""
        )
        return upf_file

    @pytest.fixture
    def v21_prompt_full(self, tmp_path):
        """Create a v2.1 prompt file with all plugin types."""
        upf_file = tmp_path / "test.promptrek.yaml"
        upf_file.write_text(
            """
schema_version: "2.1.0"
metadata:
  title: "Full Plugin Test"
  description: "Test all plugin types"
  version: "1.0.0"
content: |
  # Full Plugin Test

plugins:
  mcp_servers:
    - name: test-server
      command: npx
      args: ["-y", "@test/server"]
  commands:
    - name: test-cmd
      description: "Test command"
      prompt: "Do something"
  agents:
    - name: test-agent
      description: "Test agent"
      system_prompt: "You are a test agent"
  hooks:
    - name: test-hook
      event: test-event
      command: "echo test"
"""
        )
        return upf_file

    def test_generate_claude_mcp_servers(self, v21_prompt_with_mcp, tmp_path):
        """Test Claude adapter generates MCP server config."""
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "generate",
                str(v21_prompt_with_mcp),
                "--editor",
                "claude",
                "-o",
                str(tmp_path),
            ],
        )

        assert result.exit_code == 0

        # Check MCP config file was created
        mcp_file = tmp_path / ".claude" / "mcp.json"
        assert mcp_file.exists()

        # Validate MCP config structure
        mcp_config = json.loads(mcp_file.read_text())
        assert "mcpServers" in mcp_config
        assert "filesystem" in mcp_config["mcpServers"]
        assert "github" in mcp_config["mcpServers"]

        # Check filesystem server
        fs_server = mcp_config["mcpServers"]["filesystem"]
        assert fs_server["command"] == "npx"
        assert "-y" in fs_server["args"]

        # Check github server with env vars (should have variable substituted)
        gh_server = mcp_config["mcpServers"]["github"]
        assert "env" in gh_server
        assert gh_server["env"]["GITHUB_TOKEN"] == "test-token-123"

    def test_generate_claude_commands(self, v21_prompt_with_commands, tmp_path):
        """Test Claude adapter generates command files."""
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "generate",
                str(v21_prompt_with_commands),
                "--editor",
                "claude",
                "-o",
                str(tmp_path),
            ],
        )

        assert result.exit_code == 0

        # Check command files were created
        commands_dir = tmp_path / ".claude" / "commands"
        assert commands_dir.exists()

        review_cmd = commands_dir / "review-code.md"
        assert review_cmd.exists()

        # Validate command content
        content = review_cmd.read_text()
        assert "Review the code for:" in content
        assert "Code quality" in content
        assert "Best practices" in content

        docs_cmd = commands_dir / "generate-docs.md"
        assert docs_cmd.exists()

    def test_generate_claude_agents(self, v21_prompt_with_agents, tmp_path):
        """Test Claude adapter generates agent files."""
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "generate",
                str(v21_prompt_with_agents),
                "--editor",
                "claude",
                "-o",
                str(tmp_path),
            ],
        )

        assert result.exit_code == 0

        # Check agent files were created
        agents_dir = tmp_path / ".claude" / "agents"
        assert agents_dir.exists()

        test_gen_agent = agents_dir / "test-generator.md"
        assert test_gen_agent.exists()

        # Validate agent content
        content = test_gen_agent.read_text()
        assert "test automation expert" in content.lower()
        assert "Cover normal operations" in content

        bug_fixer_agent = agents_dir / "bug-fixer.md"
        assert bug_fixer_agent.exists()

    def test_generate_claude_hooks(self, v21_prompt_with_hooks, tmp_path):
        """Test Claude adapter generates hooks config."""
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "generate",
                str(v21_prompt_with_hooks),
                "--editor",
                "claude",
                "-o",
                str(tmp_path),
            ],
        )

        assert result.exit_code == 0

        # Check hooks file was created
        hooks_file = tmp_path / ".claude" / "hooks.yaml"
        assert hooks_file.exists()

        # Validate hooks structure
        hooks_config = yaml.safe_load(hooks_file.read_text())
        assert "hooks" in hooks_config
        assert len(hooks_config["hooks"]) == 2

        # Check pre-commit hook
        pre_commit = hooks_config["hooks"][0]
        assert pre_commit["name"] == "pre-commit"
        assert pre_commit["event"] == "pre-commit"
        assert pre_commit["command"] == "npm test"

    def test_generate_cursor_mcp_servers(self, v21_prompt_with_mcp, tmp_path):
        """Test Cursor adapter generates MCP server config."""
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "generate",
                str(v21_prompt_with_mcp),
                "--editor",
                "cursor",
                "-o",
                str(tmp_path),
            ],
        )

        assert result.exit_code == 0

        # Check MCP config file was created
        mcp_file = tmp_path / ".cursor" / "mcp-servers.json"
        assert mcp_file.exists()

        # Validate MCP config structure
        mcp_config = json.loads(mcp_file.read_text())
        assert "mcpServers" in mcp_config
        assert "filesystem" in mcp_config["mcpServers"]
        assert "github" in mcp_config["mcpServers"]

    def test_generate_cursor_agents(self, v21_prompt_with_agents, tmp_path):
        """Test Cursor adapter generates agent schemas."""
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "generate",
                str(v21_prompt_with_agents),
                "--editor",
                "cursor",
                "-o",
                str(tmp_path),
            ],
        )

        assert result.exit_code == 0

        # Check agent schema files were created
        schemas_dir = tmp_path / ".cursor" / "agent-schemas"
        assert schemas_dir.exists()

        test_gen_schema = schemas_dir / "test-generator.json"
        assert test_gen_schema.exists()

        # Validate schema structure
        schema = json.loads(test_gen_schema.read_text())
        assert schema["name"] == "test-generator"
        assert schema["description"] == "Generate unit tests"
        assert "systemPrompt" in schema
        assert schema["trustLevel"] == "partial"
        assert schema["requiresApproval"] is True

    def test_generate_all_plugins(self, v21_prompt_full, tmp_path):
        """Test generating all plugin types at once."""
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "generate",
                str(v21_prompt_full),
                "--editor",
                "claude",
                "-o",
                str(tmp_path),
            ],
        )

        assert result.exit_code == 0

        # All plugin files should exist
        assert (tmp_path / ".claude" / "mcp.json").exists()
        assert (tmp_path / ".claude" / "commands" / "test-cmd.md").exists()
        assert (tmp_path / ".claude" / "agents" / "test-agent.md").exists()
        assert (tmp_path / ".claude" / "hooks.yaml").exists()

    def test_plugins_command_list(self, v21_prompt_full, tmp_path):
        """Test 'promptrek plugins list' command."""
        runner = CliRunner()
        result = runner.invoke(
            cli, ["plugins", "list", "--file", str(v21_prompt_full)]
        )

        assert result.exit_code == 0
        assert "MCP Servers" in result.output
        assert "test-server" in result.output
        assert "Commands" in result.output
        assert "test-cmd" in result.output
        assert "Agents" in result.output
        assert "test-agent" in result.output
        assert "Hooks" in result.output
        assert "test-hook" in result.output

    def test_plugins_command_generate(self, v21_prompt_full, tmp_path):
        """Test 'promptrek plugins generate' command."""
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "plugins",
                "generate",
                "--file",
                str(v21_prompt_full),
                "--editor",
                "claude",
                "--output",
                str(tmp_path),
            ],
        )

        assert result.exit_code == 0
        assert (tmp_path / ".claude" / "mcp.json").exists()

    def test_plugins_command_validate(self, v21_prompt_full):
        """Test 'promptrek plugins validate' command."""
        runner = CliRunner()
        result = runner.invoke(
            cli, ["plugins", "validate", "--file", str(v21_prompt_full)]
        )

        assert result.exit_code == 0
        assert "No critical errors found" in result.output

    def test_plugins_validate_invalid_trust_level(self, tmp_path):
        """Test validation fails for invalid trust level."""
        upf_file = tmp_path / "invalid.promptrek.yaml"
        upf_file.write_text(
            """
schema_version: "2.1.0"
metadata:
  title: "Invalid Test"
  description: "Test invalid trust level"
  version: "1.0.0"
content: |
  # Invalid Test

plugins:
  agents:
    - name: bad-agent
      description: "Agent with invalid trust level"
      system_prompt: "Test"
      trust_level: invalid_level
"""
        )

        runner = CliRunner()
        result = runner.invoke(cli, ["plugins", "validate", "--file", str(upf_file)])

        # Should fail validation
        assert result.exit_code != 0

    def test_variable_substitution_in_mcp_servers(self, tmp_path):
        """Test variable substitution in MCP server configurations."""
        upf_file = tmp_path / "test.promptrek.yaml"
        upf_file.write_text(
            """
schema_version: "2.1.0"
metadata:
  title: "Variable Test"
  description: "Test variable substitution"
  version: "1.0.0"
content: |
  # Variable Test

plugins:
  mcp_servers:
    - name: api-server
      command: npx
      env:
        API_KEY: "{{{ API_KEY }}}"
        API_URL: "{{{ API_URL }}}"
        PROJECT: "{{{ PROJECT_NAME }}}"
variables:
  API_KEY: "secret-key-123"
  API_URL: "https://api.example.com"
  PROJECT_NAME: "TestProject"
"""
        )

        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["generate", str(upf_file), "--editor", "claude", "-o", str(tmp_path)],
        )

        assert result.exit_code == 0

        # Check variable substitution in MCP config
        mcp_file = tmp_path / ".claude" / "mcp.json"
        mcp_config = json.loads(mcp_file.read_text())

        env = mcp_config["mcpServers"]["api-server"]["env"]
        assert env["API_KEY"] == "secret-key-123"
        assert env["API_URL"] == "https://api.example.com"
        assert env["PROJECT"] == "TestProject"

    def test_dry_run_plugins(self, v21_prompt_full, tmp_path):
        """Test dry run mode for plugin generation."""
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "generate",
                str(v21_prompt_full),
                "--editor",
                "claude",
                "-o",
                str(tmp_path),
                "--dry-run",
            ],
        )

        assert result.exit_code == 0

        # No files should be created in dry run
        assert not (tmp_path / ".claude" / "mcp.json").exists()
        assert not (tmp_path / ".claude" / "commands").exists()

    def test_backward_compatibility_v20_no_plugins(self, tmp_path):
        """Test v2.0.0 files (without plugins) still work."""
        upf_file = tmp_path / "v20.promptrek.yaml"
        upf_file.write_text(
            """
schema_version: "2.0.0"
metadata:
  title: "V2.0 Test"
  description: "Test backward compatibility"
  version: "1.0.0"
content: |
  # V2.0 Test

  No plugins, just content.
"""
        )

        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["generate", str(upf_file), "--editor", "claude", "-o", str(tmp_path)],
        )

        assert result.exit_code == 0
        # Should still generate CLAUDE.md
        assert (tmp_path / ".claude" / "CLAUDE.md").exists()
        # But no plugin files
        assert not (tmp_path / ".claude" / "mcp.json").exists()


class TestPluginMigration:
    """Test migration to v2.1.0 schema."""

    def test_migrate_v20_to_v21(self, tmp_path):
        """Test migrating v2.0.0 to v2.1.0."""
        v20_file = tmp_path / "v20.promptrek.yaml"
        v20_file.write_text(
            """
schema_version: "2.0.0"
metadata:
  title: "Old Project"
  description: "V2.0 project"
  version: "1.0.0"
content: |
  # Old Project

  Some content here.
variables:
  VAR1: "value1"
"""
        )

        runner = CliRunner()
        v21_file = tmp_path / "v21.promptrek.yaml"
        result = runner.invoke(
            cli, ["migrate", str(v20_file), "-o", str(v21_file)]
        )

        assert result.exit_code == 0
        assert v21_file.exists()

        # Check migrated file
        migrated = yaml.safe_load(v21_file.read_text())
        assert migrated["schema_version"] == "2.1.0"
        assert migrated["metadata"]["title"] == "Old Project"
        assert migrated["content"] == "# Old Project\n\nSome content here.\n"
        assert migrated["variables"]["VAR1"] == "value1"
        # plugins field should be None/absent
        assert "plugins" not in migrated or migrated.get("plugins") is None

    def test_migrate_v21_no_op(self, tmp_path):
        """Test migrating v2.1.0 is a no-op."""
        v21_file = tmp_path / "v21.promptrek.yaml"
        v21_file.write_text(
            """
schema_version: "2.1.0"
metadata:
  title: "Already V2.1"
  description: "Test"
  version: "1.0.0"
content: |
  # Already V2.1
"""
        )

        runner = CliRunner()
        result = runner.invoke(cli, ["migrate", str(v21_file)])

        assert result.exit_code == 0
        assert "already v2.1 format" in result.output


class TestPluginExamples:
    """Test the example plugin configurations."""

    @staticmethod
    def _get_project_root() -> Path:
        """Get the project root directory."""
        # Start from this file's directory and go up until we find pyproject.toml
        current = Path(__file__).parent
        while current != current.parent:
            if (current / "pyproject.toml").exists():
                return current
            current = current.parent
        raise FileNotFoundError("Could not find project root (pyproject.toml not found)")

    def test_mcp_servers_example(self):
        """Test mcp-servers example file."""
        project_root = self._get_project_root()
        example_file = project_root / "examples" / "v21-plugins" / "mcp-servers.promptrek.yaml"
        assert example_file.exists(), f"Example file not found: {example_file}"

        runner = CliRunner()
        result = runner.invoke(cli, ["validate", str(example_file)])

        assert result.exit_code == 0

    def test_custom_commands_example(self):
        """Test custom-commands example file."""
        project_root = self._get_project_root()
        example_file = project_root / "examples" / "v21-plugins" / "custom-commands.promptrek.yaml"
        assert example_file.exists(), f"Example file not found: {example_file}"

        runner = CliRunner()
        result = runner.invoke(cli, ["validate", str(example_file)])

        assert result.exit_code == 0

    def test_autonomous_agents_example(self):
        """Test autonomous-agents example file."""
        project_root = self._get_project_root()
        example_file = project_root / "examples" / "v21-plugins" / "autonomous-agents.promptrek.yaml"
        assert example_file.exists(), f"Example file not found: {example_file}"

        runner = CliRunner()
        result = runner.invoke(cli, ["validate", str(example_file)])

        assert result.exit_code == 0

    def test_generate_from_examples(self, tmp_path):
        """Test generating plugin files from example configurations."""
        project_root = self._get_project_root()
        example_file = project_root / "examples" / "v21-plugins" / "mcp-servers.promptrek.yaml"

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "generate",
                str(example_file),
                "--editor",
                "claude",
                "-o",
                str(tmp_path),
            ],
        )

        # Should succeed (even if variables are missing, it should work)
        assert result.exit_code == 0
