"""
Verify Playwright setup with existing Chromium browser
"""

import os
import sys


def verify_chromium():
    """Verify existing Chromium installation"""
    chromium_path = os.path.expanduser(
        r"~\AppData\Local\ms-playwright\chromium-1155\chrome-win\chrome.exe"
    )
    
    print("🔍 Checking Chromium installation...")
    print(f"   Path: {chromium_path}")
    
    if os.path.exists(chromium_path):
        print("   ✅ Chromium found!")
        return True
    else:
        print("   ❌ Chromium not found at expected location")
        return False


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


def test_playwright():
    """Test Playwright with existing Chromium"""
    print("\n🧪 Testing Playwright with existing Chromium...")
    
    try:
        from playwright.sync_api import sync_playwright
        
        chromium_path = os.path.expanduser(
            r"~\AppData\Local\ms-playwright\chromium-1155\chrome-win\chrome.exe"
        )
        
        with sync_playwright() as p:
            browser = p.chromium.launch(
                executable_path=chromium_path,
                headless=False
            )
            page = browser.new_page()
            page.goto("https://example.com")
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
    
    chromium_ok = verify_chromium()
    deps_ok = verify_dependencies()
    
    if chromium_ok and deps_ok:
        playwright_ok = test_playwright()
        
        print("\n" + "="*60)
        if playwright_ok:
            print("✅ Setup verified! Ready to run tests.")
            print("\nRun tests with:")
            print("  python generated_tests/run_tests.py quick")
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
        print("="*60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
