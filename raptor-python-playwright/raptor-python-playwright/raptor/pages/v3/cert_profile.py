"""
V3 Certificate Profile Page Object for RAPTOR Python Playwright Framework.

This module provides the page object for the V3 Certificate Profile module,
including certificate management, profile configuration, and validation operations.
"""

from typing import Optional, Dict, List, Any
from playwright.async_api import Page
from raptor.pages.base_page import BasePage
from raptor.core.element_manager import ElementManager
from raptor.core.config_manager import ConfigManager
from raptor.core.exceptions import RaptorException
from raptor.pages.table_manager import TableManager
import logging

logger = logging.getLogger(__name__)


class CertProfile(BasePage):
    """
    Page Object for V3 Certificate Profile Module.
    
    This class provides methods to interact with the Certificate Profile module,
    including:
    - Creating and managing certificate profiles
    - Configuring certificate parameters
    - Uploading and validating certificates
    - Managing certificate expiration
    - Assigning certificates to entities
    - Viewing certificate history
    
    Example:
        >>> cert_profile = CertProfile(page, element_manager)
        >>> await cert_profile.navigate_to_cert_profile()
        >>> await cert_profile.create_certificate_profile({
        ...     "name": "SSL Certificate",
        ...     "type": "TLS",
        ...     "validity_days": "365"
        ... })
        >>> await cert_profile.upload_certificate("SSL Certificate", "/path/to/cert.pem")
    """

    def __init__(
        self,
        page: Page,
        element_manager: Optional[ElementManager] = None,
        config: Optional[ConfigManager] = None,
    ):
        """
        Initialize the Certificate Profile Page.

        Args:
            page: Playwright Page instance
            element_manager: Optional ElementManager instance
            config: Optional ConfigManager instance
        """
        super().__init__(page, element_manager, config)
        
        # Initialize table manager for certificate grid
        self.table_manager = TableManager(page, self.element_manager)
        
        # Define locators for certificate profile elements
        self.locators = {
            # Page elements
            "page_title": "css=.page-title",
            "cert_grid": "css=#cert-grid",
            "cert_details_panel": "css=#cert-details-panel",
            
            # Search elements
            "search_box": "css=#cert-search",
            "search_button": "css=#search-button",
            "clear_search_button": "css=#clear-search",
            "filter_dropdown": "css=#cert-filter",
            "status_filter": "css=#status-filter",
            
            # Action buttons
            "create_cert_button": "css=#create-cert-button",
            "edit_cert_button": "css=#edit-cert-button",
            "delete_cert_button": "css=#delete-cert-button",
            "upload_cert_button": "css=#upload-cert-button",
            "download_cert_button": "css=#download-cert-button",
            "validate_cert_button": "css=#validate-cert-button",
            "renew_cert_button": "css=#renew-cert-button",
            "refresh_button": "css=#refresh-button",
            
            # Certificate form elements
            "cert_form": "css=#cert-form",
            "cert_name_field": "css=#cert-name",
            "cert_type_dropdown": "css=#cert-type",
            "cert_description_field": "css=#cert-description",
            "validity_days_field": "css=#validity-days",
            "issuer_field": "css=#issuer",
            "subject_field": "css=#subject",
            "key_size_dropdown": "css=#key-size",
            "algorithm_dropdown": "css=#algorithm",
            
            # Upload elements
            "upload_form": "css=#upload-form",
            "cert_file_input": "css=#cert-file-input",
            "key_file_input": "css=#key-file-input",
            "passphrase_field": "css=#passphrase",
            "upload_button": "css=#upload-button",
            
            # Certificate details
            "cert_status": "css=#cert-status",
            "cert_expiry_date": "css=#cert-expiry-date",
            "cert_issuer": "css=#cert-issuer",
            "cert_subject": "css=#cert-subject",
            "cert_serial_number": "css=#cert-serial-number",
            "cert_fingerprint": "css=#cert-fingerprint",
            
            # Form buttons
            "save_button": "css=#save-button",
            "cancel_button": "css=#cancel-button",
            "reset_button": "css=#reset-button",
            
            # Confirmation dialogs
            "confirm_dialog": "css=.confirm-dialog",
            "confirm_yes_button": "css=.confirm-yes",
            "confirm_no_button": "css=.confirm-no",
            
            # Status messages
            "success_message": "css=.success-message",
            "error_message": "css=.error-message",
            "warning_message": "css=.warning-message",
            "validation_result": "css=.validation-result",
            
            # Grid columns
            "grid_cert_name_column": "css=.grid-cert-name",
            "grid_cert_type_column": "css=.grid-cert-type",
            "grid_cert_status_column": "css=.grid-cert-status",
            "grid_cert_expiry_column": "css=.grid-cert-expiry",
            "grid_cert_issuer_column": "css=.grid-cert-issuer",
        }
        
        logger.info("V3 CertProfile page initialized")

    async def navigate_to_cert_profile(
        self,
        base_url: Optional[str] = None,
    ) -> None:
        """
        Navigate directly to the Certificate Profile page.
        
        Args:
            base_url: Optional base URL. If not provided, uses config.
            
        Raises:
            RaptorException: If navigation fails
            
        Example:
            >>> await cert_profile.navigate_to_cert_profile()
        """
        try:
            base = base_url or self.config.get("v3.base_url", "")
            url = f"{base}/cert-profile"
            
            logger.info(f"Navigating to Certificate Profile: {url}")
            await self.navigate(url)
            await self.wait_for_page_load()
            
            logger.info("Successfully navigated to Certificate Profile")
            
        except Exception as e:
            logger.error(f"Failed to navigate to Certificate Profile: {str(e)}")
            raise RaptorException(
                f"Failed to navigate to Certificate Profile: {str(e)}",
                context={"base_url": base_url},
                cause=e
            )

    async def wait_for_page_load(self, timeout: Optional[int] = None) -> None:
        """
        Wait for Certificate Profile page to fully load.
        
        Args:
            timeout: Optional timeout in milliseconds
            
        Raises:
            TimeoutException: If page doesn't load within timeout
        """
        try:
            logger.debug("Waiting for Certificate Profile page to load")
            
            await self.wait_for_load(state="load", timeout=timeout)
            
            # Wait for key elements
            await self.element_manager.wait_for_element(
                self.locators["page_title"],
                timeout=timeout or self.config.get_timeout("element")
            )
            
            await self.element_manager.wait_for_element(
                self.locators["cert_grid"],
                timeout=timeout or self.config.get_timeout("element")
            )
            
            logger.info("Certificate Profile page loaded successfully")
            
        except Exception as e:
            logger.error(f"Certificate Profile page load failed: {str(e)}")
            raise

    async def create_certificate_profile(self, cert_data: Dict[str, Any]) -> None:
        """
        Create a new certificate profile with the provided data.
        
        Args:
            cert_data: Dictionary containing certificate information:
                - name: Certificate profile name (required)
                - type: Certificate type (TLS, SSL, Code Signing, etc.)
                - description: Certificate description
                - validity_days: Validity period in days
                - issuer: Certificate issuer
                - subject: Certificate subject
                - key_size: Key size (2048, 4096, etc.)
                - algorithm: Encryption algorithm (RSA, ECC, etc.)
                
        Raises:
            RaptorException: If certificate creation fails
            
        Example:
            >>> await cert_profile.create_certificate_profile({
            ...     "name": "Production SSL",
            ...     "type": "TLS",
            ...     "validity_days": "730",
            ...     "key_size": "4096"
            ... })
        """
        try:
            logger.info(f"Creating certificate profile: {cert_data.get('name')}")
            
            # Click create certificate button
            await self.element_manager.click(self.locators["create_cert_button"])
            
            # Wait for form to appear
            await self.element_manager.wait_for_element(self.locators["cert_form"])
            
            # Fill in certificate data
            await self._fill_certificate_form(cert_data)
            
            # Click save button
            await self.element_manager.click(self.locators["save_button"])
            
            # Wait for success message
            await self._wait_for_success_message()
            
            logger.info(f"Certificate profile created successfully: {cert_data.get('name')}")
            
        except Exception as e:
            logger.error(f"Failed to create certificate profile: {str(e)}")
            raise RaptorException(
                f"Failed to create certificate profile: {str(e)}",
                context={"cert_data": cert_data},
                cause=e
            )

    async def edit_certificate_profile(
        self,
        cert_name: str,
        updated_data: Dict[str, Any],
    ) -> None:
        """
        Edit an existing certificate profile's information.
        
        Args:
            cert_name: Name of the certificate profile to edit
            updated_data: Dictionary containing fields to update
            
        Raises:
            RaptorException: If certificate edit fails
            
        Example:
            >>> await cert_profile.edit_certificate_profile("Production SSL", {
            ...     "description": "Updated description",
            ...     "validity_days": "1095"
            ... })
        """
        try:
            logger.info(f"Editing certificate profile: {cert_name}")
            
            # Search for and select the certificate
            await self.search_certificate(cert_name)
            await self._select_certificate_in_grid(cert_name)
            
            # Click edit button
            await self.element_manager.click(self.locators["edit_cert_button"])
            
            # Wait for form to appear
            await self.element_manager.wait_for_element(self.locators["cert_form"])
            
            # Fill in updated data
            await self._fill_certificate_form(updated_data)
            
            # Click save button
            await self.element_manager.click(self.locators["save_button"])
            
            # Wait for success message
            await self._wait_for_success_message()
            
            logger.info(f"Certificate profile edited successfully: {cert_name}")
            
        except Exception as e:
            logger.error(f"Failed to edit certificate profile: {str(e)}")
            raise RaptorException(
                f"Failed to edit certificate profile: {str(e)}",
                context={"cert_name": cert_name, "updated_data": updated_data},
                cause=e
            )

    async def delete_certificate_profile(
        self,
        cert_name: str,
        confirm: bool = True,
    ) -> None:
        """
        Delete a certificate profile from the system.
        
        Args:
            cert_name: Name of the certificate profile to delete
            confirm: Whether to confirm the deletion (default: True)
            
        Raises:
            RaptorException: If certificate deletion fails
            
        Example:
            >>> await cert_profile.delete_certificate_profile("Old Certificate")
        """
        try:
            logger.info(f"Deleting certificate profile: {cert_name}")
            
            # Search for and select the certificate
            await self.search_certificate(cert_name)
            await self._select_certificate_in_grid(cert_name)
            
            # Click delete button
            await self.element_manager.click(self.locators["delete_cert_button"])
            
            # Wait for confirmation dialog
            await self.element_manager.wait_for_element(
                self.locators["confirm_dialog"]
            )
            
            # Confirm or cancel deletion
            if confirm:
                await self.element_manager.click(self.locators["confirm_yes_button"])
                await self._wait_for_success_message()
                logger.info(f"Certificate profile deleted successfully: {cert_name}")
            else:
                await self.element_manager.click(self.locators["confirm_no_button"])
                logger.info(f"Certificate deletion cancelled: {cert_name}")
            
        except Exception as e:
            logger.error(f"Failed to delete certificate profile: {str(e)}")
            raise RaptorException(
                f"Failed to delete certificate profile: {str(e)}",
                context={"cert_name": cert_name},
                cause=e
            )

    async def upload_certificate(
        self,
        cert_name: str,
        cert_file_path: str,
        key_file_path: Optional[str] = None,
        passphrase: Optional[str] = None,
    ) -> None:
        """
        Upload a certificate file to a certificate profile.
        
        Args:
            cert_name: Name of the certificate profile
            cert_file_path: Path to the certificate file (.pem, .crt, etc.)
            key_file_path: Optional path to the private key file
            passphrase: Optional passphrase for encrypted key
            
        Raises:
            RaptorException: If certificate upload fails
            
        Example:
            >>> await cert_profile.upload_certificate(
            ...     "Production SSL",
            ...     "/path/to/cert.pem",
            ...     "/path/to/key.pem",
            ...     "secret_passphrase"
            ... )
        """
        try:
            logger.info(f"Uploading certificate to profile: {cert_name}")
            
            # Search for and select the certificate profile
            await self.search_certificate(cert_name)
            await self._select_certificate_in_grid(cert_name)
            
            # Click upload button
            await self.element_manager.click(self.locators["upload_cert_button"])
            
            # Wait for upload form
            await self.element_manager.wait_for_element(self.locators["upload_form"])
            
            # Upload certificate file
            await self.page.set_input_files(
                self.locators["cert_file_input"],
                cert_file_path
            )
            
            # Upload key file if provided
            if key_file_path:
                await self.page.set_input_files(
                    self.locators["key_file_input"],
                    key_file_path
                )
            
            # Enter passphrase if provided
            if passphrase:
                await self.element_manager.fill(
                    self.locators["passphrase_field"],
                    passphrase
                )
            
            # Click upload button
            await self.element_manager.click(self.locators["upload_button"])
            
            # Wait for success message
            await self._wait_for_success_message()
            
            logger.info(f"Certificate uploaded successfully to: {cert_name}")
            
        except Exception as e:
            logger.error(f"Failed to upload certificate: {str(e)}")
            raise RaptorException(
                f"Failed to upload certificate: {str(e)}",
                context={"cert_name": cert_name, "cert_file_path": cert_file_path},
                cause=e
            )

    async def validate_certificate(self, cert_name: str) -> Dict[str, Any]:
        """
        Validate a certificate and return validation results.
        
        Args:
            cert_name: Name of the certificate profile to validate
            
        Returns:
            Dictionary containing validation results:
                - is_valid: Boolean indicating if certificate is valid
                - expiry_date: Certificate expiration date
                - days_until_expiry: Days until certificate expires
                - validation_errors: List of validation errors if any
                
        Raises:
            RaptorException: If validation fails
            
        Example:
            >>> result = await cert_profile.validate_certificate("Production SSL")
            >>> if result["is_valid"]:
            ...     print(f"Certificate expires in {result['days_until_expiry']} days")
        """
        try:
            logger.info(f"Validating certificate: {cert_name}")
            
            # Search for and select the certificate
            await self.search_certificate(cert_name)
            await self._select_certificate_in_grid(cert_name)
            
            # Click validate button
            await self.element_manager.click(self.locators["validate_cert_button"])
            
            # Wait for validation result
            await self.element_manager.wait_for_element(
                self.locators["validation_result"]
            )
            
            # Extract validation results
            # Note: This is a simplified example - actual implementation
            # would parse the validation result element
            result_text = await self.element_manager.get_text(
                self.locators["validation_result"]
            )
            
            # Parse result (simplified)
            result = {
                "is_valid": "valid" in result_text.lower(),
                "result_text": result_text,
            }
            
            logger.info(f"Certificate validation completed: {cert_name}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to validate certificate: {str(e)}")
            raise RaptorException(
                f"Failed to validate certificate: {str(e)}",
                context={"cert_name": cert_name},
                cause=e
            )

    async def search_certificate(self, search_term: str) -> None:
        """
        Search for certificates using the search box.
        
        Args:
            search_term: Search term (certificate name, issuer, etc.)
            
        Raises:
            RaptorException: If search fails
            
        Example:
            >>> await cert_profile.search_certificate("SSL")
        """
        try:
            logger.info(f"Searching for certificate: {search_term}")
            
            # Clear existing search
            await self.element_manager.fill(self.locators["search_box"], "")
            
            # Enter search term
            await self.element_manager.fill(
                self.locators["search_box"],
                search_term
            )
            
            # Click search button
            await self.element_manager.click(self.locators["search_button"])
            
            # Wait for grid to update
            await self.page.wait_for_timeout(1000)
            
            logger.info(f"Search completed for: {search_term}")
            
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            raise RaptorException(
                f"Failed to search for certificate: {str(e)}",
                context={"search_term": search_term},
                cause=e
            )

    async def get_certificate_details(self, cert_name: str) -> Dict[str, str]:
        """
        Get details of a certificate from the grid.
        
        Args:
            cert_name: Certificate name to retrieve details for
            
        Returns:
            Dictionary containing certificate details from the grid
            
        Raises:
            RaptorException: If unable to retrieve certificate details
            
        Example:
            >>> details = await cert_profile.get_certificate_details("Production SSL")
            >>> print(details["status"])
        """
        try:
            logger.info(f"Getting details for certificate: {cert_name}")
            
            # Search for the certificate
            await self.search_certificate(cert_name)
            
            # Find the row in the grid
            row_index = await self.table_manager.find_row_by_key(
                self.locators["cert_grid"],
                key_column=0,
                key_value=cert_name
            )
            
            if row_index == -1:
                raise RaptorException(
                    f"Certificate not found in grid: {cert_name}",
                    context={"cert_name": cert_name}
                )
            
            # Extract certificate details from the row
            details = {
                "name": await self.table_manager.get_cell_value(
                    self.locators["cert_grid"],
                    row_index,
                    0
                ),
                "type": await self.table_manager.get_cell_value(
                    self.locators["cert_grid"],
                    row_index,
                    1
                ),
                "status": await self.table_manager.get_cell_value(
                    self.locators["cert_grid"],
                    row_index,
                    2
                ),
                "expiry": await self.table_manager.get_cell_value(
                    self.locators["cert_grid"],
                    row_index,
                    3
                ),
            }
            
            logger.info(f"Retrieved details for certificate: {cert_name}")
            return details
            
        except Exception as e:
            logger.error(f"Failed to get certificate details: {str(e)}")
            raise RaptorException(
                f"Failed to get certificate details: {str(e)}",
                context={"cert_name": cert_name},
                cause=e
            )

    async def download_certificate(
        self,
        cert_name: str,
        download_path: Optional[str] = None,
    ) -> str:
        """
        Download a certificate file.
        
        Args:
            cert_name: Name of the certificate to download
            download_path: Optional path to save the downloaded file
            
        Returns:
            Path to the downloaded certificate file
            
        Raises:
            RaptorException: If download fails
            
        Example:
            >>> file_path = await cert_profile.download_certificate("Production SSL")
            >>> print(f"Certificate downloaded to: {file_path}")
        """
        try:
            logger.info(f"Downloading certificate: {cert_name}")
            
            # Search for and select the certificate
            await self.search_certificate(cert_name)
            await self._select_certificate_in_grid(cert_name)
            
            # Start waiting for download
            async with self.page.expect_download() as download_info:
                # Click download button
                await self.element_manager.click(self.locators["download_cert_button"])
            
            download = await download_info.value
            
            # Save to specified path or use suggested filename
            if download_path:
                await download.save_as(download_path)
                saved_path = download_path
            else:
                saved_path = await download.path()
            
            logger.info(f"Certificate downloaded successfully: {saved_path}")
            return saved_path
            
        except Exception as e:
            logger.error(f"Failed to download certificate: {str(e)}")
            raise RaptorException(
                f"Failed to download certificate: {str(e)}",
                context={"cert_name": cert_name},
                cause=e
            )

    async def _fill_certificate_form(self, cert_data: Dict[str, Any]) -> None:
        """
        Fill in the certificate form with provided data.
        
        Args:
            cert_data: Dictionary containing certificate information
            
        Raises:
            RaptorException: If form filling fails
        """
        try:
            logger.debug("Filling certificate form")
            
            if "name" in cert_data:
                await self.element_manager.fill(
                    self.locators["cert_name_field"],
                    cert_data["name"]
                )
            
            if "type" in cert_data:
                await self.element_manager.select_option(
                    self.locators["cert_type_dropdown"],
                    cert_data["type"]
                )
            
            if "description" in cert_data:
                await self.element_manager.fill(
                    self.locators["cert_description_field"],
                    cert_data["description"]
                )
            
            if "validity_days" in cert_data:
                await self.element_manager.fill(
                    self.locators["validity_days_field"],
                    cert_data["validity_days"]
                )
            
            if "issuer" in cert_data:
                await self.element_manager.fill(
                    self.locators["issuer_field"],
                    cert_data["issuer"]
                )
            
            if "subject" in cert_data:
                await self.element_manager.fill(
                    self.locators["subject_field"],
                    cert_data["subject"]
                )
            
            if "key_size" in cert_data:
                await self.element_manager.select_option(
                    self.locators["key_size_dropdown"],
                    cert_data["key_size"]
                )
            
            if "algorithm" in cert_data:
                await self.element_manager.select_option(
                    self.locators["algorithm_dropdown"],
                    cert_data["algorithm"]
                )
            
            logger.debug("Certificate form filled successfully")
            
        except Exception as e:
            logger.error(f"Failed to fill certificate form: {str(e)}")
            raise

    async def _select_certificate_in_grid(self, cert_name: str) -> None:
        """
        Select a certificate row in the grid by name.
        
        Args:
            cert_name: Certificate name to select
            
        Raises:
            RaptorException: If certificate selection fails
        """
        try:
            logger.debug(f"Selecting certificate in grid: {cert_name}")
            
            row_index = await self.table_manager.find_row_by_key(
                self.locators["cert_grid"],
                key_column=0,
                key_value=cert_name
            )
            
            if row_index == -1:
                raise RaptorException(
                    f"Certificate not found in grid: {cert_name}",
                    context={"cert_name": cert_name}
                )
            
            await self.table_manager.click_cell(
                self.locators["cert_grid"],
                row_index,
                0
            )
            
            logger.debug(f"Certificate selected: {cert_name}")
            
        except Exception as e:
            logger.error(f"Failed to select certificate in grid: {str(e)}")
            raise

    async def _wait_for_success_message(self, timeout: Optional[int] = None) -> None:
        """
        Wait for success message to appear after an operation.
        
        Args:
            timeout: Optional timeout in milliseconds
            
        Raises:
            TimeoutException: If success message doesn't appear
        """
        try:
            logger.debug("Waiting for success message")
            
            await self.element_manager.wait_for_element(
                self.locators["success_message"],
                timeout=timeout or 5000
            )
            
            message = await self.element_manager.get_text(
                self.locators["success_message"]
            )
            
            logger.info(f"Success message: {message}")
            
        except Exception as e:
            logger.error(f"Success message not found: {str(e)}")
            raise
