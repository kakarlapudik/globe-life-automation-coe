# Globe Life Investor Relations - Link Validation Test Suite

Comprehensive Playwright Python test suite for validating all links across the Globe Life investor relations website.

## Test Cases

### UC001: Homepage Links (`test_homepage_links.py`)
- Validates all links on the homepage
- Checks HTTP status codes
- Reports broken links

### UC002: Site-Wide Crawl (`test_sitewide_crawl.py`)
- Crawls entire website (up to 100 pages, depth 5)
- Discovers all internal pages
- Validates all links across the site
- **Note:** This is a slow test (~10-30 minutes)

### UC003: Navigation Menu (`test_navigation_menu.py`)
- Tests main navigation menu links
- Validates dropdown menus
- Tests hover interactions
- Verifies all menu destinations

### UC004: Footer Links (`test_footer_links.py`)
- Validates footer links
- Tests social media links
- Checks utility links (Privacy, Terms, etc.)
- Validates external links

### UC005: Dynamic Content (`test_dynamic_content.py`)
- Tests AJAX-loaded content
- Validates pagination links
- Tests "Load More" functionality
- Validates search results

## Installation

```bash
# Install dependencies
pip install pytest playwright pytest-html requests

# Note: Tests are configured to use existing Chromium installation
# Located at: ~\AppData\Local\ms-playwright\chromium-1155\
# No need to run 'playwright install' - using existing browser
```

## Running Tests

### Run All Tests (Parallel Execution by Default)
```bash
pytest generated_tests/ -v
```

### Run Specific Test File (Parallel Execution by Default)
```bash
pytest generated_tests/test_homepage_links.py -v
```

### Run with HTML Report
```bash
pytest generated_tests/ --html=report.html --self-contained-html
```

### Run Excluding Slow Tests
```bash
pytest generated_tests/ -v -m "not slow"
```

### Run in Headed Mode (See Browser)
```bash
pytest generated_tests/ --headed
```

### Parallel Execution Configuration
```bash
# Parallel execution is enabled by default (uses all CPU cores)
pytest generated_tests/

# Override to use specific number of workers
pytest generated_tests/ -n 4

# Disable parallel execution (run sequentially)
pytest generated_tests/ -n 0

# Note: pytest-xdist is already included in requirements.txt
```

## Test Output

Each test provides detailed output:
- ✓ Successful validations
- ✗ Failed validations with error details
- Summary statistics
- Broken link reports

Example output:
```
✓ https://investors.globelifeinsurance.com/ - Status: 200
✓ https://investors.globelifeinsurance.com/about - Status: 200
✗ https://investors.globelifeinsurance.com/broken - Status: 404

============================================================
Total Links Validated: 45
Broken Links: 1
============================================================
```

## Configuration

### Timeouts
Adjust timeouts in `conftest.py`:
```python
page.set_default_timeout(30000)  # 30 seconds
```

### Crawl Limits
Adjust in `test_sitewide_crawl.py`:
```python
MAX_PAGES = 100  # Maximum pages to crawl
MAX_DEPTH = 5    # Maximum crawl depth
```

### Browser Settings
Configure in `conftest.py`:
```python
"viewport": {"width": 1920, "height": 1080}
```

## CI/CD Integration

### GitHub Actions
```yaml
name: Link Validation Tests

on: [push, pull_request, schedule]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: playwright install chromium
      - run: pytest generated_tests/ --html=report.html
      - uses: actions/upload-artifact@v3
        if: always()
        with:
          name: test-report
          path: report.html
```

## Troubleshooting

### SSL Certificate Errors
Tests ignore HTTPS errors by default. To enforce SSL validation:
```python
# In conftest.py
"ignore_https_errors": False
```

### Timeout Issues
Increase timeout for slow pages:
```python
page.goto(url, timeout=60000)  # 60 seconds
```

### Rate Limiting
Add delays between requests:
```python
import time
time.sleep(1)  # Wait 1 second between requests
```

## Best Practices

1. **Run homepage tests first** - Quick validation before full crawl
2. **Schedule site-wide crawl** - Run nightly or weekly
3. **Monitor broken links** - Set up alerts for failures
4. **Update selectors** - If site structure changes, update locators
5. **Review external links** - Some may be temporarily unavailable

## Expected Results

- **Homepage**: ~20-50 links
- **Site-Wide**: ~100-500 links across all pages
- **Navigation**: ~10-20 menu links
- **Footer**: ~15-30 links
- **Dynamic**: Varies based on content

## Maintenance

Update tests when:
- Site structure changes
- New pages are added
- Navigation menu is redesigned
- Footer links change

## Support

For issues or questions:
1. Check test output for specific errors
2. Review Playwright documentation
3. Verify site is accessible
4. Check network connectivity
