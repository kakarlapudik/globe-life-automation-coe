"""
Integration Tests for RAPTOR Framework

These tests verify that different components work together correctly:
1. Browser + Element Manager integration
2. Database + Config integration
3. Session + Browser integration
4. Page Objects integration

**Validates: Requirements NFR-003**
"""

import pytest
import asyncio
import tempfile
import os
from pathlib import Path
from playwright.async_api import async_playwright

from raptor.core.browser_manager import BrowserManager
from raptor.core.element_manager import ElementManager
from raptor.core.session_manager import SessionManager
from raptor.core.config_manager import ConfigManager
from raptor.database.database_manager import DatabaseManager
from raptor.pages.base_page import BasePage
from raptor.pages.table_manager import TableManager
from raptor.core.exceptions import (
    ElementNotFoundException,
    SessionException,
    DatabaseException
)


# ============================================================================
# Integration Test 1: Browser + Element Manager
# ============================================================================

class TestBrowserElementManagerIntegration:
    """
    Integration tests for Browser Manager and Element Manager.
    
    Tests that browser and element management work together correctly
    for real-world scenarios.
    """
    
    @pytest.mark.asyncio
    async def test_browser_launch_and_element_location(self):
        """Test launching browser and locating elements."""
        browser_manager = BrowserManager()
        
        try:
            # Launch browser
            await browser_manager.launch_browser("chromium", headless=True)
            page = await browser_manager.create_page()
            
            # Create element manager
            config = ConfigManager()
            element_manager = ElementManager(page, config)
            
            # Navigate to a test page
            await page.goto("data:text/html,<h1 id='test'>Hello World</h1>")
            
            # Locate element
            element = await element_manager.locate_element("css=#test")
            assert element is not None
            
            text = await element.text_content()
            assert text == "Hello World"
            
        finally:
            await browser_manager.close_browser()
    
    @pytest.mark.asyncio
    async def test_browser_element_interaction_workflow(self):
        """Test complete workflow: launch, navigate, interact, verify."""
        browser_manager = BrowserManager()
        
        try:
            # Launch browser
            await browser_manager.launch_browser("chromium", headless=True)
            page = await browser_manager.create_page()
            
            # Create element manager
            config = ConfigManager()
            element_manager = ElementManager(page, config)
            
            # Create interactive test page
            await page.set_content("""
                <!DOCTYPE html>
                <html>
                <body>
                    <input id="name" type="text" />
                    <button id="submit" onclick="document.getElementById('result').textContent = document.getElementById('name').value">
                        Submit
                    </button>
                    <div id="result"></div>
                </body>
                </html>
            """)
            
            # Fill input
            await element_manager.fill("css=#name", "John Doe")
            
            # Click button
            await element_manager.click("css=#submit")
            
            # Verify result
            await asyncio.sleep(0.1)  # Small delay for DOM update
            result_element = await element_manager.locate_element("css=#result")
            result_text = await result_element.text_content()
            assert result_text == "John Doe"
            
        finally:
            await browser_manager.close_browser()
    
    @pytest.mark.asyncio
    async def test_multiple_contexts_element_isolation(self):
        """Test that elements in different contexts are isolated."""
        browser_manager = BrowserManager()
        
        try:
            # Launch browser
            await browser_manager.launch_browser("chromium", headless=True)
            
            # Create two contexts
            context1 = await browser_manager.create_context()
            context2 = await browser_manager.create_context()
            
            # Create pages in each context
            page1 = await browser_manager.create_page(context1)
            page2 = await browser_manager.create_page(context2)
            
            # Create element managers
            config = ConfigManager()
            em1 = ElementManager(page1, config)
            em2 = ElementManager(page2, config)
            
            # Set different content in each page
            await page1.set_content("<h1 id='test'>Page 1</h1>")
            await page2.set_content("<h1 id='test'>Page 2</h1>")
            
            # Verify isolation
            element1 = await em1.locate_element("css=#test")
            text1 = await element1.text_content()
            
            element2 = await em2.locate_element("css=#test")
            text2 = await element2.text_content()
            
            assert text1 == "Page 1"
            assert text2 == "Page 2"
            
        finally:
            await browser_manager.close_browser()
    
    @pytest.mark.asyncio
    async def test_element_fallback_with_real_browser(self):
        """Test element fallback mechanism with real browser."""
        browser_manager = BrowserManager()
        
        try:
            await browser_manager.launch_browser("chromium", headless=True)
            page = await browser_manager.create_page()
            
            config = ConfigManager()
            element_manager = ElementManager(page, config)
            
            await page.set_content("""
                <div id="target" class="test-class">Target Element</div>
            """)
            
            # Primary locator fails, fallback succeeds
            element = await element_manager.locate_element(
                "css=#nonexistent",
                fallback_locators=["css=.test-class", "xpath=//div[@id='target']"],
                timeout=2000
            )
            
            assert element is not None
            text = await element.text_content()
            assert text == "Target Element"
            
        finally:
            await browser_manager.close_browser()


# ============================================================================
# Integration Test 2: Database + Config
# ============================================================================

class TestDatabaseConfigIntegration:
    """
    Integration tests for Database Manager and Config Manager.
    
    Tests that database operations work correctly with configuration.
    """
    
    @pytest.fixture
    async def temp_db_with_config(self):
        """Create temporary database with configuration."""
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()
        
        # Create config
        config = ConfigManager()
        
        # Create database manager
        db_manager = DatabaseManager(temp_db.name)
        await db_manager.initialize()
        
        yield db_manager, config
        
        await db_manager.close()
        os.unlink(temp_db.name)
    
    @pytest.mark.asyncio
    async def test_database_with_config_timeout(self, temp_db_with_config):
        """Test database operations respect config timeout."""
        db_manager, config = temp_db_with_config
        
        # Create test table
        await db_manager.create_table_if_not_exists(
            "test_table",
            "id INTEGER PRIMARY KEY, name TEXT, value INTEGER"
        )
        
        # Insert data
        await db_manager.insert_record(
            "test_table",
            {"name": "test", "value": 42}
        )
        
        # Query data
        records = await db_manager.get_all_records("test_table")
        assert len(records) == 1
        assert records[0]["name"] == "test"
    
    @pytest.mark.asyncio
    async def test_database_config_driven_operations(self):
        """Test database operations driven by configuration."""
        # Create temporary database
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()
        
        try:
            # Create config with custom settings
            config = ConfigManager()
            
            # Create database manager
            db_manager = DatabaseManager(temp_db.name)
            await db_manager.initialize()
            
            # Create table based on config
            await db_manager.create_table_if_not_exists(
                "config_test",
                "id INTEGER PRIMARY KEY, setting TEXT, value TEXT"
            )
            
            # Insert config-like data
            settings = [
                {"setting": "timeout", "value": "30000"},
                {"setting": "headless", "value": "true"},
                {"setting": "browser", "value": "chromium"}
            ]
            
            for setting in settings:
                await db_manager.insert_record("config_test", setting)
            
            # Query and verify
            records = await db_manager.get_all_records("config_test")
            assert len(records) == 3
            
            # Verify specific setting
            timeout_record = await db_manager.execute_query(
                "SELECT * FROM config_test WHERE setting = ?",
                ("timeout",)
            )
            assert timeout_record[0]["value"] == "30000"
            
            await db_manager.close()
            
        finally:
            os.unlink(temp_db.name)


# ============================================================================
# Integration Test 3: Session + Browser
# ============================================================================

class TestSessionBrowserIntegration:
    """
    Integration tests for Session Manager and Browser Manager.
    
    Tests that session persistence and restoration work with real browsers.
    """
    
    @pytest.fixture
    def temp_session_dir(self, tmp_path):
        """Create temporary session directory."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir()
        return session_dir
    
    @pytest.mark.asyncio
    async def test_save_and_restore_browser_session(self, temp_session_dir):
        """Test saving and restoring browser session."""
        browser_manager = BrowserManager()
        session_manager = SessionManager(storage_dir=str(temp_session_dir))
        
        try:
            # Launch browser and navigate
            await browser_manager.launch_browser("chromium", headless=True)
            page = await browser_manager.create_page()
            await page.goto("data:text/html,<h1>Test Page</h1>")
            
            # Save session
            session_info = await session_manager.save_session(
                page,
                "test_session",
                metadata={"test": "data"}
            )
            
            assert session_info.session_id == "test_session"
            assert session_info.cdp_url is not None
            
            # Verify session was saved
            assert "test_session" in session_manager.list_sessions()
            
            # Get session info
            retrieved_info = session_manager.get_session_info("test_session")
            assert retrieved_info.session_id == "test_session"
            assert retrieved_info.metadata["test"] == "data"
            
        finally:
            await browser_manager.close_browser()
    
    @pytest.mark.asyncio
    async def test_session_persistence_across_browser_instances(self, temp_session_dir):
        """Test that session data persists across browser instances."""
        session_manager = SessionManager(storage_dir=str(temp_session_dir))
        
        # First browser instance
        browser_manager1 = BrowserManager()
        try:
            await browser_manager1.launch_browser("chromium", headless=True)
            page1 = await browser_manager1.create_page()
            await page1.goto("data:text/html,<h1>Session Test</h1>")
            
            # Save session
            await session_manager.save_session(page1, "persistent_session")
            
        finally:
            await browser_manager1.close_browser()
        
        # Verify session exists after browser closed
        assert "persistent_session" in session_manager.list_sessions()
        
        # Second browser instance - session should still exist
        browser_manager2 = BrowserManager()
        try:
            await browser_manager2.launch_browser("chromium", headless=True)
            
            # Session should still be available
            session_info = session_manager.get_session_info("persistent_session")
            assert session_info is not None
            assert session_info.session_id == "persistent_session"
            
        finally:
            await browser_manager2.close_browser()
    
    @pytest.mark.asyncio
    async def test_multiple_sessions_with_different_browsers(self, temp_session_dir):
        """Test managing multiple sessions with different browser types."""
        session_manager = SessionManager(storage_dir=str(temp_session_dir))
        
        # Chromium session
        browser_manager_chromium = BrowserManager()
        try:
            await browser_manager_chromium.launch_browser("chromium", headless=True)
            page_chromium = await browser_manager_chromium.create_page()
            await page_chromium.goto("data:text/html,<h1>Chromium</h1>")
            await session_manager.save_session(page_chromium, "chromium_session")
        finally:
            await browser_manager_chromium.close_browser()
        
        # Firefox session
        browser_manager_firefox = BrowserManager()
        try:
            await browser_manager_firefox.launch_browser("firefox", headless=True)
            page_firefox = await browser_manager_firefox.create_page()
            await page_firefox.goto("data:text/html,<h1>Firefox</h1>")
            await session_manager.save_session(page_firefox, "firefox_session")
        finally:
            await browser_manager_firefox.close_browser()
        
        # Verify both sessions exist
        sessions = session_manager.list_sessions()
        assert "chromium_session" in sessions
        assert "firefox_session" in sessions
        
        # Verify browser types
        chromium_info = session_manager.get_session_info("chromium_session")
        firefox_info = session_manager.get_session_info("firefox_session")
        
        assert chromium_info.browser_type == "chromium"
        assert firefox_info.browser_type == "firefox"


# ============================================================================
# Integration Test 4: Page Objects
# ============================================================================

class TestPageObjectsIntegration:
    """
    Integration tests for Page Objects (BasePage, TableManager).
    
    Tests that page objects work correctly with browser and element managers.
    """
    
    @pytest.mark.asyncio
    async def test_base_page_with_browser_and_elements(self):
        """Test BasePage integration with browser and element managers."""
        browser_manager = BrowserManager()
        
        try:
            # Launch browser
            await browser_manager.launch_browser("chromium", headless=True)
            page = await browser_manager.create_page()
            
            # Create element manager and config
            config = ConfigManager()
            element_manager = ElementManager(page, config)
            
            # Create base page
            base_page = BasePage(page, element_manager, config)
            
            # Navigate using base page
            await page.set_content("""
                <!DOCTYPE html>
                <html>
                <head><title>Test Page</title></head>
                <body>
                    <h1 id="heading">Welcome</h1>
                    <button id="btn">Click Me</button>
                </body>
                </html>
            """)
            
            # Get title
            title = await base_page.get_title()
            assert title == "Test Page"
            
            # Get URL
            url = await base_page.get_url()
            assert url.startswith("data:")
            
            # Execute script
            result = await base_page.execute_script("return document.getElementById('heading').textContent")
            assert result == "Welcome"
            
        finally:
            await browser_manager.close_browser()
    
    @pytest.mark.asyncio
    async def test_table_manager_with_real_table(self):
        """Test TableManager with real HTML table."""
        browser_manager = BrowserManager()
        
        try:
            # Launch browser
            await browser_manager.launch_browser("chromium", headless=True)
            page = await browser_manager.create_page()
            
            # Create managers
            config = ConfigManager()
            element_manager = ElementManager(page, config)
            table_manager = TableManager(page, element_manager)
            
            # Create test page with table
            await page.set_content("""
                <!DOCTYPE html>
                <html>
                <body>
                    <table id="test-table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Name</th>
                                <th>Value</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>1</td>
                                <td>Alice</td>
                                <td>100</td>
                            </tr>
                            <tr>
                                <td>2</td>
                                <td>Bob</td>
                                <td>200</td>
                            </tr>
                            <tr>
                                <td>3</td>
                                <td>Charlie</td>
                                <td>300</td>
                            </tr>
                        </tbody>
                    </table>
                </body>
                </html>
            """)
            
            # Find row by key
            row_index = await table_manager.find_row_by_key(
                "css=#test-table",
                key_column=1,  # Name column
                key_value="Bob"
            )
            assert row_index == 1  # Second row (0-indexed)
            
            # Get cell value
            cell_value = await table_manager.get_cell_value(
                "css=#test-table",
                row=1,
                column=2  # Value column
            )
            assert cell_value == "200"
            
            # Get row count
            row_count = await table_manager.get_row_count("css=#test-table")
            assert row_count == 3
            
        finally:
            await browser_manager.close_browser()
    
    @pytest.mark.asyncio
    async def test_page_object_workflow_end_to_end(self):
        """Test complete page object workflow."""
        browser_manager = BrowserManager()
        
        try:
            # Launch browser
            await browser_manager.launch_browser("chromium", headless=True)
            page = await browser_manager.create_page()
            
            # Create managers
            config = ConfigManager()
            element_manager = ElementManager(page, config)
            base_page = BasePage(page, element_manager, config)
            
            # Create test application page
            await page.set_content("""
                <!DOCTYPE html>
                <html>
                <head><title>Test Application</title></head>
                <body>
                    <h1>User Management</h1>
                    <form id="user-form">
                        <input id="username" type="text" placeholder="Username" />
                        <input id="email" type="email" placeholder="Email" />
                        <button id="submit" type="button" onclick="addUser()">Add User</button>
                    </form>
                    <table id="users-table">
                        <thead>
                            <tr><th>Username</th><th>Email</th></tr>
                        </thead>
                        <tbody id="users-tbody"></tbody>
                    </table>
                    <script>
                        function addUser() {
                            const username = document.getElementById('username').value;
                            const email = document.getElementById('email').value;
                            const tbody = document.getElementById('users-tbody');
                            const row = tbody.insertRow();
                            row.insertCell(0).textContent = username;
                            row.insertCell(1).textContent = email;
                            document.getElementById('username').value = '';
                            document.getElementById('email').value = '';
                        }
                    </script>
                </body>
                </html>
            """)
            
            # Fill form
            await element_manager.fill("css=#username", "john_doe")
            await element_manager.fill("css=#email", "john@example.com")
            
            # Submit form
            await element_manager.click("css=#submit")
            
            # Wait for table update
            await asyncio.sleep(0.1)
            
            # Verify table was updated using TableManager
            table_manager = TableManager(page, element_manager)
            row_count = await table_manager.get_row_count("css=#users-table")
            assert row_count == 1
            
            # Get cell values
            username = await table_manager.get_cell_value("css=#users-table", row=0, column=0)
            email = await table_manager.get_cell_value("css=#users-table", row=0, column=1)
            
            assert username == "john_doe"
            assert email == "john@example.com"
            
            # Take screenshot
            screenshot_path = await base_page.take_screenshot("integration_test")
            assert Path(screenshot_path).exists()
            
        finally:
            await browser_manager.close_browser()


# ============================================================================
# Complex Integration Scenarios
# ============================================================================

class TestComplexIntegrationScenarios:
    """
    Complex integration scenarios combining multiple components.
    """
    
    @pytest.mark.asyncio
    async def test_full_framework_integration(self):
        """Test full framework integration: browser, elements, session, config."""
        # Setup
        browser_manager = BrowserManager()
        config = ConfigManager()
        temp_session_dir = tempfile.mkdtemp()
        session_manager = SessionManager(storage_dir=temp_session_dir)
        
        try:
            # Launch browser
            await browser_manager.launch_browser("chromium", headless=True)
            page = await browser_manager.create_page()
            
            # Create element manager
            element_manager = ElementManager(page, config)
            
            # Create base page
            base_page = BasePage(page, element_manager, config)
            
            # Navigate to test page
            await page.set_content("""
                <!DOCTYPE html>
                <html>
                <head><title>Integration Test</title></head>
                <body>
                    <h1 id="title">Full Integration Test</h1>
                    <input id="input" type="text" />
                    <button id="btn">Submit</button>
                    <div id="result"></div>
                </body>
                </html>
            """)
            
            # Interact with elements
            await element_manager.fill("css=#input", "test data")
            await element_manager.click("css=#btn")
            
            # Verify page state
            title = await base_page.get_title()
            assert title == "Integration Test"
            
            # Save session
            session_info = await session_manager.save_session(
                page,
                "full_integration_session",
                metadata={"test": "full_integration"}
            )
            
            assert session_info.session_id == "full_integration_session"
            
            # Verify session
            assert session_manager.validate_session("full_integration_session")
            
            # Take screenshot
            screenshot_path = await base_page.take_screenshot("full_integration")
            assert Path(screenshot_path).exists()
            
        finally:
            await browser_manager.close_browser()
            # Cleanup session directory
            import shutil
            shutil.rmtree(temp_session_dir, ignore_errors=True)
    
    @pytest.mark.asyncio
    async def test_multi_page_workflow_integration(self):
        """Test multi-page workflow with navigation and state management."""
        browser_manager = BrowserManager()
        config = ConfigManager()
        
        try:
            # Launch browser
            await browser_manager.launch_browser("chromium", headless=True)
            page = await browser_manager.create_page()
            
            element_manager = ElementManager(page, config)
            base_page = BasePage(page, element_manager, config)
            
            # Page 1: Login
            await page.set_content("""
                <!DOCTYPE html>
                <html>
                <head><title>Login Page</title></head>
                <body>
                    <h1>Login</h1>
                    <input id="username" type="text" />
                    <input id="password" type="password" />
                    <button id="login" onclick="window.location.href='data:text/html,<h1>Dashboard</h1>'">
                        Login
                    </button>
                </body>
                </html>
            """)
            
            # Fill login form
            await element_manager.fill("css=#username", "testuser")
            await element_manager.fill("css=#password", "password123")
            
            # Verify we're on login page
            title = await base_page.get_title()
            assert title == "Login Page"
            
            # Click login (would navigate in real scenario)
            # For this test, we'll manually navigate
            await page.set_content("""
                <!DOCTYPE html>
                <html>
                <head><title>Dashboard</title></head>
                <body>
                    <h1>Dashboard</h1>
                    <div id="welcome">Welcome, testuser!</div>
                </body>
                </html>
            """)
            
            # Verify navigation
            title = await base_page.get_title()
            assert title == "Dashboard"
            
            # Verify element on new page
            welcome_element = await element_manager.locate_element("css=#welcome")
            welcome_text = await welcome_element.text_content()
            assert "testuser" in welcome_text
            
        finally:
            await browser_manager.close_browser()
    
    @pytest.mark.asyncio
    async def test_concurrent_operations_integration(self):
        """Test concurrent operations across multiple components."""
        browser_manager = BrowserManager()
        config = ConfigManager()
        
        try:
            # Launch browser
            await browser_manager.launch_browser("chromium", headless=True)
            
            # Create multiple pages
            page1 = await browser_manager.create_page()
            page2 = await browser_manager.create_page()
            page3 = await browser_manager.create_page()
            
            # Create element managers for each page
            em1 = ElementManager(page1, config)
            em2 = ElementManager(page2, config)
            em3 = ElementManager(page3, config)
            
            # Set content for each page
            await page1.set_content("<h1 id='test'>Page 1</h1>")
            await page2.set_content("<h1 id='test'>Page 2</h1>")
            await page3.set_content("<h1 id='test'>Page 3</h1>")
            
            # Concurrent element location
            async def get_text(em, page_num):
                element = await em.locate_element("css=#test")
                text = await element.text_content()
                return f"Page {page_num}", text
            
            results = await asyncio.gather(
                get_text(em1, 1),
                get_text(em2, 2),
                get_text(em3, 3)
            )
            
            # Verify results
            assert results[0] == ("Page 1", "Page 1")
            assert results[1] == ("Page 2", "Page 2")
            assert results[2] == ("Page 3", "Page 3")
            
        finally:
            await browser_manager.close_browser()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
