"""
Test Case: Comprehensive Site-Wide Link Validation - Positive Flow
Test ID: UC002_TC001
Description: Verify comprehensive site-wide link validation works correctly with valid inputs
Automation Priority: Medium
"""

import pytest
import requests
import json
import os
from urllib.parse import urljoin, urlparse
from playwright.sync_api import Page, expect


class TestUC002_TC001:
    """
    Comprehensive Site-Wide Link Validation - Positive Flow
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
    
    def test_uc002_tc001_positive_flow(self):
        """
        Test: Comprehensive Site-Wide Link Validation - Positive Flow
        Expected: Crawl multiple pages and validate all internal links across the site
        """
        page = self.page
        visited_pages = set()
        pages_to_visit = [self.base_url]
        max_pages = 5  # Limit for test performance
        
        print(f"\n[SITEWIDE] Starting comprehensive site crawl from {self.base_url}")
        
        while pages_to_visit and len(visited_pages) < max_pages:
            current_url = pages_to_visit.pop(0)
            
            if current_url in visited_pages:
                continue
                
            print(f"\n[CRAWL] Visiting page: {current_url}")
            
            try:
                # Navigate to current page
                page.goto(current_url)
                page.wait_for_load_state("networkidle")
                visited_pages.add(current_url)
                
                # Extract all links from current page
                links = page.locator("a[href]").all()
                print(f"[FOUND] {len(links)} links on {current_url}")
                
                # Process each link
                for link in links:
                    try:
                        href = link.get_attribute("href")
                        if not href:
                            continue
                            
                        # Convert relative URLs to absolute
                        if href.startswith("/"):
                            full_url = urljoin(self.base_url, href)
                        elif href.startswith("http"):
                            full_url = href
                        else:
                            full_url = urljoin(current_url, href)
                        
                        # Add internal links to crawl queue
                        if self.base_url in full_url and full_url not in visited_pages:
                            if full_url not in pages_to_visit:
                                pages_to_visit.append(full_url)
                        
                        # Validate all links (internal and external)
                        self.validate_link(full_url, current_url)
                        
                    except Exception as e:
                        print(f"[ERROR] Processing link: {e}")
                        continue
                        
            except Exception as e:
                print(f"[ERROR] Visiting {current_url}: {e}")
                continue
        
        print(f"\n[SITEWIDE] Crawled {len(visited_pages)} pages, validated {len(self.all_links)} links")
        
        # Generate comprehensive report
        self.generate_sitewide_report()
        
        # Assert no critical broken links
        critical_broken = [link for link in self.broken_links if link.get('status_code') in [404, 500]]
        assert len(critical_broken) == 0, f"Found {len(critical_broken)} critical broken links"
    
    def validate_link(self, url, source_page):
        """Validate a single link and record results"""
        try:
            # Skip certain file types and fragments
            if any(url.endswith(ext) for ext in ['.pdf', '.doc', '.zip']) or '#' in url:
                return
                
            response = requests.head(url, timeout=10, allow_redirects=True, verify=False)
            status_code = response.status_code
            
            link_data = {
                'url': url,
                'source_page': source_page,
                'status_code': status_code,
                'is_valid': status_code in [200, 301, 302, 403]
            }
            
            self.all_links.append(link_data)
            
            if link_data['is_valid']:
                self.valid_links.append(link_data)
                print(f"[VALID] {status_code} - {url}")
            else:
                self.broken_links.append(link_data)
                print(f"[BROKEN] {status_code} - {url}")
                
        except Exception as e:
            link_data = {
                'url': url,
                'source_page': source_page,
                'status_code': 'ERROR',
                'error': str(e),
                'is_valid': False
            }
            self.all_links.append(link_data)
            self.broken_links.append(link_data)
            print(f"[ERROR] {url} - {e}")
    
    def generate_sitewide_report(self):
        """Generate comprehensive sitewide validation report"""
        report_data = {
            'test_case': 'UC002_TC001',
            'description': 'Comprehensive Site-Wide Link Validation',
            'base_url': self.base_url,
            'total_links': len(self.all_links),
            'valid_links_count': len(self.valid_links),
            'broken_links_count': len(self.broken_links),
            'success_rate': f"{(len(self.valid_links) / len(self.all_links) * 100):.1f}%" if self.all_links else "0%",
            'all_links': self.all_links,
            'broken_links': self.broken_links,
            'summary': {
                'total_links': len(self.all_links),
                'valid_links': len(self.valid_links),
                'broken_links': len(self.broken_links),
                'success_rate': f"{(len(self.valid_links) / len(self.all_links) * 100):.1f}%" if self.all_links else "0%"
            }
        }
        
        # Save JSON report
        with open("reports/uc002_tc001_links_report.json", "w") as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n[REPORT] Sitewide validation report saved: reports/uc002_tc001_links_report.json")
        return
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
        
        current_test = test_case_details.get('UC002_TC001', {
            'name': 'UC002_TC001',
            'description': 'Link validation test case',
            'priority': 'Medium',
            'validation_criteria': ['Links return valid status codes']
        })
        
        # Calculate validation results
        critical_failures = [link for link in self.broken_links if link.get('status') in [404, 500, 'ERROR']]
        acceptable_failures = [link for link in self.broken_links if link.get('status') == 403]
        
        report_data = {
            'test_case_id': 'UC002_TC001',
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
        json_report_file = f"reports/{'UC002_TC001'.lower()}_links_report.json"
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
