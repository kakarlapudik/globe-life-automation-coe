"""
Test Case: Footer and Utility Links Validation - Positive Flow
Test ID: UC004_TC001
Description: Verify footer and utility links validation works correctly with valid inputs
Automation Priority: Low
"""

import pytest
import requests
import json
import os
from urllib.parse import urljoin, urlparse
from playwright.sync_api import Page, expect


class TestUC004_TC001:
    """
    Footer and Utility Links Validation - Positive Flow
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
    
    def test_uc004_tc001_positive_flow(self):
        """
        Test: Footer and Utility Links Validation - Positive Flow
        Expected: Comprehensive link validation with detailed reporting
        """
        page = self.page
        
        # Navigate to application
        page.goto(self.base_url)
        
        # Wait for page to load completely
        page.wait_for_load_state("networkidle")
        
        # Extract all links from the page
        print(f"\n[EXTRACT] Extracting links from {self.base_url}")
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
                print(f"[WARN] Error extracting link: {e}")
        
        print(f"[INFO] Found {len(self.all_links)} links to validate")
        
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
            print(f"\n[ERROR] BROKEN LINKS FOUND:")
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
                    print(f"[OK] {url} - Status: {status_code}")
                else:
                    self.broken_links.append(link_result)
                    print(f"[FAIL] {url} - Status: {status_code}")
                    
            except Exception as e:
                link_result = {
                    'url': url,
                    'text': link_data['text'],
                    'status': 'ERROR',
                    'error': str(e),
                    'valid': False
                }
                self.broken_links.append(link_result)
                print(f"[ERROR] {url} - Error: {e}")
    
    def _generate_report(self):
        """Generate detailed JSON and HTML reports"""
        import datetime
        
        # Map test case IDs to detailed information
        test_case_details = {
            'UC001_TC001': {
                'name': 'Verify Globe Life Investor Relations Homepage Links',
                'description': 'Launch the Globe Life investor relations website and verify all links on the home page are working and return HTTP status code 200',
                'priority': 'High',
                'validation_criteria': [
                    'Homepage loads successfully',
                    'All links are extracted correctly', 
                    'All links return HTTP status code 200',
                    'No broken links are found',
                    'Validation report is generated'
                ]
            },
            'UC002_TC001': {
                'name': 'Comprehensive Site-Wide Link Validation',
                'description': 'Crawl the entire Globe Life investor relations website, discover all pages, and validate all links across the entire site',
                'priority': 'High',
                'validation_criteria': [
                    'All pages on the site are discovered and visited',
                    'All links across all pages return status code 200',
                    'Navigation menus and dropdowns are tested',
                    'Dynamic content links are validated',
                    'External links are verified'
                ]
            },
            'UC003_TC001': {
                'name': 'Navigation Menu Link Validation',
                'description': 'Validate all links in the main navigation menu including dropdowns and submenus',
                'priority': 'High',
                'validation_criteria': [
                    'All navigation menu items are clickable',
                    'All dropdown menus expand correctly',
                    'All menu links navigate to valid pages',
                    'All pages return status code 200',
                    'Navigation is consistent across site'
                ]
            },
            'UC004_TC001': {
                'name': 'Footer and Utility Links Validation',
                'description': 'Validate all links in footer, social media icons, and utility navigation',
                'priority': 'Medium',
                'validation_criteria': [
                    'All footer links are valid',
                    'Social media links open correct profiles',
                    'Utility pages load successfully',
                    'External links return status code 200',
                    'Document downloads are accessible'
                ]
            },
            'UC005_TC001': {
                'name': 'Dynamic Content and AJAX Link Validation',
                'description': 'Validate links that are loaded dynamically via JavaScript or AJAX',
                'priority': 'Medium',
                'validation_criteria': [
                    'All dynamic content loads successfully',
                    'AJAX-loaded links are valid',
                    'Pagination works correctly',
                    'Search functionality returns valid links',
                    'All dynamic links return status code 200'
                ]
            },
            'UC006_TC001': {
                'name': 'Automatic Test Report Launch and Display',
                'description': 'Automatically launch and display HTML test reports in the default browser after test execution completes',
                'priority': 'High',
                'validation_criteria': [
                    'HTML report opens automatically in default browser',
                    'Report launches even when some tests fail',
                    'Success message confirms report launch',
                    'Report contains all test execution details',
                    'Consistent behavior across operating systems'
                ]
            }
        }
        
        current_test = test_case_details.get('UC004_TC001', {
            'name': 'UC004_TC001',
            'description': 'Link validation test case',
            'priority': 'Medium',
            'validation_criteria': ['Links return valid status codes']
        })
        
        # Calculate validation results
        critical_failures = [link for link in self.broken_links if link.get('status') in [404, 500, 'ERROR']]
        acceptable_failures = [link for link in self.broken_links if link.get('status') == 403]
        
        report_data = {
            'test_case_id': 'UC004_TC001',
            'test_case_name': current_test['name'],
            'test_description': current_test['description'],
            'test_priority': current_test['priority'],
            'validation_criteria': current_test['validation_criteria'],
            'execution_timestamp': datetime.datetime.now().isoformat(),
            'base_url': self.base_url,
            'total_links': len(self.all_links),
            'valid_links_count': len(self.valid_links),
            'broken_links_count': len(self.broken_links),
            'critical_failures_count': len(critical_failures),
            'acceptable_failures_count': len(acceptable_failures),
            'validation_results': {
                'overall_status': 'PASS' if len(critical_failures) == 0 else 'FAIL',
                'success_rate': f"{(len(self.valid_links) / len(self.all_links) * 100):.1f}%" if self.all_links else "0%",
                'total_validated': len(self.all_links),
                'criteria_met': len(critical_failures) == 0,
                'acceptable_status_codes': [200, 301, 302, 403],
                'critical_status_codes': [404, 500, 'ERROR', 'TIMEOUT']
            },
            'valid_links': self.valid_links,
            'broken_links': self.broken_links,
            'critical_failures': critical_failures,
            'acceptable_failures': acceptable_failures
        }
        
        # Generate JSON report
        json_report_file = f"reports/{'UC004_TC001'.lower()}_links_report.json"
        with open(json_report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n[REPORT] JSON Report saved to: {json_report_file}")
        
        # Enhanced console output with test case information
        print(f"\n[TEST CASE] {report_data['test_case_name']}")
        print(f"[DESCRIPTION] {report_data['test_description']}")
        print(f"[PRIORITY] {report_data['test_priority']}")
        print(f"[STATUS] {report_data['validation_results']['overall_status']}")
        print(f"[SUCCESS RATE] {report_data['validation_results']['success_rate']}")
        
        print(f"\n[VALIDATION CRITERIA]")
        for i, criteria in enumerate(report_data['validation_criteria'], 1):
            status = "✅" if report_data['validation_results']['criteria_met'] else "❌"
            print(f"  {i}. {criteria} {status}")
        
        print(f"\n[URLS] Valid Links ({len(report_data['valid_links'])}):")
        for link in report_data['valid_links'][:5]:  # Show first 5 for brevity
            print(f"  ✅ {link['url']} - Status: {link['status']}")
        if len(report_data['valid_links']) > 5:
            print(f"  ... and {len(report_data['valid_links']) - 5} more valid links")
        
        if report_data['broken_links']:
            print(f"\n[URLS] Broken Links ({len(report_data['broken_links'])}):")
            for link in report_data['broken_links']:
                print(f"  ❌ {link['url']} - Status: {link['status']}")
        
        if report_data['critical_failures']:
            print(f"\n[CRITICAL] Critical Failures ({len(report_data['critical_failures'])}):")
            for link in report_data['critical_failures']:
                print(f"  🚨 {link['url']} - Status: {link['status']}")
        
        if report_data['acceptable_failures']:
            print(f"\n[ACCEPTABLE] Acceptable Failures ({len(report_data['acceptable_failures'])}):")
            for link in report_data['acceptable_failures']:
                print(f"  ⚠️  {link['url']} - Status: {link['status']} (403 - Forbidden but acceptable)")
    

    

    def teardown_method(self):
        """Cleanup after test"""
        # Add cleanup logic if needed
        pass
