import logging

logger = logging.getLogger("pdfforge.styles")


class DraculaTheme:
    BACKGROUND = "#282a36"
    SIDEBAR = "#21222c"
    CURRENT_LINE = "#44475a"
    FOREGROUND = "#f8f8f2"
    COMMENT = "#6272a4"
    CYAN = "#8be9fd"
    GREEN = "#50fa7b"
    ORANGE = "#ffb86c"
    PINK = "#ff79c6"
    PURPLE = "#bd93f9"
    RED = "#ff5555"
    YELLOW = "#f1fa8c"

    BORDER_RADIUS = "8px"
    FONT_FAMILY = "Ubuntu"
    INPUT_HEIGHT = "40px"

    STYLESHEET = f"""
    QMainWindow {{
        background-color: {BACKGROUND};
        color: {FOREGROUND};
    }}
    QWidget {{
        background-color: {BACKGROUND};
        color: {FOREGROUND};
        font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;
        font-size: 14px;
    }}

    QListWidget {{
        background-color: {SIDEBAR};
        border: none;
        outline: none;
    }}
    QListWidget::item {{
        height: 52px;
        color: {COMMENT};
        padding-left: 16px;
        border-left: 3px solid transparent;
        margin-bottom: 2px;
    }}
    QListWidget::item:selected {{
        background-color: {CURRENT_LINE};
        color: {PURPLE};
        border-left: 3px solid {PURPLE};
    }}
    QListWidget::item:hover {{
        background-color: {CURRENT_LINE};
        color: {FOREGROUND};
    }}

    QLabel {{
        color: {FOREGROUND};
        background-color: transparent;
    }}

    QLineEdit, QPlainTextEdit, QTextEdit {{
        background-color: {CURRENT_LINE};
        color: {FOREGROUND};
        border: 1px solid transparent;
        border-radius: {BORDER_RADIUS};
        padding: 8px 12px;
        font-size: 14px;
        selection-background-color: {PURPLE};
    }}
    QLineEdit:focus, QPlainTextEdit:focus, QTextEdit:focus {{
        border: 1px solid {PURPLE};
    }}

    QPushButton {{
        background-color: {CURRENT_LINE};
        color: {FOREGROUND};
        border: none;
        border-radius: {BORDER_RADIUS};
        padding: 8px 16px;
        font-weight: bold;
        min-height: {INPUT_HEIGHT};
    }}
    QPushButton:hover {{
        background-color: {COMMENT};
    }}
    QPushButton:pressed {{
        background-color: {PURPLE};
        color: {BACKGROUND};
    }}
    QPushButton:disabled {{
        color: {COMMENT};
        background-color: {SIDEBAR};
    }}

    QPushButton#actionBtn {{
        background-color: {GREEN};
        color: {BACKGROUND};
        font-size: 15px;
        font-weight: bold;
        min-height: 48px;
        border-radius: {BORDER_RADIUS};
    }}
    QPushButton#actionBtn:hover {{
        background-color: #69ff94;
    }}
    QPushButton#actionBtn:disabled {{
        background-color: {CURRENT_LINE};
        color: {COMMENT};
    }}

    QPushButton#secondaryBtn {{
        background-color: {PURPLE};
        color: {BACKGROUND};
        font-size: 14px;
        border-radius: {BORDER_RADIUS};
        min-height: 44px;
    }}
    QPushButton#secondaryBtn:hover {{
        background-color: #d6acff;
    }}

    QPushButton#dangerBtn {{
        background-color: {RED};
        color: {FOREGROUND};
        font-size: 14px;
        border-radius: {BORDER_RADIUS};
        min-height: 44px;
    }}
    QPushButton#dangerBtn:hover {{
        background-color: #ff7777;
    }}

    QComboBox {{
        background-color: {CURRENT_LINE};
        color: {FOREGROUND};
        border: none;
        border-radius: {BORDER_RADIUS};
        padding: 8px 12px;
        min-height: {INPUT_HEIGHT};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 20px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {CURRENT_LINE};
        color: {FOREGROUND};
        selection-background-color: {PURPLE};
        border: 1px solid {COMMENT};
    }}

    QCheckBox {{
        color: {FOREGROUND};
        spacing: 8px;
    }}
    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border: 1px solid {COMMENT};
        border-radius: 4px;
        background: {BACKGROUND};
    }}
    QCheckBox::indicator:checked {{
        background: {PURPLE};
        border: 1px solid {PURPLE};
    }}

    QProgressBar {{
        border: none;
        border-radius: 6px;
        background-color: {CURRENT_LINE};
        color: {BACKGROUND};
        font-weight: bold;
        text-align: center;
        min-height: 20px;
    }}
    QProgressBar::chunk {{
        background-color: {PURPLE};
        border-radius: 6px;
    }}

    QTabWidget::pane {{
        border: 1px solid {CURRENT_LINE};
        border-radius: {BORDER_RADIUS};
    }}
    QTabBar::tab {{
        background-color: {SIDEBAR};
        color: {COMMENT};
        padding: 8px 20px;
        border: none;
        border-radius: 6px 6px 0 0;
        margin-right: 2px;
    }}
    QTabBar::tab:selected {{
        background-color: {CURRENT_LINE};
        color: {PURPLE};
        font-weight: bold;
    }}
    QTabBar::tab:hover {{
        background-color: {CURRENT_LINE};
        color: {FOREGROUND};
    }}

    QTableWidget {{
        background-color: {BACKGROUND};
        color: {FOREGROUND};
        border: none;
        gridline-color: {CURRENT_LINE};
        selection-background-color: {CURRENT_LINE};
    }}
    QTableWidget::item:selected {{
        background-color: {CURRENT_LINE};
        color: {PURPLE};
    }}
    QHeaderView::section {{
        background-color: {SIDEBAR};
        color: {COMMENT};
        padding: 8px;
        border: none;
        border-bottom: 1px solid {CURRENT_LINE};
        font-weight: bold;
    }}

    QScrollBar:vertical {{
        border: none;
        background: {BACKGROUND};
        width: 8px;
        margin: 0;
    }}
    QScrollBar::handle:vertical {{
        background: {COMMENT};
        min-height: 20px;
        border-radius: 4px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        border: none;
        background: none;
    }}
    QScrollBar:horizontal {{
        border: none;
        background: {BACKGROUND};
        height: 8px;
        margin: 0;
    }}
    QScrollBar::handle:horizontal {{
        background: {COMMENT};
        min-width: 20px;
        border-radius: 4px;
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        border: none;
        background: none;
    }}

    QSplitter::handle {{
        background-color: {CURRENT_LINE};
    }}

    QGroupBox {{
        border: 1px solid {COMMENT};
        border-radius: {BORDER_RADIUS};
        font-weight: bold;
        padding-top: 14px;
        margin-top: 12px;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 0 8px;
        color: {PURPLE};
    }}
    """


# "Clareza é a cortesia do filósofo." — Ortega y Gasset
