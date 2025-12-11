RAPTOR Python Playwright Framework Documentation
=================================================

Welcome to the RAPTOR (Robust Automated Playwright Test Orchestration & Reporting) Python Playwright Framework documentation.

RAPTOR is a modern, Python-based test automation framework built on Microsoft Playwright, designed to provide robust, maintainable, and efficient automated testing capabilities.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   getting_started
   api_reference
   user_guide
   migration_guide
   examples

Quick Start
-----------

Installation
~~~~~~~~~~~~

.. code-block:: bash

   pip install raptor-playwright

Basic Usage
~~~~~~~~~~~

.. code-block:: python

   from raptor.core import BrowserManager, ElementManager
   from raptor.pages import BasePage
   
   # Initialize browser
   browser_manager = BrowserManager()
   await browser_manager.launch_browser("chromium")
   page = await browser_manager.create_page()
   
   # Use element manager
   element_manager = ElementManager(page)
   await element_manager.click("css=#login-button")
   await element_manager.fill("css=#username", "testuser")

Features
--------

* **Multi-Browser Support**: Chromium, Firefox, and WebKit
* **Robust Element Location**: Multiple locator strategies with automatic fallback
* **Session Management**: Save and restore browser sessions
* **Data-Driven Testing**: Integration with DDDB for test data
* **Comprehensive Reporting**: HTML reports with screenshots
* **Property-Based Testing**: Built-in support for Hypothesis
* **CLI Interface**: Command-line tools for test execution
* **Migration Tools**: Utilities for converting Java/Selenium tests

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
