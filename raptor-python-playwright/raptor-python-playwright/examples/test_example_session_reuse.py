"""
Example Session Reuse Test

This example demonstrates session reuse capabilities using the RAPTOR framework.
It shows how to:
- Save browser sessions after authentication
- Restore sessions to skip login steps
- Share sessions across test runs
- Manage session lifecycle
- Handle session expiration

Requirements: NFR-004, Requirements 3.1, 3.2, 3.4
"""

import pytest
from raptor.core.browser_manager import BrowserManager
from raptor.core.element_manager import ElementManager
from raptor.core.config_manager import ConfigManager
from raptor.core.session_manager import SessionManager
from raptor.pages.base_page import BasePage


@pytest.mark.asyncio
class TestSessionReuseExample:
    """Example test class demonstrating session reuse"""
    
    async def test_create_and_save_session(self):
        """
        Test creating a new session and saving it for reuse
        
        This example shows:
        1. Performing initial login
        2. Saving the authenticated session
        3. Verifying session is saved
        """
        config = ConfigManager()
        browser_manager = BrowserManager(config)
        session_manager = SessionManager(config)
        
        try:
            # Launch browser
            browser = await browser_manager.launch_browser("chromium", headless=True)
            context = await browser_manager.create_context()
            page = await browser_manager.create_page(context)
            
            element_manager = ElementManager(page, config)
            base_page = BasePage(page, element_manager)
            
            print("\n=== Creating New Session ===")
            
            # Perform login
            await base_page.navigate("https://example.com/login")
            await element_manager.fill("css=#username", "testuser@example.com")
            await element_manager.fill("css=#password", "TestPass123!")
            await element_manager.click("css=#login-button")
            
            # Wait for successful login
            await page.wait_for_url("**/dashboard", timeout=10000)
            print("Login successful")
            
            # Verify we're logged in
            assert await element_manager.is_visible("css=.welcome-message")
            welcome_text = await element_manager.get_text("css=.welcome-message")
            print(f"Welcome message: {welcome_text}")
            
            # Save the session
            session_name = "test_user_session"
            await session_manager.save_session(page, session_name)
            print(f"Session saved as: {session_name}")
            
            # Verify session was saved
            sessions = await session_manager.list_sessions()
            assert session_name in sessions, "Session not saved"
            
            # Get session info
            session_info = session_manager.get_session_info(session_name)
            print(f"Session info: {session_info}")
            
        finally:
            await browser_manager.close_browser()
    
    async def test_restore_and_reuse_session(self):
        """
        Test restoring a previously saved session
        
        This example shows:
        1. Restoring a saved session
        2. Verifying authentication state
        3. Continuing work without re-login
        """
        config = ConfigManager()
        session_manager = SessionManager(config)
        
        try:
            print("\n=== Restoring Saved Session ===")
            
            # Restore the session (no login required!)
            session_name = "test_user_session"
            page = await session_manager.restore_session(session_name)
            
            print(f"Session '{session_name}' restored")
            
            # Verify we're still logged in
            element_manager = ElementManager(page, config)
            base_page = BasePage(page, element_manager)
            
            current_url = await base_page.get_url()
            print(f"Current URL: {current_url}")
            
            # Should still be on dashboard or able to navigate to it
            if "/dashboard" not in current_url:
                await base_page.navigate("https://example.com/dashboard")
            
            # Verify authenticated state
            assert await element_manager.is_visible("css=.welcome-message")
            print("Session is still authenticated!")
            
            # Can now perform actions without logging in
            await element_manager.click("css=#profile-link")
            await page.wait_for_url("**/profile", timeout=10000)
            
            profile_name = await element_manager.get_text("css=.profile-name")
            print(f"Accessed profile: {profile_name}")
            
        finally:
            # Note: We don't close the browser here as session manager handles it
            pass
    
    async def test_session_reuse_across_multiple_tests(self):
        """
        Test using the same session across multiple test scenarios
        
        This example shows:
        1. Reusing session for different test operations
        2. Maintaining state across tests
        3. Efficient test execution
        """
        config = ConfigManager()
        session_manager = SessionManager(config)
        
        try:
            session_name = "test_user_session"
            
            # Test 1: View profile
            print("\n=== Test 1: View Profile ===")
            page = await session_manager.restore_session(session_name)
            element_manager = ElementManager(page, config)
            base_page = BasePage(page, element_manager)
            
            await base_page.navigate("https://example.com/profile")
            profile_email = await element_manager.get_value("css=#profile-email")
            print(f"Profile email: {profile_email}")
            assert profile_email == "testuser@example.com"
            
            # Test 2: View orders
            print("\n=== Test 2: View Orders ===")
            await base_page.navigate("https://example.com/orders")
            await element_manager.wait_for_element("css=#orders-table", timeout=10000)
            
            order_count = await page.locator("css=.order-row").count()
            print(f"Found {order_count} orders")
            
            # Test 3: Update settings
            print("\n=== Test 3: Update Settings ===")
            await base_page.navigate("https://example.com/settings")
            await element_manager.wait_for_element("css=#settings-form", timeout=10000)
            
            # Toggle a setting
            await element_manager.click("css=#notifications-toggle")
            await element_manager.click("css=#save-settings")
            
            await element_manager.wait_for_element("css=.settings-saved", timeout=5000)
            print("Settings updated successfully")
            
        finally:
            pass
    
    async def test_session_with_different_users(self):
        """
        Test managing sessions for multiple users
        
        This example shows:
        1. Creating sessions for different users
        2. Switching between user sessions
        3. Isolating user contexts
        """
        config = ConfigManager()
        browser_manager = BrowserManager(config)
        session_manager = SessionManager(config)
        
        users = [
            {"username": "user1@example.com", "password": "User1Pass!", "session": "user1_session"},
            {"username": "user2@example.com", "password": "User2Pass!", "session": "user2_session"},
            {"username": "admin@example.com", "password": "AdminPass!", "session": "admin_session"}
        ]
        
        try:
            # Create sessions for all users
            print("\n=== Creating Sessions for Multiple Users ===")
            
            for user in users:
                browser = await browser_manager.launch_browser("chromium", headless=True)
                context = await browser_manager.create_context()
                page = await browser_manager.create_page(context)
                
                element_manager = ElementManager(page, config)
                base_page = BasePage(page, element_manager)
                
                # Login
                await base_page.navigate("https://example.com/login")
                await element_manager.fill("css=#username", user["username"])
                await element_manager.fill("css=#password", user["password"])
                await element_manager.click("css=#login-button")
                await page.wait_for_url("**/dashboard", timeout=10000)
                
                # Save session
                await session_manager.save_session(page, user["session"])
                print(f"Created session for: {user['username']}")
                
                await browser_manager.close_browser()
            
            # Now use different sessions
            print("\n=== Using Different User Sessions ===")
            
            # Use user1 session
            print("\n--- User 1 ---")
            page1 = await session_manager.restore_session("user1_session")
            element_manager1 = ElementManager(page1, config)
            user1_name = await element_manager1.get_text("css=.user-name")
            print(f"Logged in as: {user1_name}")
            
            # Use admin session
            print("\n--- Admin ---")
            page_admin = await session_manager.restore_session("admin_session")
            element_manager_admin = ElementManager(page_admin, config)
            
            # Admin can access admin panel
            await page_admin.goto("https://example.com/admin")
            assert await element_manager_admin.is_visible("css=#admin-panel")
            print("Admin panel accessible")
            
            # Use user2 session
            print("\n--- User 2 ---")
            page2 = await session_manager.restore_session("user2_session")
            element_manager2 = ElementManager(page2, config)
            user2_name = await element_manager2.get_text("css=.user-name")
            print(f"Logged in as: {user2_name}")
            
        finally:
            # Cleanup all sessions
            for user in users:
                await session_manager.delete_session(user["session"])
            print("\nAll sessions cleaned up")
    
    async def test_session_expiration_handling(self):
        """
        Test handling session expiration
        
        This example shows:
        1. Detecting expired sessions
        2. Handling session restoration failures
        3. Fallback to re-authentication
        """
        config = ConfigManager()
        browser_manager = BrowserManager(config)
        session_manager = SessionManager(config)
        
        try:
            print("\n=== Testing Session Expiration ===")
            
            # Try to restore a session that might be expired
            session_name = "potentially_expired_session"
            
            try:
                page = await session_manager.restore_session(session_name)
                element_manager = ElementManager(page, config)
                base_page = BasePage(page, element_manager)
                
                # Try to access a protected page
                await base_page.navigate("https://example.com/dashboard")
                
                # Check if we're redirected to login (session expired)
                current_url = await base_page.get_url()
                
                if "/login" in current_url:
                    print("Session expired, re-authenticating...")
                    
                    # Re-authenticate
                    await element_manager.fill("css=#username", "testuser@example.com")
                    await element_manager.fill("css=#password", "TestPass123!")
                    await element_manager.click("css=#login-button")
                    await page.wait_for_url("**/dashboard", timeout=10000)
                    
                    # Save new session
                    await session_manager.save_session(page, session_name)
                    print("New session created and saved")
                else:
                    print("Session is still valid")
                
            except Exception as e:
                print(f"Session restoration failed: {e}")
                print("Creating new session...")
                
                # Create new session
                browser = await browser_manager.launch_browser("chromium", headless=True)
                context = await browser_manager.create_context()
                page = await browser_manager.create_page(context)
                
                element_manager = ElementManager(page, config)
                base_page = BasePage(page, element_manager)
                
                await base_page.navigate("https://example.com/login")
                await element_manager.fill("css=#username", "testuser@example.com")
                await element_manager.fill("css=#password", "TestPass123!")
                await element_manager.click("css=#login-button")
                await page.wait_for_url("**/dashboard", timeout=10000)
                
                await session_manager.save_session(page, session_name)
                print("New session created successfully")
                
        finally:
            await browser_manager.close_browser()
    
    async def test_session_cleanup_and_management(self):
        """
        Test session lifecycle management
        
        This example shows:
        1. Listing all saved sessions
        2. Getting session information
        3. Deleting old sessions
        4. Managing session storage
        """
        config = ConfigManager()
        session_manager = SessionManager(config)
        
        try:
            print("\n=== Session Management ===")
            
            # List all sessions
            sessions = await session_manager.list_sessions()
            print(f"\nFound {len(sessions)} saved sessions:")
            
            for session_name in sessions:
                session_info = session_manager.get_session_info(session_name)
                print(f"\n  Session: {session_name}")
                print(f"    Created: {session_info.get('created_at', 'Unknown')}")
                print(f"    Last accessed: {session_info.get('last_accessed', 'Unknown')}")
                print(f"    Browser: {session_info.get('browser_type', 'Unknown')}")
            
            # Delete old or unused sessions
            print("\n=== Cleaning Up Old Sessions ===")
            
            sessions_to_delete = ["old_session_1", "temp_session", "expired_session"]
            
            for session_name in sessions_to_delete:
                if session_name in sessions:
                    await session_manager.delete_session(session_name)
                    print(f"Deleted session: {session_name}")
            
            # Verify cleanup
            remaining_sessions = await session_manager.list_sessions()
            print(f"\nRemaining sessions: {len(remaining_sessions)}")
            
        finally:
            pass


@pytest.mark.asyncio
async def test_session_reuse_performance_comparison():
    """
    Standalone test comparing performance with and without session reuse
    
    This example shows:
    1. Measuring time with fresh login
    2. Measuring time with session reuse
    3. Demonstrating performance benefits
    """
    import time
    
    config = ConfigManager()
    browser_manager = BrowserManager(config)
    session_manager = SessionManager(config)
    
    try:
        # Test 1: Without session reuse (fresh login)
        print("\n=== Test 1: Fresh Login (No Session Reuse) ===")
        start_time = time.time()
        
        browser = await browser_manager.launch_browser("chromium", headless=True)
        context = await browser_manager.create_context()
        page = await browser_manager.create_page(context)
        
        element_manager = ElementManager(page, config)
        base_page = BasePage(page, element_manager)
        
        await base_page.navigate("https://example.com/login")
        await element_manager.fill("css=#username", "testuser@example.com")
        await element_manager.fill("css=#password", "TestPass123!")
        await element_manager.click("css=#login-button")
        await page.wait_for_url("**/dashboard", timeout=10000)
        
        # Perform some actions
        await base_page.navigate("https://example.com/profile")
        await element_manager.wait_for_element("css=#profile-form", timeout=5000)
        
        fresh_login_time = time.time() - start_time
        print(f"Time with fresh login: {fresh_login_time:.2f} seconds")
        
        # Save session for next test
        await session_manager.save_session(page, "perf_test_session")
        await browser_manager.close_browser()
        
        # Test 2: With session reuse
        print("\n=== Test 2: Session Reuse ===")
        start_time = time.time()
        
        page = await session_manager.restore_session("perf_test_session")
        element_manager = ElementManager(page, config)
        base_page = BasePage(page, element_manager)
        
        # Perform same actions
        await base_page.navigate("https://example.com/profile")
        await element_manager.wait_for_element("css=#profile-form", timeout=5000)
        
        session_reuse_time = time.time() - start_time
        print(f"Time with session reuse: {session_reuse_time:.2f} seconds")
        
        # Calculate improvement
        time_saved = fresh_login_time - session_reuse_time
        percent_faster = (time_saved / fresh_login_time) * 100
        
        print(f"\n=== Performance Comparison ===")
        print(f"Time saved: {time_saved:.2f} seconds")
        print(f"Percent faster: {percent_faster:.1f}%")
        
        # Cleanup
        await session_manager.delete_session("perf_test_session")
        
    finally:
        pass


if __name__ == "__main__":
    """
    Run this example directly:
    python examples/test_example_session_reuse.py
    
    Or with pytest:
    pytest examples/test_example_session_reuse.py -v
    """
    pytest.main([__file__, "-v", "-s"])
