# Package Distribution Guide

This guide covers the complete process of building, testing, and publishing the RAPTOR Python Playwright Framework to PyPI.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Package Metadata](#package-metadata)
- [Building Distributions](#building-distributions)
- [Testing the Package](#testing-the-package)
- [Publishing to PyPI](#publishing-to-pypi)
- [CI/CD Integration](#cicd-integration)
- [Version Management](#version-management)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Tools

```bash
# Install build tools
pip install build twine

# Install development dependencies
pip install -e ".[dev]"
```

### PyPI Account Setup

1. **Create PyPI Account**
   - Register at https://pypi.org/account/register/
   - Verify your email address

2. **Create TestPyPI Account** (for testing)
   - Register at https://test.pypi.org/account/register/
   - Verify your email address

3. **Generate API Tokens**
   - PyPI: https://pypi.org/manage/account/token/
   - TestPyPI: https://test.pypi.org/manage/account/token/
   - Save tokens securely (you won't see them again!)

4. **Configure Credentials**

Create `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR-API-TOKEN-HERE

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR-TEST-API-TOKEN-HERE
```

Set file permissions:
```bash
chmod 600 ~/.pypirc
```

## Package Metadata

### pyproject.toml

The main package configuration is in `pyproject.toml`:

```toml
[project]
name = "raptor-playwright"
version = "1.0.0"
description = "RAPTOR Python Playwright Framework"
readme = "README.md"
requires-python = ">=3.8"
license = {text = "MIT"}
```

### Version Number

Update version in:
1. `pyproject.toml` - `version = "X.Y.Z"`
2. `raptor/__init__.py` - `__version__ = "X.Y.Z"`
3. `CHANGELOG.md` - Add new version section

Follow [Semantic Versioning](https://semver.org/):
- **Major** (X.0.0): Breaking changes
- **Minor** (1.X.0): New features, backward compatible
- **Patch** (1.0.X): Bug fixes

## Building Distributions

### Manual Build

```bash
# Clean previous builds
rm -rf build/ dist/ *.egg-info

# Build wheel and source distribution
python -m build

# Verify build
ls -lh dist/
```

This creates:
- `dist/raptor_playwright-X.Y.Z-py3-none-any.whl` (wheel)
- `dist/raptor-playwright-X.Y.Z.tar.gz` (source)

### Using Build Script

```bash
# Build with all checks
python scripts/build_and_publish.py

# Build without tests
python scripts/build_and_publish.py --skip-tests

# Build without linting
python scripts/build_and_publish.py --skip-lint

# Clean only
python scripts/build_and_publish.py --clean-only
```

### Check Distributions

```bash
# Check package metadata and structure
twine check dist/*

# Should output: "Checking dist/... PASSED"
```

## Testing the Package

### Test Installation Locally

```bash
# Create test environment
python -m venv test-env
source test-env/bin/activate  # On Windows: test-env\Scripts\activate

# Install from wheel
pip install dist/raptor_playwright-*.whl

# Test import
python -c "import raptor; print(raptor.__version__)"

# Run a simple test
python -c "from raptor.core.config_manager import ConfigManager; print('OK')"

# Cleanup
deactivate
rm -rf test-env
```

### Test Installation from TestPyPI

```bash
# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ raptor-playwright

# Test
python -c "import raptor; print(raptor.__version__)"
```

## Publishing to PyPI

### Publish to TestPyPI (Recommended First)

```bash
# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Or using build script
python scripts/build_and_publish.py --publish testpypi
```

Verify at: https://test.pypi.org/project/raptor-playwright/

### Publish to Production PyPI

```bash
# Upload to PyPI
twine upload dist/*

# Or using build script
python scripts/build_and_publish.py --publish pypi
```

Verify at: https://pypi.org/project/raptor-playwright/

### Post-Publication

1. **Create Git Tag**
   ```bash
   git tag -a v1.0.0 -m "Release version 1.0.0"
   git push origin v1.0.0
   ```

2. **Create GitHub Release**
   - Go to repository releases
   - Create new release from tag
   - Add release notes from CHANGELOG.md
   - Attach distribution files

3. **Verify Installation**
   ```bash
   pip install raptor-playwright
   python -c "import raptor; print(raptor.__version__)"
   ```

## CI/CD Integration

### GitHub Actions

The `.github/workflows/ci.yml` pipeline automatically:
- Runs tests on multiple Python versions and platforms
- Builds distributions
- Publishes to TestPyPI on `develop` branch
- Publishes to PyPI on release tags

**Trigger Release:**
```bash
git tag v1.0.0
git push origin v1.0.0
```

### Jenkins

The `Jenkinsfile` provides:
- Multi-stage pipeline
- Test execution
- Distribution building
- Optional PyPI publishing

**Configure:**
1. Add PyPI credentials to Jenkins
2. Create pipeline job
3. Point to repository

### Azure DevOps

The `azure-pipelines.yml` includes:
- Matrix testing
- Build artifacts
- Deployment stages

**Configure:**
1. Create service connections for PyPI
2. Import pipeline
3. Configure environments

## Version Management

### Pre-Release Checklist

- [ ] All tests passing
- [ ] Code coverage >80%
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version number updated
- [ ] No uncommitted changes
- [ ] Branch is up to date

### Release Process

1. **Update Version**
   ```bash
   # Update version in pyproject.toml and __init__.py
   vim pyproject.toml
   vim raptor/__init__.py
   ```

2. **Update Changelog**
   ```bash
   vim CHANGELOG.md
   # Add new version section with changes
   ```

3. **Commit Changes**
   ```bash
   git add .
   git commit -m "Bump version to X.Y.Z"
   git push origin main
   ```

4. **Create Tag**
   ```bash
   git tag -a vX.Y.Z -m "Release version X.Y.Z"
   git push origin vX.Y.Z
   ```

5. **Build and Publish**
   ```bash
   python scripts/build_and_publish.py --publish pypi
   ```

6. **Create GitHub Release**
   - Go to GitHub releases
   - Create release from tag
   - Add release notes

### Post-Release

1. **Verify Installation**
   ```bash
   pip install --upgrade raptor-playwright
   python -c "import raptor; print(raptor.__version__)"
   ```

2. **Update Documentation**
   - Update ReadTheDocs
   - Update examples
   - Announce release

3. **Monitor Issues**
   - Watch for installation issues
   - Monitor PyPI download stats
   - Respond to user feedback

## Troubleshooting

### Build Errors

**Error: "No module named 'build'"**
```bash
pip install build
```

**Error: "Invalid distribution"**
- Check pyproject.toml syntax
- Ensure all required files exist
- Run `twine check dist/*`

### Upload Errors

**Error: "403 Forbidden"**
- Check API token is correct
- Ensure token has upload permissions
- Verify package name is available

**Error: "400 Bad Request"**
- Version already exists on PyPI
- Bump version number
- Cannot re-upload same version

**Error: "File already exists"**
- Clean dist/ directory
- Rebuild distributions
- Ensure version is incremented

### Installation Errors

**Error: "No matching distribution found"**
- Check Python version compatibility
- Verify package name spelling
- Check PyPI availability

**Error: "Could not find a version"**
- Package may not be published yet
- Check version number
- Try with `--pre` flag for pre-releases

### CI/CD Errors

**GitHub Actions: "Authentication failed"**
- Add `PYPI_API_TOKEN` secret
- Add `TEST_PYPI_API_TOKEN` secret
- Check token permissions

**Jenkins: "Permission denied"**
- Configure credentials in Jenkins
- Check credential IDs match
- Verify service account permissions

## Best Practices

### Before Publishing

1. **Test Thoroughly**
   - Run full test suite
   - Test on multiple Python versions
   - Test on multiple platforms

2. **Review Changes**
   - Review all code changes
   - Update documentation
   - Update changelog

3. **Test Installation**
   - Test from TestPyPI first
   - Test in clean environment
   - Verify all dependencies

### During Publishing

1. **Use TestPyPI First**
   - Always test on TestPyPI
   - Verify installation works
   - Check package metadata

2. **Version Carefully**
   - Follow semantic versioning
   - Never reuse version numbers
   - Tag releases in git

3. **Document Changes**
   - Update CHANGELOG.md
   - Create release notes
   - Document breaking changes

### After Publishing

1. **Verify Installation**
   - Test installation from PyPI
   - Check on different platforms
   - Verify all features work

2. **Monitor Feedback**
   - Watch issue tracker
   - Monitor download stats
   - Respond to user questions

3. **Plan Next Release**
   - Review feedback
   - Plan improvements
   - Update roadmap

## Additional Resources

- [Python Packaging Guide](https://packaging.python.org/)
- [PyPI Help](https://pypi.org/help/)
- [Twine Documentation](https://twine.readthedocs.io/)
- [Semantic Versioning](https://semver.org/)
- [PEP 517 - Build System](https://peps.python.org/pep-0517/)
- [PEP 518 - pyproject.toml](https://peps.python.org/pep-0518/)

## Support

For issues with package distribution:
- Check [Troubleshooting](#troubleshooting) section
- Review [PyPI Help](https://pypi.org/help/)
- Open an issue on GitHub
- Contact maintainers

