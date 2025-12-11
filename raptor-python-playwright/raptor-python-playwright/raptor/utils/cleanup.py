"""
Test Cleanup and Teardown Utilities for RAPTOR Framework

This module provides comprehensive cleanup functionality for test execution:
- Automatic browser cleanup after tests
- Database connection cleanup
- Screenshot cleanup for passed tests
- Graceful shutdown handling
- Resource tracking and management

Requirements: 3.4, 11.5, 12.5
"""

import os
import logging
import signal
import sys
import atexit
from pathlib import Path
from typing import List, Optional, Callable, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class CleanupTask:
    """
    Represents a cleanup task to be executed.
    
    Attributes:
        name: Human-readable name for the task
        callback: Function to execute for cleanup
        priority: Execution priority (lower = earlier)
        args: Positional arguments for callback
        kwargs: Keyword arguments for callback
    """
    name: str
    callback: Callable
    priority: int = 100
    args: tuple = field(default_factory=tuple)
    kwargs: Dict[str, Any] = field(default_factory=dict)
    
    def execute(self) -> bool:
        """
        Execute the cleanup task.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.debug(f"Executing cleanup task: {self.name}")
            self.callback(*self.args, **self.kwargs)
            logger.info(f"Cleanup task completed: {self.name}")
            return True
        except Exception as e:
            logger.error(f"Cleanup task failed: {self.name} - {str(e)}")
            return False


class CleanupManager:
    """
    Manages cleanup tasks and ensures proper resource cleanup.
    
    This class provides:
    - Registration of cleanup tasks
    - Prioritized cleanup execution
    - Graceful shutdown handling
    - Signal handling for interrupts
    - Automatic cleanup on exit
    """
    
    _instance: Optional['CleanupManager'] = None
    _initialized: bool = False
    
    def __new__(cls):
        """Singleton pattern to ensure single cleanup manager."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the CleanupManager."""
        if not self._initialized:
            self._cleanup_tasks: List[CleanupTask] = []
            self._shutdown_in_progress: bool = False
            self._setup_signal_handlers()
            self._setup_exit_handler()
            CleanupManager._initialized = True
            logger.info("CleanupManager initialized")
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        # Handle SIGINT (Ctrl+C)
        signal.signal(signal.SIGINT, self._signal_handler)
        
        # Handle SIGTERM (termination signal)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Windows-specific: Handle CTRL_BREAK_EVENT
        if sys.platform == "win32":
            try:
                signal.signal(signal.SIGBREAK, self._signal_handler)
            except AttributeError:
                pass  # SIGBREAK not available on all Windows versions
        
        logger.debug("Signal handlers configured")
    
    def _setup_exit_handler(self):
        """Setup exit handler for automatic cleanup."""
        atexit.register(self._exit_handler)
        logger.debug("Exit handler registered")
    
    def _signal_handler(self, signum, frame):
        """
        Handle interrupt signals for graceful shutdown.
        
        Args:
            signum: Signal number
            frame: Current stack frame
        """
        signal_name = signal.Signals(signum).name
        logger.warning(f"Received signal {signal_name}, initiating graceful shutdown")
        
        if not self._shutdown_in_progress:
            self.cleanup_all()
            sys.exit(0)
    
    def _exit_handler(self):
        """Handle program exit for automatic cleanup."""
        if not self._shutdown_in_progress:
            logger.info("Program exit detected, performing cleanup")
            self.cleanup_all()
    
    def register_cleanup(
        self,
        name: str,
        callback: Callable,
        priority: int = 100,
        *args,
        **kwargs
    ):
        """
        Register a cleanup task.
        
        Args:
            name: Human-readable name for the task
            callback: Function to execute for cleanup
            priority: Execution priority (lower = earlier, default: 100)
            *args: Positional arguments for callback
            **kwargs: Keyword arguments for callback
            
        Example:
            cleanup_manager.register_cleanup(
                "close_browser",
                browser_manager.close_browser,
                priority=10
            )
        """
        task = CleanupTask(
            name=name,
            callback=callback,
            priority=priority,
            args=args,
            kwargs=kwargs
        )
        self._cleanup_tasks.append(task)
        logger.debug(f"Registered cleanup task: {name} (priority: {priority})")
    
    def unregister_cleanup(self, name: str) -> bool:
        """
        Unregister a cleanup task by name.
        
        Args:
            name: Name of the cleanup task to remove
            
        Returns:
            bool: True if task was found and removed, False otherwise
        """
        initial_count = len(self._cleanup_tasks)
        self._cleanup_tasks = [
            task for task in self._cleanup_tasks if task.name != name
        ]
        removed = len(self._cleanup_tasks) < initial_count
        
        if removed:
            logger.debug(f"Unregistered cleanup task: {name}")
        else:
            logger.warning(f"Cleanup task not found: {name}")
        
        return removed
    
    def cleanup_all(self):
        """
        Execute all registered cleanup tasks in priority order.
        
        Tasks are executed from lowest to highest priority number.
        Errors in individual tasks don't prevent other tasks from running.
        """
        if self._shutdown_in_progress:
            logger.debug("Cleanup already in progress, skipping")
            return
        
        self._shutdown_in_progress = True
        logger.info(f"Starting cleanup of {len(self._cleanup_tasks)} tasks")
        
        # Sort tasks by priority (lower priority = execute first)
        sorted_tasks = sorted(self._cleanup_tasks, key=lambda t: t.priority)
        
        success_count = 0
        failure_count = 0
        
        for task in sorted_tasks:
            if task.execute():
                success_count += 1
            else:
                failure_count += 1
        
        logger.info(
            f"Cleanup completed: {success_count} successful, "
            f"{failure_count} failed"
        )
        
        # Clear tasks after cleanup
        self._cleanup_tasks.clear()
        self._shutdown_in_progress = False
    
    def get_registered_tasks(self) -> List[str]:
        """
        Get list of registered cleanup task names.
        
        Returns:
            List of task names
        """
        return [task.name for task in self._cleanup_tasks]


class BrowserCleanupHelper:
    """
    Helper class for browser-specific cleanup operations.
    
    Provides utilities for cleaning up browser resources including
    contexts, pages, and browser instances.
    """
    
    @staticmethod
    async def cleanup_browser_manager(browser_manager):
        """
        Clean up a BrowserManager instance.
        
        Args:
            browser_manager: BrowserManager instance to clean up
        """
        try:
            if browser_manager and browser_manager.is_browser_launched:
                logger.info("Cleaning up browser manager")
                await browser_manager.close_browser()
                logger.info("Browser manager cleanup completed")
        except Exception as e:
            logger.error(f"Error during browser manager cleanup: {e}")
    
    @staticmethod
    async def cleanup_page(page):
        """
        Clean up a single page.
        
        Args:
            page: Playwright Page instance
        """
        try:
            if page and not page.is_closed():
                logger.debug("Closing page")
                await page.close()
        except Exception as e:
            logger.error(f"Error closing page: {e}")
    
    @staticmethod
    async def cleanup_context(context):
        """
        Clean up a browser context.
        
        Args:
            context: Playwright BrowserContext instance
        """
        try:
            if context:
                logger.debug("Closing browser context")
                await context.close()
        except Exception as e:
            logger.error(f"Error closing context: {e}")


class DatabaseCleanupHelper:
    """
    Helper class for database-specific cleanup operations.
    
    Provides utilities for cleaning up database connections and pools.
    """
    
    @staticmethod
    def cleanup_database_manager(database_manager):
        """
        Clean up a DatabaseManager instance.
        
        Args:
            database_manager: DatabaseManager instance to clean up
        """
        try:
            if database_manager:
                logger.info("Cleaning up database manager")
                database_manager.disconnect()
                logger.info("Database manager cleanup completed")
        except Exception as e:
            logger.error(f"Error during database manager cleanup: {e}")
    
    @staticmethod
    def cleanup_connection_pool(connection_pool):
        """
        Clean up a database connection pool.
        
        Args:
            connection_pool: ConnectionPool instance to clean up
        """
        try:
            if connection_pool:
                logger.info("Cleaning up connection pool")
                connection_pool.close_all()
                logger.info("Connection pool cleanup completed")
        except Exception as e:
            logger.error(f"Error during connection pool cleanup: {e}")


class ScreenshotCleanupHelper:
    """
    Helper class for screenshot cleanup operations.
    
    Provides utilities for cleaning up screenshots based on test results,
    age, and disk space management.
    """
    
    @staticmethod
    def cleanup_passed_test_screenshots(
        screenshot_dir: str = "screenshots/test_failures",
        test_results: Optional[List] = None
    ):
        """
        Clean up screenshots for passed tests.
        
        Args:
            screenshot_dir: Directory containing screenshots
            test_results: Optional list of test results to determine which to keep
        """
        try:
            screenshot_path = Path(screenshot_dir)
            if not screenshot_path.exists():
                logger.debug(f"Screenshot directory does not exist: {screenshot_dir}")
                return
            
            logger.info(f"Cleaning up passed test screenshots in: {screenshot_dir}")
            
            # If test results provided, only delete screenshots for passed tests
            if test_results:
                passed_test_names = {
                    result.test_name for result in test_results
                    if hasattr(result, 'status') and result.status.value == 'passed'
                }
                
                deleted_count = 0
                for screenshot_file in screenshot_path.glob("*.png"):
                    # Check if screenshot belongs to a passed test
                    test_name = screenshot_file.stem
                    if test_name in passed_test_names:
                        screenshot_file.unlink()
                        deleted_count += 1
                        logger.debug(f"Deleted screenshot for passed test: {test_name}")
                
                logger.info(f"Deleted {deleted_count} screenshots for passed tests")
            else:
                # No test results provided, keep all screenshots
                logger.debug("No test results provided, keeping all screenshots")
        
        except Exception as e:
            logger.error(f"Error during screenshot cleanup: {e}")
    
    @staticmethod
    def cleanup_old_screenshots(
        screenshot_dir: str = "screenshots/test_failures",
        max_age_days: int = 7,
        max_count: int = 100
    ):
        """
        Clean up old screenshots based on age and count.
        
        Args:
            screenshot_dir: Directory containing screenshots
            max_age_days: Maximum age in days to keep screenshots
            max_count: Maximum number of screenshots to keep
        """
        try:
            screenshot_path = Path(screenshot_dir)
            if not screenshot_path.exists():
                return
            
            logger.info(f"Cleaning up old screenshots in: {screenshot_dir}")
            
            # Get all screenshots with their modification times
            screenshots = []
            for screenshot_file in screenshot_path.glob("*.png"):
                mtime = screenshot_file.stat().st_mtime
                screenshots.append((screenshot_file, mtime))
            
            # Sort by modification time (newest first)
            screenshots.sort(key=lambda x: x[1], reverse=True)
            
            deleted_count = 0
            cutoff_time = datetime.now().timestamp() - (max_age_days * 86400)
            
            for idx, (screenshot_file, mtime) in enumerate(screenshots):
                # Delete if too old or beyond max count
                if mtime < cutoff_time or idx >= max_count:
                    screenshot_file.unlink()
                    deleted_count += 1
                    logger.debug(f"Deleted old screenshot: {screenshot_file.name}")
            
            logger.info(f"Deleted {deleted_count} old screenshots")
        
        except Exception as e:
            logger.error(f"Error during old screenshot cleanup: {e}")
    
    @staticmethod
    def cleanup_all_screenshots(screenshot_dir: str = "screenshots/test_failures"):
        """
        Clean up all screenshots in the directory.
        
        Args:
            screenshot_dir: Directory containing screenshots
        """
        try:
            screenshot_path = Path(screenshot_dir)
            if not screenshot_path.exists():
                return
            
            logger.info(f"Cleaning up all screenshots in: {screenshot_dir}")
            
            deleted_count = 0
            for screenshot_file in screenshot_path.glob("*.png"):
                screenshot_file.unlink()
                deleted_count += 1
            
            logger.info(f"Deleted {deleted_count} screenshots")
        
        except Exception as e:
            logger.error(f"Error during screenshot cleanup: {e}")


class LogCleanupHelper:
    """
    Helper class for log file cleanup operations.
    
    Provides utilities for cleaning up old log files and managing disk space.
    """
    
    @staticmethod
    def cleanup_old_logs(
        log_dir: str = "logs",
        max_age_days: int = 30,
        max_count: int = 50
    ):
        """
        Clean up old log files based on age and count.
        
        Args:
            log_dir: Directory containing log files
            max_age_days: Maximum age in days to keep logs
            max_count: Maximum number of log files to keep
        """
        try:
            log_path = Path(log_dir)
            if not log_path.exists():
                return
            
            logger.info(f"Cleaning up old logs in: {log_dir}")
            
            # Get all log files with their modification times
            log_files = []
            for log_file in log_path.rglob("*.log"):
                mtime = log_file.stat().st_mtime
                log_files.append((log_file, mtime))
            
            # Sort by modification time (newest first)
            log_files.sort(key=lambda x: x[1], reverse=True)
            
            deleted_count = 0
            cutoff_time = datetime.now().timestamp() - (max_age_days * 86400)
            
            for idx, (log_file, mtime) in enumerate(log_files):
                # Delete if too old or beyond max count
                if mtime < cutoff_time or idx >= max_count:
                    log_file.unlink()
                    deleted_count += 1
                    logger.debug(f"Deleted old log: {log_file.name}")
            
            logger.info(f"Deleted {deleted_count} old log files")
        
        except Exception as e:
            logger.error(f"Error during log cleanup: {e}")


class ReportCleanupHelper:
    """
    Helper class for test report cleanup operations.
    
    Provides utilities for cleaning up old test reports.
    """
    
    @staticmethod
    def cleanup_old_reports(
        report_dir: str = "reports",
        max_age_days: int = 30,
        max_count: int = 50
    ):
        """
        Clean up old test reports based on age and count.
        
        Args:
            report_dir: Directory containing test reports
            max_age_days: Maximum age in days to keep reports
            max_count: Maximum number of reports to keep
        """
        try:
            report_path = Path(report_dir)
            if not report_path.exists():
                return
            
            logger.info(f"Cleaning up old reports in: {report_dir}")
            
            # Get all report files with their modification times
            report_files = []
            for report_file in report_path.rglob("*.html"):
                mtime = report_file.stat().st_mtime
                report_files.append((report_file, mtime))
            
            # Sort by modification time (newest first)
            report_files.sort(key=lambda x: x[1], reverse=True)
            
            deleted_count = 0
            cutoff_time = datetime.now().timestamp() - (max_age_days * 86400)
            
            for idx, (report_file, mtime) in enumerate(report_files):
                # Delete if too old or beyond max count
                if mtime < cutoff_time or idx >= max_count:
                    report_file.unlink()
                    deleted_count += 1
                    logger.debug(f"Deleted old report: {report_file.name}")
            
            logger.info(f"Deleted {deleted_count} old report files")
        
        except Exception as e:
            logger.error(f"Error during report cleanup: {e}")


# Global cleanup manager instance
cleanup_manager = CleanupManager()


def register_cleanup(name: str, callback: Callable, priority: int = 100, *args, **kwargs):
    """
    Convenience function to register a cleanup task.
    
    Args:
        name: Human-readable name for the task
        callback: Function to execute for cleanup
        priority: Execution priority (lower = earlier)
        *args: Positional arguments for callback
        **kwargs: Keyword arguments for callback
    """
    cleanup_manager.register_cleanup(name, callback, priority, *args, **kwargs)


def cleanup_all():
    """Convenience function to execute all cleanup tasks."""
    cleanup_manager.cleanup_all()
