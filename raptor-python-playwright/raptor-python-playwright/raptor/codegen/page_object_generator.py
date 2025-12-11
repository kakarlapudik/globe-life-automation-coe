"""
Page Object Generator

Generates Python page object classes from DDFE element definitions.
"""

import re
from typing import List, Dict, Optional, Set
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ElementDefinition:
    """DDFE Element Definition"""
    pv_name: str
    application_name: str
    field_type: str
    locator_primary: str
    locator_fallback1: Optional[str] = None
    locator_fallback2: Optional[str] = None
    frame: Optional[str] = None
    table_column: Optional[int] = None
    table_key: Optional[int] = None
    analyst: Optional[str] = None


@dataclass
class GeneratedPageObject:
    """Result of page object generation"""
    class_name: str
    file_name: str
    code: str
    imports: Set[str]
    methods: List[str]


class PageObjectGenerator:
    """
    Generates Python page object classes from DDFE element definitions.
    
    Features:
    - Converts DDFE elements to Python methods
    - Generates proper imports and class structure
    - Creates type hints and docstrings
    - Handles fallback locators
    - Supports table operations
    - Generates frame context handling
    """
    
    def __init__(self):
        """Initialize the page object generator"""
        self.imports = set()
        self.methods = []
    
    def generate_page_object(
        self,
        application_name: str,
        elements: List[ElementDefinition],
        base_url: Optional[str] = None
    ) -> GeneratedPageObject:
        """
        Generate a page object class from DDFE elements.
        
        Args:
            application_name: Name of the application/page
            elements: List of element definitions
            base_url: Optional base URL for the page
            
        Returns:
            GeneratedPageObject with generated code
        """
        self.imports = set()
        self.methods = []
        
        # Generate class name
        class_name = self._generate_class_name(application_name)
        file_name = self._generate_file_name(application_name)
        
        # Add required imports
        self._add_base_imports()
        
        # Generate methods for each element
        for element in elements:
            self._generate_element_methods(element)
        
        # Generate the complete class code
        code = self._generate_class_code(
            class_name=class_name,
            application_name=application_name,
            base_url=base_url
        )
        
        return GeneratedPageObject(
            class_name=class_name,
            file_name=file_name,
            code=code,
            imports=self.imports.copy(),
            methods=self.methods.copy()
        )
    
    def generate_multiple_page_objects(
        self,
        elements: List[ElementDefinition],
        output_dir: Optional[Path] = None
    ) -> Dict[str, GeneratedPageObject]:
        """
        Generate multiple page objects grouped by application.
        
        Args:
            elements: List of all element definitions
            output_dir: Optional directory to write files to
            
        Returns:
            Dictionary mapping application names to GeneratedPageObjects
        """
        # Group elements by application
        elements_by_app = {}
        for element in elements:
            app_name = element.application_name
            if app_name not in elements_by_app:
                elements_by_app[app_name] = []
            elements_by_app[app_name].append(element)
        
        # Generate page object for each application
        page_objects = {}
        for app_name, app_elements in elements_by_app.items():
            page_object = self.generate_page_object(app_name, app_elements)
            page_objects[app_name] = page_object
            
            # Write to file if output directory specified
            if output_dir:
                output_path = output_dir / page_object.file_name
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text(page_object.code)
        
        return page_objects
    
    def _generate_class_name(self, application_name: str) -> str:
        """Generate a Python class name from application name"""
        # Check if already ends with 'Page' (case-sensitive)
        if application_name.endswith('Page'):
            return application_name
        
        # Remove special characters and convert to PascalCase
        words = re.findall(r'[a-zA-Z0-9]+', application_name)
        class_name = ''.join(word.capitalize() for word in words)
        
        # Ensure it ends with 'Page' if not already (case-insensitive check)
        if not class_name.lower().endswith('page'):
            class_name += 'Page'
        
        return class_name
    
    def _generate_file_name(self, application_name: str) -> str:
        """Generate a Python file name from application name"""
        # Convert to snake_case
        words = re.findall(r'[a-zA-Z0-9]+', application_name)
        file_name = '_'.join(word.lower() for word in words)
        
        # Ensure it ends with '_page' if not already
        if not file_name.endswith('_page') and not file_name.endswith('page'):
            file_name += '_page'
        elif file_name.endswith('page') and not file_name.endswith('_page'):
            # Convert 'homepage' to 'home_page'
            file_name = file_name[:-4] + '_page'
        
        return f"{file_name}.py"
    
    def _add_base_imports(self):
        """Add base imports required for page objects"""
        self.imports.add("from typing import Optional, List")
        self.imports.add("from playwright.async_api import Page, Locator")
        self.imports.add("from raptor.pages.base_page import BasePage")
        self.imports.add("from raptor.core.element_manager import ElementManager")
    
    def _generate_element_methods(self, element: ElementDefinition):
        """Generate methods for an element"""
        method_name = self._generate_method_name(element.pv_name)
        
        # Generate locator method
        locator_method = self._generate_locator_method(element, method_name)
        self.methods.append(locator_method)
        
        # Generate interaction methods based on field type
        if element.field_type.lower() in ['button', 'link']:
            click_method = self._generate_click_method(element, method_name)
            self.methods.append(click_method)
        
        elif element.field_type.lower() in ['textbox', 'input', 'textarea']:
            fill_method = self._generate_fill_method(element, method_name)
            self.methods.append(fill_method)
            get_value_method = self._generate_get_value_method(element, method_name)
            self.methods.append(get_value_method)
        
        elif element.field_type.lower() in ['dropdown', 'select']:
            select_method = self._generate_select_method(element, method_name)
            self.methods.append(select_method)
        
        elif element.field_type.lower() == 'checkbox':
            check_method = self._generate_check_method(element, method_name)
            self.methods.append(check_method)
        
        elif element.field_type.lower() == 'table':
            self.imports.add("from raptor.pages.table_manager import TableManager")
            table_methods = self._generate_table_methods(element, method_name)
            self.methods.extend(table_methods)
        
        # Always generate visibility check method
        is_visible_method = self._generate_is_visible_method(element, method_name)
        self.methods.append(is_visible_method)
    
    def _generate_method_name(self, pv_name: str) -> str:
        """Generate a Python method name from PV name"""
        # Convert to snake_case
        # Remove special characters
        clean_name = re.sub(r'[^a-zA-Z0-9_]', '_', pv_name)
        # Convert to snake_case
        snake_case = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', clean_name)
        snake_case = re.sub(r'([a-z\d])([A-Z])', r'\1_\2', snake_case)
        snake_case = snake_case.lower()
        # Remove consecutive underscores
        snake_case = re.sub(r'_+', '_', snake_case)
        # Remove leading/trailing underscores
        snake_case = snake_case.strip('_')
        
        return snake_case
    
    def _generate_locator_method(
        self,
        element: ElementDefinition,
        method_name: str
    ) -> str:
        """Generate a method that returns the element locator"""
        fallbacks = []
        if element.locator_fallback1:
            fallbacks.append(f'"{element.locator_fallback1}"')
        if element.locator_fallback2:
            fallbacks.append(f'"{element.locator_fallback2}"')
        
        fallback_str = f", fallback_locators=[{', '.join(fallbacks)}]" if fallbacks else ""
        
        frame_context = ""
        if element.frame:
            frame_context = f"\n        # Frame context: {element.frame}"
        
        return f'''    async def get_{method_name}_locator(self) -> Locator:
        """
        Get locator for {element.pv_name}.
        
        Field Type: {element.field_type}
        Primary Locator: {element.locator_primary}
        {f"Fallback Locators: {', '.join(fallbacks)}" if fallbacks else ""}
        
        Returns:
            Playwright Locator for the element
        """{frame_context}
        return await self.element_manager.locate_element(
            "{element.locator_primary}"{fallback_str}
        )
'''
    
    def _generate_click_method(
        self,
        element: ElementDefinition,
        method_name: str
    ) -> str:
        """Generate a click method for button/link elements"""
        return f'''    async def click_{method_name}(self):
        """Click the {element.pv_name} {element.field_type}."""
        locator = await self.get_{method_name}_locator()
        await self.element_manager.click(locator)
'''
    
    def _generate_fill_method(
        self,
        element: ElementDefinition,
        method_name: str
    ) -> str:
        """Generate a fill method for input elements"""
        return f'''    async def fill_{method_name}(self, text: str):
        """
        Fill the {element.pv_name} field with text.
        
        Args:
            text: Text to enter into the field
        """
        locator = await self.get_{method_name}_locator()
        await self.element_manager.fill(locator, text)
'''
    
    def _generate_get_value_method(
        self,
        element: ElementDefinition,
        method_name: str
    ) -> str:
        """Generate a method to get the value of an input element"""
        return f'''    async def get_{method_name}_value(self) -> str:
        """
        Get the current value of the {element.pv_name} field.
        
        Returns:
            Current value of the field
        """
        locator = await self.get_{method_name}_locator()
        return await self.element_manager.get_value(locator)
'''
    
    def _generate_select_method(
        self,
        element: ElementDefinition,
        method_name: str
    ) -> str:
        """Generate a select method for dropdown elements"""
        return f'''    async def select_{method_name}(self, value: str):
        """
        Select an option from the {element.pv_name} dropdown.
        
        Args:
            value: Value or text of the option to select
        """
        locator = await self.get_{method_name}_locator()
        await self.element_manager.select_option(locator, value)
'''
    
    def _generate_check_method(
        self,
        element: ElementDefinition,
        method_name: str
    ) -> str:
        """Generate check/uncheck methods for checkbox elements"""
        return f'''    async def check_{method_name}(self, checked: bool = True):
        """
        Check or uncheck the {element.pv_name} checkbox.
        
        Args:
            checked: True to check, False to uncheck
        """
        locator = await self.get_{method_name}_locator()
        if checked:
            await locator.check()
        else:
            await locator.uncheck()
    
    async def is_{method_name}_checked(self) -> bool:
        """
        Check if the {element.pv_name} checkbox is checked.
        
        Returns:
            True if checked, False otherwise
        """
        locator = await self.get_{method_name}_locator()
        return await locator.is_checked()
'''
    
    def _generate_table_methods(
        self,
        element: ElementDefinition,
        method_name: str
    ) -> List[str]:
        """Generate methods for table elements"""
        methods = []
        
        # Find row method
        methods.append(f'''    async def find_{method_name}_row(self, key_value: str) -> int:
        """
        Find a row in the {element.pv_name} table by key value.
        
        Args:
            key_value: Value to search for in the key column
            
        Returns:
            Row index (0-based)
        """
        locator = await self.get_{method_name}_locator()
        table_manager = TableManager(self.page, self.element_manager)
        return await table_manager.find_row_by_key(
            locator,
            key_column={element.table_key or 0},
            key_value=key_value
        )
''')
        
        # Get cell value method
        if element.table_column is not None:
            methods.append(f'''    async def get_{method_name}_cell_value(self, row: int) -> str:
        """
        Get cell value from the {element.pv_name} table.
        
        Args:
            row: Row index (0-based)
            
        Returns:
            Cell value as string
        """
        locator = await self.get_{method_name}_locator()
        table_manager = TableManager(self.page, self.element_manager)
        return await table_manager.get_cell_value(
            locator,
            row=row,
            column={element.table_column}
        )
''')
        
        return methods
    
    def _generate_is_visible_method(
        self,
        element: ElementDefinition,
        method_name: str
    ) -> str:
        """Generate a visibility check method"""
        return f'''    async def is_{method_name}_visible(self) -> bool:
        """
        Check if the {element.pv_name} is visible.
        
        Returns:
            True if visible, False otherwise
        """
        locator = await self.get_{method_name}_locator()
        return await self.element_manager.is_visible(locator)
'''
    
    def _generate_class_code(
        self,
        class_name: str,
        application_name: str,
        base_url: Optional[str] = None
    ) -> str:
        """Generate the complete class code"""
        # Sort imports
        imports_str = '\n'.join(sorted(self.imports))
        
        # Generate methods
        methods_str = '\n'.join(self.methods)
        
        # Generate URL property if base_url provided
        url_property = ""
        if base_url:
            url_property = f'''
    @property
    def url(self) -> str:
        """Get the URL for this page."""
        return "{base_url}"
'''
        
        # Generate class docstring
        class_docstring = f'''"""
Page Object for {application_name}.

This class was auto-generated from DDFE element definitions.
It provides methods to interact with elements on the {application_name} page.

Generated by: RAPTOR PageObjectGenerator
"""'''
        
        code = f'''{class_docstring}

{imports_str}


class {class_name}(BasePage):
    """Page object for {application_name}."""
    
    def __init__(self, page: Page, element_manager: ElementManager):
        """
        Initialize the {class_name}.
        
        Args:
            page: Playwright Page instance
            element_manager: ElementManager instance
        """
        super().__init__(page, element_manager)
{url_property}

{methods_str}
'''
        
        return code
    
    def generate_init_file(
        self,
        page_objects: Dict[str, GeneratedPageObject],
        output_path: Path
    ):
        """
        Generate __init__.py file for page objects module.
        
        Args:
            page_objects: Dictionary of generated page objects
            output_path: Path to write __init__.py
        """
        imports = []
        all_exports = []
        
        for app_name, page_object in page_objects.items():
            module_name = page_object.file_name.replace('.py', '')
            imports.append(
                f"from .{module_name} import {page_object.class_name}"
            )
            all_exports.append(f"    '{page_object.class_name}',")
        
        init_code = f'''"""
Auto-generated page objects from DDFE definitions.

Generated by: RAPTOR PageObjectGenerator
"""

{chr(10).join(imports)}

__all__ = [
{chr(10).join(all_exports)}
]
'''
        
        output_path.write_text(init_code)
