# RAPTOR Python Playwright Framework Documentation

Welcome to the RAPTOR (Robust Automated Playwright Test Orchestration & Reporting) documentation!

## Documentation Overview

This directory contains comprehensive documentation for the RAPTOR Python Playwright Framework, including:

- **API Reference**: Complete documentation of all classes and methods
- **User Guide**: Comprehensive guide to using the framework
- **Getting Started**: Quick start guide for new users
- **Migration Guide**: Guide for migrating from Java/Selenium
- **Examples**: Practical code examples for common scenarios

## Quick Start

### View Documentation

#### Option 1: Build HTML Documentation

```bash
# Install dependencies
pip install -r requirements.txt

# Build HTML docs
make html

# Open in browser
open _build/html/index.html  # Mac
xdg-open _build/html/index.html  # Linux
start _build/html/index.html  # Windows
```

#### Option 2: Read Markdown Files

Browse the markdown files directly:
- `API_REFERENCE_GUIDE.md` - Complete API reference
- `DOCUMENTATION_QUICK_REFERENCE.md` - Quick reference guide
- `TASK_35_COMPLETION_SUMMARY.md` - Documentation details

#### Option 3: Use Python Help

```python
from raptor.core import ElementManager
help(ElementManager.click)
```

## Documentation Structure

```
docs/
├── conf.py                          # Sphinx configuration
├── Makefile                         # Build automation
├── requirements.txt                 # Documentation dependencies
├── README.md                        # This file
│
├── Sphinx Documentation (RST)
│   ├── index.rst                    # Main entry point
│   ├── getting_started.rst          # Installation & basics
│   ├── api_reference.rst            # Complete API
│   ├── user_guide.rst               # Comprehensive guide
│   ├── migration_guide.rst          # Java to Python migration
│   └── examples.rst                 # Code examples
│
├── Markdown Guides
│   ├── API_REFERENCE_GUIDE.md       # Markdown API reference
│   ├── DOCUMENTATION_QUICK_REFERENCE.md # Quick reference
│   └── TASK_35_COMPLETION_SUMMARY.md # Documentation details
│
└── Module-Specific Guides
    ├── BROWSER_MANAGER_IMPLEMENTATION.md
    ├── ELEMENT_MANAGER_IMPLEMENTATION.md
    ├── DATABASE_MANAGER_IMPLEMENTATION.md
    ├── SESSION_MANAGER_IMPLEMENTATION.md
    ├── CONFIG_MANAGER_IMPLEMENTATION.md
    └── ... (many more)
```

## Building Documentation

### Prerequisites

```bash
pip install -r requirements.txt
```

This installs:
- Sphinx (documentation generator)
- sphinx-rtd-theme (Read the Docs theme)
- sphinx-autodoc-typehints (type hint support)

### Build Commands

```bash
# HTML documentation (most common)
make html

# PDF documentation
make latexpdf

# EPUB format
make epub

# Man pages
make man

# Plain text
make text

# Clean build artifacts
make clean
```

### View Built Documentation

After building, documentation is in `_build/` directory:

```bash
# HTML
open _build/html/index.html

# PDF
open _build/latex/RAPTORPythonPlaywrightFramework.pdf

# EPUB
open _build/epub/RAPTORPythonPlaywrightFramework.epub
```

## Documentation Sections

### 1. Getting Started (`getting_started.rst`)

Perfect for new users. Covers:
- Installation (PyPI and source)
- Configuration setup
- Your first test
- Page objects
- Data-driven testing
- Session management
- Running tests

**Start here if you're new to RAPTOR!**

### 2. User Guide (`user_guide.rst`)

Comprehensive guide covering:
- Framework architecture
- Key concepts (locators, synchronization, assertions)
- Advanced features (parallel execution, custom waits)
- Troubleshooting
- Performance optimization
- Best practices

**Read this to become proficient with RAPTOR.**

### 3. API Reference (`api_reference.rst`)

Complete API documentation:
- All classes and methods
- Parameters and return types
- Code examples
- Cross-references

Also available as markdown: `API_REFERENCE_GUIDE.md`

**Use this as your reference while coding.**

### 4. Migration Guide (`migration_guide.rst`)

For teams migrating from Java/Selenium:
- Migration strategy
- Class and method mapping
- Code conversion examples
- Automated tools
- Common pitfalls
- CI/CD updates

**Essential for migration projects.**

### 5. Examples (`examples.rst`)

Practical code examples:
- Basic tests (login, forms)
- Page objects
- Data-driven testing
- Table interactions
- Session management
- Advanced scenarios
- Property-based testing
- CI/CD integration

**Learn by example!**

## Quick Reference Guides

Module-specific quick references are available:

- `BROWSER_MANAGER_IMPLEMENTATION.md`
- `ELEMENT_MANAGER_IMPLEMENTATION.md`
- `DATABASE_MANAGER_IMPLEMENTATION.md`
- `SESSION_MANAGER_IMPLEMENTATION.md`
- `TABLE_MANAGER_GUIDE.md`
- `LOGGER_QUICK_REFERENCE.md`
- `REPORTER_QUICK_REFERENCE.md`
- And many more...

These provide focused documentation for specific modules.

## Documentation Features

### Comprehensive Coverage

- ✅ 100% API coverage
- ✅ All public methods documented
- ✅ Code examples for every method
- ✅ Type hints and parameter descriptions
- ✅ Error documentation

### User-Friendly

- ✅ Progressive learning path
- ✅ Task-oriented organization
- ✅ Practical examples
- ✅ Troubleshooting guides
- ✅ Best practices

### Multiple Formats

- ✅ HTML (with search)
- ✅ PDF
- ✅ EPUB
- ✅ Markdown
- ✅ Man pages

### Search Functionality

The HTML documentation includes full-text search:
1. Build HTML docs: `make html`
2. Open in browser
3. Use search box in sidebar

## Common Tasks

### Finding a Method

**Option 1: Search HTML docs**
```bash
make html
open _build/html/index.html
# Use search box
```

**Option 2: Python help**
```python
from raptor.core import ElementManager
help(ElementManager.click)
```

**Option 3: Browse API reference**
- Open `api_reference.rst` or `API_REFERENCE_GUIDE.md`
- Navigate to module
- Find method

### Learning a Feature

1. Check `user_guide.rst` for concepts
2. Look at `examples.rst` for code
3. Reference `api_reference.rst` for details
4. Review module quick reference

### Troubleshooting

1. Check `user_guide.rst` → Troubleshooting
2. Review `examples.rst` for similar scenarios
3. Check method docstrings
4. Search documentation

## Documentation Standards

### Docstring Format

All public methods follow this format:

```python
async def method_name(self, param1: str, param2: int = 0) -> ReturnType:
    """
    Brief description of what the method does.
    
    Longer description with more details about behavior,
    edge cases, and important notes.
    
    Args:
        param1 (str): Description of param1
        param2 (int, optional): Description of param2. Defaults to 0.
    
    Returns:
        ReturnType: Description of return value
    
    Raises:
        ExceptionType: When this exception is raised
    
    Example:
        >>> # Basic usage
        >>> result = await obj.method_name("value")
        >>> 
        >>> # Advanced usage
        >>> result = await obj.method_name("value", param2=10)
    
    Note:
        Important notes about usage, performance, or behavior.
    """
```

### Code Example Format

```python
# Import statements
from raptor.core import BrowserManager

# Setup
browser_manager = BrowserManager()
await browser_manager.launch_browser("chromium")

# Test code
# ... implementation

# Cleanup
await browser_manager.close_browser()
```

## Contributing to Documentation

### When to Update

- Adding new features
- Changing existing APIs
- Fixing bugs
- Improving examples
- Adding best practices

### How to Update

1. **Update docstrings** in source code
2. **Update RST files** if needed
3. **Add/update examples**
4. **Rebuild documentation**: `make html`
5. **Review generated HTML**
6. **Test code examples**
7. **Commit changes**

### Documentation Checklist

- [ ] Docstrings updated
- [ ] Examples added/updated
- [ ] RST files updated if needed
- [ ] Documentation builds without errors
- [ ] Code examples tested
- [ ] Links work correctly
- [ ] Search finds relevant content

## Deployment

### GitHub Pages

```yaml
# .github/workflows/docs.yml
name: Documentation
on: [push]
jobs:
  build-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r docs/requirements.txt
      - run: cd docs && make html
      - uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs/_build/html
```

### Read the Docs

1. Connect repository to Read the Docs
2. Configure build settings
3. Documentation builds automatically on push

### Custom Hosting

1. Build documentation: `make html`
2. Upload `_build/html/` to web server
3. Configure web server to serve static files

## Troubleshooting

### Build Errors

**Error: "sphinx-build: command not found"**
```bash
pip install -r requirements.txt
```

**Error: "No module named 'raptor'"**
```bash
# Install package in development mode
cd ..
pip install -e .
```

**Error: "Theme not found"**
```bash
pip install sphinx-rtd-theme
```

### Missing Documentation

If documentation seems incomplete:
1. Check that all modules are imported in `__init__.py`
2. Verify docstrings are present
3. Rebuild with `make clean && make html`
4. Check Sphinx warnings in build output

### Search Not Working

If search doesn't work in HTML docs:
1. Ensure JavaScript is enabled
2. Rebuild documentation
3. Clear browser cache
4. Check that `searchindex.js` exists in `_build/html/`

## Resources

### Documentation Tools

- **Sphinx**: https://www.sphinx-doc.org/
- **Read the Docs Theme**: https://sphinx-rtd-theme.readthedocs.io/
- **Napoleon**: https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html

### Writing Documentation

- **Google Style Guide**: https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings
- **NumPy Style Guide**: https://numpydoc.readthedocs.io/en/latest/format.html
- **reStructuredText**: https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html

### RAPTOR Resources

- **GitHub**: https://github.com/your-org/raptor-playwright
- **Issues**: https://github.com/your-org/raptor-playwright/issues
- **Slack**: #raptor-support

## Getting Help

### Documentation Issues

If you find issues with documentation:
1. Check if it's already reported
2. Create GitHub issue with:
   - What's wrong
   - Where it's wrong (file and section)
   - Suggested fix

### Usage Questions

For questions about using RAPTOR:
1. Check documentation first
2. Search existing issues
3. Ask in Slack #raptor-support
4. Create GitHub issue if needed

## Version Information

- **Documentation Version**: 1.0.0
- **Framework Version**: 1.0.0
- **Last Updated**: 2024-11-28
- **Python Version**: 3.8+
- **Sphinx Version**: 7.0.0+

## License

Same as RAPTOR framework license.

---

**Happy Testing with RAPTOR! 🦖**

For questions or issues, please contact:
- **Slack**: #raptor-support
- **Email**: raptor-support@example.com
- **GitHub**: https://github.com/your-org/raptor-playwright/issues
