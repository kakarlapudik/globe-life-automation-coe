"""
JIRA Integration for RAPTOR Framework

This module provides integration with Atlassian JIRA for:
- Linking test results to JIRA issues
- Creating defects automatically for failed tests
- Updating issue status
- Uploading attachments (screenshots, logs)
- Adding comments to issues
"""

import os
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

try:
    import requests
    from requests.auth import HTTPBasicAuth
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

from raptor.core.exceptions import RaptorException
from raptor.utils.logger import get_logger


logger = get_logger(__name__)


class JIRAIssueType(Enum):
    """JIRA issue types."""
    BUG = "Bug"
    DEFECT = "Defect"
    TASK = "Task"
    STORY = "Story"
    TEST = "Test"


class JIRAPriority(Enum):
    """JIRA priority levels."""
    BLOCKER = "Blocker"
    CRITICAL = "Critical"
    MAJOR = "Major"
    MINOR = "Minor"
    TRIVIAL = "Trivial"


class JIRAStatus(Enum):
    """JIRA issue status."""
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"
    CLOSED = "Closed"
    REOPENED = "Reopened"


@dataclass
class JIRAConfig:
    """
    Configuration for JIRA connection.
    
    Attributes:
        server_url: JIRA server URL (e.g., https://jira.company.com)
        username: JIRA username or email
        api_token: JIRA API token or password
        project_key: JIRA project key
        verify_ssl: Whether to verify SSL certificates
    """
    server_url: str
    username: str
    api_token: str
    project_key: str
    verify_ssl: bool = True


class JIRAIntegrationException(RaptorException):
    """Exception raised for JIRA integration errors."""
    pass


class JIRAIntegration:
    """
    Manages integration with Atlassian JIRA.
    
    Provides methods to create issues, link test results, update status,
    and upload attachments to JIRA.
    """
    
    def __init__(self, config: JIRAConfig):
        """
        Initialize JIRA integration.
        
        Args:
            config: JIRA configuration object
            
        Raises:
            JIRAIntegrationException: If requests library is not available
        """
        if not REQUESTS_AVAILABLE:
            raise JIRAIntegrationException(
                "requests library is required for JIRA integration. "
                "Install it with: pip install requests"
            )
        
        self.config = config
        self.session = requests.Session()
        self.session.verify = config.verify_ssl
        self.session.auth = HTTPBasicAuth(config.username, config.api_token)
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
        
        self.api_base = f"{config.server_url}/rest/api/2"
        
        logger.info(f"JIRA integration initialized for {config.server_url}")
    
    def test_connection(self) -> bool:
        """
        Test connection to JIRA server.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            response = self.session.get(f"{self.api_base}/myself")
            
            if response.status_code == 200:
                user_data = response.json()
                logger.info(f"Successfully connected to JIRA as {user_data.get('displayName')}")
                return True
            else:
                logger.error(f"JIRA connection test failed with status {response.status_code}")
                return False
                
        except requests.RequestException as e:
            logger.error(f"JIRA connection test error: {str(e)}")
            return False
    
    def create_issue(
        self,
        summary: str,
        description: str,
        issue_type: JIRAIssueType = JIRAIssueType.BUG,
        priority: Optional[JIRAPriority] = None,
        assignee: Optional[str] = None,
        labels: Optional[List[str]] = None,
        components: Optional[List[str]] = None,
        custom_fields: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new JIRA issue.
        
        Args:
            summary: Issue summary/title
            description: Detailed issue description
            issue_type: Type of issue to create
            priority: Issue priority level
            assignee: Username to assign the issue to
            labels: List of labels to add
            components: List of component names
            custom_fields: Dictionary of custom field values
            
        Returns:
            Dictionary containing the created issue information
            
        Raises:
            JIRAIntegrationException: If issue creation fails
        """
        try:
            issue_data = {
                "fields": {
                    "project": {"key": self.config.project_key},
                    "summary": summary,
                    "description": description,
                    "issuetype": {"name": issue_type.value}
                }
            }
            
            # Add optional fields
            if priority:
                issue_data["fields"]["priority"] = {"name": priority.value}
            
            if assignee:
                issue_data["fields"]["assignee"] = {"name": assignee}
            
            if labels:
                issue_data["fields"]["labels"] = labels
            
            if components:
                issue_data["fields"]["components"] = [{"name": comp} for comp in components]
            
            # Add custom fields
            if custom_fields:
                issue_data["fields"].update(custom_fields)
            
            response = self.session.post(
                f"{self.api_base}/issue",
                json=issue_data
            )
            
            if response.status_code not in [200, 201]:
                raise JIRAIntegrationException(
                    f"Failed to create issue. Status: {response.status_code}, "
                    f"Response: {response.text}"
                )
            
            result = response.json()
            issue_key = result.get("key", "")
            
            logger.info(f"Successfully created JIRA issue: {issue_key}")
            
            return result
            
        except requests.RequestException as e:
            logger.error(f"Error creating JIRA issue: {str(e)}")
            raise JIRAIntegrationException(f"Failed to create issue: {str(e)}")
    
    def create_defect_from_test_failure(
        self,
        test_name: str,
        test_id: str,
        error_message: str,
        stack_trace: Optional[str] = None,
        priority: JIRAPriority = JIRAPriority.MAJOR,
        labels: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a defect issue from a test failure.
        
        Args:
            test_name: Name of the failed test
            test_id: Unique test identifier
            error_message: Error message from the test
            stack_trace: Stack trace from the failure
            priority: Defect priority
            labels: Additional labels for the defect
            
        Returns:
            Dictionary containing the created defect information
            
        Raises:
            JIRAIntegrationException: If defect creation fails
        """
        summary = f"Test Failure: {test_name}"
        
        description = f"""
h3. Test Failure Details

*Test Name:* {test_name}
*Test ID:* {test_id}
*Failure Time:* {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

h4. Error Message
{{code}}
{error_message}
{{code}}
"""
        
        if stack_trace:
            description += f"""
h4. Stack Trace
{{code}}
{stack_trace}
{{code}}
"""
        
        # Add automated test label
        if labels is None:
            labels = []
        if "automated-test-failure" not in labels:
            labels.append("automated-test-failure")
        
        return self.create_issue(
            summary=summary,
            description=description,
            issue_type=JIRAIssueType.BUG,
            priority=priority,
            labels=labels
        )
    
    def link_issue(
        self,
        issue_key: str,
        linked_issue_key: str,
        link_type: str = "Relates"
    ) -> Dict[str, Any]:
        """
        Create a link between two JIRA issues.
        
        Args:
            issue_key: Key of the source issue
            linked_issue_key: Key of the issue to link to
            link_type: Type of link (e.g., "Relates", "Blocks", "Duplicates")
            
        Returns:
            Dictionary containing the link information
            
        Raises:
            JIRAIntegrationException: If linking fails
        """
        try:
            link_data = {
                "type": {"name": link_type},
                "inwardIssue": {"key": issue_key},
                "outwardIssue": {"key": linked_issue_key}
            }
            
            response = self.session.post(
                f"{self.api_base}/issueLink",
                json=link_data
            )
            
            if response.status_code not in [200, 201]:
                raise JIRAIntegrationException(
                    f"Failed to link issues. Status: {response.status_code}, "
                    f"Response: {response.text}"
                )
            
            logger.info(f"Successfully linked {issue_key} to {linked_issue_key}")
            
            return {"success": True, "issue_key": issue_key, "linked_issue_key": linked_issue_key}
            
        except requests.RequestException as e:
            logger.error(f"Error linking JIRA issues: {str(e)}")
            raise JIRAIntegrationException(f"Failed to link issues: {str(e)}")
    
    def add_comment(
        self,
        issue_key: str,
        comment: str,
        visibility: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Add a comment to a JIRA issue.
        
        Args:
            issue_key: Key of the issue to comment on
            comment: Comment text
            visibility: Optional visibility restrictions (e.g., {"type": "role", "value": "Developers"})
            
        Returns:
            Dictionary containing the comment information
            
        Raises:
            JIRAIntegrationException: If adding comment fails
        """
        try:
            comment_data = {"body": comment}
            
            if visibility:
                comment_data["visibility"] = visibility
            
            response = self.session.post(
                f"{self.api_base}/issue/{issue_key}/comment",
                json=comment_data
            )
            
            if response.status_code not in [200, 201]:
                raise JIRAIntegrationException(
                    f"Failed to add comment. Status: {response.status_code}, "
                    f"Response: {response.text}"
                )
            
            result = response.json()
            
            logger.info(f"Successfully added comment to {issue_key}")
            
            return result
            
        except requests.RequestException as e:
            logger.error(f"Error adding comment to JIRA issue: {str(e)}")
            raise JIRAIntegrationException(f"Failed to add comment: {str(e)}")
    
    def add_test_result_comment(
        self,
        issue_key: str,
        test_name: str,
        status: str,
        duration: float,
        execution_time: datetime
    ) -> Dict[str, Any]:
        """
        Add a formatted test result comment to a JIRA issue.
        
        Args:
            issue_key: Key of the issue to comment on
            test_name: Name of the test
            status: Test execution status
            duration: Test duration in seconds
            execution_time: When the test was executed
            
        Returns:
            Dictionary containing the comment information
            
        Raises:
            JIRAIntegrationException: If adding comment fails
        """
        comment = f"""
h4. Automated Test Result

*Test Name:* {test_name}
*Status:* {status}
*Duration:* {duration:.2f}s
*Execution Time:* {execution_time.strftime("%Y-%m-%d %H:%M:%S")}

_This comment was automatically generated by RAPTOR test framework._
"""
        
        return self.add_comment(issue_key, comment)
    
    def update_issue_status(
        self,
        issue_key: str,
        transition_name: str,
        comment: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update the status of a JIRA issue using a transition.
        
        Args:
            issue_key: Key of the issue to update
            transition_name: Name of the transition (e.g., "Resolve", "Close")
            comment: Optional comment to add with the transition
            
        Returns:
            Dictionary containing the transition information
            
        Raises:
            JIRAIntegrationException: If status update fails
        """
        try:
            # Get available transitions
            transitions_response = self.session.get(
                f"{self.api_base}/issue/{issue_key}/transitions"
            )
            
            if transitions_response.status_code != 200:
                raise JIRAIntegrationException(
                    f"Failed to get transitions. Status: {transitions_response.status_code}"
                )
            
            transitions = transitions_response.json().get("transitions", [])
            
            # Find the transition ID
            transition_id = None
            for transition in transitions:
                if transition["name"].lower() == transition_name.lower():
                    transition_id = transition["id"]
                    break
            
            if transition_id is None:
                available = [t["name"] for t in transitions]
                raise JIRAIntegrationException(
                    f"Transition '{transition_name}' not found. Available: {available}"
                )
            
            # Perform the transition
            transition_data = {
                "transition": {"id": transition_id}
            }
            
            if comment:
                transition_data["update"] = {
                    "comment": [{"add": {"body": comment}}]
                }
            
            response = self.session.post(
                f"{self.api_base}/issue/{issue_key}/transitions",
                json=transition_data
            )
            
            if response.status_code not in [200, 204]:
                raise JIRAIntegrationException(
                    f"Failed to update status. Status: {response.status_code}, "
                    f"Response: {response.text}"
                )
            
            logger.info(f"Successfully updated {issue_key} status to {transition_name}")
            
            return {"success": True, "issue_key": issue_key, "transition": transition_name}
            
        except requests.RequestException as e:
            logger.error(f"Error updating JIRA issue status: {str(e)}")
            raise JIRAIntegrationException(f"Failed to update status: {str(e)}")
    
    def upload_attachment(
        self,
        issue_key: str,
        file_path: str
    ) -> Dict[str, Any]:
        """
        Upload an attachment to a JIRA issue.
        
        Args:
            issue_key: Key of the issue to attach to
            file_path: Path to the file to upload
            
        Returns:
            Dictionary containing the attachment information
            
        Raises:
            JIRAIntegrationException: If upload fails
        """
        if not os.path.exists(file_path):
            raise JIRAIntegrationException(f"File not found: {file_path}")
        
        try:
            file_name = os.path.basename(file_path)
            
            with open(file_path, 'rb') as f:
                files = {'file': (file_name, f, 'application/octet-stream')}
                
                # Temporarily remove Content-Type header for multipart upload
                headers = dict(self.session.headers)
                headers.pop('Content-Type', None)
                
                response = self.session.post(
                    f"{self.api_base}/issue/{issue_key}/attachments",
                    files=files,
                    headers={"X-Atlassian-Token": "no-check"}
                )
            
            if response.status_code not in [200, 201]:
                raise JIRAIntegrationException(
                    f"Failed to upload attachment. Status: {response.status_code}, "
                    f"Response: {response.text}"
                )
            
            result = response.json()
            
            logger.info(f"Successfully uploaded {file_name} to {issue_key}")
            
            return result[0] if isinstance(result, list) and result else result
            
        except requests.RequestException as e:
            logger.error(f"Error uploading attachment to JIRA: {str(e)}")
            raise JIRAIntegrationException(f"Failed to upload attachment: {str(e)}")
        except IOError as e:
            logger.error(f"Error reading file {file_path}: {str(e)}")
            raise JIRAIntegrationException(f"Failed to read file: {str(e)}")
    
    def upload_multiple_attachments(
        self,
        issue_key: str,
        file_paths: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Upload multiple attachments to a JIRA issue.
        
        Args:
            issue_key: Key of the issue to attach to
            file_paths: List of file paths to upload
            
        Returns:
            List of dictionaries containing attachment information
            
        Raises:
            JIRAIntegrationException: If any upload fails
        """
        results = []
        
        for file_path in file_paths:
            try:
                result = self.upload_attachment(issue_key, file_path)
                results.append(result)
            except JIRAIntegrationException as e:
                logger.warning(f"Failed to upload {file_path}: {str(e)}")
                # Continue with other files
        
        return results
    
    def get_issue(self, issue_key: str) -> Dict[str, Any]:
        """
        Get details of a JIRA issue.
        
        Args:
            issue_key: Key of the issue to retrieve
            
        Returns:
            Dictionary containing the issue information
            
        Raises:
            JIRAIntegrationException: If retrieval fails
        """
        try:
            response = self.session.get(f"{self.api_base}/issue/{issue_key}")
            
            if response.status_code != 200:
                raise JIRAIntegrationException(
                    f"Failed to get issue. Status: {response.status_code}, "
                    f"Response: {response.text}"
                )
            
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Error getting JIRA issue: {str(e)}")
            raise JIRAIntegrationException(f"Failed to get issue: {str(e)}")
    
    def search_issues(
        self,
        jql: str,
        max_results: int = 50,
        fields: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for JIRA issues using JQL.
        
        Args:
            jql: JQL query string
            max_results: Maximum number of results to return
            fields: List of fields to include in results
            
        Returns:
            List of dictionaries containing issue information
            
        Raises:
            JIRAIntegrationException: If search fails
        """
        try:
            search_data = {
                "jql": jql,
                "maxResults": max_results
            }
            
            if fields:
                search_data["fields"] = fields
            
            response = self.session.post(
                f"{self.api_base}/search",
                json=search_data
            )
            
            if response.status_code != 200:
                raise JIRAIntegrationException(
                    f"Failed to search issues. Status: {response.status_code}, "
                    f"Response: {response.text}"
                )
            
            result = response.json()
            return result.get("issues", [])
            
        except requests.RequestException as e:
            logger.error(f"Error searching JIRA issues: {str(e)}")
            raise JIRAIntegrationException(f"Failed to search issues: {str(e)}")
    
    def __enter__(self):
        """Context manager entry."""
        self.test_connection()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        return False
