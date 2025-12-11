import org.openqa.selenium.By;

/**
 * Salesforce Lead Details Page Locators
 * Auto-generated from: https://globesales--uat.sandbox.my.salesforce.com
 * Lead: Neal Heidenreich
 */
public class SalesforceLeadLocators {
    
    // Page Elements
    public static final By txt_Loading = By.xpath("//span[text()='Loading']");
    public static final By txt_Sorry_to_interrupt = By.xpath("//span[text()='Sorry to interrupt']");
    public static final By txt_Search = By.xpath("//span[text()='Search']");
    public static final By txt_Search_Placeholder = By.xpath("//span[text()='Search...']");
    public static final By txt_Loading_Ellipsis = By.xpath("//span[text()='Loading...']");
    public static final By txt_Notifications = By.xpath("//span[text()='Notifications']");
    public static final By txt_Follow = By.xpath("//span[text()='Follow']");
    
    // Tab Navigation
    public static final By txt_DETAILS = By.xpath("//span[text()='DETAILS']");
    public static final By txt_RELATED = By.xpath("//span[text()='RELATED']");
    public static final By txt_ACTIVITY = By.xpath("//span[text()='ACTIVITY']");
    
    // Activity Feed
    public static final By txt_Post = By.xpath("//span[text()='Post']");
    public static final By txt_Share_an_update = By.xpath("//span[text()='Share an update...']");
    public static final By txt_Share = By.xpath("//span[text()='Share']");
    public static final By txt_Refresh_this_feed = By.xpath("//span[text()='Refresh this feed']");
    
    // Record Header
    public static final By txt_Lead_Neal_Heidenreich = By.xpath("//span[text()='Lead: Neal Heidenreich']");
    
    // Common Actions
    public static final By btn_Cancel = By.xpath("//button[contains(text(),'Cancel')]");
    public static final By btn_Search = By.xpath("//button[contains(text(),'Search')]");
    public static final By btn_Follow = By.xpath("//button[contains(text(),'Follow')]");
    public static final By btn_Share = By.xpath("//button[contains(text(),'Share')]");
    
    // Input Fields
    public static final By input_Search = By.xpath("//input[@placeholder='Search...']");
    
    // Links
    public static final By link_Details_Tab = By.linkText("DETAILS");
    public static final By link_Related_Tab = By.linkText("RELATED");
    public static final By link_Activity_Tab = By.linkText("ACTIVITY");
    public static final By link_Post = By.linkText("Post");
    
    /**
     * Get dynamic locator for any span text
     */
    public static By getSpanByText(String text) {
        return By.xpath("//span[text()='" + text + "']");
    }
    
    /**
     * Get dynamic locator for any button text
     */
    public static By getButtonByText(String text) {
        return By.xpath("//button[contains(text(),'" + text + "')]");
    }
    
    /**
     * Get dynamic locator for tab by name
     */
    public static By getTabByName(String tabName) {
        return By.xpath("//span[text()='" + tabName.toUpperCase() + "']");
    }
}
