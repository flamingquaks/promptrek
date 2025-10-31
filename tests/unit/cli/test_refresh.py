"""Tests for refresh command."""

from unittest.mock import Mock, patch

import pytest
import yaml

from promptrek.cli.commands.refresh import refresh_command
from promptrek.core.exceptions import CLIError


class TestRefreshCommand:
    """Test refresh_command function."""

    def test_refresh_no_metadata(self, tmp_path):
        """Test refresh when no generation metadata exists."""
        import os

        os.chdir(tmp_path)

        ctx = Mock()
        ctx.obj = {"verbose": False}

        with pytest.raises(CLIError, match="No generation metadata found"):
            refresh_command(
                ctx,
                editor=None,
                all_editors=False,
                dry_run=False,
                clear_cache=False,
                variables=None,
            )

    def test_refresh_with_valid_metadata(self, tmp_path):
        """Test refresh with valid generation metadata."""
        import os

        os.chdir(tmp_path)

        # Create metadata directory and file
        metadata_dir = tmp_path / ".promptrek"
        metadata_dir.mkdir()
        metadata_file = metadata_dir / "last-generation.yaml"

        # Create source file
        source_file = tmp_path / "project.promptrek.yaml"
        source_file.write_text("schema_version: 3.0.0\ncontent: test")

        # Create metadata
        metadata = {
            "source_file": str(source_file),
            "timestamp": "2025-01-01T00:00:00",
            "editors": ["claude"],
            "output_dir": str(tmp_path),
            "variables": {},
        }
        metadata_file.write_text(yaml.dump(metadata))

        ctx = Mock()
        ctx.obj = {"verbose": False}

        with patch("promptrek.cli.commands.generate.generate_command") as mock_generate:
            with patch("click.echo"):
                refresh_command(
                    ctx,
                    editor=None,
                    all_editors=False,
                    dry_run=False,
                    clear_cache=False,
                    variables=None,
                )

            # Verify generate was called
            mock_generate.assert_called_once()

    def test_refresh_with_specific_editor(self, tmp_path):
        """Test refresh with specific editor override."""
        import os

        os.chdir(tmp_path)

        # Create metadata directory and file
        metadata_dir = tmp_path / ".promptrek"
        metadata_dir.mkdir()
        metadata_file = metadata_dir / "last-generation.yaml"

        # Create source file
        source_file = tmp_path / "project.promptrek.yaml"
        source_file.write_text("schema_version: 3.0.0\ncontent: test")

        # Create metadata
        metadata = {
            "source_file": str(source_file),
            "timestamp": "2025-01-01T00:00:00",
            "editors": ["claude", "copilot"],
            "output_dir": str(tmp_path),
            "variables": {},
        }
        metadata_file.write_text(yaml.dump(metadata))

        ctx = Mock()
        ctx.obj = {"verbose": False}

        with patch("promptrek.cli.commands.generate.generate_command") as mock_generate:
            with patch("click.echo"):
                refresh_command(
                    ctx,
                    editor="copilot",  # Override to only refresh copilot
                    all_editors=False,
                    dry_run=False,
                    clear_cache=False,
                    variables=None,
                )

            # Should only call generate once for copilot
            assert mock_generate.call_count == 1
            # Verify it was called with copilot editor
            call_args = mock_generate.call_args
            assert call_args[1]["editor"] == "copilot"

    def test_refresh_dry_run(self, tmp_path):
        """Test refresh in dry run mode."""
        import os

        os.chdir(tmp_path)

        # Create metadata directory and file
        metadata_dir = tmp_path / ".promptrek"
        metadata_dir.mkdir()
        metadata_file = metadata_dir / "last-generation.yaml"

        # Create source file
        source_file = tmp_path / "project.promptrek.yaml"
        source_file.write_text("schema_version: 3.0.0\ncontent: test")

        # Create metadata
        metadata = {
            "source_file": str(source_file),
            "timestamp": "2025-01-01T00:00:00",
            "editors": ["claude"],
            "output_dir": str(tmp_path),
            "variables": {},
        }
        metadata_file.write_text(yaml.dump(metadata))

        ctx = Mock()
        ctx.obj = {"verbose": False}

        with patch("promptrek.cli.commands.generate.generate_command") as mock_generate:
            with patch("click.echo"):
                refresh_command(
                    ctx,
                    editor=None,
                    all_editors=False,
                    dry_run=True,  # Dry run mode
                    clear_cache=False,
                    variables=None,
                )

            # Should still call generate with dry_run=True
            assert mock_generate.call_count == 1
            call_args = mock_generate.call_args
            assert call_args[1]["dry_run"] is True

    def test_refresh_source_file_not_found(self, tmp_path):
        """Test refresh when source file is missing."""
        import os

        os.chdir(tmp_path)

        # Create metadata directory and file
        metadata_dir = tmp_path / ".promptrek"
        metadata_dir.mkdir()
        metadata_file = metadata_dir / "last-generation.yaml"

        # Create metadata pointing to non-existent file
        metadata = {
            "source_file": str(tmp_path / "missing.promptrek.yaml"),
            "timestamp": "2025-01-01T00:00:00",
            "editors": ["claude"],
            "output_dir": str(tmp_path),
            "variables": {},
        }
        metadata_file.write_text(yaml.dump(metadata))

        ctx = Mock()
        ctx.obj = {"verbose": False}

        with pytest.raises(CLIError, match="Source file not found"):
            refresh_command(
                ctx,
                editor=None,
                all_editors=False,
                dry_run=False,
                clear_cache=False,
                variables=None,
            )

    def test_refresh_with_variables(self, tmp_path):
        """Test refresh with variable overrides."""
        import os

        os.chdir(tmp_path)

        # Create metadata directory and file
        metadata_dir = tmp_path / ".promptrek"
        metadata_dir.mkdir()
        metadata_file = metadata_dir / "last-generation.yaml"

        # Create source file
        source_file = tmp_path / "project.promptrek.yaml"
        source_file.write_text("schema_version: 3.0.0\ncontent: test")

        # Create metadata
        metadata = {
            "source_file": str(source_file),
            "timestamp": "2025-01-01T00:00:00",
            "editors": ["claude"],
            "output_dir": str(tmp_path),
            "variables": {},
        }
        metadata_file.write_text(yaml.dump(metadata))

        ctx = Mock()
        ctx.obj = {"verbose": False}

        variables = {"MY_VAR": "value"}

        with patch("promptrek.cli.commands.generate.generate_command") as mock_generate:
            with patch("click.echo"):
                refresh_command(
                    ctx,
                    editor=None,
                    all_editors=False,
                    dry_run=False,
                    clear_cache=False,
                    variables=variables,
                )

            # Verify variables were passed to generate
            call_args = mock_generate.call_args
            assert call_args[1]["variables"] == variables

    def test_refresh_verbose_mode(self, tmp_path):
        """Test refresh in verbose mode."""
        import os

        os.chdir(tmp_path)

        # Create metadata directory and file
        metadata_dir = tmp_path / ".promptrek"
        metadata_dir.mkdir()
        metadata_file = metadata_dir / "last-generation.yaml"

        # Create source file
        source_file = tmp_path / "project.promptrek.yaml"
        source_file.write_text("schema_version: 3.0.0\ncontent: test")

        # Create metadata
        metadata = {
            "source_file": str(source_file),
            "timestamp": "2025-01-01T00:00:00",
            "editors": ["claude"],
            "output_dir": str(tmp_path),
            "variables": {},
        }
        metadata_file.write_text(yaml.dump(metadata))

        ctx = Mock()
        ctx.obj = {"verbose": True}  # Enable verbose

        with patch("promptrek.cli.commands.generate.generate_command") as mock_generate:
            with patch("click.echo") as mock_echo:
                refresh_command(
                    ctx,
                    editor=None,
                    all_editors=False,
                    dry_run=False,
                    clear_cache=False,
                    variables=None,
                )

            # Verbose mode should produce more output
            assert mock_echo.call_count > 0

    def test_refresh_all_editors_flag(self, tmp_path):
        """Test refresh with all_editors flag."""
        import os

        os.chdir(tmp_path)

        # Create metadata directory and file
        metadata_dir = tmp_path / ".promptrek"
        metadata_dir.mkdir()
        metadata_file = metadata_dir / "last-generation.yaml"

        # Create source file
        source_file = tmp_path / "project.promptrek.yaml"
        source_file.write_text("schema_version: 3.0.0\ncontent: test")

        # Create metadata with multiple editors
        metadata = {
            "source_file": str(source_file),
            "timestamp": "2025-01-01T00:00:00",
            "editors": ["claude", "copilot", "cursor"],
            "output_dir": str(tmp_path),
            "variables": {},
        }
        metadata_file.write_text(yaml.dump(metadata))

        ctx = Mock()
        ctx.obj = {"verbose": False}

        with patch("promptrek.cli.commands.generate.generate_command") as mock_generate:
            with patch("click.echo"):
                refresh_command(
                    ctx,
                    editor=None,
                    all_editors=True,  # Refresh all
                    dry_run=False,
                    clear_cache=False,
                    variables=None,
                )

            # Should call generate 3 times (one for each editor)
            assert mock_generate.call_count == 3

    def test_refresh_generate_failure(self, tmp_path):
        """Test refresh when generation fails for one editor."""
        import os

        os.chdir(tmp_path)

        # Create metadata directory and file
        metadata_dir = tmp_path / ".promptrek"
        metadata_dir.mkdir()
        metadata_file = metadata_dir / "last-generation.yaml"

        # Create source file
        source_file = tmp_path / "project.promptrek.yaml"
        source_file.write_text("schema_version: 3.0.0\ncontent: test")

        # Create metadata
        metadata = {
            "source_file": str(source_file),
            "timestamp": "2025-01-01T00:00:00",
            "editors": ["claude"],
            "output_dir": str(tmp_path),
            "variables": {},
        }
        metadata_file.write_text(yaml.dump(metadata))

        ctx = Mock()
        ctx.obj = {"verbose": False}

        with patch("promptrek.cli.commands.generate.generate_command") as mock_generate:
            # Make generate raise an exception
            mock_generate.side_effect = Exception("Generation failed")

            with patch("click.echo") as mock_echo:
                # Should not raise - should catch and display error
                refresh_command(
                    ctx,
                    editor=None,
                    all_editors=False,
                    dry_run=False,
                    clear_cache=False,
                    variables=None,
                )

            # Should have printed error message
            error_calls = [
                call
                for call in mock_echo.call_args_list
                if "Failed to refresh" in str(call)
            ]
            assert len(error_calls) > 0

    def test_refresh_invalid_metadata(self, tmp_path):
        """Test refresh when metadata file is invalid."""
        import os

        os.chdir(tmp_path)

        # Create metadata directory and file with invalid YAML
        metadata_dir = tmp_path / ".promptrek"
        metadata_dir.mkdir()
        metadata_file = metadata_dir / "last-generation.yaml"
        metadata_file.write_text("invalid: yaml: content:\n  - this is bad")

        ctx = Mock()
        ctx.obj = {"verbose": False}

        with pytest.raises(CLIError, match="Failed to load generation metadata"):
            refresh_command(
                ctx,
                editor=None,
                all_editors=False,
                dry_run=False,
                clear_cache=False,
                variables=None,
            )

    def test_refresh_verbose_with_error(self, tmp_path):
        """Test refresh in verbose mode when an error occurs."""
        import os

        os.chdir(tmp_path)

        # Create metadata directory and file
        metadata_dir = tmp_path / ".promptrek"
        metadata_dir.mkdir()
        metadata_file = metadata_dir / "last-generation.yaml"

        # Create source file
        source_file = tmp_path / "project.promptrek.yaml"
        source_file.write_text("schema_version: 3.0.0\ncontent: test")

        # Create metadata
        metadata = {
            "source_file": str(source_file),
            "timestamp": "2025-01-01T00:00:00",
            "editors": ["claude"],
            "output_dir": str(tmp_path),
            "variables": {},
        }
        metadata_file.write_text(yaml.dump(metadata))

        ctx = Mock()
        ctx.obj = {"verbose": True}  # Enable verbose to trigger re-raise

        with patch("promptrek.cli.commands.generate.generate_command") as mock_generate:
            # Make generate raise an exception
            mock_generate.side_effect = Exception("Generation failed")

            with patch("click.echo"):
                # In verbose mode, should re-raise the exception
                with pytest.raises(Exception, match="Generation failed"):
                    refresh_command(
                        ctx,
                        editor=None,
                        all_editors=False,
                        dry_run=False,
                        clear_cache=False,
                        variables=None,
                    )

    def test_refresh_dry_run_multiple_editors(self, tmp_path):
        """Test refresh in dry run mode with multiple editors."""
        import os

        os.chdir(tmp_path)

        # Create metadata directory and file
        metadata_dir = tmp_path / ".promptrek"
        metadata_dir.mkdir()
        metadata_file = metadata_dir / "last-generation.yaml"

        # Create source file
        source_file = tmp_path / "project.promptrek.yaml"
        source_file.write_text("schema_version: 3.0.0\ncontent: test")

        # Create metadata with multiple editors
        metadata = {
            "source_file": str(source_file),
            "timestamp": "2025-01-01T00:00:00",
            "editors": ["claude", "copilot"],
            "output_dir": str(tmp_path),
            "variables": {},
        }
        metadata_file.write_text(yaml.dump(metadata))

        ctx = Mock()
        ctx.obj = {"verbose": False}

        with patch("promptrek.cli.commands.generate.generate_command") as mock_generate:
            with patch("click.echo") as mock_echo:
                refresh_command(
                    ctx,
                    editor=None,
                    all_editors=False,
                    dry_run=True,
                    clear_cache=False,
                    variables=None,
                )

            # Should still call generate for both editors
            assert mock_generate.call_count == 2

            # Should print dry run message
            dry_run_calls = [
                call for call in mock_echo.call_args_list if "Dry run" in str(call)
            ]
            assert len(dry_run_calls) > 0

    def test_refresh_verbose_dry_run(self, tmp_path):
        """Test refresh in both verbose and dry run mode."""
        import os

        os.chdir(tmp_path)

        # Create metadata directory and file
        metadata_dir = tmp_path / ".promptrek"
        metadata_dir.mkdir()
        metadata_file = metadata_dir / "last-generation.yaml"

        # Create source file
        source_file = tmp_path / "project.promptrek.yaml"
        source_file.write_text("schema_version: 3.0.0\ncontent: test")

        # Create metadata
        metadata = {
            "source_file": str(source_file),
            "timestamp": "2025-01-01T00:00:00",
            "editors": ["claude", "copilot"],
            "output_dir": str(tmp_path),
            "variables": {},
        }
        metadata_file.write_text(yaml.dump(metadata))

        ctx = Mock()
        ctx.obj = {"verbose": True}  # Enable verbose

        with patch("promptrek.cli.commands.generate.generate_command") as mock_generate:
            with patch("click.echo") as mock_echo:
                refresh_command(
                    ctx,
                    editor=None,
                    all_editors=False,
                    dry_run=True,
                    clear_cache=False,
                    variables=None,
                )

            # Should call generate for both editors
            assert mock_generate.call_count == 2

            # Should print verbose output
            assert mock_echo.call_count > 5  # Multiple messages in verbose mode
