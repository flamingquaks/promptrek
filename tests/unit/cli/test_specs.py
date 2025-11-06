"""Tests for spec CLI commands."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest
from click.testing import CliRunner

from promptrek.cli.commands.specs import list_specs_command, spec_export_command
from promptrek.core.exceptions import CLIError
from promptrek.utils.spec_manager import SpecManager


class TestListSpecsCommand:
    """Tests for list-specs command."""

    def test_list_specs_empty(self, tmp_path):
        """Test listing specs when none exist."""
        runner = CliRunner()
        ctx = MagicMock()
        ctx.obj = {"verbose": False}

        with runner.isolated_filesystem(temp_dir=tmp_path):
            list_specs_command(ctx)

    def test_list_specs_with_specs(self, tmp_path):
        """Test listing existing specs."""
        manager = SpecManager(tmp_path)

        # Create some specs
        spec1 = manager.create_spec(
            title="Test Spec 1",
            content="Content 1",
            source_command="/promptrek.spec.create",
            summary="First spec",
            tags=["test", "example"],
        )
        spec2 = manager.create_spec(
            title="Test Spec 2",
            content="Content 2",
            source_command="/promptrek.spec.plan",
        )

        runner = CliRunner()
        ctx = MagicMock()
        ctx.obj = {"verbose": False}

        with runner.isolated_filesystem(temp_dir=tmp_path):
            # Change to tmp_path directory
            import os

            os.chdir(tmp_path)

            list_specs_command(ctx)

    def test_list_specs_verbose(self, tmp_path):
        """Test listing specs in verbose mode."""
        manager = SpecManager(tmp_path)

        spec = manager.create_spec(
            title="Verbose Test",
            content="Content",
            source_command="/test",
        )

        runner = CliRunner()
        ctx = MagicMock()
        ctx.obj = {"verbose": True}

        with runner.isolated_filesystem(temp_dir=tmp_path):
            import os

            os.chdir(tmp_path)

            list_specs_command(ctx)

    def test_list_specs_with_linked_specs(self, tmp_path):
        """Test listing specs with linked specs."""
        manager = SpecManager(tmp_path)

        spec1 = manager.create_spec(
            title="Base Spec",
            content="Base content",
            source_command="/promptrek.spec.create",
        )

        # Manually create a spec with linked_specs
        from promptrek.core.models import SpecMetadata, UniversalSpecFormat

        spec2 = SpecMetadata(
            id="linked1",
            title="Linked Spec",
            path="linked.md",
            source_command="/promptrek.spec.plan",
            created="2025-11-05T10:00:00",
            linked_specs=[spec1.id],
        )

        usf = manager.load_registry()
        usf.specs.append(spec2)
        manager.save_registry(usf)

        runner = CliRunner()
        ctx = MagicMock()
        ctx.obj = {"verbose": False}

        with runner.isolated_filesystem(temp_dir=tmp_path):
            import os

            os.chdir(tmp_path)

            list_specs_command(ctx)

    def test_list_specs_error_handling(self, tmp_path):
        """Test error handling in list-specs command."""
        runner = CliRunner()
        ctx = MagicMock()
        ctx.obj = {"verbose": False}

        # Manually create a malformed registry
        manager = SpecManager(tmp_path)
        manager.ensure_specs_directory()

        with open(manager.registry_path, "w") as f:
            f.write("{ invalid yaml ][")

        with runner.isolated_filesystem(temp_dir=tmp_path):
            import os

            os.chdir(tmp_path)

            with pytest.raises(CLIError):
                list_specs_command(ctx)

    def test_list_specs_error_verbose(self, tmp_path):
        """Test error handling in verbose mode."""
        runner = CliRunner()
        ctx = MagicMock()
        ctx.obj = {"verbose": True}

        # Manually create a malformed registry
        manager = SpecManager(tmp_path)
        manager.ensure_specs_directory()

        with open(manager.registry_path, "w") as f:
            f.write("{ invalid yaml ][")

        with runner.isolated_filesystem(temp_dir=tmp_path):
            import os

            os.chdir(tmp_path)

            # In verbose mode, the original exception should be raised
            with pytest.raises(ValueError):
                list_specs_command(ctx)


class TestSpecExportCommand:
    """Tests for spec export command."""

    def test_export_spec_clean(self, tmp_path):
        """Test exporting spec with clean option."""
        manager = SpecManager(tmp_path)

        spec = manager.create_spec(
            title="Export Test",
            content="Content to export.",
            source_command="/promptrek.spec.create",
            summary="Export summary",
        )

        output_path = tmp_path / "exported.md"

        runner = CliRunner()
        ctx = MagicMock()
        ctx.obj = {"verbose": False}

        with runner.isolated_filesystem(temp_dir=tmp_path):
            import os

            os.chdir(tmp_path)

            spec_export_command(ctx, spec.id, output_path, clean=True)

        assert output_path.exists()

        content = output_path.read_text()
        assert "Content to export." in content
        assert "**ID:**" not in content  # Clean mode removes metadata

    def test_export_spec_with_metadata(self, tmp_path):
        """Test exporting spec with metadata."""
        manager = SpecManager(tmp_path)

        spec = manager.create_spec(
            title="Export Test",
            content="Content.",
            source_command="/promptrek.spec.create",
        )

        output_path = tmp_path / "exported.md"

        runner = CliRunner()
        ctx = MagicMock()
        ctx.obj = {"verbose": False}

        with runner.isolated_filesystem(temp_dir=tmp_path):
            import os

            os.chdir(tmp_path)

            spec_export_command(ctx, spec.id, output_path, clean=False)

        content = output_path.read_text()
        assert f"**ID:** {spec.id}" in content  # Metadata kept

    def test_export_spec_default_output(self, tmp_path):
        """Test exporting spec with default output path."""
        manager = SpecManager(tmp_path)

        spec = manager.create_spec(
            title="Default Export",
            content="Content.",
            source_command="/promptrek.spec.create",
        )

        runner = CliRunner()
        ctx = MagicMock()
        ctx.obj = {"verbose": False}

        with runner.isolated_filesystem(temp_dir=tmp_path):
            import os

            os.chdir(tmp_path)

            spec_export_command(ctx, spec.id, None, clean=True)

        # Check that a file was created with default name
        expected_filename = spec.path.replace(".md", "-export.md")
        expected_path = tmp_path / expected_filename
        assert expected_path.exists()

    def test_export_spec_nonexistent(self, tmp_path):
        """Test exporting nonexistent spec."""
        manager = SpecManager(tmp_path)
        manager.ensure_specs_directory()

        output_path = tmp_path / "exported.md"

        runner = CliRunner()
        ctx = MagicMock()
        ctx.obj = {"verbose": False}

        with runner.isolated_filesystem(temp_dir=tmp_path):
            import os

            os.chdir(tmp_path)

            with pytest.raises(CLIError) as exc_info:
                spec_export_command(ctx, "nonexistent", output_path, clean=True)

            assert "not found" in str(exc_info.value)

    def test_export_spec_error_verbose(self, tmp_path):
        """Test export error handling in verbose mode."""
        manager = SpecManager(tmp_path)
        manager.ensure_specs_directory()

        output_path = tmp_path / "exported.md"

        runner = CliRunner()
        ctx = MagicMock()
        ctx.obj = {"verbose": True}

        with runner.isolated_filesystem(temp_dir=tmp_path):
            import os

            os.chdir(tmp_path)

            # CLIError is always raised for non-existent specs
            with pytest.raises(CLIError) as exc_info:
                spec_export_command(ctx, "nonexistent", output_path, clean=True)

            assert "not found" in str(exc_info.value)


class TestSpecCommandsIntegration:
    """Integration tests for spec CLI commands."""

    def test_create_list_export_workflow(self, tmp_path):
        """Test complete workflow: create, list, export."""
        manager = SpecManager(tmp_path)

        # Create a spec
        spec = manager.create_spec(
            title="Workflow Test",
            content="Workflow content.",
            source_command="/promptrek.spec.create",
            tags=["workflow", "test"],
        )

        runner = CliRunner()
        ctx = MagicMock()
        ctx.obj = {"verbose": False}

        with runner.isolated_filesystem(temp_dir=tmp_path):
            import os

            os.chdir(tmp_path)

            # List specs
            list_specs_command(ctx)

            # Export spec
            output_path = Path("exported.md")
            spec_export_command(ctx, spec.id, output_path, clean=True)

            assert output_path.exists()
            content = output_path.read_text()
            assert "Workflow content." in content

    def test_multiple_specs_workflow(self, tmp_path):
        """Test workflow with multiple specs."""
        manager = SpecManager(tmp_path)

        # Create multiple specs
        specs = []
        for i in range(3):
            spec = manager.create_spec(
                title=f"Spec {i+1}",
                content=f"Content {i+1}",
                source_command="/promptrek.spec.create",
            )
            specs.append(spec)

        runner = CliRunner()
        ctx = MagicMock()
        ctx.obj = {"verbose": False}

        with runner.isolated_filesystem(temp_dir=tmp_path):
            import os

            os.chdir(tmp_path)

            # List all specs
            list_specs_command(ctx)

            # Export each spec
            for i, spec in enumerate(specs):
                output_path = Path(f"export-{i+1}.md")
                spec_export_command(ctx, spec.id, output_path, clean=True)

                assert output_path.exists()
                content = output_path.read_text()
                assert f"Content {i+1}" in content
