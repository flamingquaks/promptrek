"""
Unit tests for Cline adapter.
"""

from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from promptrek.adapters.cline import ClineAdapter
from promptrek.core.models import (
    Instructions,
    ProjectContext,
    PromptMetadata,
    UniversalPrompt,
)

from .base_test import TestAdapterBase


class TestClineAdapter(TestAdapterBase):
    """Test Cline adapter."""

    @pytest.fixture
    def adapter(self):
        """Create Cline adapter instance."""
        return ClineAdapter()

    def test_init(self, adapter):
        """Test adapter initialization."""
        assert adapter.name == "cline"
        assert (
            adapter.description
            == "Cline VSCode Extension (.clinerules, .clinerules/*.md)"
        )
        assert ".clinerules" in adapter.file_patterns
        assert ".clinerules/*.md" in adapter.file_patterns

    def test_supports_features(self, adapter):
        """Test feature support."""
        assert adapter.supports_variables() is True
        assert adapter.supports_conditionals() is True

    def test_validate_valid_prompt(self, adapter, sample_prompt):
        """Test validation of valid prompt."""
        errors = adapter.validate(sample_prompt)
        assert len(errors) == 0

    def test_validate_missing_instructions(self, adapter):
        """Test validation with missing instructions."""
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(
                title="Test",
                description="Test description",
                version="1.0.0",
                author="test@example.com",
                created="2024-01-01",
                updated="2024-01-01",
            ),
            targets=["cline"],
        )
        errors = adapter.validate(prompt)
        assert len(errors) == 1
        assert errors[0].field == "instructions.general"

    def test_validate_missing_title(self, adapter):
        """Test validation with missing title."""
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(
                title="",  # Empty title should fail
                description="Test description",
            ),
        )
        errors = adapter.validate(prompt)
        assert len(errors) >= 1
        # Should have error for missing title or instructions

    def test_should_use_directory_format_simple(self, adapter):
        """Test format selection for simple project."""
        simple_metadata = PromptMetadata(
            title="Simple App", description="Basic web app"
        )
        simple_context = ProjectContext(project_type="web", technologies=["HTML"])
        simple_instructions = Instructions(general=["Keep it simple"])

        simple_prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=simple_metadata,
            context=simple_context,
            instructions=simple_instructions,
        )

        # Simple project should use single file format
        assert adapter._should_use_directory_format(simple_prompt) is False

    def test_should_use_directory_format_complex(self, adapter):
        """Test format selection for complex project."""
        complex_metadata = PromptMetadata(
            title="Complex App", description="Complex application"
        )
        complex_context = ProjectContext(
            project_type="enterprise_application",
            technologies=["React", "TypeScript", "Node.js", "PostgreSQL"],
            description="Multi-service architecture",
        )
        complex_instructions = Instructions(
            general=[
                "Follow SOLID principles",
                "Use dependency injection",
                "Implement error handling",
            ],
            code_style=["Use TypeScript", "Follow ESLint", "Use Prettier"],
        )
        complex_examples = {
            "api_endpoint": 'app.get("/users/:id", handler)',
            "component": "const App = () => <div>Hello</div>",
        }

        complex_prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=complex_metadata,
            context=complex_context,
            instructions=complex_instructions,
            examples=complex_examples,
        )

        # Complex project should use directory format
        assert adapter._should_use_directory_format(complex_prompt) is True

    def test_generate_rule_files(self, adapter, sample_prompt):
        """Test rule files generation."""
        rule_files = adapter._generate_rule_files(sample_prompt)

        # Should generate at least project overview and coding guidelines
        assert len(rule_files) >= 2
        assert "01-project-overview.md" in rule_files

        # Check project overview content
        overview_content = rule_files["01-project-overview.md"]
        assert sample_prompt.metadata.title in overview_content
        assert "## Project Overview" in overview_content
        assert sample_prompt.metadata.description in overview_content

    @patch("builtins.open", new_callable=mock_open)
    @patch("pathlib.Path.mkdir")
    def test_generate_complex_project_directory_format(
        self, mock_mkdir, mock_file, adapter
    ):
        """Test generation for complex project (directory format)."""
        # Create complex prompt that should trigger directory format
        complex_metadata = PromptMetadata(
            title="Complex App", description="Complex application"
        )
        complex_context = ProjectContext(
            project_type="enterprise_application",
            technologies=["React", "TypeScript", "Node.js", "PostgreSQL"],
            description="Multi-service architecture",
        )
        complex_instructions = Instructions(
            general=[
                "Follow SOLID principles",
                "Use dependency injection",
                "Implement error handling",
            ],
            code_style=["Use TypeScript", "Follow ESLint", "Use Prettier"],
        )
        complex_examples = {
            "api_endpoint": 'app.get("/users/:id", handler)',
            "component": "const App = () => <div>Hello</div>",
        }

        complex_prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=complex_metadata,
            context=complex_context,
            instructions=complex_instructions,
            examples=complex_examples,
        )

        output_dir = Path("/tmp/test")
        files = adapter.generate(complex_prompt, output_dir, dry_run=False)

        # Should generate multiple files for complex project
        assert len(files) >= 3

        # Check that files are in .clinerules directory
        for file_path in files:
            assert file_path.parent.name == ".clinerules"
            assert file_path.suffix == ".md"

        # Verify directory creation was called
        mock_mkdir.assert_called_once()

        # Verify files were written (once for each generated file)
        assert mock_file.call_count == len(files)

    @patch("builtins.open", new_callable=mock_open)
    def test_generate_simple_project_single_file_format(self, mock_file, adapter):
        """Test generation for simple project (single file format)."""
        # Create simple prompt that should trigger single file format
        simple_metadata = PromptMetadata(
            title="Simple App", description="Basic web app"
        )
        simple_context = ProjectContext(project_type="web", technologies=["HTML"])
        simple_instructions = Instructions(general=["Keep it simple"])

        simple_prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=simple_metadata,
            context=simple_context,
            instructions=simple_instructions,
        )

        output_dir = Path("/tmp/test")
        files = adapter.generate(simple_prompt, output_dir, dry_run=False)

        # Should generate single file for simple project
        assert len(files) == 1
        assert files[0].name == ".clinerules"

        # Verify file was written
        mock_file.assert_called_once()

    def test_build_unified_content(self, adapter):
        """Test unified content generation for single file format."""
        metadata = PromptMetadata(title="Test Project", description="Test description")
        context = ProjectContext(project_type="web", technologies=["React"])
        instructions = Instructions(
            general=["Write clean code"], code_style=["Use TypeScript"]
        )

        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=metadata,
            context=context,
            instructions=instructions,
        )

        content = adapter._build_unified_content(prompt)

        # Check that unified content contains expected sections
        assert "# Test Project" in content
        assert "## Project Overview" in content
        assert "## Project Context" in content
        assert "## Coding Guidelines" in content
        assert "## Code Style" in content
        assert "Test description" in content
        assert "Write clean code" in content
        assert "Use TypeScript" in content


class TestClineUserLevelMCPConfiguration:
    """Test user-level MCP configuration for Cline."""

    @pytest.fixture
    def adapter(self):
        """Create Cline adapter instance."""
        return ClineAdapter()

    @pytest.fixture
    def sample_mcp_servers(self):
        """Create sample MCP servers for testing."""
        from promptrek.core.models import MCPServer

        return [
            MCPServer(
                name="filesystem",
                command="npx",
                args=["-y", "@modelcontextprotocol/server-filesystem"],
                env={"ROOT_PATH": "/tmp"},
            ),
            MCPServer(
                name="github",
                command="npx",
                args=["-y", "@modelcontextprotocol/server-github"],
                env={"GITHUB_TOKEN": "token123"},
            ),
        ]

    def test_get_default_config_paths(self, adapter):
        """Test getting default config path list."""
        paths = adapter.get_default_config_paths()

        # Should return a list
        assert isinstance(paths, list)
        assert len(paths) >= 1

        # All should be Path objects
        assert all(isinstance(p, Path) for p in paths)

        # Should include expected filename
        assert all(p.name == "cline_mcp_settings.json" for p in paths)

        # Should include expected directory structure
        assert all("globalStorage" in str(p) for p in paths)
        assert all("saoudrizwan.claude-dev" in str(p) for p in paths)

    def test_find_mcp_config_file_not_found(self, adapter):
        """Test finding MCP config file when it doesn't exist."""
        # In test environment, file likely won't exist
        result = adapter.find_mcp_config_file()
        # Could be None or a Path if the file actually exists on dev machine
        assert result is None or isinstance(result, Path)

    def test_get_mcp_config_strategy(self, adapter):
        """Test MCP configuration strategy for Cline."""
        strategy = adapter.get_mcp_config_strategy()

        # Cline should NOT support project-level config
        assert strategy["supports_project"] is False
        assert strategy["project_path"] is None

        # System path is now determined at runtime
        assert strategy["system_path"] is None

        # Should require confirmation for user-level changes
        assert strategy["requires_confirmation"] is True

        # Should use JSON format
        assert strategy["config_format"] == "json"

    @patch("promptrek.adapters.cline.ClineAdapter.find_mcp_config_file")
    @patch("promptrek.adapters.cline.click.confirm")
    @patch("promptrek.adapters.mcp_mixin.MCPGenerationMixin.read_existing_mcp_config")
    @patch("promptrek.adapters.mcp_mixin.MCPGenerationMixin.write_mcp_config_file")
    def test_generate_mcp_config_user_accepts(
        self,
        mock_write,
        mock_read,
        mock_confirm,
        mock_find,
        adapter,
        sample_mcp_servers,
    ):
        """Test MCP config generation when user accepts."""
        # Setup mocks - file found automatically
        mock_find.return_value = Path("/fake/path/cline_mcp_settings.json")
        mock_confirm.return_value = True  # User accepts
        mock_read.return_value = None  # No existing config
        mock_write.return_value = True

        output_dir = Path("/tmp/test")
        created_files = adapter._generate_mcp_config(
            mcp_servers=sample_mcp_servers,
            output_dir=output_dir,
            dry_run=False,
            verbose=False,
        )

        # Should create the config file
        assert len(created_files) == 1
        assert "cline_mcp_settings.json" in str(created_files[0])

        # Should have prompted user for warning
        mock_confirm.assert_called_once()

        # Should have written config
        mock_write.assert_called_once()

    @patch("promptrek.adapters.cline.ClineAdapter.find_mcp_config_file")
    @patch("promptrek.adapters.cline.click.confirm")
    @patch("promptrek.adapters.mcp_mixin.MCPGenerationMixin.read_existing_mcp_config")
    @patch("promptrek.adapters.mcp_mixin.MCPGenerationMixin.write_mcp_config_file")
    def test_generate_mcp_config_user_declines(
        self,
        mock_write,
        mock_read,
        mock_confirm,
        mock_find,
        adapter,
        sample_mcp_servers,
    ):
        """Test MCP config generation when user declines."""
        # Setup mocks
        mock_find.return_value = Path("/fake/path/cline_mcp_settings.json")
        mock_confirm.return_value = False  # User declines
        mock_read.return_value = None

        output_dir = Path("/tmp/test")
        created_files = adapter._generate_mcp_config(
            mcp_servers=sample_mcp_servers,
            output_dir=output_dir,
            dry_run=False,
            verbose=False,
        )

        # Should NOT create any files
        assert len(created_files) == 0

        # Should have prompted user
        mock_confirm.assert_called_once()

        # Should NOT have written config
        mock_write.assert_not_called()

    @patch("promptrek.adapters.cline.ClineAdapter.find_mcp_config_file")
    @patch("promptrek.adapters.cline.click.confirm")
    @patch("promptrek.adapters.mcp_mixin.MCPGenerationMixin.read_existing_mcp_config")
    @patch("promptrek.adapters.mcp_mixin.MCPGenerationMixin.write_mcp_config_file")
    def test_generate_mcp_config_merge_with_existing(
        self,
        mock_write,
        mock_read,
        mock_confirm,
        mock_find,
        adapter,
        sample_mcp_servers,
    ):
        """Test MCP config merging with existing configuration."""
        # Setup mocks
        mock_find.return_value = Path("/fake/path/cline_mcp_settings.json")
        existing_config = {
            "mcpServers": {
                "existing_server": {
                    "command": "existing",
                    "args": ["--test"],
                }
            }
        }
        mock_read.return_value = existing_config
        mock_confirm.return_value = True  # User accepts
        mock_write.return_value = True

        output_dir = Path("/tmp/test")
        created_files = adapter._generate_mcp_config(
            mcp_servers=sample_mcp_servers,
            output_dir=output_dir,
            dry_run=False,
            verbose=False,
        )

        # Should create the config file
        assert len(created_files) == 1

        # Should have written merged config
        mock_write.assert_called_once()
        written_config = mock_write.call_args[0][0]

        # Should have both existing and new servers
        assert "existing_server" in written_config["mcpServers"]
        assert "filesystem" in written_config["mcpServers"]
        assert "github" in written_config["mcpServers"]

    @patch("promptrek.adapters.cline.ClineAdapter.find_mcp_config_file")
    @patch("promptrek.adapters.cline.click.confirm")
    @patch("promptrek.adapters.mcp_mixin.MCPGenerationMixin.read_existing_mcp_config")
    @patch("promptrek.adapters.mcp_mixin.MCPGenerationMixin.write_mcp_config_file")
    def test_generate_mcp_config_conflict_detection(
        self, mock_write, mock_read, mock_confirm, mock_find, adapter
    ):
        """Test conflict detection for MCP servers with same name."""
        from promptrek.core.models import MCPServer

        # Setup mocks
        mock_find.return_value = Path("/fake/path/cline_mcp_settings.json")

        # Existing config has a server with same name but different config
        existing_config = {
            "mcpServers": {
                "filesystem": {
                    "command": "old-command",
                    "args": ["--old"],
                }
            }
        }
        mock_read.return_value = existing_config

        # New server with same name but different config
        new_servers = [
            MCPServer(
                name="filesystem",
                command="npx",
                args=["-y", "@modelcontextprotocol/server-filesystem"],
            )
        ]

        # User accepts initial warning but declines overwrite
        mock_confirm.side_effect = [True, False]  # Accept warning, decline overwrite
        mock_write.return_value = True

        output_dir = Path("/tmp/test")
        created_files = adapter._generate_mcp_config(
            mcp_servers=new_servers,
            output_dir=output_dir,
            dry_run=False,
            verbose=False,
        )

        # Should prompt twice: initial warning + conflict confirmation
        assert mock_confirm.call_count == 2

        # Should have skipped due to conflict
        # No files created because user declined overwrite
        assert len(created_files) == 0

    @patch("promptrek.adapters.cline.ClineAdapter.find_mcp_config_file")
    def test_generate_mcp_config_dry_run(self, mock_find, adapter, sample_mcp_servers):
        """Test MCP config generation in dry run mode."""
        # Mock file not found
        mock_find.return_value = None

        output_dir = Path("/tmp/test")
        created_files = adapter._generate_mcp_config(
            mcp_servers=sample_mcp_servers,
            output_dir=output_dir,
            dry_run=True,
            verbose=True,
        )

        # Dry run mode can't determine path without prompting, should skip
        assert len(created_files) == 0

    @patch("promptrek.adapters.cline.click.confirm")
    @patch("promptrek.adapters.mcp_mixin.MCPGenerationMixin.read_existing_mcp_config")
    @patch("promptrek.adapters.mcp_mixin.MCPGenerationMixin.write_mcp_config_file")
    def test_generate_mcp_config_with_config_field(
        self, mock_write, mock_read, mock_confirm, adapter, sample_mcp_servers
    ):
        """Test MCP config generation when path is provided in config field."""
        from promptrek.core.models import (
            EditorConfig,
            PromptMetadata,
            UniversalPromptV3,
        )

        # Create a v3 prompt with config field
        prompt = UniversalPromptV3(
            schema_version="3.1.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            content="Test content",
            config=EditorConfig(cline_mcp_path="/custom/path/cline_mcp_settings.json"),
        )

        # Setup mocks
        mock_read.return_value = None
        mock_confirm.return_value = True
        mock_write.return_value = True

        output_dir = Path("/tmp/test")
        created_files = adapter._generate_mcp_config(
            mcp_servers=sample_mcp_servers,
            output_dir=output_dir,
            dry_run=False,
            verbose=False,
            prompt=prompt,
        )

        # Should use the configured path
        assert len(created_files) == 1
        assert str(created_files[0]) == "/custom/path/cline_mcp_settings.json"

        # Should have written config
        mock_write.assert_called_once()
