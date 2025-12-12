#!/usr/bin/env python
"""
Script to update all existing test files to use simple JSON reporting with URL information
"""

import os
import glob

def remove_html_generation_from_test(filepath):
    """Remove HTML generation from a test file and keep only JSON with URL console output"""
    if not os.path.exists(filepath):
        print(f"[SKIP] {filepath} not found")
        return
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove HTML generation method if it exists
    if '_generate_html_report' in content:
        # Find and remove the entire HTML generation method
        lines = content.split('\n')
        new_lines = []
        skip_method = False
        indent_level = 0
        
        for line in lines:
            if 'def _generate_html_report' in line:
                skip_method = True
                indent_level = len(line) - len(line.lstrip())
                continue
            
            if skip_method:
                current_indent = len(line) - len(line.lstrip()) if line.strip() else float('inf')
                # If we hit a line with same or less indentation (and it's not empty), we're done with the method
                if line.strip() and current_indent <= indent_level:
                    skip_method = False
                    new_lines.append(line)
                # Skip lines that are part of the HTML method
                continue
            
            new_lines.append(line)
        
        content = '\n'.join(new_lines)
    
    # Remove HTML report generation calls
    html_patterns = [
        r'html_report_file = f"reports/.*\.html"',
        r'self\._generate_html_report\(.*\)',
        r'html_filename = "reports/.*\.html"',
        r'print\(f".*HTML Report saved to:.*"\)',
        r'# Generate HTML report.*\n',
        r'# Save HTML report.*\n'
    ]
    
    import re
    for pattern in html_patterns:
        content = re.sub(pattern, '', content, flags=re.MULTILINE)
    
    # Add simple URL console output if not present
    if 'print(f"\\n[URLS] Valid Links' not in content and 'print(f"\\\\n[URLS] Valid Links' not in content:
        # Find the JSON report generation and add console output after it
        json_pattern = r'(with open\([^)]*\.json[^)]*\) as f:\s*\n\s*json\.dump\([^)]*\))'
        
        def add_console_output(match):
            return match.group(1) + '''
        
        # Simple console output for URLs
        print(f"\\n[URLS] Valid Links ({len(report_data.get('valid_links', []))}):")
        for link in report_data.get('valid_links', []):
            print(f"  ✅ {link['url']} - Status: {link['status']}")
        
        if report_data.get('broken_links', []):
            print(f"\\n[URLS] Broken Links ({len(report_data.get('broken_links', []))}):")
            for link in report_data.get('broken_links', []):
                print(f"  ❌ {link['url']} - Status: {link['status']}")'''
        
        content = re.sub(json_pattern, add_console_output, content, flags=re.MULTILINE | re.DOTALL)
    
    # Clean up extra blank lines
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"[UPDATED] {filepath} - Removed HTML generation, kept JSON with URL console output")

def update_all_test_directories():
    """Update all test files in various directories"""
    test_directories = [
        "generated_tests/",
        "generated_automation/generated_tests/",
        "generated_automation_final/generated_tests/",
        "final_automation/generated_tests/",
        "generated_automation_all/generated_tests/",
        "generated_automation_with_reports/generated_tests/",
        "generated_automation_with_url/generated_tests/",
        "generated_comprehensive_tests/"
    ]
    
    for directory in test_directories:
        if not os.path.exists(directory):
            continue
            
        print(f"\n[INFO] Processing directory: {directory}")
        test_files = glob.glob(os.path.join(directory, "test_*.py"))
        
        for filepath in test_files:
            remove_html_generation_from_test(filepath)

def main():
    """Update all test configurations to use simple JSON reporting"""
    print("Updating test configurations to use simple JSON reporting with URL information...")
    print("="*70)
    
    # Update all test files in various directories
    print("\nRemoving HTML generation from all test files:")
    update_all_test_directories()
    
    print("\n" + "="*70)
    print("✅ Configuration update complete!")
    print("\nAll tests now use:")
    print("  - Simple JSON reports with URL information")
    print("  - Console output showing valid/broken links with URLs and status codes")
    print("  - No fancy HTML generation")
    print("  - Faster execution without HTML processing overhead")

if __name__ == "__main__":
    main()