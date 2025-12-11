import org.openqa.selenium.By;

/**
 * Page Object Model for Salesforce Lead Details Tab
 * Auto-generated locators for: Neal Heidenreich Lead Record
 * URL: https://globesales--uat.sandbox.my.salesforce.com
 */
public class SalesforceDetailsTabLocators {
    
    // ========== INPUT FIELDS ==========
    
    public static class InputFields {
        // Search field
        public static final By SEARCH_INPUT = By.id("187:0");
        public static final By SEARCH_INPUT_XPATH = By.xpath("//*[@id='187:0']");
    }
    
    // ========== BUTTONS ==========
    
    public static class Buttons {
        // Cancel button
        public static final By CANCEL_BUTTON = By.xpath("/html/body/div[3]/div[1]/div[1]/div[3]/div[1]/div[2]/button[1]");
        public static final By CANCEL_BUTTON_CSS = By.cssSelector(".slds-button");
        
        // Search button
        public static final By SEARCH_BUTTON = By.xpath("/html/body/div[3]/div[1]/div[1]/div[4]/div[1]/button[1]");
        
        // Notifications button
        public static final By NOTIFICATIONS_BUTTON = By.xpath("/html/body/div[3]/div[1]/div[1]/div[4]/div[3]/div[1]/div[1]/div[1]/button[1]");
        
        // Follow button
        public static final By FOLLOW_BUTTON = By.xpath("/div[1]/div[1]/div[2]/div[1]/span[1]/div[1]/button[1]");
        
        // Share an update button
        public static final By SHARE_UPDATE_BUTTON = By.xpath("//*[@id='1203:0']/div[1]/div[1]/button[1]");
        
        // Share button
        public static final By SHARE_BUTTON = By.xpath("//*[@id='1203:0']/div[1]/div[1]/button[2]");
        
        // Refresh feed button
        public static final By REFRESH_FEED_BUTTON = By.xpath("//*[@id='5:938;a']/div[2]/div[1]/div[1]/div[1]/button[1]");
    }
    
    // ========== NAVIGATION LINKS ==========
    
    public static class NavigationLinks {
        // Dismiss error link
        public static final By DISMISS_ERROR_LINK = By.id("dismissError");
        public static final By DISMISS_ERROR_LINK_XPATH = By.xpath("//*[@id='dismissError']");
        
        // Refresh page link
        public static final By REFRESH_PAGE_LINK = By.id("auraErrorReload");
        public static final By REFRESH_PAGE_LINK_XPATH = By.xpath("//*[@id='auraErrorReload']");
        
        // Details tab
        public static final By DETAILS_TAB = By.xpath("/html/body/div[3]/div[1]/div[3]/div[1]/div[1]/div[2]/div[2]/div[1]/div[3]/div[1]/div[1]/div[1]/div[1]/ul[1]/li[1]/a[1]");
        public static final By DETAILS_TAB_TEXT = By.linkText("DETAILS");
        
        // Related tab
        public static final By RELATED_TAB = By.xpath("/html/body/div[3]/div[1]/div[3]/div[1]/div[1]/div[2]/div[2]/div[1]/div[3]/div[1]/div[1]/div[1]/div[1]/ul[1]/li[2]/a[1]");
        public static final By RELATED_TAB_TEXT = By.linkText("RELATED");
        
        // Activity tab
        public static final By ACTIVITY_TAB = By.xpath("/html/body/div[3]/div[1]/div[3]/div[1]/div[1]/div[2]/div[2]/div[1]/div[3]/div[1]/div[1]/div[1]/div[1]/ul[1]/li[3]/a[1]");
        public static final By ACTIVITY_TAB_TEXT = By.linkText("ACTIVITY");
        
        // Post link
        public static final By POST_LINK = By.xpath("/html/body/div[3]/div[1]/div[3]/div[1]/div[1]/div[2]/div[2]/div[1]/div[3]/div[1]/div[2]/div[1]/div[1]/div[1]/ul[1]/li[1]/a[1]");
        public static final By POST_LINK_TEXT = By.linkText("Post");
        
        // More link
        public static final By MORE_LINK = By.xpath("//*[@id='1173:0']/div[1]/div[1]/a[1]");
        public static final By MORE_LINK_TEXT = By.linkText("More");
        
        // Skip feed link
        public static final By SKIP_FEED_LINK = By.xpath("//*[@id='5:938;a']/div[2]/div[1]/div[2]/a[1]");
        public static final By SKIP_FEED_LINK_TEXT = By.linkText("Skip Feed");
    }
    
    // ========== HELPER METHODS ==========
    
    /**
     * Get locator by element type and label
     */
    public static By getLocatorByLabel(String elementType, String label) {
        switch (elementType.toUpperCase()) {
            case "BUTTON":
                return By.xpath("//button[contains(text(), '" + label + "')]");
            case "LINK":
                return By.linkText(label);
            case "INPUT":
                return By.xpath("//input[@placeholder='" + label + "' or @aria-label='" + label + "']");
            default:
                return null;
        }
    }
    
    /**
     * Get dynamic XPath for tab by name
     */
    public static By getTabByName(String tabName) {
        return By.xpath("//a[contains(text(), '" + tabName.toUpperCase() + "')]");
    }
}
