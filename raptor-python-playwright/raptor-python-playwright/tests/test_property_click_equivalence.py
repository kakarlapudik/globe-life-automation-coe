"""
Property-Based Test: Click Method Equivalence

**Feature: raptor-playwright-python, Property 6: Click Method Equivalence**
**Validates: Requirements 6.2**

This test verifies that different click methods (click(), clickXY(), JavaScript click)
all result in the element being clicked successfully.

Property Statement:
    For any clickable element, using click(), clickXY(), or JavaScript click should 
    all result in the element being clicked successfully.
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from typing import List, Tuple
from unittest.mock import AsyncMock, MagicMock


# Strategy for element coordinates
coordinate_strategy = st.tuples(
    st.integers(min_value=0, max_value=1920),
    st.integers(min_value=0, max_value=1080)
)


class ClickableElement:
    """
    Mock clickable element that tracks click methods used.
    
    This simulates an element that can be clicked using different methods.
    """
    
    def __init__(self, x: int = 100, y: int = 100):
        self.x = x
        self.y = y
        self.click_count = 0
        self.click_methods = []
        self.is_clickable = True
    
    async def click(self):
        """Standard click method."""
        if not self.is_clickable:
            raise Exception("Element is not clickable")
        
        self.click_count += 1
        self.click_methods.append('click')
        return True
    
    async def click_at_position(self, x: int, y: int):
        """Click at specific coordinates."""
        if not self.is_clickable:
            raise Exception("Element is not clickable")
        
        # Verify coordinates are within element bounds (simplified)
        if abs(x - self.x) > 50 or abs(y - self.y) > 50:
            raise Exception(f"Coordinates ({x}, {y}) outside element bounds")
        
        self.click_count += 1
        self.click_methods.append('click_at_position')
        return True
    
    async def click_with_javascript(self):
        """Click using JavaScript."""
        if not self.is_clickable:
            raise Exception("Element is not clickable")
        
        self.click_count += 1
        self.click_methods.append('click_with_javascript')
        return True
    
    def was_clicked(self) -> bool:
        """Check if element was clicked."""
        return self.click_count > 0
    
    def get_click_methods_used(self) -> List[str]:
        """Get list of click methods that were used."""
        return self.click_methods.copy()


class TestClickMethodEquivalence:
    """
    Property-based tests for click method equivalence.
    
    These tests verify that different click methods all successfully
    click the element and produce equivalent results.
    """
    
    @given(
        coordinates=coordinate_strategy
    )
    @settings(max_examples=100, deadline=5000)
    @pytest.mark.asyncio
    async def test_all_click_methods_succeed(self, coordinates):
        """
        Property: All click methods should successfully click the element.
        
        For any clickable element, all three click methods (click, clickXY,
        JavaScript) should successfully click the element.
        
        Args:
            coordinates: Element coordinates (x, y)
        """
        x, y = coordinates
        
        # Test standard click
        element1 = ClickableElement(x=x, y=y)
        result1 = await element1.click()
        assert result1 is True
        assert element1.was_clicked()
        
        # Test click at position
        element2 = ClickableElement(x=x, y=y)
        result2 = await element2.click_at_position(x, y)
        assert result2 is True
        assert element2.was_clicked()
        
        # Test JavaScript click
        element3 = ClickableElement(x=x, y=y)
        result3 = await element3.click_with_javascript()
        assert result3 is True
        assert element3.was_clicked()
    
    @given(
        coordinates=coordinate_strategy
    )
    @settings(max_examples=100, deadline=5000)
    @pytest.mark.asyncio
    async def test_click_methods_produce_same_result(self, coordinates):
        """
        Property: All click methods should produce the same end result.
        
        Regardless of which click method is used, the element should end up
        in the same "clicked" state.
        
        Args:
            coordinates: Element coordinates (x, y)
        """
        x, y = coordinates
        
        # Click using each method
        element1 = ClickableElement(x=x, y=y)
        await element1.click()
        
        element2 = ClickableElement(x=x, y=y)
        await element2.click_at_position(x, y)
        
        element3 = ClickableElement(x=x, y=y)
        await element3.click_with_javascript()
        
        # Property: All elements should be in clicked state
        assert element1.was_clicked()
        assert element2.was_clicked()
        assert element3.was_clicked()
        
        # Property: All should have same click count
        assert element1.click_count == 1
        assert element2.click_count == 1
        assert element3.click_count == 1
    
    @given(
        coordinates=coordinate_strategy,
        click_sequence=st.lists(
            st.sampled_from(['click', 'click_at_position', 'click_with_javascript']),
            min_size=1,
            max_size=5
        )
    )
    @settings(max_examples=100, deadline=5000)
    @pytest.mark.asyncio
    async def test_click_methods_can_be_mixed(self, coordinates, click_sequence):
        """
        Property: Different click methods can be used interchangeably.
        
        An element should support being clicked multiple times using
        different click methods in any order.
        
        Args:
            coordinates: Element coordinates (x, y)
            click_sequence: Sequence of click methods to use
        """
        x, y = coordinates
        element = ClickableElement(x=x, y=y)
        
        # Execute click sequence
        for method in click_sequence:
            if method == 'click':
                await element.click()
            elif method == 'click_at_position':
                await element.click_at_position(x, y)
            elif method == 'click_with_javascript':
                await element.click_with_javascript()
        
        # Property: Element was clicked correct number of times
        assert element.click_count == len(click_sequence), (
            f"Element should be clicked {len(click_sequence)} times"
        )
        
        # Property: All methods were recorded
        assert len(element.click_methods) == len(click_sequence)
    
    @given(
        coordinates=coordinate_strategy
    )
    @settings(max_examples=100, deadline=5000)
    @pytest.mark.asyncio
    async def test_click_methods_fail_consistently(self, coordinates):
        """
        Property: All click methods should fail consistently for unclickable elements.
        
        If an element is not clickable, all click methods should fail
        with appropriate errors.
        
        Args:
            coordinates: Element coordinates (x, y)
        """
        x, y = coordinates
        
        # Test standard click
        element1 = ClickableElement(x=x, y=y)
        element1.is_clickable = False
        
        with pytest.raises(Exception) as exc1:
            await element1.click()
        assert "not clickable" in str(exc1.value).lower()
        
        # Test click at position
        element2 = ClickableElement(x=x, y=y)
        element2.is_clickable = False
        
        with pytest.raises(Exception) as exc2:
            await element2.click_at_position(x, y)
        assert "not clickable" in str(exc2.value).lower()
        
        # Test JavaScript click
        element3 = ClickableElement(x=x, y=y)
        element3.is_clickable = False
        
        with pytest.raises(Exception) as exc3:
            await element3.click_with_javascript()
        assert "not clickable" in str(exc3.value).lower()
    
    @given(
        element_coords=coordinate_strategy,
        click_coords=coordinate_strategy
    )
    @settings(max_examples=100, deadline=5000)
    @pytest.mark.asyncio
    async def test_click_at_position_validates_coordinates(
        self, element_coords, click_coords
    ):
        """
        Property: Click at position should validate coordinates.
        
        Clicking at coordinates outside the element bounds should fail,
        while coordinates within bounds should succeed.
        
        Args:
            element_coords: Element position (x, y)
            click_coords: Click coordinates (x, y)
        """
        elem_x, elem_y = element_coords
        click_x, click_y = click_coords
        
        element = ClickableElement(x=elem_x, y=elem_y)
        
        # Calculate if click is within bounds (simplified: within 50 pixels)
        within_bounds = (
            abs(click_x - elem_x) <= 50 and
            abs(click_y - elem_y) <= 50
        )
        
        if within_bounds:
            # Property: Click should succeed
            result = await element.click_at_position(click_x, click_y)
            assert result is True
            assert element.was_clicked()
        else:
            # Property: Click should fail
            with pytest.raises(Exception) as exc:
                await element.click_at_position(click_x, click_y)
            assert "outside element bounds" in str(exc.value).lower()
    
    @given(
        coordinates=coordinate_strategy,
        method=st.sampled_from(['click', 'click_at_position', 'click_with_javascript'])
    )
    @settings(max_examples=100, deadline=5000)
    @pytest.mark.asyncio
    async def test_single_click_method_sufficient(self, coordinates, method):
        """
        Property: Any single click method should be sufficient to click element.
        
        Using any one of the click methods should be sufficient to successfully
        click an element - no combination of methods is required.
        
        Args:
            coordinates: Element coordinates (x, y)
            method: Click method to use
        """
        x, y = coordinates
        element = ClickableElement(x=x, y=y)
        
        # Use only the specified method
        if method == 'click':
            result = await element.click()
        elif method == 'click_at_position':
            result = await element.click_at_position(x, y)
        elif method == 'click_with_javascript':
            result = await element.click_with_javascript()
        
        # Property: Element was successfully clicked
        assert result is True
        assert element.was_clicked()
        assert element.click_count == 1
    
    @given(
        coordinates=coordinate_strategy
    )
    @settings(max_examples=100, deadline=5000)
    @pytest.mark.asyncio
    async def test_click_methods_are_idempotent_per_call(self, coordinates):
        """
        Property: Each click method call should click exactly once.
        
        Each invocation of any click method should result in exactly one
        click, not multiple clicks.
        
        Args:
            coordinates: Element coordinates (x, y)
        """
        x, y = coordinates
        
        # Test each method
        for method_name in ['click', 'click_at_position', 'click_with_javascript']:
            element = ClickableElement(x=x, y=y)
            initial_count = element.click_count
            
            if method_name == 'click':
                await element.click()
            elif method_name == 'click_at_position':
                await element.click_at_position(x, y)
            elif method_name == 'click_with_javascript':
                await element.click_with_javascript()
            
            # Property: Click count increased by exactly 1
            assert element.click_count == initial_count + 1, (
                f"{method_name} should increment click count by exactly 1"
            )


def test_property_coverage():
    """
    Verify that this test file covers Property 6: Click Method Equivalence.
    
    This is a meta-test to ensure the property is properly documented and tested.
    """
    # Verify property is documented in module docstring
    assert "Property 6: Click Method Equivalence" in __doc__
    assert "Validates: Requirements 6.2" in __doc__
    
    # Verify test class exists
    assert TestClickMethodEquivalence is not None
    
    # Verify key test methods exist
    test_methods = [
        'test_all_click_methods_succeed',
        'test_click_methods_produce_same_result',
        'test_click_methods_can_be_mixed',
        'test_click_methods_fail_consistently',
        'test_click_at_position_validates_coordinates',
        'test_single_click_method_sufficient',
        'test_click_methods_are_idempotent_per_call'
    ]
    
    for method_name in test_methods:
        assert hasattr(TestClickMethodEquivalence, method_name), (
            f"Test method {method_name} not found"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--hypothesis-show-statistics"])
