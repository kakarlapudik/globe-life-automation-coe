"""
Example Multi-Page Workflow Test

This example demonstrates complex multi-page workflows using the RAPTOR framework.
It shows how to:
- Navigate through multiple pages
- Maintain state across pages
- Handle complex user journeys
- Coordinate multiple page objects
- Verify end-to-end workflows

Requirements: NFR-004
"""

import pytest
from raptor.core.browser_manager import BrowserManager
from raptor.core.element_manager import ElementManager
from raptor.core.config_manager import ConfigManager
from raptor.pages.base_page import BasePage
from raptor.pages.table_manager import TableManager
from raptor.utils.reporter import TestReporter


@pytest.mark.asyncio
class TestMultiPageWorkflowExample:
    """Example test class demonstrating multi-page workflows"""
    
    async def test_complete_ecommerce_purchase_workflow(self):
        """
        Test complete e-commerce purchase from login to order confirmation
        
        This example shows:
        1. Multi-step workflow across multiple pages
        2. State management between pages
        3. Form filling and validation
        4. Shopping cart operations
        5. Checkout process
        """
        config = ConfigManager()
        browser_manager = BrowserManager(config)
        reporter = TestReporter(config)
        
        try:
            # Initialize browser
            browser = await browser_manager.launch_browser("chromium", headless=True)
            context = await browser_manager.create_context()
            page = await browser_manager.create_page(context)
            
            element_manager = ElementManager(page, config)
            base_page = BasePage(page, element_manager)
            
            reporter.start_test("Complete E-commerce Purchase")
            
            # Step 1: Login
            print("\n=== Step 1: Login ===")
            await base_page.navigate("https://example.com/login")
            await element_manager.fill("css=#username", "customer@example.com")
            await element_manager.fill("css=#password", "CustomerPass123!")
            await element_manager.click("css=#login-button")
            await page.wait_for_url("**/dashboard", timeout=10000)
            await base_page.take_screenshot("01_login_success")
            reporter.log_step("Login successful")
            
            # Step 2: Browse products
            print("\n=== Step 2: Browse Products ===")
            await base_page.navigate("https://example.com/products")
            await element_manager.wait_for_element("css=.product-grid", timeout=10000)
            
            # Search for specific product
            await element_manager.fill("css=#search-box", "Wireless Mouse")
            await element_manager.click("css=#search-button")
            await page.wait_for_timeout(1000)
            await base_page.take_screenshot("02_product_search")
            reporter.log_step("Product search completed")
            
            # Step 3: View product details
            print("\n=== Step 3: View Product Details ===")
            await element_manager.click("css=.product-card:first-child")
            await element_manager.wait_for_element("css=.product-details", timeout=5000)
            
            # Get product information
            product_name = await element_manager.get_text("css=.product-name")
            product_price = await element_manager.get_text("css=.product-price")
            print(f"Product: {product_name}, Price: {product_price}")
            await base_page.take_screenshot("03_product_details")
            reporter.log_step(f"Viewing product: {product_name}")
            
            # Step 4: Add to cart
            print("\n=== Step 4: Add to Cart ===")
            await element_manager.select_option("css=#quantity", "2")
            await element_manager.click("css=#add-to-cart-button")
            
            # Wait for cart notification
            await element_manager.wait_for_element("css=.cart-notification", timeout=5000)
            cart_message = await element_manager.get_text("css=.cart-notification")
            assert "added to cart" in cart_message.lower()
            await base_page.take_screenshot("04_added_to_cart")
            reporter.log_step("Product added to cart")
            
            # Step 5: View cart
            print("\n=== Step 5: View Cart ===")
            await element_manager.click("css=#cart-icon")
            await page.wait_for_url("**/cart", timeout=10000)
            await element_manager.wait_for_element("css=.cart-items", timeout=5000)
            
            # Verify cart contents
            cart_items = await page.locator("css=.cart-item").count()
            assert cart_items > 0, "Cart is empty"
            
            cart_total = await element_manager.get_text("css=.cart-total")
            print(f"Cart total: {cart_total}")
            await base_page.take_screenshot("05_cart_view")
            reporter.log_step(f"Cart contains {cart_items} item(s)")
            
            # Step 6: Proceed to checkout
            print("\n=== Step 6: Checkout - Shipping Info ===")
            await element_manager.click("css=#checkout-button")
            await page.wait_for_url("**/checkout", timeout=10000)
            
            # Fill shipping information
            await element_manager.fill("css=#shipping-first-name", "John")
            await element_manager.fill("css=#shipping-last-name", "Doe")
            await element_manager.fill("css=#shipping-address", "123 Main Street")
            await element_manager.fill("css=#shipping-city", "Springfield")
            await element_manager.select_option("css=#shipping-state", "IL")
            await element_manager.fill("css=#shipping-zip", "62701")
            await element_manager.fill("css=#shipping-phone", "555-123-4567")
            await base_page.take_screenshot("06_shipping_info")
            reporter.log_step("Shipping information entered")
            
            # Continue to payment
            await element_manager.click("css=#continue-to-payment")
            await page.wait_for_timeout(1000)
            
            # Step 7: Payment information
            print("\n=== Step 7: Checkout - Payment Info ===")
            await element_manager.wait_for_element("css=#payment-section", timeout=5000)
            
            # Fill payment information
            await element_manager.fill("css=#card-number", "4111111111111111")
            await element_manager.fill("css=#card-name", "John Doe")
            await element_manager.select_option("css=#card-expiry-month", "12")
            await element_manager.select_option("css=#card-expiry-year", "2025")
            await element_manager.fill("css=#card-cvv", "123")
            await base_page.take_screenshot("07_payment_info")
            reporter.log_step("Payment information entered")
            
            # Step 8: Review order
            print("\n=== Step 8: Review Order ===")
            await element_manager.click("css=#review-order-button")
            await page.wait_for_timeout(1000)
            await element_manager.wait_for_element("css=#order-summary", timeout=5000)
            
            # Verify order summary
            summary_product = await element_manager.get_text("css=.summary-product-name")
            summary_total = await element_manager.get_text("css=.summary-total")
            assert product_name in summary_product
            await base_page.take_screenshot("08_order_review")
            reporter.log_step("Order reviewed")
            
            # Step 9: Place order
            print("\n=== Step 9: Place Order ===")
            await element_manager.click("css=#place-order-button")
            
            # Wait for order confirmation
            await page.wait_for_url("**/order-confirmation", timeout=15000)
            await element_manager.wait_for_element("css=.order-confirmation", timeout=10000)
            
            # Get order details
            order_number = await element_manager.get_text("css=.order-number")
            confirmation_message = await element_manager.get_text("css=.confirmation-message")
            
            assert order_number, "Order number not found"
            assert "thank you" in confirmation_message.lower()
            
            print(f"\nOrder placed successfully!")
            print(f"Order Number: {order_number}")
            print(f"Message: {confirmation_message}")
            
            await base_page.take_screenshot("09_order_confirmation")
            reporter.log_step(f"Order placed: {order_number}")
            
            # Step 10: Verify order in account
            print("\n=== Step 10: Verify Order in Account ===")
            await base_page.navigate("https://example.com/account/orders")
            await element_manager.wait_for_element("css=#orders-table", timeout=10000)
            
            table_manager = TableManager(page, element_manager)
            
            # Find the order in the table
            row_index = await table_manager.find_row_by_key(
                table_locator="css=#orders-table",
                key_column=0,  # Order number column
                key_value=order_number
            )
            
            assert row_index >= 0, f"Order {order_number} not found in order history"
            
            order_status = await table_manager.get_cell_value("css=#orders-table", row_index, 2)
            print(f"Order status: {order_status}")
            
            await base_page.take_screenshot("10_order_history")
            reporter.log_step("Order verified in account history")
            
            # Generate test report
            reporter.end_test("PASS")
            report_path = await reporter.generate_html_report()
            print(f"\nTest report generated: {report_path}")
            
        finally:
            await browser_manager.close_browser()
    
    async def test_user_profile_management_workflow(self):
        """
        Test user profile management across multiple pages
        
        This example shows:
        1. Profile viewing and editing
        2. Password change workflow
        3. Preference updates
        4. Verification across pages
        """
        config = ConfigManager()
        browser_manager = BrowserManager(config)
        
        try:
            browser = await browser_manager.launch_browser("chromium", headless=True)
            context = await browser_manager.create_context()
            page = await browser_manager.create_page(context)
            
            element_manager = ElementManager(page, config)
            base_page = BasePage(page, element_manager)
            
            # Login
            print("\n=== Login ===")
            await base_page.navigate("https://example.com/login")
            await element_manager.fill("css=#username", "user@example.com")
            await element_manager.fill("css=#password", "UserPass123!")
            await element_manager.click("css=#login-button")
            await page.wait_for_url("**/dashboard", timeout=10000)
            
            # Navigate to profile
            print("\n=== View Profile ===")
            await element_manager.click("css=#user-menu")
            await element_manager.click("css=#profile-link")
            await page.wait_for_url("**/profile", timeout=10000)
            
            # Get current profile data
            current_name = await element_manager.get_value("css=#profile-name")
            current_email = await element_manager.get_value("css=#profile-email")
            print(f"Current profile: {current_name} ({current_email})")
            
            # Edit profile
            print("\n=== Edit Profile ===")
            await element_manager.click("css=#edit-profile-button")
            await element_manager.fill("css=#profile-name", "John Updated Doe")
            await element_manager.fill("css=#profile-phone", "555-999-8888")
            await element_manager.click("css=#save-profile-button")
            
            # Wait for success message
            await element_manager.wait_for_element("css=.success-message", timeout=5000)
            success_msg = await element_manager.get_text("css=.success-message")
            assert "updated" in success_msg.lower()
            
            # Change password
            print("\n=== Change Password ===")
            await element_manager.click("css=#security-tab")
            await element_manager.fill("css=#current-password", "UserPass123!")
            await element_manager.fill("css=#new-password", "NewUserPass456!")
            await element_manager.fill("css=#confirm-password", "NewUserPass456!")
            await element_manager.click("css=#change-password-button")
            
            await element_manager.wait_for_element("css=.password-success", timeout=5000)
            
            # Update preferences
            print("\n=== Update Preferences ===")
            await element_manager.click("css=#preferences-tab")
            await element_manager.click("css=#email-notifications")  # Toggle
            await element_manager.select_option("css=#language", "en-US")
            await element_manager.select_option("css=#timezone", "America/Chicago")
            await element_manager.click("css=#save-preferences-button")
            
            await element_manager.wait_for_element("css=.preferences-saved", timeout=5000)
            
            # Logout and login with new password
            print("\n=== Verify New Password ===")
            await element_manager.click("css=#user-menu")
            await element_manager.click("css=#logout-link")
            await page.wait_for_url("**/login", timeout=10000)
            
            # Login with new password
            await element_manager.fill("css=#username", "user@example.com")
            await element_manager.fill("css=#password", "NewUserPass456!")
            await element_manager.click("css=#login-button")
            await page.wait_for_url("**/dashboard", timeout=10000)
            
            print("Successfully logged in with new password")
            
            # Verify profile changes persisted
            await element_manager.click("css=#user-menu")
            await element_manager.click("css=#profile-link")
            await page.wait_for_url("**/profile", timeout=10000)
            
            updated_name = await element_manager.get_value("css=#profile-name")
            assert updated_name == "John Updated Doe"
            print(f"Profile changes verified: {updated_name}")
            
        finally:
            await browser_manager.close_browser()
    
    async def test_admin_user_management_workflow(self):
        """
        Test admin workflow for managing users
        
        This example shows:
        1. Admin dashboard navigation
        2. User creation workflow
        3. User search and edit
        4. Role assignment
        5. User deactivation
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
            
            # Admin login
            print("\n=== Admin Login ===")
            await base_page.navigate("https://example.com/admin/login")
            await element_manager.fill("css=#username", "admin@example.com")
            await element_manager.fill("css=#password", "AdminPass123!")
            await element_manager.click("css=#login-button")
            await page.wait_for_url("**/admin/dashboard", timeout=10000)
            
            # Navigate to user management
            print("\n=== Navigate to User Management ===")
            await element_manager.click("css=#users-menu")
            await page.wait_for_url("**/admin/users", timeout=10000)
            await element_manager.wait_for_element("css=#users-table", timeout=10000)
            
            # Create new user
            print("\n=== Create New User ===")
            await element_manager.click("css=#create-user-button")
            await element_manager.wait_for_element("css=#user-form", timeout=5000)
            
            new_user_email = f"newuser{int(page.evaluate('Date.now()'))}@example.com"
            await element_manager.fill("css=#user-first-name", "Test")
            await element_manager.fill("css=#user-last-name", "User")
            await element_manager.fill("css=#user-email", new_user_email)
            await element_manager.select_option("css=#user-role", "User")
            await element_manager.fill("css=#user-password", "TempPass123!")
            await element_manager.click("css=#save-user-button")
            
            await element_manager.wait_for_element("css=.user-created", timeout=5000)
            print(f"Created user: {new_user_email}")
            
            # Search for the new user
            print("\n=== Search for User ===")
            await element_manager.fill("css=#user-search", new_user_email)
            await element_manager.click("css=#search-button")
            await page.wait_for_timeout(1000)
            
            # Find user in table
            row_index = await table_manager.find_row_by_key(
                table_locator="css=#users-table",
                key_column=2,  # Email column
                key_value=new_user_email
            )
            
            assert row_index >= 0, "Newly created user not found"
            
            # Edit user role
            print("\n=== Edit User Role ===")
            await table_manager.click_cell("css=#users-table", row_index, 5)  # Edit button column
            await element_manager.wait_for_element("css=#edit-user-form", timeout=5000)
            
            await element_manager.select_option("css=#user-role", "Manager")
            await element_manager.click("css=#update-user-button")
            await element_manager.wait_for_element("css=.user-updated", timeout=5000)
            
            # Verify role change
            await page.reload()
            await element_manager.wait_for_element("css=#users-table", timeout=10000)
            
            row_index = await table_manager.find_row_by_key(
                table_locator="css=#users-table",
                key_column=2,
                key_value=new_user_email
            )
            
            user_role = await table_manager.get_cell_value("css=#users-table", row_index, 3)
            assert user_role == "Manager", f"Role not updated. Expected: Manager, Got: {user_role}"
            print(f"User role updated to: {user_role}")
            
            # Deactivate user
            print("\n=== Deactivate User ===")
            await table_manager.click_cell("css=#users-table", row_index, 6)  # Deactivate button
            await element_manager.wait_for_element("css=.confirm-dialog", timeout=5000)
            await element_manager.click("css=#confirm-deactivate")
            await element_manager.wait_for_element("css=.user-deactivated", timeout=5000)
            
            # Verify deactivation
            await page.reload()
            await element_manager.wait_for_element("css=#users-table", timeout=10000)
            
            row_index = await table_manager.find_row_by_key(
                table_locator="css=#users-table",
                key_column=2,
                key_value=new_user_email
            )
            
            user_status = await table_manager.get_cell_value("css=#users-table", row_index, 4)
            assert user_status == "Inactive", f"User not deactivated. Status: {user_status}"
            print(f"User deactivated successfully")
            
        finally:
            await browser_manager.close_browser()


if __name__ == "__main__":
    """
    Run this example directly:
    python examples/test_example_multi_page_workflow.py
    
    Or with pytest:
    pytest examples/test_example_multi_page_workflow.py -v
    """
    pytest.main([__file__, "-v", "-s"])
