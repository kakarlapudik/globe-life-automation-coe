"""
Tests for RAPTOR CLI functionality.

This module tests the command-line interface components.
"""

import pytest
from click.testing import CliRunner
from pathlib import Path
import json

from raptor.cli import cli, build_pytest_args


class TestCLIBasics:
    """Test basic CLI functionality."""
    
    def test_cli_version(self):
        """Test that --version flag works."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])
        
        assert result.exit_code == 0
        assert "1.0.0" in result.output
    
    def test_cli_help(self):
        """Test that --help flag works."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        
        assert result.exit_code == 0
        assert "RAPTOR" in result.output
        assert "run" in result.output
        assert "session" in result.output
        assert "config" in result.output
    
    def test_cli_verbose_flag(self):
        """Test that --verbose flag is recognized."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--verbose", "--help"])
        
        assert result.exit_code == 0


class TestRunCommand:
    """Test the 'run' command."""
    
    def test_run_help(self):
        """Test run command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["run", "--help"])
        
        assert result.exit_code == 0
        assert "Execute tests" in result.output
        assert "--browser" in result.output
        assert "--headless" in result.output
        assert "--env" in result.output
    
    def testbuild_pytest_args_basic(self):
        """Test building basic pytest arguments."""
        args = build_pytest_args(
            test_path="tests/",
            browser="chromium",
            headless=False,
            env="dev",
            parallel=1,
            markers=None,
            test_id=None,
            iteration=None,
            tag=(),
            report="html",
            report_dir="reports",
            screenshot_on_failure=True,
            video=False,
            retry=0
        )
        
        assert "tests/" in args
        assert "--browser=chromium" in args
        assert "--env=dev" in args
        assert "-v" in args
    
    def testbuild_pytest_args_with_headless(self):
        """Test building pytest arguments with headless mode."""
        args = build_pytest_args(
            test_path="tests/",
            browser="firefox",
            headless=True,
            env="staging",
            parallel=1,
            markers=None,
            test_id=None,
            iteration=None,
            tag=(),
            report="html",
            report_dir="reports",
            screenshot_on_failure=True,
            video=False,
            retry=0
        )
        
        assert "--headless" in args
        assert "--browser=firefox" in args
        assert "--env=staging" in args
    
    def testbuild_pytest_args_with_parallel(self):
        """Test building pytest arguments with parallel execution."""
        args = build_pytest_args(
            test_path="tests/",
            browser="chromium",
            headless=False,
            env="dev",
            parallel=4,
            markers=None,
            test_id=None,
            iteration=None,
            tag=(),
            report="html",
            report_dir="reports",
            screenshot_on_failure=True,
            video=False,
            retry=0
        )
        
        assert "-n" in args
        assert "4" in args
    
    def testbuild_pytest_args_with_markers(self):
        """Test building pytest arguments with markers."""
        args = build_pytest_args(
            test_path="tests/",
            browser="chromium",
            headless=False,
            env="dev",
            parallel=1,
            markers="smoke and not slow",
            test_id=None,
            iteration=None,
            tag=(),
            report="html",
            report_dir="reports",
            screenshot_on_failure=True,
            video=False,
            retry=0
        )
        
        assert "-m" in args
        assert "smoke and not slow" in args
    
    def testbuild_pytest_args_with_test_id(self):
        """Test building pytest arguments with test ID."""
        args = build_pytest_args(
            test_path="tests/",
            browser="chromium",
            headless=False,
            env="dev",
            parallel=1,
            markers=None,
            test_id="TC-001",
            iteration=None,
            tag=(),
            report="html",
            report_dir="reports",
            screenshot_on_failure=True,
            video=False,
            retry=0
        )
        
        assert "-k" in args
        assert "TC-001" in args
    
    def testbuild_pytest_args_with_iteration(self):
        """Test building pytest arguments with iteration."""
        args = build_pytest_args(
            test_path="tests/",
            browser="chromium",
            headless=False,
            env="dev",
            parallel=1,
            markers=None,
            test_id=None,
            iteration=2,
            tag=(),
            report="html",
            report_dir="reports",
            screenshot_on_failure=True,
            video=False,
            retry=0
        )
        
        assert "--iteration" in args
        assert "2" in args
    
    def testbuild_pytest_args_with_tags(self):
        """Test building pytest arguments with tags."""
        args = build_pytest_args(
            test_path="tests/",
            browser="chromium",
            headless=False,
            env="dev",
            parallel=1,
            markers=None,
            test_id=None,
            iteration=None,
            tag=("login", "authentication"),
            report="html",
            report_dir="reports",
            screenshot_on_failure=True,
            video=False,
            retry=0
        )
        
        assert "--tag" in args
        assert "login" in args
        assert "authentication" in args
    
    def testbuild_pytest_args_with_json_report(self):
        """Test building pytest arguments with JSON report."""
        args = build_pytest_args(
            test_path="tests/",
            browser="chromium",
            headless=False,
            env="dev",
            parallel=1,
            markers=None,
            test_id=None,
            iteration=None,
            tag=(),
            report="json",
            report_dir="reports",
            screenshot_on_failure=True,
            video=False,
            retry=0
        )
        
        assert "--json-report" in args
        assert any("report.json" in arg for arg in args)
    
    def testbuild_pytest_args_with_allure_report(self):
        """Test building pytest arguments with Allure report."""
        args = build_pytest_args(
            test_path="tests/",
            browser="chromium",
            headless=False,
            env="dev",
            parallel=1,
            markers=None,
            test_id=None,
            iteration=None,
            tag=(),
            report="allure",
            report_dir="reports",
            screenshot_on_failure=True,
            video=False,
            retry=0
        )
        
        assert "--alluredir" in args
        assert any("allure-results" in arg for arg in args)
    
    def testbuild_pytest_args_with_video(self):
        """Test building pytest arguments with video recording."""
        args = build_pytest_args(
            test_path="tests/",
            browser="chromium",
            headless=False,
            env="dev",
            parallel=1,
            markers=None,
            test_id=None,
            iteration=None,
            tag=(),
            report="html",
            report_dir="reports",
            screenshot_on_failure=True,
            video=True,
            retry=0
        )
        
        assert "--video=on" in args
    
    def testbuild_pytest_args_with_retry(self):
        """Test building pytest arguments with retry."""
        args = build_pytest_args(
            test_path="tests/",
            browser="chromium",
            headless=False,
            env="dev",
            parallel=1,
            markers=None,
            test_id=None,
            iteration=None,
            tag=(),
            report="html",
            report_dir="reports",
            screenshot_on_failure=True,
            video=False,
            retry=3
        )
        
        assert "--reruns" in args
        assert "3" in args


class TestSessionCommand:
    """Test the 'session' command."""
    
    def test_session_help(self):
        """Test session command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["session", "--help"])
        
        assert result.exit_code == 0
        assert "Manage browser sessions" in result.output
        assert "list" in result.output
        assert "save" in result.output
        assert "restore" in result.output
        assert "delete" in result.output
    
    def test_session_list_help(self):
        """Test session list command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["session", "list", "--help"])
        
        assert result.exit_code == 0
        assert "List all available" in result.output
    
    def test_session_save_help(self):
        """Test session save command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["session", "save", "--help"])
        
        assert result.exit_code == 0
        assert "Create and save" in result.output
        assert "--browser" in result.output
        assert "--url" in result.output
    
    def test_session_restore_help(self):
        """Test session restore command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["session", "restore", "--help"])
        
        assert result.exit_code == 0
        assert "Restore and interact" in result.output
    
    def test_session_delete_help(self):
        """Test session delete command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["session", "delete", "--help"])
        
        assert result.exit_code == 0
        assert "Delete a saved" in result.output
        assert "--force" in result.output


class TestConfigCommand:
    """Test the 'config' command."""
    
    def test_config_help(self):
        """Test config command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["config", "--help"])
        
        assert result.exit_code == 0
        assert "Manage framework configuration" in result.output
        assert "show" in result.output
        assert "set" in result.output
        assert "validate" in result.output
    
    def test_config_show_help(self):
        """Test config show command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["config", "show", "--help"])
        
        assert result.exit_code == 0
        assert "Display current configuration" in result.output
        assert "--env" in result.output
        assert "--key" in result.output
    
    def test_config_set_help(self):
        """Test config set command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["config", "set", "--help"])
        
        assert result.exit_code == 0
        assert "Set a configuration value" in result.output
    
    def test_config_validate_help(self):
        """Test config validate command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["config", "validate", "--help"])
        
        assert result.exit_code == 0
        assert "Validate configuration" in result.output


class TestCLIIntegration:
    """Integration tests for CLI commands."""
    
    def test_run_command_with_invalid_browser(self):
        """Test run command with invalid browser."""
        runner = CliRunner()
        result = runner.invoke(cli, ["run", "--browser", "invalid"])
        
        assert result.exit_code != 0
        assert "Invalid value" in result.output or "Error" in result.output
    
    def test_run_command_with_invalid_env(self):
        """Test run command with invalid environment."""
        runner = CliRunner()
        result = runner.invoke(cli, ["run", "--env", "invalid"])
        
        assert result.exit_code != 0
        assert "Invalid value" in result.output or "Error" in result.output
    
    def test_run_command_with_invalid_report(self):
        """Test run command with invalid report format."""
        runner = CliRunner()
        result = runner.invoke(cli, ["run", "--report", "invalid"])
        
        assert result.exit_code != 0
        assert "Invalid value" in result.output or "Error" in result.output


class TestCLIErrorHandling:
    """Test CLI error handling."""
    
    def test_session_delete_without_name(self):
        """Test session delete without session name."""
        runner = CliRunner()
        result = runner.invoke(cli, ["session", "delete"])
        
        assert result.exit_code != 0
        assert "Missing argument" in result.output or "Error" in result.output
    
    def test_session_save_without_name(self):
        """Test session save without session name."""
        runner = CliRunner()
        result = runner.invoke(cli, ["session", "save"])
        
        assert result.exit_code != 0
        assert "Missing argument" in result.output or "Error" in result.output
    
    def test_config_set_without_arguments(self):
        """Test config set without arguments."""
        runner = CliRunner()
        result = runner.invoke(cli, ["config", "set"])
        
        assert result.exit_code != 0
        assert "Missing argument" in result.output or "Error" in result.output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
