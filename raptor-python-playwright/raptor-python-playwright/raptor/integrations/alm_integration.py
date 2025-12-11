"""
ALM (Application Lifecycle Management) Integration for RAPTOR Framework

This module provides integration with HP ALM/Quality Center for:
- Publishing test case results
- Updating test execution status
- Uploading attachments (screenshots, logs)
- Linking test runs to requirements
"""

import os
import base64
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


class ALMTestStatus(Enum):
    """ALM test execution status."""
    PASSED = "Passed"
    FAILED = "Failed"
    BLOCKED = "Blocked"
    NOT_COMPLETED = "Not Completed"
    NO_RUN = "No Run"


@dataclass
class ALMConfig:
    """
    Configuration for ALM connection.
    
    Attributes:
        server_url: ALM server URL (e.g., http://alm-server:8080/qcbin)
        username: ALM username
        password: ALM password
        domain: ALM domain
        project: ALM project name
        verify_ssl: Whether to verify SSL certificates
    """
    server_url: str
    username: str
    password: str
    domain: str
    project: str
    verify_ssl: bool = True


class ALMIntegrationException(RaptorException):
    """Exception raised for ALM integration errors."""
    pass


class ALMIntegration:
    """
    Manages integration with HP ALM/Quality Center.
    
    Provides methods to publish test results, update test execution status,
    and upload attachments to ALM.
    """
    
    def __init__(self, config: ALMConfig):
        """
        Initialize ALM integration.
        
        Args:
            config: ALM configuration object
            
        Raises:
            ALMIntegrationException: If requests library is not available
        """
        if not REQUESTS_AVAILABLE:
            raise ALMIntegrationException(
                "requests library is required for ALM integration. "
                "Install it with: pip install requests"
            )
        
        self.config = config
        self.session = requests.Session()
        self.session.verify = config.verify_ssl
        self.session.auth = HTTPBasicAuth(config.username, config.password)
        
        self._authenticated = False
        self._cookies = None
        
        logger.info(f"ALM integration initialized for {config.server_url}")
    
    def authenticate(self) -> bool:
        """
        Authenticate with ALM server.
        
        Returns:
            True if authentication successful, False otherwise
            
        Raises:
            ALMIntegrationException: If authentication fails
        """
        try:
            # Step 1: Check if authentication is required
            auth_url = f"{self.config.server_url}/rest/is-authenticated"
            response = self.session.get(auth_url)
            
            if response.status_code == 200:
                logger.info("Already authenticated with ALM")
                self._authenticated = True
                return True
            
            # Step 2: Perform authentication
            auth_url = f"{self.config.server_url}/authentication-point/authenticate"
            response = self.session.get(auth_url)
            
            if response.status_code != 200:
                raise ALMIntegrationException(
                    f"Authentication failed with status {response.status_code}: {response.text}"
                )
            
            # Step 3: Create session
            session_url = f"{self.config.server_url}/rest/site-session"
            response = self.session.post(session_url)
            
            if response.status_code not in [200, 201]:
                raise ALMIntegrationException(
                    f"Session creation failed with status {response.status_code}: {response.text}"
                )
            
            self._cookies = self.session.cookies
            self._authenticated = True
            
            logger.info("Successfully authenticated with ALM")
            return True
            
        except requests.RequestException as e:
            logger.error(f"ALM authentication error: {str(e)}")
            raise ALMIntegrationException(f"Failed to authenticate with ALM: {str(e)}")
    
    def logout(self) -> None:
        """Logout from ALM server."""
        if not self._authenticated:
            return
        
        try:
            logout_url = f"{self.config.server_url}/authentication-point/logout"
            self.session.get(logout_url)
            
            self._authenticated = False
            self._cookies = None
            
            logger.info("Logged out from ALM")
            
        except requests.RequestException as e:
            logger.warning(f"Error during ALM logout: {str(e)}")
    
    def publish_test_result(
        self,
        test_id: str,
        test_set_id: str,
        status: ALMTestStatus,
        execution_date: Optional[datetime] = None,
        execution_time: Optional[float] = None,
        comments: Optional[str] = None,
        tester_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Publish test case result to ALM.
        
        Args:
            test_id: ALM test case ID
            test_set_id: ALM test set ID
            status: Test execution status
            execution_date: Test execution date (defaults to now)
            execution_time: Execution duration in seconds
            comments: Additional comments
            tester_name: Name of the tester
            
        Returns:
            Dictionary containing the created test run information
            
        Raises:
            ALMIntegrationException: If publishing fails
        """
        if not self._authenticated:
            self.authenticate()
        
        if execution_date is None:
            execution_date = datetime.now()
        
        try:
            # Create test run instance
            run_url = (
                f"{self.config.server_url}/rest/domains/{self.config.domain}/"
                f"projects/{self.config.project}/runs"
            )
            
            # Prepare run data
            run_data = {
                "Type": "run",
                "Fields": {
                    "Field": [
                        {"Name": "test-id", "Value": test_id},
                        {"Name": "testcycl-id", "Value": test_set_id},
                        {"Name": "status", "Value": status.value},
                        {"Name": "execution-date", "Value": execution_date.strftime("%Y-%m-%d")},
                        {"Name": "execution-time", "Value": execution_date.strftime("%H:%M:%S")},
                    ]
                }
            }
            
            # Add optional fields
            if execution_time is not None:
                run_data["Fields"]["Field"].append({
                    "Name": "duration",
                    "Value": str(int(execution_time))
                })
            
            if comments:
                run_data["Fields"]["Field"].append({
                    "Name": "comments",
                    "Value": comments
                })
            
            if tester_name:
                run_data["Fields"]["Field"].append({
                    "Name": "owner",
                    "Value": tester_name
                })
            
            # Send request
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            response = self.session.post(
                run_url,
                json=run_data,
                headers=headers
            )
            
            if response.status_code not in [200, 201]:
                raise ALMIntegrationException(
                    f"Failed to publish test result. Status: {response.status_code}, "
                    f"Response: {response.text}"
                )
            
            result = response.json()
            run_id = self._extract_run_id(result)
            
            logger.info(
                f"Successfully published test result to ALM. "
                f"Test ID: {test_id}, Run ID: {run_id}, Status: {status.value}"
            )
            
            return result
            
        except requests.RequestException as e:
            logger.error(f"Error publishing test result to ALM: {str(e)}")
            raise ALMIntegrationException(f"Failed to publish test result: {str(e)}")
    
    def update_test_status(
        self,
        run_id: str,
        status: ALMTestStatus,
        comments: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update test execution status in ALM.
        
        Args:
            run_id: ALM test run ID
            status: New test execution status
            comments: Additional comments
            
        Returns:
            Dictionary containing the updated test run information
            
        Raises:
            ALMIntegrationException: If update fails
        """
        if not self._authenticated:
            self.authenticate()
        
        try:
            update_url = (
                f"{self.config.server_url}/rest/domains/{self.config.domain}/"
                f"projects/{self.config.project}/runs/{run_id}"
            )
            
            # Prepare update data
            update_data = {
                "Type": "run",
                "Fields": {
                    "Field": [
                        {"Name": "status", "Value": status.value}
                    ]
                }
            }
            
            if comments:
                update_data["Fields"]["Field"].append({
                    "Name": "comments",
                    "Value": comments
                })
            
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            response = self.session.put(
                update_url,
                json=update_data,
                headers=headers
            )
            
            if response.status_code not in [200, 201]:
                raise ALMIntegrationException(
                    f"Failed to update test status. Status: {response.status_code}, "
                    f"Response: {response.text}"
                )
            
            logger.info(f"Successfully updated test status in ALM. Run ID: {run_id}, Status: {status.value}")
            
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Error updating test status in ALM: {str(e)}")
            raise ALMIntegrationException(f"Failed to update test status: {str(e)}")
    
    def upload_attachment(
        self,
        run_id: str,
        file_path: str,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload attachment (screenshot, log) to ALM test run.
        
        Args:
            run_id: ALM test run ID
            file_path: Path to the file to upload
            description: Optional description of the attachment
            
        Returns:
            Dictionary containing the attachment information
            
        Raises:
            ALMIntegrationException: If upload fails
        """
        if not self._authenticated:
            self.authenticate()
        
        if not os.path.exists(file_path):
            raise ALMIntegrationException(f"File not found: {file_path}")
        
        try:
            attachment_url = (
                f"{self.config.server_url}/rest/domains/{self.config.domain}/"
                f"projects/{self.config.project}/runs/{run_id}/attachments"
            )
            
            # Read file content
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            file_name = os.path.basename(file_path)
            
            # Prepare attachment data
            attachment_data = {
                "Type": "attachment",
                "Fields": {
                    "Field": [
                        {"Name": "name", "Value": file_name},
                        {"Name": "file-size", "Value": str(len(file_content))}
                    ]
                }
            }
            
            if description:
                attachment_data["Fields"]["Field"].append({
                    "Name": "description",
                    "Value": description
                })
            
            # Step 1: Create attachment entity
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            response = self.session.post(
                attachment_url,
                json=attachment_data,
                headers=headers
            )
            
            if response.status_code not in [200, 201]:
                raise ALMIntegrationException(
                    f"Failed to create attachment entity. Status: {response.status_code}, "
                    f"Response: {response.text}"
                )
            
            result = response.json()
            attachment_id = self._extract_attachment_id(result)
            
            # Step 2: Upload file content
            upload_url = f"{attachment_url}/{attachment_id}"
            
            headers = {
                "Content-Type": "application/octet-stream"
            }
            
            response = self.session.put(
                upload_url,
                data=file_content,
                headers=headers
            )
            
            if response.status_code not in [200, 201]:
                raise ALMIntegrationException(
                    f"Failed to upload file content. Status: {response.status_code}, "
                    f"Response: {response.text}"
                )
            
            logger.info(
                f"Successfully uploaded attachment to ALM. "
                f"Run ID: {run_id}, File: {file_name}, Attachment ID: {attachment_id}"
            )
            
            return result
            
        except requests.RequestException as e:
            logger.error(f"Error uploading attachment to ALM: {str(e)}")
            raise ALMIntegrationException(f"Failed to upload attachment: {str(e)}")
        except IOError as e:
            logger.error(f"Error reading file {file_path}: {str(e)}")
            raise ALMIntegrationException(f"Failed to read file: {str(e)}")
    
    def upload_multiple_attachments(
        self,
        run_id: str,
        file_paths: List[str],
        description: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Upload multiple attachments to ALM test run.
        
        Args:
            run_id: ALM test run ID
            file_paths: List of file paths to upload
            description: Optional description for all attachments
            
        Returns:
            List of dictionaries containing attachment information
            
        Raises:
            ALMIntegrationException: If any upload fails
        """
        results = []
        
        for file_path in file_paths:
            try:
                result = self.upload_attachment(run_id, file_path, description)
                results.append(result)
            except ALMIntegrationException as e:
                logger.warning(f"Failed to upload {file_path}: {str(e)}")
                # Continue with other files
        
        return results
    
    def link_to_requirement(
        self,
        test_id: str,
        requirement_id: str
    ) -> Dict[str, Any]:
        """
        Link test case to requirement in ALM.
        
        Args:
            test_id: ALM test case ID
            requirement_id: ALM requirement ID
            
        Returns:
            Dictionary containing the link information
            
        Raises:
            ALMIntegrationException: If linking fails
        """
        if not self._authenticated:
            self.authenticate()
        
        try:
            link_url = (
                f"{self.config.server_url}/rest/domains/{self.config.domain}/"
                f"projects/{self.config.project}/test-instances"
            )
            
            link_data = {
                "Type": "test-instance",
                "Fields": {
                    "Field": [
                        {"Name": "test-id", "Value": test_id},
                        {"Name": "req-id", "Value": requirement_id}
                    ]
                }
            }
            
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            response = self.session.post(
                link_url,
                json=link_data,
                headers=headers
            )
            
            if response.status_code not in [200, 201]:
                raise ALMIntegrationException(
                    f"Failed to link test to requirement. Status: {response.status_code}, "
                    f"Response: {response.text}"
                )
            
            logger.info(f"Successfully linked test {test_id} to requirement {requirement_id}")
            
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Error linking test to requirement: {str(e)}")
            raise ALMIntegrationException(f"Failed to link test to requirement: {str(e)}")
    
    def _extract_run_id(self, response_data: Dict[str, Any]) -> str:
        """Extract run ID from ALM response."""
        try:
            fields = response_data.get("Fields", {}).get("Field", [])
            for field in fields:
                if field.get("Name") == "id":
                    return field.get("Value", "")
            return ""
        except (KeyError, TypeError):
            return ""
    
    def _extract_attachment_id(self, response_data: Dict[str, Any]) -> str:
        """Extract attachment ID from ALM response."""
        try:
            fields = response_data.get("Fields", {}).get("Field", [])
            for field in fields:
                if field.get("Name") == "id":
                    return field.get("Value", "")
            return ""
        except (KeyError, TypeError):
            return ""
    
    def __enter__(self):
        """Context manager entry."""
        self.authenticate()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.logout()
        return False
