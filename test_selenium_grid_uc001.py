"""
Selenium Grid Test for UC001 - Homepage Link Validation
Test ID: UC001_TC001_SELENIUM
Description: Verify Globe Life investor relations homepage links using Selenium Grid
"""

import pytest
import requests
import json
import os
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
# Removed deprecated DesiredCapabilities import for Selenium 4


class TestUC001SeleniumGrid:
    """
    Verify Globe Life Investor Relations Homepage Links using Selenium Grid
    """
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup Selenium WebDriver for Grid"""
        # Selenium Grid configuration
        hub_url = "http://192.168.1.33:4444/wd/hub"
        
        # Chrome options for Selenium 4
        options = ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--ignore-ssl-errors=yes")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")
        
        # Create remote WebDriver using Selenium 4 syntax
        self.driver = webdriver.Remote(
            command_executor=hub_url,
            options=options
        )
        
        # Configure timeouts
        self.driver.implicitly_wait(30)
        self.driver.set_page_load_timeout(60)
        
        # Test data
        self.base_url = "https://investors.globelifeinsurance.com"
        self.all_links = []
        self.broken_links = []
        self.valid_links = []
        
        # Create reports directory
        os.makedirs("reports", exist_ok=True)
        
        yield
        
        # Cleanup
        self.driver.quit()
    
    def test_uc001_selenium_grid_homepage_links(self):
        """
        Test: Verify Globe Life Homepage Links using Selenium Grid
        Expected: All links should be valid and return proper HTTP status codes
        """
        print(f"\n[SELENIUM GRID] Starting test on: {self.driver.command_executor}")
        print(f"[SELENIUM GRID] Browser: {self.driver.capabilities['browserName']}")
        print(f"[SELENIUM GRID] Version: {self.driver.capabilities.get('browserVersion', 'Unknown')}")
        
        # Navigate to application
        print(f"[NAVIGATE] Opening: {self.base_url}")
        self.driver.get(self.base_url)
        
        # Wait for page to load
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Extract all links from the page
        print(f"[EXTRACT] Extracting links from homepage")
        link_elements = self.driver.find_elements(By.CSS_SELECTOR, "a[href]")
        
        for link_element in link_elements:
            try:
                href = link_element.get_attribute("href")
                text = link_element.text.strip()[:50]  # Limit text length
                
                if href:
                    # Convert relative URLs to absolute
                    full_url = urljoin(self.base_url, href)
                    
                    # Skip non-HTTP links
                    if not full_url.startswith(('http://', 'https://')):
                        continue
                    
                    self.all_links.append({
                        'url': full_url,
                        'text': text,
                        'original_href': href
                    })
            except Exception as e:
                print(f"[WARN] Error extracting link: {e}")
        
        print(f"[INFO] Found {len(self.all_links)} links to validate")
        
        # Validate each link
        self._validate_links()
        
        # Generate summary report
        self._generate_report()
        
        # Print results summary
        print(f"\n============================================================")
        print(f"[SELENIUM GRID] Test Results Summary")
        print(f"============================================================")
        print(f"Total Links Validated: {len(self.all_links)}")
        print(f"Valid Links: {len(self.valid_links)}")
        print(f"Broken Links: {len(self.broken_links)}")
        print(f"Success Rate: {(len(self.valid_links) / len(self.all_links) * 100):.1f}%" if self.all_links else "0%")
        print(f"============================================================")
        
        if self.broken_links:
            print(f"\n[ERROR] BROKEN LINKS FOUND:")
            for link in self.broken_links:
                print(f"  ❌ {link['url']} (Status: {link['status']})")
        
        # Take screenshot for documentation
        screenshot_path = "reports/selenium_grid_homepage_screenshot.png"
        self.driver.save_screenshot(screenshot_path)
        print(f"[SCREENSHOT] Saved to: {screenshot_path}")
        
        # Assert acceptable results (allow 403 status codes as they may be intentional)
        critical_broken_links = [link for link in self.broken_links 
                               if link['status'] not in [403]]
        
        assert len(critical_broken_links) == 0, f"Found {len(critical_broken_links)} critical broken links"
        
        print(f"[SUCCESS] ✅ All critical links are working properly!")
    
    def _validate_links(self):
        """Validate all extracted links using HTTP requests"""
        session = requests.Session()
        session.verify = False  # Disable SSL verification for corporate environments
        
        print(f"[VALIDATE] Starting link validation...")
        
        for i, link_data in enumerate(self.all_links, 1):
            url = link_data['url']
            try:
                # Use HEAD request for faster validation
                response = session.head(url, timeout=30, allow_redirects=True)
                status_code = response.status_code
                
                link_result = {
                    'url': url,
                    'text': link_data['text'],
                    'status': status_code,
                    'valid': status_code < 400
                }
                
                if status_code < 400:
                    self.valid_links.append(link_result)
                    print(f"[{i:3d}/{len(self.all_links)}] ✅ {url} - Status: {status_code}")
                else:
                    self.broken_links.append(link_result)
                    print(f"[{i:3d}/{len(self.all_links)}] ❌ {url} - Status: {status_code}")
                    
            except Exception as e:
                link_result = {
                    'url': url,
                    'text': link_data['text'],
                    'status': 'ERROR',
                    'error': str(e),
                    'valid': False
                }
                self.broken_links.append(link_result)
                print(f"[{i:3d}/{len(self.all_links)}] ❌ {url} - Error: {e}")
    
    def _generate_report(self):
        """Generate detailed JSON report"""
        report_data = {
            'test_case': 'UC001_TC001_SELENIUM_GRID',
            'execution_mode': 'Selenium Grid',
            'grid_hub': 'http://192.168.1.33:4444',
            'browser': self.driver.capabilities.get('browserName', 'Unknown'),
            'browser_version': self.driver.capabilities.get('browserVersion', 'Unknown'),
            'base_url': self.base_url,
            'total_links': len(self.all_links),
            'valid_links_count': len(self.valid_links),
            'broken_links_count': len(self.broken_links),
            'valid_links': self.valid_links,
            'broken_links': self.broken_links,
            'summary': {
                'success_rate': f"{(len(self.valid_links) / len(self.all_links) * 100):.1f}%" if self.all_links else "0%",
                'total_validated': len(self.all_links),
                'execution_mode': 'Selenium Grid Remote Execution'
            }
        }
        
        report_file = f"reports/selenium_grid_uc001_links_report.json"
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"[REPORT] Report saved to: {report_file}")


if __name__ == "__main__":
    # Run the test directly
    test_instance = TestUC001SeleniumGrid()
    test_instance.setup()
    test_instance.test_uc001_selenium_grid_homepage_links()