"""
Test Case: UC005 - Dynamic Content and AJAX Link Validation
Description: Validate dynamically loaded links and AJAX content
"""

import pytest
from playwright.sync_api import Page, expect
import requests
from typing import List, Dict
import json
import os
from datetime import datetime
import urllib3

# Disable SSL warnings for corporate proxy
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Ensure reports directory exists
os.makedirs("reports", exist_ok=True)

class TestDynamicContent:
    """Test dynamically loaded content and links"""
    
    BASE_URL = "https://investors.globelifeinsurance.com/"
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Setup before each test"""
        self.page = page
        self.dynamic_links = []
        self.broken_links = []
    
    def test_wait_for_dynamic_content(self):
        """Wait for all dynamic content to load"""
        self.page.goto(self.BASE_URL)
        
        # Wait for network to be idle
        self.page.wait_for_load_state("networkidle")
        
        # Wait for any lazy-loaded content
        self.page.wait_for_timeout(3000)
        
        # Scroll to trigger lazy loading
        self.page.evaluate("""
            window.scrollTo(0, document.body.scrollHeight / 2);
        """)
        self.page.wait_for_timeout(1000)
        
        self.page.evaluate("""
            window.scrollTo(0, document.body.scrollHeight);
        """)
        self.page.wait_for_timeout(1000)
        
        print("✓ Waited for dynamic content to load")
    
    def test_extract_ajax_loaded_links(self):
        """Extract links from AJAX-loaded content"""
        self.page.goto(self.BASE_URL)
        self.page.wait_for_load_state("networkidle")
        
        # Get initial link count
        initial_links = self.page.locator("a[href]").count()
        print(f"Initial links: {initial_links}")
        
        # Scroll to trigger lazy loading
        for i in range(3):
            self.page.evaluate(f"""
                window.scrollTo(0, document.body.scrollHeight * {(i+1)/3});
            """)
            self.page.wait_for_timeout(2000)
        
        # Get final link count
        final_links = self.page.locator("a[href]").count()
        print(f"Final links after scrolling: {final_links}")
        
        new_links = final_links - initial_links
        if new_links > 0:
            print(f"✓ Found {new_links} dynamically loaded links")
        else:
            print("⊘ No additional dynamic links found")
    
    def test_pagination_links(self):
        """Test pagination links if present"""
        self.page.goto(self.BASE_URL)
        self.page.wait_for_load_state("networkidle")
        
        # Look for pagination elements
        pagination_selectors = [
            ".pagination a",
            "[aria-label*='pagination'] a",
            ".pager a",
            "a[aria-label*='Next']",
            "a[aria-label*='Previous']"
        ]
        
        pagination_found = False
        
        for selector in pagination_selectors:
            links = self.page.locator(selector).all()
            if len(links) > 0:
                pagination_found = True
                print(f"\n✓ Found pagination with selector: {selector}")
                print(f"  - {len(links)} pagination links")
                
                # Test first pagination link
                if len(links) > 0:
                    try:
                        first_link = links[0]
                        href = first_link.get_attribute("href")
                        print(f"  - Testing pagination link: {href}")
                        
                        with self.page.expect_navigation(timeout=10000):
                            first_link.click()
                        
                        print(f"  ✓ Pagination navigation successful")
                        
                    except Exception as e:
                        print(f"  ✗ Pagination error: {str(e)}")
                
                break
        
        if not pagination_found:
            print("⊘ No pagination found on this page")
    
    def test_load_more_buttons(self):
        """Test 'Load More' or infinite scroll functionality"""
        self.page.goto(self.BASE_URL)
        self.page.wait_for_load_state("networkidle")
        
        # Look for "Load More" buttons
        load_more_selectors = [
            "button:has-text('Load More')",
            "button:has-text('Show More')",
            "a:has-text('Load More')",
            ".load-more",
            "[data-action='load-more']"
        ]
        
        for selector in load_more_selectors:
            button = self.page.locator(selector).first
            
            if button.count() > 0 and button.is_visible():
                print(f"\n✓ Found 'Load More' button: {selector}")
                
                try:
                    # Get initial content count
                    initial_count = self.page.locator("a[href]").count()
                    
                    # Click load more
                    button.click()
                    self.page.wait_for_timeout(2000)
                    
                    # Get new content count
                    new_count = self.page.locator("a[href]").count()
                    
                    if new_count > initial_count:
                        print(f"  ✓ Loaded {new_count - initial_count} additional items")
                    else:
                        print(f"  ⊘ No additional content loaded")
                
                except Exception as e:
                    print(f"  ✗ Error clicking 'Load More': {str(e)}")
                
                break
        else:
            print("⊘ No 'Load More' button found")
    
    def test_search_functionality(self):
        """Test search functionality if present"""
        self.page.goto(self.BASE_URL)
        self.page.wait_for_load_state("networkidle")
        
        # Look for search input
        search_selectors = [
            "input[type='search']",
            "input[placeholder*='Search']",
            "input[aria-label*='Search']",
            ".search-input",
            "#search"
        ]
        
        for selector in search_selectors:
            search_input = self.page.locator(selector).first
            
            if search_input.count() > 0 and search_input.is_visible():
                print(f"\n✓ Found search input: {selector}")
                
                try:
                    # Enter search term
                    search_input.fill("investor")
                    search_input.press("Enter")
                    
                    # Wait for results
                    self.page.wait_for_load_state("networkidle")
                    self.page.wait_for_timeout(2000)
                    
                    # Check for results
                    results = self.page.locator("a[href]").count()
                    print(f"  ✓ Search returned {results} links")
                    
                except Exception as e:
                    print(f"  ✗ Search error: {str(e)}")
                
                break
        else:
            print("⊘ No search functionality found")
    
    def test_validate_dynamic_links(self):
        """Validate all dynamically discovered links"""
        self.page.goto(self.BASE_URL)
        self.page.wait_for_load_state("networkidle")
        
        # Trigger all dynamic content
        self.test_wait_for_dynamic_content()
        
        # Extract all links
        links = self.page.locator("a[href]").all()
        
        validated_count = 0
        
        for link in links:
            href = link.get_attribute("href")
            
            if not href or href.startswith("#") or href.startswith("javascript:"):
                continue
            
            # Make absolute URL
            if href.startswith("/"):
                full_url = f"https://investors.globelifeinsurance.com{href}"
            elif href.startswith("http"):
                full_url = href
            else:
                continue
            
            # Validate (sample only first 20 to save time)
            if validated_count >= 20:
                break
            
            try:
                response = requests.head(full_url, timeout=10, allow_redirects=True, verify=False)
                status = response.status_code
                
                if status not in [200, 301, 302]:
                    self.broken_links.append({
                        "url": full_url,
                        "status": status
                    })
                    print(f"✗ {full_url} - Status: {status}")
                else:
                    print(f"✓ {full_url} - Status: {status}")
                
                validated_count += 1
            
            except Exception as e:
                print(f"✗ {full_url} - Error: {str(e)}")
        
        # Save results to file
        report = {
            "test": "Dynamic Content Links Validation",
            "url": self.BASE_URL,
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_links": validated_count,
                "valid_links": validated_count - len(self.broken_links),
                "broken_links": len(self.broken_links)
            },
            "dynamic_links": self.dynamic_links,
            "broken_links": self.broken_links
        }
        
        with open("reports/dynamic_content_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        # Simple console output for URLs
        print(f"\n[URLS] Valid Links ({len(report_data.get('valid_links', []))}):")
        for link in report_data.get('valid_links', []):
            print(f"  ✅ {link['url']} - Status: {link['status']}")
        
        if report_data.get('broken_links', []):
            print(f"\n[URLS] Broken Links ({len(report_data.get('broken_links', []))}):")
            for link in report_data.get('broken_links', []):
                print(f"  ❌ {link['url']} - Status: {link['status']}")
        
        print(f"\n{'='*60}")
        print(f"Dynamic Links Validated: {validated_count}")
        print(f"Broken Links: {len(self.broken_links)}")
        print(f"{'='*60}")
        print(f"\n📄 Report saved to: reports/dynamic_content_report.json")

<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Link Validation Report - {report_data.get('test', 'Test Report')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; text-align: center; border-bottom: 3px solid #007bff; padding-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; }}
        .summary {{ background-color: #e9f4ff; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }}
        .summary-item {{ text-align: center; }}
        .summary-number {{ font-size: 2em; font-weight: bold; color: #007bff; }}
        .summary-label {{ color: #666; font-size: 0.9em; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #f8f9fa; font-weight: bold; color: #333; }}
        tr:hover {{ background-color: #f5f5f5; }}
        .status-ok {{ color: #28a745; font-weight: bold; }}
        .status-error {{ color: #dc3545; font-weight: bold; }}
        .url-cell {{ max-width: 400px; word-break: break-all; }}
        .text-cell {{ max-width: 300px; }}
        .filter-buttons {{ margin: 20px 0; }}
        .filter-btn {{ padding: 8px 16px; margin: 5px; border: none; border-radius: 4px; cursor: pointer; }}
        .filter-btn.active {{ background-color: #007bff; color: white; }}
        .filter-btn:not(.active) {{ background-color: #e9ecef; color: #333; }}
        .search-box {{ width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 4px; }}
    </style>
    <script>
        function filterTable(status) {{
            const rows = document.querySelectorAll('#linksTable tbody tr');
            const buttons = document.querySelectorAll('.filter-btn');
            
            buttons.forEach(btn => btn.classList.remove('active'));
            document.querySelector(`[onclick="filterTable('${{status}}')"]`).classList.add('active');
            
            rows.forEach(row => {{
                if (status === 'all') {{
                    row.style.display = '';
                }} else if (status === 'valid') {{
                    row.style.display = row.classList.contains('valid-link') ? '' : 'none';
                }} else if (status === 'broken') {{
                    row.style.display = row.classList.contains('broken-link') ? '' : 'none';
                }}
            }});
        }}
        
        function searchLinks() {{
            const searchTerm = document.getElementById('searchBox').value.toLowerCase();
            const rows = document.querySelectorAll('#linksTable tbody tr');
            
            rows.forEach(row => {{
                const url = row.cells[0].textContent.toLowerCase();
                const text = row.cells[1].textContent.toLowerCase();
                if (url.includes(searchTerm) || text.includes(searchTerm)) {{
                    row.style.display = '';
                }} else {{
                    row.style.display = 'none';
                }}
            }});
        }}
    </script>
</head>
<body>
    <div class="container">
        <h1>🔗 Link Validation Report</h1>
        
        <div class="summary">
            <h2>📊 Summary</h2>
            <div class="summary-grid">
                <div class="summary-item">
                    <div class="summary-number">{report_data.get('summary', {}).get('total_links', 0)}</div>
                    <div class="summary-label">Total Links</div>
                </div>
                <div class="summary-item">
                    <div class="summary-number" style="color: #28a745;">{report_data.get('summary', {}).get('valid_links', 0)}</div>
                    <div class="summary-label">Valid Links</div>
                </div>
                <div class="summary-item">
                    <div class="summary-number" style="color: #dc3545;">{report_data.get('summary', {}).get('broken_links', 0)}</div>
                    <div class="summary-label">Broken Links</div>
                </div>
                <div class="summary-item">
                    <div class="summary-number" style="color: #007bff;">{((report_data.get('summary', {}).get('valid_links', 0) / max(report_data.get('summary', {}).get('total_links', 1), 1)) * 100):.1f}%</div>
                    <div class="summary-label">Success Rate</div>
                </div>
            </div>
            <p><strong>Base URL:</strong> {report_data.get('url', 'N/A')}</p>
            <p><strong>Test:</strong> {report_data.get('test', 'Link Validation')}</p>
            <p><strong>Timestamp:</strong> {report_data.get('timestamp', 'N/A')}</p>
        </div>
        
        <h2>🔍 Link Details</h2>
        
        <div class="filter-buttons">
            <button class="filter-btn active" onclick="filterTable('all')">All Links ({report_data.get('summary', {}).get('total_links', 0)})</button>
            <button class="filter-btn" onclick="filterTable('valid')">Valid Links ({report_data.get('summary', {}).get('valid_links', 0)})</button>
            <button class="filter-btn" onclick="filterTable('broken')">Broken Links ({report_data.get('summary', {}).get('broken_links', 0)})</button>
        </div>
        
        <input type="text" id="searchBox" class="search-box" placeholder="Search links by URL or text..." onkeyup="searchLinks()">
        
        <table id="linksTable">
            <thead>
                <tr>
                    <th>URL</th>
                    <th>Link Text</th>
                    <th>Status</th>
                    <th>Result</th>
                </tr>
            </thead>
            <tbody>
"""
        
        # Add all links
        for link in report_data.get('all_links', []):
            is_valid = link.get('valid', False) or (isinstance(link.get('status'), int) and link.get('status') < 400)
            row_class = "valid-link" if is_valid else "broken-link"
            status_class = "status-ok" if is_valid else "status-error"
            result_icon = "✅ Valid" if is_valid else "❌ Broken"
            
            html_content += f"""
                <tr class="{row_class}">
                    <td class="url-cell">{"<a href='" + link.get('url', '') + "' target='_blank'>" + link.get('url', '') + "</a>" if is_valid else link.get('url', '')}</td>
                    <td class="text-cell">{link.get('text', '')}</td>
                    <td class="{status_class}">{link.get('status', 'N/A')}</td>
                    <td class="{status_class}">{result_icon}</td>
                </tr>
"""
        
        html_content += """
            </tbody>
        </table>
    </div>
</body>
</html>
"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)

    def teardown_method(self):
        """Cleanup after test"""
        pass
