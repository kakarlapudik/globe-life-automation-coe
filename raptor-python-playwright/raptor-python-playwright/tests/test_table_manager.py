"""
Unit tests for TableManager.

Tests cover table operations including row location, cell reading/writing,
and table navigation.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from raptor.pages.table_manager import TableManager
from raptor.core.element_manager import ElementManager
from raptor.core.config_manager import ConfigManager
from raptor.core.exceptions import (
    ElementNotFoundException,
    ElementNotInteractableException,
)


@pytest.fixture
def mock_page():
    """Create a mock Playwright Page."""
    page = AsyncMock()
    page.wait_for_timeout = AsyncMock()
    page.wait_for_load_state = AsyncMock()
    return page


@pytest.fixture
def mock_element_manager():
    """Create a mock ElementManager."""
    return AsyncMock(spec=ElementManager)


@pytest.fixture
def mock_config_manager():
    """Create a mock ConfigManager."""
    config = MagicMock(spec=ConfigManager)
    config.get.return_value = 20000
    return config


@pytest.fixture
def table_manager(mock_page, mock_element_manager, mock_config_manager):
    """Create a TableManager instance with mocked dependencies."""
    return TableManager(mock_page, mock_element_manager, mock_config_manager)


@pytest.mark.asyncio
async def test_find_row_by_key_success(table_manager, mock_element_manager):
    """Test finding a row by key value successfully."""
    # Setup mock table with rows
    mock_table = AsyncMock()
    mock_element_manager.locate_element.return_value = mock_table

    # Create mock rows
    mock_row1 = AsyncMock()
    mock_row2 = AsyncMock()
    mock_row3 = AsyncMock()

    # Create mock cells for each row
    mock_cell1_1 = AsyncMock()
    mock_cell1_1.inner_text.return_value = "john.doe"
    mock_cell1_2 = AsyncMock()
    mock_cell1_2.inner_text.return_value = "John Doe"

    mock_cell2_1 = AsyncMock()
    mock_cell2_1.inner_text.return_value = "jane.smith"
    mock_cell2_2 = AsyncMock()
    mock_cell2_2.inner_text.return_value = "Jane Smith"

    mock_cell3_1 = AsyncMock()
    mock_cell3_1.inner_text.return_value = "bob.jones"
    mock_cell3_2 = AsyncMock()
    mock_cell3_2.inner_text.return_value = "Bob Jones"

    # Mock the locator chain properly
    mock_cells_locator1 = AsyncMock()
    mock_cells_locator1.all.return_value = [mock_cell1_1, mock_cell1_2]
    mock_row1.locator.return_value = mock_cells_locator1

    mock_cells_locator2 = AsyncMock()
    mock_cells_locator2.all.return_value = [mock_cell2_1, mock_cell2_2]
    mock_row2.locator.return_value = mock_cells_locator2

    mock_cells_locator3 = AsyncMock()
    mock_cells_locator3.all.return_value = [mock_cell3_1, mock_cell3_2]
    mock_row3.locator.return_value = mock_cells_locator3

    mock_rows_locator = AsyncMock()
    mock_rows_locator.all.return_value = [mock_row1, mock_row2, mock_row3]
    mock_table.locator.return_value = mock_rows_locator

    # Test finding row by key
    row_index = await table_manager.find_row_by_key(
        "css=#users-table",
        key_column=0,
        key_value="jane.smith"
    )

    assert row_index == 1
    mock_element_manager.locate_element.assert_called_once_with("css=#users-table")


@pytest.mark.asyncio
async def test_find_row_by_key_not_found(table_manager, mock_element_manager):
    """Test finding a row by key value when key doesn't exist."""
    # Setup mock table with rows
    mock_table = AsyncMock()
    mock_element_manager.locate_element.return_value = mock_table

    # Create mock rows
    mock_row = AsyncMock()
    mock_cell = AsyncMock()
    mock_cell.inner_text.return_value = "john.doe"
    mock_row.locator.return_value.all.return_value = [mock_cell]

    mock_table.locator.return_value.all.return_value = [mock_row]

    # Test finding non-existent key
    with pytest.raises(ElementNotFoundException) as exc_info:
        await table_manager.find_row_by_key(
            "css=#users-table",
            key_column=0,
            key_value="nonexistent"
        )

    assert "not found" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_get_cell_value_success(table_manager, mock_element_manager):
    """Test getting cell value successfully."""
    # Setup mock table and cell
    mock_table = AsyncMock()
    mock_element_manager.locate_element.return_value = mock_table

    mock_cell = AsyncMock()
    mock_cell.inner_text.return_value = "  test value  "
    mock_table.locator.return_value.first = mock_cell

    # Test getting cell value
    value = await table_manager.get_cell_value(
        "css=#users-table",
        row=1,
        column=2
    )

    assert value == "test value"
    mock_element_manager.locate_element.assert_called_once_with("css=#users-table")


@pytest.mark.asyncio
async def test_set_cell_value_with_input(table_manager, mock_element_manager, mock_page):
    """Test setting cell value when cell contains an input element."""
    # Setup mock table and cell
    mock_table = AsyncMock()
    mock_element_manager.locate_element.return_value = mock_table

    mock_cell = AsyncMock()
    mock_input = AsyncMock()
    mock_input.count.return_value = 1

    mock_cell.locator.return_value.first = mock_input
    mock_table.locator.return_value.first = mock_cell

    # Test setting cell value
    await table_manager.set_cell_value(
        "css=#users-table",
        row=1,
        column=2,
        value="new value"
    )

    mock_input.fill.assert_called_once_with("new value")


@pytest.mark.asyncio
async def test_click_cell_success(table_manager, mock_element_manager):
    """Test clicking a cell successfully."""
    # Setup mock table and cell
    mock_table = AsyncMock()
    mock_element_manager.locate_element.return_value = mock_table

    mock_cell = AsyncMock()
    mock_table.locator.return_value.first = mock_cell

    # Test clicking cell
    await table_manager.click_cell(
        "css=#users-table",
        row=1,
        column=3
    )

    mock_cell.click.assert_called_once()


@pytest.mark.asyncio
async def test_get_row_count_success(table_manager, mock_element_manager):
    """Test getting row count successfully."""
    # Setup mock table
    mock_table = AsyncMock()
    mock_element_manager.locate_element.return_value = mock_table

    mock_table.locator.return_value.count.return_value = 5

    # Test getting row count
    count = await table_manager.get_row_count("css=#users-table")

    assert count == 5
    mock_element_manager.locate_element.assert_called_once_with("css=#users-table")


@pytest.mark.asyncio
async def test_search_table_partial_match(table_manager, mock_element_manager):
    """Test searching table with partial match."""
    # Setup mock table with rows
    mock_table = AsyncMock()
    mock_element_manager.locate_element.return_value = mock_table

    # Create mock rows
    mock_row1 = AsyncMock()
    mock_row1.inner_text.return_value = "John Doe john.doe@example.com"

    mock_row2 = AsyncMock()
    mock_row2.inner_text.return_value = "Jane Smith jane.smith@example.com"

    mock_row3 = AsyncMock()
    mock_row3.inner_text.return_value = "Bob Johnson bob.j@example.com"

    mock_table.locator.return_value.all.return_value = [mock_row1, mock_row2, mock_row3]

    # Test searching with partial match
    matching_rows = await table_manager.search_table(
        "css=#users-table",
        search_text="john",
        case_sensitive=False,
        partial_match=True
    )

    assert matching_rows == [0, 2]  # Matches "John" and "Johnson"


@pytest.mark.asyncio
async def test_search_table_case_sensitive(table_manager, mock_element_manager):
    """Test searching table with case sensitivity."""
    # Setup mock table with rows
    mock_table = AsyncMock()
    mock_element_manager.locate_element.return_value = mock_table

    # Create mock rows
    mock_row1 = AsyncMock()
    mock_row1.inner_text.return_value = "John Doe"

    mock_row2 = AsyncMock()
    mock_row2.inner_text.return_value = "john smith"

    mock_table.locator.return_value.all.return_value = [mock_row1, mock_row2]

    # Test case-sensitive search
    matching_rows = await table_manager.search_table(
        "css=#users-table",
        search_text="john",
        case_sensitive=True,
        partial_match=True
    )

    assert matching_rows == [1]  # Only matches lowercase "john"


@pytest.mark.asyncio
async def test_navigate_pagination_success(table_manager, mock_element_manager, mock_page):
    """Test navigating to next page successfully."""
    # Setup mock next button
    mock_button = AsyncMock()
    mock_button.is_enabled.return_value = True
    mock_element_manager.locate_element.return_value = mock_button

    # Test navigation
    result = await table_manager.navigate_pagination("css=.next-page")

    assert result is True
    mock_button.click.assert_called_once()
    mock_page.wait_for_load_state.assert_called_once()


@pytest.mark.asyncio
async def test_navigate_pagination_last_page(table_manager, mock_element_manager):
    """Test navigating when already on last page."""
    # Setup mock next button (disabled)
    mock_button = AsyncMock()
    mock_button.is_enabled.return_value = False
    mock_element_manager.locate_element.return_value = mock_button

    # Test navigation
    result = await table_manager.navigate_pagination("css=.next-page")

    assert result is False
    mock_button.click.assert_not_called()


@pytest.mark.asyncio
async def test_get_column_values_success(table_manager, mock_element_manager):
    """Test getting all values from a column."""
    # Setup mock table with rows
    mock_table = AsyncMock()
    mock_element_manager.locate_element.return_value = mock_table

    # Create mock rows with cells
    mock_row1 = AsyncMock()
    mock_cell1 = AsyncMock()
    mock_cell1.inner_text.return_value = "value1"
    mock_row1.locator.return_value.all.return_value = [mock_cell1]

    mock_row2 = AsyncMock()
    mock_cell2 = AsyncMock()
    mock_cell2.inner_text.return_value = "value2"
    mock_row2.locator.return_value.all.return_value = [mock_cell2]

    mock_table.locator.return_value.all.return_value = [mock_row1, mock_row2]

    # Test getting column values
    values = await table_manager.get_column_values(
        "css=#users-table",
        column=0
    )

    assert values == ["value1", "value2"]
    mock_element_manager.locate_element.assert_called_once_with("css=#users-table")


@pytest.mark.asyncio
async def test_wait_for_table_update_success(table_manager, mock_element_manager, mock_page):
    """Test waiting for dynamic table to finish updating."""
    # Setup mock table
    mock_table = AsyncMock()
    mock_element_manager.locate_element.return_value = mock_table

    # Mock row count to be stable
    mock_table.locator.return_value.count.return_value = 5

    # Mock loading indicator
    mock_loader = AsyncMock()
    mock_loader.count.return_value = 0
    mock_page.locator.return_value = mock_loader

    # Test waiting for table update
    await table_manager.wait_for_table_update("css=#dynamic-table")

    mock_element_manager.locate_element.assert_called_once_with("css=#dynamic-table")
    mock_table.wait_for.assert_called_once()


@pytest.mark.asyncio
async def test_scroll_table_into_view_success(table_manager, mock_element_manager, mock_page):
    """Test scrolling table into view."""
    # Setup mock table
    mock_table = AsyncMock()
    mock_element_manager.locate_element.return_value = mock_table

    # Test scrolling
    await table_manager.scroll_table_into_view("css=#lazy-table")

    mock_element_manager.locate_element.assert_called_once_with("css=#lazy-table")
    mock_table.scroll_into_view_if_needed.assert_called_once()
    mock_page.wait_for_timeout.assert_called()


@pytest.mark.asyncio
async def test_load_all_dynamic_rows_success(table_manager, mock_element_manager, mock_page):
    """Test loading all rows in an infinite scroll table."""
    # Setup mock table
    mock_table = AsyncMock()
    mock_element_manager.locate_element.return_value = mock_table

    # Mock row count increasing then stabilizing
    row_counts = [5, 10, 15, 15, 15, 15]
    mock_table.locator.return_value.count.side_effect = row_counts

    # Mock loading indicator
    mock_loader = AsyncMock()
    mock_loader.count.return_value = 0
    mock_page.locator.return_value = mock_loader

    # Test loading dynamic rows
    total_rows = await table_manager.load_all_dynamic_rows(
        "css=#infinite-scroll-table",
        max_scrolls=10
    )

    assert total_rows == 15
    mock_element_manager.locate_element.assert_called()


@pytest.mark.asyncio
async def test_load_all_dynamic_rows_max_scrolls(table_manager, mock_element_manager, mock_page):
    """Test loading dynamic rows reaches max scrolls."""
    # Setup mock table
    mock_table = AsyncMock()
    mock_element_manager.locate_element.return_value = mock_table

    # Mock row count always increasing (never stabilizes)
    mock_table.locator.return_value.count.side_effect = range(5, 100)

    # Mock loading indicator
    mock_loader = AsyncMock()
    mock_loader.count.return_value = 0
    mock_page.locator.return_value = mock_loader

    # Test loading with max scrolls limit
    total_rows = await table_manager.load_all_dynamic_rows(
        "css=#infinite-scroll-table",
        max_scrolls=5
    )

    # Should stop at max_scrolls
    assert total_rows > 0
    mock_element_manager.locate_element.assert_called()


@pytest.mark.asyncio
async def test_get_pagination_info_success(table_manager, mock_element_manager, mock_page):
    """Test getting pagination information."""
    # Setup mock current page element
    mock_current_page = AsyncMock()
    mock_current_page.inner_text.return_value = "3"

    # Setup mock total pages element
    mock_total_pages = AsyncMock()
    mock_total_pages.inner_text.return_value = "10"

    # Mock element manager to return different elements
    async def mock_locate(locator):
        if "current" in locator:
            return mock_current_page
        elif "total" in locator:
            return mock_total_pages
        return AsyncMock()

    mock_element_manager.locate_element.side_effect = mock_locate

    # Setup mock next/previous buttons
    mock_next_button = AsyncMock()
    mock_next_button.count.return_value = 1
    mock_next_button.is_enabled.return_value = True

    mock_prev_button = AsyncMock()
    mock_prev_button.count.return_value = 1
    mock_prev_button.is_enabled.return_value = True

    def mock_page_locator(selector):
        mock_locator = AsyncMock()
        if "next" in selector.lower():
            mock_locator.first = mock_next_button
        elif "previous" in selector.lower():
            mock_locator.first = mock_prev_button
        else:
            mock_locator.first = AsyncMock()
        return mock_locator

    mock_page.locator.side_effect = mock_page_locator

    # Test getting pagination info
    info = await table_manager.get_pagination_info(
        current_page_locator="css=.current-page",
        total_pages_locator="css=.total-pages"
    )

    assert info["current_page"] == 3
    assert info["total_pages"] == 10
    assert info["has_next"] is True
    assert info["has_previous"] is True


@pytest.mark.asyncio
async def test_navigate_to_page_with_input(table_manager, mock_element_manager, mock_page):
    """Test navigating to specific page using input field."""
    # Setup mock page input
    mock_input = AsyncMock()
    mock_element_manager.locate_element.return_value = mock_input

    # Test navigation
    result = await table_manager.navigate_to_page(
        5,
        page_input_locator="css=.page-input"
    )

    assert result is True
    mock_input.fill.assert_called_once_with("5")
    mock_input.press.assert_called_once_with("Enter")
    mock_page.wait_for_load_state.assert_called_once()


@pytest.mark.asyncio
async def test_navigate_to_page_with_button(table_manager, mock_element_manager, mock_page):
    """Test navigating to specific page using button."""
    # Setup mock page button
    mock_button = AsyncMock()
    mock_element_manager.locate_element.return_value = mock_button

    # Test navigation
    result = await table_manager.navigate_to_page(
        5,
        page_button_locator_template="css=button[data-page='{page}']"
    )

    assert result is True
    mock_button.click.assert_called_once()
    mock_page.wait_for_load_state.assert_called_once()


@pytest.mark.asyncio
async def test_navigate_to_page_no_locator(table_manager):
    """Test navigating to page without providing locator."""
    # Test navigation without locator
    result = await table_manager.navigate_to_page(5)

    assert result is False
