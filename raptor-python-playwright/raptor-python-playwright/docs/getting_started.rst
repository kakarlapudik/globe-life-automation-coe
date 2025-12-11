Getting Started
===============

This guide will help you get started with the RAPTOR Python Playwright Framework.

.. note::
   For detailed installation instructions, see the `Installation Guide <INSTALLATION_GUIDE.html>`_.
   For configuration details, see the `Configuration Guide <CONFIGURATION_GUIDE.html>`_.
   For troubleshooting, see the `Troubleshooting Guide <TROUBLESHOOTING_GUIDE.html>`_.
   For common questions, see the `FAQ <FAQ.html>`_.

Installation
------------

Prerequisites
~~~~~~~~~~~~~

* Python 3.8 or higher
* pip package manager
* Virtual environment (recommended)

Quick Install
~~~~~~~~~~~~~

.. code-block:: bash

   # Create virtual environment
   python -m venv raptor-env
   source raptor-env/bin/activate  # Windows: raptor-env\Scripts\activate

   # Install RAPTOR
   pip install raptor-playwright

   # Install Playwright browsers
   playwright install

For detailed installation instructions including platform-specific setup, see the `Installation Guide <INSTALLATION_GUIDE.html>`_.

Install from PyPI
~~~~~~~~~~~~~~~~~

.. code-block:: bash

   pip install raptor-playwright

Install from Source
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   git clone https://github.com/your-org/raptor-playwright.git
   cd raptor-playwright
   pip install -e .

Install Playwright Browsers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After installing the package, install the Playwright browser binaries:

.. code-block:: bash

   playwright install

Verify Installation
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Check RAPTOR installation
   pip show raptor-playwright

   # Check Playwright installation
   playwright --version

   # List installed browsers
   playwright list-browsers

Configuration
-------------

Create a configuration file at ``config/settings.yaml``:

.. code-block:: yaml

   browser:
     type: chromium
     headless: false
     timeout: 30000
   
   database:
     server: localhost
     database: test_db
     user: test_user
     password: test_password
   
   logging:
     level: INFO
     file: logs/raptor.log

Environment-Specific Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create environment-specific configs in ``config/environments/``:

* ``dev.yaml`` - Development environment
* ``staging.yaml`` - Staging environment
* ``prod.yaml`` - Production environment

Your First Test
---------------

Create a simple test file ``test_login.py``:

.. code-block:: python

   import pytest
   from raptor.core import BrowserManager, ElementManager
   from raptor.pages import BasePage
   
   @pytest.mark.asyncio
   async def test_login():
       """Test user login functionality."""
       # Initialize browser
       browser_manager = BrowserManager()
       await browser_manager.launch_browser("chromium", headless=False)
       page = await browser_manager.create_page()
       
       # Create element manager
       element_manager = ElementManager(page)
       
       # Navigate to login page
       await page.goto("https://example.com/login")
       
       # Perform login
       await element_manager.fill("css=#username", "testuser")
       await element_manager.fill("css=#password", "testpass")
       await element_manager.click("css=#login-button")
       
       # Verify login success
       await element_manager.wait_for_element("css=#dashboard")
       
       # Cleanup
       await browser_manager.close_browser()

Run the test:

.. code-block:: bash

   pytest test_login.py

Using Page Objects
------------------

Create a page object for better maintainability:

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
           """
           Perform login with credentials.
           
           Args:
               username: Username to login with
               password: Password to login with
           """
           await self.element_manager.fill(self.username_field, username)
           await self.element_manager.fill(self.password_field, password)
           await self.element_manager.click(self.login_button)

Use the page object in your test:

.. code-block:: python

   @pytest.mark.asyncio
   async def test_login_with_page_object():
       """Test login using page object."""
       browser_manager = BrowserManager()
       await browser_manager.launch_browser("chromium")
       page = await browser_manager.create_page()
       element_manager = ElementManager(page)
       
       # Create page object
       login_page = LoginPage(page, element_manager)
       
       # Navigate and login
       await page.goto("https://example.com/login")
       await login_page.login("testuser", "testpass")
       
       # Verify
       await element_manager.wait_for_element("css=#dashboard")
       
       await browser_manager.close_browser()

Data-Driven Testing
-------------------

Use DDDB for data-driven tests:

.. code-block:: python

   from raptor.database import DatabaseManager
   from raptor.utils.data_driven import load_test_data
   
   @pytest.mark.asyncio
   async def test_login_data_driven():
       """Test login with multiple data sets."""
       # Load test data from database
       db_manager = DatabaseManager(
           connection_string="DRIVER={SQL Server};SERVER=localhost;DATABASE=test_db",
           user="test_user",
           password="test_password"
       )
       
       test_data = await load_test_data(
           db_manager=db_manager,
           table="LoginTests",
           test_id=1,
           iteration=1
       )
       
       # Use test data
       username = test_data.get("username")
       password = test_data.get("password")
       
       # Perform test with data
       # ... test implementation

Session Management
------------------

Save and restore browser sessions:

.. code-block:: python

   from raptor.core import SessionManager
   
   @pytest.mark.asyncio
   async def test_with_session():
       """Test using saved session."""
       browser_manager = BrowserManager()
       session_manager = SessionManager()
       
       # Try to restore existing session
       page = await session_manager.restore_session("my_session")
       
       if page is None:
           # Create new session
           await browser_manager.launch_browser("chromium")
           page = await browser_manager.create_page()
           
           # Perform login
           # ... login steps
           
           # Save session
           await session_manager.save_session(page, "my_session")
       
       # Continue with test using existing session
       # ... test steps

Running Tests
-------------

Run all tests:

.. code-block:: bash

   pytest

Run specific test file:

.. code-block:: bash

   pytest tests/test_login.py

Run with specific browser:

.. code-block:: bash

   pytest --browser=firefox

Run in headless mode:

.. code-block:: bash

   pytest --headless

Run in parallel:

.. code-block:: bash

   pytest -n 4

Generate HTML report:

.. code-block:: bash

   pytest --html=report.html

Troubleshooting
---------------

If you encounter issues:

* Check the `Troubleshooting Guide <TROUBLESHOOTING_GUIDE.html>`_ for common problems and solutions
* Review the `FAQ <FAQ.html>`_ for frequently asked questions
* Enable debug logging to diagnose issues
* Join the community forum for help

Common Issues
~~~~~~~~~~~~~

**Browser not launching**: Ensure browsers are installed with ``playwright install``

**Element not found**: Use fallback locators and proper wait conditions

**Timeout errors**: Increase timeout values in configuration

**Database connection fails**: Verify connection string and credentials

See the `Troubleshooting Guide <TROUBLESHOOTING_GUIDE.html>`_ for detailed solutions.

Next Steps
----------

* Read the :doc:`user_guide` for detailed usage instructions
* Review the `Configuration Guide <CONFIGURATION_GUIDE.html>`_ for all configuration options
* Check the `Installation Guide <INSTALLATION_GUIDE.html>`_ for platform-specific setup
* Explore the :doc:`api_reference` for complete API documentation
* Check out :doc:`examples` for more code samples
* Review the :doc:`migration_guide` if migrating from Java/Selenium
* Consult the `FAQ <FAQ.html>`_ for common questions
* Use the `Troubleshooting Guide <TROUBLESHOOTING_GUIDE.html>`_ when issues arise
