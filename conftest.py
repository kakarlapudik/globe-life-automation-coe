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
    import platform
    import glob
    import shutil
    
    # Determine headless mode from environment
    headless_mode = os.environ.get("PLAYWRIGHT_HEADLESS", "true").lower() == "true"
    
    # Try to find existing Chromium installation
    chromium_path = None
    
    if platform.system() == "Windows":
        # Windows - use only system Chrome installations (no Playwright cache)
        system_chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ]
        
        # Check system Chrome installations only
        for chrome_path in system_chrome_paths:
            if os.path.exists(chrome_path):
                chromium_path = chrome_path
                break
    else:
        # Linux - check environment variable first (for GitHub Actions), then system binaries
        chromium_path = os.environ.get("PLAYWRIGHT_CHROME_EXECUTABLE")
        
        if not chromium_path:
            system_binaries = [
                "/usr/bin/google-chrome",
                "/usr/bin/chromium-browser", 
                "/usr/bin/chromium",
                "/snap/bin/chromium",
            ]
            
            # Check system binaries using shutil.which
            for binary in ["google-chrome", "chromium-browser", "chromium"]:
                path = shutil.which(binary)
                if path:
                    chromium_path = path
                    break
        
        # If no system binary found, check Playwright cache
        if not chromium_path:
            playwright_patterns = [
                os.path.expanduser("~/.cache/ms-playwright/chromium-*/chrome-linux/chrome"),
            ]
            for pattern in playwright_patterns:
                matches = glob.glob(pattern)
                if matches:
                    chromium_path = matches[0]
                    break
    
    # Configure launch args
    launch_args = {
        **browser_type_launch_args,
        "headless": headless_mode,
    }
    
    # Add slow motion for debugging (only in non-headless mode)
    if not headless_mode:
        slow_mo = int(os.environ.get("PLAYWRIGHT_SLOW_MO", "0"))
        if slow_mo > 0:
            launch_args["slow_mo"] = slow_mo
    
    # Only set executable_path if we found a specific path
    if chromium_path:
        launch_args["executable_path"] = chromium_path
        print(f"Using Chrome/Chromium at: {chromium_path}")
        
        # Log if using GitHub Actions Chrome (Linux runners only)
        if chromium_path == os.environ.get("PLAYWRIGHT_CHROME_EXECUTABLE"):
            print("✅ Using Google Chrome from GitHub Actions Linux runner")
    else:
        print("Using default Playwright Chromium")
    
    # Add Linux-specific args for stability
    if platform.system() == "Linux":
        launch_args["args"] = [
            "--no-sandbox",
            "--disable-dev-shm-usage", 
            "--disable-gpu",
            "--disable-web-security",
            "--allow-running-insecure-content",
            "--disable-features=VizDisplayCompositor",
        ]
    
    return launch_args


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


def pytest_sessionfinish(session, exitstatus):
    """Generate enhanced HTML report after all tests complete"""
    import subprocess
    import os
    
    try:
        # Only generate enhanced report if we have JSON reports
        json_reports = [f for f in os.listdir("reports") if f.endswith("_links_report.json")]
        
        if json_reports:
            print("\n[ENHANCED REPORT] Generating enhanced HTML report with test case details...")
            result = subprocess.run(
                ["python", "generate_enhanced_html_report.py"], 
                capture_output=True, 
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print("[ENHANCED REPORT] Enhanced HTML report generated successfully")
                print("[ENHANCED REPORT] Location: reports/enhanced_complete_automation_report.html")
            else:
                print(f"[ENHANCED REPORT] Failed to generate enhanced report: {result.stderr}")
        else:
            print("[ENHANCED REPORT] No JSON reports found, skipping enhanced report generation")
            
    except Exception as e:
        print(f"[ENHANCED REPORT] Error generating enhanced report: {e}")


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
