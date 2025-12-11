# RAPTOR Installation Guide

This guide provides detailed instructions for installing and setting up the RAPTOR Python Playwright Framework.

## Table of Contents

- [System Requirements](#system-requirements)
- [Installation Methods](#installation-methods)
- [Post-Installation Setup](#post-installation-setup)
- [Verification](#verification)
- [Platform-Specific Instructions](#platform-specific-instructions)
- [Troubleshooting Installation](#troubleshooting-installation)

## System Requirements

### Minimum Requirements

- **Python**: 3.8 or higher
- **Operating System**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+, Debian 10+, CentOS 8+)
- **RAM**: 4GB minimum, 8GB recommended
- **Disk Space**: 2GB for framework and browser binaries
- **Network**: Internet connection for initial setup

### Recommended Requirements

- **Python**: 3.10 or higher
- **RAM**: 16GB for parallel test execution
- **Disk Space**: 5GB for multiple browser versions
- **CPU**: Multi-core processor for parallel execution

### Software Dependencies

- **pip**: Python package manager (usually included with Python)
- **git**: For installing from source (optional)
- **Visual Studio Build Tools**: Required on Windows for some dependencies
- **Xcode Command Line Tools**: Required on macOS

## Installation Methods

### Method 1: Install from PyPI (Recommended)

The simplest way to install RAPTOR is from the Python Package Index (PyPI):

```bash
# Create and activate virtual environment (recommended)
python -m venv raptor-env
source raptor-env/bin/activate  # On Windows: raptor-env\Scripts\activate

# Install RAPTOR
pip install raptor-playwright

# Verify installation
raptor --version
```

### Method 2: Install from Source

For development or to get the latest features:

```bash
# Clone the repository
git clone https://github.com/your-org/raptor-playwright.git
cd raptor-playwright

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Install development dependencies
pip install -e ".[dev]"
```

### Method 3: Install Specific Version

To install a specific version:

```bash
# Install specific version
pip install raptor-playwright==1.0.0

# Install with version constraints
pip install "raptor-playwright>=1.0.0,<2.0.0"
```

### Method 4: Install with Optional Dependencies

RAPTOR supports optional dependencies for additional features:

```bash
# Install with all optional dependencies
pip install "raptor-playwright[all]"

# Install with specific optional dependencies
pip install "raptor-playwright[reporting]"  # Enhanced reporting
pip install "raptor-playwright[database]"   # Database support
pip install "raptor-playwright[testing]"    # Testing utilities
pip install "raptor-playwright[dev]"        # Development tools
```

## Post-Installation Setup

### 1. Install Playwright Browsers

After installing RAPTOR, you must install the Playwright browser binaries:

```bash
# Install all browsers (Chromium, Firefox, WebKit)
playwright install

# Install specific browser
playwright install chromium
playwright install firefox
playwright install webkit

# Install with system dependencies (Linux)
playwright install --with-deps
```

### 2. Verify Browser Installation

```bash
# Check installed browsers
playwright --version

# Test browser launch
python -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); browser = p.chromium.launch(); browser.close(); p.stop(); print('Success!')"
```

### 3. Set Up Configuration

Create a configuration directory structure:

```bash
# Create configuration directories
mkdir -p config/environments
mkdir -p logs
mkdir -p reports
mkdir -p screenshots
```

Create a basic configuration file `config/settings.yaml`:

```yaml
# Browser configuration
browser:
  type: chromium
  headless: false
  timeout: 30000
  viewport:
    width: 1920
    height: 1080

# Database configuration (optional)
database:
  server: localhost
  database: test_db
  user: test_user
  password: ${DB_PASSWORD}  # Use environment variable

# Logging configuration
logging:
  level: INFO
  file: logs/raptor.log
  console: true
  rotation: daily
  retention: 30

# Reporting configuration
reporting:
  output_dir: reports
  screenshot_on_failure: true
  video_on_failure: false
  html_report: true

# Session management
session:
  storage_dir: .sessions
  expiration_hours: 24
  auto_cleanup: true

# Test execution
execution:
  retry_attempts: 2
  retry_delay: 1
  parallel_workers: 4
  timeout: 300
```

### 4. Set Up Environment Variables

Create a `.env` file for sensitive configuration:

```bash
# Database credentials
DB_SERVER=localhost
DB_NAME=test_db
DB_USER=test_user
DB_PASSWORD=your_secure_password

# API keys (if needed)
ALM_API_KEY=your_alm_key
JIRA_API_TOKEN=your_jira_token

# Environment
TEST_ENVIRONMENT=dev
```

### 5. Install Database Drivers (Optional)

If using database features:

```bash
# For SQL Server
pip install pyodbc

# For PostgreSQL
pip install psycopg2-binary

# For MySQL
pip install pymysql

# For Oracle
pip install cx_Oracle
```

### 6. Configure pytest

Create `pytest.ini` in your project root:

```ini
[pytest]
# Test discovery
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*

# Asyncio configuration
asyncio_mode = auto

# Markers
markers =
    smoke: Smoke tests
    regression: Regression tests
    integration: Integration tests
    slow: Slow running tests

# Logging
log_cli = true
log_cli_level = INFO
log_file = logs/pytest.log
log_file_level = DEBUG

# Coverage
addopts = 
    --verbose
    --strict-markers
    --tb=short
    --cov=raptor
    --cov-report=html
    --cov-report=term-missing

# Timeout
timeout = 300
timeout_method = thread
```

## Verification

### Verify Installation

Run the following commands to verify your installation:

```bash
# Check Python version
python --version

# Check pip version
pip --version

# Check RAPTOR installation
pip show raptor-playwright

# Check Playwright installation
playwright --version

# List installed browsers
playwright list-browsers
```

### Run Sample Test

Create a simple test file `test_sample.py`:

```python
import pytest
from raptor.core import BrowserManager, ElementManager

@pytest.mark.asyncio
async def test_sample():
    """Sample test to verify installation."""
    browser_manager = BrowserManager()
    await browser_manager.launch_browser("chromium", headless=True)
    page = await browser_manager.create_page()
    
    await page.goto("https://example.com")
    title = await page.title()
    
    assert "Example" in title
    
    await browser_manager.close_browser()
    print("✓ Installation verified successfully!")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

Run the test:

```bash
pytest test_sample.py -v
```

Expected output:
```
test_sample.py::test_sample PASSED
✓ Installation verified successfully!
```

## Platform-Specific Instructions

### Windows

#### Prerequisites

1. Install Python from [python.org](https://www.python.org/downloads/)
2. Install Visual Studio Build Tools (for some dependencies):
   - Download from [Visual Studio Downloads](https://visualstudio.microsoft.com/downloads/)
   - Select "Desktop development with C++"

#### Installation

```powershell
# Create virtual environment
python -m venv raptor-env
.\raptor-env\Scripts\activate

# Install RAPTOR
pip install raptor-playwright

# Install browsers
playwright install
```

#### Common Windows Issues

**Issue**: `error: Microsoft Visual C++ 14.0 or greater is required`
**Solution**: Install Visual Studio Build Tools

**Issue**: `playwright: command not found`
**Solution**: Add Python Scripts directory to PATH:
```powershell
$env:Path += ";C:\Python310\Scripts"
```

### macOS

#### Prerequisites

1. Install Xcode Command Line Tools:
```bash
xcode-select --install
```

2. Install Homebrew (optional but recommended):
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### Installation

```bash
# Install Python (if not already installed)
brew install python@3.10

# Create virtual environment
python3 -m venv raptor-env
source raptor-env/bin/activate

# Install RAPTOR
pip install raptor-playwright

# Install browsers
playwright install
```

#### macOS-Specific Configuration

For M1/M2 Macs, you may need to install Rosetta 2:
```bash
softwareupdate --install-rosetta
```

### Linux

#### Ubuntu/Debian

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2

# Create virtual environment
python3 -m venv raptor-env
source raptor-env/bin/activate

# Install RAPTOR
pip install raptor-playwright

# Install browsers with system dependencies
playwright install --with-deps
```

#### CentOS/RHEL

```bash
# Install system dependencies
sudo yum install -y \
    python3 \
    python3-pip \
    nss \
    nspr \
    atk \
    at-spi2-atk \
    cups-libs \
    libdrm \
    libxkbcommon \
    libXcomposite \
    libXdamage \
    libXfixes \
    libXrandr \
    mesa-libgbm \
    alsa-lib

# Continue with standard installation
python3 -m venv raptor-env
source raptor-env/bin/activate
pip install raptor-playwright
playwright install --with-deps
```

## Troubleshooting Installation

### Common Issues and Solutions

#### Issue: pip install fails with permission error

**Solution**: Use virtual environment or user installation:
```bash
pip install --user raptor-playwright
```

#### Issue: Playwright browsers fail to install

**Solution**: Install with system dependencies:
```bash
# Linux
playwright install --with-deps

# Or install system dependencies manually
sudo apt-get install -y $(playwright install --dry-run | grep -oP '(?<=apt-get install ).*')
```

#### Issue: Import errors after installation

**Solution**: Verify installation and Python path:
```bash
pip list | grep raptor
python -c "import raptor; print(raptor.__file__)"
```

#### Issue: Database connection fails

**Solution**: Install appropriate database driver:
```bash
# For SQL Server
pip install pyodbc

# Check ODBC drivers
odbcinst -q -d
```

#### Issue: Tests run slowly

**Solution**: 
1. Use headless mode
2. Disable unnecessary browser features
3. Use connection pooling for database
4. Run tests in parallel

#### Issue: Browser crashes on Linux

**Solution**: Install missing system dependencies:
```bash
playwright install --with-deps chromium
```

### Getting Help

If you encounter issues not covered here:

1. Check the [Troubleshooting Guide](TROUBLESHOOTING_GUIDE.md)
2. Review [GitHub Issues](https://github.com/your-org/raptor-playwright/issues)
3. Consult the [FAQ](FAQ.md)
4. Join our [Community Forum](https://community.raptor-framework.org)
5. Contact support at support@raptor-framework.org

## Next Steps

After successful installation:

1. Read the [Getting Started Guide](getting_started.rst)
2. Review [Configuration Options](CONFIGURATION_GUIDE.md)
3. Explore [Example Tests](examples.rst)
4. Learn about [Best Practices](user_guide.rst)

## Updating RAPTOR

To update to the latest version:

```bash
# Update to latest version
pip install --upgrade raptor-playwright

# Update browsers
playwright install

# Verify update
pip show raptor-playwright
```

## Uninstallation

To completely remove RAPTOR:

```bash
# Uninstall RAPTOR
pip uninstall raptor-playwright

# Remove Playwright browsers
playwright uninstall

# Remove configuration (optional)
rm -rf config/ logs/ reports/ screenshots/ .sessions/
```
