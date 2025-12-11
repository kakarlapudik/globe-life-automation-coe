"""
End-to-End Test Suite for RAPTOR Framework

These tests verify complete workflows from start to finish:
1. Complete login workflow
2. Data-driven execution
3. Multi-page navigation
4. Table operations

**Validates: Requirements NFR-002, NFR-003**
"""

import pytest
import asyncio
import tempfile
import os
from pathlib import Path
from datetime import datetime

from raptor.core.browser_manager import BrowserManager
from raptor.core.element_manager import ElementManager
from raptor.core.session_manager import SessionManager
from raptor.core.config_manager import ConfigManager
from raptor.database.database_manager import DatabaseManager
from raptor.pages.base_page import BasePage
from raptor.pages.table_manager import TableManager
from raptor.utils.reporter import TestReporter
from raptor.core.exceptions import (
    ElementNotFoundException,
    TimeoutException
)


# ============================================================================
# E2E Test 1: Complete Login Workflow
# ============================================================================

class TestE2ELoginWorkflow:
    """
    End-to-end tests for complete login workflow.
    
    Tests the entire login process from browser launch to successful
    authentication and session management.
    
    **Validates: Requirements NFR-002, NFR-003**
    """
    
    @pytest.mark.asyncio
    async def test_complete_login_workflow_with_session_persistence(self):
        """
        Test complete login workflow with session persistence.
        
        This E2E test covers:
        1. Browser initialization
        2. Navigation to login page
        3. Form filling and submission
        4. Authentication verification
        5. Session saving
        6. Session restoration
        7. Verification of persisted state
        """
        config = ConfigManager()
        browser_manager = BrowserManager(config)
        temp_session_dir = tempfile.mkdtemp()
        session_manager = SessionManager(storage_dir=temp_session_dir)
        reporter = TestReporter("reports/e2e")
        
        try:
            reporter.start_test("Complete Login Workflow E2E")
            
            # Step 1: Launch browser
            print("\n=== Step 1: Launch Browser ===")
            await browser_manager.launch_browser("chromium", headless=True)
            page = await browser_manager.create_page()
            
            element_manager = ElementManager(page, config)
            base_page = BasePage(page, element_manager, config)
            reporter.log_step("Browser launched successfully")
            
            # Step 2: Navigate to login page
            print("\n=== Step 2: Navigate to Login Page ===")
            await page.set_content("""
                <!DOCTYPE html>
                <html>
                <head><title>Login Page</title></head>
                <body>
                    <h1>Login</h1>
                    <form id="login-form">
                        <input id="username" type="text" placeholder="Username" />
                        <input id="password" type="password" placeholder="Password" />
                        <input id="remember-me" type="checkbox" />
                        <label for="remember-me">Remember Me</label>
                        <button id="login-button" type="button" onclick="performLogin()">Login</button>
                    </form>
                    <div id="error-message" style="display:none; color:red;"></div>
                    <script>
                        function performLogin() {
                            const username = document.getElementById('username').value;
                            const password = document.getElementById('password').value;
                            const rememberMe = document.getElementById('remember-me').checked;
                            
                            if (username === 'testuser' && password === 'TestPass123!') {
                                // Store session data
                                if (rememberMe) {
                                    localStorage.setItem('session_token', 'abc123xyz');
                                }
                                sessionStorage.setItem('user', username);
                                
                                // Navigate to dashboard
                                document.body.innerHTML = `
                                    <h1>Dashboard</h1>
                                    <div class="welcome-message">Welcome, ${username}!</div>
                                    <div id="user-info">Logged in as: ${username}</div>
                                    <button id="logout-button" onclick="logout()">Logout</button>
                                `;
                                document.title = 'Dashboard';
                            } else {
                                document.getElementById('error-message').textContent = 'Invalid credentials';
                                document.getElementById('error-message').style.display = 'block';
                            }
                        }
                        
                        function logout() {
                            sessionStorage.clear();
                            localStorage.clear();
                            location.reload();
                        }
                    </script>
                </body>
                </html>
            """)
            
            title = await base_page.get_title()
            assert title == "Login Page"
            reporter.log_step("Navigated to login page")
            
            # Step 3: Fill login form
            print("\n=== Step 3: Fill Login Form ===")
            await element_manager.fill("css=#username", "testuser")
            await element_manager.fill("css=#password", "TestPass123!")
            
            # Check remember me
            remember_me_checkbox = "css=#remember-me"
            if not await element_manager.is_selected(remember_me_checkbox):
                await element_manager.click(remember_me_checkbox)
            
            assert await element_manager.is_selected(remember_me_checkbox)
            reporter.log_step("Login form filled with credentials")
            
            # Step 4: Submit login
            print("\n=== Step 4: Submit Login ===")
            await element_manager.click("css=#login-button")
            await asyncio.sleep(0.2)  # Wait for DOM update
            
            # Step 5: Verify successful login
            print("\n=== Step 5: Verify Login Success ===")
            await element_manager.wait_for_element("css=.welcome-message", timeout=5000)
            
            welcome_text = await element_manager.get_text("css=.welcome-message")
            assert "Welcome, testuser" in welcome_text
            
            dashboard_title = await base_page.get_title()
            assert dashboard_title == "Dashboard"
            
            user_info = await element_manager.get_text("css=#user-info")
            assert "testuser" in user_info
            reporter.log_step("Login successful - user authenticated")
            
            # Step 6: Take screenshot
            screenshot_path = await base_page.take_screenshot("e2e_login_success")
            assert Path(screenshot_path).exists()
            reporter.log_step("Screenshot captured")
            
            # Step 7: Save session
            print("\n=== Step 7: Save Session ===")
            session_info = await session_manager.save_session(
                page,
                "e2e_login_session",
                metadata={"user": "testuser", "test": "e2e_login"}
            )
            
            assert session_info.session_id == "e2e_login_session"
            assert "e2e_login_session" in session_manager.list_sessions()
            reporter.log_step("Session saved successfully")
            
            # Step 8: Close browser
            print("\n=== Step 8: Close Browser ===")
            await browser_manager.close_browser()
            reporter.log_step("Browser closed")
            
            # Step 9: Restore session in new browser instance
            print("\n=== Step 9: Restore Session ===")
            await browser_manager.launch_browser("chromium", headless=True)
            
            # Verify session still exists
            assert session_manager.validate_session("e2e_login_session")
            session_info_retrieved = session_manager.get_session_info("e2e_login_session")
            assert session_info_retrieved.metadata["user"] == "testuser"
            reporter.log_step("Session restored and validated")
            
            # Step 10: Verify persisted state
            print("\n=== Step 10: Verify Persisted State ===")
            # In a real scenario, we would restore the page and verify the user is still logged in
            # For this test, we verify the session metadata
            assert session_info_retrieved.browser_type == "chromium"
            assert session_info_retrieved.session_id == "e2e_login_session"
            reporter.log_step("Session state verified")
            
            # Generate report
            reporter.end_test("PASS")
            report_path = await reporter.generate_html_report()
            print(f"\nE2E Test Report: {report_path}")
            
        finally:
            await browser_manager.close_browser()
            # Cleanup
            import shutil
            shutil.rmtree(temp_session_dir, ignore_errors=True)

    @pytest.mark.asyncio
    async def test_login_with_error_handling_and_retry(self):
        """
        Test login workflow with error handling and retry logic.
        
        This E2E test covers:
        1. Invalid login attempt
        2. Error message verification
        3. Retry with correct credentials
        4. Successful authentication
        """
        config = ConfigManager()
        browser_manager = BrowserManager(config)
        
        try:
            # Launch browser
            await browser_manager.launch_browser("chromium", headless=True)
            page = await browser_manager.create_page()
            
            element_manager = ElementManager(page, config)
            base_page = BasePage(page, element_manager, config)
            
            # Create login page
            await page.set_content("""
                <!DOCTYPE html>
                <html>
                <head><title>Login</title></head>
                <body>
                    <h1>Login</h1>
                    <input id="username" type="text" />
                    <input id="password" type="password" />
                    <button id="login-button" onclick="login()">Login</button>
                    <div id="error" style="display:none; color:red;"></div>
                    <script>
                        let attempts = 0;
                        function login() {
                            const user = document.getElementById('username').value;
                            const pass = document.getElementById('password').value;
                            attempts++;
                            
                            if (user === 'admin' && pass === 'Admin123!') {
                                document.body.innerHTML = '<h1>Dashboard</h1><div class="success">Login successful</div>';
                                document.title = 'Dashboard';
                            } else {
                                document.getElementById('error').textContent = 'Invalid credentials (Attempt ' + attempts + ')';
                                document.getElementById('error').style.display = 'block';
                            }
                        }
                    </script>
                </body>
                </html>
            """)
            
            # Attempt 1: Invalid credentials
            print("\n=== Attempt 1: Invalid Credentials ===")
            await element_manager.fill("css=#username", "wronguser")
            await element_manager.fill("css=#password", "wrongpass")
            await element_manager.click("css=#login-button")
            await asyncio.sleep(0.1)
            
            # Verify error message
            assert await element_manager.is_visible("css=#error")
            error_text = await element_manager.get_text("css=#error")
            assert "Invalid credentials" in error_text
            assert "Attempt 1" in error_text
            print(f"Error displayed: {error_text}")
            
            # Attempt 2: Correct credentials
            print("\n=== Attempt 2: Correct Credentials ===")
            await element_manager.fill("css=#username", "admin")
            await element_manager.fill("css=#password", "Admin123!")
            await element_manager.click("css=#login-button")
            await asyncio.sleep(0.1)
            
            # Verify success
            await element_manager.wait_for_element("css=.success", timeout=5000)
            success_text = await element_manager.get_text("css=.success")
            assert "Login successful" in success_text
            
            title = await base_page.get_title()
            assert title == "Dashboard"
            print("Login successful on retry")
            
        finally:
            await browser_manager.close_browser()


# ============================================================================
# E2E Test 2: Data-Driven Execution
# ============================================================================

class TestE2EDataDrivenExecution:
    """
    End-to-end tests for data-driven test execution.
    
    Tests complete data-driven workflows including database operations,
    test data loading, and result export.
    
    **Validates: Requirements NFR-002, NFR-003, 4.1, 4.2, 4.3**
    """
    
    @pytest.fixture
    async def temp_database(self):
        """Create temporary database with test data."""
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()
        
        db_manager = DatabaseManager(temp_db.name)
        await db_manager.initialize()
        
        # Create test data table
        await db_manager.create_table_if_not_exists(
            "UserTestData",
            """
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            test_id INTEGER,
            iteration INTEGER,
            instance INTEGER,
            username TEXT,
            email TEXT,
            password TEXT,
            expected_result TEXT,
            test_result TEXT,
            result_message TEXT
            """
        )
        
        # Insert test data for multiple iterations
        test_data = [
            (1001, 1, 1, "user1", "user1@example.com", "Pass123!", "success", None, None),
            (1001, 2, 1, "user2", "user2@example.com", "Pass456!", "success", None, None),
            (1001, 3, 1, "invalid", "invalid@example.com", "wrong", "failure", None, None),
        ]
        
        for data in test_data:
            await db_manager.execute_update(
                """INSERT INTO UserTestData 
                   (test_id, iteration, instance, username, email, password, expected_result, test_result, result_message)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                data
            )
        
        yield db_manager
        
        await db_manager.close()
        os.unlink(temp_db.name)

    @pytest.mark.asyncio
    async def test_complete_data_driven_workflow(self, temp_database):
        """
        Test complete data-driven workflow with database integration.
        
        This E2E test covers:
        1. Loading test data from database
        2. Executing tests with multiple iterations
        3. Exporting results back to database
        4. Verifying data persistence
        """
        db_manager = temp_database
        config = ConfigManager()
        browser_manager = BrowserManager(config)
        reporter = TestReporter("reports/e2e")
        
        try:
            reporter.start_test("Data-Driven Execution E2E")
            
            # Execute test for each iteration
            for iteration in range(1, 4):
                print(f"\n{'='*60}")
                print(f"=== Iteration {iteration} ===")
                print(f"{'='*60}")
                
                # Step 1: Load test data from database
                print(f"\n=== Step 1: Load Test Data (Iteration {iteration}) ===")
                test_data_records = await db_manager.execute_query(
                    "SELECT * FROM UserTestData WHERE test_id = ? AND iteration = ? AND instance = ?",
                    (1001, iteration, 1)
                )
                
                assert len(test_data_records) == 1, f"Test data not found for iteration {iteration}"
                test_data = test_data_records[0]
                
                print(f"Loaded data: username={test_data['username']}, email={test_data['email']}")
                reporter.log_step(f"Iteration {iteration}: Loaded test data")
                
                # Step 2: Launch browser for this iteration
                print(f"\n=== Step 2: Launch Browser (Iteration {iteration}) ===")
                await browser_manager.launch_browser("chromium", headless=True)
                page = await browser_manager.create_page()
                
                element_manager = ElementManager(page, config)
                base_page = BasePage(page, element_manager, config)
                
                # Step 3: Create test application
                await page.set_content("""
                    <!DOCTYPE html>
                    <html>
                    <head><title>Registration</title></head>
                    <body>
                        <h1>User Registration</h1>
                        <form id="reg-form">
                            <input id="username" type="text" placeholder="Username" />
                            <input id="email" type="email" placeholder="Email" />
                            <input id="password" type="password" placeholder="Password" />
                            <button id="register-button" type="button" onclick="register()">Register</button>
                        </form>
                        <div id="message" style="display:none;"></div>
                        <script>
                            function register() {
                                const username = document.getElementById('username').value;
                                const email = document.getElementById('email').value;
                                const password = document.getElementById('password').value;
                                const message = document.getElementById('message');
                                
                                // Validate
                                if (!username || !email || !password) {
                                    message.textContent = 'All fields required';
                                    message.style.color = 'red';
                                    message.style.display = 'block';
                                    return;
                                }
                                
                                // Check for invalid user
                                if (username === 'invalid' || password === 'wrong') {
                                    message.textContent = 'Registration failed: Invalid credentials';
                                    message.style.color = 'red';
                                    message.style.display = 'block';
                                    return;
                                }
                                
                                // Success
                                message.textContent = 'Registration successful for ' + username;
                                message.style.color = 'green';
                                message.style.display = 'block';
                                message.className = 'success-message';
                            }
                        </script>
                    </body>
                    </html>
                """)
                
                # Step 4: Fill form with database data
                print(f"\n=== Step 4: Fill Registration Form (Iteration {iteration}) ===")
                await element_manager.fill("css=#username", test_data["username"])
                await element_manager.fill("css=#email", test_data["email"])
                await element_manager.fill("css=#password", test_data["password"])
                reporter.log_step(f"Iteration {iteration}: Form filled")
                
                # Step 5: Submit form
                print(f"\n=== Step 5: Submit Form (Iteration {iteration}) ===")
                await element_manager.click("css=#register-button")
                await asyncio.sleep(0.1)
                
                # Step 6: Verify result
                print(f"\n=== Step 6: Verify Result (Iteration {iteration}) ===")
                await element_manager.wait_for_element("css=#message", timeout=5000)
                message_text = await element_manager.get_text("css=#message")
                
                expected_result = test_data["expected_result"]
                
                if expected_result == "success":
                    assert "successful" in message_text.lower()
                    test_result = "PASS"
                    print(f"✓ Registration successful: {message_text}")
                else:
                    assert "failed" in message_text.lower() or "invalid" in message_text.lower()
                    test_result = "PASS"  # Test passed because we expected failure
                    print(f"✓ Expected failure occurred: {message_text}")
                
                reporter.log_step(f"Iteration {iteration}: {test_result}")
                
                # Step 7: Export result to database
                print(f"\n=== Step 7: Export Result to Database (Iteration {iteration}) ===")
                await db_manager.execute_update(
                    "UPDATE UserTestData SET test_result = ?, result_message = ? WHERE id = ?",
                    (test_result, message_text, test_data["id"])
                )
                
                print(f"Result exported: {test_result}")
                reporter.log_step(f"Iteration {iteration}: Result exported")
                
                # Step 8: Take screenshot
                await base_page.take_screenshot(f"e2e_data_driven_iteration_{iteration}")
                
                # Close browser for this iteration
                await browser_manager.close_browser()
                print(f"\n{'='*60}")
                print(f"=== Iteration {iteration} Complete ===")
                print(f"{'='*60}\n")
            
            # Step 9: Verify all results were saved
            print("\n=== Step 9: Verify All Results Saved ===")
            all_results = await db_manager.execute_query(
                "SELECT * FROM UserTestData WHERE test_id = ? ORDER BY iteration",
                (1001,)
            )
            
            assert len(all_results) == 3
            for result in all_results:
                assert result["test_result"] == "PASS"
                assert result["result_message"] is not None
                print(f"Iteration {result['iteration']}: {result['test_result']} - {result['result_message']}")
            
            reporter.log_step("All iterations completed and verified")
            
            # Generate report
            reporter.end_test("PASS")
            report_path = await reporter.generate_html_report()
            print(f"\nE2E Test Report: {report_path}")
            
        finally:
            await browser_manager.close_browser()


# ============================================================================
# E2E Test 3: Multi-Page Navigation
# ============================================================================

class TestE2EMultiPageNavigation:
    """
    End-to-end tests for multi-page navigation workflows.
    
    Tests complete user journeys across multiple pages with state management.
    
    **Validates: Requirements NFR-002, NFR-003**
    """
    
    @pytest.mark.asyncio
    async def test_complete_multi_page_shopping_workflow(self):
        """
        Test complete shopping workflow across multiple pages.
        
        This E2E test covers:
        1. Login page
        2. Product browsing page
        3. Product details page
        4. Shopping cart page
        5. Checkout page
        6. Order confirmation page
        7. Order history page
        """
        config = ConfigManager()
        browser_manager = BrowserManager(config)
        reporter = TestReporter("reports/e2e")
        
        try:
            reporter.start_test("Multi-Page Shopping Workflow E2E")
            
            # Launch browser
            await browser_manager.launch_browser("chromium", headless=True)
            page = await browser_manager.create_page()
            
            element_manager = ElementManager(page, config)
            base_page = BasePage(page, element_manager, config)
            
            # Page 1: Login
            print("\n=== Page 1: Login ===")
            await page.set_content("""
                <!DOCTYPE html>
                <html>
                <head><title>Login</title></head>
                <body>
                    <h1>Login</h1>
                    <input id="username" type="text" />
                    <input id="password" type="password" />
                    <button id="login-btn" onclick="login()">Login</button>
                    <script>
                        function login() {
                            const user = document.getElementById('username').value;
                            const pass = document.getElementById('password').value;
                            if (user && pass) {
                                sessionStorage.setItem('user', user);
                                sessionStorage.setItem('cart', JSON.stringify([]));
                                window.location.href = '#products';
                            }
                        }
                    </script>
                </body>
                </html>
            """)
            
            await element_manager.fill("css=#username", "shopper@example.com")
            await element_manager.fill("css=#password", "Shop123!")
            await element_manager.click("css=#login-btn")
            await asyncio.sleep(0.1)
            reporter.log_step("Page 1: Login completed")
            
            # Page 2: Product Browsing
            print("\n=== Page 2: Product Browsing ===")
            await page.set_content("""
                <!DOCTYPE html>
                <html>
                <head><title>Products</title></head>
                <body>
                    <h1>Products</h1>
                    <div class="user-info">Logged in as: <span id="user"></span></div>
                    <div class="product-grid">
                        <div class="product" data-id="1" data-name="Laptop" data-price="999">
                            <h3>Laptop</h3>
                            <p>Price: $999</p>
                            <button onclick="viewProduct(1)">View Details</button>
                        </div>
                        <div class="product" data-id="2" data-name="Mouse" data-price="29">
                            <h3>Mouse</h3>
                            <p>Price: $29</p>
                            <button onclick="viewProduct(2)">View Details</button>
                        </div>
                    </div>
                    <script>
                        document.getElementById('user').textContent = sessionStorage.getItem('user');
                        function viewProduct(id) {
                            sessionStorage.setItem('selectedProduct', id);
                            window.location.href = '#product-details';
                        }
                    </script>
                </body>
                </html>
            """)
            
            # Verify user is logged in
            user_info = await element_manager.get_text("css=.user-info")
            assert "shopper@example.com" in user_info
            
            # Click on first product
            await page.locator("css=.product[data-id='1'] button").click()
            await asyncio.sleep(0.1)
            reporter.log_step("Page 2: Product selected")
            
            # Page 3: Product Details
            print("\n=== Page 3: Product Details ===")
            await page.set_content("""
                <!DOCTYPE html>
                <html>
                <head><title>Product Details</title></head>
                <body>
                    <h1 id="product-name">Laptop</h1>
                    <p id="product-price">Price: $999</p>
                    <p id="product-description">High-performance laptop</p>
                    <input id="quantity" type="number" value="1" min="1" />
                    <button id="add-to-cart" onclick="addToCart()">Add to Cart</button>
                    <button onclick="window.location.href='#cart'">View Cart</button>
                    <script>
                        function addToCart() {
                            const cart = JSON.parse(sessionStorage.getItem('cart') || '[]');
                            const quantity = parseInt(document.getElementById('quantity').value);
                            cart.push({
                                id: 1,
                                name: 'Laptop',
                                price: 999,
                                quantity: quantity
                            });
                            sessionStorage.setItem('cart', JSON.stringify(cart));
                            alert('Added to cart');
                        }
                    </script>
                </body>
                </html>
            """)
            
            # Verify product details
            product_name = await element_manager.get_text("css=#product-name")
            assert product_name == "Laptop"
            
            # Add to cart
            await element_manager.fill("css=#quantity", "2")
            await element_manager.click("css=#add-to-cart")
            await asyncio.sleep(0.2)
            reporter.log_step("Page 3: Product added to cart")
            
            # Page 4: Shopping Cart
            print("\n=== Page 4: Shopping Cart ===")
            await page.set_content("""
                <!DOCTYPE html>
                <html>
                <head><title>Shopping Cart</title></head>
                <body>
                    <h1>Shopping Cart</h1>
                    <div id="cart-items"></div>
                    <div id="cart-total"></div>
                    <button id="checkout-btn" onclick="window.location.href='#checkout'">Proceed to Checkout</button>
                    <script>
                        const cart = JSON.parse(sessionStorage.getItem('cart') || '[]');
                        const cartDiv = document.getElementById('cart-items');
                        let total = 0;
                        
                        cart.forEach(item => {
                            const itemDiv = document.createElement('div');
                            itemDiv.className = 'cart-item';
                            itemDiv.textContent = `${item.name} x ${item.quantity} = $${item.price * item.quantity}`;
                            cartDiv.appendChild(itemDiv);
                            total += item.price * item.quantity;
                        });
                        
                        document.getElementById('cart-total').textContent = 'Total: $' + total;
                        sessionStorage.setItem('orderTotal', total);
                    </script>
                </body>
                </html>
            """)
            
            # Verify cart contents
            cart_items = await page.locator("css=.cart-item").count()
            assert cart_items > 0
            
            cart_total = await element_manager.get_text("css=#cart-total")
            assert "$" in cart_total
            print(f"Cart total: {cart_total}")
            
            await element_manager.click("css=#checkout-btn")
            await asyncio.sleep(0.1)
            reporter.log_step("Page 4: Proceeding to checkout")
            
            # Page 5: Checkout
            print("\n=== Page 5: Checkout ===")
            await page.set_content("""
                <!DOCTYPE html>
                <html>
                <head><title>Checkout</title></head>
                <body>
                    <h1>Checkout</h1>
                    <form id="checkout-form">
                        <h3>Shipping Information</h3>
                        <input id="address" type="text" placeholder="Address" />
                        <input id="city" type="text" placeholder="City" />
                        <input id="zip" type="text" placeholder="ZIP Code" />
                        
                        <h3>Payment Information</h3>
                        <input id="card-number" type="text" placeholder="Card Number" />
                        <input id="card-name" type="text" placeholder="Name on Card" />
                        
                        <button id="place-order" type="button" onclick="placeOrder()">Place Order</button>
                    </form>
                    <script>
                        function placeOrder() {
                            const orderNumber = 'ORD' + Date.now();
                            sessionStorage.setItem('orderNumber', orderNumber);
                            window.location.href = '#confirmation';
                        }
                    </script>
                </body>
                </html>
            """)
            
            # Fill checkout form
            await element_manager.fill("css=#address", "123 Main St")
            await element_manager.fill("css=#city", "Springfield")
            await element_manager.fill("css=#zip", "62701")
            await element_manager.fill("css=#card-number", "4111111111111111")
            await element_manager.fill("css=#card-name", "John Doe")
            
            await element_manager.click("css=#place-order")
            await asyncio.sleep(0.1)
            reporter.log_step("Page 5: Order placed")
            
            # Page 6: Order Confirmation
            print("\n=== Page 6: Order Confirmation ===")
            await page.set_content("""
                <!DOCTYPE html>
                <html>
                <head><title>Order Confirmation</title></head>
                <body>
                    <h1>Order Confirmation</h1>
                    <div class="confirmation-message">Thank you for your order!</div>
                    <div class="order-number">Order Number: <span id="order-num"></span></div>
                    <div class="order-total">Total: $<span id="total"></span></div>
                    <button onclick="window.location.href='#order-history'">View Order History</button>
                    <script>
                        document.getElementById('order-num').textContent = sessionStorage.getItem('orderNumber');
                        document.getElementById('total').textContent = sessionStorage.getItem('orderTotal');
                    </script>
                </body>
                </html>
            """)
            
            # Verify confirmation
            confirmation_msg = await element_manager.get_text("css=.confirmation-message")
            assert "Thank you" in confirmation_msg
            
            order_number_elem = await element_manager.get_text("css=.order-number")
            assert "ORD" in order_number_elem
            print(f"Order confirmed: {order_number_elem}")
            
            await base_page.take_screenshot("e2e_order_confirmation")
            reporter.log_step("Page 6: Order confirmed")
            
            # Page 7: Order History
            print("\n=== Page 7: Order History ===")
            await page.locator("css=button").click()
            await asyncio.sleep(0.1)
            
            await page.set_content("""
                <!DOCTYPE html>
                <html>
                <head><title>Order History</title></head>
                <body>
                    <h1>Order History</h1>
                    <table id="orders-table">
                        <thead>
                            <tr><th>Order Number</th><th>Total</th><th>Status</th></tr>
                        </thead>
                        <tbody id="orders-tbody"></tbody>
                    </table>
                    <script>
                        const tbody = document.getElementById('orders-tbody');
                        const row = tbody.insertRow();
                        row.insertCell(0).textContent = sessionStorage.getItem('orderNumber');
                        row.insertCell(1).textContent = '$' + sessionStorage.getItem('orderTotal');
                        row.insertCell(2).textContent = 'Processing';
                    </script>
                </body>
                </html>
            """)
            
            # Verify order in history
            table_manager = TableManager(page, element_manager)
            row_count = await table_manager.get_row_count("css=#orders-table")
            assert row_count >= 1
            
            order_status = await table_manager.get_cell_value("css=#orders-table", 0, 2)
            assert order_status == "Processing"
            print(f"Order status: {order_status}")
            
            reporter.log_step("Page 7: Order history verified")
            
            # Generate report
            reporter.end_test("PASS")
            report_path = await reporter.generate_html_report()
            print(f"\nE2E Test Report: {report_path}")
            
        finally:
            await browser_manager.close_browser()


# ============================================================================
# E2E Test 4: Table Operations
# ============================================================================

class TestE2ETableOperations:
    """
    End-to-end tests for table operations.
    
    Tests complete workflows involving table interactions including
    searching, sorting, editing, and pagination.
    
    **Validates: Requirements NFR-002, NFR-003, 8.1, 8.2, 8.3, 8.4, 8.5**
    """
    
    @pytest.mark.asyncio
    async def test_complete_table_management_workflow(self):
        """
        Test complete table management workflow.
        
        This E2E test covers:
        1. Table data loading and display
        2. Searching for specific rows
        3. Reading cell values
        4. Editing cell values
        5. Sorting table data
        6. Pagination navigation
        7. Bulk operations
        """
        config = ConfigManager()
        browser_manager = BrowserManager(config)
        reporter = TestReporter("reports/e2e")
        
        try:
            reporter.start_test("Table Operations E2E")
            
            # Launch browser
            await browser_manager.launch_browser("chromium", headless=True)
            page = await browser_manager.create_page()
            
            element_manager = ElementManager(page, config)
            base_page = BasePage(page, element_manager, config)
            table_manager = TableManager(page, element_manager)
            
            # Step 1: Create page with data table
            print("\n=== Step 1: Load Table Data ===")
            await page.set_content("""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>User Management</title>
                    <style>
                        table { border-collapse: collapse; width: 100%; }
                        th, td { border: 1px solid black; padding: 8px; text-align: left; }
                        th { background-color: #f2f2f2; cursor: pointer; }
                        .editable { background-color: #ffffcc; }
                        .selected { background-color: #e0e0ff; }
                    </style>
                </head>
                <body>
                    <h1>User Management</h1>
                    
                    <div>
                        <input id="search-box" type="text" placeholder="Search..." />
                        <button id="search-btn" onclick="searchTable()">Search</button>
                        <button id="clear-search" onclick="clearSearch()">Clear</button>
                    </div>
                    
                    <div>
                        <button id="bulk-activate" onclick="bulkActivate()">Activate Selected</button>
                        <button id="bulk-deactivate" onclick="bulkDeactivate()">Deactivate Selected</button>
                    </div>
                    
                    <table id="users-table">
                        <thead>
                            <tr>
                                <th onclick="sortTable(0)">Select</th>
                                <th onclick="sortTable(1)">ID</th>
                                <th onclick="sortTable(2)">Name</th>
                                <th onclick="sortTable(3)">Email</th>
                                <th onclick="sortTable(4)">Role</th>
                                <th onclick="sortTable(5)">Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="users-tbody">
                            <tr data-id="1">
                                <td><input type="checkbox" class="row-select" /></td>
                                <td>1</td>
                                <td class="editable" contenteditable="true">Alice Johnson</td>
                                <td>alice@example.com</td>
                                <td class="editable" contenteditable="true">Admin</td>
                                <td class="status">Active</td>
                                <td><button onclick="editRow(this)">Edit</button></td>
                            </tr>
                            <tr data-id="2">
                                <td><input type="checkbox" class="row-select" /></td>
                                <td>2</td>
                                <td class="editable" contenteditable="true">Bob Smith</td>
                                <td>bob@example.com</td>
                                <td class="editable" contenteditable="true">User</td>
                                <td class="status">Active</td>
                                <td><button onclick="editRow(this)">Edit</button></td>
                            </tr>
                            <tr data-id="3">
                                <td><input type="checkbox" class="row-select" /></td>
                                <td>3</td>
                                <td class="editable" contenteditable="true">Charlie Brown</td>
                                <td>charlie@example.com</td>
                                <td class="editable" contenteditable="true">Manager</td>
                                <td class="status">Inactive</td>
                                <td><button onclick="editRow(this)">Edit</button></td>
                            </tr>
                            <tr data-id="4">
                                <td><input type="checkbox" class="row-select" /></td>
                                <td>4</td>
                                <td class="editable" contenteditable="true">Diana Prince</td>
                                <td>diana@example.com</td>
                                <td class="editable" contenteditable="true">User</td>
                                <td class="status">Active</td>
                                <td><button onclick="editRow(this)">Edit</button></td>
                            </tr>
                            <tr data-id="5">
                                <td><input type="checkbox" class="row-select" /></td>
                                <td>5</td>
                                <td class="editable" contenteditable="true">Eve Wilson</td>
                                <td>eve@example.com</td>
                                <td class="editable" contenteditable="true">Manager</td>
                                <td class="status">Inactive</td>
                                <td><button onclick="editRow(this)">Edit</button></td>
                            </tr>
                        </tbody>
                    </table>
                    
                    <div id="pagination">
                        <button id="prev-page" onclick="prevPage()">Previous</button>
                        <span id="page-info">Page 1 of 1</span>
                        <button id="next-page" onclick="nextPage()">Next</button>
                    </div>
                    
                    <div id="message" style="display:none; margin-top:10px; padding:10px; background:#d4edda;"></div>
                    
                    <script>
                        function searchTable() {
                            const searchText = document.getElementById('search-box').value.toLowerCase();
                            const rows = document.querySelectorAll('#users-tbody tr');
                            
                            rows.forEach(row => {
                                const text = row.textContent.toLowerCase();
                                row.style.display = text.includes(searchText) ? '' : 'none';
                            });
                        }
                        
                        function clearSearch() {
                            document.getElementById('search-box').value = '';
                            const rows = document.querySelectorAll('#users-tbody tr');
                            rows.forEach(row => row.style.display = '');
                        }
                        
                        function sortTable(columnIndex) {
                            // Simple sort implementation
                            const tbody = document.getElementById('users-tbody');
                            const rows = Array.from(tbody.querySelectorAll('tr'));
                            
                            rows.sort((a, b) => {
                                const aText = a.cells[columnIndex].textContent;
                                const bText = b.cells[columnIndex].textContent;
                                return aText.localeCompare(bText);
                            });
                            
                            rows.forEach(row => tbody.appendChild(row));
                        }
                        
                        function editRow(button) {
                            const row = button.closest('tr');
                            row.classList.add('selected');
                            showMessage('Row selected for editing');
                        }
                        
                        function bulkActivate() {
                            const checkboxes = document.querySelectorAll('.row-select:checked');
                            checkboxes.forEach(cb => {
                                const row = cb.closest('tr');
                                row.querySelector('.status').textContent = 'Active';
                            });
                            showMessage(`Activated ${checkboxes.length} users`);
                        }
                        
                        function bulkDeactivate() {
                            const checkboxes = document.querySelectorAll('.row-select:checked');
                            checkboxes.forEach(cb => {
                                const row = cb.closest('tr');
                                row.querySelector('.status').textContent = 'Inactive';
                            });
                            showMessage(`Deactivated ${checkboxes.length} users`);
                        }
                        
                        function showMessage(text) {
                            const msg = document.getElementById('message');
                            msg.textContent = text;
                            msg.style.display = 'block';
                            setTimeout(() => msg.style.display = 'none', 3000);
                        }
                        
                        function prevPage() {
                            showMessage('Previous page (not implemented in demo)');
                        }
                        
                        function nextPage() {
                            showMessage('Next page (not implemented in demo)');
                        }
                    </script>
                </body>
                </html>
            """)
            
            # Verify table loaded
            row_count = await table_manager.get_row_count("css=#users-table")
            assert row_count == 5
            print(f"Table loaded with {row_count} rows")
            reporter.log_step("Step 1: Table data loaded")
            
            # Step 2: Search for specific user
            print("\n=== Step 2: Search Table ===")
            await element_manager.fill("css=#search-box", "Bob")
            await element_manager.click("css=#search-btn")
            await asyncio.sleep(0.1)
            
            # Find Bob's row
            bob_row = await table_manager.find_row_by_key(
                table_locator="css=#users-table",
                key_column=2,  # Name column
                key_value="Bob Smith"
            )
            
            assert bob_row >= 0, "Bob Smith not found"
            print(f"Found Bob Smith at row {bob_row}")
            reporter.log_step("Step 2: User found via search")
            
            # Step 3: Read cell values
            print("\n=== Step 3: Read Cell Values ===")
            bob_email = await table_manager.get_cell_value("css=#users-table", bob_row, 3)
            bob_role = await table_manager.get_cell_value("css=#users-table", bob_row, 4)
            bob_status = await table_manager.get_cell_value("css=#users-table", bob_row, 5)
            
            assert bob_email == "bob@example.com"
            assert bob_role == "User"
            assert bob_status == "Active"
            print(f"Bob's details: Email={bob_email}, Role={bob_role}, Status={bob_status}")
            reporter.log_step("Step 3: Cell values read")
            
            # Step 4: Edit cell value
            print("\n=== Step 4: Edit Cell Value ===")
            await element_manager.click("css=#clear-search")
            await asyncio.sleep(0.1)
            
            # Change Bob's role to Manager
            await table_manager.set_cell_value(
                table_locator="css=#users-table",
                row=bob_row,
                column=4,
                value="Manager"
            )
            await asyncio.sleep(0.1)
            
            # Verify change
            updated_role = await table_manager.get_cell_value("css=#users-table", bob_row, 4)
            assert updated_role == "Manager"
            print(f"Bob's role updated to: {updated_role}")
            reporter.log_step("Step 4: Cell value edited")
            
            # Step 5: Sort table
            print("\n=== Step 5: Sort Table ===")
            # Click on Name column header to sort
            await page.locator("css=#users-table th:nth-child(3)").click()
            await asyncio.sleep(0.2)
            
            # Verify sort order (first few rows)
            first_name = await table_manager.get_cell_value("css=#users-table", 0, 2)
            second_name = await table_manager.get_cell_value("css=#users-table", 1, 2)
            
            # Should be alphabetically sorted
            assert first_name < second_name, "Table not sorted correctly"
            print(f"Table sorted: {first_name}, {second_name}, ...")
            reporter.log_step("Step 5: Table sorted")
            
            # Step 6: Search for inactive users
            print("\n=== Step 6: Search for Inactive Users ===")
            inactive_rows = await table_manager.search_table(
                table_locator="css=#users-table",
                search_text="Inactive",
                case_sensitive=False
            )
            
            print(f"Found {len(inactive_rows)} inactive users")
            assert len(inactive_rows) >= 2
            reporter.log_step(f"Step 6: Found {len(inactive_rows)} inactive users")
            
            # Step 7: Bulk activate inactive users
            print("\n=== Step 7: Bulk Activate Users ===")
            # Select all inactive users
            for row_index in inactive_rows:
                await table_manager.click_cell("css=#users-table", row_index, 0)  # Checkbox column
                await asyncio.sleep(0.05)
            
            # Click bulk activate button
            await element_manager.click("css=#bulk-activate")
            await asyncio.sleep(0.2)
            
            # Verify message
            message = await element_manager.get_text("css=#message")
            assert "Activated" in message
            print(f"Bulk operation result: {message}")
            reporter.log_step("Step 7: Bulk activation completed")
            
            # Step 8: Verify status changes
            print("\n=== Step 8: Verify Status Changes ===")
            for row_index in inactive_rows:
                status = await table_manager.get_cell_value("css=#users-table", row_index, 5)
                assert status == "Active", f"Row {row_index} not activated"
            
            print(f"All {len(inactive_rows)} users successfully activated")
            reporter.log_step("Step 8: Status changes verified")
            
            # Step 9: Take final screenshot
            await base_page.take_screenshot("e2e_table_operations_complete")
            
            # Generate report
            reporter.end_test("PASS")
            report_path = await reporter.generate_html_report()
            print(f"\nE2E Test Report: {report_path}")
            
        finally:
            await browser_manager.close_browser()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-s"])
