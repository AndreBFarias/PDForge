import logging
from pathlib import Path

import fitz
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from config.settings import Settings
from ui.styles import DraculaTheme

logger = logging.getLogger("pdfforge.widgets.viewer")


class PDFPageViewer(QWidget):
    page_changed = pyqtSignal(int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._doc: fitz.Document | None = None
        self._current_page: int = 0
        self._scale: float = Settings.PDF_VIEWER_DEFAULT_SCALE
        self._fit_to_width: bool = True
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet(f"background-color: {DraculaTheme.BACKGROUND}; border: none;")

        self._img_label = QLabel()
        self._img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._img_label.setStyleSheet(f"background-color: {DraculaTheme.BACKGROUND};")
        self._img_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._scroll.setWidget(self._img_label)
        layout.addWidget(self._scroll)

        nav = QHBoxLayout()
        nav.setSpacing(4)

        self._btn_prev = QPushButton("<")
        self._btn_prev.setObjectName("navBtn")
        self._btn_prev.setFixedWidth(32)
        self._btn_prev.setEnabled(False)
        self._btn_prev.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_prev.clicked.connect(lambda: self.show_page(self._current_page - 1))
        nav.addWidget(self._btn_prev)

        self._lbl_nav = QLabel("—")
        self._lbl_nav.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._lbl_nav.setStyleSheet(
            f"color: {DraculaTheme.COMMENT}; font-size: 12px; background-color: transparent;"
        )
        nav.addWidget(self._lbl_nav)

        self._btn_next = QPushButton(">")
        self._btn_next.setObjectName("navBtn")
        self._btn_next.setFixedWidth(32)
        self._btn_next.setEnabled(False)
        self._btn_next.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_next.clicked.connect(lambda: self.show_page(self._current_page + 1))
        nav.addWidget(self._btn_next)

        nav.addSpacing(10)

        self._btn_zoom_out = QPushButton("-")
        self._btn_zoom_out.setObjectName("navBtn")
        self._btn_zoom_out.setFixedWidth(28)
        self._btn_zoom_out.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_zoom_out.clicked.connect(self.zoom_out)
        nav.addWidget(self._btn_zoom_out)

        self._btn_zoom_reset = QPushButton("Ajustar")
        self._btn_zoom_reset.setObjectName("navBtn")
        self._btn_zoom_reset.setFixedWidth(56)
        self._btn_zoom_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_zoom_reset.clicked.connect(self.zoom_reset)
        nav.addWidget(self._btn_zoom_reset)

        self._btn_zoom_in = QPushButton("+")
        self._btn_zoom_in.setObjectName("navBtn")
        self._btn_zoom_in.setFixedWidth(28)
        self._btn_zoom_in.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_zoom_in.clicked.connect(self.zoom_in)
        nav.addWidget(self._btn_zoom_in)

        layout.addLayout(nav)

    def load_document(self, path: Path) -> None:
        if self._doc:
            try:
                self._doc.close()
            except Exception:
                pass
        self._doc = fitz.open(str(path))
        self._current_page = 0
        self._fit_to_width = True
        self._render()

    def show_page(self, n: int) -> None:
        if not self._doc:
            return
        n = max(0, min(n, self._doc.page_count - 1))
        self._current_page = n
        self._render()
        self.page_changed.emit(n)

    def zoom_in(self) -> None:
        self._fit_to_width = False
        self._scale = min(self._scale * 1.25, Settings.PDF_VIEWER_MAX_SCALE)
        self._render()

    def zoom_out(self) -> None:
        self._fit_to_width = False
        self._scale = max(self._scale / 1.25, Settings.PDF_VIEWER_MIN_SCALE)
        self._render()

    def zoom_reset(self) -> None:
        self._fit_to_width = True
        self._render()

    def _render(self) -> None:
        if not self._doc:
            self._img_label.clear()
            self._lbl_nav.setText("—")
            self._btn_prev.setEnabled(False)
            self._btn_next.setEnabled(False)
            return

        try:
            page = self._doc[self._current_page]
            if self._fit_to_width:
                page_width = page.rect.width
                vp = self._scroll.viewport()
                viewport_width = vp.width() if vp is not None else 0
                if viewport_width > 0 and page_width > 0:
                    self._scale = viewport_width / page_width
            mat = fitz.Matrix(self._scale, self._scale)
            pix = page.get_pixmap(matrix=mat)
            img_bytes = pix.tobytes("png")

            img = QImage.fromData(img_bytes)
            pixmap = QPixmap.fromImage(img)
            self._img_label.setPixmap(pixmap)

            total = self._doc.page_count
            self._lbl_nav.setText(f"{self._current_page + 1} / {total}")
            self._btn_prev.setEnabled(self._current_page > 0)
            self._btn_next.setEnabled(self._current_page < total - 1)
        except Exception as exc:
            logger.error("Erro ao renderizar pagina %d: %s", self._current_page, exc)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if self._fit_to_width and self._doc:
            self._render()

    def closeEvent(self, event) -> None:
        if self._doc:
            try:
                self._doc.close()
            except Exception:
                pass
            self._doc = None
        super().closeEvent(event)


# "Ver é o primeiro ato de criar." — John Berger
