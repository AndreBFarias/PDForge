import logging
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ui.components import FilePathButton, SectionHeader, Toast
from ui.styles import DraculaTheme
from ui.workers import CompressWorker

logger = logging.getLogger("pdfforge.screens.compress")

_PROFILE_MAP = {"Leve": "leve", "Médio": "medio", "Agressivo": "agressivo"}


class PageCompress(QWidget):
    def __init__(self, use_gpu: bool = True, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._use_gpu = use_gpu
        self._worker: CompressWorker | None = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 20)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        layout.addWidget(SectionHeader("Comprimir", "PDF"))

        lbl_in = QLabel("Arquivo PDF de entrada")
        lbl_in.setStyleSheet(f"color: {DraculaTheme.COMMENT}; font-weight: bold;")
        layout.addWidget(lbl_in)
        self._btn_in = FilePathButton("Selecionar PDF  ", mode="pdf")
        layout.addWidget(self._btn_in)

        lbl_out = QLabel("Arquivo de saída")
        lbl_out.setStyleSheet(f"color: {DraculaTheme.COMMENT}; font-weight: bold;")
        layout.addWidget(lbl_out)
        self._btn_out = FilePathButton("Selecionar arquivo de saída (.pdf)  ", mode="pdf")
        layout.addWidget(self._btn_out)

        lbl_profile = QLabel("Perfil de compressão")
        lbl_profile.setStyleSheet(f"color: {DraculaTheme.COMMENT}; font-weight: bold;")
        layout.addWidget(lbl_profile)
        self._cmb_profile = QComboBox()
        for name in _PROFILE_MAP:
            self._cmb_profile.addItem(name)
        self._cmb_profile.setCurrentIndex(1)
        layout.addWidget(self._cmb_profile)

        btn_analyze = QPushButton("ANALISAR")
        btn_analyze.setObjectName("secondaryBtn")
        btn_analyze.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_analyze.clicked.connect(self._analyze)
        layout.addWidget(btn_analyze)

        self._lbl_estimate = QLabel("")
        self._lbl_estimate.setWordWrap(True)
        self._lbl_estimate.setStyleSheet(
            f"color: {DraculaTheme.CYAN}; font-size: 13px; background-color: transparent;"
        )
        layout.addWidget(self._lbl_estimate)

        self._progress = QProgressBar()
        self._progress.setRange(0, 0)
        self._progress.setVisible(False)
        layout.addWidget(self._progress)

        self._lbl_status = QLabel("Pronto.")
        self._lbl_status.setStyleSheet(f"color: {DraculaTheme.COMMENT};")
        self._lbl_status.setWordWrap(True)
        layout.addWidget(self._lbl_status)

        self._btn_run = QPushButton("COMPRIMIR")
        self._btn_run.setObjectName("actionBtn")
        self._btn_run.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_run.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._btn_run.clicked.connect(self._run)
        layout.addWidget(self._btn_run)

        self._toast = Toast(self)

    def refresh_state(self, pdf_path: Path | None, output_dir: Path | None) -> None:
        if pdf_path:
            self._btn_in.set_path(pdf_path)

    def _analyze(self) -> None:
        pdf = self._btn_in.current_path
        if not pdf:
            self._toast.show_message("Selecione um arquivo PDF.")
            return

        try:
            import fitz
            from core.pdf_compressor import PDFCompressor
            doc = fitz.open(str(pdf))
            profile = _PROFILE_MAP[self._cmb_profile.currentText()]
            ct = PDFCompressor().analyze_content_type(doc)
            estimate = PDFCompressor().get_compression_estimate(doc, profile)
            doc.close()
            self._lbl_estimate.setText(
                f"Tipo detectado: {ct.value} | "
                f"Original: {estimate['original_mb']:.2f} MB | "
                f"Estimado: {estimate['estimated_mb']:.2f} MB | "
                f"Redução: ~{estimate['reduction_pct']:.0f}%"
            )
        except Exception as exc:
            logger.error("Erro na analise: %s", exc)
            self._lbl_estimate.setText(f"Erro na análise: {exc}")

    def _run(self) -> None:
        pdf = self._btn_in.current_path
        out = self._btn_out.current_path

        if not pdf:
            self._toast.show_message("Selecione um arquivo PDF.")
            return
        if not out:
            self._toast.show_message("Selecione o arquivo de saída.")
            return
        if self._worker and self._worker.isRunning():
            return

        profile = _PROFILE_MAP[self._cmb_profile.currentText()]
        self._btn_run.setEnabled(False)
        self._btn_run.setText("Comprimindo...")
        self._progress.setVisible(True)
        self._lbl_status.setStyleSheet(f"color: {DraculaTheme.COMMENT};")
        self._lbl_status.setText("Processando...")

        self._worker = CompressWorker(pdf_path=pdf, output_path=out, profile=profile)
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_finished(self, result) -> None:
        self._btn_run.setEnabled(True)
        self._btn_run.setText("COMPRIMIR")
        self._progress.setVisible(False)
        if result.success:
            self._lbl_status.setStyleSheet(f"color: {DraculaTheme.GREEN};")
            self._lbl_status.setText(
                f"Concluido: {result.original_size_mb:.2f} MB -> {result.compressed_size_mb:.2f} MB "
                f"({result.reduction_pct:.1f}% de redução)"
            )
        else:
            self._lbl_status.setStyleSheet(f"color: {DraculaTheme.RED};")
            self._lbl_status.setText(f"Erro: {result.error}")

    def _on_error(self, msg: str) -> None:
        self._btn_run.setEnabled(True)
        self._btn_run.setText("COMPRIMIR")
        self._progress.setVisible(False)
        self._lbl_status.setStyleSheet(f"color: {DraculaTheme.RED};")
        self._lbl_status.setText(f"Erro: {msg}")


# "Menos é mais." — Ludwig Mies van der Rohe
