"""
Example usage of SessionManager for browser session persistence.

This example demonstrates:
1. Saving a browser session after login
2. Restoring the session in a later test run
3. Managing multiple sessions
4. Cleaning up old sessions
"""

import asyncio
from raptor.core.browser_manager import BrowserManager
from raptor.core.session_manager import SessionManager


async def example_save_session():
    """
    Example: Save a browser session after performing login.
    
    This is useful when you want to reuse an authenticated session
    across multiple test runs without logging in each time.
    """
    print("=== Example 1: Saving a Browser Session ===\n")
    
    # Initialize managers
    browser_manager = BrowserManager()
    session_manager = SessionManager()
    
    try:
        # Launch browser and create page
        await browser_manager.launch_browser("chromium", headless=False)
        context = await browser_manager.create_context()
        page = await browser_manager.create_page(context)
        
        # Navigate to login page
        print("Navigating to example.com...")
        await page.goto("https://example.com")
        await page.wait_for_load_state("networkidle")
        
        # Simulate login (in real scenario, you would fill forms and click login)
        print("Performing login actions...")
        # await page.fill("#username", "test_user")
        # await page.fill("#password", "test_password")
        # await page.click("#login-button")
        # await page.wait_for_url("**/dashboard")
        
        # Save the session
        print("Saving session...")
        session_info = await session_manager.save_session(
            page,
            "example_login_session",
            metadata={
                "user": "test_user",
                "environment": "staging",
                "purpose": "automated_testing"
            }
        )
        
        print(f"✓ Session saved successfully!")
        print(f"  Session ID: {session_info.session_id}")
        print(f"  Browser Type: {session_info.browser_type}")
        print(f"  Created At: {session_info.created_at}")
        print(f"  CDP URL: {session_info.cdp_url[:50]}...")
        print(f"  Metadata: {session_info.metadata}")
        
    finally:
        # Note: Don't close the browser if you want to restore the session later
        # For this example, we'll keep it open
        print("\n✓ Browser session is ready for reuse")
        print("  (Browser left open for session restoration)")


async def example_restore_session():
    """
    Example: Restore a previously saved browser session.
    
    This allows you to reconnect to a browser that was left running
    and continue from where you left off.
    """
    print("\n=== Example 2: Restoring a Browser Session ===\n")
    
    session_manager = SessionManager()
    
    try:
        # Check if session exists
        if not session_manager.validate_session("example_login_session"):
            print("✗ Session 'example_login_session' not found or invalid")
            print("  Please run example_save_session() first")
            return
        
        # Restore the session
        print("Restoring session 'example_login_session'...")
        page = await session_manager.restore_session("example_login_session")
        
        print(f"✓ Session restored successfully!")
        print(f"  Current URL: {page.url}")
        print(f"  Page Title: {await page.title()}")
        
        # Now you can continue using the page
        print("\nContinuing test automation with restored session...")
        # await page.goto("https://example.com/dashboard")
        # await page.click("#some-button")
        
    except Exception as e:
        print(f"✗ Failed to restore session: {e}")


async def example_list_sessions():
    """
    Example: List all available saved sessions.
    """
    print("\n=== Example 3: Listing Available Sessions ===\n")
    
    session_manager = SessionManager()
    
    # List all sessions
    sessions = session_manager.list_sessions()
    
    if not sessions:
        print("No saved sessions found")
        return
    
    print(f"Found {len(sessions)} saved session(s):\n")
    
    for session_name in sessions:
        info = session_manager.get_session_info(session_name)
        if info:
            print(f"Session: {session_name}")
            print(f"  Browser: {info.browser_type}")
            print(f"  Created: {info.created_at}")
            print(f"  Last Accessed: {info.last_accessed}")
            print(f"  Metadata: {info.metadata}")
            print()


async def example_cleanup_sessions():
    """
    Example: Clean up old sessions.
    
    This is useful for maintenance to remove sessions that are
    no longer needed or have expired.
    """
    print("\n=== Example 4: Cleaning Up Old Sessions ===\n")
    
    session_manager = SessionManager()
    
    # Clean up sessions older than 7 days
    print("Cleaning up sessions older than 7 days...")
    deleted_count = session_manager.cleanup_expired_sessions(max_age_days=7)
    
    print(f"✓ Deleted {deleted_count} expired session(s)")


async def example_delete_session():
    """
    Example: Delete a specific session.
    """
    print("\n=== Example 5: Deleting a Specific Session ===\n")
    
    session_manager = SessionManager()
    
    session_name = "example_login_session"
    
    # Check if session exists
    if session_name not in session_manager.list_sessions():
        print(f"Session '{session_name}' not found")
        return
    
    # Delete the session
    print(f"Deleting session '{session_name}'...")
    result = session_manager.delete_session(session_name)
    
    if result:
        print(f"✓ Session '{session_name}' deleted successfully")
    else:
        print(f"✗ Failed to delete session '{session_name}'")


async def example_multiple_sessions():
    """
    Example: Managing multiple sessions for different users/scenarios.
    
    This demonstrates how to maintain separate sessions for different
    test scenarios or user accounts.
    """
    print("\n=== Example 6: Managing Multiple Sessions ===\n")
    
    browser_manager = BrowserManager()
    session_manager = SessionManager()
    
    try:
        # Launch browser
        await browser_manager.launch_browser("chromium", headless=False)
        
        # Create sessions for different users
        users = ["admin_user", "regular_user", "guest_user"]
        
        for user in users:
            print(f"\nCreating session for {user}...")
            
            # Create new context for each user (isolation)
            context = await browser_manager.create_context()
            page = await browser_manager.create_page(context)
            
            # Navigate and "login" as different user
            await page.goto("https://example.com")
            await page.wait_for_load_state("networkidle")
            
            # Save session with user-specific name
            session_name = f"session_{user}"
            await session_manager.save_session(
                page,
                session_name,
                metadata={"user": user, "role": user.split("_")[0]}
            )
            
            print(f"  ✓ Session '{session_name}' saved")
        
        print("\n✓ All user sessions created successfully")
        
        # List all sessions
        print("\nAvailable sessions:")
        for session in session_manager.list_sessions():
            print(f"  - {session}")
            
    finally:
        # Keep browser open for session reuse
        print("\n✓ Browser sessions ready for reuse")


async def example_session_validation():
    """
    Example: Validate sessions before attempting to restore.
    
    This is a best practice to check if a session is valid
    before attempting to restore it.
    """
    print("\n=== Example 7: Session Validation ===\n")
    
    session_manager = SessionManager()
    
    session_name = "example_login_session"
    
    print(f"Validating session '{session_name}'...")
    
    if session_manager.validate_session(session_name):
        print(f"✓ Session '{session_name}' is valid")
        
        # Get detailed info
        info = session_manager.get_session_info(session_name)
        print(f"\nSession Details:")
        print(f"  Browser Type: {info.browser_type}")
        print(f"  Has CDP URL: {bool(info.cdp_url)}")
        print(f"  Created: {info.created_at}")
        print(f"  Last Accessed: {info.last_accessed}")
        
        # Safe to restore
        print("\n✓ Safe to restore this session")
    else:
        print(f"✗ Session '{session_name}' is invalid or not found")
        print("  Cannot restore this session")


async def main():
    """
    Run all examples.
    
    Note: Some examples depend on previous ones (e.g., restore depends on save).
    Run them in order for best results.
    """
    print("=" * 60)
    print("SessionManager Examples")
    print("=" * 60)
    
    # Example 1: Save a session
    await example_save_session()
    
    # Wait a moment for session to be fully saved
    await asyncio.sleep(2)
    
    # Example 2: List sessions
    await example_list_sessions()
    
    # Example 3: Validate session
    await example_session_validation()
    
    # Example 4: Restore session (uncomment if you want to test restoration)
    # Note: This requires the browser from example 1 to still be running
    # await example_restore_session()
    
    # Example 5: Multiple sessions (uncomment to test)
    # await example_multiple_sessions()
    
    # Example 6: Cleanup old sessions
    # await example_cleanup_sessions()
    
    # Example 7: Delete specific session (uncomment to test)
    # await example_delete_session()
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
