import logging
from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ui.components import FilePathButton, SectionHeader, Toast
from ui.styles import DraculaTheme
from ui.workers import OCRWorker
from utils.file_utils import ensure_output_path

logger = logging.getLogger("pdfforge.screens.ocr")

_LANGUAGE_OPTIONS = {
    "Português + Inglês": ["pt", "en"],
    "Português": ["pt"],
    "Inglês": ["en"],
    "Português + Inglês + Espanhol": ["pt", "en", "es"],
}


class PageOCR(QWidget):
    """Tela de reconhecimento óptico de caracteres (OCR)."""

    pdf_changed = pyqtSignal(Path)

    def __init__(self, use_gpu: bool = True, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._use_gpu = use_gpu
        self._worker: OCRWorker | None = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 20)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        layout.addWidget(SectionHeader("Extração", "OCR"))

        lbl_pdf = QLabel("Arquivo PDF")
        lbl_pdf.setStyleSheet(f"color: {DraculaTheme.COMMENT}; font-weight: bold;")
        layout.addWidget(lbl_pdf)
        self._btn_pdf = FilePathButton("Selecionar PDF  ", mode="pdf")
        self._btn_pdf.path_selected.connect(self._on_pdf_selected)
        layout.addWidget(self._btn_pdf)

        lbl_out = QLabel("Pasta de saída")
        lbl_out.setStyleSheet(f"color: {DraculaTheme.COMMENT}; font-weight: bold;")
        layout.addWidget(lbl_out)
        self._btn_out = FilePathButton("Selecionar Pasta de Saída  ", mode="dir")
        layout.addWidget(self._btn_out)

        lbl_lang = QLabel("Idiomas para OCR")
        lbl_lang.setStyleSheet(f"color: {DraculaTheme.COMMENT}; font-weight: bold;")
        layout.addWidget(lbl_lang)
        self._cmb_lang = QComboBox()
        for option in _LANGUAGE_OPTIONS:
            self._cmb_lang.addItem(option)
        layout.addWidget(self._cmb_lang)

        self._chk_gpu = QCheckBox("Usar GPU (CUDA)")
        self._chk_gpu.setChecked(self._use_gpu)
        layout.addWidget(self._chk_gpu)

        layout.addSpacing(4)

        # Barra de progresso
        self._progress = QProgressBar()
        self._progress.setRange(0, 100)
        self._progress.setValue(0)
        self._progress.setTextVisible(True)
        layout.addWidget(self._progress)

        self._lbl_status = QLabel("Pronto.")
        self._lbl_status.setStyleSheet(f"color: {DraculaTheme.COMMENT};")
        layout.addWidget(self._lbl_status)

        layout.addStretch()

        # Botões
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self._btn_run = QPushButton("EXECUTAR OCR")
        self._btn_run.setObjectName("actionBtn")
        self._btn_run.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_run.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._btn_run.clicked.connect(self._run)
        btn_row.addWidget(self._btn_run, stretch=2)

        layout.addLayout(btn_row)

        # Resultado: texto extraído
        lbl_res = QLabel("Texto extraído (prévia)")
        lbl_res.setStyleSheet(f"color: {DraculaTheme.COMMENT}; font-weight: bold; margin-top: 8px;")
        layout.addWidget(lbl_res)

        self._txt_result = QPlainTextEdit()
        self._txt_result.setReadOnly(True)
        self._txt_result.setPlaceholderText("O texto OCR aparecerá aqui após o processamento...")
        self._txt_result.setMaximumHeight(140)
        layout.addWidget(self._txt_result)

        self._toast = Toast(self)

    def refresh_state(self, pdf_path: Path | None, output_dir: Path | None) -> None:
        if pdf_path:
            self._btn_pdf.set_path(pdf_path)
        if output_dir:
            self._btn_out.set_path(output_dir)

    def _on_pdf_selected(self, path: Path) -> None:
        self.pdf_changed.emit(path)
        if not self._btn_out.current_path:
            self._btn_out.set_path(path.parent / "data_output")

    def _run(self) -> None:
        pdf = self._btn_pdf.current_path
        out_dir = self._btn_out.current_path

        if not pdf:
            self._toast.show_message("Selecione um arquivo PDF.")
            return
        if not out_dir:
            self._toast.show_message("Selecione a pasta de saída.")
            return
        if self._worker and self._worker.isRunning():
            return

        lang_key = self._cmb_lang.currentText()
        languages = _LANGUAGE_OPTIONS.get(lang_key, ["pt", "en"])
        use_gpu = self._chk_gpu.isChecked()
        output_path = ensure_output_path(pdf, out_dir, suffix="_ocr")

        self._btn_run.setEnabled(False)
        self._btn_run.setText("Processando...")
        self._progress.setValue(0)
        self._txt_result.clear()

        self._worker = OCRWorker(
            pdf_path=pdf,
            output_path=output_path,
            languages=languages,
            use_gpu=use_gpu,
        )
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_progress(self, current: int, total: int, msg: str) -> None:
        if total > 0:
            pct = int(current / total * 100)
            self._progress.setValue(pct)
        self._lbl_status.setText(msg)

    def _on_finished(self, results: dict) -> None:
        self._btn_run.setEnabled(True)
        self._btn_run.setText("EXECUTAR OCR")
        self._progress.setValue(100)
        self._lbl_status.setText(f"Concluído — {len(results)} página(s) processada(s).")

        preview_texts = []
        for page_num in sorted(results.keys())[:3]:
            text = results[page_num].strip()
            if text:
                preview_texts.append(f"[Pág. {page_num + 1}]\n{text[:300]}")
        self._txt_result.setPlainText("\n\n".join(preview_texts) or "(nenhum texto extraído)")

    def _on_error(self, msg: str) -> None:
        self._btn_run.setEnabled(True)
        self._btn_run.setText("EXECUTAR OCR")
        self._lbl_status.setStyleSheet(f"color: {DraculaTheme.RED};")
        self._lbl_status.setText(f"Erro: {msg}")


# "A persistência é o caminho do êxito." — Charles Chaplin
