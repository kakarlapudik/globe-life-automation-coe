"""
Test Case: UC004 - Footer and Utility Links Validation
Description: Validate footer, social media, and utility links
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

class TestFooterLinks:
    """Test footer and utility links"""
    
    BASE_URL = "https://investors.globelifeinsurance.com/"
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Setup before each test"""
        self.page = page
        self.footer_links = []
        self.social_links = []
        self.broken_links = []
    
    def test_footer_exists(self):
        """Verify footer section exists"""
        self.page.goto(self.BASE_URL)
        self.page.wait_for_load_state("networkidle")
        
        # Scroll to bottom
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        self.page.wait_for_timeout(1000)
        
        # Look for footer
        footer_selectors = ["footer", "[role='contentinfo']", ".footer"]
        
        footer_found = False
        for selector in footer_selectors:
            if self.page.locator(selector).count() > 0:
                footer_found = True
                print(f"✓ Footer found with selector: {selector}")
                break
        
        assert footer_found, "Footer not found"
    
    def test_extract_footer_links(self):
        """Extract all links from footer"""
        self.page.goto(self.BASE_URL)
        self.page.wait_for_load_state("networkidle")
        
        # Scroll to footer
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        self.page.wait_for_timeout(1000)
        
        # Find footer
        footer = self.page.locator("footer, [role='contentinfo'], .footer").first
        
        if footer.count() > 0:
            links = footer.locator("a[href]").all()
            
            for link in links:
                href = link.get_attribute("href")
                text = link.inner_text().strip()
                
                if href:
                    self.footer_links.append({
                        "url": href,
                        "text": text if text else "No text"
                    })
            
            print(f"\n✓ Extracted {len(self.footer_links)} footer links")
            for link in self.footer_links:
                print(f"  - {link['text']}: {link['url']}")
        
        assert len(self.footer_links) > 0, "No footer links found"
    
    def test_validate_footer_links(self):
        """Validate all footer links"""
        self.page.goto(self.BASE_URL)
        self.page.wait_for_load_state("networkidle")
        
        # Scroll to footer
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        self.page.wait_for_timeout(1000)
        
        footer = self.page.locator("footer, [role='contentinfo'], .footer").first
        
        if footer.count() == 0:
            pytest.skip("Footer not found")
        
        links = footer.locator("a[href]").all()
        
        for link in links:
            href = link.get_attribute("href")
            text = link.inner_text().strip()
            
            if not href:
                continue
            
            # Skip mailto and tel links
            if href.startswith("mailto:") or href.startswith("tel:"):
                print(f"⊘ Skipping {href} (mailto/tel)")
                continue
            
            # Make absolute URL
            if href.startswith("/"):
                full_url = f"https://investors.globelifeinsurance.com{href}"
            elif href.startswith("http"):
                full_url = href
            else:
                continue
            
            try:
                response = requests.head(full_url, timeout=10, allow_redirects=True, verify=False)
                status = response.status_code
                
                if status not in [200, 301, 302]:
                    self.broken_links.append({
                        "url": full_url,
                        "status": status,
                        "text": text
                    })
                    print(f"✗ {text}: {full_url} - Status: {status}")
                else:
                    print(f"✓ {text}: {full_url} - Status: {status}")
            
            except Exception as e:
                self.broken_links.append({
                    "url": full_url,
                    "status": "ERROR",
                    "error": str(e),
                    "text": text
                })
                print(f"✗ {text}: {full_url} - Error: {str(e)}")
        
        # Save results to file
        report = {
            "test": "Footer Links Validation",
            "url": self.BASE_URL,
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_links": len(links),
                "valid_links": len(links) - len(self.broken_links),
                "broken_links": len(self.broken_links)
            },
            "footer_links": self.footer_links,
            "broken_links": self.broken_links
        }
        
        with open("reports/footer_links_report.json", "w") as f:
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
        print(f"Footer Links Validated: {len(links)}")
        print(f"Broken Links: {len(self.broken_links)}")
        print(f"{'='*60}")
        
        if self.broken_links:
            print("\n❌ BROKEN FOOTER LINKS:")
            for link in self.broken_links:
                print(f"  - {link['text']}: {link['url']} (Status: {link['status']})")
        
        print(f"\n📄 Report saved to: reports/footer_links_report.json")
        
        assert len(self.broken_links) == 0, f"Found {len(self.broken_links)} broken footer links"
    
    def test_social_media_links(self):
        """Test social media icon links"""
        self.page.goto(self.BASE_URL)
        self.page.wait_for_load_state("networkidle")
        
        # Scroll to footer
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        self.page.wait_for_timeout(1000)
        
        # Look for social media links
        social_selectors = [
            "a[href*='facebook']",
            "a[href*='twitter']",
            "a[href*='linkedin']",
            "a[href*='instagram']",
            "a[href*='youtube']",
            ".social-media a",
            ".social-links a"
        ]
        
        for selector in social_selectors:
            links = self.page.locator(selector).all()
            for link in links:
                href = link.get_attribute("href")
                if href:
                    self.social_links.append({
                        "url": href,
                        "platform": self._identify_platform(href)
                    })
        
        print(f"\n✓ Found {len(self.social_links)} social media links")
        for link in self.social_links:
            print(f"  - {link['platform']}: {link['url']}")
        
        # Validate social links
        for link in self.social_links:
            try:
                response = requests.head(link['url'], timeout=10, allow_redirects=True, verify=False)
                status = response.status_code
                
                if status not in [200, 301, 302]:
                    print(f"✗ {link['platform']}: Status {status}")
                else:
                    print(f"✓ {link['platform']}: Status {status}")
            
            except Exception as e:
                print(f"✗ {link['platform']}: Error - {str(e)}")
    
    def _identify_platform(self, url: str) -> str:
        """Identify social media platform from URL"""
        url_lower = url.lower()
        if "facebook" in url_lower:
            return "Facebook"
        elif "twitter" in url_lower or "x.com" in url_lower:
            return "Twitter/X"
        elif "linkedin" in url_lower:
            return "LinkedIn"
        elif "instagram" in url_lower:
            return "Instagram"
        elif "youtube" in url_lower:
            return "YouTube"
        else:
            return "Unknown"

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
