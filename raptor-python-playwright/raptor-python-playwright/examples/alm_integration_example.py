"""
Example usage of ALM Integration

This example demonstrates how to use the ALM integration to:
- Authenticate with ALM
- Publish test results
- Update test status
- Upload screenshots
"""

import asyncio
from datetime import datetime
from pathlib import Path

from raptor.integrations.alm_integration import (
    ALMIntegration,
    ALMConfig,
    ALMTestStatus
)
from raptor.utils.logger import get_logger


logger = get_logger(__name__)


async def main():
    """Example ALM integration workflow."""
    
    # Configure ALM connection
    alm_config = ALMConfig(
        server_url="http://alm-server:8080/qcbin",
        username="your_username",
        password="your_password",
        domain="DEFAULT",
        project="MY_PROJECT",
        verify_ssl=True
    )
    
    # Example 1: Using context manager (recommended)
    print("Example 1: Using ALM with context manager")
    print("-" * 50)
    
    try:
        with ALMIntegration(alm_config) as alm:
            # Publish a test result
            result = alm.publish_test_result(
                test_id="TEST-001",
                test_set_id="SET-001",
                status=ALMTestStatus.PASSED,
                execution_time=15.5,
                comments="Test executed successfully",
                tester_name="Automation"
            )
            
            print(f"Published test result: {result}")
            
            # Upload a screenshot (if exists)
            screenshot_path = "reports/screenshot.png"
            if Path(screenshot_path).exists():
                attachment = alm.upload_attachment(
                    run_id="RUN-001",
                    file_path=screenshot_path,
                    description="Test execution screenshot"
                )
                print(f"Uploaded screenshot: {attachment}")
    
    except Exception as e:
        logger.error(f"ALM integration error: {str(e)}")
    
    # Example 2: Manual authentication and logout
    print("\nExample 2: Manual authentication")
    print("-" * 50)
    
    alm = ALMIntegration(alm_config)
    
    try:
        # Authenticate
        if alm.authenticate():
            print("Successfully authenticated with ALM")
            
            # Update test status
            update_result = alm.update_test_status(
                run_id="RUN-001",
                status=ALMTestStatus.FAILED,
                comments="Test failed due to timeout"
            )
            print(f"Updated test status: {update_result}")
            
            # Link test to requirement
            link_result = alm.link_to_requirement(
                test_id="TEST-001",
                requirement_id="REQ-001"
            )
            print(f"Linked to requirement: {link_result}")
            
    finally:
        # Always logout
        alm.logout()
        print("Logged out from ALM")
    
    # Example 3: Batch upload screenshots
    print("\nExample 3: Batch upload screenshots")
    print("-" * 50)
    
    with ALMIntegration(alm_config) as alm:
        screenshots = [
            "reports/screenshot1.png",
            "reports/screenshot2.png",
            "reports/screenshot3.png"
        ]
        
        # Filter existing files
        existing_screenshots = [
            path for path in screenshots
            if Path(path).exists()
        ]
        
        if existing_screenshots:
            results = alm.upload_multiple_attachments(
                run_id="RUN-001",
                file_paths=existing_screenshots,
                description="Test execution screenshots"
            )
            print(f"Uploaded {len(results)} screenshots")
        else:
            print("No screenshots found to upload")


if __name__ == "__main__":
    asyncio.run(main())
