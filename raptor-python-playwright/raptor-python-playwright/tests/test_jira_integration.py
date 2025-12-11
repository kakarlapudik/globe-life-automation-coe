"""
Unit tests for JIRA Integration

Tests the JIRA integration functionality including:
- Creating issues
- Linking issues
- Adding comments
- Updating status
- Uploading attachments
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from raptor.integrations.jira_integration import (
    JIRAIntegration,
    JIRAConfig,
    JIRAIssueType,
    JIRAPriority,
    JIRAIntegrationException
)


@pytest.fixture
def jira_config():
    """Create a test JIRA configuration."""
    return JIRAConfig(
        server_url="https://jira-test.example.com",
        username="test_user",
        api_token="test_token",
        project_key="TEST",
        verify_ssl=False
    )


@pytest.fixture
def mock_session():
    """Create a mock requests session."""
    with patch('raptor.integrations.jira_integration.requests.Session') as mock:
        session = MagicMock()
        mock.return_value = session
        yield session


class TestJIRAIntegration:
    """Test suite for JIRA integration."""
    
    def test_initialization(self, jira_config):
        """Test JIRA integration initialization."""
        jira = JIRAIntegration(jira_config)
        
        assert jira.config == jira_config
        assert jira.api_base == f"{jira_config.server_url}/rest/api/2"
    
    def test_connection_success(self, jira_config, mock_session):
        """Test successful connection to JIRA."""
        mock_session.get.return_value = Mock(
            status_code=200,
            json=lambda: {"displayName": "Test User"}
        )
        
        jira = JIRAIntegration(jira_config)
        result = jira.test_connection()
        
        assert result is True
    
    def test_connection_failure(self, jira_config, mock_session):
        """Test failed connection to JIRA."""
        mock_session.get.return_value = Mock(status_code=401)
        
        jira = JIRAIntegration(jira_config)
        result = jira.test_connection()
        
        assert result is False
    
    def test_create_issue(self, jira_config, mock_session):
        """Test creating a JIRA issue."""
        mock_session.post.return_value = Mock(
            status_code=201,
            json=lambda: {
                "key": "TEST-123",
                "id": "10001"
            }
        )
        
        jira = JIRAIntegration(jira_config)
        
        result = jira.create_issue(
            summary="Test issue",
            description="Test description",
            issue_type=JIRAIssueType.BUG,
            priority=JIRAPriority.MAJOR
        )
        
        assert result is not None
        assert result.get("key") == "TEST-123"
        assert mock_session.post.called
    
    def test_create_issue_with_labels(self, jira_config, mock_session):
        """Test creating issue with labels and components."""
        mock_session.post.return_value = Mock(
            status_code=201,
            json=lambda: {"key": "TEST-124"}
        )
        
        jira = JIRAIntegration(jira_config)
        
        result = jira.create_issue(
            summary="Test issue",
            description="Test description",
            labels=["automation", "test"],
            components=["Component1"]
        )
        
        assert result is not None
    
    def test_create_defect_from_test_failure(self, jira_config, mock_session):
        """Test creating defect from test failure."""
        mock_session.post.return_value = Mock(
            status_code=201,
            json=lambda: {"key": "TEST-125"}
        )
        
        jira = JIRAIntegration(jira_config)
        
        result = jira.create_defect_from_test_failure(
            test_name="test_login",
            test_id="TC-001",
            error_message="Login failed",
            stack_trace="Traceback...",
            priority=JIRAPriority.CRITICAL
        )
        
        assert result is not None
        assert mock_session.post.called
    
    def test_link_issue(self, jira_config, mock_session):
        """Test linking two JIRA issues."""
        mock_session.post.return_value = Mock(status_code=201)
        
        jira = JIRAIntegration(jira_config)
        
        result = jira.link_issue(
            issue_key="TEST-123",
            linked_issue_key="TEST-124",
            link_type="Relates"
        )
        
        assert result["success"] is True
        assert mock_session.post.called
    
    def test_add_comment(self, jira_config, mock_session):
        """Test adding comment to JIRA issue."""
        mock_session.post.return_value = Mock(
            status_code=201,
            json=lambda: {"id": "10001"}
        )
        
        jira = JIRAIntegration(jira_config)
        
        result = jira.add_comment(
            issue_key="TEST-123",
            comment="Test comment"
        )
        
        assert result is not None
        assert mock_session.post.called
    
    def test_add_test_result_comment(self, jira_config, mock_session):
        """Test adding formatted test result comment."""
        mock_session.post.return_value = Mock(
            status_code=201,
            json=lambda: {"id": "10002"}
        )
        
        jira = JIRAIntegration(jira_config)
        
        result = jira.add_test_result_comment(
            issue_key="TEST-123",
            test_name="test_login",
            status="PASSED",
            duration=5.5,
            execution_time=datetime.now()
        )
        
        assert result is not None
    
    def test_update_issue_status(self, jira_config, mock_session):
        """Test updating issue status."""
        # Mock getting transitions
        mock_session.get.return_value = Mock(
            status_code=200,
            json=lambda: {
                "transitions": [
                    {"id": "11", "name": "Resolve"},
                    {"id": "21", "name": "Close"}
                ]
            }
        )
        
        # Mock performing transition
        mock_session.post.return_value = Mock(status_code=204)
        
        jira = JIRAIntegration(jira_config)
        
        result = jira.update_issue_status(
            issue_key="TEST-123",
            transition_name="Resolve",
            comment="Fixed in latest build"
        )
        
        assert result["success"] is True
        assert mock_session.get.called
        assert mock_session.post.called
    
    def test_update_issue_status_invalid_transition(self, jira_config, mock_session):
        """Test updating status with invalid transition."""
        mock_session.get.return_value = Mock(
            status_code=200,
            json=lambda: {
                "transitions": [
                    {"id": "11", "name": "Resolve"}
                ]
            }
        )
        
        jira = JIRAIntegration(jira_config)
        
        with pytest.raises(JIRAIntegrationException, match="not found"):
            jira.update_issue_status(
                issue_key="TEST-123",
                transition_name="InvalidTransition"
            )
    
    def test_upload_attachment(self, jira_config, mock_session, tmp_path):
        """Test uploading attachment to JIRA."""
        # Create a temporary file
        test_file = tmp_path / "screenshot.png"
        test_file.write_bytes(b"fake image data")
        
        mock_session.post.return_value = Mock(
            status_code=200,
            json=lambda: [{
                "id": "10001",
                "filename": "screenshot.png"
            }]
        )
        
        jira = JIRAIntegration(jira_config)
        
        result = jira.upload_attachment(
            issue_key="TEST-123",
            file_path=str(test_file)
        )
        
        assert result is not None
        assert mock_session.post.called
    
    def test_upload_attachment_file_not_found(self, jira_config):
        """Test uploading attachment with non-existent file."""
        jira = JIRAIntegration(jira_config)
        
        with pytest.raises(JIRAIntegrationException, match="File not found"):
            jira.upload_attachment(
                issue_key="TEST-123",
                file_path="/nonexistent/file.png"
            )
    
    def test_upload_multiple_attachments(self, jira_config, mock_session, tmp_path):
        """Test uploading multiple attachments."""
        # Create temporary files
        file1 = tmp_path / "screenshot1.png"
        file1.write_bytes(b"image 1")
        file2 = tmp_path / "screenshot2.png"
        file2.write_bytes(b"image 2")
        
        mock_session.post.return_value = Mock(
            status_code=200,
            json=lambda: [{"id": "10001", "filename": "screenshot.png"}]
        )
        
        jira = JIRAIntegration(jira_config)
        
        results = jira.upload_multiple_attachments(
            issue_key="TEST-123",
            file_paths=[str(file1), str(file2)]
        )
        
        assert len(results) == 2
    
    def test_get_issue(self, jira_config, mock_session):
        """Test getting issue details."""
        mock_session.get.return_value = Mock(
            status_code=200,
            json=lambda: {
                "key": "TEST-123",
                "fields": {
                    "summary": "Test issue",
                    "status": {"name": "Open"}
                }
            }
        )
        
        jira = JIRAIntegration(jira_config)
        
        result = jira.get_issue("TEST-123")
        
        assert result is not None
        assert result["key"] == "TEST-123"
    
    def test_search_issues(self, jira_config, mock_session):
        """Test searching issues with JQL."""
        mock_session.post.return_value = Mock(
            status_code=200,
            json=lambda: {
                "issues": [
                    {"key": "TEST-123"},
                    {"key": "TEST-124"}
                ]
            }
        )
        
        jira = JIRAIntegration(jira_config)
        
        results = jira.search_issues(
            jql="project = TEST AND status = Open",
            max_results=10
        )
        
        assert len(results) == 2
        assert mock_session.post.called
    
    def test_context_manager(self, jira_config, mock_session):
        """Test using JIRA integration as context manager."""
        mock_session.get.return_value = Mock(
            status_code=200,
            json=lambda: {"displayName": "Test User"}
        )
        
        with JIRAIntegration(jira_config) as jira:
            assert jira is not None
        
        # Connection test should be called on entry
        assert mock_session.get.called


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
