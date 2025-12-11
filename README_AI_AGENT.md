# AI Test Automation Agent

An intelligent agent that processes requirement documents to automatically extract use cases, generate test cases, identify automation candidates, and create Playwright Python automation scripts.

## Features

- **Requirement Parsing**: Automatically extracts use cases and requirements from documents
- **Test Case Generation**: Creates positive and negative test cases from use cases
- **Automation Scoring**: Evaluates automation feasibility with scoring algorithm
- **Script Generation**: Generates ready-to-run Playwright Python test scripts
- **Priority Classification**: Marks test cases as High/Medium/Low priority for automation

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install
```

## Usage

### Basic Usage

```python
from ai_test_automation_agent import AITestAutomationAgent

# Load your requirements document
with open('requirements.txt', 'r') as f:
    requirements_text = f.read()

# Initialize agent
agent = AITestAutomationAgent()

# Process requirements
results = agent.process_requirements(requirements_text)

# Save generated artifacts
agent.save_results(output_dir='./output')
```

### Command Line Usage

```bash
python ai_test_automation_agent.py
```

## Requirements Document Format

The agent expects requirements in this format:

```
Use Case 1: [Title]
Description: [Description]
Preconditions:
- [Precondition 1]
- [Precondition 2]
Steps:
1. [Step 1]
2. [Step 2]
3. [Step 3]
Expected Results:
- [Expected result 1]
- [Expected result 2]
Priority: High/Medium/Low

REQ001: [Requirement description]
```

## Output

The agent generates:

1. **test_automation_report.json**: Complete analysis report
2. **generated_tests/**: Directory with Playwright Python scripts
3. Test case documentation with automation priorities

## Automation Scoring

Test cases are scored based on:
- UI interaction complexity (0.2 points)
- Number of steps (0.1 points)
- Manual verification requirements (-0.2 points)
- Priority level (0.1 points)

**Score Ranges:**
- 0.8-1.0: High Priority
- 0.6-0.8: Medium Priority
- 0.4-0.6: Low Priority
- <0.4: Not Suitable

## Generated Script Structure

```python
import pytest
from playwright.sync_api import Page, expect

class TestUC001TC001:
    def test_uc001_tc001_positive_flow(self, page: Page):
        # Test implementation
        pass
```

## Customization

### Extend Parsing Logic

```python
class CustomRequirementParser(RequirementParser):
    def extract_custom_fields(self):
        # Add custom parsing logic
        pass
```

### Custom Script Templates

```python
class CustomScriptGenerator(PlaywrightScriptGenerator):
    def _create_playwright_script(self, test_case):
        # Customize script generation
        pass
```

## Example Output

```
🤖 AI Test Automation Agent Started
============================================================

📄 Step 1: Parsing requirements document...
   ✓ Extracted 2 use cases
   ✓ Extracted 0 requirements

🧪 Step 2: Generating test cases...
   ✓ Generated 3 test cases

🎯 Step 3: Identifying automation candidates...
   ✓ Identified 3 automation candidates
     - High Priority: 2
     - Medium Priority: 1

🚀 Step 4: Generating Playwright Python scripts...
   ✓ Generated 3 automation scripts

✅ Processing Complete!
============================================================
```

## Integration with CI/CD

```yaml
# .github/workflows/test.yml
name: Automated Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: playwright install
      - run: pytest generated_tests/ --html=report.html  # Runs in parallel by default
```

## Best Practices

1. **Clear Requirements**: Write detailed use cases with specific steps
2. **Consistent Format**: Follow the expected document structure
3. **Review Generated Scripts**: Always review and customize generated code
4. **Add Locators**: Update placeholder locators with actual selectors
5. **Maintain Page Objects**: Create reusable page object classes

## Limitations

- Requires structured requirement documents
- Generated scripts need locator customization
- Complex business logic may need manual implementation
- Works best with UI-based test scenarios

## Future Enhancements

- [ ] NLP-based requirement parsing
- [ ] Visual element detection for locators
- [ ] API test generation
- [ ] Performance test generation
- [ ] Integration with test management tools
- [ ] AI-powered test data generation

## License

MIT License

## Support

For issues and questions, please open an issue on the repository.
