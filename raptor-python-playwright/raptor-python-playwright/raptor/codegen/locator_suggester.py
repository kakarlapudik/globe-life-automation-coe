"""
Locator Suggestion Tool

Suggests optimal locators for web elements based on various strategies.
"""

import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class LocatorStrategy(Enum):
    """Locator strategies"""
    ROLE = "role"  # Accessibility-first (best practice)
    TEST_ID = "test_id"  # data-testid attribute
    ID = "id"  # Element ID
    TEXT = "text"  # Visible text
    CSS = "css"  # CSS selector
    XPATH = "xpath"  # XPath expression


class LocatorPriority(Enum):
    """Priority levels for locator suggestions"""
    EXCELLENT = 1  # Highly recommended
    GOOD = 2  # Recommended
    ACCEPTABLE = 3  # Acceptable but not ideal
    POOR = 4  # Not recommended


@dataclass
class LocatorSuggestion:
    """A suggested locator"""
    strategy: LocatorStrategy
    locator: str
    priority: LocatorPriority
    confidence: float  # 0.0 to 1.0
    reason: str
    playwright_syntax: str
    example_usage: str


@dataclass
class ElementInfo:
    """Information about a web element"""
    tag_name: str
    id: Optional[str] = None
    classes: Optional[List[str]] = None
    text: Optional[str] = None
    role: Optional[str] = None
    test_id: Optional[str] = None
    name: Optional[str] = None
    type: Optional[str] = None
    aria_label: Optional[str] = None
    placeholder: Optional[str] = None
    title: Optional[str] = None
    href: Optional[str] = None
    parent_tag: Optional[str] = None
    siblings_count: Optional[int] = None


class LocatorSuggester:
    """
    Suggests optimal locators for web elements.
    
    Features:
    - Prioritizes accessibility-first locators (role, label)
    - Suggests test-id based locators
    - Provides fallback strategies
    - Ranks suggestions by reliability and maintainability
    - Generates Playwright-specific syntax
    - Provides usage examples
    """
    
    # Playwright role types
    VALID_ROLES = {
        'alert', 'alertdialog', 'application', 'article', 'banner',
        'blockquote', 'button', 'caption', 'cell', 'checkbox',
        'code', 'columnheader', 'combobox', 'complementary',
        'contentinfo', 'definition', 'deletion', 'dialog', 'directory',
        'document', 'emphasis', 'feed', 'figure', 'form', 'generic',
        'grid', 'gridcell', 'group', 'heading', 'img', 'insertion',
        'link', 'list', 'listbox', 'listitem', 'log', 'main',
        'marquee', 'math', 'meter', 'menu', 'menubar', 'menuitem',
        'menuitemcheckbox', 'menuitemradio', 'navigation', 'none',
        'note', 'option', 'paragraph', 'presentation', 'progressbar',
        'radio', 'radiogroup', 'region', 'row', 'rowgroup',
        'rowheader', 'scrollbar', 'search', 'searchbox', 'separator',
        'slider', 'spinbutton', 'status', 'strong', 'subscript',
        'superscript', 'switch', 'tab', 'table', 'tablist', 'tabpanel',
        'term', 'textbox', 'time', 'timer', 'toolbar', 'tooltip',
        'tree', 'treegrid', 'treeitem'
    }
    
    def __init__(self):
        """Initialize the locator suggester"""
        pass
    
    def suggest_locators(
        self,
        element_info: ElementInfo,
        max_suggestions: int = 5
    ) -> List[LocatorSuggestion]:
        """
        Suggest locators for an element.
        
        Args:
            element_info: Information about the element
            max_suggestions: Maximum number of suggestions to return
            
        Returns:
            List of LocatorSuggestions, sorted by priority and confidence
        """
        suggestions = []
        
        # Try role-based locator (highest priority)
        role_suggestions = self._suggest_role_locators(element_info)
        suggestions.extend(role_suggestions)
        
        # Try test-id locator
        if element_info.test_id:
            test_id_suggestion = self._suggest_test_id_locator(element_info)
            suggestions.append(test_id_suggestion)
        
        # Try ID locator
        if element_info.id:
            id_suggestion = self._suggest_id_locator(element_info)
            suggestions.append(id_suggestion)
        
        # Try text locator
        if element_info.text:
            text_suggestions = self._suggest_text_locators(element_info)
            suggestions.extend(text_suggestions)
        
        # Try CSS locators
        css_suggestions = self._suggest_css_locators(element_info)
        suggestions.extend(css_suggestions)
        
        # Try XPath locators (lowest priority)
        xpath_suggestions = self._suggest_xpath_locators(element_info)
        suggestions.extend(xpath_suggestions)
        
        # Sort by priority and confidence
        suggestions.sort(key=lambda s: (s.priority.value, -s.confidence))
        
        return suggestions[:max_suggestions]
    
    def _suggest_role_locators(
        self,
        element_info: ElementInfo
    ) -> List[LocatorSuggestion]:
        """Suggest role-based locators"""
        suggestions = []
        
        if element_info.role and element_info.role.lower() in self.VALID_ROLES:
            # Role with name
            if element_info.aria_label or element_info.text:
                name = element_info.aria_label or element_info.text
                locator = f"role={element_info.role}, name={name}"
                playwright_syntax = f'page.get_by_role("{element_info.role}", name="{name}")'
                
                suggestions.append(LocatorSuggestion(
                    strategy=LocatorStrategy.ROLE,
                    locator=locator,
                    priority=LocatorPriority.EXCELLENT,
                    confidence=0.95,
                    reason="Accessibility-first approach using ARIA role and name",
                    playwright_syntax=playwright_syntax,
                    example_usage=f'await {playwright_syntax}.click()'
                ))
            
            # Role only
            locator = f"role={element_info.role}"
            playwright_syntax = f'page.get_by_role("{element_info.role}")'
            
            suggestions.append(LocatorSuggestion(
                strategy=LocatorStrategy.ROLE,
                locator=locator,
                priority=LocatorPriority.GOOD,
                confidence=0.85,
                reason="Accessibility-first approach using ARIA role",
                playwright_syntax=playwright_syntax,
                example_usage=f'await {playwright_syntax}.click()'
            ))
        
        # Infer role from tag and type
        inferred_role = self._infer_role(element_info)
        if inferred_role and inferred_role not in [s.locator for s in suggestions]:
            locator = f"role={inferred_role}"
            playwright_syntax = f'page.get_by_role("{inferred_role}")'
            
            suggestions.append(LocatorSuggestion(
                strategy=LocatorStrategy.ROLE,
                locator=locator,
                priority=LocatorPriority.GOOD,
                confidence=0.80,
                reason=f"Inferred role from {element_info.tag_name} element",
                playwright_syntax=playwright_syntax,
                example_usage=f'await {playwright_syntax}.click()'
            ))
        
        return suggestions
    
    def _suggest_test_id_locator(
        self,
        element_info: ElementInfo
    ) -> LocatorSuggestion:
        """Suggest test-id based locator"""
        locator = f"test_id={element_info.test_id}"
        playwright_syntax = f'page.get_by_test_id("{element_info.test_id}")'
        
        return LocatorSuggestion(
            strategy=LocatorStrategy.TEST_ID,
            locator=locator,
            priority=LocatorPriority.EXCELLENT,
            confidence=0.90,
            reason="Test-specific identifier, stable and reliable",
            playwright_syntax=playwright_syntax,
            example_usage=f'await {playwright_syntax}.click()'
        )
    
    def _suggest_id_locator(
        self,
        element_info: ElementInfo
    ) -> LocatorSuggestion:
        """Suggest ID-based locator"""
        # Check if ID looks stable (not auto-generated)
        is_stable = not self._looks_auto_generated(element_info.id)
        
        priority = LocatorPriority.GOOD if is_stable else LocatorPriority.ACCEPTABLE
        confidence = 0.85 if is_stable else 0.60
        reason = "Unique ID attribute" if is_stable else "ID may be auto-generated, verify stability"
        
        locator = f"id={element_info.id}"
        playwright_syntax = f'page.locator("#{element_info.id}")'
        
        return LocatorSuggestion(
            strategy=LocatorStrategy.ID,
            locator=locator,
            priority=priority,
            confidence=confidence,
            reason=reason,
            playwright_syntax=playwright_syntax,
            example_usage=f'await {playwright_syntax}.click()'
        )
    
    def _suggest_text_locators(
        self,
        element_info: ElementInfo
    ) -> List[LocatorSuggestion]:
        """Suggest text-based locators"""
        suggestions = []
        
        if not element_info.text:
            return suggestions
        
        text = element_info.text.strip()
        
        # Exact text match
        if len(text) < 50:  # Only for reasonably short text
            locator = f"text={text}"
            playwright_syntax = f'page.get_by_text("{text}", exact=True)'
            
            suggestions.append(LocatorSuggestion(
                strategy=LocatorStrategy.TEXT,
                locator=locator,
                priority=LocatorPriority.GOOD,
                confidence=0.75,
                reason="Exact text match, good for buttons and links",
                playwright_syntax=playwright_syntax,
                example_usage=f'await {playwright_syntax}.click()'
            ))
        
        # Partial text match
        if len(text) > 10:
            partial_text = text[:20] if len(text) > 20 else text
            locator = f"text~={partial_text}"
            playwright_syntax = f'page.get_by_text("{partial_text}")'
            
            suggestions.append(LocatorSuggestion(
                strategy=LocatorStrategy.TEXT,
                locator=locator,
                priority=LocatorPriority.ACCEPTABLE,
                confidence=0.65,
                reason="Partial text match, may match multiple elements",
                playwright_syntax=playwright_syntax,
                example_usage=f'await {playwright_syntax}.first.click()'
            ))
        
        return suggestions
    
    def _suggest_css_locators(
        self,
        element_info: ElementInfo
    ) -> List[LocatorSuggestion]:
        """Suggest CSS-based locators"""
        suggestions = []
        
        # ID-based CSS (if ID exists)
        if element_info.id:
            locator = f"css=#{element_info.id}"
            playwright_syntax = f'page.locator("#{element_info.id}")'
            
            suggestions.append(LocatorSuggestion(
                strategy=LocatorStrategy.CSS,
                locator=locator,
                priority=LocatorPriority.GOOD,
                confidence=0.80,
                reason="CSS selector using ID",
                playwright_syntax=playwright_syntax,
                example_usage=f'await {playwright_syntax}.click()'
            ))
        
        # Class-based CSS
        if element_info.classes and len(element_info.classes) > 0:
            # Use first class or combination
            class_selector = '.'.join(element_info.classes[:2])
            locator = f"css={element_info.tag_name}.{class_selector}"
            playwright_syntax = f'page.locator("{element_info.tag_name}.{class_selector}")'
            
            suggestions.append(LocatorSuggestion(
                strategy=LocatorStrategy.CSS,
                locator=locator,
                priority=LocatorPriority.ACCEPTABLE,
                confidence=0.60,
                reason="CSS selector using classes, may not be unique",
                playwright_syntax=playwright_syntax,
                example_usage=f'await {playwright_syntax}.first.click()'
            ))
        
        # Attribute-based CSS
        if element_info.name:
            locator = f"css={element_info.tag_name}[name='{element_info.name}']"
            playwright_syntax = f'page.locator("{element_info.tag_name}[name=\'{element_info.name}\']")'
            
            suggestions.append(LocatorSuggestion(
                strategy=LocatorStrategy.CSS,
                locator=locator,
                priority=LocatorPriority.GOOD,
                confidence=0.75,
                reason="CSS selector using name attribute",
                playwright_syntax=playwright_syntax,
                example_usage=f'await {playwright_syntax}.click()'
            ))
        
        if element_info.type:
            locator = f"css={element_info.tag_name}[type='{element_info.type}']"
            playwright_syntax = f'page.locator("{element_info.tag_name}[type=\'{element_info.type}\']")'
            
            suggestions.append(LocatorSuggestion(
                strategy=LocatorStrategy.CSS,
                locator=locator,
                priority=LocatorPriority.ACCEPTABLE,
                confidence=0.65,
                reason="CSS selector using type attribute",
                playwright_syntax=playwright_syntax,
                example_usage=f'await {playwright_syntax}.click()'
            ))
        
        return suggestions
    
    def _suggest_xpath_locators(
        self,
        element_info: ElementInfo
    ) -> List[LocatorSuggestion]:
        """Suggest XPath-based locators (last resort)"""
        suggestions = []
        
        # XPath with ID
        if element_info.id:
            locator = f"xpath=//{element_info.tag_name}[@id='{element_info.id}']"
            playwright_syntax = f'page.locator("xpath=//{element_info.tag_name}[@id=\'{element_info.id}\']")'
            
            suggestions.append(LocatorSuggestion(
                strategy=LocatorStrategy.XPATH,
                locator=locator,
                priority=LocatorPriority.ACCEPTABLE,
                confidence=0.70,
                reason="XPath using ID, prefer CSS or role-based locators",
                playwright_syntax=playwright_syntax,
                example_usage=f'await {playwright_syntax}.click()'
            ))
        
        # XPath with text
        if element_info.text and len(element_info.text) < 50:
            locator = f"xpath=//{element_info.tag_name}[text()='{element_info.text}']"
            playwright_syntax = f'page.locator("xpath=//{element_info.tag_name}[text()=\'{element_info.text}\']")'
            
            suggestions.append(LocatorSuggestion(
                strategy=LocatorStrategy.XPATH,
                locator=locator,
                priority=LocatorPriority.POOR,
                confidence=0.55,
                reason="XPath with text, prefer get_by_text() method",
                playwright_syntax=playwright_syntax,
                example_usage=f'await {playwright_syntax}.click()'
            ))
        
        return suggestions
    
    def _infer_role(self, element_info: ElementInfo) -> Optional[str]:
        """Infer ARIA role from element information"""
        tag = element_info.tag_name.lower()
        
        # Map common HTML elements to ARIA roles
        role_map = {
            'button': 'button',
            'a': 'link',
            'input': self._infer_input_role(element_info),
            'textarea': 'textbox',
            'select': 'combobox',
            'h1': 'heading',
            'h2': 'heading',
            'h3': 'heading',
            'h4': 'heading',
            'h5': 'heading',
            'h6': 'heading',
            'nav': 'navigation',
            'main': 'main',
            'header': 'banner',
            'footer': 'contentinfo',
            'aside': 'complementary',
            'article': 'article',
            'section': 'region',
            'form': 'form',
            'table': 'table',
            'ul': 'list',
            'ol': 'list',
            'li': 'listitem',
            'img': 'img',
            'dialog': 'dialog',
        }
        
        return role_map.get(tag)
    
    def _infer_input_role(self, element_info: ElementInfo) -> Optional[str]:
        """Infer role for input elements based on type"""
        if not element_info.type:
            return 'textbox'
        
        input_type = element_info.type.lower()
        
        type_role_map = {
            'text': 'textbox',
            'email': 'textbox',
            'password': 'textbox',
            'search': 'searchbox',
            'tel': 'textbox',
            'url': 'textbox',
            'number': 'spinbutton',
            'checkbox': 'checkbox',
            'radio': 'radio',
            'button': 'button',
            'submit': 'button',
            'reset': 'button',
            'range': 'slider',
        }
        
        return type_role_map.get(input_type, 'textbox')
    
    def _looks_auto_generated(self, value: str) -> bool:
        """Check if a value looks auto-generated"""
        # Check for common auto-generated patterns
        patterns = [
            r'^[a-f0-9]{8,}$',  # Long hex strings
            r'^\d{10,}$',  # Long numbers
            r'^[a-z0-9]{20,}$',  # Long random strings
            r'_\d{10,}$',  # Timestamp suffixes
            r'^(ember|react|vue|angular)\d+',  # Framework-generated IDs
        ]
        
        for pattern in patterns:
            if re.search(pattern, value, re.IGNORECASE):
                return True
        
        return False
    
    def generate_locator_report(
        self,
        suggestions: List[LocatorSuggestion]
    ) -> str:
        """Generate a formatted report of locator suggestions"""
        report = ["Locator Suggestions", "=" * 50, ""]
        
        for i, suggestion in enumerate(suggestions, 1):
            priority_emoji = {
                LocatorPriority.EXCELLENT: "🟢",
                LocatorPriority.GOOD: "🟡",
                LocatorPriority.ACCEPTABLE: "🟠",
                LocatorPriority.POOR: "🔴",
            }
            
            report.append(f"{i}. {priority_emoji[suggestion.priority]} {suggestion.strategy.value.upper()}")
            report.append(f"   Locator: {suggestion.locator}")
            report.append(f"   Priority: {suggestion.priority.name}")
            report.append(f"   Confidence: {suggestion.confidence:.0%}")
            report.append(f"   Reason: {suggestion.reason}")
            report.append(f"   Playwright: {suggestion.playwright_syntax}")
            report.append(f"   Example: {suggestion.example_usage}")
            report.append("")
        
        return '\n'.join(report)
