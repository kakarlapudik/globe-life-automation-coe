"""
Test Case: UC003 - Navigation Menu Link Validation
Description: Validate all navigation menu links including dropdowns
"""

import pytest
from playwright.sync_api import Page, expect
from typing import List, Dict
import json
import os
from datetime import datetime

# Ensure reports directory exists
os.makedirs("reports", exist_ok=True)

class TestNavigationMenu:
    """Test navigation menu links and dropdowns"""
    
    BASE_URL = "https://investors.globelifeinsurance.com/"
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Setup before each test"""
        self.page = page
        self.menu_links = []
        self.broken_links = []
    
    def test_navigation_menu_visible(self):
        """Verify navigation menu is visible"""
        self.page.goto(self.BASE_URL)
        self.page.wait_for_load_state("networkidle")
        
        # Look for common navigation selectors
        nav_selectors = [
            "nav",
            "[role='navigation']",
            ".navbar",
            ".navigation",
            ".nav-menu",
            "header nav"
        ]
        
        nav_found = False
        for selector in nav_selectors:
            if self.page.locator(selector).count() > 0:
                nav_found = True
                print(f"✓ Navigation found with selector: {selector}")
                break
        
        assert nav_found, "Navigation menu not found"
    
    def test_extract_navigation_links(self):
        """Extract all links from navigation menu"""
        self.page.goto(self.BASE_URL)
        self.page.wait_for_load_state("networkidle")
        
        # Try to find navigation
        nav = self.page.locator("nav, [role='navigation'], .navbar").first
        
        if nav.count() > 0:
            links = nav.locator("a[href]").all()
            
            for link in links:
                href = link.get_attribute("href")
                text = link.inner_text().strip()
                is_visible = link.is_visible()
                
                if href and text:
                    self.menu_links.append({
                        "url": href,
                        "text": text,
                        "visible": is_visible
                    })
            
            print(f"\n✓ Extracted {len(self.menu_links)} navigation links")
            for link in self.menu_links:
                print(f"  - {link['text']}: {link['url']}")
        
        assert len(self.menu_links) > 0, "No navigation links found"
    
    def test_click_all_navigation_links(self):
        """Click each navigation link and verify page loads"""
        self.page.goto(self.BASE_URL)
        self.page.wait_for_load_state("networkidle")
        
        # Extract navigation links
        nav = self.page.locator("nav, [role='navigation'], .navbar").first
        
        if nav.count() == 0:
            pytest.skip("Navigation menu not found")
        
        links = nav.locator("a[href]").all()
        
        for i, link in enumerate(links):
            try:
                href = link.get_attribute("href")
                text = link.inner_text().strip()
                
                if not href or href.startswith("#") or href.startswith("javascript:"):
                    continue
                
                print(f"\n🔗 Testing link {i+1}: {text}")
                
                # Click link
                with self.page.expect_navigation(timeout=10000):
                    link.click()
                
                # Verify page loaded
                current_url = self.page.url
                print(f"  ✓ Navigated to: {current_url}")
                
                # Go back to homepage
                self.page.goto(self.BASE_URL)
                self.page.wait_for_load_state("networkidle")
                
            except Exception as e:
                self.broken_links.append({
                    "text": text,
                    "href": href,
                    "error": str(e)
                })
                print(f"  ✗ Error: {str(e)}")
                # Try to recover
                self.page.goto(self.BASE_URL)
        
        # Save results to file
        report = {
            "test": "Navigation Menu Links Validation",
            "url": self.BASE_URL,
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_links": len(links),
                "successful_links": len(links) - len(self.broken_links),
                "failed_links": len(self.broken_links)
            },
            "menu_links": self.menu_links,
            "broken_links": self.broken_links
        }
        
        with open("reports/navigation_menu_report.json", "w") as f:
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
        print(f"Navigation Links Tested: {len(links)}")
        print(f"Failed Links: {len(self.broken_links)}")
        print(f"{'='*60}")
        
        if self.broken_links:
            print("\n❌ FAILED NAVIGATION LINKS:")
            for link in self.broken_links:
                print(f"  - {link['text']}: {link.get('error', 'Unknown error')}")
        
        print(f"\n📄 Report saved to: reports/navigation_menu_report.json")
        
        assert len(self.broken_links) == 0, f"Found {len(self.broken_links)} broken navigation links"
    
    def test_hover_menu_dropdowns(self):
        """Test hover interactions for dropdown menus"""
        self.page.goto(self.BASE_URL)
        self.page.wait_for_load_state("networkidle")
        
        # Find menu items that might have dropdowns
        menu_items = self.page.locator("nav li, .nav-item, .menu-item").all()
        
        dropdown_count = 0
        
        for item in menu_items:
            try:
                # Hover over menu item
                item.hover()
                self.page.wait_for_timeout(500)
                
                # Check if dropdown appeared
                dropdown = item.locator(".dropdown, .submenu, ul").first
                if dropdown.count() > 0 and dropdown.is_visible():
                    dropdown_count += 1
                    print(f"✓ Dropdown found for: {item.inner_text()[:30]}")
                    
                    # Extract dropdown links
                    dropdown_links = dropdown.locator("a[href]").all()
                    print(f"  - Contains {len(dropdown_links)} links")
            
            except Exception as e:
                pass
        
        print(f"\n✓ Found {dropdown_count} dropdown menus")

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
