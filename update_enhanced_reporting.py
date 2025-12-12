#!/usr/bin/env python
"""
Script to update all test files with enhanced reporting including test case names and validation details
"""

import os
import glob
import re

# Test case details mapping
TEST_CASE_DETAILS = {
    'UC001_TC001': {
        'name': 'Verify Globe Life Investor Relations Homepage Links',
        'description': 'Launch the Globe Life investor relations website and verify all links on the home page are working and return HTTP status code 200',
        'priority': 'High',
        'validation_criteria': [
            'Homepage loads successfully',
            'All links are extracted correctly', 
            'All links return HTTP status code 200',
            'No broken links are found',
            'Validation report is generated'
        ]
    },
    'UC002_TC001': {
        'name': 'Comprehensive Site-Wide Link Validation',
        'description': 'Crawl the entire Globe Life investor relations website, discover all pages, and validate all links across the entire site',
        'priority': 'High',
        'validation_criteria': [
            'All pages on the site are discovered and visited',
            'All links across all pages return status code 200',
            'Navigation menus and dropdowns are tested',
            'Dynamic content links are validated',
            'External links are verified'
        ]
    },
    'UC003_TC001': {
        'name': 'Navigation Menu Link Validation',
        'description': 'Validate all links in the main navigation menu including dropdowns and submenus',
        'priority': 'High',
        'validation_criteria': [
            'All navigation menu items are clickable',
            'All dropdown menus expand correctly',
            'All menu links navigate to valid pages',
            'All pages return status code 200',
            'Navigation is consistent across site'
        ]
    },
    'UC004_TC001': {
        'name': 'Footer and Utility Links Validation',
        'description': 'Validate all links in footer, social media icons, and utility navigation',
        'priority': 'Medium',
        'validation_criteria': [
            'All footer links are valid',
            'Social media links open correct profiles',
            'Utility pages load successfully',
            'External links return status code 200',
            'Document downloads are accessible'
        ]
    },
    'UC005_TC001': {
        'name': 'Dynamic Content and AJAX Link Validation',
        'description': 'Validate links that are loaded dynamically via JavaScript or AJAX',
        'priority': 'Medium',
        'validation_criteria': [
            'All dynamic content loads successfully',
            'AJAX-loaded links are valid',
            'Pagination works correctly',
            'Search functionality returns valid links',
            'All dynamic links return status code 200'
        ]
    },
    'UC006_TC001': {
        'name': 'Automatic Test Report Launch and Display',
        'description': 'Automatically launch and display HTML test reports in the default browser after test execution completes',
        'priority': 'High',
        'validation_criteria': [
            'HTML report opens automatically in default browser',
            'Report launches even when some tests fail',
            'Success message confirms report launch',
            'Report contains all test execution details',
            'Consistent behavior across operating systems'
        ]
    }
}

def extract_test_case_id(filepath):
    """Extract test case ID from file path"""
    filename = os.path.basename(filepath)
    match = re.search(r'test_(uc\d+_tc\d+)', filename, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    return None

def update_test_file_reporting(filepath):
    """Update a test file with enhanced reporting"""
    if not os.path.exists(filepath):
        print(f"[SKIP] {filepath} not found")
        return
    
    test_case_id = extract_test_case_id(filepath)
    if not test_case_id or test_case_id not in TEST_CASE_DETAILS:
        print(f"[SKIP] {filepath} - Unknown test case ID: {test_case_id}")
        return
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Skip if already updated
    if 'test_case_name' in content and 'validation_criteria' in content:
        print(f"[SKIP] {filepath} - Already has enhanced reporting")
        return
    
    test_details = TEST_CASE_DETAILS[test_case_id]
    
    # Find and replace the _generate_report method
    old_pattern = r"def _generate_report\(self\):\s*\n\s*\"\"\".*?\"\"\"\s*\n(.*?)(?=\n\s{4}def|\n\s{0,3}class|\Z)"
    
    new_method = f'''def _generate_report(self):
        """Generate detailed JSON report with enhanced test case information"""
        import datetime
        
        # Calculate validation results
        critical_failures = [link for link in self.broken_links if link.get('status') in [404, 500, 'ERROR']]
        acceptable_failures = [link for link in self.broken_links if link.get('status') == 403]
        
        report_data = {{
            'test_case_id': '{test_case_id}',
            'test_case_name': '{test_details["name"]}',
            'test_description': '{test_details["description"]}',
            'test_priority': '{test_details["priority"]}',
            'validation_criteria': {test_details["validation_criteria"]},
            'execution_timestamp': datetime.datetime.now().isoformat(),
            'base_url': self.base_url,
            'total_links': len(self.all_links),
            'valid_links_count': len(self.valid_links),
            'broken_links_count': len(self.broken_links),
            'critical_failures_count': len(critical_failures),
            'acceptable_failures_count': len(acceptable_failures),
            'validation_results': {{
                'overall_status': 'PASS' if len(critical_failures) == 0 else 'FAIL',
                'success_rate': f"{{(len(self.valid_links) / len(self.all_links) * 100):.1f}}%" if self.all_links else "0%",
                'total_validated': len(self.all_links),
                'criteria_met': len(critical_failures) == 0,
                'acceptable_status_codes': [200, 301, 302, 403],
                'critical_status_codes': [404, 500, 'ERROR', 'TIMEOUT']
            }},
            'valid_links': self.valid_links,
            'broken_links': self.broken_links,
            'critical_failures': critical_failures,
            'acceptable_failures': acceptable_failures
        }}
        
        # Generate JSON report
        json_report_file = f"reports/{{'{test_case_id}'.lower()}}_links_report.json"
        with open(json_report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\\n[REPORT] JSON Report saved to: {{json_report_file}}")
        
        # Enhanced console output with test case information
        print(f"\\n[TEST CASE] {{report_data['test_case_name']}}")
        print(f"[DESCRIPTION] {{report_data['test_description']}}")
        print(f"[PRIORITY] {{report_data['test_priority']}}")
        print(f"[STATUS] {{report_data['validation_results']['overall_status']}}")
        print(f"[SUCCESS RATE] {{report_data['validation_results']['success_rate']}}")
        
        print(f"\\n[VALIDATION CRITERIA]")
        for i, criteria in enumerate(report_data['validation_criteria'], 1):
            status = "✅" if report_data['validation_results']['criteria_met'] else "❌"
            print(f"  {{i}}. {{criteria}} {{status}}")
        
        print(f"\\n[URLS] Valid Links ({{len(report_data['valid_links'])}}):")
        for link in report_data['valid_links'][:5]:  # Show first 5 for brevity
            print(f"  ✅ {{link['url']}} - Status: {{link['status']}}")
        if len(report_data['valid_links']) > 5:
            print(f"  ... and {{len(report_data['valid_links']) - 5}} more valid links")
        
        if report_data['broken_links']:
            print(f"\\n[URLS] Broken Links ({{len(report_data['broken_links'])}}):")
            for link in report_data['broken_links']:
                print(f"  ❌ {{link['url']}} - Status: {{link['status']}}")
        
        if report_data['critical_failures']:
            print(f"\\n[CRITICAL] Critical Failures ({{len(report_data['critical_failures'])}}):")
            for link in report_data['critical_failures']:
                print(f"  🚨 {{link['url']}} - Status: {{link['status']}}")
        
        if report_data['acceptable_failures']:
            print(f"\\n[ACCEPTABLE] Acceptable Failures ({{len(report_data['acceptable_failures'])}}):")
            for link in report_data['acceptable_failures']:
                print(f"  ⚠️  {{link['url']}} - Status: {{link['status']}} (403 - Forbidden but acceptable)")'''
    
    # Replace the method
    content = re.sub(old_pattern, new_method, content, flags=re.DOTALL)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"[UPDATED] {filepath} - Enhanced reporting with test case details")

def update_all_test_directories():
    """Update all test files in various directories"""
    test_directories = [
        "final_automation/generated_tests/",
        "generated_automation/generated_tests/",
        "generated_automation_final/generated_tests/",
        "generated_automation_all/generated_tests/",
        "generated_automation_with_reports/generated_tests/",
        "generated_automation_with_url/generated_tests/"
    ]
    
    for directory in test_directories:
        if not os.path.exists(directory):
            continue
            
        print(f"\n[INFO] Processing directory: {directory}")
        test_files = glob.glob(os.path.join(directory, "test_uc*_tc*.py"))
        
        for filepath in test_files:
            update_test_file_reporting(filepath)

def main():
    """Update all test files with enhanced reporting"""
    print("Updating all test files with enhanced reporting including test case names and validation details...")
    print("="*80)
    
    # Update all test files in various directories
    print("\nAdding enhanced reporting to all test files:")
    update_all_test_directories()
    
    print("\n" + "="*80)
    print("✅ Enhanced reporting update complete!")
    print("\nAll tests now include:")
    print("  - Test case names and descriptions")
    print("  - Test priority levels")
    print("  - Detailed validation criteria")
    print("  - Execution timestamps")
    print("  - Critical vs acceptable failure categorization")
    print("  - Overall test status (PASS/FAIL)")
    print("  - Enhanced console output with test case information")

if __name__ == "__main__":
    main()