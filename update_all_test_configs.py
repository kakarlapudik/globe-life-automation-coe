#!/usr/bin/env python
"""
Script to update all existing test files to include HTML report generation by default
"""

import os
import glob

# HTML report generation method to add to all test files
HTML_REPORT_METHOD = '''
    def _generate_html_report(self, report_data, filename):
        """Generate detailed HTML report with link validation results"""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Link Validation Report - {report_data.get('test', 'Test Report')}</title>
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
                    <div class="summary-number">{report_data.get('summary', {}).get('total_links', 0)}</div>
                    <div class="summary-label">Total Links</div>
                </div>
                <div class="summary-item">
                    <div class="summary-number" style="color: #28a745;">{report_data.get('summary', {}).get('valid_links', 0)}</div>
                    <div class="summary-label">Valid Links</div>
                </div>
                <div class="summary-item">
                    <div class="summary-number" style="color: #dc3545;">{report_data.get('summary', {}).get('broken_links', 0)}</div>
                    <div class="summary-label">Broken Links</div>
                </div>
                <div class="summary-item">
                    <div class="summary-number" style="color: #007bff;">{((report_data.get('summary', {}).get('valid_links', 0) / max(report_data.get('summary', {}).get('total_links', 1), 1)) * 100):.1f}%</div>
                    <div class="summary-label">Success Rate</div>
                </div>
            </div>
            <p><strong>Base URL:</strong> {report_data.get('url', 'N/A')}</p>
            <p><strong>Test:</strong> {report_data.get('test', 'Link Validation')}</p>
            <p><strong>Timestamp:</strong> {report_data.get('timestamp', 'N/A')}</p>
        </div>
        
        <h2>🔍 Link Details</h2>
        
        <div class="filter-buttons">
            <button class="filter-btn active" onclick="filterTable('all')">All Links ({report_data.get('summary', {}).get('total_links', 0)})</button>
            <button class="filter-btn" onclick="filterTable('valid')">Valid Links ({report_data.get('summary', {}).get('valid_links', 0)})</button>
            <button class="filter-btn" onclick="filterTable('broken')">Broken Links ({report_data.get('summary', {}).get('broken_links', 0)})</button>
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
        
        # Add all links
        for link in report_data.get('all_links', []):
            is_valid = link.get('valid', False) or (isinstance(link.get('status'), int) and link.get('status') < 400)
            row_class = "valid-link" if is_valid else "broken-link"
            status_class = "status-ok" if is_valid else "status-error"
            result_icon = "✅ Valid" if is_valid else "❌ Broken"
            
            html_content += f"""
                <tr class="{row_class}">
                    <td class="url-cell">{"<a href='" + link.get('url', '') + "' target='_blank'>" + link.get('url', '') + "</a>" if is_valid else link.get('url', '')}</td>
                    <td class="text-cell">{link.get('text', '')}</td>
                    <td class="{status_class}">{link.get('status', 'N/A')}</td>
                    <td class="{status_class}">{result_icon}</td>
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

def update_homepage_links_test():
    """Update the homepage links test to include HTML report generation"""
    filepath = "generated_tests/test_homepage_links.py"
    
    if not os.path.exists(filepath):
        print(f"[SKIP] {filepath} not found")
        return
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already updated
    if '_generate_html_report' in content:
        print(f"[SKIP] {filepath} already has HTML report generation")
        return
    
    # Update the JSON report generation to also create HTML
    old_json_save = '''        with open("reports/homepage_links_report.json", "w") as f:
            json.dump(report, f, indent=2)'''
    
    new_json_save = '''        # Save JSON report
        with open("reports/homepage_links_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        # Generate HTML report
        html_filename = "reports/homepage_links_report.html"
        self._generate_html_report(report, html_filename)'''
    
    if old_json_save in content:
        content = content.replace(old_json_save, new_json_save)
        
        # Update the print statement
        old_print = '''        print(f"\\n📄 Report saved to: reports/homepage_links_report.json")'''
        new_print = '''        print(f"\\n📄 JSON Report saved to: reports/homepage_links_report.json")
        print(f"📄 HTML Report saved to: {html_filename}")'''
        
        content = content.replace(old_print, new_print)
        
        # Add the HTML report method before teardown_method
        content = content.replace('    def teardown_method(self):', HTML_REPORT_METHOD + '\n    def teardown_method(self):')
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"[UPDATED] {filepath}")
    else:
        print(f"[SKIP] {filepath} - pattern not found")

def update_other_test_files():
    """Update other test files in generated_tests folder"""
    test_files = [
        "generated_tests/test_footer_links.py",
        "generated_tests/test_navigation_menu.py", 
        "generated_tests/test_sitewide_crawl.py",
        "generated_tests/test_dynamic_content.py"
    ]
    
    for filepath in test_files:
        if not os.path.exists(filepath):
            print(f"[SKIP] {filepath} not found")
            continue
            
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if already updated
        if '_generate_html_report' in content:
            print(f"[SKIP] {filepath} already has HTML report generation")
            continue
        
        # Look for JSON report generation patterns and update them
        if 'json.dump(' in content and 'reports/' in content:
            # Add HTML report method before teardown_method if it exists
            if 'def teardown_method(self):' in content:
                content = content.replace('    def teardown_method(self):', HTML_REPORT_METHOD + '\n    def teardown_method(self):')
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"[UPDATED] {filepath} - Added HTML report method")
            else:
                print(f"[SKIP] {filepath} - No teardown_method found")
        else:
            print(f"[SKIP] {filepath} - No JSON report generation found")

def main():
    """Update all test configurations"""
    print("Updating test configurations to include HTML report generation by default...")
    print("="*70)
    
    # Update AI agent template (already done above)
    print("[INFO] AI agent template updated with HTML report generation")
    
    # Update existing test files
    print("\nUpdating existing test files:")
    update_homepage_links_test()
    update_other_test_files()
    
    print("\n" + "="*70)
    print("✅ Configuration update complete!")
    print("\nFuture generated tests will include:")
    print("  - JSON reports (existing functionality)")
    print("  - Interactive HTML reports with link details")
    print("  - Search and filter capabilities")
    print("  - Visual status indicators")
    print("  - Clickable links for validation")

if __name__ == "__main__":
    main()