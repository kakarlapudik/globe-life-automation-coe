"""
Java to Python Test Converter

Converts Java Selenium test code to Python Playwright test code.
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ConversionResult:
    """Result of a Java to Python conversion"""
    python_code: str
    warnings: List[str]
    manual_review_needed: List[str]
    conversion_stats: Dict[str, int]


class JavaToPythonConverter:
    """
    Converts Java Selenium test code to Python Playwright test code.
    
    This converter handles common patterns in RAPTOR Java tests and converts
    them to equivalent Python Playwright code.
    """
    
    # Method mapping from Java to Python
    METHOD_MAPPINGS = {
        # Click operations
        'click(': 'await element_manager.click(',
        'clickXY(': 'await element_manager.click_at_position(',
        'clickIfExists(': 'await element_manager.click_if_exists(',
        'clickSync(': 'await element_manager.click_with_sync(',
        'doubleClick(': 'await element_manager.double_click(',
        'rightClick(': 'await element_manager.right_click(',
        
        # Input operations
        'type(': 'await element_manager.fill(',
        'sendKeys(': 'await element_manager.fill(',
        'clear(': 'await element_manager.clear(',
        'selectOption(': 'await element_manager.select_option(',
        
        # Verification operations
        'verifyExists(': 'await verification.verify_exists(',
        'verifyNotExists(': 'await verification.verify_not_exists(',
        'verifyEnabled(': 'await verification.verify_enabled(',
        'verifyDisabled(': 'await verification.verify_disabled(',
        'verifyVisible(': 'await verification.verify_visible(',
        'verifyText(': 'await verification.verify_text(',
        
        # Wait operations
        'waitForElement(': 'await element_manager.wait_for_element(',
        'waitForLoadState(': 'await page.wait_for_load_state(',
        'waitForSpinner(': 'await element_manager.wait_for_spinner(',
        'waitForDisabledPane(': 'await element_manager.wait_for_disabled_pane(',
        
        # Element state operations
        'isVisible(': 'await element_manager.is_visible(',
        'isEnabled(': 'await element_manager.is_enabled(',
        'getText(': 'await element_manager.get_text(',
        'getAttribute(': 'await element_manager.get_attribute(',
        
        # Table operations
        'findRowByKey(': 'await table_manager.find_row_by_key(',
        'getCellValue(': 'await table_manager.get_cell_value(',
        'setCellValue(': 'await table_manager.set_cell_value(',
        'clickCell(': 'await table_manager.click_cell(',
        
        # Database operations
        'databaseImport(': 'await database_manager.import_data(',
        'databaseExport(': 'await database_manager.export_data(',
        'databaseQuery(': 'await database_manager.query_field(',
        'databaseExec(': 'await database_manager.execute_update(',
        
        # Navigation
        'navigate(': 'await page.navigate(',
        'goTo(': 'await page.goto(',
        
        # Screenshot
        'takeScreenshot(': 'await page.screenshot(',
    }
    
    # Type mappings
    TYPE_MAPPINGS = {
        'String': 'str',
        'Integer': 'int',
        'Boolean': 'bool',
        'Double': 'float',
        'List<String>': 'List[str]',
        'Map<String, String>': 'Dict[str, str]',
        'void': 'None',
    }
    
    def __init__(self):
        """Initialize the converter"""
        self.warnings = []
        self.manual_review_needed = []
        self.conversion_stats = {
            'methods_converted': 0,
            'types_converted': 0,
            'imports_added': 0,
            'async_methods_created': 0,
        }
    
    def convert_file(self, java_code: str) -> ConversionResult:
        """
        Convert a Java test file to Python.
        
        Args:
            java_code: Java source code as string
            
        Returns:
            ConversionResult with converted code and metadata
        """
        self.warnings = []
        self.manual_review_needed = []
        self.conversion_stats = {
            'methods_converted': 0,
            'types_converted': 0,
            'imports_added': 0,
            'async_methods_created': 0,
        }
        
        # Extract class name
        class_name = self._extract_class_name(java_code)
        
        # Convert imports
        python_imports = self._convert_imports(java_code)
        
        # Convert class structure
        python_class = self._convert_class(java_code, class_name)
        
        # Convert methods
        python_methods = self._convert_methods(java_code)
        
        # Assemble Python code
        python_code = self._assemble_python_code(
            python_imports,
            python_class,
            python_methods
        )
        
        return ConversionResult(
            python_code=python_code,
            warnings=self.warnings,
            manual_review_needed=self.manual_review_needed,
            conversion_stats=self.conversion_stats
        )
    
    def convert_method(self, java_method: str) -> str:
        """
        Convert a single Java method to Python.
        
        Args:
            java_method: Java method code as string
            
        Returns:
            Converted Python method code
        """
        python_method = java_method
        
        # Convert method signature
        python_method = self._convert_method_signature(python_method)
        
        # Convert method calls
        for java_call, python_call in self.METHOD_MAPPINGS.items():
            if java_call in python_method:
                python_method = python_method.replace(java_call, python_call)
                self.conversion_stats['methods_converted'] += 1
        
        # Convert types
        for java_type, python_type in self.TYPE_MAPPINGS.items():
            python_method = python_method.replace(java_type, python_type)
        
        # Convert variable declarations
        python_method = self._convert_variable_declarations(python_method)
        
        # Convert control structures
        python_method = self._convert_control_structures(python_method)
        
        return python_method
    
    def _extract_class_name(self, java_code: str) -> str:
        """Extract class name from Java code"""
        match = re.search(r'public\s+class\s+(\w+)', java_code)
        if match:
            return match.group(1)
        return 'ConvertedTest'
    
    def _convert_imports(self, java_code: str) -> str:
        """Convert Java imports to Python imports"""
        imports = [
            'import pytest',
            'from typing import Dict, List, Optional',
            'from raptor.core.browser_manager import BrowserManager',
            'from raptor.core.element_manager import ElementManager',
            'from raptor.pages.base_page import BasePage',
            'from raptor.pages.table_manager import TableManager',
            'from raptor.database.database_manager import DatabaseManager',
            'from raptor.core.config_manager import ConfigManager',
        ]
        
        self.conversion_stats['imports_added'] = len(imports)
        return '\n'.join(imports)
    
    def _convert_class(self, java_code: str, class_name: str) -> str:
        """Convert Java class structure to Python"""
        python_class = f'''
class {class_name}:
    """
    Converted from Java Selenium test to Python Playwright test.
    
    Note: This is an auto-generated conversion. Please review and test thoroughly.
    """
    
    def __init__(self):
        """Initialize test class"""
        self.browser_manager = None
        self.element_manager = None
        self.page = None
        self.config = ConfigManager()
    
    async def setup(self):
        """Setup test environment"""
        self.browser_manager = BrowserManager()
        browser = await self.browser_manager.launch_browser('chromium')
        context = await self.browser_manager.create_context()
        self.page = await self.browser_manager.create_page(context)
        self.element_manager = ElementManager(self.page)
    
    async def teardown(self):
        """Cleanup test environment"""
        if self.browser_manager:
            await self.browser_manager.close_browser()
'''
        return python_class
    
    def _convert_methods(self, java_code: str) -> str:
        """Convert Java methods to Python"""
        # Extract methods using regex
        method_pattern = r'(public|private|protected)\s+(\w+)\s+(\w+)\s*\((.*?)\)\s*\{([^}]*)\}'
        methods = re.finditer(method_pattern, java_code, re.DOTALL)
        
        python_methods = []
        for match in methods:
            visibility, return_type, method_name, params, body = match.groups()
            
            # Skip constructors
            if method_name == self._extract_class_name(java_code):
                continue
            
            # Convert method
            python_method = self._convert_single_method(
                method_name, params, body, return_type
            )
            python_methods.append(python_method)
            self.conversion_stats['async_methods_created'] += 1
        
        return '\n\n'.join(python_methods)
    
    def _convert_single_method(
        self,
        method_name: str,
        params: str,
        body: str,
        return_type: str
    ) -> str:
        """Convert a single Java method to Python"""
        # Convert parameters
        python_params = self._convert_parameters(params)
        
        # Convert return type
        python_return = self.TYPE_MAPPINGS.get(return_type, 'None')
        
        # Convert body
        python_body = self._convert_method_body(body)
        
        # Build method
        method = f'''    async def {method_name}(self{python_params}) -> {python_return}:
        """
        Converted from Java method.
        
        Note: Please review this method for correctness.
        """
{python_body}'''
        
        return method
    
    def _convert_parameters(self, params: str) -> str:
        """Convert Java parameters to Python"""
        if not params.strip():
            return ''
        
        python_params = []
        for param in params.split(','):
            param = param.strip()
            if not param:
                continue
            
            # Extract type and name
            parts = param.split()
            if len(parts) >= 2:
                param_type = parts[0]
                param_name = parts[1]
                python_type = self.TYPE_MAPPINGS.get(param_type, 'Any')
                python_params.append(f'{param_name}: {python_type}')
            else:
                python_params.append(param)
        
        if python_params:
            return ', ' + ', '.join(python_params)
        return ''
    
    def _convert_method_body(self, body: str) -> str:
        """Convert Java method body to Python"""
        python_body = body
        
        # Convert method calls
        for java_call, python_call in self.METHOD_MAPPINGS.items():
            python_body = python_body.replace(java_call, python_call)
        
        # Convert variable declarations
        python_body = self._convert_variable_declarations(python_body)
        
        # Convert control structures
        python_body = self._convert_control_structures(python_body)
        
        # Add proper indentation
        lines = python_body.split('\n')
        indented_lines = ['        ' + line.strip() for line in lines if line.strip()]
        
        return '\n'.join(indented_lines)
    
    def _convert_method_signature(self, method: str) -> str:
        """Convert Java method signature to Python"""
        # Convert public/private/protected to Python (no direct equivalent)
        method = re.sub(r'(public|private|protected)\s+', '', method)
        
        # Convert method declaration
        method = re.sub(
            r'(\w+)\s+(\w+)\s*\((.*?)\)',
            r'async def \2(self, \3)',
            method
        )
        
        return method
    
    def _convert_variable_declarations(self, code: str) -> str:
        """Convert Java variable declarations to Python"""
        # Convert: Type varName = value; to varName = value
        code = re.sub(
            r'(\w+)\s+(\w+)\s*=\s*([^;]+);',
            r'\2 = \3',
            code
        )
        
        # Remove semicolons
        code = code.replace(';', '')
        
        return code
    
    def _convert_control_structures(self, code: str) -> str:
        """Convert Java control structures to Python"""
        # Convert if statements
        code = re.sub(r'if\s*\((.*?)\)\s*\{', r'if \1:', code)
        
        # Convert else if to elif
        code = re.sub(r'}\s*else\s+if\s*\((.*?)\)\s*\{', r'elif \1:', code)
        
        # Convert else
        code = re.sub(r'}\s*else\s*\{', r'else:', code)
        
        # Convert for loops
        code = re.sub(
            r'for\s*\((.*?)\s+(\w+)\s*:\s*(.*?)\)\s*\{',
            r'for \2 in \3:',
            code
        )
        
        # Convert while loops
        code = re.sub(r'while\s*\((.*?)\)\s*\{', r'while \1:', code)
        
        # Remove closing braces
        code = code.replace('}', '')
        
        return code
    
    def _assemble_python_code(
        self,
        imports: str,
        class_def: str,
        methods: str
    ) -> str:
        """Assemble the final Python code"""
        header = '''"""
Auto-generated Python Playwright test from Java Selenium test.

WARNING: This code has been automatically converted and requires manual review.
Please verify:
1. All method calls are correct
2. Async/await is properly used
3. Element locators are valid
4. Test logic is preserved
5. Error handling is appropriate
"""

'''
        
        return header + imports + '\n\n' + class_def + '\n' + methods
    
    def get_conversion_summary(self) -> str:
        """Get a summary of the conversion"""
        summary = f"""
Conversion Summary:
==================
Methods Converted: {self.conversion_stats['methods_converted']}
Types Converted: {self.conversion_stats['types_converted']}
Imports Added: {self.conversion_stats['imports_added']}
Async Methods Created: {self.conversion_stats['async_methods_created']}

Warnings: {len(self.warnings)}
Manual Review Items: {len(self.manual_review_needed)}
"""
        
        if self.warnings:
            summary += "\n\nWarnings:\n"
            for warning in self.warnings:
                summary += f"  - {warning}\n"
        
        if self.manual_review_needed:
            summary += "\n\nManual Review Needed:\n"
            for item in self.manual_review_needed:
                summary += f"  - {item}\n"
        
        return summary
