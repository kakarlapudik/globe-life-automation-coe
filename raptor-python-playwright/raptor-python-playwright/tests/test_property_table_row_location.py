"""
Property-Based Test: Table Row Location Consistency

**Feature: raptor-playwright-python, Property 8: Table Row Location Consistency**
**Validates: Requirements 8.1**

This test verifies that table row location by key value is consistent and reliable,
always returning the same row index for the same key value regardless of how many
times the operation is performed.

Property Statement:
    For any table with a key column, locating a row by key value should always 
    return the same row index for the same key.
"""

import pytest
import asyncio
from hypothesis import given, strategies as st, settings, assume
from typing import List, Tuple, Dict, Any
from unittest.mock import AsyncMock, MagicMock

from raptor.pages.table_manager import TableManager
from raptor.core.element_manager import ElementManager
from raptor.core.config_manager import ConfigManager
from raptor.core.exceptions import ElementNotFoundException


# Strategy for generating table data
# Each row is a list of cell values
# Filter out whitespace-only strings since table manager trims cell values
row_data_strategy = st.lists(
    st.text(
        alphabet=st.characters(blacklist_characters='\x00\n\r\t'),
        min_size=1,
        max_size=50
    ).filter(lambda x: x.strip() != ''),  # Exclude whitespace-only strings
    min_size=1,
    max_size=10
)

table_data_strategy = st.lists(
    row_data_strategy,
    min_size=1,
    max_size=20
)


# Strategy for generating column indices
def column_index_strategy(max_columns: int):
    """Generate valid column indices based on table structure."""
    return st.integers(min_value=0, max_value=max_columns - 1)


# Strategy for generating table locators
table_locator_strategy = st.sampled_from([
    "css=#data-table",
    "css=.users-table",
    "css=#products-table",
    "xpath=//table[@id='items']",
    "css=table.data-grid",
])


class TestTableRowLocationConsistency:
    """
    Property-based tests for table row location consistency.
    
    These tests verify that finding rows by key value is deterministic
    and consistent across multiple invocations.
    """
    
    def create_mock_table_manager(self):
        """
        Create a TableManager with mocked dependencies.
        
        Returns:
            Tuple of (TableManager, mock_page, mock_element_manager)
        """
        mock_page = AsyncMock()
        mock_page.wait_for_timeout = AsyncMock()
        mock_page.wait_for_load_state = AsyncMock()
        
        mock_element_manager = AsyncMock(spec=ElementManager)
        
        mock_config = MagicMock(spec=ConfigManager)
        mock_config.get.return_value = 20000
        
        table_manager = TableManager(mock_page, mock_element_manager, mock_config)
        
        return table_manager, mock_page, mock_element_manager
    
    def create_mock_table(self, table_data: List[List[str]]):
        """
        Create a mock table with specified data.
        
        Args:
            table_data: List of rows, where each row is a list of cell values
            
        Returns:
            Mock table element
        """
        mock_table = AsyncMock()
        mock_rows = []
        
        for row_values in table_data:
            mock_row = AsyncMock()
            mock_cells = []
            
            for cell_value in row_values:
                mock_cell = AsyncMock()
                mock_cell.inner_text = AsyncMock(return_value=cell_value)
                mock_cells.append(mock_cell)
            
            # Create a mock locator that returns cells
            mock_cell_locator = AsyncMock()
            mock_cell_locator.all = AsyncMock(return_value=mock_cells)
            mock_row.locator = MagicMock(return_value=mock_cell_locator)
            mock_rows.append(mock_row)
        
        # Create a mock locator that returns rows
        mock_row_locator = AsyncMock()
        mock_row_locator.all = AsyncMock(return_value=mock_rows)
        mock_table.locator = MagicMock(return_value=mock_row_locator)
        mock_table.wait_for = AsyncMock()
        
        return mock_table
    
    @given(
        table_data=table_data_strategy,
        table_locator=table_locator_strategy,
        repeat_count=st.integers(min_value=2, max_value=5)
    )
    @settings(max_examples=100, deadline=5000)
    @pytest.mark.asyncio
    async def test_row_location_consistency_same_key(
        self,
        table_data,
        table_locator,
        repeat_count
    ):
        """
        Property: Finding the same key multiple times returns the same row index.
        
        When searching for the same key value multiple times in the same table,
        the operation should always return the same row index.
        
        Args:
            table_data: Table data as list of rows
            table_locator: Locator for the table
            repeat_count: Number of times to repeat the search
        """
        # Ensure table has at least one row with at least one column
        assume(len(table_data) > 0)
        assume(all(len(row) > 0 for row in table_data))
        
        # Get the minimum number of columns across all rows
        min_columns = min(len(row) for row in table_data)
        assume(min_columns > 0)
        
        # Create table manager and mock table
        table_manager, _, mock_element_manager = self.create_mock_table_manager()
        
        # Select a random row and column to use as key
        key_row_index = 0  # Use first row for consistency
        key_column = 0  # Use first column
        # Trim the key value since table manager trims cell values before comparison
        key_value = table_data[key_row_index][key_column].strip()
        
        # Create mock table
        mock_table = self.create_mock_table(table_data)
        mock_element_manager.locate_element.return_value = mock_table
        
        # Find the row multiple times
        found_indices = []
        for _ in range(repeat_count):
            row_index = await table_manager.find_row_by_key(
                table_locator,
                key_column=key_column,
                key_value=key_value
            )
            found_indices.append(row_index)
        
        # Verify all searches returned the same index
        assert len(set(found_indices)) == 1, (
            f"Row location should be consistent: got indices {found_indices}"
        )
        
        # Verify the returned index is correct
        assert found_indices[0] == key_row_index, (
            f"Expected row index {key_row_index}, got {found_indices[0]}"
        )
    
    @given(
        table_data=table_data_strategy,
        table_locator=table_locator_strategy
    )
    @settings(max_examples=100, deadline=5000)
    @pytest.mark.asyncio
    async def test_row_location_finds_first_occurrence(
        self,
        table_data,
        table_locator
    ):
        """
        Property: When duplicate keys exist, find_row_by_key returns the first occurrence.
        
        If the same key value appears in multiple rows, the search should
        consistently return the index of the first matching row.
        
        Args:
            table_data: Table data as list of rows
            table_locator: Locator for the table
        """
        # Ensure table has at least 2 rows with at least one column
        assume(len(table_data) >= 2)
        assume(all(len(row) > 0 for row in table_data))
        
        min_columns = min(len(row) for row in table_data)
        assume(min_columns > 0)
        
        # Create a duplicate key by copying the first row's first cell to the second row
        key_column = 0
        duplicate_key = table_data[0][key_column]
        
        # Ensure second row has enough columns
        if len(table_data[1]) <= key_column:
            table_data[1].extend([''] * (key_column + 1 - len(table_data[1])))
        
        table_data[1][key_column] = duplicate_key
        
        # Create table manager and mock table
        table_manager, _, mock_element_manager = self.create_mock_table_manager()
        mock_table = self.create_mock_table(table_data)
        mock_element_manager.locate_element.return_value = mock_table
        
        # Find the row
        row_index = await table_manager.find_row_by_key(
            table_locator,
            key_column=key_column,
            key_value=duplicate_key
        )
        
        # Should return the first occurrence (index 0)
        assert row_index == 0, (
            f"Should return first occurrence (0), got {row_index}"
        )
    
    @given(
        table_data=table_data_strategy,
        table_locator=table_locator_strategy
    )
    @settings(max_examples=100, deadline=5000)
    @pytest.mark.asyncio
    async def test_row_location_all_rows_findable(
        self,
        table_data,
        table_locator
    ):
        """
        Property: Every row with a unique key should be findable.
        
        For each unique key value in a column, find_row_by_key should
        successfully locate the row containing that key.
        
        Args:
            table_data: Table data as list of rows
            table_locator: Locator for the table
        """
        # Ensure table has at least one row with at least one column
        assume(len(table_data) > 0)
        assume(all(len(row) > 0 for row in table_data))
        
        min_columns = min(len(row) for row in table_data)
        assume(min_columns > 0)
        
        # Use first column as key column
        key_column = 0
        
        # Create table manager and mock table
        table_manager, _, mock_element_manager = self.create_mock_table_manager()
        mock_table = self.create_mock_table(table_data)
        mock_element_manager.locate_element.return_value = mock_table
        
        # Try to find each row by its key value
        for expected_index, row in enumerate(table_data):
            if len(row) > key_column:
                # Trim the key value since table manager trims cell values before comparison
                key_value = row[key_column].strip()
                
                # Find the row
                found_index = await table_manager.find_row_by_key(
                    table_locator,
                    key_column=key_column,
                    key_value=key_value
                )
                
                # Should find a valid row (might not be expected_index if duplicates exist)
                assert found_index >= 0, f"Should find row with key '{key_value}'"
                assert found_index < len(table_data), f"Found index {found_index} out of range"
                
                # Verify the found row actually contains the key (after trimming)
                assert table_data[found_index][key_column].strip() == key_value, (
                    f"Found row {found_index} should contain key '{key_value}'"
                )
    
    @given(
        table_data=table_data_strategy,
        table_locator=table_locator_strategy,
        nonexistent_key=st.text(min_size=1, max_size=50)
    )
    @settings(max_examples=100, deadline=5000)
    @pytest.mark.asyncio
    async def test_row_location_nonexistent_key_raises_exception(
        self,
        table_data,
        table_locator,
        nonexistent_key
    ):
        """
        Property: Searching for a nonexistent key should raise ElementNotFoundException.
        
        When searching for a key value that doesn't exist in the table,
        the operation should consistently raise ElementNotFoundException.
        
        Args:
            table_data: Table data as list of rows
            table_locator: Locator for the table
            nonexistent_key: Key value that doesn't exist in the table
        """
        # Ensure table has at least one row with at least one column
        assume(len(table_data) > 0)
        assume(all(len(row) > 0 for row in table_data))
        
        min_columns = min(len(row) for row in table_data)
        assume(min_columns > 0)
        
        key_column = 0
        
        # Ensure the key doesn't exist in the table
        existing_keys = {row[key_column] for row in table_data if len(row) > key_column}
        assume(nonexistent_key not in existing_keys)
        
        # Create table manager and mock table
        table_manager, _, mock_element_manager = self.create_mock_table_manager()
        mock_table = self.create_mock_table(table_data)
        mock_element_manager.locate_element.return_value = mock_table
        
        # Should raise ElementNotFoundException
        with pytest.raises(ElementNotFoundException) as exc_info:
            await table_manager.find_row_by_key(
                table_locator,
                key_column=key_column,
                key_value=nonexistent_key
            )
        
        # Verify error message contains useful information
        error_message = str(exc_info.value).lower()
        assert "not found" in error_message or "nonexistent" in error_message.lower()
    
    @given(
        table_data=table_data_strategy,
        table_locator=table_locator_strategy
    )
    @settings(max_examples=100, deadline=5000)
    @pytest.mark.asyncio
    async def test_row_location_different_columns(
        self,
        table_data,
        table_locator
    ):
        """
        Property: The same value in different columns should locate different rows.
        
        When the same value appears in different columns of different rows,
        searching in each column should locate the correct row for that column.
        
        Args:
            table_data: Table data as list of rows
            table_locator: Locator for the table
        """
        # Ensure table has at least 2 rows with at least 2 columns each
        assume(len(table_data) >= 2)
        assume(all(len(row) >= 2 for row in table_data))
        
        # Create a scenario where the same value appears in different columns
        shared_value = "SHARED_VALUE_123"
        
        # Put shared value in column 0 of row 0
        table_data[0][0] = shared_value
        # Put shared value in column 1 of row 1
        table_data[1][1] = shared_value
        
        # Make sure column 0 of row 1 is different
        table_data[1][0] = "DIFFERENT_VALUE"
        
        # Create table manager and mock table
        table_manager, _, mock_element_manager = self.create_mock_table_manager()
        mock_table = self.create_mock_table(table_data)
        mock_element_manager.locate_element.return_value = mock_table
        
        # Search in column 0 - should find row 0
        row_index_col0 = await table_manager.find_row_by_key(
            table_locator,
            key_column=0,
            key_value=shared_value
        )
        
        # Search in column 1 - should find row 1
        row_index_col1 = await table_manager.find_row_by_key(
            table_locator,
            key_column=1,
            key_value=shared_value
        )
        
        # Verify correct rows were found
        assert row_index_col0 == 0, f"Column 0 search should find row 0, got {row_index_col0}"
        assert row_index_col1 == 1, f"Column 1 search should find row 1, got {row_index_col1}"
    
    @given(
        table_data=table_data_strategy,
        table_locator=table_locator_strategy
    )
    @settings(max_examples=100, deadline=5000)
    @pytest.mark.asyncio
    async def test_row_location_whitespace_handling(
        self,
        table_data,
        table_locator
    ):
        """
        Property: Row location should handle whitespace consistently.
        
        Cell values are trimmed before comparison, so searching for a value
        should find it regardless of leading/trailing whitespace in the table.
        
        Args:
            table_data: Table data as list of rows
            table_locator: Locator for the table
        """
        # Ensure table has at least one row with at least one column
        assume(len(table_data) > 0)
        assume(all(len(row) > 0 for row in table_data))
        
        key_column = 0
        key_value = "test_value"
        
        # Add whitespace to the first row's key column
        table_data[0][key_column] = f"  {key_value}  "
        
        # Create table manager and mock table
        table_manager, _, mock_element_manager = self.create_mock_table_manager()
        mock_table = self.create_mock_table(table_data)
        mock_element_manager.locate_element.return_value = mock_table
        
        # Search for the value without whitespace
        row_index = await table_manager.find_row_by_key(
            table_locator,
            key_column=key_column,
            key_value=key_value
        )
        
        # Should find the row despite whitespace
        assert row_index == 0, f"Should find row 0 despite whitespace, got {row_index}"
    
    @given(
        table_data=table_data_strategy,
        table_locator=table_locator_strategy
    )
    @settings(max_examples=100, deadline=5000)
    @pytest.mark.asyncio
    async def test_row_location_case_sensitive(
        self,
        table_data,
        table_locator
    ):
        """
        Property: Row location should be case-sensitive.
        
        Searching for a key value should only match cells with the exact
        same case, not case-insensitive matches.
        
        Args:
            table_data: Table data as list of rows
            table_locator: Locator for the table
        """
        # Ensure table has at least 2 rows with at least one column
        assume(len(table_data) >= 2)
        assume(all(len(row) > 0 for row in table_data))
        
        key_column = 0
        
        # Set up case-sensitive test data
        table_data[0][key_column] = "TestValue"
        table_data[1][key_column] = "testvalue"
        
        # Create table manager and mock table
        table_manager, _, mock_element_manager = self.create_mock_table_manager()
        mock_table = self.create_mock_table(table_data)
        mock_element_manager.locate_element.return_value = mock_table
        
        # Search for exact case match
        row_index = await table_manager.find_row_by_key(
            table_locator,
            key_column=key_column,
            key_value="TestValue"
        )
        
        # Should find row 0 (exact match)
        assert row_index == 0, f"Should find exact case match at row 0, got {row_index}"
        
        # Search for different case
        row_index2 = await table_manager.find_row_by_key(
            table_locator,
            key_column=key_column,
            key_value="testvalue"
        )
        
        # Should find row 1 (exact match)
        assert row_index2 == 1, f"Should find exact case match at row 1, got {row_index2}"
    
    @given(
        table_data=table_data_strategy,
        table_locator=table_locator_strategy
    )
    @settings(max_examples=50, deadline=5000)
    @pytest.mark.asyncio
    async def test_row_location_empty_table(
        self,
        table_data,
        table_locator
    ):
        """
        Property: Searching in an empty table should raise ElementNotFoundException.
        
        When a table has no rows, any search should consistently fail with
        ElementNotFoundException.
        
        Args:
            table_data: Table data (will be emptied)
            table_locator: Locator for the table
        """
        # Create an empty table
        empty_table_data = []
        
        # Create table manager and mock table
        table_manager, _, mock_element_manager = self.create_mock_table_manager()
        mock_table = self.create_mock_table(empty_table_data)
        mock_element_manager.locate_element.return_value = mock_table
        
        # Should raise ElementNotFoundException
        with pytest.raises(ElementNotFoundException) as exc_info:
            await table_manager.find_row_by_key(
                table_locator,
                key_column=0,
                key_value="any_value"
            )
        
        # Verify error message mentions no rows
        error_message = str(exc_info.value).lower()
        assert "no rows" in error_message or "not found" in error_message


def test_property_coverage():
    """
    Verify that this test file covers Property 8: Table Row Location Consistency.
    
    This is a meta-test to ensure the property is properly documented and tested.
    """
    # Verify property is documented in module docstring
    assert "Property 8: Table Row Location Consistency" in __doc__
    assert "Validates: Requirements 8.1" in __doc__
    
    # Verify test class exists
    assert TestTableRowLocationConsistency is not None
    
    # Verify key test methods exist
    test_methods = [
        'test_row_location_consistency_same_key',
        'test_row_location_finds_first_occurrence',
        'test_row_location_all_rows_findable',
        'test_row_location_nonexistent_key_raises_exception',
        'test_row_location_different_columns',
        'test_row_location_whitespace_handling',
        'test_row_location_case_sensitive',
        'test_row_location_empty_table'
    ]
    
    for method_name in test_methods:
        assert hasattr(TestTableRowLocationConsistency, method_name), (
            f"Test method {method_name} not found"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--hypothesis-show-statistics"])
