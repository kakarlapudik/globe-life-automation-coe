"""
Verify Playwright setup with Chrome/Chromium browser
"""

import os
import sys
import platform
import shutil


def verify_browser():
    """Verify Chrome/Chromium installation"""
    print("🔍 Checking browser installation...")
    
    # Check for environment variable first (GitHub Actions Linux)
    chrome_path = os.environ.get("PLAYWRIGHT_CHROME_EXECUTABLE")
    if chrome_path and os.path.exists(chrome_path):
        print(f"   ✅ Using Chrome from environment: {chrome_path}")
        return True, chrome_path
    
    if platform.system() == "Windows":
        # Windows paths
        windows_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expanduser(r"~\AppData\Local\ms-playwright\chromium-1155\chrome-win\chrome.exe"),
        ]
        
        for path in windows_paths:
            if os.path.exists(path):
                print(f"   ✅ Found browser at: {path}")
                return True, path
                
    else:
        # Linux/Mac - check system binaries
        for binary in ["google-chrome", "chromium-browser", "chromium"]:
            path = shutil.which(binary)
            if path:
                print(f"   ✅ Found {binary} at: {path}")
                return True, path
        
        # Check Playwright cache as fallback
        playwright_patterns = [
            os.path.expanduser("~/.cache/ms-playwright/chromium-*/chrome-linux/chrome"),
        ]
        import glob
        for pattern in playwright_patterns:
            matches = glob.glob(pattern)
            if matches:
                path = matches[0]
                print(f"   ✅ Found Playwright Chromium at: {path}")
                return True, path
    
    print("   ❌ No browser found")
    return False, None


def verify_dependencies():
    """Verify Python dependencies"""
    print("\n🔍 Checking Python dependencies...")
    
    required = {
        "pytest": "pytest",
        "playwright": "playwright",
        "requests": "requests"
    }
    
    missing = []
    
    for name, module in required.items():
        try:
            __import__(module)
            print(f"   ✅ {name} installed")
        except ImportError:
            print(f"   ❌ {name} missing")
            missing.append(name)
    
    return len(missing) == 0


def test_playwright(browser_path=None):
    """Test Playwright with Chrome/Chromium"""
    print("\n🧪 Testing Playwright with browser...")
    
    try:
        from playwright.sync_api import sync_playwright
        
        # Determine headless mode (default to True for CI environments)
        headless = os.environ.get("PLAYWRIGHT_HEADLESS", "true").lower() == "true"
        
        launch_args = {"headless": headless}
        
        # Set executable path if provided
        if browser_path:
            launch_args["executable_path"] = browser_path
            print(f"   Using browser: {browser_path}")
        else:
            print("   Using default Playwright browser")
        
        # Add Linux-specific args for stability
        if platform.system() == "Linux":
            launch_args["args"] = [
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
            ]
        
        with sync_playwright() as p:
            browser = p.chromium.launch(**launch_args)
            page = browser.new_page()
            page.goto("https://example.com", timeout=10000)
            title = page.title()
            print(f"   ✅ Successfully opened page: {title}")
            browser.close()
            return True
    
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False


def main():
    """Main verification"""
    print("="*60)
    print("Playwright Setup Verification")
    print("="*60)
    
    # Show environment info
    print(f"Platform: {platform.system()}")
    if os.environ.get("GITHUB_ACTIONS"):
        print("Environment: GitHub Actions")
    
    browser_ok, browser_path = verify_browser()
    deps_ok = verify_dependencies()
    
    if browser_ok and deps_ok:
        playwright_ok = test_playwright(browser_path)
        
        print("\n" + "="*60)
        if playwright_ok:
            print("✅ Setup verified! Ready to run tests.")
            print("\nRun tests with:")
            print("  pytest generated_tests/ -v")
        else:
            print("❌ Playwright test failed")
        print("="*60)
        
        return 0 if playwright_ok else 1
    else:
        print("\n" + "="*60)
        print("❌ Setup incomplete")
        if not deps_ok:
            print("\nInstall missing dependencies:")
            print("  pip install pytest playwright pytest-html requests")
        if not browser_ok:
            if platform.system() == "Linux":
                print("\nFor Linux, install Chrome or run:")
                print("  playwright install chromium")
            else:
                print("\nInstall Chrome or run:")
                print("  playwright install chromium")
        print("="*60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
