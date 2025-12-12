"""
Test Case: Verify Globe Life Investor Relations Homepage Links - Positive Flow
Test ID: UC001_TC001
Description: Verify verify globe life investor relations homepage links works correctly with valid inputs
Automation Priority: Medium
"""

import pytest
import requests
import json
import os
from urllib.parse import urljoin, urlparse
from playwright.sync_api import Page, expect


class TestUC001_TC001:
    """
    Verify Globe Life Investor Relations Homepage Links - Positive Flow
    """
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Setup before each test"""
        self.page = page
        self.base_url = "https://investors.globelifeinsurance.com"
        self.all_links = []
        self.broken_links = []
        self.valid_links = []
        
        # Create reports directory
        os.makedirs("reports", exist_ok=True)
    
    def test_uc001_tc001_positive_flow(self):
        """
        Test: Verify Globe Life Investor Relations Homepage Links - Positive Flow
        Expected: Comprehensive link validation with detailed reporting
        """
        page = self.page
        
        # Navigate to application
        page.goto(self.base_url)
        
        # Wait for page to load completely
        page.wait_for_load_state("networkidle")
        
        # Extract all links from the page
        print(f"\n🔍 Extracting links from {self.base_url}")
        links = page.locator("a[href]").all()
        
        for link in links:
            try:
                href = link.get_attribute("href")
                text = link.inner_text().strip()[:50]  # Limit text length
                
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
                print(f"⚠ Error extracting link: {e}")
        
        print(f"📊 Found {len(self.all_links)} links to validate")
        
        # Validate each link
        self._validate_links()
        
        # Generate summary report
        self._generate_report()
        
        # Print results summary
        print(f"\n============================================================")
        print(f"Total Links Validated: {len(self.all_links)}")
        print(f"Broken Links: {len(self.broken_links)}")
        print(f"============================================================")
        
        if self.broken_links:
            print(f"\n❌ BROKEN LINKS FOUND:")
            for link in self.broken_links:
                print(f"  - {link['url']} (Status: {link['status']})")
        
        # Assert acceptable results (allow 403 status codes as they may be intentional)
        critical_broken_links = [link for link in self.broken_links 
                               if link['status'] not in [403]]
        
        assert len(critical_broken_links) == 0, f"Found {len(critical_broken_links)} critical broken links"
    
    def _validate_links(self):
        """Validate all extracted links"""
        session = requests.Session()
        session.verify = False  # Disable SSL verification for corporate environments
        
        for link_data in self.all_links:
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
                    print(f"✓ {url} - Status: {status_code}")
                else:
                    self.broken_links.append(link_result)
                    print(f"✗ {url} - Status: {status_code}")
                    
            except Exception as e:
                link_result = {
                    'url': url,
                    'text': link_data['text'],
                    'status': 'ERROR',
                    'error': str(e),
                    'valid': False
                }
                self.broken_links.append(link_result)
                print(f"✗ {url} - Error: {e}")
    
    def _generate_report(self):
        """Generate detailed JSON report"""
        report_data = {
            'test_case': 'UC001_TC001',
            'base_url': self.base_url,
            'total_links': len(self.all_links),
            'valid_links_count': len(self.valid_links),
            'broken_links_count': len(self.broken_links),
            'valid_links': self.valid_links,
            'broken_links': self.broken_links,
            'summary': {
                'success_rate': f"{(len(self.valid_links) / len(self.all_links) * 100):.1f}%" if self.all_links else "0%",
                'total_validated': len(self.all_links)
            }
        }
        
        report_file = f"reports/{'UC001_TC001'.lower()}_links_report.json"
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 Report saved to: {report_file}")
    
    def teardown_method(self):
        """Cleanup after test"""
        # Add cleanup logic if needed
        pass
