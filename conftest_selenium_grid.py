"""
Pytest configuration for Selenium Grid integration
Alternative conftest for running tests on Selenium Grid
"""

import pytest
import os
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions


@pytest.fixture(scope="session")
def selenium_grid_config():
    """Selenium Grid configuration"""
    return {
        "hub_url": os.environ.get("SELENIUM_HUB_URL", "http://192.168.1.33:4444"),
        "browser": os.environ.get("SELENIUM_BROWSER", "chrome"),
        "implicit_wait": 30,
        "page_load_timeout": 60
    }


@pytest.fixture(scope="function")
def selenium_driver(selenium_grid_config):
    """Create Selenium WebDriver connected to Grid"""
    hub_url = f"{selenium_grid_config['hub_url']}/wd/hub"
    browser = selenium_grid_config['browser'].lower()
    
    if browser == "chrome":
        options = ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        
        capabilities = DesiredCapabilities.CHROME.copy()
        capabilities.update(options.to_capabilities())
        
    elif browser == "firefox":
        options = FirefoxOptions()
        options.add_argument("--width=1920")
        options.add_argument("--height=1080")
        
        capabilities = DesiredCapabilities.FIREFOX.copy()
        capabilities.update(options.to_capabilities())
        
    else:
        raise ValueError(f"Unsupported browser: {browser}")
    
    # Create remote WebDriver
    driver = webdriver.Remote(
        command_executor=hub_url,
        desired_capabilities=capabilities
    )
    
    # Configure timeouts
    driver.implicitly_wait(selenium_grid_config['implicit_wait'])
    driver.set_page_load_timeout(selenium_grid_config['page_load_timeout'])
    
    yield driver
    
    # Cleanup
    driver.quit()


@pytest.fixture(scope="session")
def base_url():
    """Base URL for the application"""
    return "https://investors.globelifeinsurance.com/"


def pytest_configure(config):
    """Configure pytest with custom settings for Selenium Grid"""
    import os
    
    # Create reports directory
    os.makedirs("reports", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("screenshots", exist_ok=True)
    
    # Configure for parallel execution
    worker_id = os.environ.get("PYTEST_XDIST_WORKER")
    if worker_id:
        # Create worker-specific directories to avoid conflicts
        os.makedirs(f"screenshots/{worker_id}", exist_ok=True)


def pytest_html_report_title(report):
    """Customize HTML report title"""
    report.title = "AI Test Automation Report - Selenium Grid"


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Capture screenshots on test failure using Selenium"""
    outcome = yield
    report = outcome.get_result()
    
    if report.when == "call" and report.failed:
        # Get the selenium driver fixture if available
        if "selenium_driver" in item.funcargs:
            driver = item.funcargs["selenium_driver"]
            
            # Use worker-specific directory for parallel execution
            worker_id = os.environ.get("PYTEST_XDIST_WORKER", "main")
            screenshot_dir = f"screenshots/{worker_id}" if worker_id != "main" else "screenshots"
            screenshot_path = f"{screenshot_dir}/{item.name}_failure.png"
            
            # Take screenshot with Selenium
            driver.save_screenshot(screenshot_path)
            
            # Attach to HTML report
            if hasattr(report, "extra"):
                import pytest_html
                report.extra.append(pytest_html.extras.image(screenshot_path))


# Selenium Grid utility functions
def wait_for_element(driver, locator, timeout=30):
    """Wait for element to be present"""
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located(locator)
    )


def wait_for_clickable(driver, locator, timeout=30):
    """Wait for element to be clickable"""
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    
    return WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable(locator)
    )