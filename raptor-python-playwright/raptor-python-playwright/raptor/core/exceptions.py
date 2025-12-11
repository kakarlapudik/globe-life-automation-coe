"""
Custom exceptions for the RAPTOR Python Playwright framework.

This module defines a hierarchy of exceptions that provide detailed
error information for different failure scenarios in the framework.
"""

from typing import Optional, Dict, Any
import traceback
from datetime import datetime


class RaptorException(Exception):
    """
    Base exception for all RAPTOR framework errors.
    
    Provides common functionality for error context preservation,
    stack trace capture, and detailed error reporting.
    """

    def __init__(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ):
        """
        Initialize a RAPTOR exception.

        Args:
            message: Human-readable error description
            context: Additional context information (locators, timeouts, etc.)
            cause: The underlying exception that caused this error
        """
        super().__init__(message)
        self.message = message
        self.context = context or {}
        self.cause = cause
        self.timestamp = datetime.now()
        self.stack_trace = traceback.format_exc()

    def __str__(self) -> str:
        """Return a detailed string representation of the error."""
        error_parts = [f"{self.__class__.__name__}: {self.message}"]

        if self.context:
            error_parts.append(f"Context: {self.context}")

        if self.cause:
            error_parts.append(f"Caused by: {self.cause}")

        error_parts.append(f"Timestamp: {self.timestamp}")

        return "\n".join(error_parts)

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging/reporting."""
        return {
            "type": self.__class__.__name__,
            "message": self.message,
            "context": self.context,
            "cause": str(self.cause) if self.cause else None,
            "timestamp": self.timestamp.isoformat(),
            "stack_trace": self.stack_trace,
        }


class ElementNotFoundException(RaptorException):
    """
    Raised when an element cannot be located using any available strategy.
    
    This exception is thrown when all locator strategies (primary and fallbacks)
    fail to find the target element within the specified timeout.
    """

    def __init__(
        self,
        locator: str,
        fallback_locators: Optional[list] = None,
        timeout: Optional[int] = None,
        page_url: Optional[str] = None,
    ):
        context = {
            "primary_locator": locator,
            "fallback_locators": fallback_locators or [],
            "timeout_seconds": timeout,
            "page_url": page_url,
        }
        message = f"Element not found using locator: {locator}"
        if fallback_locators:
            message += f" (tried {len(fallback_locators)} fallback strategies)"
        super().__init__(message, context)


class ElementNotInteractableException(RaptorException):
    """
    Raised when an element exists but cannot be interacted with.
    
    This occurs when an element is found but is disabled, hidden,
    covered by another element, or otherwise not in an interactable state.
    """

    def __init__(
        self, locator: str, action: str, element_state: Optional[Dict[str, Any]] = None
    ):
        context = {
            "locator": locator,
            "attempted_action": action,
            "element_state": element_state or {},
        }
        message = f"Element not interactable for action '{action}': {locator}"
        super().__init__(message, context)


class TimeoutException(RaptorException):
    """
    Raised when an operation exceeds the specified timeout.
    
    This exception provides details about what operation timed out
    and the timeout value that was exceeded.
    """

    def __init__(
        self,
        operation: str,
        timeout_seconds: int,
        additional_info: Optional[Dict[str, Any]] = None,
    ):
        context = {
            "operation": operation,
            "timeout_seconds": timeout_seconds,
            **(additional_info or {}),
        }
        message = f"Operation '{operation}' timed out after {timeout_seconds} seconds"
        super().__init__(message, context)


class DatabaseException(RaptorException):
    """
    Raised for database-related errors.
    
    This includes connection failures, SQL errors, data validation issues,
    and other database operation problems.
    """

    def __init__(
        self,
        operation: str,
        sql_query: Optional[str] = None,
        database_error: Optional[Exception] = None,
    ):
        context = {
            "database_operation": operation,
            "sql_query": sql_query,
            "database_error_type": (
                type(database_error).__name__ if database_error else None
            ),
        }
        message = f"Database operation failed: {operation}"
        if database_error:
            message += f" - {str(database_error)}"
        super().__init__(message, context, database_error)


class SessionException(RaptorException):
    """
    Raised for session management errors.
    
    This includes session save/restore failures, invalid session data,
    and session connectivity issues.
    """

    def __init__(
        self,
        operation: str,
        session_id: Optional[str] = None,
        session_info: Optional[Dict[str, Any]] = None,
    ):
        context = {
            "session_operation": operation,
            "session_id": session_id,
            "session_info": session_info or {},
        }
        message = f"Session operation failed: {operation}"
        if session_id:
            message += f" (Session ID: {session_id})"
        super().__init__(message, context)


class ConfigurationException(RaptorException):
    """
    Raised for configuration-related errors.
    
    This includes missing configuration files, invalid configuration values,
    environment setup issues, and configuration validation failures.
    """

    def __init__(
        self,
        config_issue: str,
        config_file: Optional[str] = None,
        config_key: Optional[str] = None,
        expected_value: Optional[str] = None,
    ):
        context = {
            "config_issue": config_issue,
            "config_file": config_file,
            "config_key": config_key,
            "expected_value": expected_value,
        }
        message = f"Configuration error: {config_issue}"
        if config_file:
            message += f" in file '{config_file}'"
        if config_key:
            message += f" for key '{config_key}'"
        super().__init__(message, context)


# Utility functions for exception handling


def capture_element_context(page, locator: str) -> Dict[str, Any]:
    """
    Capture context information about an element for error reporting.

    Args:
        page: Playwright page object
        locator: Element locator string

    Returns:
        Dictionary containing element context information
    """
    try:
        return {
            "page_url": page.url,
            "page_title": page.title(),
            "locator": locator,
            "viewport_size": page.viewport_size,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception:
        # If we can't capture context, return minimal info
        return {
            "locator": locator,
            "timestamp": datetime.now().isoformat(),
            "context_capture_failed": True,
        }


def handle_playwright_error(
    error: Exception, context: Dict[str, Any]
) -> RaptorException:
    """
    Convert Playwright errors to appropriate RAPTOR exceptions.

    Args:
        error: The original Playwright exception
        context: Additional context information

    Returns:
        Appropriate RAPTOR exception with preserved context
    """
    error_message = str(error).lower()

    if "timeout" in error_message:
        return TimeoutException(
            operation=context.get("operation", "unknown"),
            timeout_seconds=context.get("timeout", 30),
            additional_info=context,
        )
    elif "not found" in error_message or "no such element" in error_message:
        return ElementNotFoundException(
            locator=context.get("locator", "unknown"),
            timeout=context.get("timeout"),
            page_url=context.get("page_url"),
        )
    elif "not interactable" in error_message or "not clickable" in error_message:
        return ElementNotInteractableException(
            locator=context.get("locator", "unknown"),
            action=context.get("action", "unknown"),
        )
    else:
        # Generic RAPTOR exception for other Playwright errors
        return RaptorException(
            message=f"Playwright error: {str(error)}", context=context, cause=error
        )
