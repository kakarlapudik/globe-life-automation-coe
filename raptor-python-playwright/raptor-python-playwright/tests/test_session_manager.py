"""
Unit tests for SessionManager.

Tests session save, restore, list, delete, and validation functionality.
"""

import pytest
import asyncio
import json
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from playwright.async_api import Page, Browser, BrowserContext

from raptor.core.session_manager import SessionManager, SessionInfo
from raptor.core.exceptions import SessionException


@pytest.fixture
def temp_session_dir(tmp_path):
    """Create a temporary directory for session storage."""
    session_dir = tmp_path / "sessions"
    session_dir.mkdir()
    return session_dir


@pytest.fixture
def session_manager(temp_session_dir):
    """Create a SessionManager instance with temporary storage."""
    return SessionManager(storage_dir=str(temp_session_dir))


@pytest.fixture
def mock_page():
    """Create a mock Playwright Page object."""
    page = AsyncMock(spec=Page)
    page.url = "https://example.com"
    page.title = AsyncMock(return_value="Example Page")
    
    # Mock context and browser
    context = Mock(spec=BrowserContext)
    browser = Mock(spec=Browser)
    browser.ws_endpoint = Mock(return_value="ws://localhost:9222/devtools/browser/test-id")
    
    context.browser = browser
    page.context = context
    
    return page


class TestSessionManagerInitialization:
    """Test SessionManager initialization."""

    def test_init_with_default_storage(self):
        """Test initialization with default storage directory."""
        manager = SessionManager()
        
        assert manager._storage_dir.exists()
        assert manager._storage_dir.name == "sessions"
        assert ".raptor" in str(manager._storage_dir)

    def test_init_with_custom_storage(self, temp_session_dir):
        """Test initialization with custom storage directory."""
        manager = SessionManager(storage_dir=str(temp_session_dir))
        
        assert manager._storage_dir == temp_session_dir
        assert manager._storage_dir.exists()

    def test_storage_dir_created_if_not_exists(self, tmp_path):
        """Test that storage directory is created if it doesn't exist."""
        new_dir = tmp_path / "new_sessions"
        assert not new_dir.exists()
        
        manager = SessionManager(storage_dir=str(new_dir))
        
        assert new_dir.exists()


class TestSaveSession:
    """Test session saving functionality."""

    @pytest.mark.asyncio
    async def test_save_session_success(self, session_manager, mock_page):
        """Test successful session save."""
        session_info = await session_manager.save_session(
            mock_page,
            "test_session",
            metadata={"test": "data"}
        )
        
        assert session_info.session_id == "test_session"
        assert session_info.cdp_url == "ws://localhost:9222/devtools/browser/test-id"
        assert session_info.browser_type == "chromium"
        assert session_info.metadata["test"] == "data"
        assert "page_url" in session_info.metadata
        assert "page_title" in session_info.metadata

    @pytest.mark.asyncio
    async def test_save_session_creates_file(self, session_manager, mock_page):
        """Test that session save creates a file."""
        await session_manager.save_session(mock_page, "test_session")
        
        session_file = session_manager._get_session_file_path("test_session")
        assert session_file.exists()
        
        # Verify file content
        with open(session_file, 'r') as f:
            data = json.load(f)
            assert data["session_id"] == "test_session"
            assert "cdp_url" in data
            assert "created_at" in data

    @pytest.mark.asyncio
    async def test_save_session_empty_name_raises_error(self, session_manager, mock_page):
        """Test that empty session name raises SessionException."""
        with pytest.raises(SessionException) as exc_info:
            await session_manager.save_session(mock_page, "")
        
        assert "Session name cannot be empty" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_save_session_no_browser_raises_error(self, session_manager):
        """Test that page without browser raises SessionException."""
        page = AsyncMock(spec=Page)
        context = Mock(spec=BrowserContext)
        context.browser = None
        page.context = context
        
        with pytest.raises(SessionException) as exc_info:
            await session_manager.save_session(page, "test_session")
        
        assert "not attached to a browser" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_save_session_overwrites_existing(self, session_manager, mock_page):
        """Test that saving with same name overwrites existing session."""
        # Save first session
        await session_manager.save_session(
            mock_page,
            "test_session",
            metadata={"version": 1}
        )
        
        # Save second session with same name
        await session_manager.save_session(
            mock_page,
            "test_session",
            metadata={"version": 2}
        )
        
        # Verify only one file exists with latest data
        session_info = session_manager.get_session_info("test_session")
        assert session_info.metadata["version"] == 2


class TestRestoreSession:
    """Test session restoration functionality."""

    @pytest.mark.asyncio
    async def test_restore_session_not_found_raises_error(self, session_manager):
        """Test that restoring non-existent session raises SessionException."""
        with pytest.raises(SessionException) as exc_info:
            await session_manager.restore_session("nonexistent_session")
        
        # After validation enhancement, error message is about validation failure
        assert "validation failed" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_restore_session_no_cdp_url_raises_error(
        self, session_manager, temp_session_dir
    ):
        """Test that session without CDP URL raises SessionException."""
        # Create session file without CDP URL
        session_data = {
            "session_id": "test_session",
            "cdp_url": "",
            "browser_type": "firefox",
            "created_at": datetime.now().isoformat(),
            "last_accessed": datetime.now().isoformat(),
            "metadata": {}
        }
        
        session_file = temp_session_dir / "test_session.json"
        with open(session_file, 'w') as f:
            json.dump(session_data, f)
        
        with pytest.raises(SessionException) as exc_info:
            await session_manager.restore_session("test_session")
        
        # After validation enhancement, error message is about validation failure
        assert "validation failed" in str(exc_info.value).lower()


class TestListSessions:
    """Test session listing functionality."""

    def test_list_sessions_empty(self, session_manager):
        """Test listing sessions when none exist."""
        sessions = session_manager.list_sessions()
        assert sessions == []

    @pytest.mark.asyncio
    async def test_list_sessions_with_saved_sessions(self, session_manager, mock_page):
        """Test listing multiple saved sessions."""
        # Save multiple sessions
        await session_manager.save_session(mock_page, "session1")
        await session_manager.save_session(mock_page, "session2")
        await session_manager.save_session(mock_page, "session3")
        
        sessions = session_manager.list_sessions()
        
        assert len(sessions) == 3
        assert "session1" in sessions
        assert "session2" in sessions
        assert "session3" in sessions
        assert sessions == sorted(sessions)  # Should be sorted


class TestDeleteSession:
    """Test session deletion functionality."""

    @pytest.mark.asyncio
    async def test_delete_session_success(self, session_manager, mock_page):
        """Test successful session deletion."""
        # Save a session
        await session_manager.save_session(mock_page, "test_session")
        assert "test_session" in session_manager.list_sessions()
        
        # Delete the session
        result = session_manager.delete_session("test_session")
        
        assert result is True
        assert "test_session" not in session_manager.list_sessions()

    def test_delete_session_not_found(self, session_manager):
        """Test deleting non-existent session returns False."""
        result = session_manager.delete_session("nonexistent_session")
        assert result is False


class TestGetSessionInfo:
    """Test getting session information."""

    @pytest.mark.asyncio
    async def test_get_session_info_success(self, session_manager, mock_page):
        """Test getting session info for existing session."""
        # Save a session
        await session_manager.save_session(
            mock_page,
            "test_session",
            metadata={"key": "value"}
        )
        
        # Get session info
        info = session_manager.get_session_info("test_session")
        
        assert info is not None
        assert info.session_id == "test_session"
        assert info.browser_type == "chromium"
        assert info.metadata["key"] == "value"

    def test_get_session_info_not_found(self, session_manager):
        """Test getting info for non-existent session returns None."""
        info = session_manager.get_session_info("nonexistent_session")
        assert info is None


class TestValidateSession:
    """Test session validation."""

    @pytest.mark.asyncio
    async def test_validate_session_valid(self, session_manager, mock_page):
        """Test validation of valid session."""
        await session_manager.save_session(mock_page, "test_session")
        
        is_valid = session_manager.validate_session("test_session")
        assert is_valid is True

    def test_validate_session_not_found(self, session_manager):
        """Test validation of non-existent session."""
        is_valid = session_manager.validate_session("nonexistent_session")
        assert is_valid is False

    def test_validate_session_missing_cdp_url(self, session_manager, temp_session_dir):
        """Test validation of session without CDP URL."""
        # Create session file without CDP URL
        session_data = {
            "session_id": "test_session",
            "cdp_url": "",
            "browser_type": "firefox",
            "created_at": datetime.now().isoformat(),
            "last_accessed": datetime.now().isoformat(),
            "metadata": {}
        }
        
        session_file = temp_session_dir / "test_session.json"
        with open(session_file, 'w') as f:
            json.dump(session_data, f)
        
        is_valid = session_manager.validate_session("test_session")
        assert is_valid is False


class TestCleanupExpiredSessions:
    """Test cleanup of expired sessions."""

    @pytest.mark.asyncio
    async def test_cleanup_expired_sessions(self, session_manager, mock_page, temp_session_dir):
        """Test cleanup of sessions older than max age."""
        # Create old session
        old_date = (datetime.now() - timedelta(days=10)).isoformat()
        old_session_data = {
            "session_id": "old_session",
            "cdp_url": "ws://localhost:9222/test",
            "browser_type": "chromium",
            "created_at": old_date,
            "last_accessed": old_date,
            "metadata": {}
        }
        
        old_session_file = temp_session_dir / "old_session.json"
        with open(old_session_file, 'w') as f:
            json.dump(old_session_data, f)
        
        # Create recent session
        await session_manager.save_session(mock_page, "recent_session")
        
        # Cleanup sessions older than 7 days
        deleted_count = session_manager.cleanup_expired_sessions(max_age_days=7)
        
        assert deleted_count == 1
        assert "old_session" not in session_manager.list_sessions()
        assert "recent_session" in session_manager.list_sessions()

    def test_cleanup_no_expired_sessions(self, session_manager):
        """Test cleanup when no sessions are expired."""
        deleted_count = session_manager.cleanup_expired_sessions(max_age_days=7)
        assert deleted_count == 0


class TestSessionInfo:
    """Test SessionInfo dataclass."""

    def test_session_info_to_dict(self):
        """Test converting SessionInfo to dictionary."""
        now = datetime.now().isoformat()
        info = SessionInfo(
            session_id="test",
            cdp_url="ws://localhost:9222/test",
            browser_type="chromium",
            created_at=now,
            last_accessed=now,
            metadata={"key": "value"}
        )
        
        data = info.to_dict()
        
        assert data["session_id"] == "test"
        assert data["cdp_url"] == "ws://localhost:9222/test"
        assert data["browser_type"] == "chromium"
        assert data["metadata"]["key"] == "value"

    def test_session_info_from_dict(self):
        """Test creating SessionInfo from dictionary."""
        now = datetime.now().isoformat()
        data = {
            "session_id": "test",
            "cdp_url": "ws://localhost:9222/test",
            "browser_type": "chromium",
            "created_at": now,
            "last_accessed": now,
            "metadata": {"key": "value"}
        }
        
        info = SessionInfo.from_dict(data)
        
        assert info.session_id == "test"
        assert info.cdp_url == "ws://localhost:9222/test"
        assert info.browser_type == "chromium"
        assert info.metadata["key"] == "value"


class TestCleanupInvalidSessions:
    """Test cleanup of invalid sessions."""

    def test_cleanup_invalid_sessions(self, session_manager, temp_session_dir):
        """Test cleanup of sessions with invalid data."""
        # Create invalid session (missing required fields)
        invalid_session_data = {
            "session_id": "",  # Invalid: empty session_id
            "cdp_url": "ws://localhost:9222/test",
            "browser_type": "chromium",
            "created_at": datetime.now().isoformat(),
            "last_accessed": datetime.now().isoformat(),
            "metadata": {}
        }
        
        invalid_session_file = temp_session_dir / "invalid_session.json"
        with open(invalid_session_file, 'w') as f:
            json.dump(invalid_session_data, f)
        
        # Create corrupted session (invalid JSON structure)
        corrupted_file = temp_session_dir / "corrupted_session.json"
        with open(corrupted_file, 'w') as f:
            f.write("{ invalid json }")
        
        # Cleanup invalid sessions
        deleted_count = session_manager.cleanup_invalid_sessions()
        
        assert deleted_count == 2
        assert "invalid_session" not in session_manager.list_sessions()
        assert "corrupted_session" not in session_manager.list_sessions()

    def test_cleanup_invalid_sessions_with_invalid_timestamps(
        self, session_manager, temp_session_dir
    ):
        """Test cleanup of sessions with invalid timestamps."""
        invalid_session_data = {
            "session_id": "test_session",
            "cdp_url": "ws://localhost:9222/test",
            "browser_type": "chromium",
            "created_at": "invalid-date",
            "last_accessed": "invalid-date",
            "metadata": {}
        }
        
        session_file = temp_session_dir / "test_session.json"
        with open(session_file, 'w') as f:
            json.dump(invalid_session_data, f)
        
        deleted_count = session_manager.cleanup_invalid_sessions()
        assert deleted_count == 1

    def test_cleanup_invalid_sessions_with_invalid_browser_type(
        self, session_manager, temp_session_dir
    ):
        """Test cleanup of sessions with invalid browser type."""
        invalid_session_data = {
            "session_id": "test_session",
            "cdp_url": "ws://localhost:9222/test",
            "browser_type": "invalid_browser",
            "created_at": datetime.now().isoformat(),
            "last_accessed": datetime.now().isoformat(),
            "metadata": {}
        }
        
        session_file = temp_session_dir / "test_session.json"
        with open(session_file, 'w') as f:
            json.dump(invalid_session_data, f)
        
        deleted_count = session_manager.cleanup_invalid_sessions()
        assert deleted_count == 1


class TestCleanupAllSessions:
    """Test cleanup of all sessions."""

    @pytest.mark.asyncio
    async def test_cleanup_all_sessions(self, session_manager, mock_page):
        """Test deleting all sessions."""
        # Create multiple sessions
        await session_manager.save_session(mock_page, "session1")
        await session_manager.save_session(mock_page, "session2")
        await session_manager.save_session(mock_page, "session3")
        
        assert len(session_manager.list_sessions()) == 3
        
        # Cleanup all sessions
        deleted_count = session_manager.cleanup_all_sessions()
        
        assert deleted_count == 3
        assert len(session_manager.list_sessions()) == 0

    def test_cleanup_all_sessions_empty(self, session_manager):
        """Test cleanup when no sessions exist."""
        deleted_count = session_manager.cleanup_all_sessions()
        assert deleted_count == 0


class TestSessionCount:
    """Test session count functionality."""

    @pytest.mark.asyncio
    async def test_get_session_count(self, session_manager, mock_page):
        """Test getting session count."""
        assert session_manager.get_session_count() == 0
        
        await session_manager.save_session(mock_page, "session1")
        assert session_manager.get_session_count() == 1
        
        await session_manager.save_session(mock_page, "session2")
        assert session_manager.get_session_count() == 2
        
        session_manager.delete_session("session1")
        assert session_manager.get_session_count() == 1


class TestStorageSize:
    """Test storage size calculation."""

    @pytest.mark.asyncio
    async def test_get_storage_size(self, session_manager, mock_page):
        """Test getting storage size."""
        initial_size = session_manager.get_storage_size()
        assert initial_size == 0
        
        # Save a session
        await session_manager.save_session(mock_page, "test_session")
        
        # Storage size should be greater than 0
        size = session_manager.get_storage_size()
        assert size > 0

    @pytest.mark.asyncio
    async def test_get_storage_size_multiple_sessions(
        self, session_manager, mock_page
    ):
        """Test storage size with multiple sessions."""
        await session_manager.save_session(mock_page, "session1")
        size1 = session_manager.get_storage_size()
        
        await session_manager.save_session(mock_page, "session2")
        size2 = session_manager.get_storage_size()
        
        # Size should increase with more sessions
        assert size2 > size1


class TestAutoCleanupOnInit:
    """Test automatic cleanup on initialization."""

    def test_auto_cleanup_on_init_disabled(self, temp_session_dir):
        """Test that auto cleanup is disabled by default."""
        # Create old session
        old_date = (datetime.now() - timedelta(days=10)).isoformat()
        old_session_data = {
            "session_id": "old_session",
            "cdp_url": "ws://localhost:9222/test",
            "browser_type": "chromium",
            "created_at": old_date,
            "last_accessed": old_date,
            "metadata": {}
        }
        
        old_session_file = temp_session_dir / "old_session.json"
        with open(old_session_file, 'w') as f:
            json.dump(old_session_data, f)
        
        # Initialize without auto cleanup
        manager = SessionManager(storage_dir=str(temp_session_dir))
        
        # Old session should still exist
        assert "old_session" in manager.list_sessions()

    def test_auto_cleanup_on_init_enabled(self, temp_session_dir):
        """Test automatic cleanup on initialization."""
        # Create old session
        old_date = (datetime.now() - timedelta(days=10)).isoformat()
        old_session_data = {
            "session_id": "old_session",
            "cdp_url": "ws://localhost:9222/test",
            "browser_type": "chromium",
            "created_at": old_date,
            "last_accessed": old_date,
            "metadata": {}
        }
        
        old_session_file = temp_session_dir / "old_session.json"
        with open(old_session_file, 'w') as f:
            json.dump(old_session_data, f)
        
        # Create invalid session
        invalid_session_data = {
            "session_id": "",
            "cdp_url": "ws://localhost:9222/test",
            "browser_type": "chromium",
            "created_at": datetime.now().isoformat(),
            "last_accessed": datetime.now().isoformat(),
            "metadata": {}
        }
        
        invalid_session_file = temp_session_dir / "invalid_session.json"
        with open(invalid_session_file, 'w') as f:
            json.dump(invalid_session_data, f)
        
        # Initialize with auto cleanup
        manager = SessionManager(
            storage_dir=str(temp_session_dir),
            auto_cleanup_on_init=True,
            max_age_days=7
        )
        
        # Both sessions should be cleaned up
        assert "old_session" not in manager.list_sessions()
        assert "invalid_session" not in manager.list_sessions()


class TestValidateSessionEnhanced:
    """Test enhanced session validation."""

    def test_validate_session_with_invalid_timestamps(
        self, session_manager, temp_session_dir
    ):
        """Test validation fails for invalid timestamps."""
        session_data = {
            "session_id": "test_session",
            "cdp_url": "ws://localhost:9222/test",
            "browser_type": "chromium",
            "created_at": "not-a-date",
            "last_accessed": datetime.now().isoformat(),
            "metadata": {}
        }
        
        session_file = temp_session_dir / "test_session.json"
        with open(session_file, 'w') as f:
            json.dump(session_data, f)
        
        is_valid = session_manager.validate_session("test_session")
        assert is_valid is False

    def test_validate_session_with_invalid_browser_type(
        self, session_manager, temp_session_dir
    ):
        """Test validation fails for invalid browser type."""
        session_data = {
            "session_id": "test_session",
            "cdp_url": "ws://localhost:9222/test",
            "browser_type": "safari",  # Not a valid Playwright browser
            "created_at": datetime.now().isoformat(),
            "last_accessed": datetime.now().isoformat(),
            "metadata": {}
        }
        
        session_file = temp_session_dir / "test_session.json"
        with open(session_file, 'w') as f:
            json.dump(session_data, f)
        
        is_valid = session_manager.validate_session("test_session")
        assert is_valid is False


class TestCleanupExpiredSessionsEnhanced:
    """Test enhanced cleanup of expired sessions."""

    def test_cleanup_expired_sessions_removes_corrupted(
        self, session_manager, temp_session_dir
    ):
        """Test that cleanup removes corrupted session files."""
        # Create corrupted session file
        corrupted_file = temp_session_dir / "corrupted_session.json"
        with open(corrupted_file, 'w') as f:
            f.write("{ invalid json }")
        
        # Cleanup should remove corrupted file
        deleted_count = session_manager.cleanup_expired_sessions(max_age_days=7)
        
        assert deleted_count == 1
        assert "corrupted_session" not in session_manager.list_sessions()

    def test_cleanup_expired_sessions_removes_invalid_dates(
        self, session_manager, temp_session_dir
    ):
        """Test that cleanup removes sessions with invalid dates."""
        session_data = {
            "session_id": "test_session",
            "cdp_url": "ws://localhost:9222/test",
            "browser_type": "chromium",
            "created_at": datetime.now().isoformat(),
            "last_accessed": "invalid-date",
            "metadata": {}
        }
        
        session_file = temp_session_dir / "test_session.json"
        with open(session_file, 'w') as f:
            json.dump(session_data, f)
        
        deleted_count = session_manager.cleanup_expired_sessions(max_age_days=7)
        assert deleted_count == 1


class TestHelperMethods:
    """Test helper methods."""

    def test_get_session_file_path(self, session_manager):
        """Test getting session file path."""
        path = session_manager._get_session_file_path("test_session")
        
        assert path.name == "test_session.json"
        assert path.parent == session_manager._storage_dir

    def test_get_session_file_path_sanitizes_name(self, session_manager):
        """Test that session name is sanitized for file path."""
        path = session_manager._get_session_file_path("test/../../../etc/passwd")
        
        # Should only contain alphanumeric characters
        assert path.name == "testetcpasswd.json"
        assert ".." not in str(path)

    def test_get_storage_dir(self, session_manager, temp_session_dir):
        """Test getting storage directory."""
        storage_dir = session_manager.get_storage_dir()
        assert storage_dir == temp_session_dir

    def test_repr(self, session_manager, temp_session_dir):
        """Test string representation."""
        repr_str = repr(session_manager)
        assert "SessionManager" in repr_str
        assert str(temp_session_dir) in repr_str
