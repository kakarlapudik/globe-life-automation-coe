# Scripts Directory

This directory contains utility scripts for building, testing, and publishing the RAPTOR Python Playwright Framework.

## Available Scripts

### build_and_publish.py

Comprehensive build and publish automation script.

**Features:**
- Clean build artifacts
- Run linting checks (Black, Flake8, MyPy)
- Run test suite (unit, property-based)
- Build distributions (wheel and source)
- Check distributions with twine
- Test package installation
- Publish to TestPyPI or PyPI
- Interactive confirmations
- Colored terminal output

**Usage:**

```bash
# Full build with all checks
python scripts/build_and_publish.py

# Build and publish to TestPyPI
python scripts/build_and_publish.py --publish testpypi

# Build and publish to PyPI
python scripts/build_and_publish.py --publish pypi

# Skip tests (faster build)
python scripts/build_and_publish.py --skip-tests

# Skip linting
python scripts/build_and_publish.py --skip-lint

# Skip installation test
python scripts/build_and_publish.py --skip-install-test

# Clean only (remove build artifacts)
python scripts/build_and_publish.py --clean-only
```

**Options:**
- `--skip-tests`: Skip running the test suite
- `--skip-lint`: Skip code quality checks
- `--skip-install-test`: Skip testing package installation
- `--publish {testpypi,pypi}`: Publish to TestPyPI or PyPI
- `--clean-only`: Only clean build artifacts

**Requirements:**
```bash
pip install build twine
```

## Common Workflows

### Development Build

```bash
# Quick build without tests
python scripts/build_and_publish.py --skip-tests --skip-lint
```

### Pre-Release Testing

```bash
# Full build and test on TestPyPI
python scripts/build_and_publish.py --publish testpypi
```

### Production Release

```bash
# Full build and publish to PyPI
python scripts/build_and_publish.py --publish pypi
```

### Clean Build Directory

```bash
# Remove all build artifacts
python scripts/build_and_publish.py --clean-only
```

## Manual Commands

If you prefer to run commands manually:

```bash
# Clean
rm -rf build/ dist/ *.egg-info

# Build
python -m build

# Check
twine check dist/*

# Test installation
pip install dist/*.whl

# Publish to TestPyPI
twine upload --repository testpypi dist/*

# Publish to PyPI
twine upload dist/*
```

## CI/CD Integration

These scripts are also used by CI/CD pipelines:

- **GitHub Actions**: `.github/workflows/ci.yml`
- **Jenkins**: `Jenkinsfile`
- **Azure DevOps**: `azure-pipelines.yml`

## Troubleshooting

### "No module named 'build'"

```bash
pip install build twine
```

### "Permission denied"

On Unix systems, make the script executable:
```bash
chmod +x scripts/build_and_publish.py
```

### "403 Forbidden" on upload

Check your PyPI credentials in `~/.pypirc`:
```ini
[pypi]
username = __token__
password = pypi-YOUR-API-TOKEN
```

### "Version already exists"

You cannot re-upload the same version to PyPI. Increment the version number in:
- `pyproject.toml`
- `raptor/__init__.py`

## Documentation

For more information, see:
- [Package Distribution Guide](../docs/PACKAGE_DISTRIBUTION_GUIDE.md)
- [Quick Reference](../docs/PACKAGE_DISTRIBUTION_QUICK_REFERENCE.md)

