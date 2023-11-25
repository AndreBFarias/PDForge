import logging
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from ui.components import ExportDialog, FilePathButton, SectionHeader, Toast
from ui.styles import DraculaTheme
from ui.workers import ImageConvertWorker

logger = logging.getLogger("pdfforge.screens.images")

_FORMAT_MAP = {"PNG": "png", "JPEG": "jpeg", "TIFF": "tiff"}


class PageImages(QWidget):
    def __init__(
        self, use_gpu: bool = True, parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._use_gpu = use_gpu
        self._worker: ImageConvertWorker | None = None
        self._image_list: list[Path] = []
        self._last_output: Path | None = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 20)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        layout.addWidget(SectionHeader("Converter", "Imagens"))

        tabs = QTabWidget()
        tabs.addTab(self._build_pdf_to_images_tab(), "PDF para Imagens")
        tabs.addTab(self._build_images_to_pdf_tab(), "Imagens para PDF")
        layout.addWidget(tabs)

        self._progress = QProgressBar()
        self._progress.setRange(0, 0)
        self._progress.setVisible(False)
        layout.addWidget(self._progress)

        self._lbl_status = QLabel("Pronto.")
        self._lbl_status.setStyleSheet(
            f"color: {DraculaTheme.COMMENT};",
        )
        self._lbl_status.setWordWrap(True)
        layout.addWidget(self._lbl_status)

        self._toast = Toast(self)

    def _build_pdf_to_images_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(8)

        lbl = QLabel("Arquivo PDF")
        lbl.setStyleSheet(
            f"color: {DraculaTheme.COMMENT}; font-weight: bold;",
        )
        layout.addWidget(lbl)
        self._p2i_btn_in = FilePathButton(
            "Selecionar PDF  ", mode="pdf",
        )
        layout.addWidget(self._p2i_btn_in)

        lbl_dir = QLabel("Pasta de saída")
        lbl_dir.setStyleSheet(
            f"color: {DraculaTheme.COMMENT}; font-weight: bold;",
        )
        layout.addWidget(lbl_dir)
        self._p2i_btn_dir = FilePathButton(
            "Selecionar pasta  ", mode="dir",
        )
        layout.addWidget(self._p2i_btn_dir)

        row = QHBoxLayout()
        lbl_fmt = QLabel("Formato:")
        lbl_fmt.setStyleSheet(
            f"color: {DraculaTheme.COMMENT};",
        )
        self._p2i_cmb_fmt = QComboBox()
        for name in _FORMAT_MAP:
            self._p2i_cmb_fmt.addItem(name)
        lbl_dpi = QLabel("DPI:")
        lbl_dpi.setStyleSheet(
            f"color: {DraculaTheme.COMMENT};",
        )
        self._p2i_spn_dpi = QSpinBox()
        self._p2i_spn_dpi.setRange(72, 600)
        self._p2i_spn_dpi.setValue(150)
        row.addWidget(lbl_fmt)
        row.addWidget(self._p2i_cmb_fmt)
        row.addWidget(lbl_dpi)
        row.addWidget(self._p2i_spn_dpi)
        row.addStretch()
        layout.addLayout(row)

        btn = QPushButton("CONVERTER")
        btn.setObjectName("actionBtn")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed,
        )
        btn.clicked.connect(self._pdf_to_images)
        layout.addWidget(btn)
        self._p2i_btn_run = btn

        layout.addStretch()
        return tab

    def _build_images_to_pdf_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(8)

        btn_add = QPushButton("Adicionar imagens...")
        btn_add.setObjectName("secondaryBtn")
        btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add.clicked.connect(self._add_images)
        layout.addWidget(btn_add)

        self._i2p_list = QListWidget()
        self._i2p_list.setMaximumHeight(200)
        layout.addWidget(self._i2p_list)

        lbl_out = QLabel("Arquivo PDF de saída")
        lbl_out.setStyleSheet(
            f"color: {DraculaTheme.COMMENT}; font-weight: bold;",
        )
        layout.addWidget(lbl_out)
        self._i2p_btn_out = FilePathButton(
            "Selecionar arquivo de saída (.pdf)  ", mode="save",
        )
        layout.addWidget(self._i2p_btn_out)

        btn = QPushButton("CRIAR PDF")
        btn.setObjectName("actionBtn")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed,
        )
        btn.clicked.connect(self._images_to_pdf)
        layout.addWidget(btn)
        self._i2p_btn_run = btn

        layout.addStretch()
        return tab

    def refresh_state(
        self, pdf_path: Path | None, output_dir: Path | None,
    ) -> None:
        if pdf_path:
            self._p2i_btn_in.set_path(pdf_path)

    def _add_images(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Selecionar imagens",
            "",
            "Imagens (*.png *.jpg *.jpeg *.bmp *.tiff)",
        )
        for f in files:
            path = Path(f)
            self._image_list.append(path)
            self._i2p_list.addItem(path.name)

    def _pdf_to_images(self) -> None:
        pdf = self._p2i_btn_in.current_path
        out_dir = self._p2i_btn_dir.current_path
        if not pdf:
            self._toast.show_message("Selecione um arquivo PDF.")
            return
        if not out_dir:
            self._toast.show_message("Selecione a pasta de saída.")
            return
        if self._worker and self._worker.isRunning():
            return

        fmt = _FORMAT_MAP[self._p2i_cmb_fmt.currentText()]
        dpi = self._p2i_spn_dpi.value()

        self._last_output = out_dir
        self._p2i_btn_run.setEnabled(False)
        self._p2i_btn_run.setText("Convertendo...")
        self._progress.setVisible(True)
        self._lbl_status.setText("Processando...")

        self._worker = ImageConvertWorker(
            mode="pdf_to_images",
            input_path=pdf,
            output_dir=out_dir,
            fmt=fmt,
            dpi=dpi,
        )
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _images_to_pdf(self) -> None:
        if not self._image_list:
            self._toast.show_message("Adicione imagens primeiro.")
            return
        out = self._i2p_btn_out.current_path
        if not out:
            self._toast.show_message("Selecione o arquivo de saída.")
            return
        if self._worker and self._worker.isRunning():
            return

        self._last_output = out
        self._i2p_btn_run.setEnabled(False)
        self._i2p_btn_run.setText("Criando PDF...")
        self._progress.setVisible(True)
        self._lbl_status.setText("Processando...")

        self._worker = ImageConvertWorker(
            mode="images_to_pdf",
            image_paths=list(self._image_list),
            output_path=out,
        )
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_finished(self, result) -> None:
        self._p2i_btn_run.setEnabled(True)
        self._p2i_btn_run.setText("CONVERTER")
        self._i2p_btn_run.setEnabled(True)
        self._i2p_btn_run.setText("CRIAR PDF")
        self._progress.setVisible(False)

        if result.success:
            self._lbl_status.setStyleSheet(
                f"color: {DraculaTheme.GREEN};",
            )
            self._lbl_status.setText(
                f"Concluído — {result.total_pages} arquivo(s).",
            )
            if self._last_output and self._last_output.exists():
                ExportDialog(self._last_output, self).exec()
        else:
            self._lbl_status.setStyleSheet(
                f"color: {DraculaTheme.RED};",
            )
            self._lbl_status.setText(f"Erro: {result.error}")

    def _on_error(self, msg: str) -> None:
        self._p2i_btn_run.setEnabled(True)
        self._p2i_btn_run.setText("CONVERTER")
        self._i2p_btn_run.setEnabled(True)
        self._i2p_btn_run.setText("CRIAR PDF")
        self._progress.setVisible(False)
        self._lbl_status.setStyleSheet(f"color: {DraculaTheme.RED};")
        self._lbl_status.setText(f"Erro: {msg}")


# "A fotografia é a verdade em fragmentos." — Jean-Luc Godard
