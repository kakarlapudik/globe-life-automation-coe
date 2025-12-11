# RAPTOR Documentation - Quick Reference

## Documentation Overview

The RAPTOR Python Playwright Framework documentation is organized into several key sections to help you find information quickly.

## Documentation Files

### Main Documentation (Sphinx/RST)

| File | Purpose | Audience |
|------|---------|----------|
| `index.rst` | Main entry point, quick start | All users |
| `getting_started.rst` | Installation and first steps | New users |
| `api_reference.rst` | Complete API documentation | Developers |
| `user_guide.rst` | Comprehensive usage guide | All users |
| `migration_guide.rst` | Java to Python migration | Migration teams |
| `examples.rst` | Code examples and patterns | All users |

### Additional Guides (Markdown)

| File | Purpose |
|------|---------|
| `API_REFERENCE_GUIDE.md` | Markdown API reference |
| `DOCUMENTATION_QUICK_REFERENCE.md` | This file |
| `TASK_35_COMPLETION_SUMMARY.md` | Documentation completion details |

## Quick Links

### For New Users

1. **Start Here**: `getting_started.rst`
   - Installation
   - Configuration
   - First test
   - Basic concepts

2. **Learn by Example**: `examples.rst`
   - Login test
   - Form submission
   - Page objects
   - Data-driven tests

3. **Understand the Framework**: `user_guide.rst`
   - Architecture
   - Key concepts
   - Best practices

### For Experienced Users

1. **API Reference**: `api_reference.rst` or `API_REFERENCE_GUIDE.md`
   - All classes and methods
   - Parameters and returns
   - Code examples

2. **Advanced Topics**: `user_guide.rst`
   - Parallel execution
   - Custom wait conditions
   - Visual regression
   - Performance optimization

3. **Integration**: `examples.rst`
   - CI/CD examples
   - Database integration
   - External systems

### For Migration Teams

1. **Migration Strategy**: `migration_guide.rst`
   - Phased approach
   - Class mapping
   - Method mapping

2. **Code Conversion**: `migration_guide.rst`
   - Java to Python examples
   - Automated tools
   - Common pitfalls

3. **Validation**: `migration_guide.rst`
   - Testing migration
   - Validation checklist
   - CI/CD updates

## Common Tasks

### Finding a Method

**Option 1: Search in HTML docs**
```bash
cd docs
make html
open _build/html/index.html
# Use search box in sidebar
```

**Option 2: Use Python help**
```python
from raptor.core import ElementManager
help(ElementManager.click)
```

**Option 3: Browse API reference**
- Open `api_reference.rst` or `API_REFERENCE_GUIDE.md`
- Navigate to module section
- Find method

### Learning a Feature

1. Check `user_guide.rst` for concept explanation
2. Look at `examples.rst` for code samples
3. Reference `api_reference.rst` for detailed API
4. Review module-specific quick reference guides

### Troubleshooting

1. Check `user_guide.rst` → Troubleshooting section
2. Review `examples.rst` for similar scenarios
3. Check method docstrings for notes and warnings
4. Search documentation for error messages

## Documentation Structure

```
docs/
├── Sphinx Documentation (RST)
│   ├── index.rst              # Main entry
│   ├── getting_started.rst    # Installation & basics
│   ├── api_reference.rst      # Complete API
│   ├── user_guide.rst         # Comprehensive guide
│   ├── migration_guide.rst    # Java to Python
│   └── examples.rst           # Code examples
│
├── Markdown Guides
│   ├── API_REFERENCE_GUIDE.md # Markdown API reference
│   └── DOCUMENTATION_QUICK_REFERENCE.md # This file
│
├── Module-Specific Guides
│   ├── BROWSER_MANAGER_IMPLEMENTATION.md
│   ├── ELEMENT_MANAGER_IMPLEMENTATION.md
│   ├── DATABASE_MANAGER_IMPLEMENTATION.md
│   └── ... (many more)
│
└── Quick Reference Guides
    ├── *_QUICK_REFERENCE.md files
    └── Task completion summaries
```

## Building Documentation

### HTML Documentation

```bash
cd docs
pip install -r requirements.txt
make html
open _build/html/index.html
```

### PDF Documentation

```bash
cd docs
make latexpdf
open _build/latex/RAPTORPythonPlaywrightFramework.pdf
```

### Other Formats

```bash
make epub      # EPUB format
make man       # Man pages
make text      # Plain text
```

## Documentation Conventions

### Code Examples

All code examples follow this pattern:

```python
# Import statements
from raptor.core import BrowserManager, ElementManager

# Setup
browser_manager = BrowserManager()
await browser_manager.launch_browser("chromium")

# Test code
await element_manager.click("css=#button")

# Cleanup
await browser_manager.close_browser()
```

### Locator Syntax

```python
"css=#element-id"           # CSS selector
"xpath=//div[@id='element']" # XPath
"text=Click Me"             # Text content
"role=button[name='Submit']" # Role-based
"id=element-id"             # ID
```

### Async/Await

All framework methods are async:

```python
# ❌ Wrong
element_manager.click("css=#button")

# ✓ Correct
await element_manager.click("css=#button")
```

## Module Quick Reference

### Core Modules

| Module | Purpose | Quick Ref |
|--------|---------|-----------|
| BrowserManager | Browser lifecycle | `BROWSER_MANAGER_IMPLEMENTATION.md` |
| ElementManager | Element interactions | `ELEMENT_MANAGER_IMPLEMENTATION.md` |
| SessionManager | Session persistence | `SESSION_MANAGER_IMPLEMENTATION.md` |
| ConfigManager | Configuration | `CONFIG_MANAGER_IMPLEMENTATION.md` |

### Database Modules

| Module | Purpose | Quick Ref |
|--------|---------|-----------|
| DatabaseManager | Database operations | `DATABASE_MANAGER_IMPLEMENTATION.md` |
| ConnectionPool | Connection pooling | `DATABASE_MANAGER_IMPLEMENTATION.md` |

### Page Objects

| Module | Purpose | Quick Ref |
|--------|---------|-----------|
| BasePage | Base page class | `BASE_PAGE_QUICK_REFERENCE.md` |
| TableManager | Table operations | `TABLE_MANAGER_GUIDE.md` |

### Utilities

| Module | Purpose | Quick Ref |
|--------|---------|-----------|
| Logger | Logging | `LOGGER_QUICK_REFERENCE.md` |
| Reporter | Test reporting | `REPORTER_QUICK_REFERENCE.md` |
| WaitHelpers | Wait conditions | `WAIT_HELPERS_QUICK_REFERENCE.md` |
| ScreenshotUtilities | Screenshots | `SCREENSHOT_UTILITIES_QUICK_REFERENCE.md` |

## Common Patterns

### Basic Test

```python
@pytest.mark.asyncio
async def test_example(browser_manager, element_manager, page):
    await page.goto("https://example.com")
    await element_manager.click("css=#button")
    assert await element_manager.is_visible("css=#result")
```

### Page Object

```python
class LoginPage(BasePage):
    async def login(self, username: str, password: str):
        await self.element_manager.fill("css=#username", username)
        await self.element_manager.fill("css=#password", password)
        await self.element_manager.click("css=#login-button")
```

### Data-Driven

```python
@pytest.mark.parametrize("username,password", [
    ("user1", "pass1"),
    ("user2", "pass2"),
])
@pytest.mark.asyncio
async def test_login(username, password):
    # Test implementation
```

### Session Management

```python
page = await session_manager.restore_session("my_session")
if page is None:
    # Create new session
    await browser_manager.launch_browser("chromium")
    page = await browser_manager.create_page()
    # ... perform login
    await session_manager.save_session(page, "my_session")
```

## Getting Help

### Documentation

1. **Search HTML docs**: Full-text search in generated HTML
2. **Browse API reference**: Complete method documentation
3. **Check examples**: Working code samples
4. **Read user guide**: Comprehensive explanations

### Code

1. **Docstrings**: `help(ClassName.method_name)`
2. **Type hints**: IDE autocomplete and hints
3. **Examples**: In docstrings and examples.rst

### Community

1. **GitHub Issues**: Report bugs and request features
2. **Slack Channel**: #raptor-support
3. **Email**: raptor-support@example.com

## Tips for Using Documentation

### For Learning

1. Start with `getting_started.rst`
2. Work through examples in `examples.rst`
3. Read relevant sections of `user_guide.rst`
4. Reference `api_reference.rst` as needed

### For Reference

1. Use HTML search for quick lookups
2. Keep `API_REFERENCE_GUIDE.md` handy
3. Bookmark frequently used sections
4. Use IDE docstring popups

### For Migration

1. Read `migration_guide.rst` completely
2. Use mapping tables for conversions
3. Follow code examples closely
4. Test incrementally

## Documentation Updates

### When to Update

- Adding new features
- Changing existing APIs
- Fixing bugs
- Improving examples
- Adding best practices

### How to Update

1. Update docstrings in source code
2. Update relevant RST files
3. Add/update examples
4. Rebuild documentation
5. Review generated HTML
6. Commit changes

## Version Information

- **Documentation Version**: 1.0.0
- **Framework Version**: 1.0.0
- **Last Updated**: 2024-11-28
- **Python Version**: 3.8+
- **Playwright Version**: 1.40.0+

## Quick Command Reference

```bash
# Install documentation dependencies
pip install -r docs/requirements.txt

# Build HTML documentation
cd docs && make html

# Build PDF documentation
cd docs && make latexpdf

# Clean build artifacts
cd docs && make clean

# View documentation
open docs/_build/html/index.html

# Search documentation
# Use search box in HTML docs

# Get help on method
python -c "from raptor.core import ElementManager; help(ElementManager.click)"
```

## Documentation Checklist

When using documentation:

- [ ] Read getting started guide
- [ ] Review relevant examples
- [ ] Check API reference for methods
- [ ] Understand async/await patterns
- [ ] Review best practices
- [ ] Check troubleshooting section
- [ ] Test code examples
- [ ] Bookmark useful sections

## Additional Resources

- **Full Documentation**: https://raptor-docs.example.com
- **GitHub**: https://github.com/your-org/raptor-playwright
- **Examples**: `raptor-python-playwright/examples/`
- **Tests**: `raptor-python-playwright/tests/`

---

**Need Help?**
- Check the documentation first
- Search for similar issues
- Ask in Slack #raptor-support
- Create GitHub issue if needed
