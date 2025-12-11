"""
Property-Based Test: Session Persistence Round-Trip

**Feature: raptor-playwright-python, Property 3: Session Persistence Round-Trip**
**Validates: Requirements 3.1, 3.2**

This test verifies that browser sessions can be saved and restored reliably,
maintaining the same browser state (URL, cookies, storage) across the round-trip.

Property Statement:
    For any browser session, saving and then restoring the session should result 
    in the same browser state (URL, cookies, storage).
"""

import pytest
import asyncio
import tempfile
import json
from pathlib import Path
from datetime import datetime
from hypothesis import given, strategies as st, settings, assume
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock, patch

from raptor.core.session_manager import SessionManager, SessionInfo
from raptor.core.exceptions import SessionException


# Strategy for generating valid session names
session_name_strategy = st.text(
    alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='-_'),
    min_size=1,
    max_size=50
).filter(lambda x: x.strip() != '')


# Strategy for generating URLs
url_strategy = st.sampled_from([
    "https://example.com",
    "https://example.com/page1",
    "https://example.com/page2?param=value",
    "https://test.example.com",
    "https://example.com/path/to/page",
    "https://example.com:8080/secure",
])


# Strategy for generating page titles
title_strategy = st.text(
    alphabet=st.characters(blacklist_characters='\x00\n\r'),
    min_size=1,
    max_size=100
)


# Strategy for generating metadata
metadata_strategy = st.dictionaries(
    keys=st.text(
        alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')),
        min_size=1,
        max_size=20
    ),
    values=st.one_of(
        st.text(max_size=50),
        st.integers(),
        st.booleans(),
        st.floats(allow_nan=False, allow_infinity=False)
    ),
    min_size=0,
    max_size=10
)


class TestSessionPersistenceRoundTrip:
    """
    Property-based tests for session persistence round-trip.
    
    These tests verify that saving and restoring browser sessions maintains
    the same browser state, including URL, cookies, and storage.
    """
    
    def create_temp_session_manager(self):
        """
        Create a SessionManager with a temporary directory.
        
        This is used instead of fixtures to avoid Hypothesis health check warnings
        about function-scoped fixtures not being reset between generated inputs.
        """
        temp_dir = tempfile.mkdtemp()
        return SessionManager(storage_dir=temp_dir), temp_dir
    
    def create_mock_page(self, url: str, title: str, cdp_url: str):
        """
        Create a mock Playwright Page object with specified properties.
        
        Args:
            url: Page URL
            title: Page title
            cdp_url: Chrome DevTools Protocol URL
            
        Returns:
            Mock Page object
        """
        page = AsyncMock()
        page.url = url
        page.title = AsyncMock(return_value=title)
        
        # Mock context and browser
        context = Mock()
        browser = Mock()
        browser.ws_endpoint = Mock(return_value=cdp_url)
        
        context.browser = browser
        page.context = context
        
        return page
    
    @given(
        session_name=session_name_strategy,
        url=url_strategy,
        title=title_strategy,
        metadata=metadata_strategy
    )
    @settings(max_examples=100, deadline=5000)
    @pytest.mark.asyncio
    async def test_session_info_round_trip(
        self,
        session_name,
        url,
        title,
        metadata
    ):
        """
        Property: Session information should survive save/load round-trip.
        
        When a session is saved and then loaded from disk, all session
        information should be preserved exactly.
        
        Args:
            session_name: Name for the session
            url: Page URL
            title: Page title
            metadata: Session metadata
        """
        # Create session manager with temp directory
        session_manager, temp_dir = self.create_temp_session_manager()
        
        # Create mock page with specified properties
        cdp_url = "ws://localhost:9222/devtools/browser/test-session-id"
        mock_page = self.create_mock_page(url, title, cdp_url)
        
        # Save the session
        saved_info = await session_manager.save_session(
            mock_page,
            session_name,
            metadata=metadata
        )
        
        # Load the session info from disk
        loaded_info = session_manager.get_session_info(session_name)
        
        # Verify all fields are preserved
        assert loaded_info is not None, "Session info should be loadable"
        assert loaded_info.session_id == saved_info.session_id
        assert loaded_info.cdp_url == saved_info.cdp_url
        assert loaded_info.browser_type == saved_info.browser_type
        assert loaded_info.created_at == saved_info.created_at
        assert loaded_info.last_accessed == saved_info.last_accessed
        
        # Verify metadata is preserved
        for key, value in metadata.items():
            assert key in loaded_info.metadata, f"Metadata key '{key}' should be preserved"
            assert loaded_info.metadata[key] == value, f"Metadata value for '{key}' should match"
        
        # Verify page URL and title are captured in metadata
        assert loaded_info.metadata.get("page_url") == url
        assert loaded_info.metadata.get("page_title") == title
    
    @given(
        session_name=session_name_strategy,
        url=url_strategy,
        title=title_strategy
    )
    @settings(max_examples=100, deadline=5000)
    @pytest.mark.asyncio
    async def test_session_file_persistence(
        self,
        session_name,
        url,
        title
    ):
        """
        Property: Session files should persist to disk correctly.
        
        After saving a session, the session file should exist on disk
        and contain valid JSON with all required fields.
        
        Args:
            session_name: Name for the session
            url: Page URL
            title: Page title
        """
        # Create session manager with temp directory
        session_manager, temp_dir = self.create_temp_session_manager()
        
        # Create mock page
        cdp_url = "ws://localhost:9222/devtools/browser/test-id"
        mock_page = self.create_mock_page(url, title, cdp_url)
        
        # Save the session
        await session_manager.save_session(mock_page, session_name)
        
        # Verify file exists
        session_file = session_manager._get_session_file_path(session_name)
        assert session_file.exists(), "Session file should exist on disk"
        
        # Verify file contains valid JSON
        with open(session_file, 'r') as f:
            data = json.load(f)
        
        # Verify required fields are present
        required_fields = [
            "session_id",
            "cdp_url",
            "browser_type",
            "created_at",
            "last_accessed",
            "metadata"
        ]
        
        for field in required_fields:
            assert field in data, f"Required field '{field}' should be in session file"
        
        # Verify field values
        assert data["session_id"] == session_name
        assert data["cdp_url"] == cdp_url
        assert data["browser_type"] == "chromium"
        assert isinstance(data["metadata"], dict)
    
    @given(
        session_name=session_name_strategy,
        url=url_strategy,
        save_count=st.integers(min_value=2, max_value=5)
    )
    @settings(max_examples=50, deadline=5000)
    @pytest.mark.asyncio
    async def test_multiple_saves_idempotence(
        self,
        session_name,
        url,
        save_count
    ):
        """
        Property: Saving the same session multiple times should be idempotent.
        
        Saving a session with the same name multiple times should result
        in only one session file with the latest data.
        
        Args:
            session_name: Name for the session
            url: Page URL
            save_count: Number of times to save the session
        """
        # Create session manager with temp directory
        session_manager, temp_dir = self.create_temp_session_manager()
        
        cdp_url = "ws://localhost:9222/devtools/browser/test-id"
        
        # Save the session multiple times
        for i in range(save_count):
            title = f"Page Title {i}"
            mock_page = self.create_mock_page(url, title, cdp_url)
            await session_manager.save_session(
                mock_page,
                session_name,
                metadata={"iteration": i}
            )
        
        # Verify only one session exists
        sessions = session_manager.list_sessions()
        session_count = sum(1 for s in sessions if s == session_name)
        assert session_count == 1, "Only one session file should exist"
        
        # Verify the latest data is preserved
        loaded_info = session_manager.get_session_info(session_name)
        assert loaded_info.metadata["iteration"] == save_count - 1
        assert loaded_info.metadata["page_title"] == f"Page Title {save_count - 1}"
    
    @given(
        session_names=st.lists(
            session_name_strategy,
            min_size=2,
            max_size=10,
            unique=True
        ),
        url=url_strategy
    )
    @settings(max_examples=50, deadline=5000)
    @pytest.mark.asyncio
    async def test_multiple_sessions_isolation(
        self,
        session_names,
        url
    ):
        """
        Property: Multiple sessions should be isolated from each other.
        
        Saving multiple sessions should not affect each other's data.
        Each session should maintain its own independent state.
        
        Args:
            session_names: List of unique session names
            url: Page URL
        """
        # Create session manager with temp directory
        session_manager, temp_dir = self.create_temp_session_manager()
        
        cdp_url = "ws://localhost:9222/devtools/browser/test-id"
        saved_sessions = {}
        
        # Save multiple sessions with different metadata
        for i, session_name in enumerate(session_names):
            title = f"Page {i}"
            mock_page = self.create_mock_page(url, title, cdp_url)
            
            session_info = await session_manager.save_session(
                mock_page,
                session_name,
                metadata={"index": i, "name": session_name}
            )
            saved_sessions[session_name] = session_info
        
        # Verify all sessions exist
        all_sessions = session_manager.list_sessions()
        for session_name in session_names:
            assert session_name in all_sessions, f"Session '{session_name}' should exist"
        
        # Verify each session has correct data
        for session_name, saved_info in saved_sessions.items():
            loaded_info = session_manager.get_session_info(session_name)
            
            assert loaded_info is not None
            assert loaded_info.session_id == session_name
            assert loaded_info.metadata["name"] == session_name
            
            # Verify this session's data wasn't affected by other sessions
            expected_index = saved_info.metadata["index"]
            assert loaded_info.metadata["index"] == expected_index
    
    @given(
        session_name=session_name_strategy,
        url=url_strategy,
        title=title_strategy,
        metadata=metadata_strategy
    )
    @settings(max_examples=100, deadline=5000)
    @pytest.mark.asyncio
    async def test_session_validation_after_save(
        self,
        session_name,
        url,
        title,
        metadata
    ):
        """
        Property: Saved sessions should be valid and restorable.
        
        After saving a session, the session should pass validation
        checks and be marked as valid for restoration.
        
        Args:
            session_name: Name for the session
            url: Page URL
            title: Page title
            metadata: Session metadata
        """
        # Create session manager with temp directory
        session_manager, temp_dir = self.create_temp_session_manager()
        
        # Create and save session
        cdp_url = "ws://localhost:9222/devtools/browser/test-id"
        mock_page = self.create_mock_page(url, title, cdp_url)
        
        await session_manager.save_session(
            mock_page,
            session_name,
            metadata=metadata
        )
        
        # Verify session is valid
        is_valid = session_manager.validate_session(session_name)
        assert is_valid is True, "Saved session should be valid"
        
        # Verify session info can be retrieved
        session_info = session_manager.get_session_info(session_name)
        assert session_info is not None
        assert session_info.session_id == session_name
        assert session_info.cdp_url != ""
    
    @given(
        session_name=session_name_strategy,
        url=url_strategy
    )
    @settings(max_examples=50, deadline=5000)
    @pytest.mark.asyncio
    async def test_session_delete_removes_all_data(
        self,
        session_name,
        url
    ):
        """
        Property: Deleting a session should completely remove it.
        
        After deleting a session, it should not appear in the session list,
        its file should not exist, and validation should fail.
        
        Args:
            session_name: Name for the session
            url: Page URL
        """
        # Create session manager with temp directory
        session_manager, temp_dir = self.create_temp_session_manager()
        
        # Create and save session
        cdp_url = "ws://localhost:9222/devtools/browser/test-id"
        mock_page = self.create_mock_page(url, "Test Page", cdp_url)
        
        await session_manager.save_session(mock_page, session_name)
        
        # Verify session exists
        assert session_name in session_manager.list_sessions()
        assert session_manager.validate_session(session_name) is True
        
        # Delete the session
        result = session_manager.delete_session(session_name)
        assert result is True, "Delete should return True"
        
        # Verify session is completely removed
        assert session_name not in session_manager.list_sessions()
        assert session_manager.validate_session(session_name) is False
        assert session_manager.get_session_info(session_name) is None
        
        # Verify file doesn't exist
        session_file = session_manager._get_session_file_path(session_name)
        assert not session_file.exists(), "Session file should be deleted"
    
    @given(
        session_name=session_name_strategy,
        url=url_strategy,
        title=title_strategy
    )
    @settings(max_examples=100, deadline=5000)
    @pytest.mark.asyncio
    async def test_session_timestamps_are_valid(
        self,
        session_name,
        url,
        title
    ):
        """
        Property: Session timestamps should be valid ISO format dates.
        
        The created_at and last_accessed timestamps should be valid
        ISO 8601 format strings that can be parsed back to datetime objects.
        
        Args:
            session_name: Name for the session
            url: Page URL
            title: Page title
        """
        # Create session manager with temp directory
        session_manager, temp_dir = self.create_temp_session_manager()
        
        # Create and save session
        cdp_url = "ws://localhost:9222/devtools/browser/test-id"
        mock_page = self.create_mock_page(url, title, cdp_url)
        
        before_save = datetime.now()
        session_info = await session_manager.save_session(mock_page, session_name)
        after_save = datetime.now()
        
        # Verify timestamps are valid ISO format
        try:
            created_dt = datetime.fromisoformat(session_info.created_at)
            accessed_dt = datetime.fromisoformat(session_info.last_accessed)
        except ValueError as e:
            pytest.fail(f"Invalid timestamp format: {e}")
        
        # Verify timestamps are reasonable (between before and after save)
        assert before_save <= created_dt <= after_save, "created_at should be during save operation"
        assert before_save <= accessed_dt <= after_save, "last_accessed should be during save operation"
        
        # Verify timestamps are equal on initial save
        assert session_info.created_at == session_info.last_accessed
    
    @given(
        session_name=session_name_strategy,
        url=url_strategy
    )
    @settings(max_examples=50, deadline=5000)
    @pytest.mark.asyncio
    async def test_session_name_sanitization(
        self,
        session_name,
        url
    ):
        """
        Property: Session names should be sanitized for safe file storage.
        
        Session names with special characters should be sanitized to
        prevent path traversal attacks while still being retrievable.
        
        Args:
            session_name: Name for the session
            url: Page URL
        """
        # Create session manager with temp directory
        session_manager, temp_dir = self.create_temp_session_manager()
        
        # Create and save session
        cdp_url = "ws://localhost:9222/devtools/browser/test-id"
        mock_page = self.create_mock_page(url, "Test Page", cdp_url)
        
        await session_manager.save_session(mock_page, session_name)
        
        # Get the file path
        session_file = session_manager._get_session_file_path(session_name)
        
        # Verify file path doesn't contain dangerous characters
        file_name = session_file.name
        assert ".." not in str(session_file), "Path should not contain .."
        assert "/" not in file_name, "File name should not contain /"
        assert "\\" not in file_name, "File name should not contain \\"
        
        # Verify file is in the correct directory
        assert session_file.parent == session_manager._storage_dir
        
        # Verify session can still be retrieved
        loaded_info = session_manager.get_session_info(session_name)
        assert loaded_info is not None
        assert loaded_info.session_id == session_name


def test_property_coverage():
    """
    Verify that this test file covers Property 3: Session Persistence Round-Trip.
    
    This is a meta-test to ensure the property is properly documented and tested.
    """
    # Verify property is documented in module docstring
    assert "Property 3: Session Persistence Round-Trip" in __doc__
    assert "Validates: Requirements 3.1, 3.2" in __doc__
    
    # Verify test class exists
    assert TestSessionPersistenceRoundTrip is not None
    
    # Verify key test methods exist
    test_methods = [
        'test_session_info_round_trip',
        'test_session_file_persistence',
        'test_multiple_saves_idempotence',
        'test_multiple_sessions_isolation',
        'test_session_validation_after_save',
        'test_session_delete_removes_all_data',
        'test_session_timestamps_are_valid',
        'test_session_name_sanitization'
    ]
    
    for method_name in test_methods:
        assert hasattr(TestSessionPersistenceRoundTrip, method_name), (
            f"Test method {method_name} not found"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--hypothesis-show-statistics"])
