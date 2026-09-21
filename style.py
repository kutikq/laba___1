from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QApplication

APP_STYLESHEET = """
QWidget {
    font-size: 13px;
}

QMainWindow, QDialog {
    background-color: #f4f5f7;
}

QMenuBar {
    background-color: #ffffff;
    border-bottom: 1px solid #d9dce1;
    padding: 2px;
    color: #1e2230;
}

QMenuBar::item {
    color: #1e2230;
    background: transparent;
    padding: 4px 10px;
}

QMenuBar::item:selected {
    background-color: #e3ebff;
    border-radius: 4px;
    color: #1e2230;
}

QMenu {
    background-color: #ffffff;
    border: 1px solid #d9dce1;
    color: #1e2230;
}

QMenu::item {
    color: #1e2230;
    padding: 5px 20px;
}

QMenu::item:selected {
    background-color: #e3ebff;
    color: #1e2230;
}

QMenu::item:disabled {
    color: #b0b5c0;
}

QStatusBar {
    background-color: #ffffff;
    border-top: 1px solid #d9dce1;
    color: #1e2230;
}

QPushButton {
    background-color: #2f6fed;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 7px 18px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #255dcc;
}

QPushButton:pressed {
    background-color: #1e4ea8;
}

QPushButton:disabled {
    background-color: #b7c2d6;
    color: #eef1f6;
}

QPushButton#secondaryButton {
    background-color: #e7eaf0;
    color: #33384a;
}

QPushButton#secondaryButton:hover {
    background-color: #d8dce4;
}

QLineEdit {
    border: 1px solid #c7ccd6;
    border-radius: 5px;
    padding: 6px 8px;
    background-color: white;
    selection-background-color: #2f6fed;
}

QLineEdit:focus {
    border: 1px solid #2f6fed;
}

QLabel#hintLabel {
    color: #5a6272;
    font-size: 12px;
}

QTableWidget {
    background-color: white;
    gridline-color: #e3e6eb;
    border: 1px solid #d9dce1;
    border-radius: 6px;
}

QHeaderView::section {
    background-color: #eef1f6;
    padding: 6px;
    border: none;
    border-bottom: 1px solid #d9dce1;
    font-weight: 600;
    color: #1e2230;
}

QMessageBox {
    background-color: #ffffff;
}

QMessageBox QLabel {
    font-size: 13px;
}
"""


def apply_app_style(app: QApplication) -> None:
    """Применить стиль Fusion + палитру + QSS ко всему приложению."""
    app.setStyle("Fusion")

    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#f4f5f7"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#1e2230"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#1e2230"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#2f6fed"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#2f6fed"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    app.setPalette(palette)

    app.setStyleSheet(APP_STYLESHEET)