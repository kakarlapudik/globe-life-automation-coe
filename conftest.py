"""
Pytest configuration and fixtures for AI Test Automation Agent
"""

import pytest
from playwright.sync_api import Page, Browser, BrowserContext
from typing import Generator


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """Configure browser launch to use existing Chromium installation"""
    import os
    
    # Use existing Chromium from ms-playwright directory
    chromium_path = os.path.expanduser(
        r"~\AppData\Local\ms-playwright\chromium-1155\chrome-win\chrome.exe"
    )
    
    return {
        **browser_type_launch_args,
        "executable_path": chromium_path if os.path.exists(chromium_path) else None,
        "headless": False
    }


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context with custom settings"""
    return {
        **browser_context_args,
        "viewport": {"width": 1920, "height": 1080},
        "ignore_https_errors": True,
        "record_video_dir": "test_videos/",
    }


@pytest.fixture(scope="function")
def page(page: Page) -> Generator[Page, None, None]:
    """Enhanced page fixture with custom configuration"""
    # Set default timeout
    page.set_default_timeout(30000)
    
    # Set default navigation timeout
    page.set_default_navigation_timeout(30000)
    
    yield page
    
    # Cleanup
    page.close()


@pytest.fixture(scope="session")
def base_url():
    """Base URL for the application"""
    return "https://investors.globelifeinsurance.com/"


@pytest.fixture(scope="function")
def test_data():
    """Test data fixture"""
    return {
        "valid_user": {
            "username": "test_user",
            "password": "test_password"
        },
        "invalid_user": {
            "username": "invalid_user",
            "password": "wrong_password"
        }
    }


def pytest_configure(config):
    """Configure pytest with custom settings"""
    # Create reports directory
    import os
    os.makedirs("reports", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("screenshots", exist_ok=True)
    os.makedirs("test_videos", exist_ok=True)
    
    # Configure for parallel execution
    worker_id = os.environ.get("PYTEST_XDIST_WORKER")
    if worker_id:
        # Create worker-specific directories to avoid conflicts
        os.makedirs(f"screenshots/{worker_id}", exist_ok=True)
        os.makedirs(f"test_videos/{worker_id}", exist_ok=True)


def pytest_html_report_title(report):
    """Customize HTML report title"""
    report.title = "AI Test Automation Report"


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Capture screenshots on test failure"""
    outcome = yield
    report = outcome.get_result()
    
    if report.when == "call" and report.failed:
        # Get the page fixture if available
        if "page" in item.funcargs:
            page = item.funcargs["page"]
            
            # Use worker-specific directory for parallel execution
            import os
            worker_id = os.environ.get("PYTEST_XDIST_WORKER", "main")
            screenshot_dir = f"screenshots/{worker_id}" if worker_id != "main" else "screenshots"
            screenshot_path = f"{screenshot_dir}/{item.name}_failure.png"
            
            page.screenshot(path=screenshot_path)
            
            # Attach to HTML report
            if hasattr(report, "extra"):
                report.extra.append(pytest.html.extras.image(screenshot_path))
