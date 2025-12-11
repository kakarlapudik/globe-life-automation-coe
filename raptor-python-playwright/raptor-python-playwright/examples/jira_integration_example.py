"""
Example usage of JIRA Integration

This example demonstrates how to use the JIRA integration to:
- Create issues and defects
- Link issues
- Add comments
- Update status
- Upload attachments
"""

import asyncio
from datetime import datetime
from pathlib import Path

from raptor.integrations.jira_integration import (
    JIRAIntegration,
    JIRAConfig,
    JIRAIssueType,
    JIRAPriority
)
from raptor.utils.logger import get_logger


logger = get_logger(__name__)


async def main():
    """Example JIRA integration workflow."""
    
    # Configure JIRA connection
    jira_config = JIRAConfig(
        server_url="https://jira.company.com",
        username="your_email@company.com",
        api_token="your_api_token",
        project_key="TEST",
        verify_ssl=True
    )
    
    # Example 1: Using context manager (recommended)
    print("Example 1: Using JIRA with context manager")
    print("-" * 50)
    
    try:
        with JIRAIntegration(jira_config) as jira:
            # Create a bug
            issue = jira.create_issue(
                summary="Login button not working",
                description="The login button does not respond to clicks",
                issue_type=JIRAIssueType.BUG,
                priority=JIRAPriority.MAJOR,
                labels=["automation", "ui"]
            )
            
            issue_key = issue.get("key")
            print(f"Created issue: {issue_key}")
            
            # Upload a screenshot
            screenshot_path = "reports/screenshot.png"
            if Path(screenshot_path).exists():
                attachment = jira.upload_attachment(
                    issue_key=issue_key,
                    file_path=screenshot_path
                )
                print(f"Uploaded screenshot: {attachment}")
    
    except Exception as e:
        logger.error(f"JIRA integration error: {str(e)}")
    
    # Example 2: Create defect from test failure
    print("\nExample 2: Create defect from test failure")
    print("-" * 50)
    
    with JIRAIntegration(jira_config) as jira:
        defect = jira.create_defect_from_test_failure(
            test_name="test_user_login",
            test_id="TC-001",
            error_message="AssertionError: Expected 'Dashboard' but got 'Login'",
            stack_trace="Traceback (most recent call last):\n  File 'test_login.py', line 42...",
            priority=JIRAPriority.CRITICAL,
            labels=["regression", "login"]
        )
        
        defect_key = defect.get("key")
        print(f"Created defect: {defect_key}")
    
    # Example 3: Link issues and add comments
    print("\nExample 3: Link issues and add comments")
    print("-" * 50)
    
    with JIRAIntegration(jira_config) as jira:
        # Link two issues
        link_result = jira.link_issue(
            issue_key="TEST-123",
            linked_issue_key="TEST-124",
            link_type="Relates"
        )
        print(f"Linked issues: {link_result}")
        
        # Add a comment
        comment = jira.add_comment(
            issue_key="TEST-123",
            comment="This issue is related to the login functionality"
        )
        print(f"Added comment: {comment.get('id')}")
        
        # Add test result comment
        test_comment = jira.add_test_result_comment(
            issue_key="TEST-123",
            test_name="test_user_login",
            status="PASSED",
            duration=5.5,
            execution_time=datetime.now()
        )
        print(f"Added test result comment: {test_comment.get('id')}")
    
    # Example 4: Update issue status
    print("\nExample 4: Update issue status")
    print("-" * 50)
    
    with JIRAIntegration(jira_config) as jira:
        # Update status to Resolved
        status_result = jira.update_issue_status(
            issue_key="TEST-123",
            transition_name="Resolve",
            comment="Fixed in build 1.2.3"
        )
        print(f"Updated status: {status_result}")
    
    # Example 5: Search for issues
    print("\nExample 5: Search for issues")
    print("-" * 50)
    
    with JIRAIntegration(jira_config) as jira:
        # Search for open bugs
        issues = jira.search_issues(
            jql="project = TEST AND issuetype = Bug AND status = Open",
            max_results=10,
            fields=["summary", "status", "priority"]
        )
        
        print(f"Found {len(issues)} open bugs:")
        for issue in issues:
            key = issue.get("key")
            summary = issue.get("fields", {}).get("summary")
            print(f"  - {key}: {summary}")
    
    # Example 6: Batch upload attachments
    print("\nExample 6: Batch upload attachments")
    print("-" * 50)
    
    with JIRAIntegration(jira_config) as jira:
        attachments = [
            "reports/screenshot1.png",
            "reports/screenshot2.png",
            "reports/test_log.txt"
        ]
        
        # Filter existing files
        existing_files = [
            path for path in attachments
            if Path(path).exists()
        ]
        
        if existing_files:
            results = jira.upload_multiple_attachments(
                issue_key="TEST-123",
                file_paths=existing_files
            )
            print(f"Uploaded {len(results)} attachments")
        else:
            print("No files found to upload")
    
    # Example 7: Get issue details
    print("\nExample 7: Get issue details")
    print("-" * 50)
    
    with JIRAIntegration(jira_config) as jira:
        issue = jira.get_issue("TEST-123")
        
        fields = issue.get("fields", {})
        print(f"Issue: {issue.get('key')}")
        print(f"Summary: {fields.get('summary')}")
        print(f"Status: {fields.get('status', {}).get('name')}")
        print(f"Priority: {fields.get('priority', {}).get('name')}")


if __name__ == "__main__":
    asyncio.run(main())
