"""
Example usage of TableManager for table operations.

This example demonstrates:
- Finding rows by key values
- Reading and writing cell values
- Clicking cells
- Searching tables
- Navigating paginated tables
"""

import asyncio
from playwright.async_api import async_playwright
from raptor.core.browser_manager import BrowserManager
from raptor.core.element_manager import ElementManager
from raptor.pages.table_manager import TableManager
from raptor.core.config_manager import ConfigManager


async def main():
    """Demonstrate TableManager functionality."""
    # Initialize managers
    config = ConfigManager()
    browser_manager = BrowserManager(config)

    async with async_playwright() as p:
        # Launch browser
        browser = await browser_manager.launch_browser("chromium", headless=False)
        context = await browser_manager.create_context()
        page = await browser_manager.create_page(context)

        # Initialize element and table managers
        element_manager = ElementManager(page, config)
        table_manager = TableManager(page, element_manager, config)

        # Navigate to a page with a table
        await page.goto("https://example.com/users")

        print("=== Table Manager Examples ===\n")

        # Example 1: Find a row by key value
        print("1. Finding row by username...")
        try:
            row_index = await table_manager.find_row_by_key(
                table_locator="css=#users-table",
                key_column=0,  # Username column
                key_value="john.doe"
            )
            print(f"   Found user 'john.doe' at row {row_index}\n")
        except Exception as e:
            print(f"   Error: {e}\n")

        # Example 2: Get cell value
        print("2. Reading cell value...")
        try:
            email = await table_manager.get_cell_value(
                table_locator="css=#users-table",
                row=row_index,
                column=2  # Email column
            )
            print(f"   Email: {email}\n")
        except Exception as e:
            print(f"   Error: {e}\n")

        # Example 3: Set cell value (for editable cells)
        print("3. Updating cell value...")
        try:
            await table_manager.set_cell_value(
                table_locator="css=#users-table",
                row=row_index,
                column=2,  # Email column
                value="new.email@example.com"
            )
            print("   Cell value updated successfully\n")
        except Exception as e:
            print(f"   Error: {e}\n")

        # Example 4: Click a cell (e.g., edit button)
        print("4. Clicking cell...")
        try:
            await table_manager.click_cell(
                table_locator="css=#users-table",
                row=row_index,
                column=4  # Edit button column
            )
            print("   Cell clicked successfully\n")
        except Exception as e:
            print(f"   Error: {e}\n")

        # Example 5: Get row count
        print("5. Getting row count...")
        try:
            count = await table_manager.get_row_count("css=#users-table")
            print(f"   Table has {count} rows\n")
        except Exception as e:
            print(f"   Error: {e}\n")

        # Example 6: Search table
        print("6. Searching table...")
        try:
            matching_rows = await table_manager.search_table(
                table_locator="css=#users-table",
                search_text="admin",
                case_sensitive=False,
                partial_match=True
            )
            print(f"   Found matches in rows: {matching_rows}\n")
        except Exception as e:
            print(f"   Error: {e}\n")

        # Example 7: Get all values from a column
        print("7. Getting column values...")
        try:
            usernames = await table_manager.get_column_values(
                table_locator="css=#users-table",
                column=0  # Username column
            )
            print(f"   Usernames: {usernames}\n")
        except Exception as e:
            print(f"   Error: {e}\n")

        # Example 8: Navigate paginated table
        print("8. Navigating paginated table...")
        try:
            page_num = 1
            while True:
                print(f"   Processing page {page_num}...")

                # Process current page data
                row_count = await table_manager.get_row_count("css=#users-table")
                print(f"   Page {page_num} has {row_count} rows")

                # Try to navigate to next page
                has_next = await table_manager.navigate_pagination("css=.next-page")

                if not has_next:
                    print("   Reached last page\n")
                    break

                page_num += 1

        except Exception as e:
            print(f"   Error: {e}\n")

        # Example 9: Complex workflow - Find and update multiple rows
        print("9. Complex workflow - updating multiple rows...")
        try:
            # Search for all admin users
            admin_rows = await table_manager.search_table(
                table_locator="css=#users-table",
                search_text="admin",
                case_sensitive=False
            )

            # Update status for each admin user
            for row_idx in admin_rows:
                username = await table_manager.get_cell_value(
                    "css=#users-table",
                    row=row_idx,
                    column=0
                )

                print(f"   Updating status for user: {username}")

                await table_manager.set_cell_value(
                    "css=#users-table",
                    row=row_idx,
                    column=3,  # Status column
                    value="Active"
                )

            print(f"   Updated {len(admin_rows)} admin users\n")

        except Exception as e:
            print(f"   Error: {e}\n")

        # Cleanup
        await browser_manager.close_browser()
        print("=== Examples Complete ===")


if __name__ == "__main__":
    asyncio.run(main())
