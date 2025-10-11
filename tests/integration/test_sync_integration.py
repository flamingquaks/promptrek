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

            # Validate content (V2 schema)
            with open(output_file, "r") as f:
                content = yaml.safe_load(f)

            assert content["schema_version"] == "2.0.0"
            assert (
                content["metadata"]["title"] == "Continue AI Assistant"
            )  # V2 uses default title

            # V2 uses documents instead of targets/instructions
            assert "documents" in content
            assert len(content["documents"]) >= 2  # general.md and testing.md

            # Check documents were parsed
            doc_names = [doc["name"] for doc in content["documents"]]
            assert "general" in doc_names
            assert "testing" in doc_names

            # Check content in documents
            general_doc = next(
                (d for d in content["documents"] if d["name"] == "general"), None
            )
            assert general_doc is not None
            assert "Use integration tests" in general_doc["content"]

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
