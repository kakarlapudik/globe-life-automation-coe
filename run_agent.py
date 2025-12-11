#!/usr/bin/env python
"""
Main entry point to run the AI Test Automation Agent
"""

import sys
import argparse
from pathlib import Path
from ai_test_automation_agent import AITestAutomationAgent


def main():
    """Main function to run the agent"""
    parser = argparse.ArgumentParser(
        description="AI Test Automation Agent - Generate tests from requirements"
    )
    parser.add_argument(
        "requirements_file",
        type=str,
        help="Path to requirements document file"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="./output",
        help="Output directory for generated artifacts (default: ./output)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Read requirements file
    requirements_path = Path(args.requirements_file)
    if not requirements_path.exists():
        print(f"❌ Error: Requirements file not found: {args.requirements_file}")
        sys.exit(1)
    
    with open(requirements_path, "r", encoding="utf-8") as f:
        requirements_text = f.read()
    
    if not requirements_text.strip():
        print("❌ Error: Requirements file is empty")
        sys.exit(1)
    
    # Initialize and run agent
    print(f"\n📂 Reading requirements from: {args.requirements_file}")
    print(f"📁 Output directory: {args.output}\n")
    
    agent = AITestAutomationAgent()
    
    try:
        results = agent.process_requirements(requirements_text)
        agent.save_results(output_dir=args.output)
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 SUMMARY")
        print("=" * 60)
        print(f"Use Cases Extracted: {results['summary']['total_use_cases']}")
        print(f"Requirements Extracted: {results['summary']['total_requirements']}")
        print(f"Test Cases Generated: {results['summary']['total_test_cases']}")
        print(f"Automation Candidates: {results['summary']['automation_candidates']}")
        print(f"Scripts Generated: {results['summary']['scripts_generated']}")
        print("=" * 60)
        
        print("\n✅ Success! Check the output directory for generated artifacts.")
        print(f"\n💡 Next steps:")
        print(f"   1. Review generated test cases in: {args.output}/test_automation_report.json")
        print(f"   2. Customize test scripts in: {args.output}/generated_tests/")
        print(f"   3. Run tests with: pytest {args.output}/generated_tests/")
        
    except Exception as e:
        print(f"\n❌ Error processing requirements: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
