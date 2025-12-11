#!/usr/bin/env python
"""
Selenium Grid Connectivity Test
Verifies that the Selenium Grid is accessible and ready for test execution
"""

import requests
import json
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions


def test_grid_status(hub_url):
    """Test if Selenium Grid hub is accessible and ready"""
    try:
        print(f"🔍 Testing Selenium Grid at: {hub_url}")
        
        # Test hub status endpoint
        status_url = f"{hub_url}/wd/hub/status"
        response = requests.get(status_url, timeout=10)
        
        if response.status_code == 200:
            status_data = response.json()
            ready = status_data.get('value', {}).get('ready', False)
            message = status_data.get('value', {}).get('message', 'Unknown')
            
            print(f"✅ Grid Status: {response.status_code}")
            print(f"✅ Grid Ready: {ready}")
            print(f"✅ Grid Message: {message}")
            
            return ready
        else:
            print(f"❌ Grid Status: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection Error: {e}")
        return False


def test_browser_session(hub_url, browser='chrome'):
    """Test creating a browser session on the grid"""
    try:
        print(f"\n🌐 Testing {browser} browser session...")
        
        hub_endpoint = f"{hub_url}/wd/hub"
        
        if browser.lower() == 'chrome':
            options = ChromeOptions()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            
            driver = webdriver.Remote(
                command_executor=hub_endpoint,
                options=options
            )
        elif browser.lower() == 'firefox':
            options = FirefoxOptions()
            options.add_argument("--headless")
            
            driver = webdriver.Remote(
                command_executor=hub_endpoint,
                options=options
            )
        else:
            print(f"❌ Unsupported browser: {browser}")
            return False
        
        # Test basic functionality
        driver.get("https://www.google.com")
        title = driver.title
        
        print(f"✅ Browser session created successfully")
        print(f"✅ Page title: {title}")
        print(f"✅ Browser: {driver.capabilities.get('browserName', 'Unknown')}")
        print(f"✅ Version: {driver.capabilities.get('browserVersion', 'Unknown')}")
        
        driver.quit()
        return True
        
    except Exception as e:
        print(f"❌ Browser session error: {e}")
        return False


def get_grid_info(hub_url):
    """Get detailed grid information"""
    try:
        print(f"\n📊 Getting grid information...")
        
        # Get grid console info (if available)
        console_url = f"{hub_url}/grid/console"
        
        print(f"🔗 Grid Console: {console_url}")
        print(f"🔗 Grid Status: {hub_url}/wd/hub/status")
        print(f"🔗 Grid Sessions: {hub_url}/wd/hub/sessions")
        
        # Try to get sessions info
        try:
            sessions_response = requests.get(f"{hub_url}/wd/hub/sessions", timeout=5)
            if sessions_response.status_code == 200:
                sessions = sessions_response.json()
                print(f"📈 Active Sessions: {len(sessions.get('value', []))}")
        except:
            print("📈 Active Sessions: Unable to retrieve")
        
        return True
        
    except Exception as e:
        print(f"❌ Grid info error: {e}")
        return False


def main():
    """Main test function"""
    hub_url = "http://192.168.1.33:4444"
    
    print("🚀 Selenium Grid Connectivity Test")
    print("=" * 50)
    
    # Test 1: Grid Status
    grid_ready = test_grid_status(hub_url)
    
    if not grid_ready:
        print("\n❌ Grid is not ready. Exiting.")
        sys.exit(1)
    
    # Test 2: Get Grid Info
    get_grid_info(hub_url)
    
    # Test 3: Browser Sessions
    browsers_to_test = ['chrome', 'firefox']
    browser_results = {}
    
    for browser in browsers_to_test:
        browser_results[browser] = test_browser_session(hub_url, browser)
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Summary")
    print("=" * 50)
    print(f"Grid Hub: {hub_url}")
    print(f"Grid Ready: {'✅' if grid_ready else '❌'}")
    
    for browser, result in browser_results.items():
        print(f"{browser.capitalize()} Browser: {'✅' if result else '❌'}")
    
    # Overall result
    all_passed = grid_ready and all(browser_results.values())
    
    if all_passed:
        print("\n🎉 All tests passed! Selenium Grid is ready for automation.")
        sys.exit(0)
    else:
        print("\n⚠️ Some tests failed. Check the grid configuration.")
        sys.exit(1)


if __name__ == "__main__":
    main()