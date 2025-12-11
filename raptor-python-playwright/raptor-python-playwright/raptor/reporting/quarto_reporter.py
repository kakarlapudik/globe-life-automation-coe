"""
Quarto Reporter for RAPTOR Framework

This module provides Quarto-based reporting capabilities with:
- Interactive visualizations (plotly, matplotlib)
- Parameterized report generation
- Multiple export formats (HTML, PDF, Word)
- Integration with existing TestReporter
"""

import os
import json
import subprocess
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from dataclasses import dataclass

from raptor.utils.reporter import TestReporter, TestResult, TestStatistics


@dataclass
class QuartoConfig:
    """
    Configuration for Quarto report generation.
    
    Attributes:
        format: Output format (html, pdf, docx)
        theme: Quarto theme name
        toc: Include table of contents
        toc_depth: Depth of table of contents
        code_fold: Enable code folding
        self_contained: Create self-contained HTML
        execute: Execute code chunks
        fig_width: Default figure width
        fig_height: Default figure height
    """
    format: str = "html"
    theme: str = "cosmo"
    toc: bool = True
    toc_depth: int = 3
    code_fold: bool = True
    self_contained: bool = True
    execute: bool = True
    fig_width: int = 10
    fig_height: int = 6
    
    def to_yaml(self) -> str:
        """Convert configuration to YAML format."""
        yaml_lines = [
            "format:",
            f"  {self.format}:",
            f"    theme: {self.theme}",
            f"    toc: {str(self.toc).lower()}",
            f"    toc-depth: {self.toc_depth}",
            f"    code-fold: {str(self.code_fold).lower()}",
        ]
        
        if self.format == "html":
            yaml_lines.append(f"    self-contained: {str(self.self_contained).lower()}")
        
        yaml_lines.extend([
            f"execute:",
            f"  echo: false",
            f"  warning: false",
            f"  message: false",
            f"fig-width: {self.fig_width}",
            f"fig-height: {self.fig_height}",
        ])
        
        return "\n".join(yaml_lines)


class QuartoReporter:
    """
    Manages Quarto-based test reporting with interactive visualizations.
    
    Provides functionality to generate rich, interactive reports using Quarto,
    with support for plotly and matplotlib visualizations, parameterized reports,
    and multiple export formats.
    """
    
    def __init__(
        self,
        report_dir: str = "reports/quarto",
        test_reporter: Optional[TestReporter] = None
    ):
        """
        Initialize the QuartoReporter.
        
        Args:
            report_dir: Directory where Quarto reports will be saved
            test_reporter: Optional TestReporter instance to integrate with
        """
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        
        self.test_reporter = test_reporter
        self.template_dir = Path(__file__).parent / "templates"
        self.template_dir.mkdir(parents=True, exist_ok=True)
        
        # Check if Quarto is installed
        self._check_quarto_installation()
    
    def _check_quarto_installation(self) -> bool:
        """
        Check if Quarto is installed and available.
        
        Returns:
            True if Quarto is installed, False otherwise
        """
        try:
            result = subprocess.run(
                ["quarto", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def generate_report(
        self,
        output_name: str = "test_report",
        config: Optional[QuartoConfig] = None,
        parameters: Optional[Dict[str, Any]] = None,
        template: Optional[str] = None,
        include_visualizations: bool = True
    ) -> str:
        """
        Generate a Quarto report from test results.
        
        Args:
            output_name: Base name for output file (without extension)
            config: QuartoConfig object for report configuration
            parameters: Optional parameters to pass to the report
            template: Optional custom template name
            include_visualizations: Whether to include interactive visualizations
            
        Returns:
            Path to the generated report
            
        Raises:
            RuntimeError: If Quarto is not installed
            ValueError: If test_reporter is not set
        """
        if not self._check_quarto_installation():
            raise RuntimeError(
                "Quarto is not installed. Please install Quarto from https://quarto.org"
            )
        
        if self.test_reporter is None:
            raise ValueError("test_reporter must be set before generating reports")
        
        # Use default config if not provided
        if config is None:
            config = QuartoConfig()
        
        # Use default template if not provided
        if template is None:
            template = "default"
        
        # Create timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        qmd_file = self.report_dir / f"{output_name}_{timestamp}.qmd"
        
        # Generate Quarto markdown content
        qmd_content = self._generate_qmd_content(
            config=config,
            parameters=parameters or {},
            template=template,
            include_visualizations=include_visualizations
        )
        
        # Write QMD file
        with open(qmd_file, 'w', encoding='utf-8') as f:
            f.write(qmd_content)
        
        # Render the report
        output_file = self._render_quarto_report(qmd_file, config)
        
        return str(output_file)
    
    def _generate_qmd_content(
        self,
        config: QuartoConfig,
        parameters: Dict[str, Any],
        template: str,
        include_visualizations: bool
    ) -> str:
        """
        Generate Quarto markdown content.
        
        Args:
            config: QuartoConfig object
            parameters: Report parameters
            template: Template name
            include_visualizations: Whether to include visualizations
            
        Returns:
            Complete QMD content as string
        """
        stats = self.test_reporter.get_statistics()
        
        # Build YAML header
        yaml_header = self._build_yaml_header(config, parameters)
        
        # Build report content
        content_parts = [
            yaml_header,
            "",
            "# Test Execution Report",
            "",
            f"**Suite:** {self.test_reporter.suite_name}",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Executive Summary",
            "",
            self._generate_summary_section(stats),
            "",
        ]
        
        if include_visualizations:
            content_parts.extend([
                "## Test Results Visualization",
                "",
                self._generate_visualization_section(stats),
                "",
            ])
        
        content_parts.extend([
            "## Detailed Test Results",
            "",
            self._generate_detailed_results_section(),
            "",
        ])
        
        if include_visualizations:
            content_parts.extend([
                "## Performance Analysis",
                "",
                self._generate_performance_section(),
                "",
            ])
        
        return "\n".join(content_parts)
    
    def _build_yaml_header(
        self,
        config: QuartoConfig,
        parameters: Dict[str, Any]
    ) -> str:
        """
        Build YAML header for Quarto document.
        
        Args:
            config: QuartoConfig object
            parameters: Report parameters
            
        Returns:
            YAML header string
        """
        header_parts = [
            "---",
            f"title: \"RAPTOR Test Report - {self.test_reporter.suite_name}\"",
            f"author: \"RAPTOR Framework\"",
            f"date: \"{datetime.now().strftime('%Y-%m-%d')}\"",
        ]
        
        # Add parameters if provided
        if parameters:
            header_parts.append("params:")
            for key, value in parameters.items():
                if isinstance(value, str):
                    header_parts.append(f"  {key}: \"{value}\"")
                else:
                    header_parts.append(f"  {key}: {value}")
        
        # Add format configuration
        header_parts.append(config.to_yaml())
        header_parts.append("---")
        
        return "\n".join(header_parts)
    
    def _generate_summary_section(self, stats: TestStatistics) -> str:
        """
        Generate summary section with key metrics.
        
        Args:
            stats: TestStatistics object
            
        Returns:
            Markdown content for summary section
        """
        return f"""
::: {{.callout-note}}
## Test Execution Summary

- **Total Tests:** {stats.total_tests}
- **Passed:** {stats.passed} ({stats.pass_rate:.1f}%)
- **Failed:** {stats.failed}
- **Skipped:** {stats.skipped}
- **Errors:** {stats.errors}
- **Total Duration:** {self._format_duration(stats.total_duration)}
:::
"""
    
    def _generate_visualization_section(self, stats: TestStatistics) -> str:
        """
        Generate visualization section with plotly charts.
        
        Args:
            stats: TestStatistics object
            
        Returns:
            Markdown content with Python code for visualizations
        """
        return f"""
```{{python}}
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# Test Status Distribution
fig1 = go.Figure(data=[go.Pie(
    labels=['Passed', 'Failed', 'Skipped', 'Errors'],
    values=[{stats.passed}, {stats.failed}, {stats.skipped}, {stats.errors}],
    marker=dict(colors=['#4caf50', '#f44336', '#ff9800', '#e91e63']),
    hole=0.4
)])
fig1.update_layout(
    title="Test Status Distribution",
    showlegend=True,
    height=400
)
fig1.show()

# Pass Rate Gauge
fig2 = go.Figure(go.Indicator(
    mode="gauge+number+delta",
    value={stats.pass_rate:.1f},
    domain={{'x': [0, 1], 'y': [0, 1]}},
    title={{'text': "Pass Rate (%)"}},
    delta={{'reference': 100}},
    gauge={{
        'axis': {{'range': [None, 100]}},
        'bar': {{'color': "darkblue"}},
        'steps': [
            {{'range': [0, 50], 'color': "lightgray"}},
            {{'range': [50, 80], 'color': "gray"}},
            {{'range': [80, 100], 'color': "lightgreen"}}
        ],
        'threshold': {{
            'line': {{'color': "red", 'width': 4}},
            'thickness': 0.75,
            'value': 90
        }}
    }}
))
fig2.update_layout(height=300)
fig2.show()
```
"""
    
    def _generate_detailed_results_section(self) -> str:
        """
        Generate detailed results section with test information.
        
        Returns:
            Markdown content for detailed results
        """
        if not self.test_reporter.test_results:
            return "*No test results available.*"
        
        content_parts = []
        
        for idx, result in enumerate(self.test_reporter.test_results, 1):
            status_emoji = {
                "passed": "✅",
                "failed": "❌",
                "skipped": "⏭️",
                "error": "⚠️"
            }.get(result.status.value, "❓")
            
            content_parts.append(f"### {status_emoji} Test {idx}: {result.test_name}")
            content_parts.append("")
            content_parts.append(f"- **Test ID:** `{result.test_id}`")
            content_parts.append(f"- **Status:** {result.status.value.upper()}")
            content_parts.append(f"- **Duration:** {self._format_duration(result.duration)}")
            content_parts.append(f"- **Start Time:** {result.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            content_parts.append(f"- **End Time:** {result.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
            content_parts.append("")
            
            if result.error_message:
                content_parts.append("::: {.callout-warning collapse=\"true\"}")
                content_parts.append("## Error Details")
                content_parts.append("")
                content_parts.append("```")
                content_parts.append(result.error_message)
                content_parts.append("```")
                content_parts.append(":::")
                content_parts.append("")
            
            if result.stack_trace:
                content_parts.append("::: {.callout-tip collapse=\"true\"}")
                content_parts.append("## Stack Trace")
                content_parts.append("")
                content_parts.append("```")
                content_parts.append(result.stack_trace)
                content_parts.append("```")
                content_parts.append(":::")
                content_parts.append("")
            
            if result.screenshots:
                content_parts.append("**Screenshots:**")
                content_parts.append("")
                for screenshot in result.screenshots:
                    if os.path.exists(screenshot):
                        content_parts.append(f"![{os.path.basename(screenshot)}]({screenshot})")
                        content_parts.append("")
            
            if result.metadata:
                content_parts.append("**Metadata:**")
                content_parts.append("")
                for key, value in result.metadata.items():
                    content_parts.append(f"- **{key}:** {value}")
                content_parts.append("")
            
            content_parts.append("---")
            content_parts.append("")
        
        return "\n".join(content_parts)
    
    def _generate_performance_section(self) -> str:
        """
        Generate performance analysis section with duration charts.
        
        Returns:
            Markdown content with performance visualizations
        """
        if not self.test_reporter.test_results:
            return "*No performance data available.*"
        
        # Prepare data for visualization
        test_names = [r.test_name[:30] + "..." if len(r.test_name) > 30 else r.test_name 
                     for r in self.test_reporter.test_results]
        durations = [r.duration for r in self.test_reporter.test_results]
        statuses = [r.status.value for r in self.test_reporter.test_results]
        
        return f"""
```{{python}}
import plotly.graph_objects as go
import plotly.express as px

# Test Duration Bar Chart
test_names = {test_names}
durations = {durations}
statuses = {statuses}

# Color mapping
color_map = {{
    'passed': '#4caf50',
    'failed': '#f44336',
    'skipped': '#ff9800',
    'error': '#e91e63'
}}
colors = [color_map.get(s, '#999999') for s in statuses]

fig = go.Figure(data=[
    go.Bar(
        x=test_names,
        y=durations,
        marker=dict(color=colors),
        text=[f'{{d:.2f}}s' for d in durations],
        textposition='auto',
    )
])

fig.update_layout(
    title="Test Execution Duration",
    xaxis_title="Test Name",
    yaxis_title="Duration (seconds)",
    height=500,
    xaxis={{'tickangle': -45}}
)

fig.show()

# Duration Distribution
fig2 = go.Figure(data=[go.Histogram(
    x=durations,
    nbinsx=20,
    marker=dict(color='#667eea'),
)])

fig2.update_layout(
    title="Duration Distribution",
    xaxis_title="Duration (seconds)",
    yaxis_title="Count",
    height=400
)

fig2.show()
```
"""
    
    def _render_quarto_report(
        self,
        qmd_file: Path,
        config: QuartoConfig
    ) -> Path:
        """
        Render Quarto document to specified format.
        
        Args:
            qmd_file: Path to QMD file
            config: QuartoConfig object
            
        Returns:
            Path to rendered output file
            
        Raises:
            RuntimeError: If rendering fails
        """
        try:
            # Determine output file extension
            ext_map = {
                "html": ".html",
                "pdf": ".pdf",
                "docx": ".docx"
            }
            output_ext = ext_map.get(config.format, ".html")
            output_file = qmd_file.with_suffix(output_ext)
            
            # Run quarto render
            result = subprocess.run(
                ["quarto", "render", str(qmd_file)],
                capture_output=True,
                text=True,
                timeout=300,
                cwd=str(qmd_file.parent)
            )
            
            if result.returncode != 0:
                raise RuntimeError(
                    f"Quarto rendering failed:\n{result.stderr}"
                )
            
            return output_file
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("Quarto rendering timed out after 5 minutes")
        except Exception as e:
            raise RuntimeError(f"Failed to render Quarto report: {str(e)}")
    
    def generate_from_json(
        self,
        json_file: str,
        output_name: str = "test_report",
        config: Optional[QuartoConfig] = None,
        include_visualizations: bool = True
    ) -> str:
        """
        Generate Quarto report from JSON test results.
        
        Args:
            json_file: Path to JSON file with test results
            output_name: Base name for output file
            config: QuartoConfig object
            include_visualizations: Whether to include visualizations
            
        Returns:
            Path to generated report
        """
        # Load JSON data
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Create temporary TestReporter and populate it
        temp_reporter = TestReporter()
        temp_reporter.suite_name = data.get("suite_name", "Test Suite")
        
        if data.get("start_time"):
            temp_reporter.suite_start_time = datetime.fromisoformat(data["start_time"])
        if data.get("end_time"):
            temp_reporter.suite_end_time = datetime.fromisoformat(data["end_time"])
        
        # Reconstruct test results
        from raptor.utils.reporter import TestStatus
        for result_data in data.get("test_results", []):
            result = TestResult(
                test_id=result_data["test_id"],
                test_name=result_data["test_name"],
                status=TestStatus(result_data["status"]),
                duration=result_data["duration"],
                start_time=datetime.fromisoformat(result_data["start_time"]),
                end_time=datetime.fromisoformat(result_data["end_time"]),
                error_message=result_data.get("error_message"),
                stack_trace=result_data.get("stack_trace"),
                screenshots=result_data.get("screenshots", []),
                metadata=result_data.get("metadata", {})
            )
            temp_reporter.add_test_result(result)
        
        # Set temporary reporter and generate
        original_reporter = self.test_reporter
        self.test_reporter = temp_reporter
        
        try:
            return self.generate_report(
                output_name=output_name,
                config=config,
                include_visualizations=include_visualizations
            )
        finally:
            self.test_reporter = original_reporter
    
    def create_custom_template(
        self,
        template_name: str,
        template_content: str
    ) -> Path:
        """
        Create a custom Quarto template.
        
        Args:
            template_name: Name for the template
            template_content: QMD template content
            
        Returns:
            Path to created template file
        """
        template_file = self.template_dir / f"{template_name}.qmd"
        
        with open(template_file, 'w', encoding='utf-8') as f:
            f.write(template_content)
        
        return template_file
    
    def export_multiple_formats(
        self,
        output_name: str = "test_report",
        formats: Optional[List[str]] = None,
        parameters: Optional[Dict[str, Any]] = None,
        include_visualizations: bool = True
    ) -> Dict[str, str]:
        """
        Export report in multiple formats.
        
        Args:
            output_name: Base name for output files
            formats: List of formats (html, pdf, docx)
            parameters: Optional parameters
            include_visualizations: Whether to include visualizations
            
        Returns:
            Dictionary mapping format to output file path
        """
        if formats is None:
            formats = ["html", "pdf", "docx"]
        
        results = {}
        
        for fmt in formats:
            try:
                config = QuartoConfig(format=fmt)
                output_path = self.generate_report(
                    output_name=f"{output_name}_{fmt}",
                    config=config,
                    parameters=parameters,
                    include_visualizations=include_visualizations
                )
                results[fmt] = output_path
            except Exception as e:
                results[fmt] = f"Error: {str(e)}"
        
        return results
    
    def _format_duration(self, seconds: float) -> str:
        """
        Format duration in human-readable format.
        
        Args:
            seconds: Duration in seconds
            
        Returns:
            Formatted duration string
        """
        if seconds < 1:
            return f"{seconds * 1000:.0f}ms"
        elif seconds < 60:
            return f"{seconds:.2f}s"
        else:
            minutes = int(seconds // 60)
            remaining_seconds = seconds % 60
            return f"{minutes}m {remaining_seconds:.1f}s"
    
    @staticmethod
    def install_dependencies() -> bool:
        """
        Install required Python packages for Quarto reporting.
        
        Returns:
            True if installation successful, False otherwise
        """
        packages = ["plotly", "kaleido", "matplotlib", "pandas"]
        
        try:
            for package in packages:
                subprocess.run(
                    ["pip", "install", package],
                    capture_output=True,
                    timeout=60
                )
            return True
        except Exception:
            return False
