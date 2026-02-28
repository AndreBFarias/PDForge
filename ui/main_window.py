import logging
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from config.settings import APP_NAME, APP_VERSION
from core.pdf_reader import PDFReader
from ui.components import Toast
from ui.screens.page_analyzer import PageAnalyzer
from ui.screens.page_batch import PageBatch
from ui.screens.page_classifier import PageClassifier
from ui.screens.page_compress import PageCompress
from ui.screens.page_editor import PageEditor
from ui.screens.page_merge import PageMerge
from ui.screens.page_ocr import PageOCR
from ui.screens.page_signature import PageSignature
from ui.screens.page_split import PageSplit
from ui.styles import DraculaTheme
from ui.widgets.pdf_page_viewer import PDFPageViewer

logger = logging.getLogger("pdfforge.main_window")

_SIDEBAR_ITEMS = [
    "Editor",
    "Analisador",
    "OCR",
    "Mesclar",
    "Dividir",
    "Comprimir",
    "Assinaturas",
    "Classificar",
    "Lote",
]


class MainWindow(QMainWindow):

    def __init__(
        self,
        initial_pdf: Path | None = None,
        use_gpu: bool = True,
    ) -> None:
        super().__init__()
        self._use_gpu = use_gpu
        self._current_pdf: Path | None = None
        self._output_dir: Path | None = None
        self._preview_reader: PDFReader | None = None

        self.setWindowTitle(f"{APP_NAME} {APP_VERSION}")
        self.setMinimumSize(1300, 800)
        self.resize(1400, 860)
        self.setStyleSheet(DraculaTheme.STYLESHEET)

        self._setup_ui()
        self._toast = Toast(self)

        if initial_pdf and initial_pdf.is_file():
            self._load_pdf(initial_pdf)

    def _setup_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self._setup_sidebar(main_layout)
        self._setup_content(main_layout)
        self._setup_preview(main_layout)

        self._sidebar.setCurrentRow(0)

    # ------------------------------------------------------------------
    # Sidebar
    # ------------------------------------------------------------------

    def _setup_sidebar(self, parent_layout: QHBoxLayout) -> None:
        container = QWidget()
        container.setFixedWidth(220)
        container.setStyleSheet(
            f"background-color: {DraculaTheme.SIDEBAR}; border: none;"
        )
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(0, 24, 0, 20)
        vbox.setSpacing(0)

        title = QLabel(
            f'<span style="font-size:20px; font-weight:700; color:#ffffff;">'
            f"PDF</span>"
            f'<span style="font-size:20px; font-weight:700;'
            f' color:{DraculaTheme.PURPLE};">Forge</span>'
        )
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("background-color: transparent; margin-bottom: 4px;")
        vbox.addWidget(title)

        sub = QLabel(f"v{APP_VERSION}")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet(
            f"color: {DraculaTheme.COMMENT}; font-size: 11px;"
            " background-color: transparent; margin-bottom: 20px;"
        )
        vbox.addWidget(sub)

        sep = QWidget()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background-color: {DraculaTheme.CURRENT_LINE};")
        vbox.addWidget(sep)
        vbox.addSpacing(8)

        self._sidebar = QListWidget()
        self._sidebar.setStyleSheet(
            f"font-size: 15px; font-weight: 600;"
            f" background-color: {DraculaTheme.SIDEBAR};"
        )
        self._sidebar.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._sidebar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._sidebar.setFixedHeight(len(_SIDEBAR_ITEMS) * 54)

        for name in _SIDEBAR_ITEMS:
            item = QListWidgetItem(f"  {name}")
            self._sidebar.addItem(item)

        self._sidebar.currentRowChanged.connect(self._change_page)
        vbox.addWidget(self._sidebar)
        vbox.addStretch()

        parent_layout.addWidget(container)

    # ------------------------------------------------------------------
    # Content area
    # ------------------------------------------------------------------

    def _setup_content(self, parent_layout: QHBoxLayout) -> None:
        container = QWidget()
        container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)

        self._stack = QStackedWidget()
        vbox.addWidget(self._stack)

        self._page_editor = PageEditor(use_gpu=self._use_gpu)       # índice 0
        self._page_analyzer = PageAnalyzer(use_gpu=self._use_gpu)   # índice 1
        self._page_ocr = PageOCR(use_gpu=self._use_gpu)             # índice 2
        self._page_merge = PageMerge(use_gpu=self._use_gpu)         # índice 3
        self._page_split = PageSplit(use_gpu=self._use_gpu)         # índice 4
        self._page_compress = PageCompress(use_gpu=self._use_gpu)   # índice 5
        self._page_signature = PageSignature(use_gpu=self._use_gpu) # índice 6
        self._page_classifier = PageClassifier(use_gpu=self._use_gpu)  # índice 7
        self._page_batch = PageBatch(use_gpu=self._use_gpu)         # índice 8

        for page in (
            self._page_editor, self._page_analyzer, self._page_ocr,
            self._page_merge, self._page_split, self._page_compress,
            self._page_signature, self._page_classifier, self._page_batch,
        ):
            self._stack.addWidget(page)

        for page in (self._page_editor, self._page_analyzer, self._page_ocr):
            page.pdf_changed.connect(self._load_pdf)

        for page in (self._page_merge, self._page_split):
            page.pdf_changed.connect(self._load_pdf)

        parent_layout.addWidget(container)

    # ------------------------------------------------------------------
    # Preview panel
    # ------------------------------------------------------------------

    def _setup_preview(self, parent_layout: QHBoxLayout) -> None:
        container = QWidget()
        container.setFixedWidth(420)
        container.setStyleSheet(
            f"background-color: {DraculaTheme.BACKGROUND};"
            f" border-left: 1px solid {DraculaTheme.CURRENT_LINE};"
        )
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(16, 24, 16, 16)
        vbox.setSpacing(8)

        hdr = QLabel(
            f'<span style="color:{DraculaTheme.FOREGROUND}; font-size:15px;'
            f' font-weight:700;">Prévia do</span>'
            f'<span style="color:{DraculaTheme.PURPLE}; font-size:15px;'
            f' font-weight:700;"> PDF</span>'
        )
        hdr.setStyleSheet("background-color: transparent; margin-bottom: 6px;")
        vbox.addWidget(hdr)

        sep = QWidget()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background-color: {DraculaTheme.CURRENT_LINE};")
        vbox.addWidget(sep)
        vbox.addSpacing(4)

        def _info_label(key: str) -> tuple[QLabel, QLabel]:
            lk = QLabel(key)
            lk.setStyleSheet(
                f"color: {DraculaTheme.COMMENT}; font-size: 12px;"
                " background-color: transparent;"
            )
            lv = QLabel("—")
            lv.setStyleSheet(
                f"color: {DraculaTheme.FOREGROUND}; font-size: 12px;"
                " background-color: transparent;"
            )
            lv.setWordWrap(True)
            return lk, lv

        info_grid = QHBoxLayout()
        info_grid.setSpacing(0)
        left_col = QVBoxLayout()
        right_col = QVBoxLayout()
        left_col.setSpacing(4)
        right_col.setSpacing(4)

        self._lbl_file_k, self._lbl_file_v = _info_label("Arquivo")
        self._lbl_pages_k, self._lbl_pages_v = _info_label("Páginas")
        self._lbl_ver_k, self._lbl_ver_v = _info_label("Versão")
        self._lbl_size_k, self._lbl_size_v = _info_label("Tamanho")

        for lk, lv in (
            (self._lbl_file_k, self._lbl_file_v),
            (self._lbl_pages_k, self._lbl_pages_v),
            (self._lbl_ver_k, self._lbl_ver_v),
            (self._lbl_size_k, self._lbl_size_v),
        ):
            left_col.addWidget(lk)
            right_col.addWidget(lv)

        info_grid.addLayout(left_col)
        info_grid.addSpacing(10)
        info_grid.addLayout(right_col)
        vbox.addLayout(info_grid)

        vbox.addSpacing(8)
        sep2 = QWidget()
        sep2.setFixedHeight(1)
        sep2.setStyleSheet(f"background-color: {DraculaTheme.CURRENT_LINE};")
        vbox.addWidget(sep2)
        vbox.addSpacing(4)

        self._pdf_viewer = PDFPageViewer()
        self._pdf_viewer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        vbox.addWidget(self._pdf_viewer)

        parent_layout.addWidget(container)

    # ------------------------------------------------------------------
    # Slots e lógica interna
    # ------------------------------------------------------------------

    def _change_page(self, index: int) -> None:
        self._stack.setCurrentIndex(index)
        self._refresh_all_pages()

    def _refresh_all_pages(self) -> None:
        for page in (
            self._page_editor, self._page_analyzer, self._page_ocr, self._page_batch,
            self._page_merge, self._page_split, self._page_compress,
            self._page_signature, self._page_classifier,
        ):
            page.refresh_state(self._current_pdf, self._output_dir)

    def _load_pdf(self, path: Path) -> None:
        if self._preview_reader:
            try:
                self._preview_reader.close()
            except Exception:
                pass
            self._preview_reader = None

        self._current_pdf = path

        try:
            self._preview_reader = PDFReader(path)
            info = self._preview_reader.get_info()

            filename = path.name
            if len(filename) > 35:
                filename = filename[:32] + "..."
            self._lbl_file_v.setText(filename)
            self._lbl_pages_v.setText(str(info.page_count))
            self._lbl_ver_v.setText(info.pdf_version)
            self._lbl_size_v.setText(info.file_size)

            self._pdf_viewer.load_document(path)
            self._refresh_all_pages()
        except Exception as exc:
            logger.error("Falha ao abrir preview do PDF: %s", exc, exc_info=True)
            self._reset_preview(error=str(exc))

    def _reset_preview(self, error: str = "") -> None:
        self._lbl_file_v.setText("—")
        self._lbl_pages_v.setText("—")
        self._lbl_ver_v.setText("—")
        self._lbl_size_v.setText("—")

    def closeEvent(self, event) -> None:
        if self._preview_reader:
            try:
                self._preview_reader.close()
            except Exception:
                pass
        super().closeEvent(event)


# "A ordem é a forma da beleza." — Victor Hugo
