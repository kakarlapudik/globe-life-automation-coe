import com.microsoft.playwright.*;
import com.microsoft.playwright.options.*;
import java.util.*;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import java.io.FileWriter;
import java.io.IOException;

public class FetchLinks {
    
    public static class LinkInfo {
        public String text;
        public String href;
        public String target;
        public String xpath;
        
        public LinkInfo(String text, String href, String target, String xpath) {
            this.text = text;
            this.href = href;
            this.target = target;
            this.xpath = xpath;
        }
    }
    
    public static void main(String[] args) {
        try (Playwright playwright = Playwright.create()) {
            Browser browser = playwright.chromium().launch(new BrowserType.LaunchOptions()
                .setHeadless(false));
            
            BrowserContext context = browser.newContext();
            Page page = context.newPage();
            
            // Navigate to the page
            page.navigate("https://investors.globelifeinsurance.com/");
            
            // Click the hamburger menu to reveal all links
            page.click(".navbar-toggler");
            
            // Wait for menu to expand
            page.waitForTimeout(1000);
            
            // Fetch all links on the page with XPaths
            List<LinkInfo> links = (List<LinkInfo>) page.evaluate("() => {" +
                "function getXPath(element) {" +
                "  if (element.id) return '//*[@id=\"' + element.id + '\"]';" +
                "  if (element === document.body) return '/html/body';" +
                "  let ix = 0;" +
                "  const siblings = element.parentNode.childNodes;" +
                "  for (let i = 0; i < siblings.length; i++) {" +
                "    const sibling = siblings[i];" +
                "    if (sibling === element) {" +
                "      return getXPath(element.parentNode) + '/' + element.tagName.toLowerCase() + '[' + (ix + 1) + ']';" +
                "    }" +
                "    if (sibling.nodeType === 1 && sibling.tagName === element.tagName) {" +
                "      ix++;" +
                "    }" +
                "  }" +
                "}" +
                "const anchors = Array.from(document.querySelectorAll('a'));" +
                "return anchors.map(anchor => ({" +
                "  text: anchor.innerText.trim()," +
                "  href: anchor.href," +
                "  target: anchor.target || '_self'," +
                "  xpath: getXPath(anchor)" +
                "})).filter(link => link.href);" +
            "}");
            
            // Display results
            System.out.println("Found " + links.size() + " links:\n");
            for (int i = 0; i < links.size(); i++) {
                LinkInfo link = links.get(i);
                System.out.println((i + 1) + ". " + (link.text.isEmpty() ? "(no text)" : link.text));
                System.out.println("   URL: " + link.href);
                System.out.println("   Target: " + link.target);
                System.out.println("   XPath: " + link.xpath + "\n");
            }
            
            // Save to JSON file
            saveLinksToJson(links, "links.json");
            System.out.println("Links saved to links.json");
            
            browser.close();
        }
    }
    
    private static void saveLinksToJson(List<LinkInfo> links, String filename) {
        Gson gson = new GsonBuilder().setPrettyPrinting().create();
        try (FileWriter writer = new FileWriter(filename)) {
            gson.toJson(links, writer);
        } catch (IOException e) {
            System.err.println("Error saving to JSON: " + e.getMessage());
        }
    }
}
