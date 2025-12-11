# RAPTOR Reporting Module

## Overview

The RAPTOR reporting module provides advanced test reporting capabilities with interactive visualizations and multiple export formats.

## Components

### QuartoReporter

Advanced reporting with Quarto integration:
- Interactive Plotly visualizations
- Multiple export formats (HTML, PDF, Word)
- Parameterized report generation
- Custom template support
- Seamless TestReporter integration

## Quick Start

```python
from raptor.reporting.quarto_reporter import QuartoReporter, QuartoConfig

# Create reporter
quarto_reporter = QuartoReporter(
    report_dir="reports/quarto",
    test_reporter=test_reporter
)

# Generate HTML report
output_path = quarto_reporter.generate_report(
    output_name="test_report",
    include_visualizations=True
)
```

## Features

### Interactive Visualizations
- Test status distribution (pie chart)
- Pass rate gauge
- Test duration analysis (bar chart)
- Duration distribution (histogram)

### Multiple Formats
- **HTML**: Interactive, self-contained, responsive
- **PDF**: Print-ready, professional
- **Word**: Editable, collaborative

### Customization
- Custom Quarto templates
- Parameterized reports
- Theme selection
- Figure size control

### Integration
- Works with TestReporter
- JSON import/export
- Batch processing
- CI/CD friendly

## Prerequisites

### Install Quarto
Download from: https://quarto.org

```bash
quarto --version  # Verify installation
```

### Install Python Dependencies
```bash
pip install plotly kaleido matplotlib pandas
```

Or use built-in installer:
```python
from raptor.reporting.quarto_reporter import QuartoReporter
QuartoReporter.install_dependencies()
```

## Usage Examples

### Basic Report
```python
quarto_reporter = QuartoReporter(test_reporter=test_reporter)
output = quarto_reporter.generate_report()
```

### Custom Configuration
```python
config = QuartoConfig(
    format="pdf",
    theme="darkly",
    toc=True,
    fig_width=12
)

output = quarto_reporter.generate_report(
    config=config,
    include_visualizations=True
)
```

### Parameterized Report
```python
output = quarto_reporter.generate_report(
    parameters={
        "environment": "production",
        "version": "2.0.0",
        "build_number": 12345
    }
)
```

### Multiple Formats
```python
results = quarto_reporter.export_multiple_formats(
    formats=["html", "pdf", "docx"]
)
```

### From JSON
```python
output = quarto_reporter.generate_from_json(
    json_file="test_results.json"
)
```

### Custom Template
```python
template_content = """---
title: "Custom Report"
---

# My Custom Report
"""

template_path = quarto_reporter.create_custom_template(
    "custom",
    template_content
)
```

## Built-in Templates

1. **default.qmd** - Standard comprehensive report
2. **executive.qmd** - High-level executive summary
3. **detailed.qmd** - In-depth technical analysis

## Configuration Options

```python
QuartoConfig(
    format="html",           # html, pdf, docx
    theme="cosmo",           # Quarto theme
    toc=True,                # Table of contents
    toc_depth=3,             # TOC depth
    code_fold=True,          # Code folding
    self_contained=True,     # Self-contained HTML
    execute=True,            # Execute code chunks
    fig_width=10,            # Figure width
    fig_height=6             # Figure height
)
```

## Available Themes

- `default` - Default Quarto theme
- `cosmo` - Modern flat theme
- `flatly` - Flat and modern
- `darkly` - Dark theme
- `journal` - Clean journal style
- `united` - Ubuntu-inspired
- `lumen` - Light and clean
- `sandstone` - Warm and inviting

## Report Sections

1. **Executive Summary** - Key metrics and statistics
2. **Test Results Visualization** - Interactive charts
3. **Detailed Test Results** - Individual test information
4. **Performance Analysis** - Duration and timing metrics

## Error Handling

```python
try:
    output = quarto_reporter.generate_report()
    print(f"Report generated: {output}")
except RuntimeError as e:
    if "Quarto is not installed" in str(e):
        print("Please install Quarto from https://quarto.org")
    else:
        print(f"Error: {e}")
```

## Integration with TestReporter

```python
from raptor.utils.reporter import TestReporter
from raptor.reporting.quarto_reporter import QuartoReporter

# Create TestReporter
test_reporter = TestReporter()
test_reporter.start_suite("My Test Suite")
# ... add test results ...
test_reporter.end_suite()

# Generate traditional HTML report
html_report = test_reporter.generate_html_report()

# Generate Quarto report from same data
quarto_reporter = QuartoReporter(test_reporter=test_reporter)
quarto_report = quarto_reporter.generate_report()
```

## Best Practices

1. **Use HTML for interactive reports** - Best visualization support
2. **Use PDF for formal documentation** - Print-ready format
3. **Use Word for collaboration** - Editable format
4. **Parameterize reports** - Include environment and version info
5. **Create custom templates** - Tailor for different audiences
6. **Handle errors gracefully** - Check Quarto installation
7. **Test with small datasets** - Verify before large-scale use

## Troubleshooting

### Quarto Not Found
**Error**: `RuntimeError: Quarto is not installed`

**Solution**: Install Quarto from https://quarto.org

### Missing Python Packages
**Error**: `ModuleNotFoundError: No module named 'plotly'`

**Solution**: `pip install plotly kaleido matplotlib pandas`

### PDF Generation Fails
**Error**: PDF rendering fails

**Solution**: Install LaTeX distribution (MiKTeX, MacTeX, or TeX Live)

### Rendering Timeout
**Error**: `RuntimeError: Quarto rendering timed out`

**Solution**: Reduce visualizations or increase timeout

## Documentation

- **Comprehensive Guide**: `docs/QUARTO_REPORTING_GUIDE.md`
- **Quick Reference**: `docs/QUARTO_QUICK_REFERENCE.md`
- **Examples**: `examples/quarto_reporter_example.py`
- **API Reference**: `docs/API_REFERENCE_GUIDE.md`

## Testing

Run tests:
```bash
pytest tests/test_quarto_reporter.py -v
```

All 28 tests should pass.

## API Reference

### QuartoReporter

```python
class QuartoReporter:
    def __init__(
        self,
        report_dir: str = "reports/quarto",
        test_reporter: Optional[TestReporter] = None
    )
    
    def generate_report(
        self,
        output_name: str = "test_report",
        config: Optional[QuartoConfig] = None,
        parameters: Optional[Dict[str, Any]] = None,
        template: Optional[str] = None,
        include_visualizations: bool = True
    ) -> str
    
    def generate_from_json(
        self,
        json_file: str,
        output_name: str = "test_report",
        config: Optional[QuartoConfig] = None,
        include_visualizations: bool = True
    ) -> str
    
    def create_custom_template(
        self,
        template_name: str,
        template_content: str
    ) -> Path
    
    def export_multiple_formats(
        self,
        output_name: str = "test_report",
        formats: Optional[List[str]] = None,
        parameters: Optional[Dict[str, Any]] = None,
        include_visualizations: bool = True
    ) -> Dict[str, str]
    
    @staticmethod
    def install_dependencies() -> bool
```

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review examples in `examples/quarto_reporter_example.py`
3. Consult documentation in `docs/`
4. Open an issue on the project repository

## License

Part of the RAPTOR Python Playwright Framework.
