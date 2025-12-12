#!/usr/bin/env python
"""
Script to generate an enhanced HTML report with detailed test case names, validation criteria, and URL information
"""

import json
import os
import glob
from datetime import datetime

def load_json_reports():
    """Load all JSON reports from the reports directory"""
    json_files = glob.glob("reports/uc*_tc*_links_report.json")
    reports = []
    
    for file_path in json_files:
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                reports.append(data)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
    
    # Sort by test case ID
    reports.sort(key=lambda x: x.get('test_case_id', ''))
    return reports

def generate_enhanced_html_report():
    """Generate comprehensive HTML report with all test case details"""
    reports = load_json_reports()
    
    if not reports:
        print("No JSON reports found!")
        return
    
    # Calculate overall statistics
    total_tests = len(reports)
    passed_tests = sum(1 for r in reports if r.get('validation_results', {}).get('overall_status') == 'PASS')
    total_links = sum(r.get('total_links', 0) for r in reports)
    total_valid = sum(r.get('valid_links_count', 0) for r in reports)
    total_broken = sum(r.get('broken_links_count', 0) for r in reports)
    total_critical = sum(r.get('critical_failures_count', 0) for r in reports)
    total_acceptable = sum(r.get('acceptable_failures_count', 0) for r in reports)
    
    overall_success_rate = (total_valid / total_links * 100) if total_links > 0 else 0
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced AI Test Automation Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f8f9fa;
            color: #333;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 3px solid #3498db;
            padding-bottom: 15px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 40px;
            margin-bottom: 20px;
            border-left: 4px solid #3498db;
            padding-left: 15px;
        }}
        h3 {{
            color: #2c3e50;
            margin-top: 30px;
            margin-bottom: 15px;
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .summary-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        .summary-card h3 {{
            margin: 0 0 10px 0;
            font-size: 2.5em;
            font-weight: bold;
            color: white;
            border: none;
            padding: 0;
        }}
        .summary-card p {{
            margin: 0;
            opacity: 0.9;
            font-size: 1.1em;
        }}
        .test-case {{
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            margin-bottom: 30px;
            overflow: hidden;
        }}
        .test-header {{
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white;
            padding: 20px;
            margin: 0;
        }}
        .test-header.failed {{
            background: linear-gradient(135deg, #dc3545 0%, #e74c3c 100%);
        }}
        .test-content {{
            padding: 25px;
        }}
        .test-meta {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 25px;
        }}
        .meta-item {{
            background: white;
            padding: 15px;
            border-radius: 6px;
            border-left: 4px solid #3498db;
        }}
        .meta-label {{
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 5px;
        }}
        .meta-value {{
            color: #34495e;
        }}
        .priority-high {{
            color: #e74c3c;
            font-weight: bold;
        }}
        .priority-medium {{
            color: #f39c12;
            font-weight: bold;
        }}
        .priority-low {{
            color: #27ae60;
            font-weight: bold;
        }}
        .status-pass {{
            color: #27ae60;
            font-weight: bold;
            font-size: 1.2em;
        }}
        .status-fail {{
            color: #e74c3c;
            font-weight: bold;
            font-size: 1.2em;
        }}
        .criteria-list {{
            background: white;
            padding: 20px;
            border-radius: 6px;
            margin-bottom: 25px;
        }}
        .criteria-item {{
            display: flex;
            align-items: center;
            margin-bottom: 10px;
            padding: 8px;
            border-radius: 4px;
        }}
        .criteria-item.met {{
            background-color: #d4edda;
        }}
        .criteria-item.not-met {{
            background-color: #f8d7da;
        }}
        .criteria-icon {{
            margin-right: 10px;
            font-size: 1.2em;
        }}
        .url-section {{
            margin-top: 25px;
        }}
        .url-tabs {{
            display: flex;
            margin-bottom: 20px;
            border-bottom: 2px solid #dee2e6;
        }}
        .url-tab {{
            padding: 12px 20px;
            background: #f8f9fa;
            border: none;
            cursor: pointer;
            font-weight: bold;
            margin-right: 5px;
            border-radius: 6px 6px 0 0;
            transition: all 0.3s;
        }}
        .url-tab.active {{
            background: #3498db;
            color: white;
        }}
        .url-content {{
            display: none;
        }}
        .url-content.active {{
            display: block;
        }}
        .url-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        .url-table th,
        .url-table td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #dee2e6;
        }}
        .url-table th {{
            background-color: #f8f9fa;
            font-weight: bold;
            color: #2c3e50;
        }}
        .url-table tr:hover {{
            background-color: #f5f5f5;
        }}
        .status-200 {{
            color: #27ae60;
            font-weight: bold;
        }}
        .status-403 {{
            color: #f39c12;
            font-weight: bold;
        }}
        .status-error {{
            color: #e74c3c;
            font-weight: bold;
        }}
        .url-link {{
            color: #3498db;
            text-decoration: none;
            word-break: break-all;
        }}
        .url-link:hover {{
            text-decoration: underline;
        }}
        .stats-bar {{
            background: #ecf0f1;
            border-radius: 10px;
            padding: 15px;
            margin: 20px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .stat-item {{
            text-align: center;
        }}
        .stat-number {{
            font-size: 1.5em;
            font-weight: bold;
            color: #2c3e50;
        }}
        .stat-label {{
            color: #7f8c8d;
            font-size: 0.9em;
        }}
        .collapsible {{
            cursor: pointer;
            padding: 10px;
            background: #ecf0f1;
            border-radius: 5px;
            margin: 10px 0;
            user-select: none;
        }}
        .collapsible:hover {{
            background: #d5dbdb;
        }}
        .collapsible-content {{
            display: none;
            padding: 15px;
            background: white;
            border-radius: 5px;
            margin-top: 5px;
        }}
        .collapsible.active + .collapsible-content {{
            display: block;
        }}
    </style>
    <script>
        function showUrlTab(testId, tabType) {{
            // Hide all tabs for this test
            const tabs = document.querySelectorAll(`#${{testId}} .url-tab`);
            const contents = document.querySelectorAll(`#${{testId}} .url-content`);
            
            tabs.forEach(tab => tab.classList.remove('active'));
            contents.forEach(content => content.classList.remove('active'));
            
            // Show selected tab
            document.querySelector(`#${{testId}} .url-tab[onclick*="${{tabType}}"]`).classList.add('active');
            document.querySelector(`#${{testId}} .url-content-${{tabType}}`).classList.add('active');
        }}
        
        function toggleCollapsible(element) {{
            element.classList.toggle('active');
        }}
        
        // Initialize first tab as active for each test
        document.addEventListener('DOMContentLoaded', function() {{
            const testCases = document.querySelectorAll('.test-case');
            testCases.forEach(testCase => {{
                const testId = testCase.id;
                if (testId) {{
                    showUrlTab(testId, 'valid');
                }}
            }});
        }});
    </script>
</head>
<body>
    <div class="container">
        <h1>🚀 Enhanced AI Test Automation Report</h1>
        
        <div class="summary-grid">
            <div class="summary-card">
                <h3>{total_tests}</h3>
                <p>Total Tests</p>
            </div>
            <div class="summary-card">
                <h3>{passed_tests}</h3>
                <p>Tests Passed</p>
            </div>
            <div class="summary-card">
                <h3>{total_links}</h3>
                <p>Links Validated</p>
            </div>
            <div class="summary-card">
                <h3>{overall_success_rate:.1f}%</h3>
                <p>Success Rate</p>
            </div>
        </div>
        
        <div class="stats-bar">
            <div class="stat-item">
                <div class="stat-number" style="color: #27ae60;">{total_valid}</div>
                <div class="stat-label">Valid Links</div>
            </div>
            <div class="stat-item">
                <div class="stat-number" style="color: #f39c12;">{total_acceptable}</div>
                <div class="stat-label">Acceptable Failures</div>
            </div>
            <div class="stat-item">
                <div class="stat-number" style="color: #e74c3c;">{total_critical}</div>
                <div class="stat-label">Critical Failures</div>
            </div>
            <div class="stat-item">
                <div class="stat-number" style="color: #3498db;">{datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
                <div class="stat-label">Generated</div>
            </div>
        </div>
        
        <h2>📋 Detailed Test Case Results</h2>
"""

    # Add each test case
    for report in reports:
        test_id = report.get('test_case_id', 'Unknown')
        test_name = report.get('test_case_name', 'Unknown Test')
        test_description = report.get('test_description', 'No description available')
        test_priority = report.get('test_priority', 'Medium')
        validation_criteria = report.get('validation_criteria', [])
        validation_results = report.get('validation_results', {})
        overall_status = validation_results.get('overall_status', 'UNKNOWN')
        success_rate = validation_results.get('success_rate', '0%')
        criteria_met = validation_results.get('criteria_met', False)
        execution_timestamp = report.get('execution_timestamp', 'Unknown')
        
        # Format timestamp
        try:
            dt = datetime.fromisoformat(execution_timestamp.replace('Z', '+00:00'))
            formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            formatted_time = execution_timestamp
        
        priority_class = f"priority-{test_priority.lower()}"
        status_class = "status-pass" if overall_status == "PASS" else "status-fail"
        header_class = "test-header" if overall_status == "PASS" else "test-header failed"
        
        html_content += f"""
        <div class="test-case" id="{test_id}">
            <div class="{header_class}">
                <h3 style="margin: 0; color: white; border: none; padding: 0;">
                    {test_id}: {test_name}
                </h3>
            </div>
            <div class="test-content">
                <div class="test-meta">
                    <div class="meta-item">
                        <div class="meta-label">Description</div>
                        <div class="meta-value">{test_description}</div>
                    </div>
                    <div class="meta-item">
                        <div class="meta-label">Priority</div>
                        <div class="meta-value {priority_class}">{test_priority}</div>
                    </div>
                    <div class="meta-item">
                        <div class="meta-label">Status</div>
                        <div class="meta-value {status_class}">{overall_status}</div>
                    </div>
                    <div class="meta-item">
                        <div class="meta-label">Success Rate</div>
                        <div class="meta-value">{success_rate}</div>
                    </div>
                    <div class="meta-item">
                        <div class="meta-label">Execution Time</div>
                        <div class="meta-value">{formatted_time}</div>
                    </div>
                    <div class="meta-item">
                        <div class="meta-label">Links Validated</div>
                        <div class="meta-value">{report.get('total_links', 0)}</div>
                    </div>
                </div>
                
                <h4>✅ Validation Criteria</h4>
                <div class="criteria-list">
"""
        
        # Add validation criteria
        for i, criteria in enumerate(validation_criteria, 1):
            criteria_class = "criteria-item met" if criteria_met else "criteria-item not-met"
            icon = "✅" if criteria_met else "❌"
            html_content += f"""
                    <div class="{criteria_class}">
                        <span class="criteria-icon">{icon}</span>
                        <span>{i}. {criteria}</span>
                    </div>
"""
        
        html_content += """
                </div>
                
                <div class="url-section">
                    <h4>🔗 URL Validation Results</h4>
                    <div class="url-tabs">
"""
        
        # Add URL tabs
        valid_count = report.get('valid_links_count', 0)
        broken_count = report.get('broken_links_count', 0)
        critical_count = report.get('critical_failures_count', 0)
        acceptable_count = report.get('acceptable_failures_count', 0)
        
        html_content += f"""
                        <button class="url-tab active" onclick="showUrlTab('{test_id}', 'valid')">
                            Valid Links ({valid_count})
                        </button>
                        <button class="url-tab" onclick="showUrlTab('{test_id}', 'broken')">
                            All Failures ({broken_count})
                        </button>
                        <button class="url-tab" onclick="showUrlTab('{test_id}', 'critical')">
                            Critical ({critical_count})
                        </button>
                        <button class="url-tab" onclick="showUrlTab('{test_id}', 'acceptable')">
                            Acceptable ({acceptable_count})
                        </button>
                    </div>
"""
        
        # Add URL content sections
        valid_links = report.get('valid_links', [])
        broken_links = report.get('broken_links', [])
        critical_failures = report.get('critical_failures', [])
        acceptable_failures = report.get('acceptable_failures', [])
        
        # Valid links section
        html_content += f"""
                    <div class="url-content url-content-valid active">
                        <table class="url-table">
                            <thead>
                                <tr>
                                    <th>URL</th>
                                    <th>Link Text</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
"""
        
        for link in valid_links[:20]:  # Show first 20 for performance
            status_class = f"status-{link.get('status', 'unknown')}"
            html_content += f"""
                                <tr>
                                    <td><a href="{link.get('url', '')}" target="_blank" class="url-link">{link.get('url', '')}</a></td>
                                    <td>{link.get('text', '')[:50]}{'...' if len(link.get('text', '')) > 50 else ''}</td>
                                    <td class="{status_class}">{link.get('status', 'Unknown')}</td>
                                </tr>
"""
        
        if len(valid_links) > 20:
            html_content += f"""
                                <tr>
                                    <td colspan="3" style="text-align: center; font-style: italic; color: #7f8c8d;">
                                        ... and {len(valid_links) - 20} more valid links
                                    </td>
                                </tr>
"""
        
        html_content += """
                            </tbody>
                        </table>
                    </div>
"""
        
        # All failures section
        html_content += f"""
                    <div class="url-content url-content-broken">
                        <table class="url-table">
                            <thead>
                                <tr>
                                    <th>URL</th>
                                    <th>Link Text</th>
                                    <th>Status</th>
                                    <th>Type</th>
                                </tr>
                            </thead>
                            <tbody>
"""
        
        for link in broken_links:
            status_class = "status-error" if link.get('status') in [404, 500, 'ERROR'] else "status-403"
            failure_type = "Critical" if link.get('status') in [404, 500, 'ERROR'] else "Acceptable"
            html_content += f"""
                                <tr>
                                    <td class="url-link">{link.get('url', '')}</td>
                                    <td>{link.get('text', '')[:50]}{'...' if len(link.get('text', '')) > 50 else ''}</td>
                                    <td class="{status_class}">{link.get('status', 'Unknown')}</td>
                                    <td>{failure_type}</td>
                                </tr>
"""
        
        html_content += """
                            </tbody>
                        </table>
                    </div>
"""
        
        # Critical failures section
        html_content += f"""
                    <div class="url-content url-content-critical">
"""
        if critical_failures:
            html_content += """
                        <table class="url-table">
                            <thead>
                                <tr>
                                    <th>URL</th>
                                    <th>Link Text</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
"""
            for link in critical_failures:
                html_content += f"""
                                <tr>
                                    <td class="url-link">{link.get('url', '')}</td>
                                    <td>{link.get('text', '')}</td>
                                    <td class="status-error">{link.get('status', 'Unknown')}</td>
                                </tr>
"""
            html_content += """
                            </tbody>
                        </table>
"""
        else:
            html_content += """
                        <div style="text-align: center; padding: 40px; color: #27ae60;">
                            <h3>🎉 No Critical Failures Found!</h3>
                            <p>All links returned acceptable status codes.</p>
                        </div>
"""
        
        html_content += """
                    </div>
"""
        
        # Acceptable failures section
        html_content += f"""
                    <div class="url-content url-content-acceptable">
"""
        if acceptable_failures:
            html_content += """
                        <table class="url-table">
                            <thead>
                                <tr>
                                    <th>URL</th>
                                    <th>Link Text</th>
                                    <th>Status</th>
                                    <th>Reason</th>
                                </tr>
                            </thead>
                            <tbody>
"""
            for link in acceptable_failures:
                reason = "Forbidden but acceptable" if link.get('status') == 403 else "Acceptable failure"
                html_content += f"""
                                <tr>
                                    <td class="url-link">{link.get('url', '')}</td>
                                    <td>{link.get('text', '')}</td>
                                    <td class="status-403">{link.get('status', 'Unknown')}</td>
                                    <td>{reason}</td>
                                </tr>
"""
            html_content += """
                            </tbody>
                        </table>
"""
        else:
            html_content += """
                        <div style="text-align: center; padding: 40px; color: #3498db;">
                            <h3>ℹ️ No Acceptable Failures</h3>
                            <p>All links either passed or had critical failures.</p>
                        </div>
"""
        
        html_content += """
                    </div>
                </div>
            </div>
        </div>
"""
    
    html_content += """
        <div style="text-align: center; margin-top: 40px; padding: 20px; background: #ecf0f1; border-radius: 8px;">
            <p style="margin: 0; color: #7f8c8d;">
                Report generated on """ + datetime.now().strftime('%Y-%m-%d at %H:%M:%S') + """<br>
                Enhanced AI Test Automation Framework
            </p>
        </div>
    </div>
</body>
</html>"""
    
    # Save the enhanced report
    output_file = "reports/enhanced_complete_automation_report.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Enhanced HTML report generated: {output_file}")
    return output_file

if __name__ == "__main__":
    generate_enhanced_html_report()