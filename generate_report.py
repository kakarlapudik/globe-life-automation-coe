#!/usr/bin/env python
"""
Simple script to generate enhanced HTML report
Can be run independently or as part of automation workflow
"""

import sys
import os

# Add current directory to path to import the report generator
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from generate_enhanced_html_report import generate_enhanced_html_report
    
    print("Generating Enhanced HTML Report...")
    output_file = generate_enhanced_html_report()
    
    if output_file and os.path.exists(output_file):
        print(f"Enhanced report generated successfully!")
        print(f"Report location: {output_file}")
        
        # Optionally open the report
        if len(sys.argv) > 1 and sys.argv[1] == "--open":
            try:
                if os.name == 'nt':  # Windows
                    os.system(f"start {output_file}")
                else:  # Linux/Mac
                    os.system(f"open {output_file}")
                print("Opening report in browser...")
            except Exception as e:
                print(f"Could not open report automatically: {e}")
    else:
        print("Failed to generate enhanced report")
        sys.exit(1)
        
except ImportError as e:
    print(f"Error importing report generator: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Error generating report: {e}")
    sys.exit(1)