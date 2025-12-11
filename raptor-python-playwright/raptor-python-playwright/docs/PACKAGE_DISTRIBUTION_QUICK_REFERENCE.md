# Package Distribution Quick Reference

Quick commands for building and publishing the RAPTOR Python Playwright Framework.

## Quick Start

```bash
# Complete build and publish workflow
python scripts/build_and_publish.py --publish testpypi
```

## Build Commands

```bash
# Clean previous builds
rm -rf build/ dist/ *.egg-info

# Build distributions
python -m build

# Check distributions
twine check dist/*
```

## Test Commands

```bash
# Run all tests
pytest tests/ -v --cov=raptor

# Run property tests
pytest tests/test_property_*.py -v

# Test installation
pip install dist/*.whl
python -c "import raptor; print(raptor.__version__)"
```

## Publish Commands

```bash
# Publish to TestPyPI
twine upload --repository testpypi dist/*

# Publish to PyPI
twine upload dist/*
```

## Version Update

```bash
# 1. Update version in pyproject.toml
# 2. Update version in raptor/__init__.py
# 3. Update CHANGELOG.md
# 4. Commit and tag
git add .
git commit -m "Bump version to X.Y.Z"
git tag -a vX.Y.Z -m "Release version X.Y.Z"
git push origin main --tags
```

## CI/CD Triggers

```bash
# GitHub Actions - Publish to TestPyPI
git push origin develop

# GitHub Actions - Publish to PyPI
git tag vX.Y.Z
git push origin vX.Y.Z

# Jenkins - Manual trigger
# Azure DevOps - Automatic on tag
```

## Build Script Options

```bash
# Full build with all checks
python scripts/build_and_publish.py

# Skip tests
python scripts/build_and_publish.py --skip-tests

# Skip linting
python scripts/build_and_publish.py --skip-lint

# Skip installation test
python scripts/build_and_publish.py --skip-install-test

# Publish to TestPyPI
python scripts/build_and_publish.py --publish testpypi

# Publish to PyPI
python scripts/build_and_publish.py --publish pypi

# Clean only
python scripts/build_and_publish.py --clean-only
```

## Common Issues

```bash
# Fix: "No module named 'build'"
pip install build twine

# Fix: "403 Forbidden" on upload
# Check API token in ~/.pypirc

# Fix: "Version already exists"
# Increment version number

# Fix: "Invalid distribution"
twine check dist/*
```

## File Locations

- **Package Config**: `pyproject.toml`
- **Version**: `raptor/__init__.py`
- **Changelog**: `CHANGELOG.md`
- **License**: `LICENSE`
- **Manifest**: `MANIFEST.in`
- **Build Script**: `scripts/build_and_publish.py`
- **CI/CD**: `.github/workflows/ci.yml`, `Jenkinsfile`, `azure-pipelines.yml`

## PyPI Links

- **Production**: https://pypi.org/project/raptor-playwright/
- **Test**: https://test.pypi.org/project/raptor-playwright/
- **Account**: https://pypi.org/manage/account/
- **Tokens**: https://pypi.org/manage/account/token/

## Installation Commands

```bash
# Install from PyPI
pip install raptor-playwright

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ raptor-playwright

# Install with extras
pip install raptor-playwright[dev]
pip install raptor-playwright[reporting]
pip install raptor-playwright[parallel]
pip install raptor-playwright[all]

# Install from local wheel
pip install dist/raptor_playwright-*.whl

# Install in editable mode
pip install -e ".[dev]"
```

## Pre-Release Checklist

- [ ] All tests passing
- [ ] Version updated in pyproject.toml
- [ ] Version updated in __init__.py
- [ ] CHANGELOG.md updated
- [ ] Documentation updated
- [ ] Git committed and tagged
- [ ] Tested on TestPyPI

## Release Workflow

1. Update version numbers
2. Update CHANGELOG.md
3. Commit changes
4. Create git tag
5. Push to repository
6. Build distributions
7. Test on TestPyPI
8. Publish to PyPI
9. Create GitHub release
10. Verify installation

## Support

- **Documentation**: `docs/PACKAGE_DISTRIBUTION_GUIDE.md`
- **Issues**: GitHub issue tracker
- **PyPI Help**: https://pypi.org/help/

