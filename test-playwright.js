const { chromium } = require('playwright');

(async () => {
  console.log('Starting Playwright test...');
  
  try {
    // Launch browser
    const browser = await chromium.launch({ headless: false });
    console.log('✓ Browser launched successfully');
    
    // Create context and page
    const context = await browser.newContext();
    const page = await context.newPage();
    console.log('✓ Page created successfully');
    
    // Navigate to a test page
    await page.goto('https://example.com');
    console.log('✓ Navigation successful');
    
    // Get page title
    const title = await page.title();
    console.log(`✓ Page title: ${title}`);
    
    // Take a screenshot
    await page.screenshot({ path: 'playwright-test-screenshot.png' });
    console.log('✓ Screenshot saved: playwright-test-screenshot.png');
    
    // Close browser
    await browser.close();
    console.log('✓ Browser closed successfully');
    
    console.log('\n✅ Playwright is fully accessible and working!');
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  }
})();
