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
        font-family: '{FONT_FAMILY}', 'Noto Sans', 'DejaVu Sans', sans-serif;
        font-size: 14px;
    }}

    /* ─── Sidebar list ─── */
    QListWidget {{
        background-color: {SIDEBAR};
        border: none;
        outline: none;
    }}
    QListWidget::item {{
        height: 48px;
        color: {COMMENT};
        padding-left: 18px;
        border-left: 3px solid transparent;
        margin-bottom: 1px;
        font-size: 14px;
    }}
    QListWidget::item:selected {{
        background-color: rgba(68, 71, 90, 0.85);
        color: {FOREGROUND};
        border-left: 3px solid {PURPLE};
    }}
    QListWidget::item:hover:!selected {{
        background-color: rgba(68, 71, 90, 0.4);
        color: {FOREGROUND};
        border-left: 3px solid rgba(189, 147, 249, 0.25);
    }}

    /* ─── Labels ─── */
    QLabel {{
        color: {FOREGROUND};
        background-color: transparent;
    }}

    /* ─── Inputs ─── */
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

    /* ─── Button base ─── */
    QPushButton {{
        background-color: {CURRENT_LINE};
        color: {FOREGROUND};
        border: none;
        border-radius: {BORDER_RADIUS};
        padding: 8px 16px;
        font-weight: 600;
        min-height: {INPUT_HEIGHT};
    }}
    QPushButton:hover {{
        background-color: #55586e;
    }}
    QPushButton:pressed {{
        background-color: {COMMENT};
    }}
    QPushButton:disabled {{
        color: {COMMENT};
        background-color: {SIDEBAR};
    }}

    /* ─── Primary CTA: purple filled ─── */
    QPushButton#actionBtn {{
        background-color: {PURPLE};
        color: {BACKGROUND};
        font-size: 14px;
        font-weight: 700;
        letter-spacing: 1.2px;
        min-height: 48px;
        border-radius: {BORDER_RADIUS};
        border: none;
    }}
    QPushButton#actionBtn:hover {{
        background-color: #caa9ff;
    }}
    QPushButton#actionBtn:pressed {{
        background-color: #9c74e0;
    }}
    QPushButton#actionBtn:disabled {{
        background-color: {CURRENT_LINE};
        color: {COMMENT};
    }}

    /* ─── Secondary: ghost purple ─── */
    QPushButton#secondaryBtn {{
        background-color: transparent;
        color: {PURPLE};
        border: 1px solid rgba(189, 147, 249, 0.55);
        font-size: 14px;
        font-weight: 600;
        border-radius: {BORDER_RADIUS};
        min-height: 40px;
    }}
    QPushButton#secondaryBtn:hover {{
        background-color: rgba(189, 147, 249, 0.1);
        border-color: {PURPLE};
        color: #caa9ff;
    }}
    QPushButton#secondaryBtn:pressed {{
        background-color: rgba(189, 147, 249, 0.18);
    }}
    QPushButton#secondaryBtn:disabled {{
        color: {COMMENT};
        border-color: rgba(98, 114, 164, 0.35);
    }}

    /* ─── Danger: ghost red ─── */
    QPushButton#dangerBtn {{
        background-color: transparent;
        color: {RED};
        border: 1px solid rgba(255, 85, 85, 0.5);
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

    /* ─── File picker / drop zone ─── */
    QPushButton#fileBtn {{
        background-color: rgba(33, 34, 44, 0.6);
        color: {COMMENT};
        border: 1px dashed rgba(98, 114, 164, 0.55);
        border-radius: {BORDER_RADIUS};
        min-height: 44px;
        font-size: 13px;
        text-align: left;
        padding-left: 14px;
        font-weight: 400;
    }}
    QPushButton#fileBtn:hover {{
        border-color: rgba(189, 147, 249, 0.7);
        color: {FOREGROUND};
        background-color: rgba(189, 147, 249, 0.05);
    }}
    QPushButton[hasPath="true"]#fileBtn {{
        border-style: solid;
        border-color: rgba(80, 250, 123, 0.45);
        color: rgba(80, 250, 123, 0.9);
    }}
    QPushButton[hasPath="true"]#fileBtn:hover {{
        border-color: {GREEN};
        background-color: rgba(80, 250, 123, 0.06);
    }}

    /* ─── ComboBox ─── */
    QComboBox {{
        background-color: {CURRENT_LINE};
        color: {FOREGROUND};
        border: 1px solid transparent;
        border-radius: {BORDER_RADIUS};
        padding: 8px 12px;
        min-height: {INPUT_HEIGHT};
    }}
    QComboBox:hover {{
        border: 1px solid {COMMENT};
    }}
    QComboBox:focus {{
        border: 1px solid {PURPLE};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 24px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {CURRENT_LINE};
        color: {FOREGROUND};
        selection-background-color: rgba(189, 147, 249, 0.2);
        border: 1px solid {COMMENT};
        outline: none;
    }}

    /* ─── CheckBox ─── */
    QCheckBox {{
        color: {FOREGROUND};
        spacing: 8px;
    }}
    QCheckBox::indicator {{
        width: 16px;
        height: 16px;
        border: 1px solid {COMMENT};
        border-radius: 3px;
        background: {BACKGROUND};
    }}
    QCheckBox::indicator:checked {{
        background: {PURPLE};
        border: 1px solid {PURPLE};
    }}
    QCheckBox::indicator:hover {{
        border-color: {PURPLE};
    }}

    /* ─── ProgressBar (slim) ─── */
    QProgressBar {{
        border: none;
        border-radius: 3px;
        background-color: {CURRENT_LINE};
        color: transparent;
        min-height: 6px;
        max-height: 6px;
        text-align: center;
    }}
    QProgressBar::chunk {{
        background-color: {PURPLE};
        border-radius: 3px;
    }}

    /* ─── TabWidget (underline style) ─── */
    QTabWidget::pane {{
        border: none;
        border-top: 1px solid {CURRENT_LINE};
        padding-top: 8px;
    }}
    QTabBar::tab {{
        background-color: transparent;
        color: {COMMENT};
        padding: 8px 22px;
        border: none;
        border-bottom: 2px solid transparent;
        margin-right: 2px;
        font-weight: 600;
        font-size: 13px;
    }}
    QTabBar::tab:selected {{
        color: {PURPLE};
        border-bottom: 2px solid {PURPLE};
    }}
    QTabBar::tab:hover:!selected {{
        color: {FOREGROUND};
        border-bottom: 2px solid rgba(189, 147, 249, 0.3);
    }}

    /* ─── TableWidget ─── */
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
        padding: 4px 8px;
    }}
    QTableWidget::item:selected {{
        background-color: rgba(189, 147, 249, 0.14);
        color: {PURPLE};
    }}
    QHeaderView::section {{
        background-color: {SIDEBAR};
        color: {COMMENT};
        padding: 8px 12px;
        border: none;
        border-bottom: 1px solid {CURRENT_LINE};
        font-weight: 700;
        font-size: 12px;
        letter-spacing: 0.4px;
    }}

    /* ─── Drag-drop list ─── */
    QListWidget#dropZone {{
        background-color: {SIDEBAR};
        border: 1px dashed rgba(98, 114, 164, 0.4);
        border-radius: {BORDER_RADIUS};
        outline: none;
    }}
    QListWidget#dropZone::item {{
        height: 36px;
        background-color: {CURRENT_LINE};
        border-radius: 4px;
        padding-left: 12px;
        margin: 2px 4px;
        color: {FOREGROUND};
        border-left: 2px solid transparent;
        font-size: 13px;
    }}
    QListWidget#dropZone::item:selected {{
        background-color: rgba(189, 147, 249, 0.14);
        border-left: 2px solid {PURPLE};
        color: {PURPLE};
    }}
    QListWidget#dropZone::item:hover:!selected {{
        background-color: rgba(68, 71, 90, 0.9);
        border-left: 2px solid rgba(189, 147, 249, 0.35);
    }}

    /* ─── Scrollbars (minimal) ─── */
    QScrollBar:vertical {{
        border: none;
        background: transparent;
        width: 6px;
        margin: 0;
    }}
    QScrollBar::handle:vertical {{
        background: rgba(98, 114, 164, 0.45);
        min-height: 24px;
        border-radius: 3px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: rgba(98, 114, 164, 0.75);
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        border: none;
        background: none;
        height: 0px;
    }}
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
        background: none;
    }}
    QScrollBar:horizontal {{
        border: none;
        background: transparent;
        height: 6px;
        margin: 0;
    }}
    QScrollBar::handle:horizontal {{
        background: rgba(98, 114, 164, 0.45);
        min-width: 24px;
        border-radius: 3px;
    }}
    QScrollBar::handle:horizontal:hover {{
        background: rgba(98, 114, 164, 0.75);
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        border: none;
        background: none;
        width: 0px;
    }}
    QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
        background: none;
    }}

    /* ─── Splitter ─── */
    QSplitter::handle {{
        background-color: {CURRENT_LINE};
    }}

    /* ─── GroupBox ─── */
    QGroupBox {{
        border: 1px solid {CURRENT_LINE};
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
