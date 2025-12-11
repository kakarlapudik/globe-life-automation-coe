# Quarto Reporter Quick Reference

## Installation

```bash
# Install Quarto
# Download from: https://quarto.org

# Install Python dependencies
pip install plotly kaleido matplotlib pandas
```

## Basic Usage

```python
from raptor.reporting.quarto_reporter import QuartoReporter, QuartoConfig

# Create reporter
quarto_reporter = QuartoReporter(
    report_dir="reports/quarto",
    test_reporter=test_reporter
)

# Generate report
output_path = quarto_reporter.generate_report()
```

## Configuration

```python
config = QuartoConfig(
    format="html",        # html, pdf, docx
    theme="cosmo",        # Theme name
    toc=True,             # Table of contents
    code_fold=True,       # Code folding
    fig_width=10,         # Figure width
    fig_height=6          # Figure height
)
```

## Common Tasks

### Generate HTML Report
```python
quarto_reporter.generate_report(
    output_name="report",
    include_visualizations=True
)
```

### Generate PDF Report
```python
config = QuartoConfig(format="pdf")
quarto_reporter.generate_report(config=config)
```

### Multiple Formats
```python
results = quarto_reporter.export_multiple_formats(
    formats=["html", "pdf", "docx"]
)
```

### Parameterized Report
```python
quarto_reporter.generate_report(
    parameters={
        "environment": "prod",
        "version": "2.0.0"
    }
)
```

### From JSON
```python
quarto_reporter.generate_from_json(
    json_file="results.json"
)
```

### Custom Template
```python
template_path = quarto_reporter.create_custom_template(
    "custom",
    template_content
)
```

## Themes

- `default` - Default theme
- `cosmo` - Modern flat
- `flatly` - Flat modern
- `darkly` - Dark theme
- `journal` - Clean journal
- `united` - Ubuntu-inspired
- `lumen` - Light clean
- `sandstone` - Warm

## Report Sections

1. **Executive Summary** - Key metrics
2. **Visualizations** - Interactive charts
3. **Detailed Results** - Test information
4. **Performance Analysis** - Duration metrics

## Visualizations

- Test status pie chart
- Pass rate gauge
- Duration bar chart
- Duration histogram

## Error Handling

```python
try:
    output = quarto_reporter.generate_report()
except RuntimeError as e:
    if "Quarto is not installed" in str(e):
        print("Install Quarto from https://quarto.org")
    else:
        print(f"Error: {e}")
```

## Integration

```python
# With TestReporter
test_reporter = TestReporter()
# ... add results ...

quarto_reporter = QuartoReporter(
    test_reporter=test_reporter
)
quarto_reporter.generate_report()
```

## File Locations

- **Reports**: `reports/quarto/`
- **Templates**: `raptor/reporting/templates/`
- **Examples**: `examples/quarto_reporter_example.py`
- **Tests**: `tests/test_quarto_reporter.py`

## Dependencies

```python
# Check installation
quarto_reporter._check_quarto_installation()

# Install Python packages
QuartoReporter.install_dependencies()
```

## Tips

1. Use HTML for interactive visualizations
2. Use PDF for printing
3. Use Word for editing
4. Parameterize for different environments
5. Create custom templates for audiences
6. Handle errors gracefully
7. Test with small datasets first

## Resources

- [Full Guide](./QUARTO_REPORTING_GUIDE.md)
- [Examples](../examples/quarto_reporter_example.py)
- [Quarto Docs](https://quarto.org)
- [API Reference](./API_REFERENCE_GUIDE.md)
