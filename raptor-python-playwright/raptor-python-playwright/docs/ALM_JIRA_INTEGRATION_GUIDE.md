## ALM and JIRA Integration Guide

This guide explains how to integrate RAPTOR with ALM (Application Lifecycle Management) and JIRA for test result publishing and defect tracking.

### Table of Contents

1. [Overview](#overview)
2. [ALM Integration](#alm-integration)
3. [JIRA Integration](#jira-integration)
4. [Configuration](#configuration)
5. [Usage Examples](#usage-examples)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

---

## Overview

RAPTOR provides seamless integration with:
- **HP ALM/Quality Center**: For publishing test execution results and managing test cases
- **Atlassian JIRA**: For creating defects, linking issues, and tracking test results

### Features

**ALM Integration:**
- Authenticate with ALM server
- Publish test case results
- Update test execution status
- Upload attachments (screenshots, logs)
- Link tests to requirements

**JIRA Integration:**
- Create issues and defects
- Link test results to JIRA issues
- Add comments with test execution details
- Update issue status
- Upload attachments
- Search for issues using JQL

---

## ALM Integration

### Installation

The ALM integration requires the `requests` library:

```bash
pip install requests
```

### Configuration

Create an ALM configuration object:

```python
from raptor.integrations.alm_integration import ALMConfig, ALMIntegration

alm_config = ALMConfig(
    server_url="http://alm-server:8080/qcbin",
    username="your_username",
    password="your_password",
    domain="DEFAULT",
    project="MY_PROJECT",
    verify_ssl=True  # Set to False for self-signed certificates
)
```

### Basic Usage

#### Using Context Manager (Recommended)

```python
from raptor.integrations.alm_integration import ALMIntegration, ALMTestStatus

with ALMIntegration(alm_config) as alm:
    # Publish test result
    result = alm.publish_test_result(
        test_id="TEST-001",
        test_set_id="SET-001",
        status=ALMTestStatus.PASSED,
        execution_time=15.5,
        comments="Test executed successfully"
    )
    
    # Upload screenshot
    alm.upload_attachment(
        run_id="RUN-001",
        file_path="screenshot.png",
        description="Test screenshot"
    )
```

#### Manual Authentication

```python
alm = ALMIntegration(alm_config)

try:
    alm.authenticate()
    
    # Your ALM operations here
    alm.publish_test_result(...)
    
finally:
    alm.logout()
```

### ALM Test Status Values

```python
from raptor.integrations.alm_integration import ALMTestStatus

ALMTestStatus.PASSED        # Test passed
ALMTestStatus.FAILED        # Test failed
ALMTestStatus.BLOCKED       # Test blocked
ALMTestStatus.NOT_COMPLETED # Test not completed
ALMTestStatus.NO_RUN        # Test not run
```

### Publishing Test Results

```python
result = alm.publish_test_result(
    test_id="TEST-001",           # ALM test case ID
    test_set_id="SET-001",        # ALM test set ID
    status=ALMTestStatus.PASSED,  # Test status
    execution_date=datetime.now(), # Optional: defaults to now
    execution_time=10.5,          # Optional: duration in seconds
    comments="Test passed",       # Optional: comments
    tester_name="Automation"      # Optional: tester name
)
```

### Updating Test Status

```python
alm.update_test_status(
    run_id="RUN-001",
    status=ALMTestStatus.FAILED,
    comments="Test failed due to timeout"
)
```

### Uploading Attachments

```python
# Single attachment
alm.upload_attachment(
    run_id="RUN-001",
    file_path="screenshot.png",
    description="Failure screenshot"
)

# Multiple attachments
alm.upload_multiple_attachments(
    run_id="RUN-001",
    file_paths=["screenshot1.png", "screenshot2.png", "log.txt"],
    description="Test artifacts"
)
```

### Linking to Requirements

```python
alm.link_to_requirement(
    test_id="TEST-001",
    requirement_id="REQ-001"
)
```

---

## JIRA Integration

### Installation

The JIRA integration requires the `requests` library:

```bash
pip install requests
```

### Configuration

Create a JIRA configuration object:

```python
from raptor.integrations.jira_integration import JIRAConfig, JIRAIntegration

jira_config = JIRAConfig(
    server_url="https://jira.company.com",
    username="your_email@company.com",
    api_token="your_api_token",  # Generate from JIRA account settings
    project_key="TEST",
    verify_ssl=True
)
```

**Note:** For JIRA Cloud, use an API token instead of password. Generate it from:
Account Settings → Security → API Tokens

### Basic Usage

#### Using Context Manager (Recommended)

```python
from raptor.integrations.jira_integration import (
    JIRAIntegration,
    JIRAIssueType,
    JIRAPriority
)

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
```

### Creating Issues

```python
issue = jira.create_issue(
    summary="Issue summary",
    description="Detailed description",
    issue_type=JIRAIssueType.BUG,      # BUG, DEFECT, TASK, STORY, TEST
    priority=JIRAPriority.MAJOR,       # BLOCKER, CRITICAL, MAJOR, MINOR, TRIVIAL
    assignee="username",               # Optional
    labels=["automation", "test"],     # Optional
    components=["Component1"],         # Optional
    custom_fields={"customfield_10001": "value"}  # Optional
)
```

### Creating Defects from Test Failures

```python
defect = jira.create_defect_from_test_failure(
    test_name="test_user_login",
    test_id="TC-001",
    error_message="AssertionError: Expected 'Dashboard' but got 'Login'",
    stack_trace="Traceback...",
    priority=JIRAPriority.CRITICAL,
    labels=["regression", "login"]
)
```

### Linking Issues

```python
jira.link_issue(
    issue_key="TEST-123",
    linked_issue_key="TEST-124",
    link_type="Relates"  # Relates, Blocks, Duplicates, etc.
)
```

### Adding Comments

```python
# Simple comment
jira.add_comment(
    issue_key="TEST-123",
    comment="This issue is related to the login functionality"
)

# Test result comment (formatted)
jira.add_test_result_comment(
    issue_key="TEST-123",
    test_name="test_user_login",
    status="PASSED",
    duration=5.5,
    execution_time=datetime.now()
)
```

### Updating Issue Status

```python
jira.update_issue_status(
    issue_key="TEST-123",
    transition_name="Resolve",  # Transition name from your workflow
    comment="Fixed in build 1.2.3"
)
```

### Uploading Attachments

```python
# Single attachment
jira.upload_attachment(
    issue_key="TEST-123",
    file_path="screenshot.png"
)

# Multiple attachments
jira.upload_multiple_attachments(
    issue_key="TEST-123",
    file_paths=["screenshot1.png", "screenshot2.png", "log.txt"]
)
```

### Searching Issues

```python
issues = jira.search_issues(
    jql="project = TEST AND issuetype = Bug AND status = Open",
    max_results=50,
    fields=["summary", "status", "priority"]
)

for issue in issues:
    print(f"{issue['key']}: {issue['fields']['summary']}")
```

### Getting Issue Details

```python
issue = jira.get_issue("TEST-123")

fields = issue.get("fields", {})
print(f"Summary: {fields.get('summary')}")
print(f"Status: {fields.get('status', {}).get('name')}")
```

---

## Configuration

### Environment Variables

Store sensitive credentials in environment variables:

```python
import os
from raptor.integrations.alm_integration import ALMConfig

alm_config = ALMConfig(
    server_url=os.getenv("ALM_SERVER_URL"),
    username=os.getenv("ALM_USERNAME"),
    password=os.getenv("ALM_PASSWORD"),
    domain=os.getenv("ALM_DOMAIN"),
    project=os.getenv("ALM_PROJECT")
)
```

### Configuration File

Store configuration in YAML:

```yaml
# config/integrations.yaml
alm:
  server_url: "http://alm-server:8080/qcbin"
  domain: "DEFAULT"
  project: "MY_PROJECT"
  verify_ssl: true

jira:
  server_url: "https://jira.company.com"
  project_key: "TEST"
  verify_ssl: true
```

Load configuration:

```python
import yaml

with open("config/integrations.yaml") as f:
    config = yaml.safe_load(f)

alm_config = ALMConfig(
    server_url=config["alm"]["server_url"],
    username=os.getenv("ALM_USERNAME"),
    password=os.getenv("ALM_PASSWORD"),
    domain=config["alm"]["domain"],
    project=config["alm"]["project"],
    verify_ssl=config["alm"]["verify_ssl"]
)
```

---

## Usage Examples

### Example 1: Publish Test Results to ALM

```python
from raptor.integrations.alm_integration import ALMIntegration, ALMTestStatus
from raptor.utils.reporter import TestReporter, TestResult, TestStatus

# Get test results from reporter
reporter = TestReporter()
test_results = reporter.test_results

# Publish to ALM
with ALMIntegration(alm_config) as alm:
    for result in test_results:
        # Map RAPTOR status to ALM status
        alm_status = (
            ALMTestStatus.PASSED if result.status == TestStatus.PASSED
            else ALMTestStatus.FAILED
        )
        
        # Publish result
        alm.publish_test_result(
            test_id=result.test_id,
            test_set_id="SET-001",
            status=alm_status,
            execution_time=result.duration,
            comments=result.error_message or "Test completed"
        )
        
        # Upload screenshots if test failed
        if result.status == TestStatus.FAILED and result.screenshots:
            alm.upload_multiple_attachments(
                run_id=result.test_id,
                file_paths=result.screenshots
            )
```

### Example 2: Create JIRA Defects for Failed Tests

```python
from raptor.integrations.jira_integration import JIRAIntegration, JIRAPriority
from raptor.utils.reporter import TestReporter, TestStatus

reporter = TestReporter()

with JIRAIntegration(jira_config) as jira:
    for result in reporter.test_results:
        if result.status == TestStatus.FAILED:
            # Create defect
            defect = jira.create_defect_from_test_failure(
                test_name=result.test_name,
                test_id=result.test_id,
                error_message=result.error_message,
                stack_trace=result.stack_trace,
                priority=JIRAPriority.MAJOR
            )
            
            defect_key = defect.get("key")
            
            # Upload screenshots
            if result.screenshots:
                jira.upload_multiple_attachments(
                    issue_key=defect_key,
                    file_paths=result.screenshots
                )
```

### Example 3: Update JIRA Issues with Test Results

```python
with JIRAIntegration(jira_config) as jira:
    for result in reporter.test_results:
        # Find related JIRA issue (assuming test_id matches issue key)
        issue_key = result.metadata.get("jira_issue")
        
        if issue_key:
            # Add test result comment
            jira.add_test_result_comment(
                issue_key=issue_key,
                test_name=result.test_name,
                status=result.status.value,
                duration=result.duration,
                execution_time=result.start_time
            )
            
            # Update status if test passed
            if result.status == TestStatus.PASSED:
                jira.update_issue_status(
                    issue_key=issue_key,
                    transition_name="Resolve",
                    comment="Test passed in automated execution"
                )
```

---

## Best Practices

### 1. Use Context Managers

Always use context managers to ensure proper cleanup:

```python
with ALMIntegration(alm_config) as alm:
    # Your code here
    pass  # Automatic logout on exit
```

### 2. Handle Exceptions

Wrap integration calls in try-except blocks:

```python
try:
    with JIRAIntegration(jira_config) as jira:
        jira.create_issue(...)
except JIRAIntegrationException as e:
    logger.error(f"JIRA integration failed: {str(e)}")
    # Handle error appropriately
```

### 3. Batch Operations

Use batch methods for multiple attachments:

```python
# Good: Single API call
alm.upload_multiple_attachments(run_id, file_paths)

# Avoid: Multiple API calls
for file_path in file_paths:
    alm.upload_attachment(run_id, file_path)
```

### 4. Secure Credentials

Never hardcode credentials:

```python
# Bad
password = "my_password"

# Good
password = os.getenv("ALM_PASSWORD")
```

### 5. Test Connection

Test connectivity before running tests:

```python
jira = JIRAIntegration(jira_config)
if not jira.test_connection():
    logger.error("Cannot connect to JIRA")
    sys.exit(1)
```

### 6. Use Meaningful Labels

Add labels to help categorize issues:

```python
labels = [
    "automated-test",
    f"environment-{environment}",
    f"build-{build_number}"
]

jira.create_issue(..., labels=labels)
```

---

## Troubleshooting

### ALM Issues

**Problem:** Authentication fails with 401 error

**Solution:**
- Verify username and password
- Check if account is locked
- Ensure domain and project names are correct

**Problem:** Cannot upload attachments

**Solution:**
- Check file exists and is readable
- Verify file size is within ALM limits
- Ensure run ID is valid

### JIRA Issues

**Problem:** API token authentication fails

**Solution:**
- Generate a new API token from JIRA account settings
- Use email address as username (for JIRA Cloud)
- Check if API token has expired

**Problem:** Cannot update issue status

**Solution:**
- Verify transition name matches your workflow
- Check user has permission to perform transition
- Use `get_transitions()` to see available transitions

**Problem:** SSL certificate verification fails

**Solution:**
```python
config = JIRAConfig(
    ...,
    verify_ssl=False  # For self-signed certificates
)
```

### General Issues

**Problem:** `requests` module not found

**Solution:**
```bash
pip install requests
```

**Problem:** Connection timeout

**Solution:**
- Check network connectivity
- Verify server URL is correct
- Check firewall settings

---

## API Reference

### ALM Integration

See `raptor/integrations/alm_integration.py` for complete API documentation.

Key classes:
- `ALMIntegration`: Main integration class
- `ALMConfig`: Configuration dataclass
- `ALMTestStatus`: Test status enumeration
- `ALMIntegrationException`: Exception class

### JIRA Integration

See `raptor/integrations/jira_integration.py` for complete API documentation.

Key classes:
- `JIRAIntegration`: Main integration class
- `JIRAConfig`: Configuration dataclass
- `JIRAIssueType`: Issue type enumeration
- `JIRAPriority`: Priority enumeration
- `JIRAIntegrationException`: Exception class

---

## Additional Resources

- [HP ALM REST API Documentation](https://admhelp.microfocus.com/alm/en/latest/api_refs/REST/webframe.html)
- [JIRA REST API Documentation](https://developer.atlassian.com/cloud/jira/platform/rest/v2/)
- [RAPTOR Framework Documentation](../README.md)

---

**Last Updated:** 2024
**Version:** 1.0.0
