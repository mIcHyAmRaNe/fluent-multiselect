# FILE: src/fluent_multiselect/colors.py
"""Fluent Design color definitions."""

from PyQt6.QtGui import QColor


class FluentColors:
    """Fluent Design color palette for light and dark themes."""

    # Dark theme colors
    DARK_BACKGROUND = QColor(32, 32, 32)
    DARK_SURFACE = QColor(44, 44, 44)
    DARK_BORDER = QColor(255, 255, 255, 14)
    DARK_BORDER_HOVER = QColor(255, 255, 255, 21)
    DARK_TEXT = QColor(255, 255, 255)
    DARK_TEXT_SECONDARY = QColor(255, 255, 255, 163)
    DARK_TEXT_DISABLED = QColor(255, 255, 255, 92)  # QSS: rgba(255, 255, 255, 0.36)
    DARK_ACCENT = QColor(138, 180, 248)
    DARK_ACCENT_HOVER = QColor(158, 195, 255)
    DARK_ACCENT_PRESSED = QColor(118, 165, 235)
    DARK_CHECKBOX_BG = QColor(255, 255, 255, 14)
    DARK_CHECKBOX_BORDER = QColor(255, 255, 255, 70)  # QSS: rgba(255, 255, 255, 0.27)
    DARK_CHECKBOX_CHECKED = QColor(138, 180, 248)
    DARK_CHECK_MARK = QColor(0, 0, 0)

    # Light theme colors
    LIGHT_BACKGROUND = QColor(255, 255, 255)
    LIGHT_SURFACE = QColor(252, 252, 252)
    LIGHT_BORDER = QColor(0, 0, 0, 19)
    LIGHT_BORDER_HOVER = QColor(0, 0, 0, 27)
    LIGHT_TEXT = QColor(0, 0, 0)
    LIGHT_TEXT_SECONDARY = QColor(0, 0, 0, 163)
    LIGHT_TEXT_DISABLED = QColor(0, 0, 0, 92)  # QSS: rgba(0, 0, 0, 0.36)
    LIGHT_ACCENT = QColor(0, 103, 192)
    LIGHT_ACCENT_HOVER = QColor(0, 123, 212)
    LIGHT_ACCENT_PRESSED = QColor(0, 83, 172)
    LIGHT_CHECKBOX_BG = QColor(0, 0, 0, 14)
    LIGHT_CHECKBOX_BORDER = QColor(0, 0, 0, 90)  # QSS: rgba(0, 0, 0, 0.35)
    LIGHT_CHECKBOX_CHECKED = QColor(0, 103, 192)
    LIGHT_CHECK_MARK = QColor(255, 255, 255)

    @classmethod
    def get_accent_color(cls, dark: bool = True) -> QColor:
        """Get the accent color for the specified theme."""
        return cls.DARK_ACCENT if dark else cls.LIGHT_ACCENT

    @classmethod
    def get_text_color(cls, dark: bool = True) -> QColor:
        """Get the primary text color for the specified theme."""
        return cls.DARK_TEXT if dark else cls.LIGHT_TEXT

    @classmethod
    def get_disabled_text_color(cls, dark: bool = True) -> QColor:
        """Get the disabled text color for the specified theme (QSS: 0.36 alpha)."""
        return cls.DARK_TEXT_DISABLED if dark else cls.LIGHT_TEXT_DISABLED

    @classmethod
    def get_checkbox_colors(cls, dark: bool = True) -> dict:
        """Get all checkbox-related colors for the specified theme."""
        if dark:
            return {
                'background': cls.DARK_CHECKBOX_BG,
                'border': cls.DARK_CHECKBOX_BORDER,
                'checked': cls.DARK_CHECKBOX_CHECKED,
                'check_mark': cls.DARK_CHECK_MARK,
                'accent_hover': cls.DARK_ACCENT_HOVER,
                'accent_pressed': cls.DARK_ACCENT_PRESSED,
            }
        else:
            return {
                'background': cls.LIGHT_CHECKBOX_BG,
                'border': cls.LIGHT_CHECKBOX_BORDER,
                'checked': cls.LIGHT_CHECKBOX_CHECKED,
                'check_mark': cls.LIGHT_CHECK_MARK,
                'accent_hover': cls.LIGHT_ACCENT_HOVER,
                'accent_pressed': cls.LIGHT_ACCENT_PRESSED,
            }