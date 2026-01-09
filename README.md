# PyQt6 Fluent MultiSelect ComboBox

[![PyPI version](https://badge.fury.io/py/fluent_multiselect.svg)](https://badge.fury.io/py/fluent_multiselect)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A beautiful, modern multi-select combo box widget for PyQt6 with **Windows 11 Fluent Design** styling.

## ✨ Features

- 🎨 **Fluent Design** - Windows 11 inspired styling
- 🌙 **Dark & Light Themes** - Built-in theme support
- ✅ **Multi-Select** - Select multiple items with checkboxes
- 🔄 **Select All** - Optional "Select All" functionality
- 🎯 **Max Selection** - Limit the number of selections
- ⌨️ **Keyboard Support** - Full keyboard navigation
- 🖱️ **Scroll Protection** - Mouse wheel won't change selection accidentally
- 🎭 **Animations** - Smooth arrow rotation animations
- 📦 **Zero Dependencies** - Only requires PyQt6

## 📦 Installation

```bash
pip install fluent_multiselect
```

## 🚀 Quick Start

```python
from PyQt6.QtWidgets import QApplication
from fluent_multiselect import FluentMultiSelectComboBox, Theme

app = QApplication([])

# Create combo box with dark theme
combo = FluentMultiSelectComboBox(theme=Theme.DARK)

# Add items
combo.addItems(["Python", "JavaScript", "TypeScript", "Rust", "Go"])

# Enable "Select All" option
combo.setSelectAllEnabled(True)

# Set placeholder text
combo.setPlaceholderText("Select languages...")

# Connect to selection changes
combo.selectionChanged.connect(lambda items: print(f"Selected: {items}"))

combo.show()
app.exec()
```

## 📖 Usage

### Basic Usage

```python
from fluent_multiselect import FluentMultiSelectComboBox, Theme

# Create with dark theme (default)
combo = FluentMultiSelectComboBox(theme=Theme.DARK)

# Or light theme
combo = FluentMultiSelectComboBox(theme=Theme.LIGHT)

# Add items
combo.addItem("Item 1")
combo.addItem("Item 2", data="custom_data")
combo.addItems(["Item 3", "Item 4", "Item 5"])
```

### Selection Management

```python
# Get selected items
selected_texts = combo.currentTexts()  # ["Item 1", "Item 3"]
selected_data = combo.currentData()     # Returns data values

# Set selection by text
combo.setCurrentTexts(["Item 1", "Item 3"])

# Set selection by indexes
combo.setCurrentIndexes([0, 2, 4])

# Select/deselect all
combo.selectAll()
combo.clearSelection()
```

### Configuration

```python
# Enable "Select All" option
combo.setSelectAllEnabled(True, text="Select All")

# Limit maximum selections
combo.setMaxSelectionCount(3)

# Close popup after each selection
combo.setCloseOnSelect(True)

# Custom delimiter for display
combo.setDisplayDelimiter(" | ")

# Placeholder text
combo.setPlaceholderText("Choose options...")
```

## 🔧 Requirements

- Python 3.9+
- PyQt6 >= 6.4.0

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.
