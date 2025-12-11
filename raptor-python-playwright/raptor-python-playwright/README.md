# RAPTOR Python Playwright Framework

**R**obust **A**utomated **P**laywright **T**est **O**rchestration & **R**eporting

A modern Python-based test automation framework using Playwright, converted from the original Java Selenium RAPTOR framework.

## Features

- 🚀 **Multi-Browser Support**: Chromium, Firefox, and WebKit
- 🔄 **Session Management**: Reuse browser sessions across test runs
- 📊 **Data-Driven Testing**: Integration with DDFE and DDDB
- 🎯 **Smart Element Location**: Multiple locator strategies with automatic fallback
- ⚡ **Async/Await**: Leverages Python's asyncio for performance
- 📝 **Comprehensive Reporting**: HTML reports with screenshots
- 🧪 **pytest Integration**: Full pytest support with fixtures
- 🔧 **Flexible Configuration**: Environment-specific settings

## Installation

```bash
# Install from PyPI
pip install raptor-playwright

# Install with development dependencies
pip install raptor-playwright[dev]

# Install Playwright browsers
playwright install
```

## Quick Start

```python
import asyncio
from raptor import BrowserManager, ElementManager

async def test_example():
    # Initialize browser
    browser_manager = BrowserManager()
    await browser_manager.launch_browser("chromium")
    
    # Create page
    page = await browser_manager.create_page()
    
    # Initialize element manager
    element_manager = ElementManager(page)
    
    # Navigate and interact
    await page.goto("https://example.com")
    await element_manager.click("css=#login-button")
    await element_manager.fill("css=#username", "testuser")
    
    # Cleanup
    await browser_manager.close_browser()

# Run the test
asyncio.run(test_example())
```

## Configuration

RAPTOR uses a flexible configuration system with environment-specific settings.

### Quick Configuration

```python
from raptor.core.config_manager import ConfigManager

# Load configuration for development
config = ConfigManager()
config.load_config("dev")

# Access configuration values
browser_type = config.get("browser.type")
timeout = config.get("timeouts.default")
```

### Environment Files

Configuration files are located in `raptor/config/`:
- `settings.yaml` - Default configuration
- `environments/dev.yaml` - Development settings
- `environments/staging.yaml` - Staging settings
- `environments/prod.yaml` - Production settings

### Environment Variables

Override configuration using environment variables:

```bash
# Create .env file
cp .env.example .env

# Set your values
RAPTOR_BROWSER_TYPE=chromium
RAPTOR_HEADLESS=false
RAPTOR_DB_HOST=localhost
RAPTOR_DB_USER=your_username
RAPTOR_DB_PASSWORD=your_password
```

See [Configuration Guide](raptor/config/README.md) for detailed documentation.

## Project Structure

```
raptor/
├── core/              # Core framework components
├── database/          # Database operations
├── pages/             # Page object models
├── utils/             # Utility functions
└── config/            # Configuration files
```

## Documentation

- [User Guide](docs/user-guide.md)
- [API Reference](docs/api-reference.md)
- [Migration Guide](docs/migration-guide.md)
- [Examples](examples/)

## Requirements

- Python 3.8+
- Playwright 1.40+
- pytest 7.4+

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please read our contributing guidelines.

## Support

For issues and questions, please use the GitHub issue tracker.
