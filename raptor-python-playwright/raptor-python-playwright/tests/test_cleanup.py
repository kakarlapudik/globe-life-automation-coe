"""
Tests for Cleanup and Teardown Functionality

This module tests the cleanup utilities including:
- CleanupManager functionality
- Browser cleanup helpers
- Database cleanup helpers
- Screenshot cleanup helpers
- Log cleanup helpers
- Graceful shutdown handling

Requirements: 3.4, 11.5, 12.5
"""

import pytest
import asyncio
import os
import signal
import time
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch, MagicMock

from raptor.utils.cleanup import (
    CleanupManager,
    CleanupTask,
    BrowserCleanupHelper,
    DatabaseCleanupHelper,
    ScreenshotCleanupHelper,
    LogCleanupHelper,
    ReportCleanupHelper,
    cleanup_manager,
    register_cleanup,
    cleanup_all
)


class TestCleanupTask:
    """Test CleanupTask dataclass."""
    
    def test_cleanup_task_creation(self):
        """Test creating a cleanup task."""
        callback = Mock()
        task = CleanupTask(
            name="test_task",
            callback=callback,
            priority=50,
            args=(1, 2),
            kwargs={"key": "value"}
        )
        
        assert task.name == "test_task"
        assert task.callback == callback
        assert task.priority == 50
        assert task.args == (1, 2)
        assert task.kwargs == {"key": "value"}
    
    def test_cleanup_task_execute_success(self):
        """Test successful cleanup task execution."""
        callback = Mock()
        task = CleanupTask(
            name="test_task",
            callback=callback,
            args=(1, 2),
            kwargs={"key": "value"}
        )
        
        result = task.execute()
        
        assert result is True
        callback.assert_called_once_with(1, 2, key="value")
    
    def test_cleanup_task_execute_failure(self):
        """Test cleanup task execution with error."""
        callback = Mock(side_effect=Exception("Test error"))
        task = CleanupTask(
            name="test_task",
            callback=callback
        )
        
        result = task.execute()
        
        assert result is False


class TestCleanupManager:
    """Test CleanupManager class."""
    
    def test_cleanup_manager_singleton(self):
        """Test that CleanupManager is a singleton."""
        manager1 = CleanupManager()
        manager2 = CleanupManager()
        
        assert manager1 is manager2
    
    def test_register_cleanup(self):
        """Test registering a cleanup task."""
        manager = CleanupManager()
        callback = Mock()
        
        # Clear any existing tasks
        manager._cleanup_tasks.clear()
        
        manager.register_cleanup(
            name="test_cleanup",
            callback=callback,
            priority=50
        )
        
        tasks = manager.get_registered_tasks()
        assert "test_cleanup" in tasks
    
    def test_unregister_cleanup(self):
        """Test unregistering a cleanup task."""
        manager = CleanupManager()
        callback = Mock()
        
        # Clear and register
        manager._cleanup_tasks.clear()
        manager.register_cleanup(
            name="test_cleanup",
            callback=callback
        )
        
        # Unregister
        result = manager.unregister_cleanup("test_cleanup")
        
        assert result is True
        assert "test_cleanup" not in manager.get_registered_tasks()
    
    def test_unregister_nonexistent_cleanup(self):
        """Test unregistering a non-existent cleanup task."""
        manager = CleanupManager()
        
        result = manager.unregister_cleanup("nonexistent")
        
        assert result is False
    
    def test_cleanup_all_priority_order(self):
        """Test that cleanup tasks execute in priority order."""
        manager = CleanupManager()
        execution_order = []
        
        def make_callback(name):
            def callback():
                execution_order.append(name)
            return callback
        
        # Clear and register tasks with different priorities
        manager._cleanup_tasks.clear()
        manager.register_cleanup("low_priority", make_callback("low"), priority=100)
        manager.register_cleanup("high_priority", make_callback("high"), priority=10)
        manager.register_cleanup("medium_priority", make_callback("medium"), priority=50)
        
        # Execute cleanup
        manager.cleanup_all()
        
        # Verify execution order (low priority number = execute first)
        assert execution_order == ["high", "medium", "low"]
    
    def test_cleanup_all_continues_on_error(self):
        """Test that cleanup continues even if a task fails."""
        manager = CleanupManager()
        successful_callback = Mock()
        failing_callback = Mock(side_effect=Exception("Test error"))
        
        # Clear and register tasks
        manager._cleanup_tasks.clear()
        manager.register_cleanup("failing", failing_callback, priority=10)
        manager.register_cleanup("successful", successful_callback, priority=20)
        
        # Execute cleanup
        manager.cleanup_all()
        
        # Both should have been attempted
        failing_callback.assert_called_once()
        successful_callback.assert_called_once()
    
    def test_cleanup_all_clears_tasks(self):
        """Test that cleanup_all clears tasks after execution."""
        manager = CleanupManager()
        callback = Mock()
        
        # Clear and register
        manager._cleanup_tasks.clear()
        manager.register_cleanup("test", callback)
        
        # Execute cleanup
        manager.cleanup_all()
        
        # Tasks should be cleared
        assert len(manager.get_registered_tasks()) == 0
    
    def test_cleanup_all_prevents_duplicate_execution(self):
        """Test that cleanup_all prevents duplicate execution."""
        manager = CleanupManager()
        callback = Mock()
        
        # Clear and register
        manager._cleanup_tasks.clear()
        manager.register_cleanup("test", callback)
        
        # Execute cleanup twice
        manager.cleanup_all()
        manager.cleanup_all()
        
        # Callback should only be called once
        callback.assert_called_once()


class TestBrowserCleanupHelper:
    """Test BrowserCleanupHelper class."""
    
    @pytest.mark.asyncio
    async def test_cleanup_browser_manager(self):
        """Test cleaning up a browser manager."""
        mock_manager = Mock()
        mock_manager.is_browser_launched = True
        mock_manager.close_browser = AsyncMock()
        
        await BrowserCleanupHelper.cleanup_browser_manager(mock_manager)
        
        mock_manager.close_browser.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_cleanup_browser_manager_not_launched(self):
        """Test cleaning up a browser manager that wasn't launched."""
        mock_manager = Mock()
        mock_manager.is_browser_launched = False
        mock_manager.close_browser = AsyncMock()
        
        await BrowserCleanupHelper.cleanup_browser_manager(mock_manager)
        
        # Should not call close_browser if not launched
        mock_manager.close_browser.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_cleanup_browser_manager_error(self):
        """Test browser manager cleanup handles errors gracefully."""
        mock_manager = Mock()
        mock_manager.is_browser_launched = True
        mock_manager.close_browser = AsyncMock(side_effect=Exception("Test error"))
        
        # Should not raise exception
        await BrowserCleanupHelper.cleanup_browser_manager(mock_manager)
    
    @pytest.mark.asyncio
    async def test_cleanup_page(self):
        """Test cleaning up a page."""
        mock_page = Mock()
        mock_page.is_closed = Mock(return_value=False)
        mock_page.close = AsyncMock()
        
        await BrowserCleanupHelper.cleanup_page(mock_page)
        
        mock_page.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_cleanup_page_already_closed(self):
        """Test cleaning up an already closed page."""
        mock_page = Mock()
        mock_page.is_closed = Mock(return_value=True)
        mock_page.close = AsyncMock()
        
        await BrowserCleanupHelper.cleanup_page(mock_page)
        
        # Should not call close if already closed
        mock_page.close.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_cleanup_context(self):
        """Test cleaning up a browser context."""
        mock_context = Mock()
        mock_context.close = AsyncMock()
        
        await BrowserCleanupHelper.cleanup_context(mock_context)
        
        mock_context.close.assert_called_once()


class TestDatabaseCleanupHelper:
    """Test DatabaseCleanupHelper class."""
    
    def test_cleanup_database_manager(self):
        """Test cleaning up a database manager."""
        mock_manager = Mock()
        mock_manager.disconnect = Mock()
        
        DatabaseCleanupHelper.cleanup_database_manager(mock_manager)
        
        mock_manager.disconnect.assert_called_once()
    
    def test_cleanup_database_manager_error(self):
        """Test database manager cleanup handles errors gracefully."""
        mock_manager = Mock()
        mock_manager.disconnect = Mock(side_effect=Exception("Test error"))
        
        # Should not raise exception
        DatabaseCleanupHelper.cleanup_database_manager(mock_manager)
    
    def test_cleanup_connection_pool(self):
        """Test cleaning up a connection pool."""
        mock_pool = Mock()
        mock_pool.close_all = Mock()
        
        DatabaseCleanupHelper.cleanup_connection_pool(mock_pool)
        
        mock_pool.close_all.assert_called_once()


class TestScreenshotCleanupHelper:
    """Test ScreenshotCleanupHelper class."""
    
    def test_cleanup_passed_test_screenshots(self, tmp_path):
        """Test cleaning up screenshots for passed tests."""
        # Create test screenshots
        screenshot_dir = tmp_path / "screenshots"
        screenshot_dir.mkdir()
        
        passed_screenshot = screenshot_dir / "test_passed.png"
        failed_screenshot = screenshot_dir / "test_failed.png"
        passed_screenshot.write_text("passed")
        failed_screenshot.write_text("failed")
        
        # Create mock test results
        mock_passed_result = Mock()
        mock_passed_result.test_name = "test_passed"
        mock_passed_result.status = Mock(value="passed")
        
        mock_failed_result = Mock()
        mock_failed_result.test_name = "test_failed"
        mock_failed_result.status = Mock(value="failed")
        
        test_results = [mock_passed_result, mock_failed_result]
        
        # Cleanup
        ScreenshotCleanupHelper.cleanup_passed_test_screenshots(
            screenshot_dir=str(screenshot_dir),
            test_results=test_results
        )
        
        # Passed screenshot should be deleted, failed should remain
        assert not passed_screenshot.exists()
        assert failed_screenshot.exists()
    
    def test_cleanup_old_screenshots_by_age(self, tmp_path):
        """Test cleaning up old screenshots by age."""
        screenshot_dir = tmp_path / "screenshots"
        screenshot_dir.mkdir()
        
        # Create old and new screenshots
        old_screenshot = screenshot_dir / "old.png"
        new_screenshot = screenshot_dir / "new.png"
        old_screenshot.write_text("old")
        new_screenshot.write_text("new")
        
        # Set old modification time (8 days ago)
        old_time = (datetime.now() - timedelta(days=8)).timestamp()
        os.utime(old_screenshot, (old_time, old_time))
        
        # Cleanup (max age 7 days)
        ScreenshotCleanupHelper.cleanup_old_screenshots(
            screenshot_dir=str(screenshot_dir),
            max_age_days=7,
            max_count=100
        )
        
        # Old screenshot should be deleted, new should remain
        assert not old_screenshot.exists()
        assert new_screenshot.exists()
    
    def test_cleanup_old_screenshots_by_count(self, tmp_path):
        """Test cleaning up old screenshots by count."""
        screenshot_dir = tmp_path / "screenshots"
        screenshot_dir.mkdir()
        
        # Create multiple screenshots
        screenshots = []
        for i in range(5):
            screenshot = screenshot_dir / f"screenshot_{i}.png"
            screenshot.write_text(f"screenshot {i}")
            screenshots.append(screenshot)
            time.sleep(0.01)  # Ensure different modification times
        
        # Cleanup (keep only 3)
        ScreenshotCleanupHelper.cleanup_old_screenshots(
            screenshot_dir=str(screenshot_dir),
            max_age_days=365,  # Don't delete by age
            max_count=3
        )
        
        # Oldest 2 should be deleted, newest 3 should remain
        assert not screenshots[0].exists()
        assert not screenshots[1].exists()
        assert screenshots[2].exists()
        assert screenshots[3].exists()
        assert screenshots[4].exists()
    
    def test_cleanup_all_screenshots(self, tmp_path):
        """Test cleaning up all screenshots."""
        screenshot_dir = tmp_path / "screenshots"
        screenshot_dir.mkdir()
        
        # Create screenshots
        for i in range(3):
            screenshot = screenshot_dir / f"screenshot_{i}.png"
            screenshot.write_text(f"screenshot {i}")
        
        # Cleanup all
        ScreenshotCleanupHelper.cleanup_all_screenshots(
            screenshot_dir=str(screenshot_dir)
        )
        
        # All screenshots should be deleted
        assert len(list(screenshot_dir.glob("*.png"))) == 0


class TestLogCleanupHelper:
    """Test LogCleanupHelper class."""
    
    def test_cleanup_old_logs_by_age(self, tmp_path):
        """Test cleaning up old log files by age."""
        log_dir = tmp_path / "logs"
        log_dir.mkdir()
        
        # Create old and new logs
        old_log = log_dir / "old.log"
        new_log = log_dir / "new.log"
        old_log.write_text("old log")
        new_log.write_text("new log")
        
        # Set old modification time (31 days ago)
        old_time = (datetime.now() - timedelta(days=31)).timestamp()
        os.utime(old_log, (old_time, old_time))
        
        # Cleanup (max age 30 days)
        LogCleanupHelper.cleanup_old_logs(
            log_dir=str(log_dir),
            max_age_days=30,
            max_count=100
        )
        
        # Old log should be deleted, new should remain
        assert not old_log.exists()
        assert new_log.exists()
    
    def test_cleanup_old_logs_by_count(self, tmp_path):
        """Test cleaning up old log files by count."""
        log_dir = tmp_path / "logs"
        log_dir.mkdir()
        
        # Create multiple logs
        logs = []
        for i in range(5):
            log = log_dir / f"log_{i}.log"
            log.write_text(f"log {i}")
            logs.append(log)
            time.sleep(0.01)  # Ensure different modification times
        
        # Cleanup (keep only 3)
        LogCleanupHelper.cleanup_old_logs(
            log_dir=str(log_dir),
            max_age_days=365,  # Don't delete by age
            max_count=3
        )
        
        # Oldest 2 should be deleted, newest 3 should remain
        assert not logs[0].exists()
        assert not logs[1].exists()
        assert logs[2].exists()
        assert logs[3].exists()
        assert logs[4].exists()


class TestReportCleanupHelper:
    """Test ReportCleanupHelper class."""
    
    def test_cleanup_old_reports_by_age(self, tmp_path):
        """Test cleaning up old report files by age."""
        report_dir = tmp_path / "reports"
        report_dir.mkdir()
        
        # Create old and new reports
        old_report = report_dir / "old.html"
        new_report = report_dir / "new.html"
        old_report.write_text("old report")
        new_report.write_text("new report")
        
        # Set old modification time (31 days ago)
        old_time = (datetime.now() - timedelta(days=31)).timestamp()
        os.utime(old_report, (old_time, old_time))
        
        # Cleanup (max age 30 days)
        ReportCleanupHelper.cleanup_old_reports(
            report_dir=str(report_dir),
            max_age_days=30,
            max_count=100
        )
        
        # Old report should be deleted, new should remain
        assert not old_report.exists()
        assert new_report.exists()
    
    def test_cleanup_old_reports_by_count(self, tmp_path):
        """Test cleaning up old report files by count."""
        report_dir = tmp_path / "reports"
        report_dir.mkdir()
        
        # Create multiple reports
        reports = []
        for i in range(5):
            report = report_dir / f"report_{i}.html"
            report.write_text(f"report {i}")
            reports.append(report)
            time.sleep(0.01)  # Ensure different modification times
        
        # Cleanup (keep only 3)
        ReportCleanupHelper.cleanup_old_reports(
            report_dir=str(report_dir),
            max_age_days=365,  # Don't delete by age
            max_count=3
        )
        
        # Oldest 2 should be deleted, newest 3 should remain
        assert not reports[0].exists()
        assert not reports[1].exists()
        assert reports[2].exists()
        assert reports[3].exists()
        assert reports[4].exists()


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    def test_register_cleanup_function(self):
        """Test register_cleanup convenience function."""
        callback = Mock()
        
        # Clear existing tasks
        cleanup_manager._cleanup_tasks.clear()
        
        register_cleanup("test", callback, priority=50)
        
        assert "test" in cleanup_manager.get_registered_tasks()
    
    def test_cleanup_all_function(self):
        """Test cleanup_all convenience function."""
        callback = Mock()
        
        # Clear and register
        cleanup_manager._cleanup_tasks.clear()
        register_cleanup("test", callback)
        
        cleanup_all()
        
        callback.assert_called_once()


class TestGracefulShutdown:
    """Test graceful shutdown handling."""
    
    def test_signal_handler_registration(self):
        """Test that signal handlers are registered."""
        manager = CleanupManager()
        
        # Verify signal handlers are set
        assert signal.getsignal(signal.SIGINT) is not signal.SIG_DFL
        assert signal.getsignal(signal.SIGTERM) is not signal.SIG_DFL
    
    @patch('sys.exit')
    def test_signal_handler_triggers_cleanup(self, mock_exit):
        """Test that signal handler triggers cleanup."""
        manager = CleanupManager()
        callback = Mock()
        
        # Clear and register
        manager._cleanup_tasks.clear()
        manager.register_cleanup("test", callback)
        
        # Simulate signal
        manager._signal_handler(signal.SIGINT, None)
        
        # Cleanup should have been called
        callback.assert_called_once()
        mock_exit.assert_called_once_with(0)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
