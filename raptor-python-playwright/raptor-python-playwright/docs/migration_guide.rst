Migration Guide
===============

This guide helps you migrate from the Java/Selenium RAPTOR framework to the Python/Playwright version.

Overview
--------

The Python/Playwright RAPTOR framework maintains functional parity with the Java/Selenium version while providing:

* **Improved Performance**: Playwright is faster than Selenium
* **Modern API**: Async/await patterns for better concurrency
* **Better Reliability**: Auto-waiting and retry mechanisms
* **Simpler Syntax**: Python's concise syntax reduces code
* **Enhanced Features**: Built-in screenshot, video, and tracing

Migration Strategy
------------------

We recommend a phased approach:

1. **Phase 1**: Set up Python environment and install RAPTOR
2. **Phase 2**: Convert utility classes and helpers
3. **Phase 3**: Convert page objects
4. **Phase 4**: Convert test cases
5. **Phase 5**: Update CI/CD pipelines
6. **Phase 6**: Validate and optimize

Class Mapping
-------------

Java to Python Class Mapping
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 30 40

   * - Java Class
     - Python Module
     - Notes
   * - ``Common.java``
     - ``raptor.pages.base_page``
     - Common page operations
   * - ``Web.java``
     - ``raptor.core.element_manager``
     - Element interactions
   * - ``Global.java``
     - ``raptor.core.config_manager``
     - Configuration management
   * - ``Table.java``
     - ``raptor.pages.table_manager``
     - Table operations
   * - ``Dms.java``
     - ``raptor.database.database_manager``
     - Database operations
   * - ``LFG.java``
     - ``raptor.core.element_manager``
     - Element location
   * - ``V3/*.java``
     - ``raptor.pages.v3/*.py``
     - V3 page objects

Method Mapping
--------------

Click Operations
~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 40 40 20

   * - Java Method
     - Python Method
     - Status
   * - ``click(locator)``
     - ``await element_manager.click(locator)``
     - ✓
   * - ``clickXY(locator)``
     - ``await element_manager.click_at_position(locator)``
     - ✓
   * - ``clickIfExists(locator)``
     - ``await element_manager.click_if_exists(locator)``
     - ✓
   * - ``clickSync(locator)``
     - ``await element_manager.click_with_sync(locator)``
     - ✓
   * - ``doubleClick(locator)``
     - ``await element_manager.double_click(locator)``
     - ✓
   * - ``rightClick(locator)``
     - ``await element_manager.right_click(locator)``
     - ✓

Input Operations
~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 40 40 20

   * - Java Method
     - Python Method
     - Status
   * - ``type(locator, text)``
     - ``await element_manager.fill(locator, text)``
     - ✓
   * - ``clear(locator)``
     - ``await element_manager.clear(locator)``
     - ✓
   * - ``selectOption(locator, value)``
     - ``await element_manager.select_option(locator, value)``
     - ✓
   * - ``hover(locator)``
     - ``await element_manager.hover(locator)``
     - ✓

Verification Operations
~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 40 40 20

   * - Java Method
     - Python Method
     - Status
   * - ``verifyExists(locator)``
     - ``await element_manager.verify_exists(locator)``
     - ✓
   * - ``verifyNotExists(locator)``
     - ``await element_manager.verify_not_exists(locator)``
     - ✓
   * - ``verifyEnabled(locator)``
     - ``await element_manager.verify_enabled(locator)``
     - ✓
   * - ``verifyDisabled(locator)``
     - ``await element_manager.verify_disabled(locator)``
     - ✓
   * - ``verifyText(locator, text)``
     - ``await element_manager.verify_text(locator, text)``
     - ✓

Database Operations
~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 40 40 20

   * - Java Method
     - Python Method
     - Status
   * - ``databaseImport(...)``
     - ``await db_manager.import_data(...)``
     - ✓
   * - ``databaseExport(...)``
     - ``await db_manager.export_data(...)``
     - ✓
   * - ``databaseQuery(...)``
     - ``await db_manager.query_field(...)``
     - ✓
   * - ``databaseExec(...)``
     - ``await db_manager.execute_update(...)``
     - ✓

Wait Operations
~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 40 40 20

   * - Java Method
     - Python Method
     - Status
   * - ``waitForElement(locator)``
     - ``await element_manager.wait_for_element(locator)``
     - ✓
   * - ``waitForSpinner()``
     - ``await element_manager.wait_for_spinner(locator)``
     - ✓
   * - ``waitForDisabledPane()``
     - ``await element_manager.wait_for_disabled_pane()``
     - ✓
   * - ``waitForNetworkIdle()``
     - ``await page.wait_for_load_state("networkidle")``
     - ✓

Code Examples
-------------

Example 1: Simple Test Conversion
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Java (Before)**:

.. code-block:: java

   @Test
   public void testLogin() {
       Web.navigate("https://example.com/login");
       Web.type("css=#username", "testuser");
       Web.type("css=#password", "testpass");
       Web.click("css=#login-button");
       Web.verifyExists("css=#dashboard");
   }

**Python (After)**:

.. code-block:: python

   @pytest.mark.asyncio
   async def test_login():
       """Test user login."""
       await page.goto("https://example.com/login")
       await element_manager.fill("css=#username", "testuser")
       await element_manager.fill("css=#password", "testpass")
       await element_manager.click("css=#login-button")
       await element_manager.verify_exists("css=#dashboard")

Example 2: Page Object Conversion
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Java (Before)**:

.. code-block:: java

   public class LoginPage extends Common {
       private String usernameField = "css=#username";
       private String passwordField = "css=#password";
       private String loginButton = "css=#login-button";
       
       public void login(String username, String password) {
           Web.type(usernameField, username);
           Web.type(passwordField, password);
           Web.click(loginButton);
       }
   }

**Python (After)**:

.. code-block:: python

   from raptor.pages import BasePage
   
   class LoginPage(BasePage):
       """Login page object."""
       
       def __init__(self, page, element_manager):
           super().__init__(page, element_manager)
           self.username_field = "css=#username"
           self.password_field = "css=#password"
           self.login_button = "css=#login-button"
       
       async def login(self, username: str, password: str):
           """Perform login."""
           await self.element_manager.fill(self.username_field, username)
           await self.element_manager.fill(self.password_field, password)
           await self.element_manager.click(self.login_button)

Example 3: Data-Driven Test Conversion
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Java (Before)**:

.. code-block:: java

   @Test
   public void testDataDriven() {
       HashMap<String, String> data = Dms.databaseImport("TestData", 1, 1, 1);
       String username = data.get("username");
       String password = data.get("password");
       
       Web.type("css=#username", username);
       Web.type("css=#password", password);
       Web.click("css=#login-button");
   }

**Python (After)**:

.. code-block:: python

   @pytest.mark.asyncio
   async def test_data_driven():
       """Data-driven test."""
       data = await db_manager.import_data(
           table="TestData",
           test_id=1,
           iteration=1,
           instance=1
       )
       
       username = data["username"]
       password = data["password"]
       
       await element_manager.fill("css=#username", username)
       await element_manager.fill("css=#password", password)
       await element_manager.click("css=#login-button")

Example 4: Table Operations Conversion
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Java (Before)**:

.. code-block:: java

   int row = Table.findRowByKey("css=table", 0, "John Doe");
   String email = Table.getCellValue("css=table", row, 2);
   Table.clickCell("css=table", row, 3);

**Python (After)**:

.. code-block:: python

   row = await table_manager.find_row_by_key(
       "css=table",
       key_column=0,
       key_value="John Doe"
   )
   email = await table_manager.get_cell_value("css=table", row, 2)
   await table_manager.click_cell("css=table", row, 3)

Automated Conversion
--------------------

Use the built-in conversion tool:

.. code-block:: bash

   raptor migrate convert --input MyTest.java --output my_test.py

The converter handles:

* Class structure conversion
* Method signature updates
* Locator syntax conversion
* Import statement updates
* Async/await addition

Manual Review Required
~~~~~~~~~~~~~~~~~~~~~~

After automated conversion, manually review:

1. **Async/await patterns**: Ensure all async methods are awaited
2. **Error handling**: Update exception handling
3. **Configuration**: Update config file references
4. **Imports**: Verify all imports are correct
5. **Test fixtures**: Update pytest fixtures

Migration Utilities
-------------------

DDFE Validator
~~~~~~~~~~~~~~

Validate existing DDFE element definitions:

.. code-block:: python

   from raptor.migration import DDFEValidator
   
   validator = DDFEValidator()
   results = validator.validate_ddfe_file("elements.xml")
   
   if results.is_valid:
       print("DDFE file is valid")
   else:
       for error in results.errors:
           print(f"Error: {error}")

Compatibility Checker
~~~~~~~~~~~~~~~~~~~~~

Check compatibility of existing tests:

.. code-block:: python

   from raptor.migration import CompatibilityChecker
   
   checker = CompatibilityChecker()
   report = checker.check_compatibility("tests/")
   
   print(f"Compatible: {report.compatible_count}")
   print(f"Needs Update: {report.needs_update_count}")
   print(f"Incompatible: {report.incompatible_count}")

Migration Reporter
~~~~~~~~~~~~~~~~~~

Generate migration progress report:

.. code-block:: python

   from raptor.migration import MigrationReporter
   
   reporter = MigrationReporter()
   reporter.add_file("MyTest.java", status="converted")
   reporter.add_file("OtherTest.java", status="in_progress")
   reporter.generate_report("migration_report.html")

Common Pitfalls
---------------

1. **Forgetting await**
   
   ❌ Wrong:
   
   .. code-block:: python
   
      element_manager.click("css=#button")
   
   ✓ Correct:
   
   .. code-block:: python
   
      await element_manager.click("css=#button")

2. **Synchronous database calls**
   
   ❌ Wrong:
   
   .. code-block:: python
   
      data = db_manager.import_data(...)
   
   ✓ Correct:
   
   .. code-block:: python
   
      data = await db_manager.import_data(...)

3. **Missing pytest.mark.asyncio**
   
   ❌ Wrong:
   
   .. code-block:: python
   
      async def test_something():
          ...
   
   ✓ Correct:
   
   .. code-block:: python
   
      @pytest.mark.asyncio
      async def test_something():
          ...

4. **Incorrect locator syntax**
   
   ❌ Wrong:
   
   .. code-block:: python
   
      await element_manager.click("#button")  # Missing css= prefix
   
   ✓ Correct:
   
   .. code-block:: python
   
      await element_manager.click("css=#button")

5. **Not using context managers**
   
   ❌ Wrong:
   
   .. code-block:: python
   
      browser = await browser_manager.launch_browser()
      # ... test code
      # Forgot to close
   
   ✓ Correct:
   
   .. code-block:: python
   
      async with browser_manager.launch_browser() as browser:
          # ... test code
          # Automatically closed

Testing Migration
-----------------

Validate migrated tests:

1. **Run original Java tests** and capture results
2. **Run migrated Python tests** and capture results
3. **Compare results** for consistency
4. **Fix discrepancies** in migrated code
5. **Document differences** if behavior intentionally changed

Validation Checklist
~~~~~~~~~~~~~~~~~~~~

- [ ] All tests converted
- [ ] All tests pass
- [ ] Performance is acceptable
- [ ] Reports are generated correctly
- [ ] Database integration works
- [ ] Session management works
- [ ] CI/CD pipeline updated
- [ ] Team trained on new framework
- [ ] Documentation updated

CI/CD Updates
-------------

Update your CI/CD pipeline:

**Jenkins**:

.. code-block:: groovy

   pipeline {
       agent any
       stages {
           stage('Install') {
               steps {
                   sh 'pip install -r requirements.txt'
                   sh 'playwright install'
               }
           }
           stage('Test') {
               steps {
                   sh 'pytest --html=report.html'
               }
           }
       }
   }

**GitHub Actions**:

.. code-block:: yaml

   name: Tests
   on: [push, pull_request]
   jobs:
     test:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v2
         - uses: actions/setup-python@v2
           with:
             python-version: '3.11'
         - run: pip install -r requirements.txt
         - run: playwright install
         - run: pytest --html=report.html

**Azure DevOps**:

.. code-block:: yaml

   trigger:
     - main
   
   pool:
     vmImage: 'ubuntu-latest'
   
   steps:
     - task: UsePythonVersion@0
       inputs:
         versionSpec: '3.11'
     - script: |
         pip install -r requirements.txt
         playwright install
       displayName: 'Install dependencies'
     - script: pytest --html=report.html
       displayName: 'Run tests'

Support and Resources
---------------------

* **Documentation**: https://raptor-docs.example.com
* **GitHub**: https://github.com/your-org/raptor-playwright
* **Slack**: #raptor-support
* **Email**: raptor-support@example.com

Migration Timeline
------------------

Typical migration timeline for a medium-sized project (100-200 tests):

* **Week 1-2**: Setup and training
* **Week 3-4**: Convert utilities and page objects
* **Week 5-8**: Convert test cases
* **Week 9-10**: Validation and optimization
* **Week 11-12**: CI/CD updates and deployment

Next Steps
----------

1. Review the :doc:`getting_started` guide
2. Set up your development environment
3. Start with a pilot project (5-10 tests)
4. Validate results and gather feedback
5. Scale to full migration
6. Update CI/CD pipelines
7. Train team on new framework
