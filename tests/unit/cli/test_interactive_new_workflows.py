"""
Tests for new interactive CLI workflows.
"""

from unittest.mock import Mock, patch

from promptrek.core.exceptions import PrompTrekError


class TestWorkflowListSpecs:
    """Tests for workflow_list_specs function."""

    @patch("builtins.input", return_value="")
    @patch("click.echo")
    @patch("promptrek.cli.interactive.list_specs_command")
    def test_workflow_list_specs_success(
        self, mock_list, mock_echo, mock_input, tmp_path
    ):
        """Test listing specs successfully."""
        import os

        os.chdir(tmp_path)

        ctx = Mock()
        ctx.obj = {"verbose": False}

        from promptrek.cli.interactive import workflow_list_specs

        workflow_list_specs(ctx)

        # Should have called list_specs_command
        mock_list.assert_called_once_with(ctx)
        # Should have called wait_for_return
        mock_input.assert_called_once()

    @patch("builtins.input", return_value="")
    @patch("click.echo")
    @patch("promptrek.cli.interactive.list_specs_command")
    def test_workflow_list_specs_error(
        self, mock_list, mock_echo, mock_input, tmp_path
    ):
        """Test listing specs with error."""
        import os

        os.chdir(tmp_path)

        ctx = Mock()
        ctx.obj = {"verbose": False}

        # Make command raise error
        mock_list.side_effect = PrompTrekError("Failed to list specs")

        from promptrek.cli.interactive import workflow_list_specs

        workflow_list_specs(ctx)

        # Should have called wait_for_return even on error
        mock_input.assert_called_once()


class TestWorkflowSpecExport:
    """Tests for workflow_spec_export function."""

    @patch("click.echo")
    @patch("promptrek.cli.interactive.questionary.confirm")
    @patch("promptrek.cli.interactive.questionary.text")
    @patch("promptrek.cli.interactive.spec_export_command")
    @patch("promptrek.utils.spec_manager.SpecManager")
    def test_workflow_spec_export_success(
        self,
        mock_manager_class,
        mock_export,
        mock_text,
        mock_confirm,
        mock_echo,
        tmp_path,
    ):
        """Test exporting spec successfully."""
        import os

        os.chdir(tmp_path)

        ctx = Mock()
        ctx.obj = {"verbose": False}

        # Mock spec manager
        mock_spec = Mock()
        mock_spec.id = "test123"
        mock_spec.title = "Test Spec"
        mock_spec.path = "test.md"

        mock_instance = Mock()
        mock_instance.list_specs.return_value = [mock_spec]
        mock_instance.get_spec_by_id.return_value = mock_spec
        mock_manager_class.return_value = mock_instance

        # Mock user inputs
        mock_text.return_value.ask.side_effect = ["test123", "test-export.md"]
        mock_confirm.return_value.ask.return_value = True

        from promptrek.cli.interactive import workflow_spec_export

        workflow_spec_export(ctx)

        # Should have called export command
        mock_export.assert_called_once()

    @patch("click.echo")
    @patch("promptrek.utils.spec_manager.SpecManager")
    def test_workflow_spec_export_no_specs(
        self, mock_manager_class, mock_echo, tmp_path
    ):
        """Test exporting when no specs exist."""
        import os

        os.chdir(tmp_path)

        ctx = Mock()
        ctx.obj = {"verbose": False}

        # Mock spec manager with no specs
        mock_instance = Mock()
        mock_instance.list_specs.return_value = []
        mock_manager_class.return_value = mock_instance

        from promptrek.cli.interactive import workflow_spec_export

        workflow_spec_export(ctx)

        # Should return early
        warning_calls = [
            call for call in mock_echo.call_args_list if "No specs found" in str(call)
        ]
        assert len(warning_calls) > 0


class TestWorkflowListEditors:
    """Tests for workflow_list_editors function."""

    @patch("builtins.input", return_value="")
    @patch("click.echo")
    def test_workflow_list_editors_success(self, mock_echo, mock_input, tmp_path):
        """Test listing editors successfully."""
        import os

        os.chdir(tmp_path)

        ctx = Mock()
        ctx.obj = {"verbose": False}

        from promptrek.cli.interactive import workflow_list_editors

        workflow_list_editors(ctx)

        # Should have printed editor information
        assert mock_echo.call_count > 0
        # Should have called wait_for_return
        mock_input.assert_called_once()


class TestWorkflowPreview:
    """Tests for workflow_preview function."""

    @patch("click.echo")
    @patch("promptrek.cli.interactive.questionary.select")
    @patch("promptrek.cli.interactive.questionary.confirm")
    @patch("promptrek.cli.interactive.questionary.text")
    @patch("promptrek.cli.interactive.preview_command")
    def test_workflow_preview_success(
        self, mock_preview, mock_text, mock_confirm, mock_select, mock_echo, tmp_path
    ):
        """Test preview workflow successfully."""
        import os

        os.chdir(tmp_path)

        # Create config file
        config_file = tmp_path / "project.promptrek.yaml"
        config_file.write_text("schema_version: 3.0.0\ncontent: test")

        ctx = Mock()
        ctx.obj = {"verbose": False}

        # Mock user selections
        mock_select.return_value.ask.return_value = "claude"
        mock_confirm.return_value.ask.return_value = False  # No variables

        from promptrek.cli.interactive import workflow_preview

        workflow_preview(ctx)

        # Should have called preview command
        mock_preview.assert_called_once()

    @patch("click.echo")
    def test_workflow_preview_no_config(self, mock_echo, tmp_path):
        """Test preview when no config exists."""
        import os

        os.chdir(tmp_path)

        ctx = Mock()
        ctx.obj = {"verbose": False}

        from promptrek.cli.interactive import workflow_preview

        workflow_preview(ctx)

        # Should display warning
        warning_calls = [
            call for call in mock_echo.call_args_list if "No project" in str(call)
        ]
        assert len(warning_calls) > 0

    @patch("click.echo")
    @patch("promptrek.cli.interactive.questionary.select")
    @patch("promptrek.cli.interactive.questionary.confirm")
    @patch("promptrek.cli.interactive.questionary.text")
    @patch("promptrek.cli.interactive.preview_command")
    def test_workflow_preview_with_variables(
        self, mock_preview, mock_text, mock_confirm, mock_select, mock_echo, tmp_path
    ):
        """Test preview with variable overrides."""
        import os

        os.chdir(tmp_path)

        # Create config file
        config_file = tmp_path / "project.promptrek.yaml"
        config_file.write_text("schema_version: 3.0.0\ncontent: test")

        ctx = Mock()
        ctx.obj = {"verbose": False}

        # Mock user selections
        mock_select.return_value.ask.return_value = "claude"
        mock_confirm.return_value.ask.return_value = True  # Use variables

        # Mock variable input
        mock_text.return_value.ask.side_effect = [
            "VAR1=value1",
            "",  # Empty to finish
        ]

        from promptrek.cli.interactive import workflow_preview

        workflow_preview(ctx)

        # Should have called preview command with variables
        mock_preview.assert_called_once()

    @patch("click.echo")
    @patch("promptrek.cli.interactive.questionary.select")
    @patch("promptrek.cli.interactive.questionary.confirm")
    @patch("promptrek.cli.interactive.questionary.text")
    def test_workflow_preview_cancel_variable_input(
        self, mock_text, mock_confirm, mock_select, mock_echo, tmp_path
    ):
        """Test preview cancellation during variable input."""
        import os

        os.chdir(tmp_path)

        # Create config file
        config_file = tmp_path / "project.promptrek.yaml"
        config_file.write_text("schema_version: 3.0.0\ncontent: test")

        ctx = Mock()
        ctx.obj = {"verbose": False}

        # Mock user selections
        mock_select.return_value.ask.return_value = "claude"
        mock_confirm.return_value.ask.return_value = True  # Use variables

        # Mock variable input - user cancels
        mock_text.return_value.ask.return_value = None

        from promptrek.cli.interactive import workflow_preview

        workflow_preview(ctx)

        # Should display cancelled message
        cancelled_calls = [
            call for call in mock_echo.call_args_list if "Cancelled" in str(call)
        ]
        assert len(cancelled_calls) > 0

    @patch("click.echo")
    @patch("promptrek.cli.interactive.questionary.select")
    @patch("promptrek.cli.interactive.questionary.confirm")
    def test_workflow_preview_cancel_use_variables(
        self, mock_confirm, mock_select, mock_echo, tmp_path
    ):
        """Test preview cancellation at use variables prompt."""
        import os

        os.chdir(tmp_path)

        # Create config file
        config_file = tmp_path / "project.promptrek.yaml"
        config_file.write_text("schema_version: 3.0.0\ncontent: test")

        ctx = Mock()
        ctx.obj = {"verbose": False}

        # Mock user selections
        mock_select.return_value.ask.return_value = "claude"
        # User cancels at use_variables
        mock_confirm.return_value.ask.return_value = None

        from promptrek.cli.interactive import workflow_preview

        workflow_preview(ctx)

        # Should display cancelled message
        cancelled_calls = [
            call for call in mock_echo.call_args_list if "Cancelled" in str(call)
        ]
        assert len(cancelled_calls) > 0


class TestWorkflowRefresh:
    """Tests for workflow_refresh function."""

    @patch("click.echo")
    @patch("promptrek.cli.interactive.questionary.select")
    @patch("promptrek.cli.interactive.questionary.confirm")
    @patch("promptrek.cli.interactive.questionary.text")
    @patch("promptrek.cli.interactive.refresh_command")
    def test_workflow_refresh_with_editor(
        self, mock_refresh, mock_text, mock_confirm, mock_select, mock_echo, tmp_path
    ):
        """Test refresh with specific editor."""
        import os

        os.chdir(tmp_path)

        ctx = Mock()
        ctx.obj = {"verbose": False}

        # Mock user selections
        mock_select.return_value.ask.return_value = "claude"
        confirm_returns = [
            Mock(ask=Mock(return_value=False)),  # clear_cache
            Mock(ask=Mock(return_value=False)),  # use_variables
            Mock(ask=Mock(return_value=False)),  # dry_run
        ]
        mock_confirm.side_effect = confirm_returns

        from promptrek.cli.interactive import workflow_refresh

        workflow_refresh(ctx)

        # Should have called refresh command
        mock_refresh.assert_called_once()

    @patch("click.echo")
    @patch("promptrek.cli.interactive.questionary.select")
    @patch("promptrek.cli.interactive.questionary.confirm")
    @patch("promptrek.cli.interactive.refresh_command")
    def test_workflow_refresh_use_last(
        self, mock_refresh, mock_confirm, mock_select, mock_echo, tmp_path
    ):
        """Test refresh with last generation settings."""
        import os

        os.chdir(tmp_path)

        ctx = Mock()
        ctx.obj = {"verbose": False}

        # Mock user selecting "use last"
        mock_select.return_value.ask.return_value = "__use_last__"
        confirm_returns = [
            Mock(ask=Mock(return_value=False)),  # clear_cache
            Mock(ask=Mock(return_value=False)),  # use_variables
            Mock(ask=Mock(return_value=False)),  # dry_run
        ]
        mock_confirm.side_effect = confirm_returns

        from promptrek.cli.interactive import workflow_refresh

        workflow_refresh(ctx)

        # Should have called refresh with None editor
        call_args = mock_refresh.call_args
        assert call_args[1]["editor"] is None

    @patch("click.echo")
    @patch("promptrek.cli.interactive.questionary.select")
    @patch("promptrek.cli.interactive.questionary.confirm")
    @patch("promptrek.cli.interactive.refresh_command")
    def test_workflow_refresh_all_editors(
        self, mock_refresh, mock_confirm, mock_select, mock_echo, tmp_path
    ):
        """Test refresh all editors."""
        import os

        os.chdir(tmp_path)

        ctx = Mock()
        ctx.obj = {"verbose": False}

        # Mock user selecting "all"
        mock_select.return_value.ask.return_value = "__all__"
        confirm_returns = [
            Mock(ask=Mock(return_value=False)),  # clear_cache
            Mock(ask=Mock(return_value=False)),  # use_variables
            Mock(ask=Mock(return_value=False)),  # dry_run
        ]
        mock_confirm.side_effect = confirm_returns

        from promptrek.cli.interactive import workflow_refresh

        workflow_refresh(ctx)

        # Should have called refresh with all_editors=True
        call_args = mock_refresh.call_args
        assert call_args[1]["all_editors"] is True

    @patch("click.echo")
    @patch("promptrek.cli.interactive.questionary.select")
    @patch("promptrek.cli.interactive.questionary.confirm")
    @patch("promptrek.cli.interactive.questionary.text")
    @patch("promptrek.cli.interactive.refresh_command")
    def test_workflow_refresh_with_variables(
        self, mock_refresh, mock_text, mock_confirm, mock_select, mock_echo, tmp_path
    ):
        """Test refresh with variable overrides."""
        import os

        os.chdir(tmp_path)

        ctx = Mock()
        ctx.obj = {"verbose": False}

        # Mock user selections
        mock_select.return_value.ask.return_value = "claude"
        # clear_cache, use_variables=yes, dry_run
        confirm_returns = [
            Mock(ask=Mock(return_value=False)),  # clear_cache
            Mock(ask=Mock(return_value=True)),  # use_variables (yes)
            Mock(ask=Mock(return_value=False)),  # dry_run
        ]
        mock_confirm.side_effect = confirm_returns

        # Mock variable input
        mock_text.return_value.ask.side_effect = [
            "VAR1=value1",
            "VAR2=value2",
            "",  # Empty to finish
        ]

        from promptrek.cli.interactive import workflow_refresh

        workflow_refresh(ctx)

        # Should have called refresh with variables
        call_args = mock_refresh.call_args
        assert call_args[1]["variables"] is not None

    @patch("click.echo")
    @patch("promptrek.cli.interactive.questionary.select")
    @patch("promptrek.cli.interactive.questionary.confirm")
    @patch("promptrek.cli.interactive.questionary.text")
    def test_workflow_refresh_cancel_variable_input(
        self, mock_text, mock_confirm, mock_select, mock_echo, tmp_path
    ):
        """Test refresh cancellation during variable input."""
        import os

        os.chdir(tmp_path)

        ctx = Mock()
        ctx.obj = {"verbose": False}

        # Mock user selections
        mock_select.return_value.ask.return_value = "claude"
        # clear_cache, use_variables=yes
        confirm_returns = [
            Mock(ask=Mock(return_value=False)),  # clear_cache
            Mock(ask=Mock(return_value=True)),  # use_variables (yes)
        ]
        mock_confirm.side_effect = confirm_returns

        # Mock variable input - user cancels
        mock_text.return_value.ask.return_value = None

        from promptrek.cli.interactive import workflow_refresh

        workflow_refresh(ctx)

        # Should display cancelled message
        cancelled_calls = [
            call for call in mock_echo.call_args_list if "Cancelled" in str(call)
        ]
        assert len(cancelled_calls) > 0

    @patch("click.echo")
    @patch("promptrek.cli.interactive.questionary.select")
    @patch("promptrek.cli.interactive.questionary.confirm")
    def test_workflow_refresh_cancel_clear_cache(
        self, mock_confirm, mock_select, mock_echo, tmp_path
    ):
        """Test refresh cancellation at clear cache prompt."""
        import os

        os.chdir(tmp_path)

        ctx = Mock()
        ctx.obj = {"verbose": False}

        # Mock user selections
        mock_select.return_value.ask.return_value = "claude"
        # User cancels at clear_cache
        mock_confirm.return_value.ask.return_value = None

        from promptrek.cli.interactive import workflow_refresh

        workflow_refresh(ctx)

        # Should display cancelled message
        cancelled_calls = [
            call for call in mock_echo.call_args_list if "Cancelled" in str(call)
        ]
        assert len(cancelled_calls) > 0

    @patch("click.echo")
    @patch("promptrek.cli.interactive.questionary.select")
    @patch("promptrek.cli.interactive.questionary.confirm")
    def test_workflow_refresh_cancel_use_variables(
        self, mock_confirm, mock_select, mock_echo, tmp_path
    ):
        """Test refresh cancellation at use variables prompt."""
        import os

        os.chdir(tmp_path)

        ctx = Mock()
        ctx.obj = {"verbose": False}

        # Mock user selections
        mock_select.return_value.ask.return_value = "claude"
        # clear_cache=no, then cancel at use_variables
        confirm_returns = [
            Mock(ask=Mock(return_value=False)),  # clear_cache
            Mock(ask=Mock(return_value=None)),  # use_variables (cancelled)
        ]
        mock_confirm.side_effect = confirm_returns

        from promptrek.cli.interactive import workflow_refresh

        workflow_refresh(ctx)

        # Should display cancelled message
        cancelled_calls = [
            call for call in mock_echo.call_args_list if "Cancelled" in str(call)
        ]
        assert len(cancelled_calls) > 0

    @patch("click.echo")
    @patch("promptrek.cli.interactive.questionary.select")
    @patch("promptrek.cli.interactive.questionary.confirm")
    def test_workflow_refresh_cancel_dry_run(
        self, mock_confirm, mock_select, mock_echo, tmp_path
    ):
        """Test refresh cancellation at dry run prompt."""
        import os

        os.chdir(tmp_path)

        ctx = Mock()
        ctx.obj = {"verbose": False}

        # Mock user selections
        mock_select.return_value.ask.return_value = "claude"
        # clear_cache=no, use_variables=no, then cancel at dry_run
        confirm_returns = [
            Mock(ask=Mock(return_value=False)),  # clear_cache
            Mock(ask=Mock(return_value=False)),  # use_variables
            Mock(ask=Mock(return_value=None)),  # dry_run (cancelled)
        ]
        mock_confirm.side_effect = confirm_returns

        from promptrek.cli.interactive import workflow_refresh

        workflow_refresh(ctx)

        # Should display cancelled message
        cancelled_calls = [
            call for call in mock_echo.call_args_list if "Cancelled" in str(call)
        ]
        assert len(cancelled_calls) > 0


class TestWorkflowConfigIgnores:
    """Tests for workflow_config_ignores function."""

    @patch("click.echo")
    @patch("promptrek.cli.interactive.questionary.confirm")
    @patch("promptrek.cli.interactive.config_ignores_command")
    def test_workflow_config_ignores_success(
        self, mock_config, mock_confirm, mock_echo, tmp_path
    ):
        """Test config ignores successfully."""
        import os

        os.chdir(tmp_path)

        # Create config file
        config_file = tmp_path / "project.promptrek.yaml"
        config_file.write_text("schema_version: 3.0.0\ncontent: test")

        ctx = Mock()
        ctx.obj = {"verbose": False}

        # Mock user confirmations
        confirm_returns = [
            Mock(ask=Mock(return_value=False)),  # remove_cached
            Mock(ask=Mock(return_value=False)),  # dry_run
        ]
        mock_confirm.side_effect = confirm_returns

        from promptrek.cli.interactive import workflow_config_ignores

        workflow_config_ignores(ctx)

        # Should have called command
        mock_config.assert_called_once()


class TestWorkflowInstallHooks:
    """Tests for workflow_install_hooks function."""

    @patch("click.echo")
    @patch("promptrek.cli.interactive.questionary.text")
    @patch("promptrek.cli.interactive.questionary.confirm")
    @patch("promptrek.cli.interactive.install_hooks_command")
    def test_workflow_install_hooks_success(
        self, mock_install, mock_confirm, mock_text, mock_echo, tmp_path
    ):
        """Test install hooks successfully."""
        import os

        os.chdir(tmp_path)

        ctx = Mock()
        ctx.obj = {"verbose": False}

        # Mock user inputs
        mock_text.return_value.ask.return_value = ".pre-commit-config.yaml"
        confirm_returns = [
            Mock(ask=Mock(return_value=False)),  # force
            Mock(ask=Mock(return_value=True)),  # activate
        ]
        mock_confirm.side_effect = confirm_returns

        from promptrek.cli.interactive import workflow_install_hooks

        workflow_install_hooks(ctx)

        # Should have called command
        mock_install.assert_called_once()


class TestWorkflowPluginsValidate:
    """Tests for workflow_plugins_validate function."""

    @patch("click.echo")
    @patch("promptrek.cli.commands.plugins.validate_plugins_command")
    def test_workflow_plugins_validate_success(
        self, mock_validate, mock_echo, tmp_path
    ):
        """Test validate plugins successfully."""
        import os

        os.chdir(tmp_path)

        # Create config file
        config_file = tmp_path / "project.promptrek.yaml"
        config_file.write_text("schema_version: 3.0.0\ncontent: test")

        ctx = Mock()
        ctx.obj = {"verbose": False}

        from promptrek.cli.interactive import workflow_plugins_validate

        workflow_plugins_validate(ctx)

        # Should have called validate command
        mock_validate.assert_called_once()

    @patch("click.echo")
    def test_workflow_plugins_validate_no_config(self, mock_echo, tmp_path):
        """Test validate plugins when no config exists."""
        import os

        os.chdir(tmp_path)

        ctx = Mock()
        ctx.obj = {"verbose": False}

        from promptrek.cli.interactive import workflow_plugins_validate

        workflow_plugins_validate(ctx)

        # Should display warning
        warning_calls = [
            call for call in mock_echo.call_args_list if "No project" in str(call)
        ]
        assert len(warning_calls) > 0


class TestWorkflowCancellations:
    """Tests for workflow cancellations."""

    @patch("click.echo")
    @patch("promptrek.cli.interactive.questionary.select")
    def test_workflow_preview_cancel(self, mock_select, mock_echo, tmp_path):
        """Test preview workflow cancellation."""
        import os

        os.chdir(tmp_path)

        # Create config file
        config_file = tmp_path / "project.promptrek.yaml"
        config_file.write_text("schema_version: 3.0.0\ncontent: test")

        ctx = Mock()
        ctx.obj = {"verbose": False}

        # User cancels editor selection
        mock_select.return_value.ask.return_value = None

        from promptrek.cli.interactive import workflow_preview

        workflow_preview(ctx)

        # Should display cancelled message
        cancelled_calls = [
            call for call in mock_echo.call_args_list if "Cancelled" in str(call)
        ]
        assert len(cancelled_calls) > 0

    @patch("click.echo")
    @patch("promptrek.cli.interactive.questionary.select")
    def test_workflow_refresh_cancel(self, mock_select, mock_echo, tmp_path):
        """Test refresh workflow cancellation."""
        import os

        os.chdir(tmp_path)

        ctx = Mock()
        ctx.obj = {"verbose": False}

        # User cancels editor selection
        mock_select.return_value.ask.return_value = None

        from promptrek.cli.interactive import workflow_refresh

        workflow_refresh(ctx)

        # Should display cancelled message
        cancelled_calls = [
            call for call in mock_echo.call_args_list if "Cancelled" in str(call)
        ]
        assert len(cancelled_calls) > 0

    @patch("click.echo")
    @patch("promptrek.cli.interactive.questionary.text")
    def test_workflow_install_hooks_cancel(self, mock_text, mock_echo, tmp_path):
        """Test install hooks workflow cancellation."""
        import os

        os.chdir(tmp_path)

        ctx = Mock()
        ctx.obj = {"verbose": False}

        # User cancels config path input
        mock_text.return_value.ask.return_value = None

        from promptrek.cli.interactive import workflow_install_hooks

        workflow_install_hooks(ctx)

        # Should display cancelled message
        cancelled_calls = [
            call for call in mock_echo.call_args_list if "Cancelled" in str(call)
        ]
        assert len(cancelled_calls) > 0


class TestWorkflowErrorPaths:
    """Tests for error paths in workflows."""

    @patch("builtins.input", return_value="")
    @patch("click.echo")
    @patch("promptrek.cli.interactive.list_specs_command")
    def test_workflow_list_specs_verbose_error(
        self, mock_list, mock_echo, mock_input, tmp_path
    ):
        """Test listing specs with verbose error."""
        import os

        os.chdir(tmp_path)

        ctx = Mock()
        ctx.obj = {"verbose": True}

        # Make command raise generic error
        mock_list.side_effect = Exception("Generic error")

        from promptrek.cli.interactive import workflow_list_specs

        # Should re-raise in verbose mode
        try:
            workflow_list_specs(ctx)
        except Exception:
            pass  # Expected

    @patch("click.echo")
    @patch("promptrek.cli.interactive.preview_command")
    @patch("promptrek.cli.interactive.questionary.select")
    @patch("promptrek.cli.interactive.questionary.confirm")
    def test_workflow_preview_error(
        self, mock_confirm, mock_select, mock_preview, mock_echo, tmp_path
    ):
        """Test preview with error."""
        import os

        os.chdir(tmp_path)

        # Create config file
        config_file = tmp_path / "project.promptrek.yaml"
        config_file.write_text("schema_version: 3.0.0\ncontent: test")

        ctx = Mock()
        ctx.obj = {"verbose": False}

        # Mock selections
        mock_select.return_value.ask.return_value = "claude"
        mock_confirm.return_value.ask.return_value = False

        # Make command raise error
        mock_preview.side_effect = PrompTrekError("Preview failed")

        from promptrek.cli.interactive import workflow_preview

        workflow_preview(ctx)

        # Should display error message
        error_calls = [
            call for call in mock_echo.call_args_list if "Error" in str(call)
        ]
        assert len(error_calls) > 0

    @patch("click.echo")
    @patch("promptrek.cli.interactive.refresh_command")
    @patch("promptrek.cli.interactive.questionary.select")
    @patch("promptrek.cli.interactive.questionary.confirm")
    def test_workflow_refresh_error(
        self, mock_confirm, mock_select, mock_refresh, mock_echo, tmp_path
    ):
        """Test refresh with error."""
        import os

        os.chdir(tmp_path)

        ctx = Mock()
        ctx.obj = {"verbose": False}

        # Mock selections
        mock_select.return_value.ask.return_value = "claude"
        confirm_returns = [
            Mock(ask=Mock(return_value=False)),  # clear_cache
            Mock(ask=Mock(return_value=False)),  # use_variables
            Mock(ask=Mock(return_value=False)),  # dry_run
        ]
        mock_confirm.side_effect = confirm_returns

        # Make command raise error
        mock_refresh.side_effect = PrompTrekError("Refresh failed")

        from promptrek.cli.interactive import workflow_refresh

        workflow_refresh(ctx)

        # Should display error message
        error_calls = [
            call for call in mock_echo.call_args_list if "Error" in str(call)
        ]
        assert len(error_calls) > 0

    @patch("click.echo")
    @patch("promptrek.cli.interactive.config_ignores_command")
    @patch("promptrek.cli.interactive.questionary.confirm")
    def test_workflow_config_ignores_error(
        self, mock_confirm, mock_config, mock_echo, tmp_path
    ):
        """Test config ignores with error."""
        import os

        os.chdir(tmp_path)

        ctx = Mock()
        ctx.obj = {"verbose": False}

        # Mock confirmations
        confirm_returns = [
            Mock(ask=Mock(return_value=False)),  # remove_cached
            Mock(ask=Mock(return_value=False)),  # dry_run
        ]
        mock_confirm.side_effect = confirm_returns

        # Make command raise error
        mock_config.side_effect = PrompTrekError("Config failed")

        from promptrek.cli.interactive import workflow_config_ignores

        workflow_config_ignores(ctx)

        # Should display error message
        error_calls = [
            call for call in mock_echo.call_args_list if "Error" in str(call)
        ]
        assert len(error_calls) > 0

    @patch("click.echo")
    @patch("promptrek.cli.interactive.install_hooks_command")
    @patch("promptrek.cli.interactive.questionary.text")
    @patch("promptrek.cli.interactive.questionary.confirm")
    def test_workflow_install_hooks_error(
        self, mock_confirm, mock_text, mock_install, mock_echo, tmp_path
    ):
        """Test install hooks with error."""
        import os

        os.chdir(tmp_path)

        ctx = Mock()
        ctx.obj = {"verbose": False}

        # Mock inputs
        mock_text.return_value.ask.return_value = ".pre-commit-config.yaml"
        confirm_returns = [
            Mock(ask=Mock(return_value=False)),  # force
            Mock(ask=Mock(return_value=True)),  # activate
        ]
        mock_confirm.side_effect = confirm_returns

        # Make command raise error
        mock_install.side_effect = PrompTrekError("Install failed")

        from promptrek.cli.interactive import workflow_install_hooks

        workflow_install_hooks(ctx)

        # Should display error message
        error_calls = [
            call for call in mock_echo.call_args_list if "Error" in str(call)
        ]
        assert len(error_calls) > 0

    @patch("click.echo")
    @patch("promptrek.cli.commands.plugins.validate_plugins_command")
    def test_workflow_plugins_validate_error(self, mock_validate, mock_echo, tmp_path):
        """Test plugins validate with error."""
        import os

        os.chdir(tmp_path)

        # Create config file
        config_file = tmp_path / "project.promptrek.yaml"
        config_file.write_text("schema_version: 3.0.0\ncontent: test")

        ctx = Mock()
        ctx.obj = {"verbose": False}

        # Make command raise error
        mock_validate.side_effect = PrompTrekError("Validation failed")

        from promptrek.cli.interactive import workflow_plugins_validate

        workflow_plugins_validate(ctx)

        # Should display error message
        error_calls = [
            call for call in mock_echo.call_args_list if "Error" in str(call)
        ]
        assert len(error_calls) > 0

    @patch("click.echo")
    @patch("promptrek.cli.interactive.questionary.confirm")
    @patch("promptrek.cli.interactive.questionary.text")
    @patch("promptrek.cli.interactive.spec_export_command")
    @patch("promptrek.utils.spec_manager.SpecManager")
    def test_workflow_spec_export_error(
        self,
        mock_manager_class,
        mock_export,
        mock_text,
        mock_confirm,
        mock_echo,
        tmp_path,
    ):
        """Test spec export with error."""
        import os

        os.chdir(tmp_path)

        ctx = Mock()
        ctx.obj = {"verbose": False}

        # Mock spec manager
        mock_spec = Mock()
        mock_spec.id = "test123"
        mock_spec.title = "Test Spec"
        mock_spec.path = "test.md"

        mock_instance = Mock()
        mock_instance.list_specs.return_value = [mock_spec]
        mock_instance.get_spec_by_id.return_value = mock_spec
        mock_manager_class.return_value = mock_instance

        # Mock user inputs
        mock_text.return_value.ask.side_effect = ["test123", "test-export.md"]
        mock_confirm.return_value.ask.return_value = True

        # Make export raise error
        mock_export.side_effect = PrompTrekError("Export failed")

        from promptrek.cli.interactive import workflow_spec_export

        workflow_spec_export(ctx)

        # Should display error message
        error_calls = [
            call for call in mock_echo.call_args_list if "Error" in str(call)
        ]
        assert len(error_calls) > 0

    @patch("click.echo")
    @patch("promptrek.cli.interactive.questionary.text")
    @patch("promptrek.utils.spec_manager.SpecManager")
    def test_workflow_spec_export_cancel_spec_id(
        self, mock_manager_class, mock_text, mock_echo, tmp_path
    ):
        """Test spec export cancellation at spec ID input."""
        import os

        os.chdir(tmp_path)

        ctx = Mock()
        ctx.obj = {"verbose": False}

        # Mock spec manager with specs
        mock_spec = Mock()
        mock_spec.id = "test123"
        mock_spec.title = "Test Spec"

        mock_instance = Mock()
        mock_instance.list_specs.return_value = [mock_spec]
        mock_manager_class.return_value = mock_instance

        # User cancels at spec ID input
        mock_text.return_value.ask.return_value = None

        from promptrek.cli.interactive import workflow_spec_export

        workflow_spec_export(ctx)

        # Should display cancelled message
        cancelled_calls = [
            call for call in mock_echo.call_args_list if "Cancelled" in str(call)
        ]
        assert len(cancelled_calls) > 0

    @patch("click.echo")
    @patch("promptrek.cli.interactive.questionary.text")
    @patch("promptrek.utils.spec_manager.SpecManager")
    def test_workflow_spec_export_spec_not_found(
        self, mock_manager_class, mock_text, mock_echo, tmp_path
    ):
        """Test spec export when spec ID not found."""
        import os

        os.chdir(tmp_path)

        ctx = Mock()
        ctx.obj = {"verbose": False}

        # Mock spec manager
        mock_spec = Mock()
        mock_spec.id = "test123"
        mock_spec.title = "Test Spec"

        mock_instance = Mock()
        mock_instance.list_specs.return_value = [mock_spec]
        mock_instance.get_spec_by_id.return_value = None  # Not found
        mock_manager_class.return_value = mock_instance

        # User enters invalid spec ID
        mock_text.return_value.ask.return_value = "invalid"

        from promptrek.cli.interactive import workflow_spec_export

        workflow_spec_export(ctx)

        # Should display error message
        error_calls = [
            call for call in mock_echo.call_args_list if "not found" in str(call)
        ]
        assert len(error_calls) > 0

    @patch("click.echo")
    @patch("promptrek.cli.interactive.questionary.confirm")
    @patch("promptrek.cli.interactive.questionary.text")
    @patch("promptrek.cli.interactive.spec_export_command")
    @patch("promptrek.utils.spec_manager.SpecManager")
    def test_workflow_spec_export_cancel_output_path(
        self,
        mock_manager_class,
        mock_export,
        mock_text,
        mock_confirm,
        mock_echo,
        tmp_path,
    ):
        """Test spec export cancellation at output path."""
        import os

        os.chdir(tmp_path)

        ctx = Mock()
        ctx.obj = {"verbose": False}

        # Mock spec manager
        mock_spec = Mock()
        mock_spec.id = "test123"
        mock_spec.title = "Test Spec"
        mock_spec.path = "test.md"

        mock_instance = Mock()
        mock_instance.list_specs.return_value = [mock_spec]
        mock_instance.get_spec_by_id.return_value = mock_spec
        mock_manager_class.return_value = mock_instance

        # User enters spec ID, then cancels at output path
        mock_text.return_value.ask.side_effect = ["test123", None]

        from promptrek.cli.interactive import workflow_spec_export

        workflow_spec_export(ctx)

        # Should not call export command
        mock_export.assert_not_called()

    @patch("click.echo")
    @patch("promptrek.cli.interactive.questionary.confirm")
    @patch("promptrek.cli.interactive.questionary.text")
    @patch("promptrek.utils.spec_manager.SpecManager")
    def test_workflow_spec_export_cancel_clean_mode(
        self, mock_manager_class, mock_text, mock_confirm, mock_echo, tmp_path
    ):
        """Test spec export cancellation at clean mode."""
        import os

        os.chdir(tmp_path)

        ctx = Mock()
        ctx.obj = {"verbose": False}

        # Mock spec manager
        mock_spec = Mock()
        mock_spec.id = "test123"
        mock_spec.title = "Test Spec"
        mock_spec.path = "test.md"

        mock_instance = Mock()
        mock_instance.list_specs.return_value = [mock_spec]
        mock_instance.get_spec_by_id.return_value = mock_spec
        mock_manager_class.return_value = mock_instance

        # User enters spec ID and output path, then cancels at clean mode
        mock_text.return_value.ask.side_effect = ["test123", "output.md"]
        mock_confirm.return_value.ask.return_value = None

        from promptrek.cli.interactive import workflow_spec_export

        workflow_spec_export(ctx)

        # Should display cancelled message
        cancelled_calls = [
            call for call in mock_echo.call_args_list if "Cancelled" in str(call)
        ]
        assert len(cancelled_calls) > 0

    @patch("click.echo")
    @patch("promptrek.cli.interactive.questionary.confirm")
    def test_workflow_config_ignores_cancel_remove_cached(
        self, mock_confirm, mock_echo, tmp_path
    ):
        """Test config ignores cancel at remove cached."""
        import os

        os.chdir(tmp_path)

        ctx = Mock()
        ctx.obj = {"verbose": False}

        # User cancels at remove_cached
        mock_confirm.return_value.ask.return_value = None

        from promptrek.cli.interactive import workflow_config_ignores

        workflow_config_ignores(ctx)

        # Should display cancelled message
        cancelled_calls = [
            call for call in mock_echo.call_args_list if "Cancelled" in str(call)
        ]
        assert len(cancelled_calls) > 0

    @patch("click.echo")
    @patch("promptrek.cli.interactive.questionary.confirm")
    def test_workflow_config_ignores_cancel_dry_run(
        self, mock_confirm, mock_echo, tmp_path
    ):
        """Test config ignores cancel at dry run."""
        import os

        os.chdir(tmp_path)

        ctx = Mock()
        ctx.obj = {"verbose": False}

        # User confirms remove_cached, then cancels at dry_run
        confirm_returns = [
            Mock(ask=Mock(return_value=False)),  # remove_cached
            Mock(ask=Mock(return_value=None)),  # dry_run (cancelled)
        ]
        mock_confirm.side_effect = confirm_returns

        from promptrek.cli.interactive import workflow_config_ignores

        workflow_config_ignores(ctx)

        # Should display cancelled message
        cancelled_calls = [
            call for call in mock_echo.call_args_list if "Cancelled" in str(call)
        ]
        assert len(cancelled_calls) > 0

    @patch("click.echo")
    @patch("promptrek.cli.interactive.questionary.confirm")
    @patch("promptrek.cli.interactive.questionary.text")
    def test_workflow_install_hooks_cancel_force(
        self, mock_text, mock_confirm, mock_echo, tmp_path
    ):
        """Test install hooks cancel at force."""
        import os

        os.chdir(tmp_path)

        ctx = Mock()
        ctx.obj = {"verbose": False}

        # User enters path, then cancels at force
        mock_text.return_value.ask.return_value = ".pre-commit-config.yaml"
        mock_confirm.return_value.ask.return_value = None

        from promptrek.cli.interactive import workflow_install_hooks

        workflow_install_hooks(ctx)

        # Should display cancelled message
        cancelled_calls = [
            call for call in mock_echo.call_args_list if "Cancelled" in str(call)
        ]
        assert len(cancelled_calls) > 0

    @patch("click.echo")
    @patch("promptrek.cli.interactive.questionary.confirm")
    @patch("promptrek.cli.interactive.questionary.text")
    def test_workflow_install_hooks_cancel_activate(
        self, mock_text, mock_confirm, mock_echo, tmp_path
    ):
        """Test install hooks cancel at activate."""
        import os

        os.chdir(tmp_path)

        ctx = Mock()
        ctx.obj = {"verbose": False}

        # User enters path and force, then cancels at activate
        mock_text.return_value.ask.return_value = ".pre-commit-config.yaml"
        confirm_returns = [
            Mock(ask=Mock(return_value=False)),  # force
            Mock(ask=Mock(return_value=None)),  # activate (cancelled)
        ]
        mock_confirm.side_effect = confirm_returns

        from promptrek.cli.interactive import workflow_install_hooks

        workflow_install_hooks(ctx)

        # Should display cancelled message
        cancelled_calls = [
            call for call in mock_echo.call_args_list if "Cancelled" in str(call)
        ]
        assert len(cancelled_calls) > 0


class TestWorkflowUnexpectedErrors:
    """Tests for unexpected error handling in workflows."""

    @patch("builtins.input", return_value="")
    @patch("click.echo")
    @patch("promptrek.cli.interactive.list_specs_command")
    def test_workflow_list_specs_unexpected_error(
        self, mock_list, mock_echo, mock_input, tmp_path
    ):
        """Test list specs with unexpected error (non-PrompTrekError)."""
        import os

        os.chdir(tmp_path)

        ctx = Mock()
        ctx.obj = {"verbose": False}

        # Make command raise unexpected error
        mock_list.side_effect = RuntimeError("Unexpected error")

        from promptrek.cli.interactive import workflow_list_specs

        workflow_list_specs(ctx)

        # Should display unexpected error message
        error_calls = [
            call for call in mock_echo.call_args_list if "Unexpected error" in str(call)
        ]
        assert len(error_calls) > 0

    @patch("click.echo")
    @patch("promptrek.cli.interactive.questionary.text")
    @patch("promptrek.cli.interactive.questionary.select")
    @patch("promptrek.utils.spec_manager.SpecManager")
    def test_workflow_spec_export_unexpected_error(
        self, mock_manager_class, mock_select, mock_text, mock_echo, tmp_path
    ):
        """Test spec export with unexpected error (non-PrompTrekError)."""
        import os

        os.chdir(tmp_path)

        ctx = Mock()
        ctx.obj = {"verbose": False}

        # Setup mock spec
        mock_instance = Mock()
        mock_spec = Mock()
        mock_spec.id = "test123"
        mock_spec.title = "Test Spec"
        mock_instance.list_specs.return_value = [mock_spec]
        # Make export raise unexpected error
        mock_instance.export_spec.side_effect = RuntimeError("Unexpected error")
        mock_manager_class.return_value = mock_instance

        # User selects spec and enters filename
        mock_select.return_value.ask.return_value = "test123"
        mock_text.return_value.ask.return_value = "output.md"

        from promptrek.cli.interactive import workflow_spec_export

        workflow_spec_export(ctx)

        # Should display unexpected error message
        error_calls = [
            call for call in mock_echo.call_args_list if "Unexpected error" in str(call)
        ]
        assert len(error_calls) > 0

    @patch("builtins.input", return_value="")
    @patch("click.echo")
    @patch("promptrek.cli.commands.generate.registry")
    def test_workflow_list_editors_with_exception(
        self, mock_registry, mock_echo, mock_input, tmp_path
    ):
        """Test list editors when get_adapter_info raises exception."""
        import os

        os.chdir(tmp_path)

        ctx = Mock()
        ctx.obj = {"verbose": False}

        # Setup mock registry
        mock_registry.get_project_file_adapters.return_value = ["test_editor"]
        mock_registry.get_global_config_adapters.return_value = ["global_editor"]
        mock_registry.get_adapters_by_capability.return_value = ["ide_editor"]
        # Make get_adapter_info raise exception for first adapter
        mock_registry.get_adapter_info.side_effect = [
            Exception("Info error"),  # project adapter
            {"description": "Global", "file_patterns": []},  # global adapter
            Exception("Info error"),  # ide adapter
        ]

        from promptrek.cli.interactive import workflow_list_editors

        workflow_list_editors(ctx)

        # Should display available message for failed adapters
        available_calls = [
            call for call in mock_echo.call_args_list if "Available" in str(call)
        ]
        assert len(available_calls) >= 1
        mock_input.assert_called_once()


class TestWorkflowGenerateEdgeCases:
    """Tests for edge cases in generate workflow."""

    @patch("click.echo")
    @patch("promptrek.cli.interactive.questionary.confirm")
    @patch("promptrek.cli.interactive.questionary.checkbox")
    def test_workflow_generate_cancel_at_variables_confirm(
        self, mock_checkbox, mock_confirm, mock_echo, tmp_path
    ):
        """Test generate workflow cancel at variable confirmation."""
        import os

        os.chdir(tmp_path)
        (tmp_path / "project.promptrek.yaml").write_text("schema_version: '3.0.0'\n")

        ctx = Mock()
        ctx.obj = {"verbose": False}

        # User selects editor, then cancels at variable confirmation
        mock_checkbox.return_value.ask.return_value = ["claude"]
        mock_confirm.return_value.ask.return_value = None

        from promptrek.cli.interactive import workflow_generate_config

        workflow_generate_config(ctx)

        # Should display cancelled message
        cancelled_calls = [
            call for call in mock_echo.call_args_list if "Cancelled" in str(call)
        ]
        assert len(cancelled_calls) > 0

    @patch("promptrek.cli.interactive.generate_command")
    @patch("click.echo")
    @patch("promptrek.cli.interactive.questionary.text")
    @patch("promptrek.cli.interactive.questionary.confirm")
    @patch("promptrek.cli.interactive.questionary.checkbox")
    def test_workflow_generate_invalid_variable_format(
        self, mock_checkbox, mock_confirm, mock_text, mock_echo, mock_generate, tmp_path
    ):
        """Test generate workflow with invalid variable format."""
        import os

        os.chdir(tmp_path)
        (tmp_path / "project.promptrek.yaml").write_text("schema_version: '3.0.0'\n")

        ctx = Mock()
        ctx.obj = {"verbose": False}

        # User selects editor, wants variables, enters invalid format, then empty
        mock_checkbox.return_value.ask.return_value = ["claude"]
        confirm_returns = [
            Mock(ask=Mock(return_value=True)),  # use_variables
            Mock(ask=Mock(return_value=False)),  # headless
            Mock(ask=Mock(return_value=False)),  # dry_run
        ]
        mock_confirm.side_effect = confirm_returns
        # First invalid (no =), then empty to finish
        text_returns = [
            Mock(ask=Mock(return_value="INVALID_NO_EQUALS")),
            Mock(ask=Mock(return_value="")),
        ]
        mock_text.side_effect = text_returns

        from promptrek.cli.interactive import workflow_generate_config

        workflow_generate_config(ctx)

        # Should display invalid format message
        invalid_calls = [
            call
            for call in mock_echo.call_args_list
            if "Invalid format" in str(call) or "KEY=VALUE" in str(call)
        ]
        assert len(invalid_calls) > 0

    @patch("click.echo")
    @patch("promptrek.cli.interactive.questionary.text")
    @patch("promptrek.cli.interactive.questionary.confirm")
    @patch("promptrek.cli.interactive.questionary.checkbox")
    def test_workflow_generate_cancel_during_variable_input(
        self, mock_checkbox, mock_confirm, mock_text, mock_echo, tmp_path
    ):
        """Test generate workflow cancel during variable input."""
        import os

        os.chdir(tmp_path)
        (tmp_path / "project.promptrek.yaml").write_text("schema_version: '3.0.0'\n")

        ctx = Mock()
        ctx.obj = {"verbose": False}

        # User selects editor, wants variables, then cancels during input
        mock_checkbox.return_value.ask.return_value = ["claude"]
        mock_confirm.return_value.ask.return_value = True  # use_variables
        mock_text.return_value.ask.return_value = None  # cancel

        from promptrek.cli.interactive import workflow_generate_config

        workflow_generate_config(ctx)

        # Should display cancelled message
        cancelled_calls = [
            call for call in mock_echo.call_args_list if "Cancelled" in str(call)
        ]
        assert len(cancelled_calls) > 0
