"""
Cleanup and Teardown Example

This example demonstrates the cleanup and teardown functionality in RAPTOR,
including automatic cleanup, manual cleanup, and graceful shutdown handling.

Requirements: 3.4, 11.5, 12.5
"""

import asyncio
import logging
from pathlib import Path

from raptor.core.browser_manager import BrowserManager
from raptor.core.config_manager import ConfigManager
from raptor.database.database_manager import DatabaseManager
from raptor.utils.cleanup import (
    cleanup_manager,
    register_cleanup,
    cleanup_all,
    BrowserCleanupHelper,
    DatabaseCleanupHelper,
    ScreenshotCleanupHelper,
    LogCleanupHelper,
    ReportCleanupHelper
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def example_automatic_cleanup():
    """
    Example 1: Automatic cleanup with CleanupManager.
    
    This example shows how cleanup tasks are automatically registered
    and executed when the program exits or receives a signal.
    """
    logger.info("=== Example 1: Automatic Cleanup ===")
    
    # Create resources
    config = ConfigManager()
    browser_manager = BrowserManager(config=config)
    
    # Register cleanup tasks
    register_cleanup(
        name="browser_cleanup",
        callback=lambda: asyncio.run(BrowserCleanupHelper.cleanup_browser_manager(browser_manager)),
        priority=10  # High priority - cleanup early
    )
    
    logger.info("Cleanup task registered")
    logger.info("Registered tasks: %s", cleanup_manager.get_registered_tasks())
    
    # Launch browser
    await browser_manager.launch_browser("chromium", headless=True)
    context = await browser_manager.create_context()
    page = await browser_manager.create_page(context)
    
    # Use browser
    await page.goto("https://example.com")
    logger.info("Page title: %s", await page.title())
    
    # Cleanup happens automatically on exit or signal
    # You can also trigger it manually:
    cleanup_all()
    
    logger.info("Example 1 completed\n")


async def example_manual_cleanup():
    """
    Example 2: Manual cleanup using helper classes.
    
    This example shows how to manually clean up resources using
    the provided helper classes.
    """
    logger.info("=== Example 2: Manual Cleanup ===")
    
    # Create resources
    config = ConfigManager()
    browser_manager = BrowserManager(config=config)
    
    try:
        # Launch browser
        await browser_manager.launch_browser("chromium", headless=True)
        context = await browser_manager.create_context()
        page = await browser_manager.create_page(context)
        
        # Use browser
        await page.goto("https://example.com")
        logger.info("Page title: %s", await page.title())
        
    finally:
        # Manual cleanup
        logger.info("Performing manual cleanup")
        await BrowserCleanupHelper.cleanup_browser_manager(browser_manager)
        logger.info("Manual cleanup completed")
    
    logger.info("Example 2 completed\n")


async def example_priority_based_cleanup():
    """
    Example 3: Priority-based cleanup execution.
    
    This example demonstrates how cleanup tasks execute in priority order,
    with lower priority numbers executing first.
    """
    logger.info("=== Example 3: Priority-Based Cleanup ===")
    
    execution_order = []
    
    def make_cleanup(name):
        def cleanup():
            execution_order.append(name)
            logger.info(f"Cleaning up: {name}")
        return cleanup
    
    # Register tasks with different priorities
    register_cleanup("critical_resource", make_cleanup("critical"), priority=10)
    register_cleanup("important_resource", make_cleanup("important"), priority=50)
    register_cleanup("optional_resource", make_cleanup("optional"), priority=100)
    
    logger.info("Registered tasks: %s", cleanup_manager.get_registered_tasks())
    
    # Execute cleanup
    cleanup_all()
    
    logger.info("Execution order: %s", execution_order)
    logger.info("Expected order: ['critical', 'important', 'optional']")
    logger.info("Example 3 completed\n")


async def example_error_resilience():
    """
    Example 4: Error resilience during cleanup.
    
    This example shows how cleanup continues even if individual tasks fail.
    """
    logger.info("=== Example 4: Error Resilience ===")
    
    def failing_cleanup():
        logger.info("Attempting failing cleanup")
        raise Exception("Simulated cleanup error")
    
    def successful_cleanup():
        logger.info("Performing successful cleanup")
    
    # Register tasks (one will fail)
    register_cleanup("failing_task", failing_cleanup, priority=10)
    register_cleanup("successful_task", successful_cleanup, priority=20)
    
    # Execute cleanup - both tasks will be attempted
    cleanup_all()
    
    logger.info("Cleanup completed despite error")
    logger.info("Example 4 completed\n")


def example_screenshot_cleanup():
    """
    Example 5: Screenshot cleanup.
    
    This example demonstrates cleaning up screenshots based on test results,
    age, and count.
    """
    logger.info("=== Example 5: Screenshot Cleanup ===")
    
    # Create test screenshots directory
    screenshot_dir = Path("screenshots/test_failures")
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    
    # Create some test screenshots
    for i in range(5):
        screenshot_file = screenshot_dir / f"test_{i}.png"
        screenshot_file.write_text(f"Screenshot {i}")
    
    logger.info(f"Created {len(list(screenshot_dir.glob('*.png')))} screenshots")
    
    # Cleanup old screenshots (keep only 3)
    ScreenshotCleanupHelper.cleanup_old_screenshots(
        screenshot_dir=str(screenshot_dir),
        max_age_days=365,  # Don't delete by age
        max_count=3
    )
    
    remaining = len(list(screenshot_dir.glob("*.png")))
    logger.info(f"After cleanup: {remaining} screenshots remaining")
    
    # Cleanup all screenshots
    ScreenshotCleanupHelper.cleanup_all_screenshots(str(screenshot_dir))
    
    final_count = len(list(screenshot_dir.glob("*.png")))
    logger.info(f"After full cleanup: {final_count} screenshots remaining")
    logger.info("Example 5 completed\n")


def example_log_cleanup():
    """
    Example 6: Log file cleanup.
    
    This example demonstrates cleaning up old log files.
    """
    logger.info("=== Example 6: Log Cleanup ===")
    
    # Create test logs directory
    log_dir = Path("logs/test")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Create some test logs
    for i in range(5):
        log_file = log_dir / f"test_{i}.log"
        log_file.write_text(f"Log {i}")
    
    logger.info(f"Created {len(list(log_dir.glob('*.log')))} log files")
    
    # Cleanup old logs (keep only 3)
    LogCleanupHelper.cleanup_old_logs(
        log_dir=str(log_dir),
        max_age_days=365,  # Don't delete by age
        max_count=3
    )
    
    remaining = len(list(log_dir.glob("*.log")))
    logger.info(f"After cleanup: {remaining} log files remaining")
    logger.info("Example 6 completed\n")


def example_report_cleanup():
    """
    Example 7: Test report cleanup.
    
    This example demonstrates cleaning up old test reports.
    """
    logger.info("=== Example 7: Report Cleanup ===")
    
    # Create test reports directory
    report_dir = Path("reports/test")
    report_dir.mkdir(parents=True, exist_ok=True)
    
    # Create some test reports
    for i in range(5):
        report_file = report_dir / f"report_{i}.html"
        report_file.write_text(f"<html>Report {i}</html>")
    
    logger.info(f"Created {len(list(report_dir.glob('*.html')))} report files")
    
    # Cleanup old reports (keep only 3)
    ReportCleanupHelper.cleanup_old_reports(
        report_dir=str(report_dir),
        max_age_days=365,  # Don't delete by age
        max_count=3
    )
    
    remaining = len(list(report_dir.glob("*.html")))
    logger.info(f"After cleanup: {remaining} report files remaining")
    logger.info("Example 7 completed\n")


async def example_custom_cleanup():
    """
    Example 8: Custom cleanup with arguments.
    
    This example shows how to register custom cleanup functions with arguments.
    """
    logger.info("=== Example 8: Custom Cleanup ===")
    
    class CustomResource:
        """Example custom resource that needs cleanup."""
        
        def __init__(self, resource_id):
            self.resource_id = resource_id
            self.is_open = True
            logger.info(f"Resource {resource_id} created")
        
        def close(self, force=False):
            """Close the resource."""
            if self.is_open:
                logger.info(f"Closing resource {self.resource_id} (force={force})")
                self.is_open = False
            else:
                logger.info(f"Resource {self.resource_id} already closed")
    
    # Create resources
    resource1 = CustomResource(1)
    resource2 = CustomResource(2)
    
    # Register cleanup with arguments
    register_cleanup(
        "resource1_cleanup",
        resource1.close,
        priority=50,
        force=False
    )
    
    register_cleanup(
        "resource2_cleanup",
        resource2.close,
        priority=50,
        force=True
    )
    
    # Execute cleanup
    cleanup_all()
    
    logger.info("Example 8 completed\n")


async def example_context_manager():
    """
    Example 9: Cleanup with context manager.
    
    This example demonstrates using cleanup with context managers.
    """
    logger.info("=== Example 9: Context Manager ===")
    
    class ManagedResource:
        """Resource with automatic cleanup registration."""
        
        def __init__(self, name):
            self.name = name
            self.is_open = False
        
        def __enter__(self):
            self.is_open = True
            logger.info(f"Resource {self.name} opened")
            
            # Register cleanup
            register_cleanup(
                f"resource_{self.name}",
                self.cleanup,
                priority=50
            )
            
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            # Unregister and cleanup
            cleanup_manager.unregister_cleanup(f"resource_{self.name}")
            self.cleanup()
            return False
        
        def cleanup(self):
            if self.is_open:
                logger.info(f"Cleaning up resource {self.name}")
                self.is_open = False
    
    # Use context manager
    with ManagedResource("test_resource") as resource:
        logger.info(f"Using resource: {resource.name}")
    
    logger.info("Context manager exited, cleanup completed")
    logger.info("Example 9 completed\n")


async def main():
    """Run all examples."""
    logger.info("Starting Cleanup and Teardown Examples\n")
    
    try:
        # Run examples
        await example_automatic_cleanup()
        await example_manual_cleanup()
        await example_priority_based_cleanup()
        await example_error_resilience()
        example_screenshot_cleanup()
        example_log_cleanup()
        example_report_cleanup()
        await example_custom_cleanup()
        await example_context_manager()
        
        logger.info("All examples completed successfully!")
        
    except Exception as e:
        logger.error(f"Error running examples: {e}", exc_info=True)
    
    finally:
        # Final cleanup
        logger.info("\nPerforming final cleanup")
        cleanup_all()


if __name__ == "__main__":
    asyncio.run(main())
