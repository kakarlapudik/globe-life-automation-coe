"""
Session Manager for RAPTOR Python Playwright Framework.

This module provides browser session persistence and restoration capabilities,
allowing tests to reuse browser sessions across test runs to reduce startup time
and maintain state.
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import json
import logging
from playwright.async_api import Page, Browser, BrowserContext
from playwright.async_api import async_playwright

from raptor.core.exceptions import SessionException, RaptorException
from raptor.core.config_manager import ConfigManager

logger = logging.getLogger(__name__)


@dataclass
class SessionInfo:
    """
    Information about a saved browser session.
    
    Attributes:
        session_id: Unique identifier for the session
        cdp_url: Chrome DevTools Protocol URL for reconnection
        browser_type: Browser type (chromium, firefox, webkit)
        created_at: Session creation timestamp
        last_accessed: Last access timestamp
        metadata: Additional session metadata
    """
    session_id: str
    cdp_url: str
    browser_type: str
    created_at: str
    last_accessed: str
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert SessionInfo to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionInfo':
        """Create SessionInfo from dictionary."""
        return cls(**data)


class SessionManager:
    """
    Manages browser session persistence and restoration.
    
    This class handles:
    - Saving browser sessions with CDP URLs
    - Restoring previously saved sessions
    - Listing available sessions
    - Deleting old or invalid sessions
    - Session validation and cleanup
    
    Sessions are stored as JSON files in a configurable directory.
    
    Example:
        >>> session_manager = SessionManager()
        >>> await session_manager.save_session(page, "my_test_session")
        >>> # Later, in another test run...
        >>> page = await session_manager.restore_session("my_test_session")
    """

    def __init__(
        self,
        config: Optional[ConfigManager] = None,
        storage_dir: Optional[str] = None,
        auto_cleanup_on_init: bool = False,
        max_age_days: int = 7
    ):
        """
        Initialize the Session Manager.

        Args:
            config: Optional ConfigManager instance for configuration
            storage_dir: Optional directory path for session storage.
                        If not provided, uses default .raptor/sessions
            auto_cleanup_on_init: If True, automatically cleanup expired
                                 sessions on initialization (default: False)
            max_age_days: Maximum age for sessions when auto_cleanup_on_init
                         is enabled (default: 7 days)
        """
        self.config = config or ConfigManager()
        self._max_age_days = max_age_days
        
        # Determine storage directory
        if storage_dir:
            self._storage_dir = Path(storage_dir)
        else:
            # Default to .raptor/sessions in user's home directory
            home_dir = Path.home()
            self._storage_dir = home_dir / ".raptor" / "sessions"
        
        # Create storage directory if it doesn't exist
        self._storage_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"SessionManager initialized with storage: {self._storage_dir}")
        
        # Perform automatic cleanup if enabled
        if auto_cleanup_on_init:
            logger.info("Performing automatic session cleanup on initialization")
            expired_count = self.cleanup_expired_sessions(max_age_days)
            invalid_count = self.cleanup_invalid_sessions()
            logger.info(
                f"Automatic cleanup complete: "
                f"{expired_count} expired, {invalid_count} invalid sessions removed"
            )

    async def save_session(
        self,
        page: Page,
        session_name: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> SessionInfo:
        """
        Save a browser session for later restoration.

        This method captures the CDP (Chrome DevTools Protocol) endpoint URL
        and other session information to enable reconnection to the same
        browser instance later.

        Args:
            page: Playwright Page object to save
            session_name: Unique name for the session
            metadata: Optional additional metadata to store with session

        Returns:
            SessionInfo object containing session details

        Raises:
            SessionException: If session save fails
            
        Example:
            >>> session_info = await session_manager.save_session(
            ...     page,
            ...     "login_session",
            ...     metadata={"user": "test_user", "environment": "staging"}
            ... )
        """
        try:
            # Validate inputs
            if not session_name or not session_name.strip():
                raise SessionException(
                    "save_session",
                    session_id=session_name,
                    session_info={"error": "Session name cannot be empty"}
                )

            # Get browser context and browser
            context = page.context
            browser = context.browser
            
            if not browser:
                raise SessionException(
                    "save_session",
                    session_id=session_name,
                    session_info={"error": "Page is not attached to a browser"}
                )

            # Get CDP endpoint URL
            # Note: CDP URL is available through browser.ws_endpoint() for Chromium
            # For Firefox and WebKit, we'll store browser type and handle differently
            cdp_url = ""
            browser_type = "chromium"  # Default
            
            try:
                # Try to get WebSocket endpoint (works for Chromium)
                cdp_url = browser.ws_endpoint()
                browser_type = "chromium"
            except Exception as e:
                logger.warning(f"Could not get CDP URL: {e}. Session may not be restorable.")
                # For non-Chromium browsers, we can't get CDP URL
                # Store browser type for informational purposes
                cdp_url = ""

            # Create session info
            now = datetime.now().isoformat()
            session_info = SessionInfo(
                session_id=session_name,
                cdp_url=cdp_url,
                browser_type=browser_type,
                created_at=now,
                last_accessed=now,
                metadata=metadata or {}
            )

            # Add page URL and title to metadata
            try:
                session_info.metadata["page_url"] = page.url
                session_info.metadata["page_title"] = await page.title()
            except Exception as e:
                logger.warning(f"Could not capture page info: {e}")

            # Save session to file
            session_file = self._get_session_file_path(session_name)
            with open(session_file, 'w') as f:
                json.dump(session_info.to_dict(), f, indent=2)

            logger.info(
                f"Session '{session_name}' saved successfully. "
                f"CDP URL: {cdp_url[:50]}..." if cdp_url else "No CDP URL available"
            )
            
            return session_info

        except SessionException:
            raise
        except Exception as e:
            error_context = {
                "session_name": session_name,
                "has_page": page is not None,
                "metadata": metadata
            }
            logger.error(f"Failed to save session: {str(e)}", extra=error_context)
            raise SessionException(
                "save_session",
                session_id=session_name,
                session_info=error_context
            ) from e

    async def restore_session(self, session_name: str) -> Page:
        """
        Restore a previously saved browser session.

        Reconnects to a saved browser session using the stored CDP URL
        and returns a Page object that can be used for test automation.

        Args:
            session_name: Name of the session to restore

        Returns:
            Page object connected to the restored session

        Raises:
            SessionException: If session restore fails or session not found
            
        Example:
            >>> page = await session_manager.restore_session("login_session")
            >>> await page.goto("https://example.com/dashboard")
        """
        try:
            # Validate session before attempting restore
            if not self.validate_session(session_name):
                raise SessionException(
                    "restore_session",
                    session_id=session_name,
                    session_info={
                        "error": "Session validation failed. "
                                "Session may be corrupted or invalid."
                    }
                )
            
            # Load session info
            session_info = self.get_session_info(session_name)
            
            if not session_info:
                raise SessionException(
                    "restore_session",
                    session_id=session_name,
                    session_info={"error": "Session not found"}
                )

            # Validate session has CDP URL (redundant check for safety)
            if not session_info.cdp_url:
                raise SessionException(
                    "restore_session",
                    session_id=session_name,
                    session_info={
                        "error": "Session does not have CDP URL. "
                                "Only Chromium sessions can be restored."
                    }
                )

            # Connect to browser using CDP URL
            logger.info(f"Restoring session '{session_name}' from CDP URL")
            
            playwright = await async_playwright().start()
            
            try:
                browser = await playwright.chromium.connect_over_cdp(session_info.cdp_url)
            except Exception as e:
                # Browser may have crashed or CDP endpoint is no longer valid
                logger.error(
                    f"Failed to connect to CDP endpoint for session '{session_name}': {e}"
                )
                raise SessionException(
                    "restore_session",
                    session_id=session_name,
                    session_info={
                        "error": "Browser connection failed. "
                                "Browser may have crashed or been closed.",
                        "cdp_url": session_info.cdp_url
                    }
                ) from e
            
            # Get the default context (or first available context)
            contexts = browser.contexts
            if not contexts:
                raise SessionException(
                    "restore_session",
                    session_id=session_name,
                    session_info={"error": "No browser contexts available in session"}
                )
            
            context = contexts[0]
            
            # Get the first page from the context
            pages = context.pages
            if not pages:
                # Create a new page if none exist
                logger.debug("No pages in context, creating new page")
                page = await context.new_page()
            else:
                page = pages[0]

            # Update last accessed time
            session_info.last_accessed = datetime.now().isoformat()
            self._save_session_info(session_name, session_info)

            logger.info(
                f"Session '{session_name}' restored successfully. "
                f"Current URL: {page.url}"
            )
            
            return page

        except SessionException:
            raise
        except Exception as e:
            error_context = {
                "session_name": session_name,
                "error_type": type(e).__name__
            }
            logger.error(f"Failed to restore session: {str(e)}", extra=error_context)
            raise SessionException(
                "restore_session",
                session_id=session_name,
                session_info=error_context
            ) from e

    def list_sessions(self) -> List[str]:
        """
        List all available saved sessions.

        Returns:
            List of session names

        Example:
            >>> sessions = session_manager.list_sessions()
            >>> print(f"Available sessions: {sessions}")
            Available sessions: ['login_session', 'checkout_session']
        """
        try:
            session_files = self._storage_dir.glob("*.json")
            sessions = [f.stem for f in session_files]
            
            logger.debug(f"Found {len(sessions)} saved sessions")
            return sorted(sessions)
            
        except Exception as e:
            logger.error(f"Failed to list sessions: {str(e)}")
            return []

    def delete_session(self, session_name: str) -> bool:
        """
        Delete a saved session.

        Removes the session file from storage. This does not close
        the browser if it's still running.

        Args:
            session_name: Name of the session to delete

        Returns:
            True if session was deleted, False if session not found

        Raises:
            SessionException: If deletion fails
            
        Example:
            >>> session_manager.delete_session("old_session")
            True
        """
        try:
            session_file = self._get_session_file_path(session_name)
            
            if not session_file.exists():
                logger.warning(f"Session '{session_name}' not found")
                return False

            session_file.unlink()
            logger.info(f"Session '{session_name}' deleted successfully")
            return True

        except Exception as e:
            error_context = {"session_name": session_name}
            logger.error(f"Failed to delete session: {str(e)}", extra=error_context)
            raise SessionException(
                "delete_session",
                session_id=session_name,
                session_info=error_context
            ) from e

    def get_session_info(self, session_name: str) -> Optional[SessionInfo]:
        """
        Get information about a saved session.

        Args:
            session_name: Name of the session

        Returns:
            SessionInfo object or None if session not found

        Example:
            >>> info = session_manager.get_session_info("login_session")
            >>> if info:
            ...     print(f"Session created: {info.created_at}")
            ...     print(f"Last accessed: {info.last_accessed}")
        """
        try:
            session_file = self._get_session_file_path(session_name)
            
            if not session_file.exists():
                logger.debug(f"Session '{session_name}' not found")
                return None

            with open(session_file, 'r') as f:
                data = json.load(f)
                return SessionInfo.from_dict(data)

        except Exception as e:
            logger.error(f"Failed to load session info: {str(e)}")
            return None

    def cleanup_expired_sessions(self, max_age_days: int = 7) -> int:
        """
        Clean up sessions older than the specified age.

        Args:
            max_age_days: Maximum age of sessions in days (default: 7)

        Returns:
            Number of sessions deleted

        Example:
            >>> deleted = session_manager.cleanup_expired_sessions(max_age_days=3)
            >>> print(f"Deleted {deleted} expired sessions")
        """
        try:
            deleted_count = 0
            now = datetime.now()
            
            for session_name in self.list_sessions():
                session_info = self.get_session_info(session_name)
                
                if not session_info:
                    # Delete corrupted session files
                    logger.warning(
                        f"Session '{session_name}' has invalid data, deleting"
                    )
                    if self.delete_session(session_name):
                        deleted_count += 1
                    continue

                # Parse last accessed time
                try:
                    last_accessed = datetime.fromisoformat(session_info.last_accessed)
                    age_days = (now - last_accessed).days
                    
                    if age_days > max_age_days:
                        logger.info(
                            f"Deleting expired session '{session_name}' "
                            f"(age: {age_days} days)"
                        )
                        if self.delete_session(session_name):
                            deleted_count += 1
                            
                except Exception as e:
                    logger.warning(
                        f"Could not parse date for session '{session_name}': {e}. "
                        f"Deleting invalid session."
                    )
                    if self.delete_session(session_name):
                        deleted_count += 1

            logger.info(f"Cleanup complete. Deleted {deleted_count} expired sessions")
            return deleted_count

        except Exception as e:
            logger.error(f"Failed to cleanup expired sessions: {str(e)}")
            return 0

    def validate_session(self, session_name: str) -> bool:
        """
        Validate that a session exists and has required information.

        Args:
            session_name: Name of the session to validate

        Returns:
            True if session is valid, False otherwise

        Example:
            >>> if session_manager.validate_session("login_session"):
            ...     page = await session_manager.restore_session("login_session")
        """
        try:
            session_info = self.get_session_info(session_name)
            
            if not session_info:
                logger.debug(f"Session '{session_name}' not found")
                return False

            # Check required fields
            if not session_info.session_id:
                logger.warning(
                    f"Session '{session_name}' is missing session_id"
                )
                return False
                
            if not session_info.cdp_url:
                logger.warning(
                    f"Session '{session_name}' is missing CDP URL. "
                    f"Only Chromium sessions can be restored."
                )
                return False

            # Validate timestamps
            try:
                datetime.fromisoformat(session_info.created_at)
                datetime.fromisoformat(session_info.last_accessed)
            except (ValueError, TypeError) as e:
                logger.warning(
                    f"Session '{session_name}' has invalid timestamps: {e}"
                )
                return False

            # Validate browser type
            valid_browser_types = ["chromium", "firefox", "webkit"]
            if session_info.browser_type not in valid_browser_types:
                logger.warning(
                    f"Session '{session_name}' has invalid browser type: "
                    f"{session_info.browser_type}"
                )
                return False

            return True

        except Exception as e:
            logger.error(f"Failed to validate session: {str(e)}")
            return False

    def _get_session_file_path(self, session_name: str) -> Path:
        """
        Get the file path for a session.

        Args:
            session_name: Name of the session

        Returns:
            Path object for the session file
        """
        # Sanitize session name to prevent path traversal
        safe_name = "".join(c for c in session_name if c.isalnum() or c in ('-', '_'))
        return self._storage_dir / f"{safe_name}.json"

    def _save_session_info(self, session_name: str, session_info: SessionInfo) -> None:
        """
        Save session info to file.

        Args:
            session_name: Name of the session
            session_info: SessionInfo object to save
        """
        session_file = self._get_session_file_path(session_name)
        with open(session_file, 'w') as f:
            json.dump(session_info.to_dict(), f, indent=2)

    def cleanup_invalid_sessions(self) -> int:
        """
        Clean up sessions that fail validation.

        This method removes session files that are corrupted or have
        invalid data, helping maintain a clean session storage.

        Returns:
            Number of invalid sessions deleted

        Example:
            >>> deleted = session_manager.cleanup_invalid_sessions()
            >>> print(f"Deleted {deleted} invalid sessions")
        """
        try:
            deleted_count = 0
            
            for session_name in self.list_sessions():
                if not self.validate_session(session_name):
                    logger.info(
                        f"Deleting invalid session '{session_name}'"
                    )
                    if self.delete_session(session_name):
                        deleted_count += 1

            logger.info(
                f"Invalid session cleanup complete. "
                f"Deleted {deleted_count} invalid sessions"
            )
            return deleted_count

        except Exception as e:
            logger.error(f"Failed to cleanup invalid sessions: {str(e)}")
            return 0

    def cleanup_all_sessions(self) -> int:
        """
        Delete all saved sessions.

        This is useful for test cleanup or resetting the session storage.

        Returns:
            Number of sessions deleted

        Example:
            >>> deleted = session_manager.cleanup_all_sessions()
            >>> print(f"Deleted all {deleted} sessions")
        """
        try:
            deleted_count = 0
            
            for session_name in self.list_sessions():
                if self.delete_session(session_name):
                    deleted_count += 1

            logger.info(f"All sessions deleted. Total: {deleted_count}")
            return deleted_count

        except Exception as e:
            logger.error(f"Failed to cleanup all sessions: {str(e)}")
            return 0

    def get_session_count(self) -> int:
        """
        Get the total number of saved sessions.

        Returns:
            Number of sessions

        Example:
            >>> count = session_manager.get_session_count()
            >>> print(f"Total sessions: {count}")
        """
        return len(self.list_sessions())

    def get_storage_size(self) -> int:
        """
        Get the total size of session storage in bytes.

        Returns:
            Total size in bytes

        Example:
            >>> size_bytes = session_manager.get_storage_size()
            >>> size_mb = size_bytes / (1024 * 1024)
            >>> print(f"Storage size: {size_mb:.2f} MB")
        """
        try:
            total_size = 0
            for session_file in self._storage_dir.glob("*.json"):
                total_size += session_file.stat().st_size
            return total_size
        except Exception as e:
            logger.error(f"Failed to calculate storage size: {str(e)}")
            return 0

    def get_storage_dir(self) -> Path:
        """
        Get the session storage directory path.

        Returns:
            Path object for storage directory
        """
        return self._storage_dir

    def __repr__(self) -> str:
        """String representation of SessionManager."""
        return f"SessionManager(storage_dir='{self._storage_dir}')"
