"""
Integration tests for sync functionality.
"""

import tempfile
from pathlib import Path

import yaml
from click.testing import CliRunner

from promptrek.cli.main import cli


class TestSyncIntegration:
    """Integration tests for sync command."""

    def test_full_sync_workflow(self):
        """Test complete sync workflow from CLI."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create Continue files structure
            rules_dir = temp_path / ".continue" / "rules"
            rules_dir.mkdir(parents=True)

            # Create config.yaml
            config_content = {
                "name": "Integration Test Assistant",
                "systemMessage": "Integration Test Assistant\n\nTesting the full workflow",
                "rules": ["Integration test rule", "Full workflow test"],
            }

            config_file = temp_path / "config.yaml"
            with open(config_file, "w") as f:
                yaml.dump(config_content, f)

            # Create rule files
            (rules_dir / "general.md").write_text(
                """# General Rules
- Use integration tests
- Test the full workflow
- Validate end-to-end functionality
"""
            )

            (rules_dir / "testing.md").write_text(
                """# Testing Rules
- Write comprehensive integration tests
- Test CLI commands
- Validate file operations
"""
            )

            output_file = temp_path / "integration.promptrek.yaml"

            # Run sync command through CLI
            runner = CliRunner()
            result = runner.invoke(
                cli,
                [
                    "sync",
                    "--source-dir",
                    str(temp_path),
                    "--editor",
                    "continue",
                    "--output",
                    str(output_file),
                ],
            )

            # Should succeed
            assert result.exit_code == 0
            assert "Synced continue configuration" in result.output

            # Check output file was created
            assert output_file.exists()

            # Validate content (V3 schema)
            with open(output_file, "r") as f:
                content = yaml.safe_load(f)

            assert content["schema_version"] == "3.0.0"
            assert (
                content["metadata"]["title"] == "Continue AI Assistant"
            )  # V3 uses default title

            # V3 uses documents instead of targets/instructions
            # general.md becomes main content, other files become documents
            assert "documents" in content
            assert len(content["documents"]) >= 1  # testing.md

            # Check general.md content is in main content field
            assert "content" in content
            assert content["content"] is not None
            assert "Use integration tests" in content["content"]

            # Check documents were parsed
            doc_names = [doc["name"] for doc in content["documents"]]
            assert "general" not in doc_names  # general.md is main content
            assert "testing" in doc_names

            # Check testing.md in documents
            testing_doc = next(
                (d for d in content["documents"] if d["name"] == "testing"), None
            )
            assert testing_doc is not None
            assert "Write comprehensive integration tests" in testing_doc["content"]

    def test_sync_dry_run_cli(self):
        """Test sync dry run through CLI."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create minimal Continue structure
            rules_dir = temp_path / ".continue" / "rules"
            rules_dir.mkdir(parents=True)

            (rules_dir / "general.md").write_text("# General\n- Dry run test")

            runner = CliRunner()
            result = runner.invoke(
                cli,
                [
                    "sync",
                    "--source-dir",
                    str(temp_path),
                    "--editor",
                    "continue",
                    "--dry-run",
                ],
            )

            # Should succeed and show dry run output
            assert result.exit_code == 0
            assert "Dry run mode" in result.output
            assert "would write to" in result.output

    def test_sync_error_handling_cli(self):
        """Test sync error handling through CLI."""
        runner = CliRunner()

        # Test with unsupported editor
        result = runner.invoke(
            cli, ["sync", "--source-dir", ".", "--editor", "fake_editor"]
        )

        assert result.exit_code == 1
        assert "Unsupported editor" in result.output

    def test_sync_preserves_variables(self):
        """Test that sync preserves variable references from original PrompTrek file."""
        import os

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create variables file
            var_dir = temp_path / ".promptrek"
            var_dir.mkdir(parents=True)
            var_file = var_dir / "variables.promptrek.yaml"
            var_file.write_text("PROJECT_NAME: TestProject\nAUTHOR: TestAuthor")

            # Create original PrompTrek file with variables
            promptrek_file = temp_path / "test.promptrek.yaml"
            original_content = {
                "schema_version": "3.1.0",
                "metadata": {
                    "title": "Test {{{ PROJECT_NAME }}}",
                    "description": "A test for {{{ PROJECT_NAME }}}",
                    "author": "{{{ AUTHOR }}}",
                    "version": "1.0.0",
                    "created": "2024-01-01",
                    "updated": "2024-01-01",
                },
                "content": "Welcome to {{{ PROJECT_NAME }}} by {{{ AUTHOR }}}",
            }

            with open(promptrek_file, "w") as f:
                yaml.dump(original_content, f)

            # Save current directory and change to temp directory
            # This is needed so that variables.promptrek.yaml is found
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_path)

                # Generate to Claude format (this will replace variables with values)
                runner = CliRunner()
                result = runner.invoke(
                    cli,
                    [
                        "generate",
                        "--editor",
                        "claude",
                        "--output",
                        str(temp_path),
                        str(promptrek_file),
                    ],
                )

                assert result.exit_code == 0, f"Generate failed: {result.output}"
            finally:
                os.chdir(original_cwd)

            # Check that generated file has values, not variables
            claude_file = temp_path / ".claude" / "CLAUDE.md"
            assert claude_file.exists()

            claude_content = claude_file.read_text()
            assert "TestProject" in claude_content
            assert "TestAuthor" in claude_content
            assert "{{{ PROJECT_NAME }}}" not in claude_content  # Variables replaced

            # Now sync back from Claude to PrompTrek
            # Sync to the original file so that variable restoration can compare
            # with the existing content
            synced_file = promptrek_file

            # Change back to temp directory for sync (to find variables file)
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_path)

                result = runner.invoke(
                    cli,
                    [
                        "sync",
                        "--source-dir",
                        str(temp_path),
                        "--editor",
                        "claude",
                        "--output",
                        str(synced_file),
                        "--force",  # Don't prompt for confirmation
                    ],
                )

                assert result.exit_code == 0, f"Sync failed: {result.output}"
            finally:
                os.chdir(original_cwd)

            # Check that synced file has variables restored, not concrete values
            with open(synced_file, "r") as f:
                synced_content = yaml.safe_load(f)

            # Variables should be restored in content
            assert "{{{ PROJECT_NAME }}}" in synced_content["content"]
            assert "{{{ AUTHOR }}}" in synced_content["content"]
            assert "TestProject" not in synced_content["content"]  # Value replaced back
            assert "TestAuthor" not in synced_content["content"]  # Value replaced back

            # Metadata should also have variables restored
            assert "{{{ PROJECT_NAME }}}" in synced_content["metadata"]["title"]
            assert "{{{ AUTHOR }}}" in synced_content["metadata"]["author"]
