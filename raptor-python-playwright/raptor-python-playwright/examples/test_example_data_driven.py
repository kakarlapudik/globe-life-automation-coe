"""
Example Data-Driven Test

This example demonstrates data-driven testing using the RAPTOR framework with DDDB.
It shows how to:
- Load test data from database
- Parametrize tests with multiple data sets
- Execute iterations with different data
- Export results back to database

Requirements: NFR-004, Requirements 4.1, 4.2, 4.3
"""

import pytest
from raptor.core.browser_manager import BrowserManager
from raptor.core.element_manager import ElementManager
from raptor.core.config_manager import ConfigManager
from raptor.database.database_manager import DatabaseManager
from raptor.pages.base_page import BasePage
from raptor.utils.data_driven import load_test_data_from_db, parametrize_from_db


@pytest.mark.asyncio
class TestDataDrivenExample:
    """Example test class demonstrating data-driven testing"""
    
    async def test_user_registration_with_database_data(self):
        """
        Test user registration using data from DDDB
        
        This example shows:
        1. Loading test data from database
        2. Using data to fill forms
        3. Exporting results back to database
        """
        config = ConfigManager()
        browser_manager = BrowserManager(config)
        db_manager = DatabaseManager(
            connection_string=config.get("database.connection_string"),
            user=config.get("database.user"),
            password=config.get("database.password")
        )
        
        try:
            # Connect to database
            await db_manager.connect()
            
            # Load test data for test_id=1001, iteration=1, instance=1
            test_data = await db_manager.import_data(
                table="UserRegistrationData",
                test_id=1001,
                iteration=1,
                instance=1
            )
            
            # Launch browser
            browser = await browser_manager.launch_browser("chromium", headless=True)
            context = await browser_manager.create_context()
            page = await browser_manager.create_page(context)
            
            element_manager = ElementManager(page, config)
            base_page = BasePage(page, element_manager)
            
            # Navigate to registration page
            await base_page.navigate("https://example.com/register")
            
            # Fill form with database data
            await element_manager.fill("css=#first-name", test_data.get("first_name", ""))
            await element_manager.fill("css=#last-name", test_data.get("last_name", ""))
            await element_manager.fill("css=#email", test_data.get("email", ""))
            await element_manager.fill("css=#phone", test_data.get("phone", ""))
            await element_manager.fill("css=#password", test_data.get("password", ""))
            await element_manager.fill("css=#confirm-password", test_data.get("password", ""))
            
            # Submit registration
            await element_manager.click("css=#register-button")
            
            # Wait for confirmation
            await element_manager.wait_for_element("css=.success-message", timeout=10000)
            
            # Verify success
            success_message = await element_manager.get_text("css=.success-message")
            test_passed = "successfully registered" in success_message.lower()
            
            # Export result back to database
            await db_manager.export_data(
                table="UserRegistrationData",
                pk_id=test_data.get("pk_id"),
                field="test_result",
                value="PASS" if test_passed else "FAIL"
            )
            
            await db_manager.export_data(
                table="UserRegistrationData",
                pk_id=test_data.get("pk_id"),
                field="result_message",
                value=success_message
            )
            
            assert test_passed, f"Registration failed: {success_message}"
            
        finally:
            await db_manager.disconnect()
            await browser_manager.close_browser()
    
    async def test_multiple_iterations_from_database(self):
        """
        Test multiple user registrations using different iterations
        
        This example shows:
        1. Loading multiple iterations of test data
        2. Running the same test with different data sets
        3. Collecting results for all iterations
        """
        config = ConfigManager()
        browser_manager = BrowserManager(config)
        db_manager = DatabaseManager(
            connection_string=config.get("database.connection_string"),
            user=config.get("database.user"),
            password=config.get("database.password")
        )
        
        try:
            await db_manager.connect()
            
            # Test with 3 different iterations
            for iteration in range(1, 4):
                print(f"\n=== Running iteration {iteration} ===")
                
                # Load data for this iteration
                test_data = await db_manager.import_data(
                    table="UserRegistrationData",
                    test_id=1001,
                    iteration=iteration,
                    instance=1
                )
                
                # Launch browser for this iteration
                browser = await browser_manager.launch_browser("chromium", headless=True)
                context = await browser_manager.create_context()
                page = await browser_manager.create_page(context)
                
                element_manager = ElementManager(page, config)
                base_page = BasePage(page, element_manager)
                
                # Navigate and fill form
                await base_page.navigate("https://example.com/register")
                await element_manager.fill("css=#email", test_data.get("email", ""))
                await element_manager.fill("css=#password", test_data.get("password", ""))
                await element_manager.click("css=#register-button")
                
                # Check result
                try:
                    await element_manager.wait_for_element("css=.success-message", timeout=5000)
                    result = "PASS"
                    message = await element_manager.get_text("css=.success-message")
                except Exception as e:
                    result = "FAIL"
                    message = str(e)
                
                # Export result
                await db_manager.export_data(
                    table="UserRegistrationData",
                    pk_id=test_data.get("pk_id"),
                    field="test_result",
                    value=result
                )
                
                print(f"Iteration {iteration}: {result} - {message}")
                
                # Close browser for this iteration
                await browser_manager.close_browser()
            
        finally:
            await db_manager.disconnect()


@pytest.mark.asyncio
@pytest.mark.parametrize("test_id,iteration,instance", [
    (1001, 1, 1),
    (1001, 2, 1),
    (1001, 3, 1),
    (1002, 1, 1),
    (1002, 2, 1),
])
async def test_parametrized_login(test_id, iteration, instance):
    """
    Parametrized test using pytest parametrize with database data
    
    This example shows:
    1. Using pytest.mark.parametrize with database identifiers
    2. Running same test with multiple parameter combinations
    3. Efficient test execution with different data sets
    """
    config = ConfigManager()
    browser_manager = BrowserManager(config)
    db_manager = DatabaseManager(
        connection_string=config.get("database.connection_string"),
        user=config.get("database.user"),
        password=config.get("database.password")
    )
    
    try:
        await db_manager.connect()
        
        # Load specific test data
        test_data = await db_manager.import_data(
            table="LoginTestData",
            test_id=test_id,
            iteration=iteration,
            instance=instance
        )
        
        # Launch browser
        browser = await browser_manager.launch_browser("chromium", headless=True)
        context = await browser_manager.create_context()
        page = await browser_manager.create_page(context)
        
        element_manager = ElementManager(page, config)
        base_page = BasePage(page, element_manager)
        
        # Execute login test
        await base_page.navigate("https://example.com/login")
        await element_manager.fill("css=#username", test_data.get("username", ""))
        await element_manager.fill("css=#password", test_data.get("password", ""))
        await element_manager.click("css=#login-button")
        
        # Verify expected result
        expected_result = test_data.get("expected_result", "success")
        
        if expected_result == "success":
            await page.wait_for_url("**/dashboard", timeout=10000)
            assert "/dashboard" in await base_page.get_url()
            result = "PASS"
        else:
            # Expect error message
            await element_manager.wait_for_element("css=.error-message", timeout=5000)
            assert await element_manager.is_visible("css=.error-message")
            result = "PASS"  # Test passed because we expected failure
        
        # Export result
        await db_manager.export_data(
            table="LoginTestData",
            pk_id=test_data.get("pk_id"),
            field="test_result",
            value=result
        )
        
    finally:
        await db_manager.disconnect()
        await browser_manager.close_browser()


@pytest.mark.asyncio
async def test_complex_data_driven_workflow():
    """
    Complex data-driven test with multiple tables and relationships
    
    This example shows:
    1. Loading data from multiple related tables
    2. Using foreign keys to link data
    3. Complex workflow with multiple steps
    """
    config = ConfigManager()
    browser_manager = BrowserManager(config)
    db_manager = DatabaseManager(
        connection_string=config.get("database.connection_string"),
        user=config.get("database.user"),
        password=config.get("database.password")
    )
    
    try:
        await db_manager.connect()
        
        # Load main test data
        main_data = await db_manager.import_data(
            table="OrderTestData",
            test_id=2001,
            iteration=1,
            instance=1
        )
        
        # Load related product data using foreign key
        fk_id = main_data.get("fk_product_id")
        product_data = await db_manager.execute_query(
            f"SELECT * FROM ProductData WHERE pk_id = {fk_id}"
        )
        
        # Launch browser
        browser = await browser_manager.launch_browser("chromium", headless=True)
        context = await browser_manager.create_context()
        page = await browser_manager.create_page(context)
        
        element_manager = ElementManager(page, config)
        base_page = BasePage(page, element_manager)
        
        # Step 1: Login
        await base_page.navigate("https://example.com/login")
        await element_manager.fill("css=#username", main_data.get("username", ""))
        await element_manager.fill("css=#password", main_data.get("password", ""))
        await element_manager.click("css=#login-button")
        await page.wait_for_url("**/dashboard", timeout=10000)
        
        # Step 2: Search for product
        await base_page.navigate("https://example.com/products")
        await element_manager.fill("css=#search", product_data[0].get("product_name", ""))
        await element_manager.click("css=#search-button")
        
        # Step 3: Add to cart
        await element_manager.wait_for_element("css=.product-item", timeout=5000)
        await element_manager.click("css=.add-to-cart-button")
        
        # Step 4: Checkout
        await element_manager.click("css=#cart-icon")
        await element_manager.click("css=#checkout-button")
        
        # Step 5: Fill shipping info
        await element_manager.fill("css=#shipping-address", main_data.get("address", ""))
        await element_manager.fill("css=#city", main_data.get("city", ""))
        await element_manager.fill("css=#zip", main_data.get("zip", ""))
        
        # Step 6: Complete order
        await element_manager.click("css=#place-order-button")
        
        # Verify order confirmation
        await element_manager.wait_for_element("css=.order-confirmation", timeout=10000)
        order_number = await element_manager.get_text("css=.order-number")
        
        # Export results
        await db_manager.export_data(
            table="OrderTestData",
            pk_id=main_data.get("pk_id"),
            field="test_result",
            value="PASS"
        )
        
        await db_manager.export_data(
            table="OrderTestData",
            pk_id=main_data.get("pk_id"),
            field="order_number",
            value=order_number
        )
        
        assert order_number, "Order number not found"
        
    finally:
        await db_manager.disconnect()
        await browser_manager.close_browser()


if __name__ == "__main__":
    """
    Run this example directly:
    python examples/test_example_data_driven.py
    
    Or with pytest:
    pytest examples/test_example_data_driven.py -v
    """
    pytest.main([__file__, "-v", "-s"])
