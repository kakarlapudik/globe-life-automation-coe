"""
Test Case: Verify Globe Life Investor Relations Homepage Links - Positive Flow
Test ID: UC001_TC001
Description: Verify verify globe life investor relations homepage links works correctly with valid inputs
Automation Priority: Medium
"""

import pytest
from playwright.sync_api import Page, expect

class TestUC001_TC001:
    """
    Verify Globe Life Investor Relations Homepage Links - Positive Flow
    """
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Setup before each test"""
        self.page = page
        # Add your base URL configuration
        self.base_url = "https://investors.globelifeinsurance.com"
    
    def test_uc001_tc001_positive_flow(self):
        """
        Test: Verify Globe Life Investor Relations Homepage Links - Positive Flow
        Expected: 
        """
        page = self.page
        
        # Navigate to application
        page.goto(self.base_url)
        
        # Verify page loads successfully
        expect(page).to_have_title("Globe Life Inc. - Investor Relations")
        
        # Extract and verify homepage links
        links = page.locator("a[href]").all()
        print(f"Found {len(links)} links on homepage")
        
        # Verify at least some links are present
        assert len(links) > 0, "No links found on homepage"
        
    def teardown_method(self):
        """Cleanup after test"""
        # Add cleanup logic if needed
        pass
