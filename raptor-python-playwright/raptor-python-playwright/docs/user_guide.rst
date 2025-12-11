User Guide
==========

This comprehensive guide covers all aspects of using the RAPTOR Python Playwright Framework.

.. toctree::
   :maxdepth: 2

   user_guide/browser_management
   user_guide/element_interactions
   user_guide/page_objects
   user_guide/data_driven_testing
   user_guide/session_management
   user_guide/reporting
   user_guide/configuration
   user_guide/best_practices

Overview
--------

RAPTOR is designed to provide a robust, maintainable test automation framework with the following key features:

* **Multi-browser support**: Test across Chromium, Firefox, and WebKit
* **Intelligent element location**: Multiple locator strategies with automatic fallback
* **Session persistence**: Save and restore browser sessions between test runs
* **Data-driven testing**: Integration with DDDB for test data management
* **Comprehensive reporting**: HTML reports with screenshots and execution metrics
* **Property-based testing**: Built-in support for Hypothesis framework
* **Migration tools**: Utilities for converting existing Java/Selenium tests

Architecture
------------

The framework is organized into several key modules:

Core Modules
~~~~~~~~~~~~

* **BrowserManager**: Manages browser lifecycle and contexts
* **ElementManager**: Handles element location and interactions
* **SessionManager**: Manages session persistence and restoration
* **ConfigManager**: Handles configuration loading and management

Database Modules
~~~~~~~~~~~~~~~~

* **DatabaseManager**: Manages database connections and queries
* **ConnectionPool**: Provides connection pooling for efficiency

Page Object Modules
~~~~~~~~~~~~~~~~~~~

* **BasePage**: Base class for all page objects
* **TableManager**: Specialized operations for data tables

Utility Modules
~~~~~~~~~~~~~~~

* **Logger**: Structured logging with context
* **Reporter**: Test result reporting and HTML generation
* **Helpers**: Common utility functions
* **WaitHelpers**: Custom wait conditions and synchronization

Integration Modules
~~~~~~~~~~~~~~~~~~~

* **ALMIntegration**: Integration with HP ALM
* **JIRAIntegration**: Integration with Atlassian JIRA

Migration Modules
~~~~~~~~~~~~~~~~~

* **JavaToPythonConverter**: Converts Java test code to Python
* **DDFEValidator**: Validates DDFE element definitions
* **CompatibilityChecker**: Checks compatibility with existing tests

Code Generation Modules
~~~~~~~~~~~~~~~~~~~~~~~

* **PageObjectGenerator**: Generates page objects from DDFE
* **TestTemplateGenerator**: Creates test templates
* **LocatorSuggester**: Suggests optimal locator strategies

Framework Workflow
------------------

A typical test workflow in RAPTOR follows these steps:

1. **Configuration Loading**: Load environment-specific settings
2. **Browser Initialization**: Launch browser and create context
3. **Session Management**: Restore existing session or create new
4. **Test Data Loading**: Load test data from DDDB if needed
5. **Test Execution**: Execute test steps using page objects
6. **Verification**: Verify expected outcomes
7. **Reporting**: Capture screenshots and generate reports
8. **Cleanup**: Close browser and clean up resources

Example Workflow
~~~~~~~~~~~~~~~~

.. code-block:: python

   import pytest
   from raptor.core import BrowserManager, ElementManager, ConfigManager
   from raptor.database import DatabaseManager
   from raptor.utils import TestReporter
   
   @pytest.mark.asyncio
   async def test_complete_workflow():
       """Example of complete test workflow."""
       # 1. Load configuration
       config = ConfigManager()
       config.load_config(environment="dev")
       
       # 2. Initialize browser
       browser_manager = BrowserManager()
       await browser_manager.launch_browser(
           browser_type=config.get("browser.type"),
           headless=config.get("browser.headless")
       )
       page = await browser_manager.create_page()
       
       # 3. Initialize element manager
       element_manager = ElementManager(page)
       
       # 4. Load test data
       db_manager = DatabaseManager(
           connection_string=config.get("database.connection_string"),
           user=config.get("database.user"),
           password=config.get("database.password")
       )
       test_data = await db_manager.import_data(
           table="TestData",
           test_id=1,
           iteration=1,
           instance=1
       )
       
       # 5. Execute test
       await page.goto(test_data["url"])
       await element_manager.fill("css=#username", test_data["username"])
       await element_manager.fill("css=#password", test_data["password"])
       await element_manager.click("css=#login-button")
       
       # 6. Verify
       await element_manager.wait_for_element("css=#dashboard")
       is_visible = await element_manager.is_visible("css=#welcome-message")
       assert is_visible, "Welcome message not visible"
       
       # 7. Generate report
       reporter = TestReporter()
       reporter.add_test_result(
           test_name="test_complete_workflow",
           status="PASS",
           duration=10.5
       )
       reporter.generate_html_report("reports/test_report.html")
       
       # 8. Cleanup
       await browser_manager.close_browser()

Key Concepts
------------

Locator Strategies
~~~~~~~~~~~~~~~~~~

RAPTOR supports multiple locator strategies:

* **CSS Selectors**: ``css=#element-id``, ``css=.class-name``
* **XPath**: ``xpath=//div[@id='element']``
* **Text Content**: ``text=Click Me``
* **Role-based**: ``role=button[name="Submit"]``
* **ID**: ``id=element-id``

Fallback Locators
~~~~~~~~~~~~~~~~~

Define fallback locators for resilience:

.. code-block:: python

   await element_manager.locate_element(
       locator="css=#primary-button",
       fallback_locators=[
           "xpath=//button[@id='primary-button']",
           "text=Submit",
           "role=button[name='Submit']"
       ]
   )

Synchronization
~~~~~~~~~~~~~~~

RAPTOR provides intelligent waiting mechanisms:

.. code-block:: python

   # Wait for element
   await element_manager.wait_for_element("css=#element", timeout=30000)
   
   # Wait for page load
   await page.wait_for_load_state("networkidle")
   
   # Wait for spinner to disappear
   await element_manager.wait_for_spinner("css=.loading-spinner")
   
   # Custom wait condition
   from raptor.utils.wait_helpers import wait_for_condition
   
   await wait_for_condition(
       condition=lambda: element_manager.is_visible("css=#element"),
       timeout=30,
       message="Element not visible"
   )

Soft Assertions
~~~~~~~~~~~~~~~

Use soft assertions to continue test execution after failures:

.. code-block:: python

   from raptor.core import SoftAssertionCollector
   
   soft_assert = SoftAssertionCollector()
   
   # These won't stop execution
   soft_assert.verify_exists("css=#element1")
   soft_assert.verify_text("css=#title", "Expected Title")
   soft_assert.verify_enabled("css=#submit-button")
   
   # Check all assertions at end
   soft_assert.assert_all()  # Raises if any failed

Property-Based Testing
~~~~~~~~~~~~~~~~~~~~~~

RAPTOR includes support for property-based testing with Hypothesis:

.. code-block:: python

   from hypothesis import given, strategies as st
   import pytest
   
   @given(
       username=st.text(min_size=3, max_size=20),
       password=st.text(min_size=8, max_size=50)
   )
   @pytest.mark.asyncio
   async def test_login_property(username, password):
       """Property test for login with various inputs."""
       # Test implementation

Advanced Features
-----------------

Parallel Execution
~~~~~~~~~~~~~~~~~~

Run tests in parallel using pytest-xdist:

.. code-block:: bash

   pytest -n 4  # Run with 4 workers

Each test gets isolated browser context automatically.

Custom Wait Conditions
~~~~~~~~~~~~~~~~~~~~~~

Create custom wait conditions:

.. code-block:: python

   from raptor.utils.wait_helpers import CustomWaitCondition
   
   class ElementCountCondition(CustomWaitCondition):
       """Wait for specific number of elements."""
       
       def __init__(self, locator: str, count: int):
           self.locator = locator
           self.count = count
       
       async def check(self, page) -> bool:
           elements = await page.locator(self.locator).all()
           return len(elements) == self.count
   
   # Use custom condition
   await wait_for_condition(
       ElementCountCondition("css=.item", 5),
       timeout=30
   )

Visual Regression Testing
~~~~~~~~~~~~~~~~~~~~~~~~~~

Capture and compare screenshots:

.. code-block:: python

   from raptor.utils.screenshot_utilities import (
       capture_full_page_screenshot,
       compare_screenshots
   )
   
   # Capture baseline
   await capture_full_page_screenshot(
       page,
       "screenshots/baseline.png"
   )
   
   # Capture current
   await capture_full_page_screenshot(
       page,
       "screenshots/current.png"
   )
   
   # Compare
   diff_percentage = compare_screenshots(
       "screenshots/baseline.png",
       "screenshots/current.png",
       "screenshots/diff.png"
   )
   
   assert diff_percentage < 5.0, f"Visual diff too large: {diff_percentage}%"

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

**Browser not launching**

* Ensure Playwright browsers are installed: ``playwright install``
* Check browser type in configuration
* Verify system has required dependencies

**Element not found**

* Verify locator strategy is correct
* Check if element is in iframe
* Ensure page has loaded completely
* Use fallback locators

**Timeout errors**

* Increase timeout in configuration
* Check network connectivity
* Verify element is actually present on page
* Use explicit waits

**Session restore fails**

* Check if session file exists
* Verify session hasn't expired
* Ensure browser type matches saved session
* Clear old sessions and create new

Debug Mode
~~~~~~~~~~

Enable debug logging:

.. code-block:: python

   from raptor.utils.logger import get_logger
   
   logger = get_logger(__name__, level="DEBUG")
   logger.debug("Debug message")

Run tests with verbose output:

.. code-block:: bash

   pytest -v -s

Performance Optimization
------------------------

Tips for faster test execution:

1. **Reuse browser sessions** when possible
2. **Use headless mode** for CI/CD
3. **Run tests in parallel** with pytest-xdist
4. **Minimize page loads** by navigating directly to test pages
5. **Use connection pooling** for database operations
6. **Cache configuration** to avoid repeated loading
7. **Disable unnecessary browser features** (images, CSS) when not needed

Best Practices
--------------

See :doc:`user_guide/best_practices` for detailed best practices and coding standards.
