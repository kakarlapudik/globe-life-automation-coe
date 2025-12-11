# Contributing to RAPTOR Python Playwright Framework

Thank you for your interest in contributing to RAPTOR! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Documentation](#documentation)
- [Submitting Changes](#submitting-changes)
- [Style Guidelines](#style-guidelines)
- [Release Process](#release-process)

## Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code:

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Basic understanding of Playwright and pytest
- Familiarity with async/await in Python

### Finding Issues

- Check the [issue tracker](https://github.com/example/raptor-playwright/issues)
- Look for issues labeled `good first issue` or `help wanted`
- Comment on an issue to let others know you're working on it

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Clone your fork
git clone https://github.com/YOUR_USERNAME/raptor-playwright.git
cd raptor-playwright
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
# Install package in editable mode with dev dependencies
pip install -e ".[dev]"

# Install Playwright browsers
playwright install
```

### 4. Verify Installation

```bash
# Run tests to verify setup
pytest tests/ -v

# Run property-based tests
pytest tests/test_property_*.py -v

# Check code style
black --check raptor/
flake8 raptor/
```

## Making Changes

### 1. Create a Branch

```bash
# Create a feature branch
git checkout -b feature/your-feature-name

# Or a bugfix branch
git checkout -b fix/issue-number-description
```

### 2. Make Your Changes

- Write clear, concise code
- Follow the existing code style
- Add docstrings to all public methods
- Update documentation as needed
- Add tests for new functionality

### 3. Commit Your Changes

```bash
# Stage your changes
git add .

# Commit with a descriptive message
git commit -m "Add feature: description of your changes"
```

#### Commit Message Guidelines

- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit first line to 72 characters
- Reference issues and pull requests when relevant

Examples:
```
Add session persistence for Firefox browser
Fix element location timeout in table manager
Update documentation for configuration manager
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_browser_manager.py

# Run with coverage
pytest --cov=raptor --cov-report=html

# Run property-based tests
pytest tests/test_property_*.py -v

# Run integration tests
pytest tests/test_integration.py -v

# Run performance tests
pytest tests/test_performance.py -v
```

### Writing Tests

#### Unit Tests

```python
import pytest
from raptor.core.browser_manager import BrowserManager

@pytest.mark.asyncio
async def test_browser_launch():
    """Test browser launches successfully."""
    manager = BrowserManager()
    browser = await manager.launch_browser("chromium")
    assert browser is not None
    await manager.close_browser()
```

#### Property-Based Tests

```python
from hypothesis import given, strategies as st
import pytest

@given(browser_type=st.sampled_from(["chromium", "firefox", "webkit"]))
@pytest.mark.asyncio
async def test_property_browser_launch(browser_type):
    """Property: All browser types should launch successfully."""
    manager = BrowserManager()
    browser = await manager.launch_browser(browser_type)
    assert browser.is_connected()
    await manager.close_browser()
```

### Test Requirements

- All new features must have unit tests
- Critical functionality should have property-based tests
- Integration tests for component interactions
- Maintain >80% code coverage
- All tests must pass before submitting PR

## Documentation

### Docstring Format

Use Google-style docstrings:

```python
async def click(self, locator: str, timeout: int = 20000) -> None:
    """Click an element on the page.
    
    Args:
        locator: Element locator string (CSS, XPath, text, role)
        timeout: Maximum wait time in milliseconds
        
    Returns:
        None
        
    Raises:
        ElementNotFoundException: If element cannot be located
        TimeoutException: If operation exceeds timeout
        
    Example:
        >>> await element_manager.click("css=#login-button")
        >>> await element_manager.click("text=Submit", timeout=30000)
    """
    # Implementation
```

### Documentation Updates

- Update docstrings for modified methods
- Update user guide for new features
- Update API reference for new classes/methods
- Add examples for new functionality
- Update migration guide if API changes

## Submitting Changes

### 1. Push Your Changes

```bash
# Push to your fork
git push origin feature/your-feature-name
```

### 2. Create Pull Request

- Go to the original repository on GitHub
- Click "New Pull Request"
- Select your fork and branch
- Fill out the PR template
- Link related issues

### 3. PR Requirements

Your PR should include:

- [ ] Clear description of changes
- [ ] Tests for new functionality
- [ ] Documentation updates
- [ ] Changelog entry
- [ ] All tests passing
- [ ] Code style checks passing
- [ ] No merge conflicts

### 4. Code Review

- Respond to review comments
- Make requested changes
- Push updates to your branch
- Request re-review when ready

## Style Guidelines

### Python Code Style

- Follow [PEP 8](https://pep8.org/)
- Use [Black](https://black.readthedocs.io/) for formatting
- Use [flake8](https://flake8.pycqa.org/) for linting
- Use type hints where appropriate

```bash
# Format code
black raptor/

# Check linting
flake8 raptor/

# Type checking
mypy raptor/
```

### Code Organization

- Keep functions focused and small
- Use descriptive variable names
- Avoid deep nesting (max 3-4 levels)
- Extract complex logic into helper functions
- Use async/await consistently

### Naming Conventions

- Classes: `PascalCase` (e.g., `BrowserManager`)
- Functions/Methods: `snake_case` (e.g., `launch_browser`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_TIMEOUT`)
- Private methods: `_leading_underscore` (e.g., `_internal_method`)

## Release Process

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):

- **Major** (X.0.0): Breaking changes
- **Minor** (1.X.0): New features, backward compatible
- **Patch** (1.0.X): Bug fixes

### Release Checklist

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Run full test suite
4. Update documentation
5. Create release tag
6. Build distributions
7. Upload to PyPI
8. Create GitHub release

### Building Distributions

```bash
# Clean previous builds
rm -rf build/ dist/ *.egg-info

# Build wheel and source distribution
python -m build

# Check distribution
twine check dist/*

# Upload to TestPyPI (for testing)
twine upload --repository testpypi dist/*

# Upload to PyPI (production)
twine upload dist/*
```

## Questions?

- Open an issue for bugs or feature requests
- Start a discussion for questions
- Check existing documentation
- Reach out to maintainers

## Thank You!

Your contributions make RAPTOR better for everyone. We appreciate your time and effort!

