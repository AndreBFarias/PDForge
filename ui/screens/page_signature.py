import logging
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from config.settings import Settings
from ui.components import FilePathButton, SectionHeader, Toast
from ui.styles import DraculaTheme
from ui.workers import ReinsertWorker, SignatureWorker

logger = logging.getLogger("pdfforge.screens.signature")


class PageSignature(QWidget):
    def __init__(self, use_gpu: bool = True, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._use_gpu = use_gpu
        self._worker: SignatureWorker | ReinsertWorker | None = None
        self._regions: list = []
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 20)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        layout.addWidget(SectionHeader("Assinaturas", ""))

        lbl_pdf = QLabel("Arquivo PDF de entrada")
        lbl_pdf.setStyleSheet(f"color: {DraculaTheme.COMMENT}; font-weight: bold;")
        layout.addWidget(lbl_pdf)
        self._btn_pdf = FilePathButton("Selecionar PDF  ", mode="pdf")
        layout.addWidget(self._btn_pdf)

        self._btn_detect = QPushButton("DETECTAR ASSINATURAS")
        self._btn_detect.setObjectName("secondaryBtn")
        self._btn_detect.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_detect.clicked.connect(self._detect)
        layout.addWidget(self._btn_detect)

        self._list_regions = QListWidget()
        self._list_regions.setMinimumHeight(100)
        self._list_regions.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout.addWidget(self._list_regions)

        action_row = QHBoxLayout()
        self._btn_extract = QPushButton("EXTRAIR SELECIONADA")
        self._btn_extract.setObjectName("secondaryBtn")
        self._btn_extract.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_extract.clicked.connect(self._extract)
        action_row.addWidget(self._btn_extract)

        self._btn_reinsert = QPushButton("REINSERIR")
        self._btn_reinsert.setObjectName("actionBtn")
        self._btn_reinsert.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_reinsert.clicked.connect(self._reinsert)
        action_row.addWidget(self._btn_reinsert)
        layout.addLayout(action_row)

        lbl_img = QLabel("Imagem para reinserção (PNG/JPG)")
        lbl_img.setStyleSheet(f"color: {DraculaTheme.COMMENT}; font-weight: bold;")
        layout.addWidget(lbl_img)
        self._btn_img = FilePathButton("Selecionar imagem  ", mode="pdf")
        layout.addWidget(self._btn_img)

        lbl_out = QLabel("PDF de saída")
        lbl_out.setStyleSheet(f"color: {DraculaTheme.COMMENT}; font-weight: bold;")
        layout.addWidget(lbl_out)
        self._btn_out = FilePathButton("Selecionar arquivo de saída (.pdf)  ", mode="pdf")
        layout.addWidget(self._btn_out)

        self._lbl_status = QLabel("Pronto.")
        self._lbl_status.setWordWrap(True)
        self._lbl_status.setStyleSheet(f"color: {DraculaTheme.COMMENT};")
        layout.addWidget(self._lbl_status)

        self._toast = Toast(self)

    def refresh_state(self, pdf_path: Path | None, output_dir: Path | None) -> None:
        if pdf_path:
            self._btn_pdf.set_path(pdf_path)

    def _detect(self) -> None:
        pdf = self._btn_pdf.current_path
        if not pdf:
            self._toast.show_message("Selecione um arquivo PDF.")
            return
        if self._worker and self._worker.isRunning():
            return

        self._btn_detect.setEnabled(False)
        self._btn_detect.setText("Detectando...")
        self._list_regions.clear()
        self._regions = []

        self._worker = SignatureWorker(pdf_path=pdf)
        self._worker.finished.connect(self._on_detect_finished)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_detect_finished(self, regions: list) -> None:
        self._btn_detect.setEnabled(True)
        self._btn_detect.setText("DETECTAR ASSINATURAS")
        self._regions = regions

        if not regions:
            self._lbl_status.setStyleSheet(f"color: {DraculaTheme.COMMENT};")
            self._lbl_status.setText("Nenhuma assinatura detectada.")
            return

        for region in regions:
            item = QListWidgetItem(
                f"Página {region.page_index + 1} — confiança {region.confidence:.0%}"
            )
            item.setData(Qt.ItemDataRole.UserRole, region)
            self._list_regions.addItem(item)

        self._lbl_status.setStyleSheet(f"color: {DraculaTheme.GREEN};")
        self._lbl_status.setText(f"{len(regions)} assinatura(s) detectada(s).")

    def _extract(self) -> None:
        item = self._list_regions.currentItem()
        if not item:
            self._toast.show_message("Selecione uma assinatura na lista.")
            return

        pdf = self._btn_pdf.current_path
        if not pdf:
            self._toast.show_message("Selecione o arquivo PDF.")
            return

        region = item.data(Qt.ItemDataRole.UserRole)
        tmp_dir = Settings().SIGNATURE_TEMP_DIR
        tmp_dir.mkdir(parents=True, exist_ok=True)
        out_path = tmp_dir / f"sig_p{region.page_index + 1}_{id(region)}.png"

        try:
            import fitz
            from core.signature_handler import SignatureHandler
            doc = fitz.open(str(pdf))
            SignatureHandler().extract_signature(doc, region, out_path, scale=Settings().SIGNATURE_EXTRACT_SCALE)
            doc.close()
            self._lbl_status.setStyleSheet(f"color: {DraculaTheme.GREEN};")
            self._lbl_status.setText(f"Extraida em: {out_path}")
        except Exception as exc:
            logger.error("Erro ao extrair assinatura: %s", exc)
            self._lbl_status.setStyleSheet(f"color: {DraculaTheme.RED};")
            self._lbl_status.setText(f"Erro: {exc}")

    def _reinsert(self) -> None:
        item = self._list_regions.currentItem()
        if not item:
            self._toast.show_message("Selecione uma assinatura na lista.")
            return

        pdf = self._btn_pdf.current_path
        img = self._btn_img.current_path
        out = self._btn_out.current_path

        if not pdf or not img or not out:
            self._toast.show_message("Selecione PDF, imagem e arquivo de saída.")
            return

        if self._worker and self._worker.isRunning():
            return

        region = item.data(Qt.ItemDataRole.UserRole)
        self._btn_reinsert.setEnabled(False)
        self._btn_reinsert.setText("Reinserindo...")

        self._worker = ReinsertWorker(
            pdf_path=pdf, region=region, image_path=img, output_path=out
        )
        self._worker.finished.connect(self._on_reinsert_finished)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_reinsert_finished(self, ok: bool) -> None:
        self._btn_reinsert.setEnabled(True)
        self._btn_reinsert.setText("REINSERIR")
        if ok:
            self._lbl_status.setStyleSheet(f"color: {DraculaTheme.GREEN};")
            self._lbl_status.setText("Assinatura reinserida com sucesso.")
        else:
            self._lbl_status.setStyleSheet(f"color: {DraculaTheme.RED};")
            self._lbl_status.setText("Falha ao reinserir assinatura.")

    def _on_error(self, msg: str) -> None:
        self._btn_detect.setEnabled(True)
        self._btn_detect.setText("DETECTAR ASSINATURAS")
        self._btn_reinsert.setEnabled(True)
        self._btn_reinsert.setText("REINSERIR")
        self._lbl_status.setStyleSheet(f"color: {DraculaTheme.RED};")
        self._lbl_status.setText(f"Erro: {msg}")


# "A identidade é mais do que uma imagem." — Anônimo
