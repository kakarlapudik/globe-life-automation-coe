"""
Property-Based Test: Error Context Preservation

**Feature: raptor-playwright-python, Property 11: Error Context Preservation**
**Validates: Requirements 11.1**

This test verifies that errors and exceptions preserve full stack trace and
context information for debugging.

Property Statement:
    For any error or exception, the system should preserve the full stack trace 
    and context information for debugging.
"""

import pytest
import traceback
import sys
from hypothesis import given, strategies as st, settings, assume
from typing import Dict, Any, List, Optional
from unittest.mock import AsyncMock, MagicMock


# Strategy for error messages
error_message_strategy = st.text(min_size=10, max_size=200)

# Strategy for error types
error_type_strategy = st.sampled_from([
    'ElementNotFoundException',
    'TimeoutException',
    'DatabaseException',
    'SessionException',
    'ConfigurationException'
])

# Strategy for context data
context_data_strategy = st.dictionaries(
    keys=st.text(
        alphabet=st.characters(whitelist_categories=('Lu', 'Ll'), whitelist_characters='_'),
        min_size=3,
        max_size=20
    ),
    values=st.one_of(
        st.text(max_size=50),
        st.integers(),
        st.booleans()
    ),
    min_size=1,
    max_size=10
)


class RaptorException(Exception):
    """Base exception with context preservation."""
    
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.context = context or {}
        # Capture stack trace from the current exception context
        self.stack_trace = ''.join(traceback.format_stack())
        self.exception_type = self.__class__.__name__
    
    def get_context(self) -> Dict[str, Any]:
        """Get error context."""
        return self.context.copy()
    
    def get_full_context(self) -> Dict[str, Any]:
        """Get full error context including stack trace."""
        return {
            'message': self.message,
            'exception_type': self.exception_type,
            'context': self.context,
            'stack_trace': self.stack_trace
        }


class ElementNotFoundException(RaptorException):
    """Exception for element not found errors."""
    pass


class TimeoutException(RaptorException):
    """Exception for timeout errors."""
    pass


class DatabaseException(RaptorException):
    """Exception for database errors."""
    pass


class SessionException(RaptorException):
    """Exception for session management errors."""
    pass


class ConfigurationException(RaptorException):
    """Exception for configuration errors."""
    pass


class ErrorHandler:
    """
    Handler for errors that preserves context.
    
    This simulates error handling in the framework.
    """
    
    def __init__(self):
        self.captured_errors = []
    
    def raise_error(
        self,
        error_type: str,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Raise an error with context preservation.
        
        Args:
            error_type: Type of error to raise
            message: Error message
            context: Additional context information
        """
        exception_class = {
            'ElementNotFoundException': ElementNotFoundException,
            'TimeoutException': TimeoutException,
            'DatabaseException': DatabaseException,
            'SessionException': SessionException,
            'ConfigurationException': ConfigurationException
        }.get(error_type, RaptorException)
        
        raise exception_class(message, context)
    
    def capture_error(self, exception: Exception):
        """Capture an error for analysis."""
        if isinstance(exception, RaptorException):
            self.captured_errors.append(exception.get_full_context())
        else:
            self.captured_errors.append({
                'message': str(exception),
                'exception_type': type(exception).__name__,
                'stack_trace': traceback.format_exc()
            })
    
    def get_captured_errors(self) -> List[Dict[str, Any]]:
        """Get all captured errors."""
        return self.captured_errors.copy()


class TestErrorContextPreservation:
    """
    Property-based tests for error context preservation.
    
    These tests verify that errors preserve full stack trace and context
    information for debugging.
    """
    
    @given(
        error_type=error_type_strategy,
        message=error_message_strategy,
        context=context_data_strategy
    )
    @settings(max_examples=100, deadline=5000)
    def test_error_preserves_message(self, error_type, message, context):
        """
        Property: Errors should preserve the original error message.
        
        When an error is raised, the error message should be preserved
        and accessible.
        
        Args:
            error_type: Type of error to raise
            message: Error message
            context: Error context
        """
        error_handler = ErrorHandler()
        
        try:
            error_handler.raise_error(error_type, message, context)
        except RaptorException as e:
            # Property: Message is preserved
            assert e.message == message, (
                f"Error message should be preserved: expected '{message}', "
                f"got '{e.message}'"
            )
            
            # Property: Message is in string representation
            assert message in str(e)
    
    @given(
        error_type=error_type_strategy,
        message=error_message_strategy,
        context=context_data_strategy
    )
    @settings(max_examples=100, deadline=5000)
    def test_error_preserves_context(self, error_type, message, context):
        """
        Property: Errors should preserve context information.
        
        When an error is raised with context, all context information
        should be preserved and accessible.
        
        Args:
            error_type: Type of error to raise
            message: Error message
            context: Error context
        """
        error_handler = ErrorHandler()
        
        try:
            error_handler.raise_error(error_type, message, context)
        except RaptorException as e:
            # Property: Context is preserved
            error_context = e.get_context()
            assert error_context == context, (
                f"Error context should be preserved"
            )
            
            # Property: All context keys are present
            for key in context.keys():
                assert key in error_context, (
                    f"Context key '{key}' should be preserved"
                )
            
            # Property: All context values are correct
            for key, value in context.items():
                assert error_context[key] == value, (
                    f"Context value for '{key}' should be preserved"
                )
    
    @given(
        error_type=error_type_strategy,
        message=error_message_strategy,
        context=context_data_strategy
    )
    @settings(max_examples=100, deadline=5000)
    def test_error_preserves_stack_trace(self, error_type, message, context):
        """
        Property: Errors should preserve stack trace information.
        
        When an error is raised, the full stack trace should be preserved
        for debugging.
        
        Args:
            error_type: Type of error to raise
            message: Error message
            context: Error context
        """
        error_handler = ErrorHandler()
        
        try:
            error_handler.raise_error(error_type, message, context)
        except RaptorException as e:
            # Property: Stack trace is preserved
            assert e.stack_trace is not None, (
                "Stack trace should be preserved"
            )
            
            # Property: Stack trace is a string
            assert isinstance(e.stack_trace, str), (
                "Stack trace should be a string"
            )
            
            # Property: Stack trace contains function name
            assert 'raise_error' in e.stack_trace, (
                "Stack trace should contain function name"
            )
    
    @given(
        error_type=error_type_strategy,
        message=error_message_strategy,
        context=context_data_strategy
    )
    @settings(max_examples=100, deadline=5000)
    def test_error_preserves_exception_type(self, error_type, message, context):
        """
        Property: Errors should preserve exception type information.
        
        When an error is raised, the exception type should be preserved
        and accessible.
        
        Args:
            error_type: Type of error to raise
            message: Error message
            context: Error context
        """
        error_handler = ErrorHandler()
        
        try:
            error_handler.raise_error(error_type, message, context)
        except RaptorException as e:
            # Property: Exception type is preserved
            assert e.exception_type == error_type, (
                f"Exception type should be preserved: expected '{error_type}', "
                f"got '{e.exception_type}'"
            )
            
            # Property: Exception type matches class name
            assert e.exception_type == e.__class__.__name__
    
    @given(
        error_type=error_type_strategy,
        message=error_message_strategy,
        context=context_data_strategy
    )
    @settings(max_examples=100, deadline=5000)
    def test_error_full_context_includes_all_info(
        self, error_type, message, context
    ):
        """
        Property: Full error context should include all information.
        
        The full error context should include message, type, context,
        and stack trace.
        
        Args:
            error_type: Type of error to raise
            message: Error message
            context: Error context
        """
        error_handler = ErrorHandler()
        
        try:
            error_handler.raise_error(error_type, message, context)
        except RaptorException as e:
            full_context = e.get_full_context()
            
            # Property: Full context contains all required keys
            required_keys = ['message', 'exception_type', 'context', 'stack_trace']
            for key in required_keys:
                assert key in full_context, (
                    f"Full context should contain '{key}'"
                )
            
            # Property: Values match original
            assert full_context['message'] == message
            assert full_context['exception_type'] == error_type
            assert full_context['context'] == context
            assert full_context['stack_trace'] is not None
    
    @given(
        error_type=error_type_strategy,
        message=error_message_strategy,
        context=context_data_strategy
    )
    @settings(max_examples=100, deadline=5000)
    def test_captured_errors_preserve_context(
        self, error_type, message, context
    ):
        """
        Property: Captured errors should preserve all context.
        
        When errors are captured for logging/reporting, all context
        information should be preserved.
        
        Args:
            error_type: Type of error to raise
            message: Error message
            context: Error context
        """
        error_handler = ErrorHandler()
        
        try:
            error_handler.raise_error(error_type, message, context)
        except RaptorException as e:
            error_handler.capture_error(e)
        
        captured_errors = error_handler.get_captured_errors()
        
        # Property: Error was captured
        assert len(captured_errors) == 1
        
        captured_error = captured_errors[0]
        
        # Property: All information is preserved
        assert captured_error['message'] == message
        assert captured_error['exception_type'] == error_type
        assert captured_error['context'] == context
        assert captured_error['stack_trace'] is not None
    
    @given(
        errors=st.lists(
            st.tuples(error_type_strategy, error_message_strategy, context_data_strategy),
            min_size=1,
            max_size=5
        )
    )
    @settings(max_examples=50, deadline=10000)
    def test_multiple_errors_preserve_individual_context(self, errors):
        """
        Property: Multiple errors should preserve individual contexts.
        
        When multiple errors are raised and captured, each should preserve
        its own unique context.
        
        Args:
            errors: List of (error_type, message, context) tuples
        """
        error_handler = ErrorHandler()
        
        # Raise and capture all errors
        for error_type, message, context in errors:
            try:
                error_handler.raise_error(error_type, message, context)
            except RaptorException as e:
                error_handler.capture_error(e)
        
        captured_errors = error_handler.get_captured_errors()
        
        # Property: All errors were captured
        assert len(captured_errors) == len(errors)
        
        # Property: Each error preserves its own context
        for i, (error_type, message, context) in enumerate(errors):
            captured = captured_errors[i]
            assert captured['message'] == message
            assert captured['exception_type'] == error_type
            assert captured['context'] == context
    
    @given(
        error_type=error_type_strategy,
        message=error_message_strategy
    )
    @settings(max_examples=100, deadline=5000)
    def test_error_without_context_still_preserves_info(
        self, error_type, message
    ):
        """
        Property: Errors without context should still preserve basic info.
        
        Even when no context is provided, errors should preserve message,
        type, and stack trace.
        
        Args:
            error_type: Type of error to raise
            message: Error message
        """
        error_handler = ErrorHandler()
        
        try:
            error_handler.raise_error(error_type, message, context=None)
        except RaptorException as e:
            # Property: Message is preserved
            assert e.message == message
            
            # Property: Type is preserved
            assert e.exception_type == error_type
            
            # Property: Stack trace is preserved
            assert e.stack_trace is not None
            
            # Property: Context is empty dict (not None)
            assert e.get_context() == {}


def test_property_coverage():
    """
    Verify that this test file covers Property 11: Error Context Preservation.
    
    This is a meta-test to ensure the property is properly documented and tested.
    """
    # Verify property is documented in module docstring
    assert "Property 11: Error Context Preservation" in __doc__
    assert "Validates: Requirements 11.1" in __doc__
    
    # Verify test class exists
    assert TestErrorContextPreservation is not None
    
    # Verify key test methods exist
    test_methods = [
        'test_error_preserves_message',
        'test_error_preserves_context',
        'test_error_preserves_stack_trace',
        'test_error_preserves_exception_type',
        'test_error_full_context_includes_all_info',
        'test_captured_errors_preserve_context',
        'test_multiple_errors_preserve_individual_context',
        'test_error_without_context_still_preserves_info'
    ]
    
    for method_name in test_methods:
        assert hasattr(TestErrorContextPreservation, method_name), (
            f"Test method {method_name} not found"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--hypothesis-show-statistics"])
