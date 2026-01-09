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