Examples
========

This section provides practical examples for common testing scenarios.

Basic Examples
--------------

Simple Login Test
~~~~~~~~~~~~~~~~~

.. code-block:: python

   import pytest
   from raptor.core import BrowserManager, ElementManager
   
   @pytest.mark.asyncio
   async def test_simple_login():
       """Test basic login functionality."""
       # Setup
       browser_manager = BrowserManager()
       await browser_manager.launch_browser("chromium", headless=False)
       page = await browser_manager.create_page()
       element_manager = ElementManager(page)
       
       try:
           # Navigate
           await page.goto("https://example.com/login")
           
           # Login
           await element_manager.fill("css=#username", "testuser")
           await element_manager.fill("css=#password", "testpass")
           await element_manager.click("css=#login-button")
           
           # Verify
           await element_manager.wait_for_element("css=#dashboard")
           assert await element_manager.is_visible("css=#welcome-message")
           
       finally:
           # Cleanup
           await browser_manager.close_browser()

Form Submission
~~~~~~~~~~~~~~~

.. code-block:: python

   @pytest.mark.asyncio
   async def test_form_submission(browser_manager, element_manager, page):
       """Test form submission with multiple fields."""
       await page.goto("https://example.com/contact")
       
       # Fill form fields
       await element_manager.fill("css=#name", "John Doe")
       await element_manager.fill("css=#email", "john@example.com")
       await element_manager.fill("css=#phone", "555-1234")
       await element_manager.select_option("css=#country", "USA")
       await element_manager.fill("css=#message", "Test message")
       
       # Submit
       await element_manager.click("css=#submit-button")
       
       # Verify success
       await element_manager.wait_for_element("css=.success-message")
       success_text = await element_manager.get_text("css=.success-message")
       assert "Thank you" in success_text

Page Object Examples
--------------------

Login Page Object
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from raptor.pages import BasePage
   
   class LoginPage(BasePage):
       """Login page object with all login functionality."""
       
       def __init__(self, page, element_manager):
           super().__init__(page, element_manager)
           # Locators
           self.username_field = "css=#username"
           self.password_field = "css=#password"
           self.login_button = "css=#login-button"
           self.error_message = "css=.error-message"
           self.remember_me_checkbox = "css=#remember-me"
       
       async def login(self, username: str, password: str, remember_me: bool = False):
           """
           Perform login with credentials.
           
           Args:
               username: Username to login with
               password: Password to login with
               remember_me: Whether to check "Remember Me" checkbox
               
           Example:
               >>> login_page = LoginPage(page, element_manager)
               >>> await login_page.login("testuser", "testpass", remember_me=True)
           """
           await self.element_manager.fill(self.username_field, username)
           await self.element_manager.fill(self.password_field, password)
           
           if remember_me:
               await self.element_manager.click(self.remember_me_checkbox)
           
           await self.element_manager.click(self.login_button)
       
       async def get_error_message(self) -> str:
           """
           Get error message text if login fails.
           
           Returns:
               Error message text
               
           Example:
               >>> error = await login_page.get_error_message()
               >>> assert "Invalid credentials" in error
           """
           await self.element_manager.wait_for_element(self.error_message)
           return await self.element_manager.get_text(self.error_message)
       
       async def is_login_button_enabled(self) -> bool:
           """
           Check if login button is enabled.
           
           Returns:
               True if enabled, False otherwise
           """
           return await self.element_manager.is_enabled(self.login_button)

Dashboard Page Object
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   class DashboardPage(BasePage):
       """Dashboard page object."""
       
       def __init__(self, page, element_manager):
           super().__init__(page, element_manager)
           self.welcome_message = "css=#welcome-message"
           self.user_menu = "css=#user-menu"
           self.logout_button = "css=#logout-button"
           self.notifications = "css=.notification"
       
       async def get_welcome_message(self) -> str:
           """Get welcome message text."""
           return await self.element_manager.get_text(self.welcome_message)
       
       async def logout(self):
           """Perform logout."""
           await self.element_manager.click(self.user_menu)
           await self.element_manager.click(self.logout_button)
       
       async def get_notification_count(self) -> int:
           """Get number of notifications."""
           notifications = await self.page.locator(self.notifications).all()
           return len(notifications)

Data-Driven Examples
--------------------

Parameterized Test
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import pytest
   
   @pytest.mark.parametrize("username,password,expected", [
       ("user1", "pass1", "Welcome user1"),
       ("user2", "pass2", "Welcome user2"),
       ("admin", "admin123", "Welcome admin"),
   ])
   @pytest.mark.asyncio
   async def test_login_multiple_users(
       browser_manager, element_manager, page,
       username, password, expected
   ):
       """Test login with multiple user credentials."""
       await page.goto("https://example.com/login")
       
       await element_manager.fill("css=#username", username)
       await element_manager.fill("css=#password", password)
       await element_manager.click("css=#login-button")
       
       await element_manager.wait_for_element("css=#welcome-message")
       message = await element_manager.get_text("css=#welcome-message")
       assert expected in message

Database-Driven Test
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from raptor.database import DatabaseManager
   from raptor.utils.data_driven import load_test_data
   
   @pytest.mark.asyncio
   async def test_database_driven_login(browser_manager, element_manager, page):
       """Test login using data from database."""
       # Setup database
       db_manager = DatabaseManager(
           connection_string="DRIVER={SQL Server};SERVER=localhost;DATABASE=test_db",
           user="test_user",
           password="test_password"
       )
       
       # Load test data
       test_data = await load_test_data(
           db_manager=db_manager,
           table="LoginTests",
           test_id=1,
           iteration=1
       )
       
       # Execute test
       await page.goto(test_data["url"])
       await element_manager.fill("css=#username", test_data["username"])
       await element_manager.fill("css=#password", test_data["password"])
       await element_manager.click("css=#login-button")
       
       # Verify
       expected_message = test_data["expected_message"]
       actual_message = await element_manager.get_text("css=#welcome-message")
       assert expected_message in actual_message
       
       # Export results
       await db_manager.export_data(
           table="LoginTests",
           pk_id=test_data["pk_id"],
           field="result",
           value="PASS"
       )

Table Interaction Examples
---------------------------

Find and Click Row
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from raptor.pages import TableManager
   
   @pytest.mark.asyncio
   async def test_table_interaction(page, element_manager):
       """Test finding and clicking table row."""
       table_manager = TableManager(page, element_manager)
       
       await page.goto("https://example.com/users")
       
       # Find row by key
       row_index = await table_manager.find_row_by_key(
           table_locator="css=#users-table",
           key_column=0,
           key_value="John Doe"
       )
       
       # Get cell value
       email = await table_manager.get_cell_value(
           table_locator="css=#users-table",
           row=row_index,
           column=2
       )
       assert "@example.com" in email
       
       # Click edit button in row
       await table_manager.click_cell(
           table_locator="css=#users-table",
           row=row_index,
           column=4  # Edit button column
       )

Search Table
~~~~~~~~~~~~

.. code-block:: python

   @pytest.mark.asyncio
   async def test_table_search(page, element_manager):
       """Test searching within table."""
       table_manager = TableManager(page, element_manager)
       
       await page.goto("https://example.com/products")
       
       # Search for products
       matching_rows = await table_manager.search_table(
           table_locator="css=#products-table",
           search_text="laptop",
           case_sensitive=False
       )
       
       assert len(matching_rows) > 0, "No matching products found"
       
       # Verify first match
       first_match = matching_rows[0]
       product_name = await table_manager.get_cell_value(
           table_locator="css=#products-table",
           row=first_match,
           column=1
       )
       assert "laptop" in product_name.lower()

Session Management Examples
----------------------------

Save and Restore Session
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from raptor.core import SessionManager
   
   @pytest.mark.asyncio
   async def test_with_saved_session():
       """Test using saved browser session."""
       browser_manager = BrowserManager()
       session_manager = SessionManager()
       element_manager = None
       
       # Try to restore session
       page = await session_manager.restore_session("user_session")
       
       if page is None:
           # Create new session
           await browser_manager.launch_browser("chromium")
           page = await browser_manager.create_page()
           element_manager = ElementManager(page)
           
           # Perform login
           await page.goto("https://example.com/login")
           await element_manager.fill("css=#username", "testuser")
           await element_manager.fill("css=#password", "testpass")
           await element_manager.click("css=#login-button")
           await element_manager.wait_for_element("css=#dashboard")
           
           # Save session
           await session_manager.save_session(page, "user_session")
       else:
           element_manager = ElementManager(page)
       
       # Continue with test using existing session
       await page.goto("https://example.com/profile")
       assert await element_manager.is_visible("css=#profile-info")

Multiple Sessions
~~~~~~~~~~~~~~~~~

.. code-block:: python

   @pytest.mark.asyncio
   async def test_multiple_sessions():
       """Test with multiple user sessions."""
       session_manager = SessionManager()
       
       # User 1 session
       page1 = await session_manager.restore_session("user1_session")
       if page1:
           await page1.goto("https://example.com/dashboard")
       
       # User 2 session
       page2 = await session_manager.restore_session("user2_session")
       if page2:
           await page2.goto("https://example.com/dashboard")
       
       # Interact with both sessions
       # ... test implementation

Verification Examples
---------------------

Soft Assertions
~~~~~~~~~~~~~~~

.. code-block:: python

   from raptor.core import SoftAssertionCollector
   
   @pytest.mark.asyncio
   async def test_with_soft_assertions(page, element_manager):
       """Test using soft assertions."""
       soft_assert = SoftAssertionCollector()
       
       await page.goto("https://example.com/profile")
       
       # Multiple verifications that won't stop execution
       soft_assert.verify_exists("css=#profile-name")
       soft_assert.verify_exists("css=#profile-email")
       soft_assert.verify_exists("css=#profile-phone")
       soft_assert.verify_text("css=#profile-status", "Active")
       soft_assert.verify_enabled("css=#edit-button")
       
       # Assert all at end
       soft_assert.assert_all()  # Raises if any failed

Multiple Verifications
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   @pytest.mark.asyncio
   async def test_multiple_verifications(page, element_manager):
       """Test with multiple verification points."""
       await page.goto("https://example.com/checkout")
       
       # Verify page elements
       await element_manager.verify_exists("css=#cart-items")
       await element_manager.verify_exists("css=#total-price")
       await element_manager.verify_exists("css=#checkout-button")
       
       # Verify button states
       await element_manager.verify_enabled("css=#checkout-button")
       await element_manager.verify_disabled("css=#promo-apply")
       
       # Verify text content
       await element_manager.verify_text("css=#page-title", "Checkout")
       
       # Verify visibility
       await element_manager.verify_visible("css=#payment-section")
       await element_manager.verify_not_visible("css=#success-message")

Advanced Examples
-----------------

File Upload
~~~~~~~~~~~

.. code-block:: python

   @pytest.mark.asyncio
   async def test_file_upload(page, element_manager):
       """Test file upload functionality."""
       await page.goto("https://example.com/upload")
       
       # Set file input
       file_input = await page.locator("css=#file-input")
       await file_input.set_input_files("test_files/document.pdf")
       
       # Submit
       await element_manager.click("css=#upload-button")
       
       # Verify upload
       await element_manager.wait_for_element("css=.upload-success")
       success_message = await element_manager.get_text("css=.upload-success")
       assert "uploaded successfully" in success_message.lower()

Drag and Drop
~~~~~~~~~~~~~

.. code-block:: python

   @pytest.mark.asyncio
   async def test_drag_and_drop(page):
       """Test drag and drop functionality."""
       await page.goto("https://example.com/kanban")
       
       # Drag element
       source = await page.locator("css=#task-1")
       target = await page.locator("css=#done-column")
       
       await source.drag_to(target)
       
       # Verify task moved
       task_in_done = await page.locator("css=#done-column #task-1")
       assert await task_in_done.is_visible()

Screenshot Comparison
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from raptor.utils.screenshot_utilities import (
       capture_full_page_screenshot,
       compare_screenshots
   )
   
   @pytest.mark.asyncio
   async def test_visual_regression(page):
       """Test for visual regressions."""
       await page.goto("https://example.com/home")
       
       # Capture current screenshot
       await capture_full_page_screenshot(
           page,
           "screenshots/current_home.png"
       )
       
       # Compare with baseline
       diff_percentage = compare_screenshots(
           "screenshots/baseline_home.png",
           "screenshots/current_home.png",
           "screenshots/diff_home.png"
       )
       
       # Assert acceptable difference
       assert diff_percentage < 2.0, f"Visual diff too large: {diff_percentage}%"

Property-Based Testing
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from hypothesis import given, strategies as st
   import pytest
   
   @given(
       username=st.text(min_size=3, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
       password=st.text(min_size=8, max_size=50)
   )
   @pytest.mark.asyncio
   async def test_login_property(browser_manager, element_manager, page, username, password):
       """Property-based test for login with various inputs."""
       await page.goto("https://example.com/login")
       
       # Fill credentials
       await element_manager.fill("css=#username", username)
       await element_manager.fill("css=#password", password)
       await element_manager.click("css=#login-button")
       
       # Should either succeed or show error
       try:
           await element_manager.wait_for_element("css=#dashboard", timeout=5000)
           # Login succeeded
           assert await element_manager.is_visible("css=#welcome-message")
       except:
           # Login failed - should show error
           assert await element_manager.is_visible("css=.error-message")

Parallel Execution
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # conftest.py
   import pytest
   from raptor.core import BrowserManager, ElementManager
   
   @pytest.fixture(scope="function")
   async def isolated_browser():
       """Fixture for isolated browser instance."""
       browser_manager = BrowserManager()
       await browser_manager.launch_browser("chromium")
       page = await browser_manager.create_page()
       element_manager = ElementManager(page)
       
       yield browser_manager, page, element_manager
       
       await browser_manager.close_browser()
   
   # test_parallel.py
   @pytest.mark.asyncio
   async def test_parallel_1(isolated_browser):
       """Test that runs in parallel."""
       browser_manager, page, element_manager = isolated_browser
       await page.goto("https://example.com/page1")
       # ... test implementation
   
   @pytest.mark.asyncio
   async def test_parallel_2(isolated_browser):
       """Another test that runs in parallel."""
       browser_manager, page, element_manager = isolated_browser
       await page.goto("https://example.com/page2")
       # ... test implementation

Run with: ``pytest -n 4`` for 4 parallel workers

Custom Wait Conditions
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from raptor.utils.wait_helpers import wait_for_condition
   
   @pytest.mark.asyncio
   async def test_custom_wait(page, element_manager):
       """Test with custom wait condition."""
       await page.goto("https://example.com/dynamic")
       
       # Wait for specific number of items
       async def items_loaded():
           items = await page.locator("css=.item").all()
           return len(items) >= 10
       
       await wait_for_condition(
           condition=items_loaded,
           timeout=30,
           message="Items not loaded"
       )
       
       # Verify
       items = await page.locator("css=.item").all()
       assert len(items) >= 10

Integration with CI/CD
----------------------

GitHub Actions Example
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   # .github/workflows/tests.yml
   name: Automated Tests
   
   on: [push, pull_request]
   
   jobs:
     test:
       runs-on: ubuntu-latest
       
       steps:
         - uses: actions/checkout@v2
         
         - name: Set up Python
           uses: actions/setup-python@v2
           with:
             python-version: '3.11'
         
         - name: Install dependencies
           run: |
             pip install -r requirements.txt
             playwright install
         
         - name: Run tests
           run: pytest --html=report.html --self-contained-html
         
         - name: Upload report
           if: always()
           uses: actions/upload-artifact@v2
           with:
             name: test-report
             path: report.html

More Examples
-------------

For more examples, see:

* ``examples/`` directory in the repository
* Individual module documentation in :doc:`api_reference`
* Quick reference guides in the ``docs/`` directory
