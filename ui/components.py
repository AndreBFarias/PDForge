import logging
from pathlib import Path

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import (
    QFileDialog,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ui.styles import DraculaTheme

logger = logging.getLogger("pdfforge.components")


class Toast(QWidget):
    """Notificação flutuante temporária no canto inferior direito da janela pai."""

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.SubWindow
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet(f"""
            background-color: {DraculaTheme.CURRENT_LINE};
            color: {DraculaTheme.CYAN};
            border-radius: 10px;
            border: 1px solid {DraculaTheme.PURPLE};
            padding: 12px 16px;
            font-weight: bold;
        """)
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("background: transparent; border: none;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.label)
        self.hide()
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.hide)

    def show_message(self, message: str, duration_ms: int = 3000) -> None:
        self.label.setText(message)
        self.adjustSize()
        if self.parent():
            rect = self.parent().rect()
            self.move(
                rect.width() - self.width() - 20,
                rect.height() - self.height() - 80,
            )
        self.show()
        self.raise_()
        self.timer.start(duration_ms)


class FilePathButton(QPushButton):
    """
    QPushButton que abre um diálogo nativo ao clicar e exibe o caminho selecionado.

    mode="pdf"  → QFileDialog.getOpenFileName filtrado por PDF
    mode="dir"  → QFileDialog.getExistingDirectory
    """

    path_selected = pyqtSignal(Path)

    def __init__(
        self,
        label: str,
        mode: str = "pdf",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(label, parent)
        self._mode = mode
        self._path: Path | None = None
        self._default_label = label
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clicked.connect(self._open_dialog)

    @property
    def current_path(self) -> Path | None:
        return self._path

    def set_path(self, path: Path | None) -> None:
        self._path = path
        if path:
            display = str(path)
            if len(display) > 46:
                display = "..." + display[-43:]
            self.setText(display)
        else:
            self.setText(self._default_label)

    def _open_dialog(self) -> None:
        if self._mode == "pdf":
            start = str(self._path.parent) if self._path else ""
            raw, _ = QFileDialog.getOpenFileName(
                self, "Selecionar PDF", start, "PDF (*.pdf)"
            )
            if raw:
                path = Path(raw)
                self.set_path(path)
                self.path_selected.emit(path)
        else:
            start = str(self._path) if self._path else ""
            raw = QFileDialog.getExistingDirectory(
                self, "Selecionar Pasta de Saída", start
            )
            if raw:
                path = Path(raw)
                self.set_path(path)
                self.path_selected.emit(path)


class SectionHeader(QLabel):
    """Cabeçalho de seção com estilo Dracula (texto branco + destaque roxo)."""

    def __init__(self, white: str, purple: str = "", parent: QWidget | None = None) -> None:
        rich = (
            f'<span style="color:{DraculaTheme.FOREGROUND};">{white}</span>'
            f'<span style="color:{DraculaTheme.PURPLE};"> {purple}</span>'
            if purple
            else white
        )
        super().__init__(rich, parent)
        self.setStyleSheet(
            "font-size: 26px; font-weight: bold; margin-bottom: 10px;"
            f" background-color: transparent; color: {DraculaTheme.FOREGROUND};"
        )


# "A ordem é o prazer da razão; a desordem é a delícia da imaginação." — Paul Claudel
