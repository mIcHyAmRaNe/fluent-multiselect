# FILE: src\fluent_multiselect\chips.py
# FILE: src/fluent_multiselect/chips.py
"""Fluent Design chip widgets for multi-select display."""

from typing import List, Tuple, Optional

from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import (
    QPainter,
    QColor,
    QPen,
    QPainterPath,
    QFontMetrics,
    QPaintEvent,
    QMouseEvent,
    QFont,
)
from PyQt6.QtCore import Qt, pyqtSignal, QRectF, QPointF, QEvent

from .styles import Theme


class FluentChipsDisplay(QWidget):
    """
    Widget that displays selected items as chips with remove buttons.

    Each chip shows the item text and an X button to remove it.
    Chips that don't fit are shown as "+N" overflow indicator.

    Signals:
        chipRemoved: Emitted when a chip's X button is clicked, with row index.
        clicked: Emitted when clicking on empty area (to open popup).

    Example:
        display = FluentChipsDisplay(theme=Theme.DARK)
        display.setItems([(0, "Python"), (2, "JavaScript")])
        display.chipRemoved.connect(lambda idx: print(f"Remove item at row {idx}"))
    """

    chipRemoved = pyqtSignal(int)  # Emits row index of removed item
    clicked = pyqtSignal()  # Emitted when clicking on empty area

    # Visual constants
    CHIP_HEIGHT = 22
    CHIP_BORDER_RADIUS = 11
    CHIP_PADDING_LEFT = 10
    CHIP_PADDING_RIGHT = 6
    CHIP_SPACING = 4
    X_BUTTON_SIZE = 16
    X_ICON_SIZE = 3.5
    X_STROKE_WIDTH = 1.6

    def __init__(self, parent: Optional[QWidget] = None, theme: Theme = Theme.DARK):
        """
        Initialize the chips display widget.

        Args:
            parent: Parent widget.
            theme: Visual theme (Theme.DARK or Theme.LIGHT).
        """
        super().__init__(parent)
        self._theme = theme
        self._items: List[Tuple[int, str]] = []  # List of (row_idx, text)
        self._chip_rects: List[Tuple[int, QRectF, QRectF]] = []  # (row_idx, chip_rect, x_rect)
        self._hovered_chip: int = -1
        self._hovered_x: int = -1
        self._placeholder_text: str = ""
        self._max_visible_chips: Optional[int] = None

        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.setMinimumHeight(28)

        # Set font
        font = QFont("Segoe UI", 9)
        self.setFont(font)

    def setItems(self, items: List[Tuple[int, str]]) -> None:
        """
        Set the items to display as chips.

        Args:
            items: List of (row_index, display_text) tuples.
        """
        self._items = list(items)
        self._chip_rects.clear()
        self._hovered_chip = -1
        self._hovered_x = -1
        self.update()

    def items(self) -> List[Tuple[int, str]]:
        """Get the current items."""
        return list(self._items)

    def setPlaceholderText(self, text: str) -> None:
        """
        Set placeholder text shown when no items are selected.

        Args:
            text: Placeholder text.
        """
        self._placeholder_text = text
        self.update()

    def placeholderText(self) -> str:
        """Get the placeholder text."""
        return self._placeholder_text

    def setMaxVisibleChips(self, count: Optional[int]) -> None:
        """
        Set maximum number of visible chips before showing overflow.

        Args:
            count: Maximum chips to show, or None for auto (based on width).
        """
        self._max_visible_chips = count
        self.update()

    def maxVisibleChips(self) -> Optional[int]:
        """Get the maximum visible chips setting."""
        return self._max_visible_chips

    def setTheme(self, theme: Theme) -> None:
        """
        Set the display theme.

        Args:
            theme: Theme.DARK or Theme.LIGHT.
        """
        self._theme = theme
        self.update()

    def theme(self) -> Theme:
        """Get the current theme."""
        return self._theme

    def clear(self) -> None:
        """Clear all chips."""
        self._items.clear()
        self._chip_rects.clear()
        self._hovered_chip = -1
        self._hovered_x = -1
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        """Paint the chips."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setFont(self.font())

        self._chip_rects.clear()

        if not self._items:
            self._draw_placeholder(painter)
            return

        self._draw_chips(painter)

    def _draw_placeholder(self, painter: QPainter) -> None:
        """Draw placeholder text when no items are selected."""
        if not self._placeholder_text:
            return

        color = self._get_placeholder_color()
        painter.setPen(color)

        text_rect = self.rect().adjusted(8, 0, -35, 0)
        painter.drawText(
            text_rect,
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            self._placeholder_text,
        )

    def _draw_chips(self, painter: QPainter) -> None:
        """Draw all chips with overflow handling."""
        x = self.CHIP_SPACING
        y = (self.height() - self.CHIP_HEIGHT) // 2
        max_width = self.width() - 40  # Leave space for dropdown arrow

        fm = QFontMetrics(self.font())
        visible_count = 0

        for row_idx, text in self._items:
            # Check max visible limit
            if self._max_visible_chips is not None:
                if visible_count >= self._max_visible_chips:
                    break

            # Calculate chip width
            text_width = fm.horizontalAdvance(text)
            chip_width = (
                self.CHIP_PADDING_LEFT
                + text_width
                + self.CHIP_PADDING_RIGHT
                + self.X_BUTTON_SIZE
                + 2
            )

            # Check if chip fits
            if x + chip_width > max_width and visible_count > 0:
                break

            # Create rectangles
            chip_rect = QRectF(x, y, chip_width, self.CHIP_HEIGHT)
            x_rect = QRectF(
                x + chip_width - self.X_BUTTON_SIZE - 4,
                y + (self.CHIP_HEIGHT - self.X_BUTTON_SIZE) / 2,
                self.X_BUTTON_SIZE,
                self.X_BUTTON_SIZE,
            )

            # Draw the chip
            self._draw_chip(painter, chip_rect, x_rect, text, row_idx)
            self._chip_rects.append((row_idx, chip_rect, x_rect))

            x += chip_width + self.CHIP_SPACING
            visible_count += 1

        # Draw overflow indicator
        remaining = len(self._items) - visible_count
        if remaining > 0:
            self._draw_overflow(painter, x, y, remaining)

    def _draw_chip(
        self, painter: QPainter, chip_rect: QRectF, x_rect: QRectF, text: str, row_idx: int
    ) -> None:
        """Draw a single chip with text and X button."""
        is_hovered = self._hovered_chip == row_idx
        is_x_hovered = self._hovered_x == row_idx

        colors = self._get_chip_colors(is_hovered, is_x_hovered)

        # Draw chip background
        path = QPainterPath()
        path.addRoundedRect(chip_rect, self.CHIP_BORDER_RADIUS, self.CHIP_BORDER_RADIUS)
        painter.fillPath(path, colors["background"])
        painter.setPen(QPen(colors["border"], 1))
        painter.drawPath(path)

        # Draw text
        text_rect = chip_rect.adjusted(
            self.CHIP_PADDING_LEFT, 0, -(self.X_BUTTON_SIZE + self.CHIP_PADDING_RIGHT), 0
        )
        painter.setPen(colors["text"])
        painter.drawText(
            text_rect.toRect(), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, text
        )

        # Draw X button hover background
        if is_x_hovered:
            x_bg_path = QPainterPath()
            x_bg_path.addEllipse(x_rect)
            painter.fillPath(x_bg_path, colors["x_hover_bg"])

        # Draw X icon
        self._draw_x_icon(painter, x_rect, colors["x"])

    def _draw_x_icon(self, painter: QPainter, rect: QRectF, color: QColor) -> None:
        """Draw the X (close) icon."""
        painter.setPen(
            QPen(color, self.X_STROKE_WIDTH, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        )

        cx, cy = rect.center().x(), rect.center().y()
        size = self.X_ICON_SIZE

        painter.drawLine(QPointF(cx - size, cy - size), QPointF(cx + size, cy + size))
        painter.drawLine(QPointF(cx - size, cy + size), QPointF(cx + size, cy - size))

    def _draw_overflow(self, painter: QPainter, x: float, y: float, count: int) -> None:
        """Draw the overflow indicator (+N)."""
        colors = self._get_chip_colors(False, False)
        overflow_text = f"+{count}"

        fm = QFontMetrics(self.font())
        text_width = fm.horizontalAdvance(overflow_text)

        # Draw overflow chip (without X button)
        chip_rect = QRectF(x, y, text_width + 16, self.CHIP_HEIGHT)

        path = QPainterPath()
        path.addRoundedRect(chip_rect, self.CHIP_BORDER_RADIUS, self.CHIP_BORDER_RADIUS)
        painter.fillPath(path, colors["overflow_bg"])
        painter.setPen(QPen(colors["border"], 1))
        painter.drawPath(path)

        # Draw text
        painter.setPen(colors["text"])
        painter.drawText(chip_rect.toRect(), Qt.AlignmentFlag.AlignCenter, overflow_text)

    def _get_chip_colors(self, is_hovered: bool, is_x_hovered: bool) -> dict:
        """Get colors for chip rendering based on theme and state."""
        if self._theme == Theme.DARK:
            return {
                "background": QColor(255, 255, 255, 35 if is_hovered else 25),
                "border": QColor(255, 255, 255, 50 if is_hovered else 35),
                "text": QColor(255, 255, 255),
                "x": QColor(255, 255, 255, 230 if is_x_hovered else 160),
                "x_hover_bg": QColor(255, 255, 255, 50),
                "overflow_bg": QColor(255, 255, 255, 15),
            }
        else:
            return {
                "background": QColor(0, 0, 0, 18 if is_hovered else 10),
                "border": QColor(0, 0, 0, 30 if is_hovered else 18),
                "text": QColor(0, 0, 0),
                "x": QColor(0, 0, 0, 210 if is_x_hovered else 130),
                "x_hover_bg": QColor(0, 0, 0, 35),
                "overflow_bg": QColor(0, 0, 0, 8),
            }

    def _get_placeholder_color(self) -> QColor:
        """Get the placeholder text color based on theme."""
        if self._theme == Theme.DARK:
            return QColor(255, 255, 255, 120)
        return QColor(0, 0, 0, 100)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Handle mouse movement for hover effects."""
        pos = event.position()
        old_chip = self._hovered_chip
        old_x = self._hovered_x
        self._hovered_chip = -1
        self._hovered_x = -1

        for row_idx, chip_rect, x_rect in self._chip_rects:
            if x_rect.contains(pos):
                self._hovered_x = row_idx
                self._hovered_chip = row_idx
                self.setCursor(Qt.CursorShape.PointingHandCursor)
                break
            elif chip_rect.contains(pos):
                self._hovered_chip = row_idx
                self.setCursor(Qt.CursorShape.ArrowCursor)
                break
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)

        if old_chip != self._hovered_chip or old_x != self._hovered_x:
            self.update()

        super().mouseMoveEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle mouse press to remove chips or open popup."""
        if event.button() != Qt.MouseButton.LeftButton:
            super().mousePressEvent(event)
            return

        pos = event.position()

        # Check if clicked on X button
        for row_idx, chip_rect, x_rect in self._chip_rects:
            if x_rect.contains(pos):
                self.chipRemoved.emit(row_idx)
                event.accept()
                return

        # Click was not on an X button, emit clicked to open popup
        self.clicked.emit()
        event.accept()

    def leaveEvent(self, event: QEvent) -> None:
        """Handle mouse leave."""
        self._hovered_chip = -1
        self._hovered_x = -1
        self.update()
        super().leaveEvent(event)

    def resizeEvent(self, event) -> None:
        """Handle resize to update chip layout."""
        super().resizeEvent(event)
        self.update()

# FILE: src\fluent_multiselect\colors.py
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

# FILE: src\fluent_multiselect\combobox.py
# FILE: src/fluent_multiselect/combobox.py
"""
Fluent Design MultiSelect ComboBox for PyQt6.

A multi-select combo box widget styled according to Windows 11 Fluent Design.
"""

from typing import Any, List, Optional, Set, Union

from PyQt6.QtWidgets import (
    QComboBox,
    QLineEdit,
    QWidget,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QStackedWidget,
)
from PyQt6.QtGui import (
    QStandardItem,
    QStandardItemModel,
    QFontMetrics,
    QCursor,
    QPainter,
    QColor,
    QPen,
    QPainterPath,
    QMouseEvent,
    QPaintEvent,
    QEnterEvent,
    QWheelEvent,
    QKeyEvent,
)
from PyQt6.QtCore import (
    Qt,
    QEvent,
    pyqtSignal,
    QObject,
    QRect,
    QPropertyAnimation,
    QEasingCurve,
    pyqtProperty,
    QRectF,
    QModelIndex,
    QAbstractItemModel,
)

from .styles import Theme, FluentStyleSheet
from .colors import FluentColors
from .delegate import FluentCheckBoxDelegate
from .chips import FluentChipsDisplay


class FluentLineEdit(QLineEdit):
    """Custom read-only line edit for the combo box display."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setCursor(Qt.CursorShape.ArrowCursor)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Prevent text selection on click."""
        event.accept()

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        """Prevent text selection on double click."""
        event.accept()


class FluentMultiSelectComboBox(QComboBox):
    """
    A Fluent Design styled multi-select combo box for PyQt6.

    This widget allows selecting multiple items from a dropdown list with
    Windows 11 Fluent Design styling.

    Signals:
        selectionChanged: Emitted when selection changes, with list of selected values.

    Example:
        combo = FluentMultiSelectComboBox(theme=Theme.DARK)
        combo.addItems(["Python", "JavaScript", "TypeScript"])
        combo.setSelectAllEnabled(True)
        combo.setChipsEnabled(True)  # Enable chips display with X buttons
        combo.selectionChanged.connect(lambda items: print(f"Selected: {items}"))
    """

    selectionChanged = pyqtSignal(list)

    # Constants
    _SELECT_ALL_DATA = "__select_all__"

    def __init__(self, parent: Optional[QWidget] = None, theme: Theme = Theme.DARK):
        """
        Initialize the FluentMultiSelectComboBox.

        Args:
            parent: Parent widget.
            theme: Theme to use (Theme.DARK or Theme.LIGHT).
        """
        super().__init__(parent)

        # Configuration
        self._theme = theme
        self._placeholder_text = ""
        self._display_delimiter = ", "
        self._output_type = "data"
        self._display_type = "text"
        self._duplicates_enabled = True
        self._max_selection_count: Optional[int] = None
        self._close_on_select = False
        self._select_all_enabled = False
        self._select_all_text = "Select All"

        # Visual configuration
        self._focus_border_enabled = False
        self._focus_border_width = 2
        self._focus_border_position = "bottom"

        # Chips configuration
        self._chips_enabled = False
        self._chips_display: Optional[FluentChipsDisplay] = None

        # State
        self._checked_rows: Set[int] = set()
        self._last_selection_snapshot: List[Any] = []
        self._in_bulk_update = False
        self._updating_text = False
        self._hovered = False
        self._pressed = False
        self._popup_visible = False
        self._arrow_rotation = 0.0

        self._setup_ui()
        self._apply_theme()
        self._connect_model_signals(self.model())
        self._rebuild_checked_cache()
        self.updateText()

    def _setup_ui(self) -> None:
        """Setup the UI components."""
        self.setEditable(True)
        line_edit = FluentLineEdit(self)
        self.setLineEdit(line_edit)
        line_edit.installEventFilter(self)

        self._delegate = FluentCheckBoxDelegate(self, self._theme)
        self.setItemDelegate(self._delegate)

        view = self.view()
        view.setMouseTracking(True)
        view.viewport().installEventFilter(self)
        view.installEventFilter(self)

        if hasattr(view, "setUniformItemSizes"):
            view.setUniformItemSizes(True)

        # Setup arrow animation
        self._arrow_animation = QPropertyAnimation(self, b"arrowRotation")
        self._arrow_animation.setDuration(150)
        self._arrow_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.setMinimumHeight(32)
        self.setMinimumWidth(120)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def _setup_chips_display(self) -> None:
        """Setup the chips display widget."""
        if self._chips_display is not None:
            return

        self._chips_display = FluentChipsDisplay(self, self._theme)
        self._chips_display.setPlaceholderText(self._placeholder_text)
        self._chips_display.chipRemoved.connect(self._on_chip_removed)
        self._chips_display.clicked.connect(self._on_chips_clicked)

        # Position the chips display over the line edit
        self._update_chips_geometry()

    def _update_chips_geometry(self) -> None:
        """Update the chips display geometry to match the combo box."""
        if self._chips_display is None:
            return

        # Leave space for the dropdown arrow
        rect = self.rect()
        chips_rect = rect.adjusted(1, 1, -30, -1)
        self._chips_display.setGeometry(chips_rect)

    def _on_chip_removed(self, row_idx: int) -> None:
        """Handle chip removal by unchecking the item."""
        self.setItemChecked(row_idx, False)

    def _on_chips_clicked(self) -> None:
        """Handle click on chips display to toggle popup."""
        if self._popup_visible:
            self.hidePopup()
        else:
            self.showPopup()

    # ==================== Properties ====================

    @pyqtProperty(float)
    def arrowRotation(self) -> float:
        """Get the current arrow rotation angle."""
        return self._arrow_rotation

    @arrowRotation.setter
    def arrowRotation(self, value: float) -> None:
        """Set the arrow rotation angle."""
        self._arrow_rotation = value
        self.update()

    # ==================== Theme ====================

    def _apply_theme(self) -> None:
        """Apply the current theme styling."""
        self._delegate.setTheme(self._theme)
        self.setStyleSheet(FluentStyleSheet.get_combo_box_style(self._theme))
        self.view().setStyleSheet(FluentStyleSheet.get_popup_style(self._theme))

        if self._chips_display is not None:
            self._chips_display.setTheme(self._theme)

        self.update()

    def setTheme(self, theme: Theme) -> None:
        """
        Set the theme for the combo box.

        Args:
            theme: The theme to apply (Theme.DARK or Theme.LIGHT).
        """
        self._theme = theme
        self._apply_theme()

    def theme(self) -> Theme:
        """Get the current theme."""
        return self._theme

    # ==================== Chips Display ====================

    def setChipsEnabled(self, enabled: bool) -> None:
        """
        Enable or disable the chips display mode.

        When enabled, selected items are shown as chips with X buttons
        to remove them individually.

        Args:
            enabled: Whether to enable chips display.

        Example:
            combo.setChipsEnabled(True)
            # Now selected items appear as removable chips
        """
        self._chips_enabled = enabled

        if enabled:
            self._setup_chips_display()
            self._chips_display.show()
            self.lineEdit().hide()
        else:
            if self._chips_display is not None:
                self._chips_display.hide()
            self.lineEdit().show()

        self.updateText()

    def isChipsEnabled(self) -> bool:
        """
        Check if chips display mode is enabled.

        Returns:
            True if chips are enabled, False otherwise.
        """
        return self._chips_enabled

    def setMaxVisibleChips(self, count: Optional[int]) -> None:
        """
        Set maximum number of visible chips before showing overflow.

        Args:
            count: Maximum chips to display, or None for auto (based on width).

        Example:
            combo.setMaxVisibleChips(3)  # Show max 3 chips, then "+N"
        """
        if self._chips_display is not None:
            self._chips_display.setMaxVisibleChips(count)

    def maxVisibleChips(self) -> Optional[int]:
        """Get the maximum visible chips setting."""
        if self._chips_display is not None:
            return self._chips_display.maxVisibleChips()
        return None

    # ==================== Paint Events ====================

    def _draw_focus_border(self, painter: QPainter, rect: QRect, color: QColor) -> None:
        """Draw the focus border based on configuration."""
        if self._focus_border_position == "none":
            return

        if self._focus_border_position == "bottom":
            focus_rect = QRectF(
                rect.left() + 1,
                rect.bottom() - self._focus_border_width,
                rect.width() - 2,
                self._focus_border_width,
            )
            focus_path = QPainterPath()
            focus_path.addRoundedRect(focus_rect, 1, 1)
            painter.fillPath(focus_path, color)

        elif self._focus_border_position == "all":
            painter.setPen(QPen(color, self._focus_border_width))
            border_path = QPainterPath()
            border_path.addRoundedRect(QRectF(rect.adjusted(1, 1, -1, -1)), 5, 5)
            painter.drawPath(border_path)

    def paintEvent(self, event: QPaintEvent) -> None:
        """Custom paint event for Fluent Design styling."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        colors = self._get_state_colors()
        rect = self.rect()

        # Background
        path = QPainterPath()
        path.addRoundedRect(QRectF(rect.adjusted(0, 0, -1, -1)), 5, 5)
        painter.fillPath(path, colors["background"])
        painter.setPen(QPen(colors["border"], 1))
        painter.drawPath(path)

        # Focus border
        if self._focus_border_enabled and (self.hasFocus() or self._popup_visible):
            self._draw_focus_border(painter, rect, colors["accent"])

        # Arrow
        self._draw_arrow(painter, rect, colors["arrow"])

    def _get_state_colors(self) -> dict:
        """Get colors based on current state and theme."""
        if self._theme == Theme.DARK:
            if not self.isEnabled():
                bg = QColor(255, 255, 255, 11)
                border = QColor(255, 255, 255, 14)
            elif self._pressed:
                bg = QColor(255, 255, 255, 8)
                border = QColor(255, 255, 255, 14)
            elif self._hovered:
                bg = QColor(255, 255, 255, 21)
                border = QColor(255, 255, 255, 21)
            else:
                bg = QColor(255, 255, 255, 15)
                border = QColor(255, 255, 255, 14)
            return {
                "background": bg,
                "border": border,
                "accent": FluentColors.DARK_ACCENT,
                "arrow": QColor(255, 255, 255, 200),
            }
        else:
            if not self.isEnabled():
                bg = QColor(249, 249, 249, 77)
                border = QColor(0, 0, 0, 15)
            elif self._pressed:
                bg = QColor(249, 249, 249, 77)
                border = QColor(0, 0, 0, 15)
            elif self._hovered:
                bg = QColor(249, 249, 249, 128)
                border = QColor(0, 0, 0, 19)
            else:
                bg = QColor(255, 255, 255, 179)
                border = QColor(0, 0, 0, 19)
            return {
                "background": bg,
                "border": border,
                "accent": FluentColors.LIGHT_ACCENT,
                "arrow": QColor(0, 0, 0, 200),
            }

    def _draw_arrow(self, painter: QPainter, rect: QRect, color: QColor) -> None:
        """Draw the dropdown arrow."""
        painter.save()
        arrow_size = 10
        arrow_x = rect.right() - 20
        arrow_y = rect.center().y()

        painter.translate(arrow_x, arrow_y)
        painter.rotate(self._arrow_rotation)

        painter.setPen(
            QPen(
                color,
                1.5,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
                Qt.PenJoinStyle.RoundJoin,
            )
        )

        path = QPainterPath()
        path.moveTo(-arrow_size / 2, -arrow_size / 4)
        path.lineTo(0, arrow_size / 4)
        path.lineTo(arrow_size / 2, -arrow_size / 4)
        painter.drawPath(path)
        painter.restore()

    # ==================== Event Handlers ====================

    def enterEvent(self, event: QEnterEvent) -> None:
        """Handle mouse enter."""
        self._hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event: QEvent) -> None:
        """Handle mouse leave."""
        self._hovered = False
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle mouse press."""
        self._pressed = True
        self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Handle mouse release."""
        self._pressed = False
        self.update()

        # Only toggle popup if not clicking on chips
        if self._chips_enabled and self._chips_display is not None:
            # Let chips handle their own clicks
            chips_rect = self._chips_display.geometry()
            if chips_rect.contains(event.pos()):
                return

        if self._popup_visible:
            self.hidePopup()
        else:
            self.showPopup()

    def wheelEvent(self, event: QWheelEvent) -> None:
        """Ignore wheel events to prevent changing selection by scrolling."""
        if self._popup_visible:
            self.view().wheelEvent(event)
        else:
            event.ignore()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Handle key press events."""
        key = event.key()

        if key == Qt.Key.Key_Escape and self._popup_visible:
            self.hidePopup()
            event.accept()
            return

        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space):
            if not self._popup_visible:
                self.showPopup()
            event.accept()
            return

        super().keyPressEvent(event)

    def showPopup(self) -> None:
        """Show the popup with animation."""
        self._popup_visible = True

        self._arrow_animation.stop()
        self._arrow_animation.setStartValue(self._arrow_rotation)
        self._arrow_animation.setEndValue(180)
        self._arrow_animation.start()

        view = self.view()
        shadow = QGraphicsDropShadowEffect(view)
        shadow.setBlurRadius(16)
        shadow.setOffset(0, 4)
        shadow_alpha = 80 if self._theme == Theme.DARK else 40
        shadow.setColor(QColor(0, 0, 0, shadow_alpha))
        view.setGraphicsEffect(shadow)

        super().showPopup()
        self.update()

    def hidePopup(self) -> None:
        """Hide the popup with animation."""
        self._popup_visible = False

        self._arrow_animation.stop()
        self._arrow_animation.setStartValue(self._arrow_rotation)
        self._arrow_animation.setEndValue(0)
        self._arrow_animation.start()

        super().hidePopup()
        self.update()

    def resizeEvent(self, event) -> None:
        """Handle resize events."""
        super().resizeEvent(event)
        self._update_chips_geometry()
        self.updateText()

    def setModel(self, model: QAbstractItemModel) -> None:
        """Override to reconnect model signals."""
        old_model = self.model()
        if old_model:
            self._disconnect_model_signals(old_model)

        super().setModel(model)

        self._connect_model_signals(model)
        self._rebuild_checked_cache()
        self.updateText()

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        """Handle events for child widgets."""
        event_type = event.type()

        # Line edit events (only when chips not enabled)
        if obj == self.lineEdit() and not self._chips_enabled:
            if event_type == QEvent.Type.MouseButtonRelease:
                if self._popup_visible:
                    self.hidePopup()
                else:
                    self.showPopup()
                return True
            elif event_type == QEvent.Type.KeyPress:
                self.keyPressEvent(event)
                return True

        # View viewport click
        if obj == self.view().viewport():
            if event_type == QEvent.Type.MouseButtonRelease:
                pos = event.position().toPoint()
                index = self.view().indexAt(pos)
                if index.isValid():
                    self._toggle_item(index.row())
                    return True

        # View keyboard events
        if obj in (self.view(), self.view().viewport()):
            if event_type == QEvent.Type.KeyPress:
                key = event.key()
                if key in (Qt.Key.Key_Space, Qt.Key.Key_Return, Qt.Key.Key_Enter):
                    index = self.view().currentIndex()
                    if index.isValid():
                        self._toggle_item(index.row())
                        return True
                elif key == Qt.Key.Key_Escape:
                    self.hidePopup()
                    return True

        return super().eventFilter(obj, event)

    def _toggle_item(self, row: int) -> None:
        """Toggle the check state of an item."""
        model = self.model()
        if not isinstance(model, QStandardItemModel):
            return

        # Handle Select All
        if self._select_all_enabled and row == 0:
            sa_item = model.item(0)
            if sa_item is None:
                return
            state = sa_item.data(Qt.ItemDataRole.CheckStateRole)
            if state in (Qt.CheckState.Unchecked, Qt.CheckState.PartiallyChecked):
                self.selectAll()
            else:
                self.clearSelection()
        else:
            item = model.item(row)
            if item is None:
                return

            if not (item.flags() & Qt.ItemFlag.ItemIsEnabled):
                return

            state = item.data(Qt.ItemDataRole.CheckStateRole)
            new_state = (
                Qt.CheckState.Unchecked if state == Qt.CheckState.Checked else Qt.CheckState.Checked
            )

            if new_state == Qt.CheckState.Checked and not self._can_select_more(1):
                self._notify_limit_reached()
                return

            item.setData(new_state, Qt.ItemDataRole.CheckStateRole)
            self._update_checked_cache_for_row(row, new_state == Qt.CheckState.Checked)

        self._sync_select_all_state()
        self.updateText()
        self._emit_selection_if_changed()

        if self._close_on_select:
            self.hidePopup()

    def _update_checked_cache_for_row(self, row: int, checked: bool) -> None:
        """Update the checked cache for a single row."""
        if checked:
            self._checked_rows.add(row)
        else:
            self._checked_rows.discard(row)

    # ==================== Public API: Adding Items ====================

    def addItem(
        self, text: str, data: Any = None, *, enabled: bool = True, checked: bool = False
    ) -> None:
        """
        Add an item to the combo box.

        Args:
            text: The display text for the item.
            data: Optional data associated with the item.
            enabled: Whether the item should be enabled.
            checked: Whether the item should be initially checked.
        """
        model = self.model()
        if not isinstance(model, QStandardItemModel):
            return

        if not self._duplicates_enabled:
            for i in range(self._first_option_row(), model.rowCount()):
                existing = model.item(i)
                if existing and existing.text() == text:
                    return

        item = QStandardItem()
        item.setText(text)
        item.setData(data if data is not None else text, Qt.ItemDataRole.UserRole)

        flags = Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsSelectable
        if enabled:
            flags |= Qt.ItemFlag.ItemIsEnabled
        item.setFlags(flags)

        initial_state = Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked
        item.setData(initial_state, Qt.ItemDataRole.CheckStateRole)

        model.appendRow(item)

        if checked:
            self._checked_rows.add(model.rowCount() - 1)

        self._sync_select_all_state()
        self.updateText()

    def addItems(self, texts: List[str], data_list: Optional[List[Any]] = None) -> None:
        """
        Add multiple items to the combo box.

        Args:
            texts: List of display texts.
            data_list: Optional list of data associated with each item.
        """
        if data_list is None:
            data_list = [None] * len(texts)

        self._begin_bulk_update()
        try:
            for text, data in zip(texts, data_list):
                self.addItem(text, data)
        finally:
            self._end_bulk_update()

    def insertItem(self, index: int, text: str, data: Any = None, *, enabled: bool = True) -> None:
        """
        Insert an item at a specific position.

        Args:
            index: Position to insert at.
            text: The display text for the item.
            data: Optional data associated with the item.
            enabled: Whether the item should be enabled.
        """
        model = self.model()
        if not isinstance(model, QStandardItemModel):
            return

        actual_index = max(self._first_option_row(), index)

        item = QStandardItem()
        item.setText(text)
        item.setData(data if data is not None else text, Qt.ItemDataRole.UserRole)

        flags = Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsSelectable
        if enabled:
            flags |= Qt.ItemFlag.ItemIsEnabled
        item.setFlags(flags)
        item.setData(Qt.CheckState.Unchecked, Qt.ItemDataRole.CheckStateRole)

        model.insertRow(actual_index, item)

        new_checked = set()
        for r in self._checked_rows:
            if r >= actual_index:
                new_checked.add(r + 1)
            else:
                new_checked.add(r)
        self._checked_rows = new_checked

        self._sync_select_all_state()
        self.updateText()

    def removeItem(self, index: int) -> None:
        """
        Remove an item at a specific index.

        Args:
            index: Index of item to remove.
        """
        model = self.model()
        if not isinstance(model, QStandardItemModel):
            return

        if not self._is_option_row(index):
            return

        if index < 0 or index >= model.rowCount():
            return

        model.removeRow(index)

        self._checked_rows.discard(index)
        new_checked = set()
        for r in self._checked_rows:
            if r > index:
                new_checked.add(r - 1)
            else:
                new_checked.add(r)
        self._checked_rows = new_checked

        self._sync_select_all_state()
        self.updateText()
        self._emit_selection_if_changed()

    def clear(self) -> None:
        """Clear all items from the combo box."""
        model = self.model()
        if isinstance(model, QStandardItemModel):
            model.clear()
        self._checked_rows.clear()
        self._last_selection_snapshot = []
        self._select_all_enabled = False
        self.lineEdit().clear()

        if self._chips_display is not None:
            self._chips_display.clear()

        self.updateText()

    def count(self) -> int:
        """Get the number of items (excluding Select All)."""
        total = self.model().rowCount()
        return total - self._first_option_row()

    def itemText(self, index: int) -> str:
        """Get the text of an item."""
        model = self.model()
        if isinstance(model, QStandardItemModel):
            item = model.item(index)
            if item:
                return item.text()
        return ""

    def itemData(self, index: int, role: int = Qt.ItemDataRole.UserRole) -> Any:
        """Get the data of an item."""
        model = self.model()
        if isinstance(model, QStandardItemModel):
            item = model.item(index)
            if item:
                return item.data(role)
        return None

    def setItemText(self, index: int, text: str) -> None:
        """Set the text of an item."""
        model = self.model()
        if isinstance(model, QStandardItemModel):
            item = model.item(index)
            if item:
                item.setText(text)
                self.updateText()

    def setItemData(self, index: int, data: Any, role: int = Qt.ItemDataRole.UserRole) -> None:
        """Set the data of an item."""
        model = self.model()
        if isinstance(model, QStandardItemModel):
            item = model.item(index)
            if item:
                item.setData(data, role)

    def setItemEnabled(self, index: int, enabled: bool) -> None:
        """Enable or disable an item."""
        model = self.model()
        if isinstance(model, QStandardItemModel):
            item = model.item(index)
            if item:
                flags = item.flags()
                if enabled:
                    flags |= Qt.ItemFlag.ItemIsEnabled
                else:
                    flags &= ~Qt.ItemFlag.ItemIsEnabled
                item.setFlags(flags)

    def isItemEnabled(self, index: int) -> bool:
        """Check if an item is enabled."""
        model = self.model()
        if isinstance(model, QStandardItemModel):
            item = model.item(index)
            if item:
                return bool(item.flags() & Qt.ItemFlag.ItemIsEnabled)
        return False

    # ==================== Public API: Placeholder ====================

    def setPlaceholderText(self, text: str) -> None:
        """Set the placeholder text shown when nothing is selected."""
        self._placeholder_text = text
        self.lineEdit().setPlaceholderText(text)

        if self._chips_display is not None:
            self._chips_display.setPlaceholderText(text)

        self.updateText()

    def placeholderText(self) -> str:
        """Get the placeholder text."""
        return self._placeholder_text

    # ==================== Public API: Selection ====================

    def currentData(self, role: int = Qt.ItemDataRole.UserRole) -> List[Any]:
        """Get the data values of all selected items."""
        self._rebuild_checked_cache()
        model = self.model()
        if not isinstance(model, QStandardItemModel):
            return []

        rows = sorted(r for r in self._checked_rows if self._is_option_row(r))
        result = []

        for i in rows:
            item = model.item(i)
            if item:
                if self._output_type == "data":
                    result.append(item.data(role))
                else:
                    result.append(item.text())
        return result

    def currentTexts(self) -> List[str]:
        """Get the display texts of all selected items."""
        self._rebuild_checked_cache()
        model = self.model()
        if not isinstance(model, QStandardItemModel):
            return []

        rows = sorted(r for r in self._checked_rows if self._is_option_row(r))
        result = []

        for i in rows:
            item = model.item(i)
            if item:
                result.append(item.text())
        return result

    def currentText(self) -> str:
        """Get the display texts of selected items as a joined string."""
        texts = self.currentTexts()
        return self._display_delimiter.join(texts) if texts else ""

    def setCurrentTexts(self, texts: List[str]) -> None:
        """Select items by their display texts."""
        to_select = set(texts)
        model = self.model()
        if not isinstance(model, QStandardItemModel):
            return

        self._begin_bulk_update()
        try:
            selected_count = 0
            for i in range(self._first_option_row(), model.rowCount()):
                item = model.item(i)
                if item:
                    should_check = item.text() in to_select
                    if should_check:
                        if self._can_select_more(1 - selected_count):
                            item.setData(Qt.CheckState.Checked, Qt.ItemDataRole.CheckStateRole)
                            selected_count += 1
                        else:
                            item.setData(Qt.CheckState.Unchecked, Qt.ItemDataRole.CheckStateRole)
                    else:
                        item.setData(Qt.CheckState.Unchecked, Qt.ItemDataRole.CheckStateRole)
        finally:
            self._end_bulk_update()

    def setCurrentText(self, value: Union[str, List[str]]) -> None:
        """Select items - accepts string (delimiter-separated) or list."""
        if isinstance(value, str):
            items = [item.strip() for item in value.split(self._display_delimiter) if item.strip()]
            self.setCurrentTexts(items)
        elif isinstance(value, list):
            self.setCurrentTexts(value)

    def setCurrentIndexes(self, indexes: List[int]) -> None:
        """Select items by their indexes."""
        model = self.model()
        if not isinstance(model, QStandardItemModel):
            return

        self._begin_bulk_update()
        try:
            allowed = set(i for i in indexes if self._is_option_row(i) and i < model.rowCount())

            if self._max_selection_count is not None and len(allowed) > self._max_selection_count:
                allowed = set(sorted(allowed)[: self._max_selection_count])

            for i in range(self._first_option_row(), model.rowCount()):
                item = model.item(i)
                if item:
                    new_state = Qt.CheckState.Checked if i in allowed else Qt.CheckState.Unchecked
                    item.setData(new_state, Qt.ItemDataRole.CheckStateRole)
        finally:
            self._end_bulk_update()

    def currentIndexes(self) -> List[int]:
        """Get the indexes of all selected items."""
        self._rebuild_checked_cache()
        return sorted(r for r in self._checked_rows if self._is_option_row(r))

    def getCurrentIndexes(self) -> List[int]:
        """Alias for currentIndexes()."""
        return self.currentIndexes()

    def findText(self, text: str, flags: Qt.MatchFlag = Qt.MatchFlag.MatchExactly) -> int:
        """Find the index of an item by its text."""
        model = self.model()
        if not isinstance(model, QStandardItemModel):
            return -1

        case_sensitive = not (flags & Qt.MatchFlag.MatchCaseSensitive)

        for i in range(self._first_option_row(), model.rowCount()):
            item = model.item(i)
            if item:
                item_text = item.text()
                if flags & Qt.MatchFlag.MatchContains:
                    if text.lower() in item_text.lower() if case_sensitive else text in item_text:
                        return i
                elif flags & Qt.MatchFlag.MatchStartsWith:
                    compare_text = item_text.lower() if case_sensitive else item_text
                    search_text = text.lower() if case_sensitive else text
                    if compare_text.startswith(search_text):
                        return i
                else:
                    if case_sensitive:
                        if item_text.lower() == text.lower():
                            return i
                    else:
                        if item_text == text:
                            return i
        return -1

    def findData(self, data: Any, role: int = Qt.ItemDataRole.UserRole) -> int:
        """Find the index of an item by its data."""
        model = self.model()
        if not isinstance(model, QStandardItemModel):
            return -1

        for i in range(self._first_option_row(), model.rowCount()):
            item = model.item(i)
            if item and item.data(role) == data:
                return i
        return -1

    def isItemChecked(self, index: int) -> bool:
        """Check if an item is checked."""
        model = self.model()
        if isinstance(model, QStandardItemModel):
            item = model.item(index)
            if item:
                return item.checkState() == Qt.CheckState.Checked
        return False

    def setItemChecked(self, index: int, checked: bool) -> None:
        """Set the checked state of an item."""
        model = self.model()
        if not isinstance(model, QStandardItemModel):
            return

        if not self._is_option_row(index):
            return

        item = model.item(index)
        if item is None:
            return

        if checked and not self._can_select_more(1):
            self._notify_limit_reached()
            return

        new_state = Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked
        item.setData(new_state, Qt.ItemDataRole.CheckStateRole)
        self._update_checked_cache_for_row(index, checked)
        self._sync_select_all_state()
        self.updateText()
        self._emit_selection_if_changed()

    def selectAll(self) -> None:
        """Select all enabled items."""
        model = self.model()
        if not isinstance(model, QStandardItemModel):
            return

        self._begin_bulk_update()
        try:
            count = 0
            for i in range(self._first_option_row(), model.rowCount()):
                item = model.item(i)
                if item and (item.flags() & Qt.ItemFlag.ItemIsEnabled):
                    if self._max_selection_count is not None and count >= self._max_selection_count:
                        item.setData(Qt.CheckState.Unchecked, Qt.ItemDataRole.CheckStateRole)
                    else:
                        item.setData(Qt.CheckState.Checked, Qt.ItemDataRole.CheckStateRole)
                        count += 1
        finally:
            self._end_bulk_update()

    def clearSelection(self) -> None:
        """Clear all selections."""
        model = self.model()
        if not isinstance(model, QStandardItemModel):
            return

        self._begin_bulk_update()
        try:
            for i in range(self._first_option_row(), model.rowCount()):
                item = model.item(i)
                if item:
                    item.setData(Qt.CheckState.Unchecked, Qt.ItemDataRole.CheckStateRole)
        finally:
            self._end_bulk_update()

    def selectionCount(self) -> int:
        """Get the number of selected items."""
        self._rebuild_checked_cache()
        return len([r for r in self._checked_rows if self._is_option_row(r)])

    def hasSelection(self) -> bool:
        """Check if any items are selected."""
        return self.selectionCount() > 0

    # ==================== Public API: Select All ====================

    def setSelectAllEnabled(self, enabled: bool, text: str = "Select All") -> None:
        """Enable or disable the "Select All" option."""
        model = self.model()
        if not isinstance(model, QStandardItemModel):
            return

        self._select_all_enabled = enabled
        self._select_all_text = text

        if enabled:
            if model.rowCount() > 0:
                first_item = model.item(0)
                if (
                    first_item
                    and first_item.data(Qt.ItemDataRole.UserRole) == self._SELECT_ALL_DATA
                ):
                    first_item.setText(text)
                    return

            sa = QStandardItem()
            sa.setText(self._select_all_text)
            sa.setData(self._SELECT_ALL_DATA, Qt.ItemDataRole.UserRole)
            sa.setFlags(
                Qt.ItemFlag.ItemIsEnabled
                | Qt.ItemFlag.ItemIsUserCheckable
                | Qt.ItemFlag.ItemIsSelectable
            )
            sa.setData(Qt.CheckState.Unchecked, Qt.ItemDataRole.CheckStateRole)
            model.insertRow(0, sa)

            new_checked = set(r + 1 for r in self._checked_rows)
            self._checked_rows = new_checked
        else:
            if model.rowCount() > 0:
                first_item = model.item(0)
                if (
                    first_item
                    and first_item.data(Qt.ItemDataRole.UserRole) == self._SELECT_ALL_DATA
                ):
                    model.removeRow(0)

                    new_checked = set(r - 1 for r in self._checked_rows if r > 0)
                    self._checked_rows = new_checked

        self._sync_select_all_state()
        self.updateText()

    def isSelectAllEnabled(self) -> bool:
        """Check if Select All option is enabled."""
        return self._select_all_enabled

    def setSelectAllText(self, text: str) -> None:
        """Set the text for the Select All option."""
        self._select_all_text = text
        if self._select_all_enabled:
            model = self.model()
            if isinstance(model, QStandardItemModel) and model.rowCount() > 0:
                item = model.item(0)
                if item and item.data(Qt.ItemDataRole.UserRole) == self._SELECT_ALL_DATA:
                    item.setText(text)

    def selectAllText(self) -> str:
        """Get the Select All text."""
        return self._select_all_text

    # ==================== Public API: Configuration ====================

    def setMaxSelectionCount(self, count: Optional[int]) -> None:
        """Set the maximum number of items that can be selected."""
        if count is None or count <= 0:
            self._max_selection_count = None
        else:
            self._max_selection_count = count
            self._enforce_max_selection()

    def maxSelectionCount(self) -> Optional[int]:
        """Get the maximum selection count."""
        return self._max_selection_count

    def setCloseOnSelect(self, enabled: bool) -> None:
        """Set whether to close the popup after each selection."""
        self._close_on_select = enabled

    def isCloseOnSelect(self) -> bool:
        """Check if popup closes after selection."""
        return self._close_on_select

    def setDisplayDelimiter(self, delimiter: str) -> None:
        """Set the delimiter used when displaying selected items."""
        self._display_delimiter = delimiter
        self.updateText()

    def displayDelimiter(self) -> str:
        """Get the display delimiter."""
        return self._display_delimiter

    def setOutputType(self, output_type: str) -> None:
        """Set the output type for currentData()."""
        if output_type not in ("data", "text"):
            raise ValueError("Output type must be 'data' or 'text'")
        self._output_type = output_type

    def outputType(self) -> str:
        """Get the output type."""
        return self._output_type

    def setDisplayType(self, display_type: str) -> None:
        """Set the display type for the combo box text."""
        if display_type not in ("data", "text"):
            raise ValueError("Display type must be 'data' or 'text'")
        self._display_type = display_type
        self.updateText()

    def displayType(self) -> str:
        """Get the display type."""
        return self._display_type

    def setDuplicatesEnabled(self, enabled: bool) -> None:
        """Set whether duplicate items are allowed."""
        self._duplicates_enabled = enabled

    def isDuplicatesEnabled(self) -> bool:
        """Check if duplicates are allowed."""
        return self._duplicates_enabled

    # ==================== Text Update ====================

    def updateText(self) -> None:
        """Update the displayed text based on selection."""
        if self._updating_text:
            return

        self._updating_text = True
        try:
            model = self.model()
            if not isinstance(model, QStandardItemModel):
                return

            rows = sorted(r for r in self._checked_rows if self._is_option_row(r))

            # Update chips display if enabled
            if self._chips_enabled and self._chips_display is not None:
                chip_items = []
                for i in rows:
                    item = model.item(i)
                    if item:
                        text = item.text()
                        chip_items.append((i, text))
                self._chips_display.setItems(chip_items)
                return

            # Standard text display
            texts = []
            for i in rows:
                item = model.item(i)
                if item:
                    if self._display_type == "text":
                        texts.append(item.text())
                    else:
                        data = item.data(Qt.ItemDataRole.UserRole)
                        texts.append(str(data) if data is not None else "")

            display_text = self._display_delimiter.join(texts) if texts else ""

            line_edit = self.lineEdit()
            if line_edit:
                available_width = line_edit.width() - 10
                if available_width > 0:
                    metrics = QFontMetrics(line_edit.font())
                    elided = metrics.elidedText(
                        display_text, Qt.TextElideMode.ElideRight, available_width
                    )
                else:
                    elided = display_text

                line_edit.blockSignals(True)
                line_edit.setText(elided)
                line_edit.blockSignals(False)

            tooltip = display_text if display_text else self._placeholder_text
            self.setToolTip(tooltip)

        finally:
            self._updating_text = False

    # ==================== Internal Methods ====================

    def _first_option_row(self) -> int:
        """Get the index of the first actual option row."""
        if not self._select_all_enabled:
            return 0

        model = self.model()
        if isinstance(model, QStandardItemModel) and model.rowCount() > 0:
            item = model.item(0)
            if item and item.data(Qt.ItemDataRole.UserRole) == self._SELECT_ALL_DATA:
                return 1
        return 0

    def _is_option_row(self, row: int) -> bool:
        """Check if a row is an actual option (not Select All)."""
        return row >= self._first_option_row()

    def _rebuild_checked_cache(self) -> None:
        """Rebuild the cache of checked row indexes."""
        self._checked_rows.clear()

        model = self.model()
        if not isinstance(model, QStandardItemModel):
            return

        start = self._first_option_row()
        for i in range(start, model.rowCount()):
            item = model.item(i)
            if item and item.checkState() == Qt.CheckState.Checked:
                self._checked_rows.add(i)

    def _sync_select_all_state(self) -> None:
        """Synchronize the Select All checkbox state."""
        if not self._select_all_enabled:
            return

        model = self.model()
        if not isinstance(model, QStandardItemModel) or model.rowCount() == 0:
            return

        sa = model.item(0)
        if sa is None or sa.data(Qt.ItemDataRole.UserRole) != self._SELECT_ALL_DATA:
            return

        first_option = self._first_option_row()
        total = model.rowCount() - first_option

        if total <= 0:
            sa.setData(Qt.CheckState.Unchecked, Qt.ItemDataRole.CheckStateRole)
            return

        checked = len([r for r in self._checked_rows if self._is_option_row(r)])

        if checked == 0:
            new_state = Qt.CheckState.Unchecked
        elif checked == total:
            new_state = Qt.CheckState.Checked
        else:
            new_state = Qt.CheckState.PartiallyChecked

        if sa.data(Qt.ItemDataRole.CheckStateRole) != new_state:
            sa.setData(new_state, Qt.ItemDataRole.CheckStateRole)

    def _emit_selection_if_changed(self) -> None:
        """Emit selectionChanged signal if selection has changed."""
        if self._in_bulk_update:
            return

        current = self.currentData()
        if current != self._last_selection_snapshot:
            self._last_selection_snapshot = list(current)
            self.selectionChanged.emit(list(current))

    def _begin_bulk_update(self) -> None:
        """Begin a bulk update operation."""
        self._in_bulk_update = True

    def _end_bulk_update(self) -> None:
        """End a bulk update operation."""
        self._in_bulk_update = False
        self._rebuild_checked_cache()
        self._sync_select_all_state()
        self.updateText()
        self._emit_selection_if_changed()

    def _can_select_more(self, count: int = 1) -> bool:
        """Check if more items can be selected."""
        if self._max_selection_count is None:
            return True
        current = len([r for r in self._checked_rows if self._is_option_row(r)])
        return current + count <= self._max_selection_count

    def _enforce_max_selection(self) -> None:
        """Enforce the maximum selection limit."""
        if self._max_selection_count is None:
            return

        model = self.model()
        if not isinstance(model, QStandardItemModel):
            return

        selected = sorted(r for r in self._checked_rows if self._is_option_row(r))
        if len(selected) <= self._max_selection_count:
            return

        for r in selected[self._max_selection_count :]:
            item = model.item(r)
            if item:
                item.setData(Qt.CheckState.Unchecked, Qt.ItemDataRole.CheckStateRole)

        self._rebuild_checked_cache()
        self.updateText()
        self._emit_selection_if_changed()

    def _notify_limit_reached(self) -> None:
        """Show notification when selection limit is reached."""
        if self._max_selection_count is None:
            return

        from PyQt6.QtWidgets import QToolTip

        msg = f"Maximum {self._max_selection_count} selection(s) allowed"
        QToolTip.showText(QCursor.pos(), msg, self)

    def _connect_model_signals(self, model: QAbstractItemModel) -> None:
        """Connect to model signals."""
        if model is None:
            return

        try:
            model.dataChanged.connect(self._on_model_data_changed)
            model.rowsInserted.connect(self._on_rows_changed)
            model.rowsRemoved.connect(self._on_rows_changed)
            model.modelReset.connect(self._on_model_reset)
        except (AttributeError, TypeError):
            pass

    def _disconnect_model_signals(self, model: QAbstractItemModel) -> None:
        """Disconnect from model signals."""
        if model is None:
            return

        try:
            model.dataChanged.disconnect(self._on_model_data_changed)
            model.rowsInserted.disconnect(self._on_rows_changed)
            model.rowsRemoved.disconnect(self._on_rows_changed)
            model.modelReset.disconnect(self._on_model_reset)
        except (AttributeError, TypeError, RuntimeError):
            pass

    def _on_model_data_changed(
        self, top_left: QModelIndex, bottom_right: QModelIndex, roles: List[int] = None
    ) -> None:
        """Handle model data changes."""
        if self._in_bulk_update:
            return

        if roles is not None and Qt.ItemDataRole.CheckStateRole not in roles:
            return

        self._rebuild_checked_cache()
        self._sync_select_all_state()
        self.updateText()
        self._emit_selection_if_changed()

    def _on_rows_changed(self, parent: QModelIndex, start: int, end: int) -> None:
        """Handle rows inserted/removed."""
        if self._in_bulk_update:
            return
        self._rebuild_checked_cache()
        self._sync_select_all_state()
        self.updateText()

    def _on_model_reset(self) -> None:
        """Handle model reset."""
        if self._in_bulk_update:
            return
        self._checked_rows.clear()
        self._last_selection_snapshot = []
        self._sync_select_all_state()
        self.updateText()
        self._emit_selection_if_changed()

    # ==================== Public API: Focus Border ====================

    def setFocusBorderEnabled(self, enabled: bool) -> None:
        """Enable or disable the focus border."""
        self._focus_border_enabled = enabled
        self.update()

    def isFocusBorderEnabled(self) -> bool:
        """Check if the focus border is enabled."""
        return self._focus_border_enabled

    def setFocusBorderWidth(self, width: int) -> None:
        """Set the focus border width."""
        if width < 1:
            raise ValueError("Focus border width must be at least 1")
        self._focus_border_width = width
        self.update()

    def focusBorderWidth(self) -> int:
        """Get the focus border width."""
        return self._focus_border_width

    def setFocusBorderPosition(self, position: str) -> None:
        """Set the focus border position."""
        valid_positions = ("bottom", "all", "none")
        if position not in valid_positions:
            raise ValueError(
                f"Position must be one of {valid_positions}, got '{position}'"
            )
        self._focus_border_position = position
        self.update()

    def focusBorderPosition(self) -> str:
        """Get the focus border position."""
        return self._focus_border_position

# FILE: src\fluent_multiselect\config.py
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

# FILE: src\fluent_multiselect\delegate.py
# FILE: src/fluent_multiselect/delegate.py
"""Fluent Design checkbox delegate for list items."""

from typing import Optional

from PyQt6.QtWidgets import QStyledItemDelegate, QStyle, QStyleOptionViewItem
from PyQt6.QtGui import QPainter, QColor, QPen, QPainterPath, QFontMetrics
from PyQt6.QtCore import Qt, QRect, QSize, QRectF, QPointF, QModelIndex

from .styles import Theme
from .colors import FluentColors


class FluentCheckBoxDelegate(QStyledItemDelegate):
    """Custom delegate for rendering Fluent Design checkboxes."""

    # Constants matching QSS specifications
    CHECKBOX_SIZE = 18  # width: 18px; height: 18px;
    CHECKBOX_MARGIN = 8  # spacing: 8px;
    CHECKBOX_BORDER_RADIUS = 2  # border-radius: 5px;
    CHECKBOX_BORDER_WIDTH = 1.0  # border: 1px solid
    CHECK_MARK_WIDTH = 1.8
    ITEM_PADDING_V = 6
    ITEM_PADDING_H = 8
    ITEM_BORDER_RADIUS = 4
    MIN_ITEM_HEIGHT = 22  # min-height: 22px;

    def __init__(self, parent: Optional[object] = None, theme: Theme = Theme.DARK):
        super().__init__(parent)
        self._theme = theme

    def setTheme(self, theme: Theme) -> None:
        """Set the theme."""
        self._theme = theme

    def theme(self) -> Theme:
        """Get the current theme."""
        return self._theme

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex) -> QSize:
        """Calculate the size hint for an item."""
        size = super().sizeHint(option, index)
        metrics = QFontMetrics(option.font)
        min_height = max(
            metrics.height() + self.ITEM_PADDING_V * 2,
            self.MIN_ITEM_HEIGHT + self.ITEM_PADDING_V * 2,
            36,
        )
        size.setHeight(min_height)
        return size

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        """Paint the item with checkbox."""
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Get colors based on theme
        colors = self._get_colors()

        rect = option.rect
        is_hovered = bool(option.state & QStyle.StateFlag.State_MouseOver)
        is_selected = bool(option.state & QStyle.StateFlag.State_Selected)
        is_enabled = bool(option.state & QStyle.StateFlag.State_Enabled)

        # Draw hover/selection background
        if is_hovered or is_selected:
            bg_rect = rect.adjusted(2, 1, -2, -1)
            path = QPainterPath()
            path.addRoundedRect(QRectF(bg_rect), self.ITEM_BORDER_RADIUS, self.ITEM_BORDER_RADIUS)
            painter.fillPath(path, colors["item_hover"])

        # Get check state
        check_state = index.data(Qt.ItemDataRole.CheckStateRole)
        is_checked = check_state == Qt.CheckState.Checked
        is_partial = check_state == Qt.CheckState.PartiallyChecked

        # Calculate checkbox position (margin-left: 1px from QSS)
        checkbox_x = rect.left() + self.CHECKBOX_MARGIN + 1
        checkbox_y = rect.center().y() - self.CHECKBOX_SIZE // 2
        checkbox_rect = QRectF(checkbox_x, checkbox_y, self.CHECKBOX_SIZE, self.CHECKBOX_SIZE)

        # Draw checkbox
        self._draw_checkbox(painter, checkbox_rect, is_checked, is_partial, is_enabled, colors)

        # Draw text with spacing from QSS
        text_x = checkbox_x + self.CHECKBOX_SIZE + self.CHECKBOX_MARGIN
        text_rect = rect.adjusted(int(text_x), 0, -self.ITEM_PADDING_H, 0)
        text = index.data(Qt.ItemDataRole.DisplayRole)

        if text:
            text_color = colors["text_disabled"] if not is_enabled else colors["text"]
            painter.setPen(text_color)
            painter.setFont(option.font)
            painter.drawText(
                text_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, text
            )

        painter.restore()

    def _get_colors(self) -> dict:
        """Get colors based on current theme."""
        if self._theme == Theme.DARK:
            return {
                "text": FluentColors.DARK_TEXT,
                "text_disabled": QColor(255, 255, 255, 92),
                "item_hover": QColor(255, 255, 255, 20),
                "checkbox_bg": QColor(255, 255, 255, 14),
                "checkbox_checked": FluentColors.DARK_CHECKBOX_CHECKED,
                "checkbox_border": QColor(255, 255, 255, 70),
                "check_mark": FluentColors.DARK_CHECK_MARK,
            }
        else:
            return {
                "text": FluentColors.LIGHT_TEXT,
                "text_disabled": QColor(0, 0, 0, 92),
                "item_hover": QColor(0, 0, 0, 13),
                "checkbox_bg": QColor(0, 0, 0, 14),
                "checkbox_checked": FluentColors.LIGHT_CHECKBOX_CHECKED,
                "checkbox_border": QColor(0, 0, 0, 90),
                "check_mark": FluentColors.LIGHT_CHECK_MARK,
            }

    def _draw_checkbox(
        self,
        painter: QPainter,
        rect: QRectF,
        checked: bool,
        partial: bool,
        enabled: bool,
        colors: dict,
    ) -> None:
        """Draw the checkbox matching QSS specifications."""
        path = QPainterPath()
        path.addRoundedRect(rect, self.CHECKBOX_BORDER_RADIUS, self.CHECKBOX_BORDER_RADIUS)

        if checked or partial:
            # Checked/partial state - filled background
            fill_color = colors["checkbox_checked"]
            if not enabled:
                fill_color = QColor(fill_color.red(), fill_color.green(), fill_color.blue(), 100)
            painter.fillPath(path, fill_color)

            # Draw check mark or partial mark
            mark_color = colors["check_mark"]
            if checked:
                self._draw_check_mark(painter, rect, mark_color)
            else:
                self._draw_partial_mark(painter, rect, mark_color)
        else:
            # Unchecked state
            fill_color = colors["checkbox_bg"]
            border_color = colors["checkbox_border"]

            if not enabled:
                fill_color = QColor(fill_color.red(), fill_color.green(), fill_color.blue(), 50)
                border_color = QColor(
                    border_color.red(), border_color.green(), border_color.blue(), 50
                )

            painter.fillPath(path, fill_color)
            painter.setPen(QPen(border_color, self.CHECKBOX_BORDER_WIDTH))
            painter.drawPath(path)

    def _draw_check_mark(self, painter: QPainter, rect: QRectF, color: QColor) -> None:
        """Draw a properly centered check mark."""
        painter.setPen(
            QPen(
                color,
                self.CHECK_MARK_WIDTH,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
                Qt.PenJoinStyle.RoundJoin,
            )
        )

        # Get exact center using floating point
        cx = rect.center().x()
        cy = rect.center().y()
        w = rect.width()

        # Checkmark points calculated to be visually centered
        # The checkmark spans roughly 55% of the checkbox width
        # Coordinates are balanced so the visual center matches the geometric center

        # Left point (start of short stroke)
        left_x = cx - w * 0.22
        left_y = cy + w * 0.02

        # Bottom point (corner where strokes meet)
        bottom_x = cx - w * 0.02
        bottom_y = cy + w * 0.22

        # Right point (end of long stroke going up)
        right_x = cx + w * 0.28
        right_y = cy - w * 0.22

        path = QPainterPath()
        path.moveTo(left_x, left_y)
        path.lineTo(bottom_x, bottom_y)
        path.lineTo(right_x, right_y)

        painter.drawPath(path)

    def _draw_partial_mark(self, painter: QPainter, rect: QRectF, color: QColor) -> None:
        """Draw a centered partial (indeterminate) mark."""
        painter.setPen(
            QPen(color, self.CHECK_MARK_WIDTH, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        )

        cx = rect.center().x()
        cy = rect.center().y()
        half_width = rect.width() * 0.28  # Horizontal line spanning ~56% of checkbox

        painter.drawLine(
            QPointF(cx - half_width, cy),
            QPointF(cx + half_width, cy)
        )

# FILE: src\fluent_multiselect\styles.py
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

