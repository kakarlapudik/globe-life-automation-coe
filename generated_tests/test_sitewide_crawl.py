"""
Test Case: UC002 - Comprehensive Site-Wide Link Validation
Description: Crawl entire site, discover all pages, validate all links
"""

import pytest
from playwright.sync_api import Page, expect
import requests
from typing import Set, List, Dict
from urllib.parse import urljoin, urlparse
import json
import os
from datetime import datetime
import urllib3

# Disable SSL warnings for corporate proxy
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Ensure reports directory exists
os.makedirs("reports", exist_ok=True)

class TestSiteWideCrawl:
    """Crawl entire Globe Life site and validate all links"""
    
    BASE_URL = "https://investors.globelifeinsurance.com/"
    MAX_PAGES = 100
    MAX_DEPTH = 5
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Setup before each test"""
        self.page = page
        self.visited_pages: Set[str] = set()
        self.pages_to_visit: List[str] = [self.BASE_URL]
        self.all_links: Dict[str, List[Dict]] = {}
        self.broken_links: List[Dict] = []
    
    def is_internal_link(self, url: str) -> bool:
        """Check if URL is internal to the site"""
        parsed = urlparse(url)
        base_parsed = urlparse(self.BASE_URL)
        return parsed.netloc == base_parsed.netloc or parsed.netloc == ""
    
    def normalize_url(self, url: str, base: str) -> str:
        """Normalize URL to absolute form"""
        if url.startswith("javascript:") or url.startswith("mailto:") or url.startswith("tel:"):
            return None
        
        if url.startswith("#"):
            return None
        
        absolute_url = urljoin(base, url)
        # Remove fragment
        return absolute_url.split("#")[0]
    
    def test_crawl_entire_site(self):
        """Crawl entire site and discover all pages"""
        depth = 0
        
        while self.pages_to_visit and len(self.visited_pages) < self.MAX_PAGES and depth < self.MAX_DEPTH:
            current_batch = self.pages_to_visit.copy()
            self.pages_to_visit = []
            
            for url in current_batch:
                if url in self.visited_pages:
                    continue
                
                print(f"\n🔍 Crawling: {url}")
                
                try:
                    response = self.page.goto(url, wait_until="networkidle", timeout=30000)
                    
                    if response.status != 200:
                        print(f"  ⚠️  Non-200 status: {response.status}")
                        continue
                    
                    self.visited_pages.add(url)
                    
                    # Extract all links from this page
                    links = self.page.locator("a[href]").all()
                    page_links = []
                    
                    for link in links:
                        href = link.get_attribute("href")
                        if not href:
                            continue
                        
                        normalized = self.normalize_url(href, url)
                        if not normalized:
                            continue
                        
                        page_links.append({
                            "url": normalized,
                            "text": link.inner_text().strip()[:50],
                            "is_internal": self.is_internal_link(normalized)
                        })
                        
                        # Add internal links to crawl queue
                        if self.is_internal_link(normalized) and normalized not in self.visited_pages:
                            if normalized not in self.pages_to_visit:
                                self.pages_to_visit.append(normalized)
                    
                    self.all_links[url] = page_links
                    print(f"  ✓ Found {len(page_links)} links")
                    
                except Exception as e:
                    print(f"  ✗ Error: {str(e)}")
            
            depth += 1
        
        print(f"\n{'='*60}")
        print(f"📊 CRAWL SUMMARY")
        print(f"{'='*60}")
        print(f"Pages Crawled: {len(self.visited_pages)}")
        print(f"Total Links Found: {sum(len(links) for links in self.all_links.values())}")
        print(f"Depth Reached: {depth}")
        print(f"{'='*60}")
        
        assert len(self.visited_pages) > 0, "No pages were crawled"
    
    def test_validate_all_discovered_links(self):
        """Validate all links found during crawl"""
        # First crawl the site
        self.test_crawl_entire_site()
        
        print(f"\n🔗 Validating all discovered links...")
        
        validated_urls = set()
        
        for source_page, links in self.all_links.items():
            for link_info in links:
                url = link_info["url"]
                
                # Skip already validated URLs
                if url in validated_urls:
                    continue
                
                validated_urls.add(url)
                
                try:
                    response = requests.head(url, timeout=10, allow_redirects=True, verify=False)
                    status = response.status_code
                    
                    if status not in [200, 301, 302]:
                        self.broken_links.append({
                            "url": url,
                            "status": status,
                            "source_page": source_page,
                            "link_text": link_info["text"]
                        })
                        print(f"✗ {url} - Status: {status}")
                    else:
                        print(f"✓ {url} - Status: {status}")
                
                except Exception as e:
                    self.broken_links.append({
                        "url": url,
                        "status": "ERROR",
                        "error": str(e),
                        "source_page": source_page
                    })
                    print(f"✗ {url} - Error: {str(e)}")
        
        # Save results to file
        report = {
            "test": "Site-Wide Link Validation",
            "base_url": self.BASE_URL,
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "pages_crawled": len(self.visited_pages),
                "total_unique_links": len(validated_urls),
                "valid_links": len(validated_urls) - len(self.broken_links),
                "broken_links": len(self.broken_links)
            },
            "crawled_pages": list(self.visited_pages),
            "all_links": {page: links for page, links in self.all_links.items()},
            "broken_links": self.broken_links
        }
        
        with open("reports/sitewide_crawl_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        # Simple console output for URLs
        print(f"\n[URLS] Valid Links ({len(report_data.get('valid_links', []))}):")
        for link in report_data.get('valid_links', []):
            print(f"  ✅ {link['url']} - Status: {link['status']}")
        
        if report_data.get('broken_links', []):
            print(f"\n[URLS] Broken Links ({len(report_data.get('broken_links', []))}):")
            for link in report_data.get('broken_links', []):
                print(f"  ❌ {link['url']} - Status: {link['status']}")
        
        # Report results
        print(f"\n{'='*60}")
        print(f"📊 VALIDATION SUMMARY")
        print(f"{'='*60}")
        print(f"Total Unique Links Validated: {len(validated_urls)}")
        print(f"Broken Links: {len(self.broken_links)}")
        print(f"{'='*60}")
        
        if self.broken_links:
            print("\n❌ BROKEN LINKS FOUND:")
            for link in self.broken_links[:10]:  # Show first 10
                print(f"  - {link['url']}")
                print(f"    Status: {link['status']}")
                print(f"    Source: {link['source_page']}")
        
        print(f"\n📄 Report saved to: reports/sitewide_crawl_report.json")
        
        assert len(self.broken_links) == 0, f"Found {len(self.broken_links)} broken links"
