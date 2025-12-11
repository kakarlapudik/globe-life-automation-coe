"""
AI Test Automation Agent
Processes requirement documents to extract use cases, generate test cases,
identify automation candidates, and create Playwright Python scripts.
"""

import json
import re
from typing import List, Dict, Any
from dataclasses import dataclass, asdict
from enum import Enum


class AutomationPriority(Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    NOT_SUITABLE = "Not Suitable"


@dataclass
class UseCase:
    id: str
    title: str
    description: str
    preconditions: List[str]
    steps: List[str]
    expected_results: List[str]
    priority: str


@dataclass
class TestCase:
    id: str
    use_case_id: str
    title: str
    description: str
    test_steps: List[Dict[str, str]]
    expected_result: str
    automation_priority: str
    automation_feasibility_score: float
    automation_rationale: str


@dataclass
class AutomationScript:
    test_case_id: str
    script_name: str
    script_content: str
    page_objects: List[str]
    dependencies: List[str]


class RequirementParser:
    """Parses requirement documents to extract use cases and requirements"""
    
    def __init__(self, document_text: str):
        self.document_text = document_text
        self.use_cases = []
        self.requirements = []
    
    def parse(self) -> Dict[str, Any]:
        """Main parsing method"""
        self.extract_use_cases()
        self.extract_requirements()
        
        return {
            "use_cases": [asdict(uc) for uc in self.use_cases],
            "requirements": self.requirements
        }
    
    def extract_use_cases(self):
        """Extract use cases from document"""
        # Pattern to match use case sections
        uc_pattern = r"(?:Use Case|UC)[\s#]*(\d+)[:\s]*([^\n]+)\n(.*?)(?=(?:Use Case|UC)[\s#]*\d+|$)"
        
        matches = re.finditer(uc_pattern, self.document_text, re.DOTALL | re.IGNORECASE)
        
        for match in matches:
            uc_id = f"UC{match.group(1).zfill(3)}"
            title = match.group(2).strip()
            content = match.group(3).strip()
            
            # Extract components
            description = self._extract_section(content, "Description")
            preconditions = self._extract_list(content, "Preconditions?")
            steps = self._extract_list(content, "Steps?|Flow")
            expected_results = self._extract_list(content, "Expected Results?|Postconditions?")
            priority = self._extract_priority(content)
            
            use_case = UseCase(
                id=uc_id,
                title=title,
                description=description,
                preconditions=preconditions,
                steps=steps,
                expected_results=expected_results,
                priority=priority
            )
            
            self.use_cases.append(use_case)
    
    def extract_requirements(self):
        """Extract functional requirements"""
        req_pattern = r"(?:REQ|Requirement)[\s#]*(\d+)[:\s]*([^\n]+)"
        matches = re.finditer(req_pattern, self.document_text, re.IGNORECASE)
        
        for match in matches:
            self.requirements.append({
                "id": f"REQ{match.group(1).zfill(3)}",
                "description": match.group(2).strip()
            })
    
    def _extract_section(self, text: str, section_name: str) -> str:
        if not text:
            return ""
        pattern = rf"{section_name}[:\s]*([^\n]+(?:\n(?!\w+:)[^\n]+)*)"
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else ""
    
    def _extract_list(self, text: str, section_name: str) -> List[str]:
        if not text:
            return []
        pattern = rf"{section_name}[:\s]*((?:[\n\s]*[-•\d.]+[^\n]+)+)"
        match = re.search(pattern, text, re.IGNORECASE)
        
        if match and match.group(1) is not None:
            items = re.findall(r"[-•\d.]+\s*([^\n]+)", match.group(1))
            return [item.strip() for item in items if item.strip()]
        return []
    
    def _extract_priority(self, text: str) -> str:
        if not text:
            return "Medium"
        priority_match = re.search(r"Priority[:\s]*(High|Medium|Low)", text, re.IGNORECASE)
        return priority_match.group(1).capitalize() if priority_match else "Medium"


class TestCaseGenerator:
    """Generates test cases from use cases"""
    
    def __init__(self, use_cases: List[UseCase]):
        self.use_cases = use_cases
        self.test_cases = []
    
    def generate(self) -> List[TestCase]:
        """Generate test cases from use cases"""
        for uc in self.use_cases:
            # Generate positive test case
            positive_tc = self._create_positive_test_case(uc)
            self.test_cases.append(positive_tc)
            
            # Generate negative test cases
            negative_tcs = self._create_negative_test_cases(uc)
            self.test_cases.extend(negative_tcs)
        
        return self.test_cases
    
    def _create_positive_test_case(self, use_case: UseCase) -> TestCase:
        """Create positive/happy path test case"""
        test_steps = []
        for i, step in enumerate(use_case.steps, 1):
            test_steps.append({
                "step_number": i,
                "action": step,
                "expected": use_case.expected_results[i-1] if i-1 < len(use_case.expected_results) else "Step completes successfully"
            })
        
        automation_score, rationale = self._calculate_automation_feasibility(use_case, test_steps)
        
        return TestCase(
            id=f"{use_case.id}_TC001",
            use_case_id=use_case.id,
            title=f"{use_case.title} - Positive Flow",
            description=f"Verify {use_case.title.lower()} works correctly with valid inputs",
            test_steps=test_steps,
            expected_result="; ".join(use_case.expected_results),
            automation_priority=self._determine_automation_priority(automation_score),
            automation_feasibility_score=automation_score,
            automation_rationale=rationale
        )
    
    def _create_negative_test_cases(self, use_case: UseCase) -> List[TestCase]:
        """Create negative test cases"""
        negative_tcs = []
        
        # Generate validation test cases
        if any(keyword in use_case.description.lower() for keyword in ['form', 'input', 'field', 'enter']):
            tc = TestCase(
                id=f"{use_case.id}_TC002",
                use_case_id=use_case.id,
                title=f"{use_case.title} - Invalid Input Validation",
                description="Verify system handles invalid inputs correctly",
                test_steps=[
                    {"step_number": 1, "action": "Enter invalid data", "expected": "Validation error displayed"}
                ],
                expected_result="Appropriate error messages shown",
                automation_priority="High",
                automation_feasibility_score=0.9,
                automation_rationale="Input validation is highly automatable"
            )
            negative_tcs.append(tc)
        
        return negative_tcs
    
    def _calculate_automation_feasibility(self, use_case: UseCase, test_steps: List[Dict]) -> tuple:
        """Calculate automation feasibility score (0-1)"""
        score = 0.5  # Base score
        rationale_parts = []
        
        # UI-based interactions are good candidates
        ui_keywords = ['click', 'enter', 'select', 'navigate', 'fill', 'submit', 'verify']
        ui_count = sum(1 for step in use_case.steps if any(kw in step.lower() for kw in ui_keywords))
        if ui_count > 0:
            score += 0.2
            rationale_parts.append("Contains UI interactions")
        
        # Repetitive tests are good candidates
        if len(test_steps) > 5:
            score += 0.1
            rationale_parts.append("Multiple steps benefit from automation")
        
        # API/manual verification reduces score
        if any(kw in use_case.description.lower() for kw in ['manual', 'review', 'approve']):
            score -= 0.2
            rationale_parts.append("Contains manual verification steps")
        
        # High priority increases score
        if use_case.priority == "High":
            score += 0.1
            rationale_parts.append("High priority use case")
        
        score = max(0.0, min(1.0, score))
        rationale = "; ".join(rationale_parts) if rationale_parts else "Standard automation candidate"
        
        return score, rationale
    
    def _determine_automation_priority(self, score: float) -> str:
        """Determine automation priority based on feasibility score"""
        if score >= 0.8:
            return AutomationPriority.HIGH.value
        elif score >= 0.6:
            return AutomationPriority.MEDIUM.value
        elif score >= 0.4:
            return AutomationPriority.LOW.value
        else:
            return AutomationPriority.NOT_SUITABLE.value


class PlaywrightScriptGenerator:
    """Generates Playwright Python automation scripts"""
    
    def __init__(self, test_cases: List[TestCase], base_url: str = "https://your-application-url.com"):
        self.test_cases = test_cases
        self.base_url = base_url
        self.scripts = []
    
    def generate(self) -> List[AutomationScript]:
        """Generate Playwright scripts for automatable test cases"""
        for tc in self.test_cases:
            if tc.automation_priority in [AutomationPriority.HIGH.value, AutomationPriority.MEDIUM.value, AutomationPriority.LOW.value]:
                script = self._create_playwright_script(tc)
                self.scripts.append(script)
        
        return self.scripts
    
    def _create_playwright_script(self, test_case: TestCase) -> AutomationScript:
        """Create Playwright Python script for a test case"""
        script_name = f"test_{test_case.id.lower()}.py"
        
        # Generate comprehensive link validation script
        script_content = f'''"""
Test Case: {test_case.title}
Test ID: {test_case.id}
Description: {test_case.description}
Automation Priority: {test_case.automation_priority}
"""

import pytest
import requests
import json
import os
from urllib.parse import urljoin, urlparse
from playwright.sync_api import Page, expect


class Test{test_case.id}:
    """
    {test_case.title}
    """
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Setup before each test"""
        self.page = page
        self.base_url = "{self.base_url}"
        self.all_links = []
        self.broken_links = []
        self.valid_links = []
        
        # Create reports directory
        os.makedirs("reports", exist_ok=True)
    
    def test_{test_case.id.lower()}_positive_flow(self):
        """
        Test: {test_case.title}
        Expected: Comprehensive link validation with detailed reporting
        """
        page = self.page
        
        # Navigate to application
        page.goto(self.base_url)
        
        # Wait for page to load completely
        page.wait_for_load_state("networkidle")
        
        # Extract all links from the page
        print(f"\\n[EXTRACT] Extracting links from {{self.base_url}}")
        links = page.locator("a[href]").all()
        
        for link in links:
            try:
                href = link.get_attribute("href")
                text = link.inner_text().strip()[:50]  # Limit text length
                
                if href:
                    # Convert relative URLs to absolute
                    full_url = urljoin(self.base_url, href)
                    
                    # Skip non-HTTP links
                    if not full_url.startswith(('http://', 'https://')):
                        continue
                    
                    self.all_links.append({{
                        'url': full_url,
                        'text': text,
                        'original_href': href
                    }})
            except Exception as e:
                print(f"[WARN] Error extracting link: {{e}}")
        
        print(f"[INFO] Found {{len(self.all_links)}} links to validate")
        
        # Validate each link
        self._validate_links()
        
        # Generate summary report
        self._generate_report()
        
        # Print results summary
        print(f"\\n{'='*60}")
        print(f"Total Links Validated: {{len(self.all_links)}}")
        print(f"Broken Links: {{len(self.broken_links)}}")
        print(f"{'='*60}")
        
        if self.broken_links:
            print(f"\\n[ERROR] BROKEN LINKS FOUND:")
            for link in self.broken_links:
                print(f"  - {{link['url']}} (Status: {{link['status']}})")
        
        # Assert acceptable results (allow 403 status codes as they may be intentional)
        critical_broken_links = [link for link in self.broken_links 
                               if link['status'] not in [403]]
        
        assert len(critical_broken_links) == 0, f"Found {{len(critical_broken_links)}} critical broken links"
    
    def _validate_links(self):
        """Validate all extracted links"""
        session = requests.Session()
        session.verify = False  # Disable SSL verification for corporate environments
        
        for link_data in self.all_links:
            url = link_data['url']
            try:
                # Use HEAD request for faster validation
                response = session.head(url, timeout=30, allow_redirects=True)
                status_code = response.status_code
                
                link_result = {{
                    'url': url,
                    'text': link_data['text'],
                    'status': status_code,
                    'valid': status_code < 400
                }}
                
                if status_code < 400:
                    self.valid_links.append(link_result)
                    print(f"[OK] {{url}} - Status: {{status_code}}")
                else:
                    self.broken_links.append(link_result)
                    print(f"[FAIL] {{url}} - Status: {{status_code}}")
                    
            except Exception as e:
                link_result = {{
                    'url': url,
                    'text': link_data['text'],
                    'status': 'ERROR',
                    'error': str(e),
                    'valid': False
                }}
                self.broken_links.append(link_result)
                print(f"[ERROR] {{url}} - Error: {{e}}")
    
    def _generate_report(self):
        """Generate detailed JSON report"""
        report_data = {{
            'test_case': '{test_case.id}',
            'base_url': self.base_url,
            'total_links': len(self.all_links),
            'valid_links_count': len(self.valid_links),
            'broken_links_count': len(self.broken_links),
            'valid_links': self.valid_links,
            'broken_links': self.broken_links,
            'summary': {{
                'success_rate': f"{{(len(self.valid_links) / len(self.all_links) * 100):.1f}}%" if self.all_links else "0%",
                'total_validated': len(self.all_links)
            }}
        }}
        
        report_file = f"reports/{{'{test_case.id}'.lower()}}_links_report.json"
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\\n[REPORT] Report saved to: {{report_file}}")
    
    def teardown_method(self):
        """Cleanup after test"""
        # Add cleanup logic if needed
        pass
'''
        
        return AutomationScript(
            test_case_id=test_case.id,
            script_name=script_name,
            script_content=script_content,
            page_objects=self._identify_page_objects(test_case),
            dependencies=["pytest", "playwright"]
        )
    
    def _generate_step_code(self, step: Dict[str, str]) -> str:
        """Generate Python code for a test step"""
        action = step['action'].lower()
        step_num = step['step_number']
        
        code = f"\n        # Step {step_num}: {step['action']}\n"
        
        if 'click' in action:
            element = self._extract_element(action)
            code += f'        page.click("{element}")\n'
        elif 'enter' in action or 'fill' in action or 'type' in action:
            element = self._extract_element(action)
            code += f'        page.fill("{element}", "test_data")\n'
        elif 'select' in action:
            element = self._extract_element(action)
            code += f'        page.select_option("{element}", "option_value")\n'
        elif 'navigate' in action or 'go to' in action:
            code += f'        page.goto(self.base_url + "/path")\n'
        elif 'verify' in action or 'check' in action:
            element = self._extract_element(action)
            code += f'        expect(page.locator("{element}")).to_be_visible()\n'
        else:
            code += f'        # TODO: Implement - {step["action"]}\n'
        
        code += f'        # Expected: {step["expected"]}\n'
        
        return code
    
    def _extract_element(self, action: str) -> str:
        """Extract element identifier from action description"""
        # Simple extraction - in production, use NLP or more sophisticated parsing
        words = action.split()
        for i, word in enumerate(words):
            if word in ['button', 'field', 'link', 'input', 'dropdown']:
                if i > 0:
                    return f"[aria-label='{words[i-1]}']"
        return "[data-testid='element']"
    
    def _identify_page_objects(self, test_case: TestCase) -> List[str]:
        """Identify page objects needed for the test"""
        page_objects = set()
        
        for step in test_case.test_steps:
            action = step['action'].lower()
            if 'login' in action:
                page_objects.add("LoginPage")
            elif 'dashboard' in action:
                page_objects.add("DashboardPage")
            elif 'form' in action:
                page_objects.add("FormPage")
        
        return list(page_objects)


class AITestAutomationAgent:
    """Main AI agent orchestrating the entire process"""
    
    def __init__(self):
        self.parser = None
        self.test_generator = None
        self.script_generator = None
        self.results = {}
        self.base_url = "https://your-application-url.com"  # Default fallback
    
    def process_requirements(self, document_text: str) -> Dict[str, Any]:
        """
        Main method to process requirements document
        
        Args:
            document_text: Raw text from requirements document
            
        Returns:
            Dictionary containing all generated artifacts
        """
        print("[AI AGENT] AI Test Automation Agent Started")
        print("=" * 60)
        
        # Step 1: Parse requirements
        print("\n[STEP 1] Parsing requirements document...")
        self.parser = RequirementParser(document_text)
        parsed_data = self.parser.parse()
        print(f"   [OK] Extracted {len(parsed_data['use_cases'])} use cases")
        print(f"   [OK] Extracted {len(parsed_data['requirements'])} requirements")
        
        # Extract Base URL from Test Data section
        self._extract_base_url(document_text)
        
        # Step 2: Generate test cases
        print("\n[STEP 2] Generating test cases...")
        self.test_generator = TestCaseGenerator(self.parser.use_cases)
        test_cases = self.test_generator.generate()
        print(f"   [OK] Generated {len(test_cases)} test cases")
        
        # Step 3: Identify automation candidates
        print("\n[STEP 3] Identifying automation candidates...")
        automation_candidates = [tc for tc in test_cases if tc.automation_priority != AutomationPriority.NOT_SUITABLE.value]
        print(f"   [OK] Identified {len(automation_candidates)} automation candidates")
        
        high_priority = len([tc for tc in automation_candidates if tc.automation_priority == AutomationPriority.HIGH.value])
        medium_priority = len([tc for tc in automation_candidates if tc.automation_priority == AutomationPriority.MEDIUM.value])
        low_priority = len([tc for tc in automation_candidates if tc.automation_priority == AutomationPriority.LOW.value])
        print(f"     - High Priority: {high_priority}")
        print(f"     - Medium Priority: {medium_priority}")
        print(f"     - Low Priority: {low_priority}")
        
        # Step 4: Generate Playwright scripts
        print("\n[STEP 4] Generating Playwright Python scripts...")
        self.script_generator = PlaywrightScriptGenerator(test_cases, self.base_url)
        scripts = self.script_generator.generate()
        print(f"   [OK] Generated {len(scripts)} automation scripts")
        
        # Compile results
        self.results = {
            "use_cases": parsed_data['use_cases'],
            "requirements": parsed_data['requirements'],
            "test_cases": [asdict(tc) for tc in test_cases],
            "automation_scripts": [asdict(script) for script in scripts],
            "summary": {
                "total_use_cases": len(parsed_data['use_cases']),
                "total_requirements": len(parsed_data['requirements']),
                "total_test_cases": len(test_cases),
                "automation_candidates": len(automation_candidates),
                "scripts_generated": len(scripts)
            }
        }
        
        print("\n[SUCCESS] Processing Complete!")
        print("=" * 60)
        
        return self.results
    
    def _extract_base_url(self, document_text: str):
        """Extract Base URL from Test Data section"""
        # Look for "Base URL:" pattern in the document
        base_url_pattern = r'Base URL:\s*(https?://[^\s\n]+)'
        match = re.search(base_url_pattern, document_text, re.IGNORECASE)
        
        if match:
            self.base_url = match.group(1).rstrip('/')  # Remove trailing slash
            print(f"   [OK] Extracted Base URL: {self.base_url}")
        else:
            print(f"   [WARN] No Base URL found, using default: {self.base_url}")
    
    def save_results(self, output_dir: str = "."):
        """Save all generated artifacts to files"""
        import os
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Save JSON report
        with open(os.path.join(output_dir, "test_automation_report.json"), "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2)
        
        # Save individual scripts
        scripts_dir = os.path.join(output_dir, "generated_tests")
        os.makedirs(scripts_dir, exist_ok=True)
        
        for script in self.results['automation_scripts']:
            script_path = os.path.join(scripts_dir, script['script_name'])
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(script['script_content'])
        
        print(f"\n[SAVED] Results saved to: {output_dir}")
        print(f"   - Report: test_automation_report.json")
        print(f"   - Scripts: {scripts_dir}/")


# Example usage
if __name__ == "__main__":
    # Sample requirements document
    sample_requirements = """
    Use Case 1: User Login
    Description: User logs into the application with valid credentials
    Preconditions:
    - User has valid account
    - Application is accessible
    Steps:
    1. Navigate to login page
    2. Enter username
    3. Enter password
    4. Click login button
    Expected Results:
    - User is redirected to dashboard
    - Welcome message is displayed
    Priority: High
    
    Use Case 2: Create New Lead
    Description: Sales agent creates a new lead in the system
    Preconditions:
    - User is logged in
    - User has create lead permission
    Steps:
    1. Click on Leads tab
    2. Click New Lead button
    3. Fill in lead details (Name, Company, Email)
    4. Select lead source
    5. Click Save button
    Expected Results:
    - Lead is created successfully
    - Success message displayed
    - Lead appears in leads list
    Priority: High
    """
    
    # Initialize and run agent
    agent = AITestAutomationAgent()
    results = agent.process_requirements(sample_requirements)
    agent.save_results()
