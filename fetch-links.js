const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  // Navigate to the page
  await page.goto('https://investors.globelifeinsurance.com/');
  
  // Click the hamburger menu to reveal all links
  await page.click('.navbar-toggler');
  
  // Wait a moment for menu to expand
  await page.waitForTimeout(1000);
  
  // Fetch all links on the page
  const links = await page.evaluate(() => {
    const anchors = Array.from(document.querySelectorAll('a'));
    return anchors.map(anchor => ({
      text: anchor.innerText.trim(),
      href: anchor.href,
      target: anchor.target || '_self'
    })).filter(link => link.href); // Filter out empty hrefs
  });
  
  // Display results
  console.log(`Found ${links.length} links:\n`);
  links.forEach((link, index) => {
    console.log(`${index + 1}. ${link.text || '(no text)'}`);
    console.log(`   URL: ${link.href}`);
    console.log(`   Target: ${link.target}\n`);
  });
  
  // Save to JSON file
  const fs = require('fs');
  fs.writeFileSync('links.json', JSON.stringify(links, null, 2));
  console.log('Links saved to links.json');
  
  await browser.close();
})();
