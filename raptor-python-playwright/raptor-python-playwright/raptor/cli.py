"""
Command-Line Interface for RAPTOR Python Playwright Framework.

This module provides a comprehensive CLI for test execution, session management,
and configuration operations.
"""

import sys
import asyncio
import click
from pathlib import Path
from typing import Optional, List
import logging
import json

from raptor.core.config_manager import ConfigManager
from raptor.core.session_manager import SessionManager
from raptor.core.browser_manager import BrowserManager
from raptor.core.exceptions import RaptorException
from raptor.utils.logger import setup_logging


# Configure logging
logger = logging.getLogger(__name__)


@click.group()
@click.version_option(version="1.0.0", prog_name="RAPTOR")
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose output"
)
@click.pass_context
def cli(ctx, verbose):
    """
    RAPTOR - Robust Automated Playwright Test Orchestration & Reporting
    
    A modern Python Playwright-based test automation framework.
    """
    # Ensure context object exists
    ctx.ensure_object(dict)
    
    # Set up logging
    log_level = logging.DEBUG if verbose else logging.INFO
    setup_logging(log_level=log_level)
    
    ctx.obj["verbose"] = verbose
    logger.debug("RAPTOR CLI initialized")



@cli.command()
@click.argument("test_path", required=False, default="tests")
@click.option("--browser", "-b", type=click.Choice(["chromium", "firefox", "webkit"], case_sensitive=False), default="chromium", help="Browser to use for test execution")
@click.option("--headless", is_flag=True, default=False, help="Run browser in headless mode")
@click.option("--env", "-e", type=click.Choice(["dev", "staging", "prod"], case_sensitive=False), default="dev", help="Environment configuration to use")
@click.option("--parallel", "-n", type=int, default=1, help="Number of parallel workers (requires pytest-xdist)")
@click.option("--markers", "-m", type=str, help="Run tests matching given mark expression (e.g., 'smoke and not slow')")
@click.option("--test-id", type=str, help="Run specific test by ID")
@click.option("--iteration", type=int, help="Run specific iteration number")
@click.option("--tag", type=str, multiple=True, help="Run tests with specific tag(s)")
@click.option("--report", type=click.Choice(["html", "json", "allure"], case_sensitive=False), default="html", help="Report format")
@click.option("--report-dir", type=click.Path(), default="reports", help="Directory for test reports")
@click.option("--screenshot-on-failure", is_flag=True, default=True, help="Capture screenshots on test failure")
@click.option("--video", is_flag=True, default=False, help="Record video of test execution")
@click.option("--retry", type=int, default=0, help="Number of times to retry failed tests")
@click.pass_context
def run(ctx, test_path, browser, headless, env, parallel, markers, test_id, iteration, tag, report, report_dir, screenshot_on_failure, video, retry):
    """Execute tests with specified configuration."""
    verbose = ctx.obj.get("verbose", False)
    
    try:
        config = ConfigManager()
        config.load_config(environment=env)
        
        if verbose:
            click.echo(f"Configuration loaded for environment: {env}")
            click.echo(f"Browser: {browser}")
            click.echo(f"Headless: {headless}")
        
        pytest_args = build_pytest_args(test_path, browser, headless, env, parallel, markers, test_id, iteration, tag, report, report_dir, screenshot_on_failure, video, retry)
        
        if verbose:
            click.echo(f"Executing: pytest {' '.join(pytest_args)}")
        
        import pytest as pytest_module
        exit_code = pytest_module.main(pytest_args)
        
        if exit_code == 0:
            click.secho("✓ All tests passed!", fg="green", bold=True)
        else:
            click.secho(f"✗ Tests failed with exit code: {exit_code}", fg="red", bold=True)
        
        sys.exit(exit_code)
        
    except Exception as e:
        logger.exception("Error executing tests")
        click.secho(f"Error: {str(e)}", fg="red", err=True)
        sys.exit(1)



@cli.group()
def session():
    """Manage browser sessions for test reuse."""
    pass


@session.command("list")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed session information")
@click.pass_context
def session_list(ctx, verbose):
    """List all available browser sessions."""
    try:
        session_manager = SessionManager()
        sessions = asyncio.run(session_manager.list_sessions())
        
        if not sessions:
            click.echo("No saved sessions found.")
            return
        
        click.echo(f"Found {len(sessions)} session(s):\n")
        
        for session_id in sessions:
            click.echo(f"  • {session_id}")
            
            if verbose:
                info = session_manager.get_session_info(session_id)
                if info:
                    click.echo(f"    Browser: {info.browser_type}")
                    click.echo(f"    Created: {info.created_at}")
                    click.echo(f"    Last accessed: {info.last_accessed}")
                    if info.metadata:
                        click.echo(f"    Metadata: {json.dumps(info.metadata, indent=6)}")
                click.echo()
        
    except Exception as e:
        logger.exception("Error listing sessions")
        click.secho(f"Error: {str(e)}", fg="red", err=True)
        sys.exit(1)


@session.command("save")
@click.argument("session_name")
@click.option("--browser", "-b", type=click.Choice(["chromium", "firefox", "webkit"], case_sensitive=False), default="chromium", help="Browser type")
@click.option("--headless", is_flag=True, default=False, help="Run browser in headless mode")
@click.option("--url", type=str, help="Navigate to URL before saving session")
@click.pass_context
def session_save(ctx, session_name, browser, headless, url):
    """Create and save a new browser session."""
    verbose = ctx.obj.get("verbose", False)
    
    try:
        async def _save_session():
            browser_manager = BrowserManager()
            session_manager = SessionManager()
            
            if verbose:
                click.echo(f"Launching {browser} browser...")
            
            browser_instance = await browser_manager.launch_browser(browser_type=browser, headless=headless)
            context = await browser_manager.create_context()
            page = await browser_manager.create_page(context)
            
            if url:
                if verbose:
                    click.echo(f"Navigating to {url}...")
                await page.goto(url)
                await page.wait_for_load_state("networkidle")
            
            if verbose:
                click.echo(f"Saving session as '{session_name}'...")
            
            await session_manager.save_session(page, session_name)
            click.secho(f"✓ Session '{session_name}' saved successfully!", fg="green")
            
            click.echo("\nBrowser is open. Press Ctrl+C when done to close...")
            try:
                await asyncio.sleep(3600)
            except KeyboardInterrupt:
                pass
            
            await browser_manager.close_browser()
        
        asyncio.run(_save_session())
        
    except KeyboardInterrupt:
        click.echo("\nSession saved. Browser closed.")
    except Exception as e:
        logger.exception("Error saving session")
        click.secho(f"Error: {str(e)}", fg="red", err=True)
        sys.exit(1)


@session.command("restore")
@click.argument("session_name")
@click.option("--url", type=str, help="Navigate to URL after restoring session")
@click.pass_context
def session_restore(ctx, session_name, url):
    """Restore and interact with a saved browser session."""
    verbose = ctx.obj.get("verbose", False)
    
    try:
        async def _restore_session():
            session_manager = SessionManager()
            
            if verbose:
                click.echo(f"Restoring session '{session_name}'...")
            
            page = await session_manager.restore_session(session_name)
            click.secho(f"✓ Session '{session_name}' restored successfully!", fg="green")
            
            if url:
                if verbose:
                    click.echo(f"Navigating to {url}...")
                await page.goto(url)
                await page.wait_for_load_state("networkidle")
            
            click.echo("\nBrowser is open. Press Ctrl+C when done to close...")
            try:
                await asyncio.sleep(3600)
            except KeyboardInterrupt:
                pass
        
        asyncio.run(_restore_session())
        
    except KeyboardInterrupt:
        click.echo("\nBrowser closed.")
    except Exception as e:
        logger.exception("Error restoring session")
        click.secho(f"Error: {str(e)}", fg="red", err=True)
        sys.exit(1)


@session.command("delete")
@click.argument("session_name")
@click.option("--force", "-f", is_flag=True, help="Skip confirmation prompt")
@click.pass_context
def session_delete(ctx, session_name, force):
    """Delete a saved browser session."""
    try:
        session_manager = SessionManager()
        
        if not force:
            if not click.confirm(f"Are you sure you want to delete session '{session_name}'?"):
                click.echo("Deletion cancelled.")
                return
        
        asyncio.run(session_manager.delete_session(session_name))
        click.secho(f"✓ Session '{session_name}' deleted successfully!", fg="green")
        
    except Exception as e:
        logger.exception("Error deleting session")
        click.secho(f"Error: {str(e)}", fg="red", err=True)
        sys.exit(1)



@cli.group()
def config():
    """Manage framework configuration."""
    pass


@config.command("show")
@click.option("--env", "-e", type=click.Choice(["dev", "staging", "prod"], case_sensitive=False), default="dev", help="Environment to show configuration for")
@click.option("--key", type=str, help="Show specific configuration key")
@click.pass_context
def config_show(ctx, env, key):
    """Display current configuration settings."""
    try:
        config_manager = ConfigManager()
        config_manager.load_config(environment=env)
        
        if key:
            value = config_manager.get(key)
            if value is not None:
                click.echo(f"{key}: {value}")
            else:
                click.secho(f"Key '{key}' not found in configuration", fg="yellow")
        else:
            click.echo(f"Configuration for environment: {env}\n")
            config_dict = config_manager._config
            click.echo(json.dumps(config_dict, indent=2))
        
    except Exception as e:
        logger.exception("Error showing configuration")
        click.secho(f"Error: {str(e)}", fg="red", err=True)
        sys.exit(1)


@config.command("set")
@click.argument("key")
@click.argument("value")
@click.option("--env", "-e", type=click.Choice(["dev", "staging", "prod"], case_sensitive=False), default="dev", help="Environment to modify")
@click.pass_context
def config_set(ctx, key, value, env):
    """Set a configuration value."""
    try:
        config_manager = ConfigManager()
        config_manager.load_config(environment=env)
        
        try:
            parsed_value = json.loads(value)
        except json.JSONDecodeError:
            parsed_value = value
        
        config_manager.set(key, parsed_value)
        click.secho(f"✓ Configuration updated: {key} = {parsed_value}", fg="green")
        
    except Exception as e:
        logger.exception("Error setting configuration")
        click.secho(f"Error: {str(e)}", fg="red", err=True)
        sys.exit(1)


@config.command("validate")
@click.option("--env", "-e", type=click.Choice(["dev", "staging", "prod"], case_sensitive=False), default="dev", help="Environment to validate")
@click.pass_context
def config_validate(ctx, env):
    """Validate configuration for an environment."""
    try:
        config_manager = ConfigManager()
        config_manager.load_config(environment=env)
        
        errors = []
        warnings = []
        
        required_keys = ["browser.type", "browser.timeout", "timeouts.default", "timeouts.element_wait"]
        
        for req_key in required_keys:
            if config_manager.get(req_key) is None:
                errors.append(f"Missing required key: {req_key}")
        
        timeout_keys = ["browser.timeout", "timeouts.default", "timeouts.element_wait"]
        for timeout_key in timeout_keys:
            value = config_manager.get(timeout_key)
            if value is not None and (not isinstance(value, (int, float)) or value <= 0):
                errors.append(f"Invalid timeout value for {timeout_key}: {value}")
        
        if errors:
            click.secho(f"\n✗ Configuration validation failed for '{env}':", fg="red", bold=True)
            for error in errors:
                click.secho(f"  • {error}", fg="red")
            sys.exit(1)
        elif warnings:
            click.secho(f"\n⚠ Configuration validation passed with warnings for '{env}':", fg="yellow", bold=True)
            for warning in warnings:
                click.secho(f"  • {warning}", fg="yellow")
        else:
            click.secho(f"\n✓ Configuration is valid for '{env}'!", fg="green", bold=True)
        
    except Exception as e:
        logger.exception("Error validating configuration")
        click.secho(f"Error: {str(e)}", fg="red", err=True)
        sys.exit(1)


def build_pytest_args(test_path, browser, headless, env, parallel, markers, test_id, iteration, tag, report, report_dir, screenshot_on_failure, video, retry):
    """Build pytest command-line arguments from CLI options."""
    args = [test_path]
    
    args.extend([f"--browser={browser}", f"--env={env}"])
    
    if headless:
        args.append("--headless")
    
    if parallel > 1:
        args.extend(["-n", str(parallel)])
    
    if markers:
        args.extend(["-m", markers])
    
    if test_id:
        args.extend(["-k", test_id])
    
    if iteration is not None:
        args.extend(["--iteration", str(iteration)])
    
    for t in tag:
        args.extend(["--tag", t])
    
    Path(report_dir).mkdir(parents=True, exist_ok=True)
    
    if report == "html":
        args.extend(["--html", f"{report_dir}/report.html", "--self-contained-html"])
    elif report == "json":
        args.extend(["--json-report", f"--json-report-file={report_dir}/report.json"])
    elif report == "allure":
        args.extend(["--alluredir", f"{report_dir}/allure-results"])
    
    if screenshot_on_failure:
        args.append("--screenshot=only-on-failure")
    
    if video:
        args.append("--video=on")
    
    if retry > 0:
        args.extend(["--reruns", str(retry)])
    
    args.append("-v")
    
    return args


def main():
    """Entry point for the CLI."""
    cli(obj={})


if __name__ == "__main__":
    main()
