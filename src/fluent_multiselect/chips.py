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

        # Cache pour optimisation
        self._font_metrics: Optional[QFontMetrics] = None
        self._last_width: int = 0

        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.setMinimumHeight(28)

        # Set font
        font = QFont("Segoe UI", 9)
        self.setFont(font)

    def setFont(self, font: QFont) -> None:
        """
        Override to invalidate font metrics cache.

        Args:
            font: New font to set.
        """
        super().setFont(font)
        self._font_metrics = None  # Invalider le cache

    def _get_font_metrics(self) -> QFontMetrics:
        """
        Get cached font metrics.

        Returns:
            QFontMetrics instance for current font.
        """
        if self._font_metrics is None:
            self._font_metrics = QFontMetrics(self.font())
        return self._font_metrics

    def setItems(self, items: List[Tuple[int, str]]) -> None:
        """
        Set the items to display as chips.

        Args:
            items: List of (row_index, display_text) tuples.
        """
        # Optimisation : éviter les updates inutiles
        if self._items == items:
            return

        self._items = list(items)
        self._chip_rects.clear()
        self._hovered_chip = -1
        self._hovered_x = -1
        self.update()

    def items(self) -> List[Tuple[int, str]]:
        """
        Get the current items.

        Returns:
            Copy of the items list.
        """
        return list(self._items)

    def setPlaceholderText(self, text: str) -> None:
        """
        Set placeholder text shown when no items are selected.

        Args:
            text: Placeholder text.

        Raises:
            TypeError: If text is not a string.
        """
        if not isinstance(text, str):
            raise TypeError("Placeholder text must be a string")

        self._placeholder_text = text
        self.update()

    def placeholderText(self) -> str:
        """
        Get the placeholder text.

        Returns:
            Current placeholder text.
        """
        return self._placeholder_text

    def setMaxVisibleChips(self, count: Optional[int]) -> None:
        """
        Set maximum number of visible chips before showing overflow.

        Args:
            count: Maximum chips to show, or None for auto (based on width).

        Raises:
            ValueError: If count is negative.

        Example:
            display.setMaxVisibleChips(3)  # Show max 3 chips, then "+N"
        """
        # Validation
        if count is not None and count < 0:
            raise ValueError("maxVisibleChips must be None or >= 0")

        self._max_visible_chips = count
        self.update()

    def maxVisibleChips(self) -> Optional[int]:
        """
        Get the maximum visible chips setting.

        Returns:
            Maximum visible chips or None if unlimited.
        """
        return self._max_visible_chips

    def setTheme(self, theme: Theme) -> None:
        """
        Set the display theme.

        Args:
            theme: Theme.DARK or Theme.LIGHT.

        Raises:
            ValueError: If theme is not a valid Theme enum value.
        """
        if not isinstance(theme, Theme):
            raise ValueError(f"theme must be a Theme enum, got {type(theme)}")

        if self._theme == theme:
            return

        self._theme = theme
        self.update()

    def theme(self) -> Theme:
        """
        Get the current theme.

        Returns:
            Current theme.
        """
        return self._theme

    def clear(self) -> None:
        """Clear all chips and reset state."""
        if not self._items:
            return

        self._items.clear()
        self._chip_rects.clear()
        self._hovered_chip = -1
        self._hovered_x = -1
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        """
        Paint the chips.

        Args:
            event: Paint event.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setFont(self.font())

        self._chip_rects.clear()

        if not self._items:
            self._draw_placeholder(painter)
            return

        self._draw_chips(painter)

    def _draw_placeholder(self, painter: QPainter) -> None:
        """
        Draw placeholder text when no items are selected.

        Args:
            painter: QPainter instance.
        """
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
        """
        Draw all chips with overflow handling.

        Args:
            painter: QPainter instance.
        """
        x = self.CHIP_SPACING
        y = (self.height() - self.CHIP_HEIGHT) // 2
        max_width = self.width() - 40  # Leave space for dropdown arrow

        fm = self._get_font_metrics()  # Utiliser le cache
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
        """
        Draw a single chip with text and X button.

        Args:
            painter: QPainter instance.
            chip_rect: Rectangle for the chip background.
            x_rect: Rectangle for the X button.
            text: Text to display in the chip.
            row_idx: Row index of the item.
        """
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
        """
        Draw the X (close) icon.

        Args:
            painter: QPainter instance.
            rect: Rectangle for the X icon.
            color: Color for the X icon.
        """
        painter.setPen(
            QPen(color, self.X_STROKE_WIDTH, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        )

        cx, cy = rect.center().x(), rect.center().y()
        size = self.X_ICON_SIZE

        painter.drawLine(QPointF(cx - size, cy - size), QPointF(cx + size, cy + size))
        painter.drawLine(QPointF(cx - size, cy + size), QPointF(cx + size, cy - size))

    def _draw_overflow(self, painter: QPainter, x: float, y: float, count: int) -> None:
        """
        Draw the overflow indicator (+N).

        Args:
            painter: QPainter instance.
            x: X position for the overflow chip.
            y: Y position for the overflow chip.
            count: Number of hidden items.
        """
        colors = self._get_chip_colors(False, False)
        overflow_text = f"+{count}"

        fm = self._get_font_metrics()  # Utiliser le cache
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
        """
        Get colors for chip rendering based on theme and state.

        Args:
            is_hovered: Whether the chip is being hovered.
            is_x_hovered: Whether the X button is being hovered.

        Returns:
            Dictionary of color values for different chip elements.
        """
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
        """
        Get the placeholder text color based on theme.

        Returns:
            QColor for placeholder text.
        """
        if self._theme == Theme.DARK:
            return QColor(255, 255, 255, 120)
        return QColor(0, 0, 0, 100)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """
        Handle mouse movement for hover effects.

        Args:
            event: Mouse event.
        """
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

        # Ne mettre à jour que si l'état a changé
        if old_chip != self._hovered_chip or old_x != self._hovered_x:
            self.update()

        super().mouseMoveEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """
        Handle mouse press to remove chips or open popup.

        Args:
            event: Mouse event.
        """
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
        """
        Handle mouse leave.

        Args:
            event: Event object.
        """
        # Ne mettre à jour que si nécessaire
        if self._hovered_chip != -1 or self._hovered_x != -1:
            self._hovered_chip = -1
            self._hovered_x = -1
            self.update()
        super().leaveEvent(event)

    def resizeEvent(self, event) -> None:
        """
        Handle resize to update chip layout.

        Args:
            event: Resize event.
        """
        super().resizeEvent(event)  # CORRECTION CRITIQUE

        # Optimisation : ne mettre à jour que si la largeur a changé significativement
        new_width = self.width()
        if abs(new_width - self._last_width) > 5:  # Seuil de 5px
            self._last_width = new_width
            self.update()

    def sizeHint(self) -> "QSize":
        """
        Provide a size hint for layout management.

        Returns:
            Suggested size for the widget.
        """
        from PyQt6.QtCore import QSize

        return QSize(200, 28)

    def minimumSizeHint(self) -> "QSize":
        """
        Provide minimum size hint.

        Returns:
            Minimum size for the widget.
        """
        from PyQt6.QtCore import QSize

        return QSize(100, 28)

    # Méthodes utilitaires supplémentaires

    def isEmpty(self) -> bool:
        """
        Check if there are no items displayed.

        Returns:
            True if no items, False otherwise.
        """
        return len(self._items) == 0

    def itemCount(self) -> int:
        """
        Get the number of items currently displayed.

        Returns:
            Number of items.
        """
        return len(self._items)

    def visibleItemCount(self) -> int:
        """
        Get the number of items currently visible (not in overflow).

        Returns:
            Number of visible items.
        """
        if self._max_visible_chips is not None:
            return min(len(self._items), self._max_visible_chips)

        # Calculate based on available width
        if not self._items:
            return 0

        max_width = self.width() - 40
        fm = self._get_font_metrics()
        x = self.CHIP_SPACING
        count = 0

        for _, text in self._items:
            text_width = fm.horizontalAdvance(text)
            chip_width = (
                self.CHIP_PADDING_LEFT
                + text_width
                + self.CHIP_PADDING_RIGHT
                + self.X_BUTTON_SIZE
                + 2
            )

            if x + chip_width > max_width and count > 0:
                break

            x += chip_width + self.CHIP_SPACING
            count += 1

        return count

    def overflowCount(self) -> int:
        """
        Get the number of items in overflow (hidden with +N indicator).

        Returns:
            Number of overflow items.
        """
        return max(0, len(self._items) - self.visibleItemCount())