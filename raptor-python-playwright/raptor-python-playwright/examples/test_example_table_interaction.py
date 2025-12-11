"""
Example Table Interaction Test

This example demonstrates table operations using the RAPTOR framework.
It shows how to:
- Locate rows in tables by key values
- Read and write cell data
- Search tables with various criteria
- Handle pagination
- Perform bulk operations on table data

Requirements: NFR-004, Requirements 8.1, 8.2, 8.3, 8.4, 8.5
"""

import pytest
from raptor.core.browser_manager import BrowserManager
from raptor.core.element_manager import ElementManager
from raptor.core.config_manager import ConfigManager
from raptor.pages.base_page import BasePage
from raptor.pages.table_manager import TableManager


@pytest.mark.asyncio
class TestTableInteractionExample:
    """Example test class demonstrating table operations"""
    
    async def test_find_and_read_table_row(self):
        """
        Test finding a specific row in a table and reading its data
        
        This example shows:
        1. Locating a row by key column value
        2. Reading cell values from the row
        3. Verifying data accuracy
        """
        config = ConfigManager()
        browser_manager = BrowserManager(config)
        
        try:
            # Launch browser
            browser = await browser_manager.launch_browser("chromium", headless=True)
            context = await browser_manager.create_context()
            page = await browser_manager.create_page(context)
            
            element_manager = ElementManager(page, config)
            base_page = BasePage(page, element_manager)
            table_manager = TableManager(page, element_manager)
            
            # Navigate to page with table
            await base_page.navigate("https://example.com/users")
            await base_page.wait_for_load()
            
            # Wait for table to load
            await element_manager.wait_for_element("css=#users-table", timeout=10000)
            
            # Find row by email (key column = 2)
            table_locator = "css=#users-table"
            row_index = await table_manager.find_row_by_key(
                table_locator=table_locator,
                key_column=2,  # Email column
                key_value="john.doe@example.com"
            )
            
            assert row_index >= 0, "User not found in table"
            
            # Read data from the found row
            user_id = await table_manager.get_cell_value(table_locator, row_index, 0)
            name = await table_manager.get_cell_value(table_locator, row_index, 1)
            email = await table_manager.get_cell_value(table_locator, row_index, 2)
            role = await table_manager.get_cell_value(table_locator, row_index, 3)
            status = await table_manager.get_cell_value(table_locator, row_index, 4)
            
            # Verify data
            assert email == "john.doe@example.com"
            assert name == "John Doe"
            assert role in ["Admin", "User", "Manager"]
            assert status in ["Active", "Inactive"]
            
            print(f"Found user: ID={user_id}, Name={name}, Role={role}, Status={status}")
            
        finally:
            await browser_manager.close_browser()
    
    async def test_edit_table_cell(self):
        """
        Test editing a cell in a table
        
        This example shows:
        1. Locating a specific cell
        2. Editing the cell value
        3. Verifying the change was saved
        """
        config = ConfigManager()
        browser_manager = BrowserManager(config)
        
        try:
            browser = await browser_manager.launch_browser("chromium", headless=True)
            context = await browser_manager.create_context()
            page = await browser_manager.create_page(context)
            
            element_manager = ElementManager(page, config)
            base_page = BasePage(page, element_manager)
            table_manager = TableManager(page, element_manager)
            
            # Navigate and login
            await base_page.navigate("https://example.com/login")
            await element_manager.fill("css=#username", "admin@example.com")
            await element_manager.fill("css=#password", "AdminPass123!")
            await element_manager.click("css=#login-button")
            
            # Navigate to users page
            await base_page.navigate("https://example.com/users")
            await element_manager.wait_for_element("css=#users-table", timeout=10000)
            
            # Find the user to edit
            table_locator = "css=#users-table"
            row_index = await table_manager.find_row_by_key(
                table_locator=table_locator,
                key_column=2,
                key_value="jane.smith@example.com"
            )
            
            assert row_index >= 0, "User not found"
            
            # Get current role
            current_role = await table_manager.get_cell_value(table_locator, row_index, 3)
            print(f"Current role: {current_role}")
            
            # Change role to "Manager"
            new_role = "Manager"
            await table_manager.set_cell_value(
                table_locator=table_locator,
                row=row_index,
                column=3,
                value=new_role
            )
            
            # Wait for save (assuming auto-save or click save button)
            await element_manager.click_if_exists("css=#save-button")
            await page.wait_for_timeout(1000)  # Wait for save to complete
            
            # Verify the change
            updated_role = await table_manager.get_cell_value(table_locator, row_index, 3)
            assert updated_role == new_role, f"Role not updated. Expected: {new_role}, Got: {updated_role}"
            
            print(f"Successfully updated role to: {updated_role}")
            
        finally:
            await browser_manager.close_browser()
    
    async def test_search_table(self):
        """
        Test searching within a table
        
        This example shows:
        1. Searching for text in table
        2. Case-insensitive search
        3. Partial match search
        4. Processing search results
        """
        config = ConfigManager()
        browser_manager = BrowserManager(config)
        
        try:
            browser = await browser_manager.launch_browser("chromium", headless=True)
            context = await browser_manager.create_context()
            page = await browser_manager.create_page(context)
            
            element_manager = ElementManager(page, config)
            base_page = BasePage(page, element_manager)
            table_manager = TableManager(page, element_manager)
            
            # Navigate to products page
            await base_page.navigate("https://example.com/products")
            await element_manager.wait_for_element("css=#products-table", timeout=10000)
            
            table_locator = "css=#products-table"
            
            # Search for products containing "laptop" (case-insensitive)
            matching_rows = await table_manager.search_table(
                table_locator=table_locator,
                search_text="laptop",
                case_sensitive=False
            )
            
            print(f"Found {len(matching_rows)} products matching 'laptop'")
            
            # Process each matching row
            for row_index in matching_rows:
                product_name = await table_manager.get_cell_value(table_locator, row_index, 1)
                price = await table_manager.get_cell_value(table_locator, row_index, 2)
                stock = await table_manager.get_cell_value(table_locator, row_index, 3)
                
                print(f"  - {product_name}: ${price} (Stock: {stock})")
                
                # Verify search term is in product name
                assert "laptop" in product_name.lower()
            
            assert len(matching_rows) > 0, "No products found matching search criteria"
            
        finally:
            await browser_manager.close_browser()
    
    async def test_table_pagination(self):
        """
        Test navigating through paginated table
        
        This example shows:
        1. Detecting pagination
        2. Navigating through pages
        3. Collecting data from multiple pages
        4. Handling last page
        """
        config = ConfigManager()
        browser_manager = BrowserManager(config)
        
        try:
            browser = await browser_manager.launch_browser("chromium", headless=True)
            context = await browser_manager.create_context()
            page = await browser_manager.create_page(context)
            
            element_manager = ElementManager(page, config)
            base_page = BasePage(page, element_manager)
            table_manager = TableManager(page, element_manager)
            
            # Navigate to orders page
            await base_page.navigate("https://example.com/orders")
            await element_manager.wait_for_element("css=#orders-table", timeout=10000)
            
            table_locator = "css=#orders-table"
            all_orders = []
            current_page = 1
            max_pages = 5  # Safety limit
            
            while current_page <= max_pages:
                print(f"Processing page {current_page}...")
                
                # Get row count on current page
                row_count = await table_manager.get_row_count(table_locator)
                print(f"  Found {row_count} rows on page {current_page}")
                
                # Collect data from current page
                for row_index in range(row_count):
                    order_id = await table_manager.get_cell_value(table_locator, row_index, 0)
                    customer = await table_manager.get_cell_value(table_locator, row_index, 1)
                    total = await table_manager.get_cell_value(table_locator, row_index, 2)
                    
                    all_orders.append({
                        "order_id": order_id,
                        "customer": customer,
                        "total": total
                    })
                
                # Check if there's a next page
                next_button_exists = await element_manager.is_visible("css=#next-page-button")
                next_button_enabled = await element_manager.is_enabled("css=#next-page-button")
                
                if not next_button_exists or not next_button_enabled:
                    print("Reached last page")
                    break
                
                # Navigate to next page
                await table_manager.navigate_pagination(
                    table_locator=table_locator,
                    direction="next"
                )
                
                # Wait for table to reload
                await page.wait_for_timeout(1000)
                current_page += 1
            
            print(f"\nCollected {len(all_orders)} total orders from {current_page} pages")
            assert len(all_orders) > 0, "No orders found"
            
            # Verify we collected data
            for order in all_orders[:5]:  # Print first 5
                print(f"  Order {order['order_id']}: {order['customer']} - ${order['total']}")
            
        finally:
            await browser_manager.close_browser()
    
    async def test_bulk_table_operations(self):
        """
        Test performing bulk operations on table data
        
        This example shows:
        1. Selecting multiple rows
        2. Performing bulk actions
        3. Verifying bulk changes
        """
        config = ConfigManager()
        browser_manager = BrowserManager(config)
        
        try:
            browser = await browser_manager.launch_browser("chromium", headless=True)
            context = await browser_manager.create_context()
            page = await browser_manager.create_page(context)
            
            element_manager = ElementManager(page, config)
            base_page = BasePage(page, element_manager)
            table_manager = TableManager(page, element_manager)
            
            # Navigate to users page
            await base_page.navigate("https://example.com/users")
            await element_manager.wait_for_element("css=#users-table", timeout=10000)
            
            table_locator = "css=#users-table"
            
            # Find all inactive users
            inactive_rows = await table_manager.search_table(
                table_locator=table_locator,
                search_text="Inactive",
                case_sensitive=False
            )
            
            print(f"Found {len(inactive_rows)} inactive users")
            
            # Select all inactive users (click checkbox in first column)
            for row_index in inactive_rows:
                await table_manager.click_cell(
                    table_locator=table_locator,
                    row=row_index,
                    column=0  # Checkbox column
                )
            
            # Click bulk activate button
            await element_manager.click("css=#bulk-activate-button")
            
            # Wait for confirmation dialog
            await element_manager.wait_for_element("css=.confirmation-dialog", timeout=5000)
            await element_manager.click("css=#confirm-button")
            
            # Wait for operation to complete
            await element_manager.wait_for_element("css=.success-message", timeout=10000)
            
            # Verify users are now active
            await page.reload()
            await element_manager.wait_for_element(table_locator, timeout=10000)
            
            # Check that previously inactive users are now active
            for row_index in inactive_rows:
                status = await table_manager.get_cell_value(table_locator, row_index, 4)
                assert status == "Active", f"Row {row_index} not activated"
            
            print(f"Successfully activated {len(inactive_rows)} users")
            
        finally:
            await browser_manager.close_browser()
    
    async def test_table_sorting_and_filtering(self):
        """
        Test table sorting and filtering operations
        
        This example shows:
        1. Sorting table by column
        2. Applying filters
        3. Verifying sort order
        4. Combining multiple filters
        """
        config = ConfigManager()
        browser_manager = BrowserManager(config)
        
        try:
            browser = await browser_manager.launch_browser("chromium", headless=True)
            context = await browser_manager.create_context()
            page = await browser_manager.create_page(context)
            
            element_manager = ElementManager(page, config)
            base_page = BasePage(page, element_manager)
            table_manager = TableManager(page, element_manager)
            
            # Navigate to products page
            await base_page.navigate("https://example.com/products")
            await element_manager.wait_for_element("css=#products-table", timeout=10000)
            
            table_locator = "css=#products-table"
            
            # Sort by price (column 2) - ascending
            await element_manager.click("css=#products-table th:nth-child(3)")  # Price column header
            await page.wait_for_timeout(1000)  # Wait for sort
            
            # Verify sort order
            row_count = await table_manager.get_row_count(table_locator)
            previous_price = 0.0
            
            for row_index in range(min(5, row_count)):  # Check first 5 rows
                price_text = await table_manager.get_cell_value(table_locator, row_index, 2)
                price = float(price_text.replace("$", "").replace(",", ""))
                
                assert price >= previous_price, f"Table not sorted correctly at row {row_index}"
                previous_price = price
                print(f"Row {row_index}: ${price}")
            
            # Apply filter for category
            await element_manager.click("css=#category-filter")
            await element_manager.select_option("css=#category-filter", "Electronics")
            await page.wait_for_timeout(1000)  # Wait for filter
            
            # Verify all visible products are in Electronics category
            filtered_row_count = await table_manager.get_row_count(table_locator)
            for row_index in range(filtered_row_count):
                category = await table_manager.get_cell_value(table_locator, row_index, 3)
                assert category == "Electronics", f"Filter not applied correctly at row {row_index}"
            
            print(f"Filter applied successfully. Showing {filtered_row_count} Electronics products")
            
        finally:
            await browser_manager.close_browser()


if __name__ == "__main__":
    """
    Run this example directly:
    python examples/test_example_table_interaction.py
    
    Or with pytest:
    pytest examples/test_example_table_interaction.py -v
    """
    pytest.main([__file__, "-v", "-s"])
