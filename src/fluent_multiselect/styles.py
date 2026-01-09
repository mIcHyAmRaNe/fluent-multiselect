# FILE: src/fluent_multiselect/styles.py
"""Fluent Design style sheet definitions."""

from enum import Enum


class Theme(Enum):
    """Theme enumeration for the combo box."""
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"


class FluentStyleSheet:
    """Fluent Design style sheet generator."""

    @staticmethod
    def get_combo_box_style(theme: Theme) -> str:
        """Get the style sheet for the combo box based on theme."""
        if theme == Theme.DARK:
            return FluentStyleSheet._dark_combo_style()
        return FluentStyleSheet._light_combo_style()

    @staticmethod
    def _dark_combo_style() -> str:
        return """
            FluentMultiSelectComboBox {
                border: 1px solid rgba(255, 255, 255, 0.053);
                border-radius: 5px;
                border-top: 1px solid rgba(255, 255, 255, 0.08);
                padding: 5px 31px 6px 11px;
                color: white;
                background-color: rgba(255, 255, 255, 0.0605);
                text-align: left;
                outline: none;
                min-height: 30px;
            }

            FluentMultiSelectComboBox:hover {
                background-color: rgba(255, 255, 255, 0.0837);
            }

            FluentMultiSelectComboBox:pressed {
                background-color: rgba(255, 255, 255, 0.0326);
                border-top: 1px solid rgba(255, 255, 255, 0.053);
                color: rgba(255, 255, 255, 0.63);
            }

            FluentMultiSelectComboBox:disabled {
                color: rgba(255, 255, 255, 0.3628);
                background: rgba(255, 255, 255, 0.0419);
                border: 1px solid rgba(255, 255, 255, 0.053);
            }

            FluentMultiSelectComboBox:focus {
                border: 1px solid rgba(138, 180, 248, 0.8);
                border-bottom: 2px solid rgb(138, 180, 248);
            }

            FluentMultiSelectComboBox QLineEdit {
                background: transparent;
                border: none;
                color: white;
                padding: 0px;
                margin: 0px;
                selection-background-color: rgba(138, 180, 248, 0.3);
            }
        """

    @staticmethod
    def _light_combo_style() -> str:
        return """
            FluentMultiSelectComboBox {
                border: 1px solid rgba(0, 0, 0, 0.073);
                border-radius: 5px;
                border-bottom: 1px solid rgba(0, 0, 0, 0.183);
                padding: 5px 31px 6px 11px;
                color: black;
                background-color: rgba(255, 255, 255, 0.7);
                text-align: left;
                outline: none;
                min-height: 30px;
            }

            FluentMultiSelectComboBox:hover {
                background-color: rgba(249, 249, 249, 0.5);
            }

            FluentMultiSelectComboBox:pressed {
                background-color: rgba(249, 249, 249, 0.3);
                color: rgba(0, 0, 0, 0.63);
            }

            FluentMultiSelectComboBox:disabled {
                color: rgba(0, 0, 0, 0.3614);
                background: rgba(249, 249, 249, 0.3);
            }

            FluentMultiSelectComboBox:focus {
                border: 1px solid rgba(0, 103, 192, 0.6);
                border-bottom: 2px solid rgb(0, 103, 192);
            }

            FluentMultiSelectComboBox QLineEdit {
                background: transparent;
                border: none;
                color: black;
                padding: 0px;
                margin: 0px;
            }
        """

    @staticmethod
    def get_popup_style(theme: Theme) -> str:
        """Get the style sheet for the popup/dropdown."""
        if theme == Theme.DARK:
            return FluentStyleSheet._dark_popup_style()
        return FluentStyleSheet._light_popup_style()

    @staticmethod
    def _dark_popup_style() -> str:
        return """
            QListView {
                background-color: rgb(44, 44, 44);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 6px;
                outline: none;
                padding: 4px;
            }

            QListView::item {
                background: transparent;
                border: none;
                border-radius: 4px;
                padding: 6px 8px;
                margin: 1px 0px;
                color: white;
            }

            QListView::item:hover {
                background-color: rgba(255, 255, 255, 0.08);
            }

            QListView::item:selected {
                background-color: rgba(255, 255, 255, 0.06);
            }

            QListView::item:disabled {
                color: rgba(255, 255, 255, 0.36);
            }
        """

    @staticmethod
    def _light_popup_style() -> str:
        return """
            QListView {
                background-color: rgb(252, 252, 252);
                border: 1px solid rgba(0, 0, 0, 0.08);
                border-radius: 6px;
                outline: none;
                padding: 4px;
            }

            QListView::item {
                background: transparent;
                border: none;
                border-radius: 4px;
                padding: 6px 8px;
                margin: 1px 0px;
                color: black;
            }

            QListView::item:hover {
                background-color: rgba(0, 0, 0, 0.05);
            }

            QListView::item:selected {
                background-color: rgba(0, 0, 0, 0.03);
            }

            QListView::item:disabled {
                color: rgba(0, 0, 0, 0.36);
            }
        """

    @staticmethod
    def get_checkbox_style(theme: Theme) -> str:
        """
        Get the checkbox style sheet.
        
        Note: This style is provided for reference and consistency.
        The actual checkbox in the delegate is custom-painted to match these specs.
        """
        if theme == Theme.DARK:
            return FluentStyleSheet._dark_checkbox_style()
        return FluentStyleSheet._light_checkbox_style()

    @staticmethod
    def _dark_checkbox_style() -> str:
        """Dark theme checkbox QSS."""
        return """
            QCheckBox {
                color: white;
                spacing: 8px;
                min-width: 28px;
                min-height: 22px;
                outline: none;
                margin-left: 1px;
            }

            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 5px;
                border: 1px solid rgba(255, 255, 255, 0.27);
                background-color: rgba(255, 255, 255, 0.05);
            }

            QCheckBox::indicator:hover {
                border: 1px solid rgba(255, 255, 255, 0.35);
                background-color: rgba(255, 255, 255, 0.08);
            }

            QCheckBox::indicator:pressed {
                border: 1px solid rgba(255, 255, 255, 0.20);
                background-color: rgba(255, 255, 255, 0.03);
            }

            QCheckBox::indicator:checked {
                border: 1px solid rgb(138, 180, 248);
                background-color: rgb(138, 180, 248);
                image: url(:/icons/checkbox_check_dark.svg);
            }

            QCheckBox::indicator:checked:hover {
                border: 1px solid rgb(158, 195, 255);
                background-color: rgb(158, 195, 255);
            }

            QCheckBox::indicator:checked:pressed {
                border: 1px solid rgb(118, 165, 235);
                background-color: rgb(118, 165, 235);
            }

            QCheckBox::indicator:indeterminate {
                border: 1px solid rgb(138, 180, 248);
                background-color: rgb(138, 180, 248);
                image: url(:/icons/checkbox_partial_dark.svg);
            }

            QCheckBox:disabled {
                color: rgba(255, 255, 255, 0.36);
            }

            QCheckBox::indicator:disabled {
                border: 1px solid rgba(255, 255, 255, 0.20);
                background-color: rgba(255, 255, 255, 0.03);
            }

            QCheckBox::indicator:checked:disabled {
                border: 1px solid rgba(138, 180, 248, 0.40);
                background-color: rgba(138, 180, 248, 0.40);
            }
        """

    @staticmethod
    def _light_checkbox_style() -> str:
        """Light theme checkbox QSS."""
        return """
            QCheckBox {
                color: black;
                spacing: 8px;
                min-width: 28px;
                min-height: 22px;
                outline: none;
                margin-left: 1px;
            }

            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 5px;
                border: 1px solid rgba(0, 0, 0, 0.35);
                background-color: rgba(0, 0, 0, 0.05);
            }

            QCheckBox::indicator:hover {
                border: 1px solid rgba(0, 0, 0, 0.45);
                background-color: rgba(0, 0, 0, 0.03);
            }

            QCheckBox::indicator:pressed {
                border: 1px solid rgba(0, 0, 0, 0.30);
                background-color: rgba(0, 0, 0, 0.08);
            }

            QCheckBox::indicator:checked {
                border: 1px solid rgb(0, 103, 192);
                background-color: rgb(0, 103, 192);
                image: url(:/icons/checkbox_check_light.svg);
            }

            QCheckBox::indicator:checked:hover {
                border: 1px solid rgb(0, 123, 212);
                background-color: rgb(0, 123, 212);
            }

            QCheckBox::indicator:checked:pressed {
                border: 1px solid rgb(0, 83, 172);
                background-color: rgb(0, 83, 172);
            }

            QCheckBox::indicator:indeterminate {
                border: 1px solid rgb(0, 103, 192);
                background-color: rgb(0, 103, 192);
                image: url(:/icons/checkbox_partial_light.svg);
            }

            QCheckBox:disabled {
                color: rgba(0, 0, 0, 0.36);
            }

            QCheckBox::indicator:disabled {
                border: 1px solid rgba(0, 0, 0, 0.20);
                background-color: rgba(0, 0, 0, 0.03);
            }

            QCheckBox::indicator:checked:disabled {
                border: 1px solid rgba(0, 103, 192, 0.40);
                background-color: rgba(0, 103, 192, 0.40);
            }
        """

    @staticmethod
    def get_full_style(theme: Theme) -> str:
        """Get the complete style sheet for all components."""
        return "\n".join([
            FluentStyleSheet.get_combo_box_style(theme),
            FluentStyleSheet.get_popup_style(theme),
            FluentStyleSheet.get_checkbox_style(theme),
        ])