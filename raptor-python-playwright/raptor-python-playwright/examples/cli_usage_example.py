"""
Example demonstrating programmatic usage of RAPTOR CLI components.

This example shows how to use the CLI components programmatically
rather than through the command-line interface.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from raptor.core.config_manager import ConfigManager
from raptor.core.session_manager import SessionManager
from raptor.core.browser_manager import BrowserManager
from raptor.utils.logger import setup_logging


async def example_session_workflow():
    """
    Example: Create, use, and manage browser sessions programmatically.
    
    This demonstrates the same functionality as the CLI session commands
    but in Python code.
    """
    print("\n=== Session Management Example ===\n")
    
    # Initialize managers
    browser_manager = BrowserManager()
    session_manager = SessionManager()
    
    # 1. Create a new session
    print("1. Creating new browser session...")
    browser = await browser_manager.launch_browser(browser_type="chromium", headless=False)
    context = await browser_manager.create_context()
    page = await browser_manager.create_page(context)
    
    # Navigate to a page
    await page.goto("https://example.com")
    await page.wait_for_load_state("networkidle")
    print("   ✓ Navigated to example.com")
    
    # Save the session
    session_name = "example-session"
    await session_manager.save_session(page, session_name)
    print(f"   ✓ Session saved as '{session_name}'")
    
    # Close browser
    await browser_manager.close_browser()
    print("   ✓ Browser closed")
    
    # 2. List available sessions
    print("\n2. Listing available sessions...")
    sessions = await session_manager.list_sessions()
    print(f"   Found {len(sessions)} session(s):")
    for session_id in sessions:
        info = session_manager.get_session_info(session_id)
        if info:
            print(f"   • {session_id}")
            print(f"     Browser: {info.browser_type}")
            print(f"     Created: {info.created_at}")
    
    # 3. Restore the session
    print("\n3. Restoring saved session...")
    restored_page = await session_manager.restore_session(session_name)
    print(f"   ✓ Session '{session_name}' restored")
    print(f"   Current URL: {restored_page.url}")
    
    # Use the restored session
    await restored_page.goto("https://example.com/about")
    print("   ✓ Navigated to /about using restored session")
    
    # 4. Clean up
    print("\n4. Cleaning up...")
    await session_manager.delete_session(session_name)
    print(f"   ✓ Session '{session_name}' deleted")


async def example_config_workflow():
    """
    Example: Load and manage configuration programmatically.
    
    This demonstrates the same functionality as the CLI config commands
    but in Python code.
    """
    print("\n=== Configuration Management Example ===\n")
    
    # 1. Load configuration for different environments
    print("1. Loading configurations...")
    
    config_dev = ConfigManager()
    config_dev.load_config(environment="dev")
    print("   ✓ Dev configuration loaded")
    
    config_staging = ConfigManager()
    config_staging.load_config(environment="staging")
    print("   ✓ Staging configuration loaded")
    
    # 2. Get configuration values
    print("\n2. Reading configuration values...")
    
    browser_type = config_dev.get("browser.type")
    timeout = config_dev.get("browser.timeout")
    print(f"   Browser type: {browser_type}")
    print(f"   Timeout: {timeout}ms")
    
    # 3. Set configuration values
    print("\n3. Updating configuration...")
    
    config_dev.set("browser.timeout", 45000)
    new_timeout = config_dev.get("browser.timeout")
    print(f"   ✓ Timeout updated to: {new_timeout}ms")
    
    # 4. Get browser options
    print("\n4. Getting browser options...")
    
    browser_options = config_dev.get_browser_options()
    print(f"   Browser options: {browser_options}")
    
    # 5. Get timeout values
    print("\n5. Getting timeout values...")
    
    default_timeout = config_dev.get_timeout("default")
    element_timeout = config_dev.get_timeout("element_wait")
    print(f"   Default timeout: {default_timeout}ms")
    print(f"   Element wait timeout: {element_timeout}ms")


async def example_test_execution_workflow():
    """
    Example: Execute tests programmatically with different configurations.
    
    This demonstrates how to build and execute test runs programmatically.
    """
    print("\n=== Test Execution Example ===\n")
    
    # 1. Load configuration
    print("1. Loading test configuration...")
    config = ConfigManager()
    config.load_config(environment="dev")
    print("   ✓ Configuration loaded")
    
    # 2. Set up browser
    print("\n2. Setting up browser...")
    browser_manager = BrowserManager()
    
    browser_type = config.get("browser.type", "chromium")
    headless = config.get("browser.headless", False)
    
    browser = await browser_manager.launch_browser(
        browser_type=browser_type,
        headless=headless
    )
    print(f"   ✓ {browser_type} browser launched (headless={headless})")
    
    # 3. Create test context
    print("\n3. Creating test context...")
    context = await browser_manager.create_context()
    page = await browser_manager.create_page(context)
    print("   ✓ Browser context and page created")
    
    # 4. Execute test steps
    print("\n4. Executing test steps...")
    
    # Navigate to test page
    await page.goto("https://example.com")
    print("   ✓ Navigated to test page")
    
    # Verify page title
    title = await page.title()
    print(f"   ✓ Page title: {title}")
    
    # Take screenshot
    screenshot_path = Path("reports/example_screenshot.png")
    screenshot_path.parent.mkdir(parents=True, exist_ok=True)
    await page.screenshot(path=str(screenshot_path))
    print(f"   ✓ Screenshot saved to {screenshot_path}")
    
    # 5. Clean up
    print("\n5. Cleaning up...")
    await browser_manager.close_browser()
    print("   ✓ Browser closed")


async def example_parallel_execution():
    """
    Example: Execute multiple test scenarios in parallel.
    
    This demonstrates how to run multiple browser instances concurrently.
    """
    print("\n=== Parallel Execution Example ===\n")
    
    async def run_test_scenario(scenario_name: str, url: str):
        """Run a single test scenario."""
        print(f"   Starting scenario: {scenario_name}")
        
        browser_manager = BrowserManager()
        browser = await browser_manager.launch_browser(
            browser_type="chromium",
            headless=True
        )
        context = await browser_manager.create_context()
        page = await browser_manager.create_page(context)
        
        await page.goto(url)
        title = await page.title()
        
        await browser_manager.close_browser()
        
        print(f"   ✓ {scenario_name} completed: {title}")
        return scenario_name, title
    
    # Run multiple scenarios in parallel
    print("Running 3 test scenarios in parallel...\n")
    
    scenarios = [
        ("Scenario 1", "https://example.com"),
        ("Scenario 2", "https://example.org"),
        ("Scenario 3", "https://example.net"),
    ]
    
    results = await asyncio.gather(*[
        run_test_scenario(name, url) for name, url in scenarios
    ])
    
    print("\nAll scenarios completed:")
    for name, title in results:
        print(f"   • {name}: {title}")


def example_cli_integration():
    """
    Example: Integrate CLI functionality into custom scripts.
    
    This shows how to use CLI components in custom automation scripts.
    """
    print("\n=== CLI Integration Example ===\n")
    
    # 1. Parse custom arguments
    print("1. Custom argument parsing...")
    import argparse
    
    parser = argparse.ArgumentParser(description="Custom test runner")
    parser.add_argument("--env", choices=["dev", "staging", "prod"], default="dev")
    parser.add_argument("--browser", choices=["chromium", "firefox", "webkit"], default="chromium")
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--parallel", type=int, default=1)
    
    # Simulate command-line arguments
    args = parser.parse_args(["--env", "staging", "--browser", "firefox", "--parallel", "4"])
    
    print(f"   Environment: {args.env}")
    print(f"   Browser: {args.browser}")
    print(f"   Headless: {args.headless}")
    print(f"   Parallel workers: {args.parallel}")
    
    # 2. Build pytest command
    print("\n2. Building pytest command...")
    
    pytest_args = [
        "tests/",
        f"--browser={args.browser}",
        f"--env={args.env}",
    ]
    
    if args.headless:
        pytest_args.append("--headless")
    
    if args.parallel > 1:
        pytest_args.extend(["-n", str(args.parallel)])
    
    print(f"   pytest {' '.join(pytest_args)}")
    
    # 3. Execute tests (commented out to avoid actual execution)
    print("\n3. Test execution...")
    print("   (Execution skipped in example)")
    # import pytest
    # exit_code = pytest.main(pytest_args)


async def main():
    """Run all examples."""
    # Set up logging
    setup_logging()
    
    print("=" * 60)
    print("RAPTOR CLI Usage Examples")
    print("=" * 60)
    
    try:
        # Run examples
        await example_config_workflow()
        await example_session_workflow()
        await example_test_execution_workflow()
        await example_parallel_execution()
        example_cli_integration()
        
        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run examples
    asyncio.run(main())
