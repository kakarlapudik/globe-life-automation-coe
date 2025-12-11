"""
Simple Cleanup Example (No Browser Required)

This example demonstrates the cleanup functionality without requiring
browser installation, focusing on the core cleanup mechanisms.

Requirements: 3.4, 11.5, 12.5
"""

import logging
from pathlib import Path

from raptor.utils.cleanup import (
    cleanup_manager,
    register_cleanup,
    cleanup_all,
    ScreenshotCleanupHelper,
    LogCleanupHelper,
    ReportCleanupHelper
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def example_basic_cleanup():
    """Example 1: Basic cleanup registration and execution."""
    logger.info("=== Example 1: Basic Cleanup ===")
    
    def cleanup_task():
        logger.info("Executing cleanup task")
    
    # Register cleanup
    register_cleanup("basic_cleanup", cleanup_task, priority=50)
    
    logger.info("Registered tasks: %s", cleanup_manager.get_registered_tasks())
    
    # Execute cleanup
    cleanup_all()
    
    logger.info("Example 1 completed\n")


def example_priority_order():
    """Example 2: Priority-based execution order."""
    logger.info("=== Example 2: Priority Order ===")
    
    execution_order = []
    
    def make_cleanup(name):
        def cleanup():
            execution_order.append(name)
            logger.info(f"Cleaning up: {name}")
        return cleanup
    
    # Register with different priorities
    register_cleanup("low_priority", make_cleanup("low"), priority=100)
    register_cleanup("high_priority", make_cleanup("high"), priority=10)
    register_cleanup("medium_priority", make_cleanup("medium"), priority=50)
    
    # Execute cleanup
    cleanup_all()
    
    logger.info("Execution order: %s", execution_order)
    logger.info("Example 2 completed\n")


def example_error_handling():
    """Example 3: Error handling during cleanup."""
    logger.info("=== Example 3: Error Handling ===")
    
    def failing_cleanup():
        logger.info("Attempting failing cleanup")
        raise Exception("Simulated error")
    
    def successful_cleanup():
        logger.info("Performing successful cleanup")
    
    # Register both tasks
    register_cleanup("failing", failing_cleanup, priority=10)
    register_cleanup("successful", successful_cleanup, priority=20)
    
    # Execute - both will be attempted
    cleanup_all()
    
    logger.info("Cleanup completed despite error")
    logger.info("Example 3 completed\n")


def example_screenshot_cleanup():
    """Example 4: Screenshot cleanup."""
    logger.info("=== Example 4: Screenshot Cleanup ===")
    
    # Create test directory
    screenshot_dir = Path("test_screenshots")
    screenshot_dir.mkdir(exist_ok=True)
    
    # Create test screenshots
    for i in range(5):
        (screenshot_dir / f"test_{i}.png").write_text(f"Screenshot {i}")
    
    logger.info(f"Created {len(list(screenshot_dir.glob('*.png')))} screenshots")
    
    # Cleanup (keep only 3)
    ScreenshotCleanupHelper.cleanup_old_screenshots(
        screenshot_dir=str(screenshot_dir),
        max_age_days=365,
        max_count=3
    )
    
    remaining = len(list(screenshot_dir.glob("*.png")))
    logger.info(f"After cleanup: {remaining} screenshots")
    
    # Cleanup all
    ScreenshotCleanupHelper.cleanup_all_screenshots(str(screenshot_dir))
    screenshot_dir.rmdir()
    
    logger.info("Example 4 completed\n")


def example_log_cleanup():
    """Example 5: Log file cleanup."""
    logger.info("=== Example 5: Log Cleanup ===")
    
    # Create test directory
    log_dir = Path("test_logs")
    log_dir.mkdir(exist_ok=True)
    
    # Create test logs
    for i in range(5):
        (log_dir / f"test_{i}.log").write_text(f"Log {i}")
    
    logger.info(f"Created {len(list(log_dir.glob('*.log')))} log files")
    
    # Cleanup (keep only 3)
    LogCleanupHelper.cleanup_old_logs(
        log_dir=str(log_dir),
        max_age_days=365,
        max_count=3
    )
    
    remaining = len(list(log_dir.glob("*.log")))
    logger.info(f"After cleanup: {remaining} log files")
    
    # Cleanup remaining files and directory
    for log_file in log_dir.glob("*.log"):
        log_file.unlink()
    log_dir.rmdir()
    
    logger.info("Example 5 completed\n")


def example_custom_cleanup():
    """Example 6: Custom cleanup with arguments."""
    logger.info("=== Example 6: Custom Cleanup ===")
    
    class Resource:
        def __init__(self, resource_id):
            self.resource_id = resource_id
            self.is_open = True
            logger.info(f"Resource {resource_id} created")
        
        def close(self, force=False):
            if self.is_open:
                logger.info(f"Closing resource {self.resource_id} (force={force})")
                self.is_open = False
    
    # Create resources
    resource1 = Resource(1)
    resource2 = Resource(2)
    
    # Register cleanup with arguments
    register_cleanup("resource1", resource1.close, priority=50, force=False)
    register_cleanup("resource2", resource2.close, priority=50, force=True)
    
    # Execute cleanup
    cleanup_all()
    
    logger.info("Example 6 completed\n")


def main():
    """Run all examples."""
    logger.info("Starting Simple Cleanup Examples\n")
    
    try:
        example_basic_cleanup()
        example_priority_order()
        example_error_handling()
        example_screenshot_cleanup()
        example_log_cleanup()
        example_custom_cleanup()
        
        logger.info("All examples completed successfully!")
        
    except Exception as e:
        logger.error(f"Error running examples: {e}", exc_info=True)
    
    finally:
        # Final cleanup
        logger.info("\nPerforming final cleanup")
        cleanup_all()


if __name__ == "__main__":
    main()
