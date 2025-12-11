# Quarto Reporting Guide

## Overview

The RAPTOR Quarto Reporter provides advanced reporting capabilities with interactive visualizations, multiple export formats, and seamless integration with the existing TestReporter.

## Features

- **Interactive Visualizations**: Plotly and Matplotlib charts
- **Multiple Formats**: Export to HTML, PDF, and Word
- **Parameterized Reports**: Pass custom parameters to reports
- **Custom Templates**: Create and use custom Quarto templates
- **Seamless Integration**: Works with existing TestReporter
- **Rich Content**: Callouts, code folding, and responsive design

## Prerequisites

### Install Quarto

Download and install Quarto from [https://quarto.org](https://quarto.org)

**Verification:**
```bash
quarto --version
```

### Install Python Dependencies

```bash
pip install plotly kaleido matplotlib pandas
```

Or use the built-in installer:
```python
from raptor.reporting.quarto_reporter import QuartoReporter
QuartoReporter.install_dependencies()
```

## Quick Start

### Basic Usage

```python
from raptor.utils.reporter import TestReporter
from raptor.reporting.quarto_reporter import QuartoReporter

# Create test reporter with results
test_reporter = TestReporter()
test_reporter.start_suite("My Test Suite")
# ... add test results ...
test_reporter.end_suite()

# Create Quarto reporter
quarto_reporter = QuartoReporter(
    report_dir="reports/quarto",
    test_reporter=test_reporter
)

# Generate HTML report
output_path = quarto_reporter.generate_report(
    output_name="test_report",
    include_visualizations=True
)
print(f"Report generated: {output_path}")
```

## Configuration

### QuartoConfig Options

```python
from raptor.reporting.quarto_reporter import QuartoConfig

config = QuartoConfig(
    format="html",           # Output format: html, pdf, docx
    theme="cosmo",           # Quarto theme
    toc=True,                # Include table of contents
    toc_depth=3,             # TOC depth
    code_fold=True,          # Enable code folding
    self_contained=True,     # Self-contained HTML
    execute=True,            # Execute code chunks
    fig_width=10,            # Figure width
    fig_height=6             # Figure height
)
```

### Available Themes

- `default` - Default Quarto theme
- `cosmo` - Modern flat theme
- `flatly` - Flat and modern
- `darkly` - Dark theme
- `journal` - Clean journal style
- `united` - Ubuntu-inspired
- `lumen` - Light and clean
- `sandstone` - Warm and inviting

## Report Generation

### Generate HTML Report

```python
output_path = quarto_reporter.generate_report(
    output_name="html_report",
    config=QuartoConfig(format="html"),
    include_visualizations=True
)
```

### Generate PDF Report

```python
config = QuartoConfig(format="pdf")
output_path = quarto_reporter.generate_report(
    output_name="pdf_report",
    config=config,
    include_visualizations=True
)
```

### Generate Word Document

```python
config = QuartoConfig(format="docx")
output_path = quarto_reporter.generate_report(
    output_name="word_report",
    config=config,
    include_visualizations=False  # Limited support in Word
)
```

### Export Multiple Formats

```python
results = quarto_reporter.export_multiple_formats(
    output_name="multi_format_report",
    formats=["html", "pdf", "docx"],
    include_visualizations=True
)

for format_type, path in results.items():
    print(f"{format_type}: {path}")
```

## Parameterized Reports

Pass custom parameters to your reports:

```python
parameters = {
    "environment": "production",
    "version": "2.0.0",
    "build_number": 12345,
    "test_run_id": "TR-2024-001"
}

output_path = quarto_reporter.generate_report(
    output_name="parameterized_report",
    parameters=parameters,
    include_visualizations=True
)
```

Access parameters in custom templates:
```markdown
---
params:
  environment: "staging"
  version: "1.0.0"
---

# Test Report for `r params$environment`

Version: `r params$version`
```

## Custom Templates

### Create Custom Template

```python
custom_template = """---
title: "Custom Executive Report"
author: "QA Team"
format:
  html:
    theme: united
    toc: true
---

# Executive Summary

Custom content here...
"""

template_path = quarto_reporter.create_custom_template(
    "executive",
    custom_template
)
```

### Use Custom Template

```python
output_path = quarto_reporter.generate_report(
    output_name="custom_report",
    template="executive",
    include_visualizations=True
)
```

### Built-in Templates

1. **default.qmd** - Standard comprehensive report
2. **executive.qmd** - High-level executive summary
3. **detailed.qmd** - Detailed technical report

## Visualizations

### Automatic Visualizations

When `include_visualizations=True`, reports include:

1. **Test Status Distribution** - Pie chart showing pass/fail/skip/error
2. **Pass Rate Gauge** - Gauge chart showing overall pass rate
3. **Test Duration Bar Chart** - Duration of each test
4. **Duration Distribution** - Histogram of test durations

### Custom Visualizations

Add custom visualizations in templates:

```python
```{python}
import plotly.graph_objects as go

# Custom chart
fig = go.Figure(data=[
    go.Bar(x=['Test 1', 'Test 2'], y=[2.5, 3.1])
])
fig.show()
```
```

## Integration with TestReporter

### Seamless Workflow

```python
# 1. Create TestReporter
test_reporter = TestReporter()
test_reporter.start_suite("Integration Test")

# 2. Add test results
test_reporter.add_test_result(result)

# 3. Generate traditional HTML report
html_report = test_reporter.generate_html_report()

# 4. Generate Quarto report from same data
quarto_reporter = QuartoReporter(test_reporter=test_reporter)
quarto_report = quarto_reporter.generate_report()
```

### Generate from JSON

```python
# Export test results to JSON
json_path = test_reporter.export_json("results.json")

# Generate Quarto report from JSON
quarto_reporter = QuartoReporter()
output_path = quarto_reporter.generate_from_json(
    json_file=json_path,
    output_name="json_report"
)
```

## Report Sections

### Executive Summary

High-level metrics in a callout box:
- Total tests
- Pass/fail/skip/error counts
- Pass rate percentage
- Total duration

### Test Results Visualization

Interactive charts:
- Status distribution pie chart
- Pass rate gauge
- Performance metrics

### Detailed Test Results

For each test:
- Test name and ID
- Status with emoji indicator
- Duration and timestamps
- Error messages (if failed)
- Stack traces (collapsible)
- Screenshots (embedded)
- Metadata

### Performance Analysis

- Test duration bar chart
- Duration distribution histogram
- Statistical summaries

## Advanced Features

### Code Folding

Control code visibility:
```python
config = QuartoConfig(
    code_fold=True,   # Fold code by default
    # or
    code_fold=False   # Show code by default
)
```

### Self-Contained HTML

Create standalone HTML files:
```python
config = QuartoConfig(
    format="html",
    self_contained=True  # Embed all resources
)
```

### Custom Figure Sizes

```python
config = QuartoConfig(
    fig_width=12,   # Width in inches
    fig_height=8    # Height in inches
)
```

## Best Practices

### 1. Use Appropriate Formats

- **HTML**: Best for interactive visualizations and web viewing
- **PDF**: Best for printing and formal documentation
- **Word**: Best for editing and collaboration

### 2. Optimize Visualizations

- Use `include_visualizations=False` for Word documents
- Adjust figure sizes for different formats
- Consider file size for self-contained HTML

### 3. Parameterize Reports

- Pass environment information
- Include version numbers
- Add build/run identifiers

### 4. Custom Templates

- Create templates for different audiences
- Executive summaries for management
- Detailed reports for developers
- Compliance reports for auditors

### 5. Error Handling

```python
try:
    output_path = quarto_reporter.generate_report()
    print(f"Success: {output_path}")
except RuntimeError as e:
    if "Quarto is not installed" in str(e):
        print("Please install Quarto")
    else:
        print(f"Error: {e}")
```

## Troubleshooting

### Quarto Not Found

**Error**: `RuntimeError: Quarto is not installed`

**Solution**: Install Quarto from https://quarto.org

### Missing Python Packages

**Error**: `ModuleNotFoundError: No module named 'plotly'`

**Solution**:
```bash
pip install plotly kaleido matplotlib pandas
```

### PDF Generation Fails

**Error**: PDF rendering fails

**Solution**: Install LaTeX distribution:
- **Windows**: MiKTeX or TeX Live
- **macOS**: MacTeX
- **Linux**: TeX Live

### Rendering Timeout

**Error**: `RuntimeError: Quarto rendering timed out`

**Solution**: 
- Reduce number of visualizations
- Simplify complex charts
- Increase timeout in code

### Memory Issues

**Error**: Out of memory during rendering

**Solution**:
- Generate reports in batches
- Reduce figure sizes
- Disable self-contained HTML

## Examples

See `examples/quarto_reporter_example.py` for complete examples:

1. Basic HTML report
2. Custom configuration
3. Parameterized reports
4. Multiple format export
5. Custom templates
6. JSON-based generation
7. TestReporter integration

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

### QuartoConfig

```python
@dataclass
class QuartoConfig:
    format: str = "html"
    theme: str = "cosmo"
    toc: bool = True
    toc_depth: int = 3
    code_fold: bool = True
    self_contained: bool = True
    execute: bool = True
    fig_width: int = 10
    fig_height: int = 6
```

## Resources

- [Quarto Documentation](https://quarto.org/docs/guide/)
- [Plotly Python](https://plotly.com/python/)
- [Matplotlib Documentation](https://matplotlib.org/)
- [RAPTOR Framework Documentation](./API_REFERENCE_GUIDE.md)

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review examples in `examples/quarto_reporter_example.py`
3. Consult Quarto documentation
4. Open an issue on the project repository
