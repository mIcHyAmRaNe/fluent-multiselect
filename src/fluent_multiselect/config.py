# FILE: src/fluent_multiselect/config.py
"""Configuration and customization options for FluentMultiSelectComboBox."""

from dataclasses import dataclass, field

from PyQt6.QtGui import QColor


@dataclass
class CheckboxStyle:
    """Style configuration for checkboxes."""

    size: int = 18
    margin: int = 8
    border_radius: int = 4
    border_width: float = 1.5
    check_mark_width: float = 2.0


@dataclass
class AnimationConfig:
    """Animation configuration."""

    enabled: bool = True
    arrow_duration: int = 150  # ms


@dataclass
class ColorScheme:
    """Color scheme for theming."""

    # Background colors
    background: QColor = field(default_factory=lambda: QColor(255, 255, 255, 15))
    background_hover: QColor = field(default_factory=lambda: QColor(255, 255, 255, 21))
    background_pressed: QColor = field(default_factory=lambda: QColor(255, 255, 255, 8))
    background_disabled: QColor = field(default_factory=lambda: QColor(255, 255, 255, 11))

    # Border colors
    border: QColor = field(default_factory=lambda: QColor(255, 255, 255, 14))
    border_hover: QColor = field(default_factory=lambda: QColor(255, 255, 255, 21))

    # Accent / Focus
    accent: QColor = field(default_factory=lambda: QColor(138, 180, 248))

    # Text colors
    text: QColor = field(default_factory=lambda: QColor(255, 255, 255))
    text_secondary: QColor = field(default_factory=lambda: QColor(255, 255, 255, 163))
    text_disabled: QColor = field(default_factory=lambda: QColor(255, 255, 255, 93))
    placeholder: QColor = field(default_factory=lambda: QColor(255, 255, 255, 155))

    # Checkbox colors
    checkbox_background: QColor = field(default_factory=lambda: QColor(255, 255, 255, 14))
    checkbox_checked: QColor = field(default_factory=lambda: QColor(138, 180, 248))
    checkbox_border: QColor = field(default_factory=lambda: QColor(255, 255, 255, 70))
    check_mark: QColor = field(default_factory=lambda: QColor(0, 0, 0))

    # Popup colors
    popup_background: QColor = field(default_factory=lambda: QColor(44, 44, 44))
    popup_border: QColor = field(default_factory=lambda: QColor(255, 255, 255, 20))
    item_hover: QColor = field(default_factory=lambda: QColor(255, 255, 255, 20))
    item_selected: QColor = field(default_factory=lambda: QColor(255, 255, 255, 15))

    # Arrow
    arrow: QColor = field(default_factory=lambda: QColor(255, 255, 255, 200))

    # Shadow
    shadow: QColor = field(default_factory=lambda: QColor(0, 0, 0, 80))


@dataclass
class VisualConfig:
    """Visual effects configuration."""

    # Focus border
    focus_border_enabled: bool = True
    focus_border_width: int = 2
    focus_border_position: str = "bottom"  # "bottom", "all", "none"

    # Border radius
    border_radius: int = 5
    popup_border_radius: int = 6
    item_border_radius: int = 4

    # Shadow
    shadow_enabled: bool = True
    shadow_blur_radius: int = 16
    shadow_offset_y: int = 4

    # Arrow
    arrow_size: int = 10
    arrow_animated: bool = True

    # Sizing
    min_height: int = 32
    min_width: int = 120
    item_padding_h: int = 8
    item_padding_v: int = 6


@dataclass
class ComboBoxConfig:
    """Complete configuration for FluentMultiSelectComboBox."""

    colors: ColorScheme = field(default_factory=ColorScheme)
    visual: VisualConfig = field(default_factory=VisualConfig)
    checkbox: CheckboxStyle = field(default_factory=CheckboxStyle)
    animation: AnimationConfig = field(default_factory=AnimationConfig)

    @classmethod
    def dark_theme(cls) -> "ComboBoxConfig":
        """Create a dark theme configuration."""
        return cls(
            colors=ColorScheme(
                background=QColor(255, 255, 255, 15),
                background_hover=QColor(255, 255, 255, 21),
                background_pressed=QColor(255, 255, 255, 8),
                background_disabled=QColor(255, 255, 255, 11),
                border=QColor(255, 255, 255, 14),
                border_hover=QColor(255, 255, 255, 21),
                accent=QColor(138, 180, 248),
                text=QColor(255, 255, 255),
                text_secondary=QColor(255, 255, 255, 163),
                text_disabled=QColor(255, 255, 255, 93),
                placeholder=QColor(255, 255, 255, 155),
                checkbox_background=QColor(255, 255, 255, 14),
                checkbox_checked=QColor(138, 180, 248),
                checkbox_border=QColor(255, 255, 255, 70),
                check_mark=QColor(0, 0, 0),
                popup_background=QColor(44, 44, 44),
                popup_border=QColor(255, 255, 255, 20),
                item_hover=QColor(255, 255, 255, 20),
                item_selected=QColor(255, 255, 255, 15),
                arrow=QColor(255, 255, 255, 200),
                shadow=QColor(0, 0, 0, 80),
            )
        )

    @classmethod
    def light_theme(cls) -> "ComboBoxConfig":
        """Create a light theme configuration."""
        return cls(
            colors=ColorScheme(
                background=QColor(255, 255, 255, 179),
                background_hover=QColor(249, 249, 249, 128),
                background_pressed=QColor(249, 249, 249, 77),
                background_disabled=QColor(249, 249, 249, 77),
                border=QColor(0, 0, 0, 19),
                border_hover=QColor(0, 0, 0, 27),
                accent=QColor(0, 103, 192),
                text=QColor(0, 0, 0),
                text_secondary=QColor(0, 0, 0, 163),
                text_disabled=QColor(0, 0, 0, 93),
                placeholder=QColor(0, 0, 0, 155),
                checkbox_background=QColor(0, 0, 0, 14),
                checkbox_checked=QColor(0, 103, 192),
                checkbox_border=QColor(0, 0, 0, 90),
                check_mark=QColor(255, 255, 255),
                popup_background=QColor(252, 252, 252),
                popup_border=QColor(0, 0, 0, 20),
                item_hover=QColor(0, 0, 0, 13),
                item_selected=QColor(0, 0, 0, 8),
                arrow=QColor(0, 0, 0, 200),
                shadow=QColor(0, 0, 0, 40),
            )
        )

    def copy(self) -> "ComboBoxConfig":
        """Create a deep copy of this configuration."""
        import copy
        return copy.deepcopy(self)