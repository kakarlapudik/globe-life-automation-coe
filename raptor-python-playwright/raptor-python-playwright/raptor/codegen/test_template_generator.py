"""
Test Template Generator

Generates pytest test templates from page objects and test scenarios.
"""

import re
from typing import List, Dict, Optional, Set
from dataclasses import dataclass
from pathlib import Path
from enum import Enum


class TestType(Enum):
    """Types of test templates"""
    SMOKE = "smoke"
    FUNCTIONAL = "functional"
    REGRESSION = "regression"
    DATA_DRIVEN = "data_driven"
    E2E = "e2e"


@dataclass
class TestScenario:
    """Test scenario definition"""
    name: str
    description: str
    test_type: TestType
    page_object: str
    steps: List[str]
    assertions: List[str]
    test_data: Optional[Dict] = None
    tags: Optional[List[str]] = None


@dataclass
class GeneratedTest:
    """Result of test generation"""
    file_name: str
    code: str
    test_count: int
    imports: Set[str]


class TestTemplateGenerator:
    """
    Generates pytest test templates from page objects and scenarios.
    
    Features:
    - Creates pytest test functions
    - Generates fixtures and setup/teardown
    - Supports data-driven tests
    - Adds proper assertions and error handling
    - Generates test documentation
    - Supports test markers and tags
    """
    
    def __init__(self):
        """Initialize the test template generator"""
        self.imports = set()
        self.fixtures = []
        self.tests = []
    
    def generate_test_file(
        self,
        page_object_name: str,
        scenarios: List[TestScenario],
        include_fixtures: bool = True
    ) -> GeneratedTest:
        """
        Generate a test file for a page object.
        
        Args:
            page_object_name: Name of the page object class
            scenarios: List of test scenarios
            include_fixtures: Whether to include fixture definitions
            
        Returns:
            GeneratedTest with generated code
        """
        self.imports = set()
        self.fixtures = []
        self.tests = []
        
        # Add base imports
        self._add_base_imports()
        
        # Add page object import
        module_name = self._class_to_module_name(page_object_name)
        self.imports.add(f"from raptor.pages.{module_name} import {page_object_name}")
        
        # Generate fixtures if requested
        if include_fixtures:
            self._generate_fixtures(page_object_name)
        
        # Generate tests for each scenario
        for scenario in scenarios:
            test_code = self._generate_test_function(scenario, page_object_name)
            self.tests.append(test_code)
        
        # Generate complete file code
        file_name = f"test_{module_name}.py"
        code = self._generate_file_code(page_object_name)
        
        return GeneratedTest(
            file_name=file_name,
            code=code,
            test_count=len(self.tests),
            imports=self.imports.copy()
        )
    
    def generate_smoke_test_suite(
        self,
        page_objects: List[str],
        output_dir: Optional[Path] = None
    ) -> Dict[str, GeneratedTest]:
        """
        Generate smoke test suite for multiple page objects.
        
        Args:
            page_objects: List of page object class names
            output_dir: Optional directory to write files to
            
        Returns:
            Dictionary mapping page object names to GeneratedTests
        """
        test_files = {}
        
        for page_object in page_objects:
            # Create basic smoke test scenario
            scenario = TestScenario(
                name=f"verify_{self._class_to_snake_case(page_object)}_loads",
                description=f"Verify that {page_object} loads successfully",
                test_type=TestType.SMOKE,
                page_object=page_object,
                steps=[
                    "Navigate to page",
                    "Wait for page to load",
                    "Verify key elements are visible"
                ],
                assertions=[
                    "Page title is correct",
                    "Main elements are visible"
                ],
                tags=["smoke", "critical"]
            )
            
            test_file = self.generate_test_file(page_object, [scenario])
            test_files[page_object] = test_file
            
            # Write to file if output directory specified
            if output_dir:
                output_path = output_dir / test_file.file_name
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text(test_file.code)
        
        return test_files
    
    def generate_data_driven_test(
        self,
        page_object_name: str,
        test_name: str,
        test_data_source: str,
        steps: List[str]
    ) -> GeneratedTest:
        """
        Generate a data-driven test template.
        
        Args:
            page_object_name: Name of the page object class
            test_name: Name of the test
            test_data_source: Source of test data (e.g., "database", "csv", "json")
            steps: List of test steps
            
        Returns:
            GeneratedTest with data-driven test code
        """
        scenario = TestScenario(
            name=test_name,
            description=f"Data-driven test for {page_object_name}",
            test_type=TestType.DATA_DRIVEN,
            page_object=page_object_name,
            steps=steps,
            assertions=["Verify expected results for each data set"],
            test_data={"source": test_data_source}
        )
        
        return self.generate_test_file(page_object_name, [scenario])
    
    def _add_base_imports(self):
        """Add base imports required for tests"""
        self.imports.add("import pytest")
        self.imports.add("from playwright.async_api import Page, expect")
        self.imports.add("from raptor.core.browser_manager import BrowserManager")
        self.imports.add("from raptor.core.element_manager import ElementManager")
    
    def _generate_fixtures(self, page_object_name: str):
        """Generate pytest fixtures"""
        # Browser fixture
        browser_fixture = '''@pytest.fixture
async def browser():
    """Provide a browser instance for tests."""
    browser_manager = BrowserManager()
    browser = await browser_manager.launch_browser("chromium", headless=True)
    yield browser
    await browser_manager.close_browser()
'''
        self.fixtures.append(browser_fixture)
        
        # Page fixture
        page_fixture = '''@pytest.fixture
async def page(browser):
    """Provide a page instance for tests."""
    context = await browser.new_context()
    page = await context.new_page()
    yield page
    await page.close()
    await context.close()
'''
        self.fixtures.append(page_fixture)
        
        # Page object fixture
        snake_case_name = self._class_to_snake_case(page_object_name)
        page_object_fixture = f'''@pytest.fixture
async def {snake_case_name}(page):
    """Provide a {page_object_name} instance for tests."""
    element_manager = ElementManager(page)
    return {page_object_name}(page, element_manager)
'''
        self.fixtures.append(page_object_fixture)
    
    def _generate_test_function(
        self,
        scenario: TestScenario,
        page_object_name: str
    ) -> str:
        """Generate a test function from a scenario"""
        # Generate test name
        test_name = f"test_{scenario.name}"
        
        # Generate markers
        markers = []
        if scenario.tags:
            for tag in scenario.tags:
                markers.append(f"@pytest.mark.{tag}")
        
        # Add asyncio marker
        markers.append("@pytest.mark.asyncio")
        
        markers_str = '\n'.join(markers)
        
        # Generate fixture parameter
        fixture_param = self._class_to_snake_case(page_object_name)
        
        # Generate docstring
        docstring = f'''    """
    {scenario.description}
    
    Test Type: {scenario.test_type.value}
    
    Steps:
{self._format_steps(scenario.steps)}
    
    Assertions:
{self._format_assertions(scenario.assertions)}
    """'''
        
        # Generate test body based on test type
        if scenario.test_type == TestType.DATA_DRIVEN:
            test_body = self._generate_data_driven_body(scenario, fixture_param)
        else:
            test_body = self._generate_standard_body(scenario, fixture_param)
        
        return f'''{markers_str}
async def {test_name}({fixture_param}):
{docstring}
{test_body}
'''
    
    def _generate_standard_body(
        self,
        scenario: TestScenario,
        fixture_param: str
    ) -> str:
        """Generate standard test body"""
        steps = []
        
        # Add setup comment
        steps.append("    # Arrange")
        steps.append(f"    page_object = {fixture_param}")
        steps.append("")
        
        # Add action comment
        steps.append("    # Act")
        for i, step in enumerate(scenario.steps, 1):
            steps.append(f"    # Step {i}: {step}")
            steps.append(f"    # TODO: Implement step {i}")
        steps.append("")
        
        # Add assertion comment
        steps.append("    # Assert")
        for i, assertion in enumerate(scenario.assertions, 1):
            steps.append(f"    # Assertion {i}: {assertion}")
            steps.append(f"    # TODO: Implement assertion {i}")
        
        return '\n'.join(steps)
    
    def _generate_data_driven_body(
        self,
        scenario: TestScenario,
        fixture_param: str
    ) -> str:
        """Generate data-driven test body"""
        data_source = scenario.test_data.get('source', 'database') if scenario.test_data else 'database'
        
        steps = []
        steps.append("    # Arrange")
        steps.append(f"    page_object = {fixture_param}")
        steps.append(f"    # TODO: Load test data from {data_source}")
        steps.append("    test_data = []  # Replace with actual data loading")
        steps.append("")
        steps.append("    # Act & Assert")
        steps.append("    for data_row in test_data:")
        steps.append("        # TODO: Execute test steps with data_row")
        steps.append("        # TODO: Verify results")
        steps.append("        pass")
        
        return '\n'.join(steps)
    
    def _format_steps(self, steps: List[str]) -> str:
        """Format steps for docstring"""
        return '\n'.join(f"    - {step}" for step in steps)
    
    def _format_assertions(self, assertions: List[str]) -> str:
        """Format assertions for docstring"""
        return '\n'.join(f"    - {assertion}" for assertion in assertions)
    
    def _generate_file_code(self, page_object_name: str) -> str:
        """Generate complete file code"""
        # Sort imports
        imports_str = '\n'.join(sorted(self.imports))
        
        # Generate file docstring
        file_docstring = f'''"""
Tests for {page_object_name}.

This test file was auto-generated by RAPTOR TestTemplateGenerator.
"""'''
        
        # Combine all parts
        fixtures_str = '\n\n'.join(self.fixtures) if self.fixtures else ""
        tests_str = '\n\n'.join(self.tests)
        
        code = f'''{file_docstring}

{imports_str}


{fixtures_str}


{tests_str}
'''
        
        return code
    
    def _class_to_module_name(self, class_name: str) -> str:
        """Convert class name to module name"""
        # Convert to snake_case first
        snake_case = self._class_to_snake_case(class_name)
        
        # Ensure it ends with '_page' if not already
        if not snake_case.endswith('_page') and not snake_case.endswith('page'):
            snake_case += '_page'
        elif snake_case.endswith('page') and not snake_case.endswith('_page'):
            # Convert 'homepage' to 'home_page'
            snake_case = snake_case[:-4] + '_page'
        
        return snake_case
    
    def _class_to_snake_case(self, class_name: str) -> str:
        """Convert class name to snake_case"""
        # Insert underscore before uppercase letters
        snake_case = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', class_name)
        snake_case = re.sub(r'([a-z\d])([A-Z])', r'\1_\2', snake_case)
        return snake_case.lower()
    
    def generate_conftest(
        self,
        output_path: Path,
        include_database: bool = False,
        include_config: bool = True
    ):
        """
        Generate conftest.py with common fixtures.
        
        Args:
            output_path: Path to write conftest.py
            include_database: Whether to include database fixtures
            include_config: Whether to include config fixtures
        """
        imports = [
            "import pytest",
            "from playwright.async_api import Page",
            "from raptor.core.browser_manager import BrowserManager",
            "from raptor.core.element_manager import ElementManager",
        ]
        
        if include_config:
            imports.append("from raptor.core.config_manager import ConfigManager")
        
        if include_database:
            imports.append("from raptor.database.database_manager import DatabaseManager")
        
        fixtures = []
        
        # Browser manager fixture
        fixtures.append('''@pytest.fixture(scope="session")
async def browser_manager():
    """Provide a browser manager for the test session."""
    manager = BrowserManager()
    yield manager
    await manager.close_browser()
''')
        
        # Config fixture
        if include_config:
            fixtures.append('''@pytest.fixture(scope="session")
def config():
    """Provide configuration for tests."""
    return ConfigManager()
''')
        
        # Database fixture
        if include_database:
            fixtures.append('''@pytest.fixture(scope="session")
async def database(config):
    """Provide database connection for tests."""
    db_config = config.get("database", {})
    db = DatabaseManager(
        connection_string=db_config.get("connection_string"),
        user=db_config.get("user"),
        password=db_config.get("password")
    )
    await db.connect()
    yield db
    await db.disconnect()
''')
        
        conftest_code = f'''"""
Common pytest fixtures for RAPTOR tests.

Auto-generated by RAPTOR TestTemplateGenerator.
"""

{chr(10).join(imports)}


{chr(10).join(fixtures)}
'''
        
        output_path.write_text(conftest_code)
