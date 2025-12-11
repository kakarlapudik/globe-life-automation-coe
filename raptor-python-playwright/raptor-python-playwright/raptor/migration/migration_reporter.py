"""
Migration Report Generator

Generates comprehensive reports for Java to Python migration.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
from dataclasses import dataclass, asdict

from .java_to_python_converter import ConversionResult
from .ddfe_validator import ValidationResult, ValidationSeverity
from .compatibility_checker import CompatibilityCheckResult


@dataclass
class MigrationReport:
    """Complete migration report"""
    timestamp: str
    project_name: str
    conversion_results: List[Dict]
    validation_results: List[Dict]
    compatibility_results: List[Dict]
    summary: Dict
    recommendations: List[str]


class MigrationReporter:
    """
    Generates comprehensive migration reports.
    
    Supports multiple output formats:
    - HTML (detailed, interactive)
    - JSON (machine-readable)
    - Markdown (documentation)
    - Text (console output)
    """
    
    def __init__(self, project_name: str = "RAPTOR Migration"):
        """
        Initialize the reporter.
        
        Args:
            project_name: Name of the migration project
        """
        self.project_name = project_name
        self.timestamp = datetime.now().isoformat()
    
    def generate_report(
        self,
        conversion_results: List[ConversionResult] = None,
        validation_results: List[ValidationResult] = None,
        compatibility_results: List[CompatibilityCheckResult] = None,
        output_format: str = 'html',
        output_path: Optional[Path] = None
    ) -> str:
        """
        Generate a migration report.
        
        Args:
            conversion_results: Results from Java to Python conversion
            validation_results: Results from DDFE validation
            compatibility_results: Results from compatibility checking
            output_format: Format for output ('html', 'json', 'markdown', 'text')
            output_path: Optional path to save the report
            
        Returns:
            Report content as string
        """
        # Prepare data
        report_data = self._prepare_report_data(
            conversion_results or [],
            validation_results or [],
            compatibility_results or []
        )
        
        # Generate report based on format
        if output_format == 'html':
            report_content = self._generate_html_report(report_data)
        elif output_format == 'json':
            report_content = self._generate_json_report(report_data)
        elif output_format == 'markdown':
            report_content = self._generate_markdown_report(report_data)
        else:  # text
            report_content = self._generate_text_report(report_data)
        
        # Save to file if path provided
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(report_content, encoding='utf-8')
        
        return report_content
    
    def _prepare_report_data(
        self,
        conversion_results: List[ConversionResult],
        validation_results: List[ValidationResult],
        compatibility_results: List[CompatibilityCheckResult]
    ) -> MigrationReport:
        """Prepare report data structure"""
        # Convert results to dictionaries
        conversion_dicts = [
            {
                'warnings': r.warnings,
                'manual_review_needed': r.manual_review_needed,
                'conversion_stats': r.conversion_stats
            }
            for r in conversion_results
        ]
        
        validation_dicts = [
            {
                'is_valid': r.is_valid,
                'element_name': r.element.pv_name,
                'compatibility_score': r.compatibility_score,
                'issues': [
                    {
                        'severity': issue.severity.value,
                        'field': issue.field,
                        'message': issue.message,
                        'suggestion': issue.suggestion
                    }
                    for issue in r.issues
                ]
            }
            for r in validation_results
        ]
        
        compatibility_dicts = [asdict(r) for r in compatibility_results]
        
        # Calculate summary
        summary = self._calculate_summary(
            conversion_results,
            validation_results,
            compatibility_results
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            conversion_results,
            validation_results,
            compatibility_results
        )
        
        return MigrationReport(
            timestamp=self.timestamp,
            project_name=self.project_name,
            conversion_results=conversion_dicts,
            validation_results=validation_dicts,
            compatibility_results=compatibility_dicts,
            summary=summary,
            recommendations=recommendations
        )
    
    def _calculate_summary(
        self,
        conversion_results: List[ConversionResult],
        validation_results: List[ValidationResult],
        compatibility_results: List[CompatibilityCheckResult]
    ) -> Dict:
        """Calculate summary statistics"""
        summary = {
            'conversion': {
                'total_files': len(conversion_results),
                'total_methods': sum(r.conversion_stats.get('methods_converted', 0) for r in conversion_results),
                'total_warnings': sum(len(r.warnings) for r in conversion_results),
                'total_manual_review': sum(len(r.manual_review_needed) for r in conversion_results),
            },
            'validation': {
                'total_elements': len(validation_results),
                'valid_elements': sum(1 for r in validation_results if r.is_valid),
                'invalid_elements': sum(1 for r in validation_results if not r.is_valid),
                'avg_compatibility_score': (
                    sum(r.compatibility_score for r in validation_results) / len(validation_results)
                    if validation_results else 0.0
                ),
                'total_errors': sum(
                    sum(1 for issue in r.issues if issue.severity == ValidationSeverity.ERROR)
                    for r in validation_results
                ),
                'total_warnings': sum(
                    sum(1 for issue in r.issues if issue.severity == ValidationSeverity.WARNING)
                    for r in validation_results
                ),
            },
            'compatibility': {
                'total_checks': len(compatibility_results),
                'compatible': sum(1 for r in compatibility_results if r.is_compatible),
                'incompatible': sum(1 for r in compatibility_results if not r.is_compatible),
            }
        }
        
        return summary
    
    def _generate_recommendations(
        self,
        conversion_results: List[ConversionResult],
        validation_results: List[ValidationResult],
        compatibility_results: List[CompatibilityCheckResult]
    ) -> List[str]:
        """Generate recommendations based on results"""
        recommendations = []
        
        # Conversion recommendations
        total_manual_review = sum(len(r.manual_review_needed) for r in conversion_results)
        if total_manual_review > 0:
            recommendations.append(
                f"Review {total_manual_review} items that require manual attention in converted code"
            )
        
        # Validation recommendations
        invalid_count = sum(1 for r in validation_results if not r.is_valid)
        if invalid_count > 0:
            recommendations.append(
                f"Fix {invalid_count} invalid element definitions before migration"
            )
        
        avg_score = (
            sum(r.compatibility_score for r in validation_results) / len(validation_results)
            if validation_results else 1.0
        )
        if avg_score < 0.7:
            recommendations.append(
                "Average compatibility score is low. Consider updating element definitions"
            )
        
        # Compatibility recommendations
        incompatible_count = sum(1 for r in compatibility_results if not r.is_compatible)
        if incompatible_count > 0:
            recommendations.append(
                f"Address {incompatible_count} compatibility issues before migration"
            )
        
        # General recommendations
        if not recommendations:
            recommendations.append("Migration looks good! Proceed with testing")
        else:
            recommendations.append("Run comprehensive tests after migration")
            recommendations.append("Update documentation to reflect Python/Playwright changes")
        
        return recommendations
    
    def _generate_html_report(self, report_data: MigrationReport) -> str:
        """Generate HTML report"""
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{report_data.project_name} - Migration Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            margin: 0 0 10px 0;
        }}
        .header .timestamp {{
            opacity: 0.9;
            font-size: 14px;
        }}
        .section {{
            background: white;
            padding: 25px;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .section h2 {{
            margin-top: 0;
            color: #333;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .stat-card {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            border-left: 4px solid #667eea;
        }}
        .stat-card .label {{
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .stat-card .value {{
            font-size: 28px;
            font-weight: bold;
            color: #333;
            margin-top: 5px;
        }}
        .recommendations {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
        }}
        .recommendations h3 {{
            margin-top: 0;
            color: #856404;
        }}
        .recommendations ul {{
            margin: 10px 0;
            padding-left: 20px;
        }}
        .recommendations li {{
            margin: 8px 0;
            color: #856404;
        }}
        .success {{ color: #28a745; }}
        .warning {{ color: #ffc107; }}
        .error {{ color: #dc3545; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #f8f9fa;
            font-weight: 600;
            color: #333;
        }}
        tr:hover {{
            background-color: #f8f9fa;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{report_data.project_name}</h1>
        <div class="timestamp">Generated: {report_data.timestamp}</div>
    </div>
    
    <div class="section">
        <h2>Summary</h2>
        <div class="stats-grid">
            <div class="stat-card">
                <div class="label">Files Converted</div>
                <div class="value">{report_data.summary['conversion']['total_files']}</div>
            </div>
            <div class="stat-card">
                <div class="label">Methods Converted</div>
                <div class="value">{report_data.summary['conversion']['total_methods']}</div>
            </div>
            <div class="stat-card">
                <div class="label">Elements Validated</div>
                <div class="value">{report_data.summary['validation']['total_elements']}</div>
            </div>
            <div class="stat-card">
                <div class="label">Compatibility Score</div>
                <div class="value">{report_data.summary['validation']['avg_compatibility_score']:.2f}</div>
            </div>
        </div>
    </div>
    
    <div class="section">
        <h2>Conversion Results</h2>
        <div class="stats-grid">
            <div class="stat-card">
                <div class="label">Warnings</div>
                <div class="value warning">{report_data.summary['conversion']['total_warnings']}</div>
            </div>
            <div class="stat-card">
                <div class="label">Manual Review Items</div>
                <div class="value error">{report_data.summary['conversion']['total_manual_review']}</div>
            </div>
        </div>
    </div>
    
    <div class="section">
        <h2>Validation Results</h2>
        <div class="stats-grid">
            <div class="stat-card">
                <div class="label">Valid Elements</div>
                <div class="value success">{report_data.summary['validation']['valid_elements']}</div>
            </div>
            <div class="stat-card">
                <div class="label">Invalid Elements</div>
                <div class="value error">{report_data.summary['validation']['invalid_elements']}</div>
            </div>
            <div class="stat-card">
                <div class="label">Errors</div>
                <div class="value error">{report_data.summary['validation']['total_errors']}</div>
            </div>
            <div class="stat-card">
                <div class="label">Warnings</div>
                <div class="value warning">{report_data.summary['validation']['total_warnings']}</div>
            </div>
        </div>
    </div>
    
    <div class="recommendations">
        <h3>Recommendations</h3>
        <ul>
            {''.join(f'<li>{rec}</li>' for rec in report_data.recommendations)}
        </ul>
    </div>
</body>
</html>"""
        
        return html
    
    def _generate_json_report(self, report_data: MigrationReport) -> str:
        """Generate JSON report"""
        return json.dumps(asdict(report_data), indent=2)
    
    def _generate_markdown_report(self, report_data: MigrationReport) -> str:
        """Generate Markdown report"""
        md = f"""# {report_data.project_name}

**Generated:** {report_data.timestamp}

## Summary

### Conversion
- **Files Converted:** {report_data.summary['conversion']['total_files']}
- **Methods Converted:** {report_data.summary['conversion']['total_methods']}
- **Warnings:** {report_data.summary['conversion']['total_warnings']}
- **Manual Review Items:** {report_data.summary['conversion']['total_manual_review']}

### Validation
- **Total Elements:** {report_data.summary['validation']['total_elements']}
- **Valid Elements:** {report_data.summary['validation']['valid_elements']}
- **Invalid Elements:** {report_data.summary['validation']['invalid_elements']}
- **Average Compatibility Score:** {report_data.summary['validation']['avg_compatibility_score']:.2f}
- **Errors:** {report_data.summary['validation']['total_errors']}
- **Warnings:** {report_data.summary['validation']['total_warnings']}

### Compatibility
- **Total Checks:** {report_data.summary['compatibility']['total_checks']}
- **Compatible:** {report_data.summary['compatibility']['compatible']}
- **Incompatible:** {report_data.summary['compatibility']['incompatible']}

## Recommendations

"""
        for rec in report_data.recommendations:
            md += f"- {rec}\n"
        
        return md
    
    def _generate_text_report(self, report_data: MigrationReport) -> str:
        """Generate plain text report"""
        text = f"""
{'='*80}
{report_data.project_name}
{'='*80}
Generated: {report_data.timestamp}

SUMMARY
-------
Conversion:
  Files Converted: {report_data.summary['conversion']['total_files']}
  Methods Converted: {report_data.summary['conversion']['total_methods']}
  Warnings: {report_data.summary['conversion']['total_warnings']}
  Manual Review Items: {report_data.summary['conversion']['total_manual_review']}

Validation:
  Total Elements: {report_data.summary['validation']['total_elements']}
  Valid Elements: {report_data.summary['validation']['valid_elements']}
  Invalid Elements: {report_data.summary['validation']['invalid_elements']}
  Avg Compatibility Score: {report_data.summary['validation']['avg_compatibility_score']:.2f}
  Errors: {report_data.summary['validation']['total_errors']}
  Warnings: {report_data.summary['validation']['total_warnings']}

Compatibility:
  Total Checks: {report_data.summary['compatibility']['total_checks']}
  Compatible: {report_data.summary['compatibility']['compatible']}
  Incompatible: {report_data.summary['compatibility']['incompatible']}

RECOMMENDATIONS
---------------
"""
        for i, rec in enumerate(report_data.recommendations, 1):
            text += f"{i}. {rec}\n"
        
        text += "\n" + "="*80 + "\n"
        
        return text
