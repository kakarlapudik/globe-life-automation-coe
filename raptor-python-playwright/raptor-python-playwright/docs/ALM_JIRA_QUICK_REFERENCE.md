# ALM and JIRA Integration - Quick Reference

## ALM Integration

### Setup
```python
from raptor.integrations.alm_integration import ALMIntegration, ALMConfig, ALMTestStatus

alm_config = ALMConfig(
    server_url="http://alm-server:8080/qcbin",
    username="user",
    password="pass",
    domain="DEFAULT",
    project="PROJECT"
)
```

### Publish Test Result
```python
with ALMIntegration(alm_config) as alm:
    alm.publish_test_result(
        test_id="TEST-001",
        test_set_id="SET-001",
        status=ALMTestStatus.PASSED,
        execution_time=10.5,
        comments="Test passed"
    )
```

### Update Status
```python
alm.update_test_status(
    run_id="RUN-001",
    status=ALMTestStatus.FAILED,
    comments="Test failed"
)
```

### Upload Attachments
```python
# Single
alm.upload_attachment(
    run_id="RUN-001",
    file_path="screenshot.png"
)

# Multiple
alm.upload_multiple_attachments(
    run_id="RUN-001",
    file_paths=["file1.png", "file2.png"]
)
```

### Link to Requirement
```python
alm.link_to_requirement(
    test_id="TEST-001",
    requirement_id="REQ-001"
)
```

---

## JIRA Integration

### Setup
```python
from raptor.integrations.jira_integration import (
    JIRAIntegration, JIRAConfig, JIRAIssueType, JIRAPriority
)

jira_config = JIRAConfig(
    server_url="https://jira.company.com",
    username="email@company.com",
    api_token="token",
    project_key="TEST"
)
```

### Create Issue
```python
with JIRAIntegration(jira_config) as jira:
    issue = jira.create_issue(
        summary="Bug summary",
        description="Bug description",
        issue_type=JIRAIssueType.BUG,
        priority=JIRAPriority.MAJOR,
        labels=["automation"]
    )
```

### Create Defect from Test Failure
```python
defect = jira.create_defect_from_test_failure(
    test_name="test_login",
    test_id="TC-001",
    error_message="Login failed",
    stack_trace="Traceback...",
    priority=JIRAPriority.CRITICAL
)
```

### Link Issues
```python
jira.link_issue(
    issue_key="TEST-123",
    linked_issue_key="TEST-124",
    link_type="Relates"
)
```

### Add Comment
```python
# Simple
jira.add_comment(
    issue_key="TEST-123",
    comment="Test comment"
)

# Test result
jira.add_test_result_comment(
    issue_key="TEST-123",
    test_name="test_login",
    status="PASSED",
    duration=5.5,
    execution_time=datetime.now()
)
```

### Update Status
```python
jira.update_issue_status(
    issue_key="TEST-123",
    transition_name="Resolve",
    comment="Fixed"
)
```

### Upload Attachments
```python
# Single
jira.upload_attachment(
    issue_key="TEST-123",
    file_path="screenshot.png"
)

# Multiple
jira.upload_multiple_attachments(
    issue_key="TEST-123",
    file_paths=["file1.png", "file2.png"]
)
```

### Search Issues
```python
issues = jira.search_issues(
    jql="project = TEST AND status = Open",
    max_results=50
)
```

### Get Issue
```python
issue = jira.get_issue("TEST-123")
```

---

## Status Values

### ALM Test Status
```python
ALMTestStatus.PASSED
ALMTestStatus.FAILED
ALMTestStatus.BLOCKED
ALMTestStatus.NOT_COMPLETED
ALMTestStatus.NO_RUN
```

### JIRA Issue Types
```python
JIRAIssueType.BUG
JIRAIssueType.DEFECT
JIRAIssueType.TASK
JIRAIssueType.STORY
JIRAIssueType.TEST
```

### JIRA Priorities
```python
JIRAPriority.BLOCKER
JIRAPriority.CRITICAL
JIRAPriority.MAJOR
JIRAPriority.MINOR
JIRAPriority.TRIVIAL
```

---

## Error Handling

```python
from raptor.integrations.alm_integration import ALMIntegrationException
from raptor.integrations.jira_integration import JIRAIntegrationException

try:
    with ALMIntegration(alm_config) as alm:
        alm.publish_test_result(...)
except ALMIntegrationException as e:
    logger.error(f"ALM error: {str(e)}")

try:
    with JIRAIntegration(jira_config) as jira:
        jira.create_issue(...)
except JIRAIntegrationException as e:
    logger.error(f"JIRA error: {str(e)}")
```

---

## Environment Variables

```bash
# ALM
export ALM_SERVER_URL="http://alm-server:8080/qcbin"
export ALM_USERNAME="user"
export ALM_PASSWORD="pass"
export ALM_DOMAIN="DEFAULT"
export ALM_PROJECT="PROJECT"

# JIRA
export JIRA_SERVER_URL="https://jira.company.com"
export JIRA_USERNAME="email@company.com"
export JIRA_API_TOKEN="token"
export JIRA_PROJECT_KEY="TEST"
```

```python
import os

alm_config = ALMConfig(
    server_url=os.getenv("ALM_SERVER_URL"),
    username=os.getenv("ALM_USERNAME"),
    password=os.getenv("ALM_PASSWORD"),
    domain=os.getenv("ALM_DOMAIN"),
    project=os.getenv("ALM_PROJECT")
)

jira_config = JIRAConfig(
    server_url=os.getenv("JIRA_SERVER_URL"),
    username=os.getenv("JIRA_USERNAME"),
    api_token=os.getenv("JIRA_API_TOKEN"),
    project_key=os.getenv("JIRA_PROJECT_KEY")
)
```
