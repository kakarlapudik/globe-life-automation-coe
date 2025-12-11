"""
Unit tests for ALM Integration

Tests the ALM integration functionality including:
- Authentication
- Publishing test results
- Updating test status
- Uploading attachments
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from raptor.integrations.alm_integration import (
    ALMIntegration,
    ALMConfig,
    ALMTestStatus,
    ALMIntegrationException
)


@pytest.fixture
def alm_config():
    """Create a test ALM configuration."""
    return ALMConfig(
        server_url="http://alm-test.example.com/qcbin",
        username="test_user",
        password="test_password",
        domain="TEST_DOMAIN",
        project="TEST_PROJECT",
        verify_ssl=False
    )


@pytest.fixture
def mock_session():
    """Create a mock requests session."""
    with patch('raptor.integrations.alm_integration.requests.Session') as mock:
        session = MagicMock()
        mock.return_value = session
        yield session


class TestALMIntegration:
    """Test suite for ALM integration."""
    
    def test_initialization(self, alm_config):
        """Test ALM integration initialization."""
        alm = ALMIntegration(alm_config)
        
        assert alm.config == alm_config
        assert not alm._authenticated
    
    def test_authentication_success(self, alm_config, mock_session):
        """Test successful authentication."""
        # Mock authentication responses
        mock_session.get.side_effect = [
            Mock(status_code=401),  # Not authenticated
            Mock(status_code=200),  # Authentication successful
        ]
        mock_session.post.return_value = Mock(status_code=201)  # Session created
        
        alm = ALMIntegration(alm_config)
        result = alm.authenticate()
        
        assert result is True
        assert alm._authenticated is True
    
    def test_authentication_already_authenticated(self, alm_config, mock_session):
        """Test authentication when already authenticated."""
        mock_session.get.return_value = Mock(status_code=200)
        
        alm = ALMIntegration(alm_config)
        result = alm.authenticate()
        
        assert result is True
        assert alm._authenticated is True
    
    def test_authentication_failure(self, alm_config, mock_session):
        """Test authentication failure."""
        mock_session.get.side_effect = [
            Mock(status_code=401),
            Mock(status_code=401, text="Authentication failed")
        ]
        
        alm = ALMIntegration(alm_config)
        
        with pytest.raises(ALMIntegrationException):
            alm.authenticate()
    
    def test_publish_test_result(self, alm_config, mock_session):
        """Test publishing test result to ALM."""
        mock_session.post.return_value = Mock(
            status_code=201,
            json=lambda: {
                "Fields": {
                    "Field": [
                        {"Name": "id", "Value": "12345"}
                    ]
                }
            }
        )
        
        alm = ALMIntegration(alm_config)
        alm._authenticated = True
        
        result = alm.publish_test_result(
            test_id="TEST-001",
            test_set_id="SET-001",
            status=ALMTestStatus.PASSED,
            execution_time=10.5,
            comments="Test passed successfully"
        )
        
        assert result is not None
        assert mock_session.post.called
    
    def test_publish_test_result_auto_authenticate(self, alm_config, mock_session):
        """Test that publish_test_result authenticates if needed."""
        mock_session.get.return_value = Mock(status_code=200)
        mock_session.post.return_value = Mock(
            status_code=201,
            json=lambda: {"Fields": {"Field": [{"Name": "id", "Value": "12345"}]}}
        )
        
        alm = ALMIntegration(alm_config)
        
        result = alm.publish_test_result(
            test_id="TEST-001",
            test_set_id="SET-001",
            status=ALMTestStatus.FAILED
        )
        
        assert alm._authenticated is True
        assert result is not None
    
    def test_update_test_status(self, alm_config, mock_session):
        """Test updating test status in ALM."""
        mock_session.put.return_value = Mock(
            status_code=200,
            json=lambda: {"success": True}
        )
        
        alm = ALMIntegration(alm_config)
        alm._authenticated = True
        
        result = alm.update_test_status(
            run_id="RUN-001",
            status=ALMTestStatus.PASSED,
            comments="Test completed"
        )
        
        assert result is not None
        assert mock_session.put.called
    
    def test_upload_attachment(self, alm_config, mock_session, tmp_path):
        """Test uploading attachment to ALM."""
        # Create a temporary file
        test_file = tmp_path / "screenshot.png"
        test_file.write_bytes(b"fake image data")
        
        mock_session.post.return_value = Mock(
            status_code=201,
            json=lambda: {
                "Fields": {
                    "Field": [
                        {"Name": "id", "Value": "ATT-001"}
                    ]
                }
            }
        )
        mock_session.put.return_value = Mock(status_code=200)
        
        alm = ALMIntegration(alm_config)
        alm._authenticated = True
        
        result = alm.upload_attachment(
            run_id="RUN-001",
            file_path=str(test_file),
            description="Test screenshot"
        )
        
        assert result is not None
        assert mock_session.post.called
        assert mock_session.put.called
    
    def test_upload_attachment_file_not_found(self, alm_config):
        """Test uploading attachment with non-existent file."""
        alm = ALMIntegration(alm_config)
        alm._authenticated = True
        
        with pytest.raises(ALMIntegrationException, match="File not found"):
            alm.upload_attachment(
                run_id="RUN-001",
                file_path="/nonexistent/file.png"
            )
    
    def test_upload_multiple_attachments(self, alm_config, mock_session, tmp_path):
        """Test uploading multiple attachments."""
        # Create temporary files
        file1 = tmp_path / "screenshot1.png"
        file1.write_bytes(b"image 1")
        file2 = tmp_path / "screenshot2.png"
        file2.write_bytes(b"image 2")
        
        mock_session.post.return_value = Mock(
            status_code=201,
            json=lambda: {"Fields": {"Field": [{"Name": "id", "Value": "ATT-001"}]}}
        )
        mock_session.put.return_value = Mock(status_code=200)
        
        alm = ALMIntegration(alm_config)
        alm._authenticated = True
        
        results = alm.upload_multiple_attachments(
            run_id="RUN-001",
            file_paths=[str(file1), str(file2)]
        )
        
        assert len(results) == 2
    
    def test_link_to_requirement(self, alm_config, mock_session):
        """Test linking test to requirement."""
        mock_session.post.return_value = Mock(
            status_code=201,
            json=lambda: {"success": True}
        )
        
        alm = ALMIntegration(alm_config)
        alm._authenticated = True
        
        result = alm.link_to_requirement(
            test_id="TEST-001",
            requirement_id="REQ-001"
        )
        
        assert result is not None
        assert mock_session.post.called
    
    def test_logout(self, alm_config, mock_session):
        """Test logout from ALM."""
        mock_session.get.return_value = Mock(status_code=200)
        
        alm = ALMIntegration(alm_config)
        alm._authenticated = True
        
        alm.logout()
        
        assert alm._authenticated is False
        assert mock_session.get.called
    
    def test_context_manager(self, alm_config, mock_session):
        """Test using ALM integration as context manager."""
        mock_session.get.return_value = Mock(status_code=200)
        mock_session.post.return_value = Mock(status_code=201)
        
        with ALMIntegration(alm_config) as alm:
            assert alm._authenticated is True
        
        # Logout should be called on exit
        assert mock_session.get.called


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
