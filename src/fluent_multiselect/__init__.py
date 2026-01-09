# FILE: src/fluent_multiselect/__init__.py
"""
Fluent MultiSelect ComboBox for PyQt6
A Windows 11 Fluent Design styled multi-select combo box widget.
"""

__version__ = "0.1.0"
__author__ = "mIcHyAmRaNe"
__license__ = "MIT"

from .combobox import FluentMultiSelectComboBox
from .styles import Theme, FluentStyleSheet
from .chips import FluentChipsDisplay
from .delegate import FluentCheckBoxDelegate
from .colors import FluentColors

__all__ = [
    "FluentMultiSelectComboBox",
    "Theme",
    "FluentStyleSheet",
    "FluentChipsDisplay",
    "FluentCheckBoxDelegate",
    "FluentColors",
]