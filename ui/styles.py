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
        font-weight: 600;
        border-radius: {BORDER_RADIUS};
        min-height: 40px;
    }}
    QPushButton#dangerBtn:hover {{
        background-color: rgba(255, 85, 85, 0.1);
        border-color: {RED};
    }}
    QPushButton#dangerBtn:pressed {{
        background-color: rgba(255, 85, 85, 0.18);
    }}

    /* ─── Navigation / compact buttons ─── */
    QPushButton#navBtn {{
        background-color: transparent;
        color: {COMMENT};
        border: 1px solid rgba(68, 71, 90, 0.6);
        border-radius: 4px;
        font-size: 12px;
        font-weight: 600;
        min-height: 28px;
        max-height: 28px;
        padding: 0 8px;
    }}
    QPushButton#navBtn:hover {{
        background-color: rgba(68, 71, 90, 0.5);
        color: {FOREGROUND};
        border-color: rgba(189, 147, 249, 0.4);
    }}
    QPushButton#navBtn:pressed {{
        background-color: rgba(68, 71, 90, 0.8);
    }}
    QPushButton#navBtn:disabled {{
        color: rgba(98, 114, 164, 0.3);
        border-color: rgba(68, 71, 90, 0.3);
    }}

    /* ─── File picker / drop zone ─── */
    QPushButton#fileBtn {{
        background-color: rgba(33, 34, 44, 0.6);
        color: {COMMENT};
        border: 1px dashed rgba(98, 114, 164, 0.55);
        border-radius: {BORDER_RADIUS};
        min-height: 44px;
    }}
    QPushButton#fileBtn:hover {{
        border-color: {PURPLE};
        background-color: rgba(33, 34, 44, 0.9);
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
        border: 1px solid {CURRENT_LINE};
        border-radius: {BORDER_RADIUS};
        gridline-color: rgba(68, 71, 90, 0.6);
        selection-background-color: rgba(68, 71, 90, 0.8);
        outline: none;
    }}
    QTableWidget::item {{
        padding: 6px 8px;
    }}
    QTableWidget::item:selected {{
        background-color: {CURRENT_LINE};
        color: {PURPLE};
    }}
    QTableWidget QLineEdit {{
        border-radius: 2px;
        padding: 2px 6px;
        min-height: 0px;
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
