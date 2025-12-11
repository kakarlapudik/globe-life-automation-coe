"""
Advanced Table Operations Example for RAPTOR Python Playwright Framework.

This example demonstrates advanced table operations including:
- Dynamic table loading
- Infinite scroll tables
- Pagination navigation
- Table search with partial matching
- Waiting for table updates
"""

import asyncio
from playwright.async_api import async_playwright
from raptor.core.browser_manager import BrowserManager
from raptor.core.element_manager import ElementManager
from raptor.pages.table_manager import TableManager
from raptor.core.config_manager import ConfigManager


async def example_search_table():
    """Example: Search table with partial matching and case-insensitive search."""
    print("\n=== Example: Search Table ===")
    
    async with async_playwright() as p:
        # Initialize managers
        browser_manager = BrowserManager()
        browser = await browser_manager.launch_browser("chromium", headless=False)
        page = await browser_manager.create_page()
        
        element_manager = ElementManager(page)
        table_manager = TableManager(page, element_manager)
        
        # Navigate to a page with a table
        await page.goto("https://example.com/users-table")
        
        # Search for rows containing "john" (case-insensitive, partial match)
        matching_rows = await table_manager.search_table(
            table_locator="css=#users-table",
            search_text="john",
            case_sensitive=False,
            partial_match=True
        )
        
        print(f"Found {len(matching_rows)} rows matching 'john': {matching_rows}")
        
        # Search for exact match (case-sensitive)
        exact_matches = await table_manager.search_table(
            table_locator="css=#users-table",
            search_text="John Doe",
            case_sensitive=True,
            partial_match=False
        )
        
        print(f"Found {len(exact_matches)} exact matches for 'John Doe'")
        
        await browser_manager.close_browser()


async def example_dynamic_table_loading():
    """Example: Wait for dynamic table to finish loading."""
    print("\n=== Example: Dynamic Table Loading ===")
    
    async with async_playwright() as p:
        # Initialize managers
        browser_manager = BrowserManager()
        browser = await browser_manager.launch_browser("chromium", headless=False)
        page = await browser_manager.create_page()
        
        element_manager = ElementManager(page)
        table_manager = TableManager(page, element_manager)
        
        # Navigate to a page with a dynamically loading table
        await page.goto("https://example.com/dynamic-table")
        
        # Wait for the table to finish loading
        await table_manager.wait_for_table_update("css=#dynamic-table")
        
        # Now safe to read table data
        row_count = await table_manager.get_row_count("css=#dynamic-table")
        print(f"Table has {row_count} rows after loading")
        
        # Get all values from a specific column
        emails = await table_manager.get_column_values(
            "css=#dynamic-table",
            column=2  # Email column
        )
        print(f"Found {len(emails)} email addresses")
        
        await browser_manager.close_browser()


async def example_infinite_scroll_table():
    """Example: Load all rows from an infinite scroll table."""
    print("\n=== Example: Infinite Scroll Table ===")
    
    async with async_playwright() as p:
        # Initialize managers
        browser_manager = BrowserManager()
        browser = await browser_manager.launch_browser("chromium", headless=False)
        page = await browser_manager.create_page()
        
        element_manager = ElementManager(page)
        table_manager = TableManager(page, element_manager)
        
        # Navigate to a page with an infinite scroll table
        await page.goto("https://example.com/infinite-scroll-table")
        
        # Load all rows by scrolling
        total_rows = await table_manager.load_all_dynamic_rows(
            table_locator="css=#infinite-scroll-table",
            max_scrolls=100  # Maximum number of scroll attempts
        )
        
        print(f"Loaded {total_rows} total rows from infinite scroll table")
        
        # Now you can process all the loaded data
        for row_idx in range(min(10, total_rows)):  # Process first 10 rows
            cell_value = await table_manager.get_cell_value(
                "css=#infinite-scroll-table",
                row=row_idx,
                column=0
            )
            print(f"Row {row_idx}: {cell_value}")
        
        await browser_manager.close_browser()


async def example_pagination_navigation():
    """Example: Navigate through paginated table."""
    print("\n=== Example: Pagination Navigation ===")
    
    async with async_playwright() as p:
        # Initialize managers
        browser_manager = BrowserManager()
        browser = await browser_manager.launch_browser("chromium", headless=False)
        page = await browser_manager.create_page()
        
        element_manager = ElementManager(page)
        table_manager = TableManager(page, element_manager)
        
        # Navigate to a page with a paginated table
        await page.goto("https://example.com/paginated-table")
        
        # Get pagination information
        pagination_info = await table_manager.get_pagination_info(
            current_page_locator="css=.current-page",
            total_pages_locator="css=.total-pages"
        )
        
        print(f"Current page: {pagination_info['current_page']}")
        print(f"Total pages: {pagination_info['total_pages']}")
        print(f"Has next: {pagination_info['has_next']}")
        print(f"Has previous: {pagination_info['has_previous']}")
        
        # Navigate through all pages
        page_num = 1
        while True:
            print(f"\nProcessing page {page_num}...")
            
            # Process current page data
            row_count = await table_manager.get_row_count("css=#data-table")
            print(f"  Found {row_count} rows on this page")
            
            # Try to navigate to next page
            has_next = await table_manager.navigate_pagination("css=.next-page")
            
            if not has_next:
                print("Reached last page")
                break
            
            page_num += 1
            
            # Wait for new page to load
            await table_manager.wait_for_table_update("css=#data-table")
        
        await browser_manager.close_browser()


async def example_navigate_to_specific_page():
    """Example: Navigate to a specific page number."""
    print("\n=== Example: Navigate to Specific Page ===")
    
    async with async_playwright() as p:
        # Initialize managers
        browser_manager = BrowserManager()
        browser = await browser_manager.launch_browser("chromium", headless=False)
        page = await browser_manager.create_page()
        
        element_manager = ElementManager(page)
        table_manager = TableManager(page, element_manager)
        
        # Navigate to a page with a paginated table
        await page.goto("https://example.com/paginated-table")
        
        # Navigate to page 5 using input field
        success = await table_manager.navigate_to_page(
            page_number=5,
            page_input_locator="css=.page-input"
        )
        
        if success:
            print("Successfully navigated to page 5")
            
            # Wait for table to update
            await table_manager.wait_for_table_update("css=#data-table")
            
            # Process page 5 data
            row_count = await table_manager.get_row_count("css=#data-table")
            print(f"Page 5 has {row_count} rows")
        else:
            print("Failed to navigate to page 5")
        
        await browser_manager.close_browser()


async def example_scroll_table_into_view():
    """Example: Scroll table into view for lazy-loaded content."""
    print("\n=== Example: Scroll Table Into View ===")
    
    async with async_playwright() as p:
        # Initialize managers
        browser_manager = BrowserManager()
        browser = await browser_manager.launch_browser("chromium", headless=False)
        page = await browser_manager.create_page()
        
        element_manager = ElementManager(page)
        table_manager = TableManager(page, element_manager)
        
        # Navigate to a page with a lazy-loaded table
        await page.goto("https://example.com/lazy-table")
        
        # Scroll table into view to trigger lazy loading
        await table_manager.scroll_table_into_view("css=#lazy-table")
        
        # Wait for content to load
        await table_manager.wait_for_table_update("css=#lazy-table")
        
        # Now table content is loaded and visible
        row_count = await table_manager.get_row_count("css=#lazy-table")
        print(f"Lazy-loaded table has {row_count} rows")
        
        await browser_manager.close_browser()


async def example_combined_workflow():
    """Example: Combined workflow with search, pagination, and dynamic loading."""
    print("\n=== Example: Combined Workflow ===")
    
    async with async_playwright() as p:
        # Initialize managers
        browser_manager = BrowserManager()
        browser = await browser_manager.launch_browser("chromium", headless=False)
        page = await browser_manager.create_page()
        
        element_manager = ElementManager(page)
        table_manager = TableManager(page, element_manager)
        
        # Navigate to application
        await page.goto("https://example.com/users")
        
        # Wait for initial table load
        await table_manager.wait_for_table_update("css=#users-table")
        
        # Search for specific users
        matching_rows = await table_manager.search_table(
            table_locator="css=#users-table",
            search_text="admin",
            case_sensitive=False,
            partial_match=True
        )
        
        print(f"Found {len(matching_rows)} admin users on current page")
        
        # Collect all admin users across all pages
        all_admin_users = []
        page_num = 1
        
        while True:
            print(f"\nSearching page {page_num}...")
            
            # Search current page
            matching_rows = await table_manager.search_table(
                table_locator="css=#users-table",
                search_text="admin",
                case_sensitive=False,
                partial_match=True
            )
            
            # Collect matching user data
            for row_idx in matching_rows:
                username = await table_manager.get_cell_value(
                    "css=#users-table",
                    row=row_idx,
                    column=0
                )
                email = await table_manager.get_cell_value(
                    "css=#users-table",
                    row=row_idx,
                    column=1
                )
                all_admin_users.append({"username": username, "email": email})
            
            # Try to go to next page
            has_next = await table_manager.navigate_pagination("css=.next-page")
            
            if not has_next:
                break
            
            page_num += 1
            await table_manager.wait_for_table_update("css=#users-table")
        
        print(f"\nTotal admin users found: {len(all_admin_users)}")
        for user in all_admin_users[:5]:  # Show first 5
            print(f"  - {user['username']}: {user['email']}")
        
        await browser_manager.close_browser()


async def main():
    """Run all examples."""
    print("RAPTOR Advanced Table Operations Examples")
    print("=" * 50)
    
    # Note: These examples use placeholder URLs
    # Replace with actual URLs for your application
    
    print("\nNote: These examples use placeholder URLs.")
    print("Update the URLs to match your application for actual testing.")
    
    # Uncomment the examples you want to run:
    
    # await example_search_table()
    # await example_dynamic_table_loading()
    # await example_infinite_scroll_table()
    # await example_pagination_navigation()
    # await example_navigate_to_specific_page()
    # await example_scroll_table_into_view()
    # await example_combined_workflow()
    
    print("\nExamples completed!")


if __name__ == "__main__":
    asyncio.run(main())
