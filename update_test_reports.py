#!/usr/bin/env python
"""
Script to update all test files with HTML report generation
"""

import os
import glob

# HTML report generation method to add to all test files
html_report_method = '''
    def _generate_html_report(self, report_data, filename):
        """Generate detailed HTML report with link validation results"""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Link Validation Report - {report_data['test_case']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; text-align: center; border-bottom: 3px solid #007bff; padding-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; }}
        .summary {{ background-color: #e9f4ff; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }}
        .summary-item {{ text-align: center; }}
        .summary-number {{ font-size: 2em; font-weight: bold; color: #007bff; }}
        .summary-label {{ color: #666; font-size: 0.9em; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #f8f9fa; font-weight: bold; color: #333; }}
        tr:hover {{ background-color: #f5f5f5; }}
        .status-ok {{ color: #28a745; font-weight: bold; }}
        .status-error {{ color: #dc3545; font-weight: bold; }}
        .url-cell {{ max-width: 400px; word-break: break-all; }}
        .text-cell {{ max-width: 300px; }}
        .filter-buttons {{ margin: 20px 0; }}
        .filter-btn {{ padding: 8px 16px; margin: 5px; border: none; border-radius: 4px; cursor: pointer; }}
        .filter-btn.active {{ background-color: #007bff; color: white; }}
        .filter-btn:not(.active) {{ background-color: #e9ecef; color: #333; }}
        .search-box {{ width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 4px; }}
    </style>
    <script>
        function filterTable(status) {{
            const rows = document.querySelectorAll('#linksTable tbody tr');
            const buttons = document.querySelectorAll('.filter-btn');
            
            buttons.forEach(btn => btn.classList.remove('active'));
            document.querySelector(`[onclick="filterTable('${{status}}')"]`).classList.add('active');
            
            rows.forEach(row => {{
                if (status === 'all') {{
                    row.style.display = '';
                }} else if (status === 'valid') {{
                    row.style.display = row.classList.contains('valid-link') ? '' : 'none';
                }} else if (status === 'broken') {{
                    row.style.display = row.classList.contains('broken-link') ? '' : 'none';
                }}
            }});
        }}
        
        function searchLinks() {{
            const searchTerm = document.getElementById('searchBox').value.toLowerCase();
            const rows = document.querySelectorAll('#linksTable tbody tr');
            
            rows.forEach(row => {{
                const url = row.cells[0].textContent.toLowerCase();
                const text = row.cells[1].textContent.toLowerCase();
                if (url.includes(searchTerm) || text.includes(searchTerm)) {{
                    row.style.display = '';
                }} else {{
                    row.style.display = 'none';
                }}
            }});
        }}
    </script>
</head>
<body>
    <div class="container">
        <h1>🔗 Link Validation Report</h1>
        
        <div class="summary">
            <h2>📊 Summary</h2>
            <div class="summary-grid">
                <div class="summary-item">
                    <div class="summary-number">{report_data['total_links']}</div>
                    <div class="summary-label">Total Links</div>
                </div>
                <div class="summary-item">
                    <div class="summary-number" style="color: #28a745;">{report_data['valid_links_count']}</div>
                    <div class="summary-label">Valid Links</div>
                </div>
                <div class="summary-item">
                    <div class="summary-number" style="color: #dc3545;">{report_data['broken_links_count']}</div>
                    <div class="summary-label">Broken Links</div>
                </div>
                <div class="summary-item">
                    <div class="summary-number" style="color: #007bff;">{report_data['summary']['success_rate']}</div>
                    <div class="summary-label">Success Rate</div>
                </div>
            </div>
            <p><strong>Base URL:</strong> {report_data['base_url']}</p>
            <p><strong>Test Case:</strong> {report_data['test_case']}</p>
        </div>
        
        <h2>🔍 Link Details</h2>
        
        <div class="filter-buttons">
            <button class="filter-btn active" onclick="filterTable('all')">All Links ({report_data['total_links']})</button>
            <button class="filter-btn" onclick="filterTable('valid')">Valid Links ({report_data['valid_links_count']})</button>
            <button class="filter-btn" onclick="filterTable('broken')">Broken Links ({report_data['broken_links_count']})</button>
        </div>
        
        <input type="text" id="searchBox" class="search-box" placeholder="Search links by URL or text..." onkeyup="searchLinks()">
        
        <table id="linksTable">
            <thead>
                <tr>
                    <th>URL</th>
                    <th>Link Text</th>
                    <th>Status</th>
                    <th>Result</th>
                </tr>
            </thead>
            <tbody>
"""
        
        # Add valid links
        for link in report_data['valid_links']:
            html_content += f"""
                <tr class="valid-link">
                    <td class="url-cell"><a href="{link['url']}" target="_blank">{link['url']}</a></td>
                    <td class="text-cell">{link['text']}</td>
                    <td class="status-ok">{link['status']}</td>
                    <td class="status-ok">✅ Valid</td>
                </tr>
"""
        
        # Add broken links
        for link in report_data['broken_links']:
            html_content += f"""
                <tr class="broken-link">
                    <td class="url-cell">{link['url']}</td>
                    <td class="text-cell">{link['text']}</td>
                    <td class="status-error">{link['status']}</td>
                    <td class="status-error">❌ Broken</td>
                </tr>
"""
        
        html_content += """
            </tbody>
        </table>
    </div>
</body>
</html>
"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
'''

def update_test_file(filepath):
    """Update a single test file with HTML report generation"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already updated
    if '_generate_html_report' in content:
        print(f"[SKIP] {filepath} already has HTML report generation")
        return
    
    # Update the _generate_report method
    old_generate_report = '''    def _generate_report(self):
        """Generate detailed JSON report"""
        report_data = {
            'test_case': 'UC001_TC001',
            'base_url': self.base_url,
            'total_links': len(self.all_links),
            'valid_links_count': len(self.valid_links),
            'broken_links_count': len(self.broken_links),
            'valid_links': self.valid_links,
            'broken_links': self.broken_links,
            'summary': {
                'success_rate': f"{(len(self.valid_links) / len(self.all_links) * 100):.1f}%" if self.all_links else "0%",
                'total_validated': len(self.all_links)
            }
        }
        
        report_file = f"reports/{'UC001_TC001'.lower()}_links_report.json"
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\\n[REPORT] Report saved to: {report_file}")'''
    
    # Extract test case ID from filename
    test_case_id = os.path.basename(filepath).replace('test_', '').replace('.py', '').upper()
    
    new_generate_report = f'''    def _generate_report(self):
        """Generate detailed JSON and HTML reports"""
        report_data = {{
            'test_case': '{test_case_id}',
            'base_url': self.base_url,
            'total_links': len(self.all_links),
            'valid_links_count': len(self.valid_links),
            'broken_links_count': len(self.broken_links),
            'valid_links': self.valid_links,
            'broken_links': self.broken_links,
            'summary': {{
                'success_rate': f"{{(len(self.valid_links) / len(self.all_links) * 100):.1f}}%" if self.all_links else "0%",
                'total_validated': len(self.all_links)
            }}
        }}
        
        # Generate JSON report
        json_report_file = f"reports/{{'{test_case_id}'.lower()}}_links_report.json"
        with open(json_report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        # Generate HTML report with link details
        html_report_file = f"reports/{{'{test_case_id}'.lower()}}_links_report.html"
        self._generate_html_report(report_data, html_report_file)
        
        print(f"\\n[REPORT] JSON Report saved to: {{json_report_file}}")
        print(f"[REPORT] HTML Report saved to: {{html_report_file}}")'''
    
    # Replace the method and add HTML generation method
    if old_generate_report in content:
        content = content.replace(old_generate_report, new_generate_report)
        # Add the HTML report method before the teardown_method
        content = content.replace('    def teardown_method(self):', html_report_method + '\n    def teardown_method(self):')
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[UPDATED] {filepath}")
    else:
        print(f"[SKIP] {filepath} - pattern not found")

def main():
    """Update all test files in final_automation/generated_tests/"""
    test_files = glob.glob('final_automation/generated_tests/test_*.py')
    
    print(f"Found {len(test_files)} test files to update:")
    for filepath in test_files:
        print(f"  - {filepath}")
    
    print("\nUpdating test files...")
    for filepath in test_files:
        update_test_file(filepath)
    
    print("\nUpdate complete!")

if __name__ == "__main__":
    main()