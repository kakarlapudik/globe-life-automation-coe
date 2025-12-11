"""
Property-Based Test: Element Location Fallback

**Feature: raptor-playwright-python, Property 2: Element Location Fallback**
**Validates: Requirements 2.2**

This test verifies that element location with fallback locators works correctly
and attempts fallback strategies in order when primary locators fail.

Property Statement:
    For any element with multiple locator strategies, if the primary locator fails, 
    the system should automatically attempt fallback locators in order until one 
    succeeds or all fail.
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from typing import List, Optional
from unittest.mock import AsyncMock, MagicMock


# Strategy for locator strings
locator_strategy = st.text(
    alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='#.-_[]'),
    min_size=3,
    max_size=30
).filter(lambda x: x.strip() != '')

# Strategy for fallback locator lists
fallback_locators_strategy = st.lists(
    locator_strategy,
    min_size=1,
    max_size=5,
    unique=True
)


class MockLocator:
    """Mock Playwright locator for testing."""
    
    def __init__(self, selector: str, exists: bool = True):
        self.selector = selector
        self._exists = exists
        self._visible = exists
    
    async def count(self) -> int:
        """Return count of matching elements."""
        return 1 if self._exists else 0
    
    async def is_visible(self) -> bool:
        """Check if element is visible."""
        if not self._exists:
            raise Exception(f"Element not found: {self.selector}")
        return self._visible
    
    async def click(self):
        """Click the element."""
        if not self._exists:
            raise Exception(f"Element not found: {self.selector}")
        if not self._visible:
            raise Exception(f"Element not visible: {self.selector}")


class MockPage:
    """Mock Playwright page for testing."""
    
    def __init__(self, existing_selectors: List[str]):
        self.existing_selectors = set(existing_selectors)
        self.locator_attempts = []
    
    def locator(self, selector: str) -> MockLocator:
        """Create a locator for the given selector."""
        self.locator_attempts.append(selector)
        exists = selector in self.existing_selectors
        return MockLocator(selector, exists=exists)


class ElementManagerWithFallback:
    """
    Mock element manager with fallback support.
    
    This simulates the ElementManager's fallback locator behavior.
    """
    
    def __init__(self, page: MockPage):
        self.page = page
        self.fallback_attempts = []
    
    async def locate_element(
        self,
        primary_locator: str,
        fallback_locators: Optional[List[str]] = None
    ) -> Optional[MockLocator]:
        """
        Locate element with fallback support.
        
        Tries primary locator first, then fallback locators in order.
        
        Args:
            primary_locator: Primary locator to try first
            fallback_locators: List of fallback locators to try if primary fails
            
        Returns:
            MockLocator if found, None if all locators fail
        """
        self.fallback_attempts = []
        
        # Try primary locator
        self.fallback_attempts.append(('primary', primary_locator))
        locator = self.page.locator(primary_locator)
        
        if await locator.count() > 0:
            return locator
        
        # Try fallback locators in order
        if fallback_locators:
            for i, fallback in enumerate(fallback_locators):
                self.fallback_attempts.append(('fallback', fallback, i))
                locator = self.page.locator(fallback)
                
                if await locator.count() > 0:
                    return locator
        
        # All locators failed
        return None
    
    def get_attempt_order(self) -> List[str]:
        """Get the order in which locators were attempted."""
        return [attempt[1] if len(attempt) == 2 else attempt[1] for attempt in self.fallback_attempts]


class TestElementLocationFallback:
    """
    Property-based tests for element location fallback.
    
    These tests verify that fallback locators are attempted in the correct
    order when primary locators fail.
    """
    
    @given(
        primary_locator=locator_strategy,
        fallback_locators=fallback_locators_strategy
    )
    @settings(max_examples=100, deadline=5000)
    @pytest.mark.asyncio
    async def test_primary_locator_succeeds_no_fallback_attempted(
        self, primary_locator, fallback_locators
    ):
        """
        Property: If primary locator succeeds, fallback locators should not be attempted.
        
        When the primary locator finds an element, the system should not
        attempt any fallback locators.
        
        Args:
            primary_locator: Primary locator string
            fallback_locators: List of fallback locators
        """
        # Ensure primary and fallbacks are different
        assume(primary_locator not in fallback_locators)
        
        # Setup: primary locator exists
        page = MockPage(existing_selectors=[primary_locator])
        element_manager = ElementManagerWithFallback(page)
        
        # Locate element
        locator = await element_manager.locate_element(
            primary_locator=primary_locator,
            fallback_locators=fallback_locators
        )
        
        # Property 1: Element was found
        assert locator is not None, "Element should be found with primary locator"
        
        # Property 2: Only primary locator was attempted
        attempts = element_manager.get_attempt_order()
        assert len(attempts) == 1, (
            f"Only primary locator should be attempted, but got {len(attempts)} attempts"
        )
        assert attempts[0] == primary_locator, (
            f"First attempt should be primary locator: {primary_locator}"
        )
        
        # Property 3: No fallback locators were attempted
        for fallback in fallback_locators:
            assert fallback not in attempts, (
                f"Fallback locator {fallback} should not be attempted when primary succeeds"
            )
    
    @given(
        primary_locator=locator_strategy,
        fallback_locators=fallback_locators_strategy,
        success_index=st.integers(min_value=0, max_value=4)
    )
    @settings(max_examples=100, deadline=5000)
    @pytest.mark.asyncio
    async def test_fallback_locators_attempted_in_order(
        self, primary_locator, fallback_locators, success_index
    ):
        """
        Property: Fallback locators should be attempted in order.
        
        When the primary locator fails, fallback locators should be attempted
        in the order they were provided.
        
        Args:
            primary_locator: Primary locator string
            fallback_locators: List of fallback locators
            success_index: Index of fallback locator that should succeed
        """
        # Ensure we have enough fallback locators
        assume(success_index < len(fallback_locators))
        
        # Ensure primary and fallbacks are different
        assume(primary_locator not in fallback_locators)
        
        # Setup: only the fallback at success_index exists
        successful_locator = fallback_locators[success_index]
        page = MockPage(existing_selectors=[successful_locator])
        element_manager = ElementManagerWithFallback(page)
        
        # Locate element
        locator = await element_manager.locate_element(
            primary_locator=primary_locator,
            fallback_locators=fallback_locators
        )
        
        # Property 1: Element was found
        assert locator is not None, (
            f"Element should be found with fallback locator at index {success_index}"
        )
        
        # Property 2: Locators were attempted in correct order
        attempts = element_manager.get_attempt_order()
        
        # Should have attempted: primary + fallbacks up to and including success_index
        expected_attempts = [primary_locator] + fallback_locators[:success_index + 1]
        assert attempts == expected_attempts, (
            f"Locators should be attempted in order. "
            f"Expected: {expected_attempts}, Got: {attempts}"
        )
        
        # Property 3: Fallback locators after success_index were not attempted
        for i in range(success_index + 1, len(fallback_locators)):
            assert fallback_locators[i] not in attempts, (
                f"Fallback locator at index {i} should not be attempted "
                f"after success at index {success_index}"
            )
    
    @given(
        primary_locator=locator_strategy,
        fallback_locators=fallback_locators_strategy
    )
    @settings(max_examples=100, deadline=5000)
    @pytest.mark.asyncio
    async def test_all_locators_fail_returns_none(
        self, primary_locator, fallback_locators
    ):
        """
        Property: If all locators fail, None should be returned.
        
        When both primary and all fallback locators fail to find an element,
        the system should return None.
        
        Args:
            primary_locator: Primary locator string
            fallback_locators: List of fallback locators
        """
        # Ensure primary and fallbacks are different
        assume(primary_locator not in fallback_locators)
        
        # Setup: no locators exist
        page = MockPage(existing_selectors=[])
        element_manager = ElementManagerWithFallback(page)
        
        # Locate element
        locator = await element_manager.locate_element(
            primary_locator=primary_locator,
            fallback_locators=fallback_locators
        )
        
        # Property 1: No element was found
        assert locator is None, "Should return None when all locators fail"
        
        # Property 2: All locators were attempted
        attempts = element_manager.get_attempt_order()
        expected_attempts = [primary_locator] + fallback_locators
        assert attempts == expected_attempts, (
            f"All locators should be attempted. "
            f"Expected: {expected_attempts}, Got: {attempts}"
        )
    
    @given(
        primary_locator=locator_strategy
    )
    @settings(max_examples=100, deadline=5000)
    @pytest.mark.asyncio
    async def test_no_fallback_locators_provided(self, primary_locator):
        """
        Property: Without fallback locators, only primary should be attempted.
        
        When no fallback locators are provided, only the primary locator
        should be attempted.
        
        Args:
            primary_locator: Primary locator string
        """
        # Test case 1: Primary succeeds
        page = MockPage(existing_selectors=[primary_locator])
        element_manager = ElementManagerWithFallback(page)
        
        locator = await element_manager.locate_element(
            primary_locator=primary_locator,
            fallback_locators=None
        )
        
        assert locator is not None
        attempts = element_manager.get_attempt_order()
        assert attempts == [primary_locator]
        
        # Test case 2: Primary fails
        page = MockPage(existing_selectors=[])
        element_manager = ElementManagerWithFallback(page)
        
        locator = await element_manager.locate_element(
            primary_locator=primary_locator,
            fallback_locators=None
        )
        
        assert locator is None
        attempts = element_manager.get_attempt_order()
        assert attempts == [primary_locator]
    
    @given(
        primary_locator=locator_strategy,
        fallback_locators=fallback_locators_strategy
    )
    @settings(max_examples=100, deadline=5000)
    @pytest.mark.asyncio
    async def test_first_fallback_succeeds(self, primary_locator, fallback_locators):
        """
        Property: If first fallback succeeds, remaining fallbacks not attempted.
        
        When the first fallback locator finds an element, subsequent fallback
        locators should not be attempted.
        
        Args:
            primary_locator: Primary locator string
            fallback_locators: List of fallback locators
        """
        # Ensure we have at least one fallback
        assume(len(fallback_locators) >= 1)
        
        # Ensure primary and fallbacks are different
        assume(primary_locator not in fallback_locators)
        
        # Setup: only first fallback exists
        first_fallback = fallback_locators[0]
        page = MockPage(existing_selectors=[first_fallback])
        element_manager = ElementManagerWithFallback(page)
        
        # Locate element
        locator = await element_manager.locate_element(
            primary_locator=primary_locator,
            fallback_locators=fallback_locators
        )
        
        # Property 1: Element was found
        assert locator is not None
        
        # Property 2: Only primary and first fallback were attempted
        attempts = element_manager.get_attempt_order()
        assert attempts == [primary_locator, first_fallback], (
            f"Should only attempt primary and first fallback. Got: {attempts}"
        )
        
        # Property 3: Remaining fallbacks were not attempted
        for i in range(1, len(fallback_locators)):
            assert fallback_locators[i] not in attempts, (
                f"Fallback at index {i} should not be attempted"
            )
    
    @given(
        primary_locator=locator_strategy,
        fallback_locators=fallback_locators_strategy
    )
    @settings(max_examples=100, deadline=5000)
    @pytest.mark.asyncio
    async def test_last_fallback_succeeds(self, primary_locator, fallback_locators):
        """
        Property: If only last fallback succeeds, all previous locators attempted.
        
        When only the last fallback locator finds an element, all previous
        locators should have been attempted.
        
        Args:
            primary_locator: Primary locator string
            fallback_locators: List of fallback locators
        """
        # Ensure we have at least one fallback
        assume(len(fallback_locators) >= 1)
        
        # Ensure primary and fallbacks are different
        assume(primary_locator not in fallback_locators)
        
        # Setup: only last fallback exists
        last_fallback = fallback_locators[-1]
        page = MockPage(existing_selectors=[last_fallback])
        element_manager = ElementManagerWithFallback(page)
        
        # Locate element
        locator = await element_manager.locate_element(
            primary_locator=primary_locator,
            fallback_locators=fallback_locators
        )
        
        # Property 1: Element was found
        assert locator is not None
        
        # Property 2: All locators were attempted
        attempts = element_manager.get_attempt_order()
        expected_attempts = [primary_locator] + fallback_locators
        assert attempts == expected_attempts, (
            f"All locators should be attempted. "
            f"Expected: {expected_attempts}, Got: {attempts}"
        )
    
    @given(
        primary_locator=locator_strategy,
        fallback_locators=fallback_locators_strategy
    )
    @settings(max_examples=100, deadline=5000)
    @pytest.mark.asyncio
    async def test_fallback_order_preserved(self, primary_locator, fallback_locators):
        """
        Property: Fallback order should be preserved regardless of which succeeds.
        
        The order in which fallback locators are attempted should always match
        the order they were provided, regardless of which one succeeds.
        
        Args:
            primary_locator: Primary locator string
            fallback_locators: List of fallback locators
        """
        # Ensure primary and fallbacks are different
        assume(primary_locator not in fallback_locators)
        
        # Test with each fallback succeeding
        for success_index in range(len(fallback_locators)):
            successful_locator = fallback_locators[success_index]
            page = MockPage(existing_selectors=[successful_locator])
            element_manager = ElementManagerWithFallback(page)
            
            locator = await element_manager.locate_element(
                primary_locator=primary_locator,
                fallback_locators=fallback_locators
            )
            
            assert locator is not None
            
            # Verify order
            attempts = element_manager.get_attempt_order()
            expected_order = [primary_locator] + fallback_locators[:success_index + 1]
            
            assert attempts == expected_order, (
                f"Fallback order not preserved for success at index {success_index}. "
                f"Expected: {expected_order}, Got: {attempts}"
            )
    
    @given(
        primary_locator=locator_strategy,
        fallback_count=st.integers(min_value=1, max_value=10)
    )
    @settings(max_examples=50, deadline=5000)
    @pytest.mark.asyncio
    async def test_fallback_count_matches_attempts(
        self, primary_locator, fallback_count
    ):
        """
        Property: Number of fallback attempts should match fallback count.
        
        When all locators fail, the number of fallback attempts should equal
        the number of fallback locators provided.
        
        Args:
            primary_locator: Primary locator string
            fallback_count: Number of fallback locators to generate
        """
        # Generate unique fallback locators
        fallback_locators = [f"fallback_{i}_{primary_locator}" for i in range(fallback_count)]
        
        # Setup: no locators exist
        page = MockPage(existing_selectors=[])
        element_manager = ElementManagerWithFallback(page)
        
        # Locate element
        locator = await element_manager.locate_element(
            primary_locator=primary_locator,
            fallback_locators=fallback_locators
        )
        
        # Property: Total attempts = 1 (primary) + fallback_count
        attempts = element_manager.get_attempt_order()
        assert len(attempts) == 1 + fallback_count, (
            f"Should have {1 + fallback_count} attempts, got {len(attempts)}"
        )


def test_property_coverage():
    """
    Verify that this test file covers Property 2: Element Location Fallback.
    
    This is a meta-test to ensure the property is properly documented and tested.
    """
    # Verify property is documented in module docstring
    assert "Property 2: Element Location Fallback" in __doc__
    assert "Validates: Requirements 2.2" in __doc__
    
    # Verify test class exists
    assert TestElementLocationFallback is not None
    
    # Verify key test methods exist
    test_methods = [
        'test_primary_locator_succeeds_no_fallback_attempted',
        'test_fallback_locators_attempted_in_order',
        'test_all_locators_fail_returns_none',
        'test_no_fallback_locators_provided',
        'test_first_fallback_succeeds',
        'test_last_fallback_succeeds',
        'test_fallback_order_preserved',
        'test_fallback_count_matches_attempts'
    ]
    
    for method_name in test_methods:
        assert hasattr(TestElementLocationFallback, method_name), (
            f"Test method {method_name} not found"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--hypothesis-show-statistics"])
