"""Tests for FluentMultiSelectComboBox."""

import pytest
from PyQt6.QtCore import Qt

from fluent_multiselect import FluentMultiSelectComboBox, Theme


@pytest.fixture
def combo(qtbot):
    """Create a combo box for testing."""
    widget = FluentMultiSelectComboBox(theme=Theme.DARK)
    widget.addItems(["Item 1", "Item 2", "Item 3", "Item 4", "Item 5"])
    qtbot.addWidget(widget)
    return widget


class TestFluentMultiSelectComboBox:
    """Tests for FluentMultiSelectComboBox."""

    def test_add_items(self, combo):
        """Test adding items."""
        assert combo.model().rowCount() == 5

    def test_select_items(self, combo):
        """Test selecting items by text."""
        combo.setCurrentTexts(["Item 1", "Item 3"])
        assert combo.currentTexts() == ["Item 1", "Item 3"]

    def test_clear_selection(self, combo):
        """Test clearing selection."""
        combo.setCurrentTexts(["Item 1", "Item 2"])
        combo.clearSelection()
        assert combo.currentTexts() == []

    def test_select_all(self, combo):
        """Test select all."""
        combo.selectAll()
        assert len(combo.currentTexts()) == 5

    def test_max_selection(self, combo):
        """Test max selection limit."""
        combo.setMaxSelectionCount(2)
        combo.selectAll()
        assert len(combo.currentTexts()) == 2

    def test_theme_switch(self, combo):
        """Test theme switching."""
        combo.setTheme(Theme.LIGHT)
        assert combo.theme() == Theme.LIGHT
        combo.setTheme(Theme.DARK)
        assert combo.theme() == Theme.DARK

    def test_placeholder_text(self, combo):
        """Test placeholder text."""
        combo.setPlaceholderText("Select items...")
        assert combo.placeholderText() == "Select items..."

    def test_select_all_enabled(self, combo):
        """Test Select All option."""
        combo.setSelectAllEnabled(True, "Select All")
        assert combo.isSelectAllEnabled()
        assert combo.model().rowCount() == 6  # 5 items + Select All

    def test_find_text(self, combo):
        """Test finding item by text."""
        index = combo.findText("Item 3")
        assert index == 2

        index = combo.findText("Non-existent")
        assert index == -1

    def test_current_indexes(self, combo):
        """Test getting/setting by indexes."""
        combo.setCurrentIndexes([0, 2, 4])
        assert combo.getCurrentIndexes() == [0, 2, 4]

    def test_clear(self, combo):
        """Test clearing all items."""
        combo.clear()
        assert combo.model().rowCount() == 0

    def test_display_delimiter(self, combo):
        """Test display delimiter."""
        combo.setDisplayDelimiter(" | ")
        combo.setCurrentTexts(["Item 1", "Item 2"])
        assert combo.displayDelimiter() == " | "
