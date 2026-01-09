# FILE: demo.py
"""Demo application for FluentMultiSelectComboBox with chips example."""

import sys
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QGroupBox,
    QPushButton,
    QSpinBox,
)
from PyQt6.QtCore import Qt

from src.fluent_multiselect import FluentMultiSelectComboBox, Theme


class DemoWindow(QMainWindow):
    """Demo window showcasing FluentMultiSelectComboBox features."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fluent MultiSelect ComboBox Demo")
        self.setMinimumSize(800, 600)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)

        # Dark theme column
        dark_column = self._create_theme_column(Theme.DARK, "Dark Theme")
        dark_column.setStyleSheet("background-color: #202020;")
        main_layout.addWidget(dark_column)

        # Light theme column
        light_column = self._create_theme_column(Theme.LIGHT, "Light Theme")
        light_column.setStyleSheet("background-color: #f5f5f5;")
        main_layout.addWidget(light_column)

    def _create_theme_column(self, theme: Theme, title: str) -> QWidget:
        """Create a column with examples for a specific theme."""
        column = QWidget()
        layout = QVBoxLayout(column)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet(
            f"font-size: 18px; font-weight: bold; color: {'white' if theme == Theme.DARK else 'black'};"
        )
        layout.addWidget(title_label)

        # 1. Standard ComboBox (no chips)
        layout.addWidget(self._create_standard_example(theme))

        # 2. ComboBox with Chips ⭐ NEW
        layout.addWidget(self._create_chips_example(theme))

        # 3. ComboBox with Select All
        layout.addWidget(self._create_select_all_example(theme))

        # 4. ComboBox with max selection
        layout.addWidget(self._create_max_selection_example(theme))

        layout.addStretch()
        return column

    def _create_standard_example(self, theme: Theme) -> QGroupBox:
        """Create standard combo box example."""
        group = self._create_group("Standard MultiSelect", theme)
        layout = QVBoxLayout(group)

        combo = FluentMultiSelectComboBox(theme=theme)
        combo.setPlaceholderText("Select languages...")
        combo.addItems(["Python", "JavaScript", "TypeScript", "Rust", "Go", "C++"])
        combo.selectionChanged.connect(lambda items: print(f"Standard selection: {items}"))

        layout.addWidget(combo)
        return group

    def _create_chips_example(self, theme: Theme) -> QGroupBox:
        """Create combo box with chips display. ⭐ THIS IS THE CHIPS EXAMPLE"""
        group = self._create_group("With Chips Display ⭐", theme)
        layout = QVBoxLayout(group)

        combo = FluentMultiSelectComboBox(theme=theme)
        combo.setPlaceholderText("Select frameworks...")
        combo.addItems(
            ["React", "Vue", "Angular", "Svelte", "Django", "Flask", "FastAPI", "Express"]
        )

        # ⭐ Enable chips display
        combo.setChipsEnabled(True)

        # Optional: limit visible chips before showing "+N"
        combo.setMaxVisibleChips(3)

        # Pre-select some items to show chips
        combo.setCurrentTexts(["React", "Django", "FastAPI"])

        combo.selectionChanged.connect(lambda items: print(f"Chips selection: {items}"))

        # Add info label
        info_label = QLabel("Click X on chips to remove items")
        info_label.setStyleSheet(
            f"color: {'rgba(255,255,255,0.6)' if theme == Theme.DARK else 'rgba(0,0,0,0.6)'}; font-size: 11px;"
        )

        layout.addWidget(combo)
        layout.addWidget(info_label)
        return group

    def _create_select_all_example(self, theme: Theme) -> QGroupBox:
        """Create combo box with Select All option."""
        group = self._create_group("With Select All", theme)
        layout = QVBoxLayout(group)

        combo = FluentMultiSelectComboBox(theme=theme)
        combo.setPlaceholderText("Select databases...")
        combo.addItems(["PostgreSQL", "MySQL", "MongoDB", "Redis", "SQLite"])
        combo.setSelectAllEnabled(True, "Select All Databases")
        combo.selectionChanged.connect(lambda items: print(f"Select All example: {items}"))

        layout.addWidget(combo)
        return group

    def _create_max_selection_example(self, theme: Theme) -> QGroupBox:
        """Create combo box with maximum selection limit."""
        group = self._create_group("Max Selection (3)", theme)
        layout = QVBoxLayout(group)

        combo = FluentMultiSelectComboBox(theme=theme)
        combo.setPlaceholderText("Select up to 3...")
        combo.addItems(["Option 1", "Option 2", "Option 3", "Option 4", "Option 5"])
        combo.setMaxSelectionCount(3)

        # Also enable chips for this example
        combo.setChipsEnabled(True)

        combo.selectionChanged.connect(lambda items: print(f"Max selection: {items}"))

        layout.addWidget(combo)
        return group

    def _create_group(self, title: str, theme: Theme) -> QGroupBox:
        """Create a styled group box."""
        group = QGroupBox(title)
        if theme == Theme.DARK:
            group.setStyleSheet("""
                QGroupBox {
                    color: white;
                    font-weight: bold;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 8px;
                    margin-top: 12px;
                    padding-top: 8px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px;
                }
            """)
        else:
            group.setStyleSheet("""
                QGroupBox {
                    color: black;
                    font-weight: bold;
                    border: 1px solid rgba(0, 0, 0, 0.1);
                    border-radius: 8px;
                    margin-top: 12px;
                    padding-top: 8px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px;
                }
            """)
        return group


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = DemoWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()