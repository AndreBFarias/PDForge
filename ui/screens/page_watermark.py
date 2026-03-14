import logging
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QColorDialog,
    QComboBox,
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QSlider,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from ui.components import ExportDialog, FilePathButton, SectionHeader, Toast
from ui.styles import DraculaTheme
from ui.workers import WatermarkWorker

logger = logging.getLogger("pdfforge.screens.watermark")

_POSITION_MAP = {
    "Centro": "center",
    "Diagonal": "diagonal",
    "Repetição": "tile",
}


class PageWatermark(QWidget):
    def __init__(
        self, use_gpu: bool = True, parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._use_gpu = use_gpu
        self._worker: WatermarkWorker | None = None
        self._color = (128, 128, 128)
        self._last_output: Path | None = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 20)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        layout.addWidget(SectionHeader("Marca d'Água", ""))

        tabs = QTabWidget()
        tabs.addTab(self._build_text_tab(), "Texto")
        tabs.addTab(self._build_image_tab(), "Imagem")
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

    def _build_text_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(8)

        lbl_in = QLabel("Arquivo PDF")
        lbl_in.setStyleSheet(
            f"color: {DraculaTheme.COMMENT}; font-weight: bold;",
        )
        layout.addWidget(lbl_in)
        self._txt_btn_in = FilePathButton(
            "Selecionar PDF  ", mode="pdf",
        )
        layout.addWidget(self._txt_btn_in)

        lbl_out = QLabel("Arquivo de saída")
        lbl_out.setStyleSheet(
            f"color: {DraculaTheme.COMMENT}; font-weight: bold;",
        )
        layout.addWidget(lbl_out)
        self._txt_btn_out = FilePathButton(
            "Selecionar arquivo de saída (.pdf)  ", mode="save",
        )
        layout.addWidget(self._txt_btn_out)

        lbl_text = QLabel("Texto da marca")
        lbl_text.setStyleSheet(
            f"color: {DraculaTheme.COMMENT}; font-weight: bold;",
        )
        layout.addWidget(lbl_text)
        self._txt_input = QLineEdit()
        self._txt_input.setPlaceholderText("CONFIDENCIAL")
        layout.addWidget(self._txt_input)

        row1 = QHBoxLayout()
        lbl_fs = QLabel("Tamanho:")
        lbl_fs.setStyleSheet(f"color: {DraculaTheme.COMMENT};")
        self._txt_fontsize = QSpinBox()
        self._txt_fontsize.setRange(12, 200)
        self._txt_fontsize.setValue(48)
        lbl_pos = QLabel("Posição:")
        lbl_pos.setStyleSheet(f"color: {DraculaTheme.COMMENT};")
        self._txt_position = QComboBox()
        for name in _POSITION_MAP:
            self._txt_position.addItem(name)
        row1.addWidget(lbl_fs)
        row1.addWidget(self._txt_fontsize)
        row1.addWidget(lbl_pos)
        row1.addWidget(self._txt_position)
        row1.addStretch()
        layout.addLayout(row1)

        row2 = QHBoxLayout()
        lbl_op = QLabel("Opacidade:")
        lbl_op.setStyleSheet(f"color: {DraculaTheme.COMMENT};")
        self._txt_opacity = QSlider(Qt.Orientation.Horizontal)
        self._txt_opacity.setRange(5, 100)
        self._txt_opacity.setValue(30)
        self._txt_opacity_lbl = QLabel("30%")
        self._txt_opacity_lbl.setStyleSheet(
            f"color: {DraculaTheme.FOREGROUND};",
        )
        self._txt_opacity.valueChanged.connect(
            lambda v: self._txt_opacity_lbl.setText(f"{v}%"),
        )
        lbl_rot = QLabel("Rotação:")
        lbl_rot.setStyleSheet(f"color: {DraculaTheme.COMMENT};")
        self._txt_rotation = QSpinBox()
        self._txt_rotation.setRange(-180, 180)
        self._txt_rotation.setValue(-45)
        row2.addWidget(lbl_op)
        row2.addWidget(self._txt_opacity)
        row2.addWidget(self._txt_opacity_lbl)
        row2.addWidget(lbl_rot)
        row2.addWidget(self._txt_rotation)
        layout.addLayout(row2)

        btn_color = QPushButton("Cor da marca")
        btn_color.setObjectName("secondaryBtn")
        btn_color.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_color.clicked.connect(self._pick_color)
        layout.addWidget(btn_color)

        btn = QPushButton("APLICAR MARCA D'ÁGUA")
        btn.setObjectName("actionBtn")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed,
        )
        btn.clicked.connect(self._apply_text)
        layout.addWidget(btn)
        self._txt_btn_run = btn

        layout.addStretch()
        return tab

    def _build_image_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(8)

        lbl_in = QLabel("Arquivo PDF")
        lbl_in.setStyleSheet(
            f"color: {DraculaTheme.COMMENT}; font-weight: bold;",
        )
        layout.addWidget(lbl_in)
        self._img_btn_in = FilePathButton(
            "Selecionar PDF  ", mode="pdf",
        )
        layout.addWidget(self._img_btn_in)

        lbl_img = QLabel("Imagem da marca")
        lbl_img.setStyleSheet(
            f"color: {DraculaTheme.COMMENT}; font-weight: bold;",
        )
        layout.addWidget(lbl_img)
        self._img_btn_img = FilePathButton(
            "Selecionar imagem  ", mode="image",
        )
        layout.addWidget(self._img_btn_img)

        lbl_out = QLabel("Arquivo de saída")
        lbl_out.setStyleSheet(
            f"color: {DraculaTheme.COMMENT}; font-weight: bold;",
        )
        layout.addWidget(lbl_out)
        self._img_btn_out = FilePathButton(
            "Selecionar arquivo de saída (.pdf)  ", mode="save",
        )
        layout.addWidget(self._img_btn_out)

        row = QHBoxLayout()
        lbl_op = QLabel("Opacidade:")
        lbl_op.setStyleSheet(f"color: {DraculaTheme.COMMENT};")
        self._img_opacity = QSlider(Qt.Orientation.Horizontal)
        self._img_opacity.setRange(5, 100)
        self._img_opacity.setValue(30)
        self._img_opacity_lbl = QLabel("30%")
        self._img_opacity_lbl.setStyleSheet(
            f"color: {DraculaTheme.FOREGROUND};",
        )
        self._img_opacity.valueChanged.connect(
            lambda v: self._img_opacity_lbl.setText(f"{v}%"),
        )
        lbl_sc = QLabel("Escala:")
        lbl_sc.setStyleSheet(f"color: {DraculaTheme.COMMENT};")
        self._img_scale = QDoubleSpinBox()
        self._img_scale.setRange(0.1, 3.0)
        self._img_scale.setValue(1.0)
        self._img_scale.setSingleStep(0.1)
        row.addWidget(lbl_op)
        row.addWidget(self._img_opacity)
        row.addWidget(self._img_opacity_lbl)
        row.addWidget(lbl_sc)
        row.addWidget(self._img_scale)
        layout.addLayout(row)

        btn = QPushButton("APLICAR MARCA D'ÁGUA")
        btn.setObjectName("actionBtn")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed,
        )
        btn.clicked.connect(self._apply_image)
        layout.addWidget(btn)
        self._img_btn_run = btn

        layout.addStretch()
        return tab

    def refresh_state(
        self, pdf_path: Path | None, output_dir: Path | None,
    ) -> None:
        if pdf_path:
            self._txt_btn_in.set_path(pdf_path)
            self._img_btn_in.set_path(pdf_path)

    def _pick_color(self) -> None:
        from PyQt6.QtGui import QColor
        color = QColorDialog.getColor(
            QColor(*self._color), self, "Cor da marca d'água",
        )
        if color.isValid():
            self._color = (color.red(), color.green(), color.blue())

    def _apply_text(self) -> None:
        pdf = self._txt_btn_in.current_path
        out = self._txt_btn_out.current_path
        text = self._txt_input.text().strip()

        if not pdf:
            self._toast.show_message("Selecione um arquivo PDF.")
            return
        if not out:
            self._toast.show_message("Selecione o arquivo de saída.")
            return
        if not text:
            self._toast.show_message("Informe o texto da marca.")
            return
        if self._worker and self._worker.isRunning():
            return

        from core.pdf_watermark import WatermarkConfig
        config = WatermarkConfig(
            text=text,
            font_size=self._txt_fontsize.value(),
            color=self._color,
            opacity=self._txt_opacity.value() / 100.0,
            rotation=float(self._txt_rotation.value()),
            position=_POSITION_MAP[self._txt_position.currentText()],
        )

        self._last_output = out
        self._txt_btn_run.setEnabled(False)
        self._txt_btn_run.setText("Aplicando...")
        self._progress.setVisible(True)
        self._lbl_status.setText("Processando...")

        self._worker = WatermarkWorker(
            mode="text",
            input_path=pdf,
            output_path=out,
            config=config,
        )
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _apply_image(self) -> None:
        pdf = self._img_btn_in.current_path
        img = self._img_btn_img.current_path
        out = self._img_btn_out.current_path

        if not pdf:
            self._toast.show_message("Selecione um arquivo PDF.")
            return
        if not img:
            self._toast.show_message("Selecione a imagem.")
            return
        if not out:
            self._toast.show_message("Selecione o arquivo de saída.")
            return
        if self._worker and self._worker.isRunning():
            return

        self._last_output = out
        self._img_btn_run.setEnabled(False)
        self._img_btn_run.setText("Aplicando...")
        self._progress.setVisible(True)
        self._lbl_status.setText("Processando...")

        self._worker = WatermarkWorker(
            mode="image",
            input_path=pdf,
            output_path=out,
            image_path=img,
            opacity=self._img_opacity.value() / 100.0,
            scale=self._img_scale.value(),
        )
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_finished(self, result) -> None:
        self._txt_btn_run.setEnabled(True)
        self._txt_btn_run.setText("APLICAR MARCA D'ÁGUA")
        self._img_btn_run.setEnabled(True)
        self._img_btn_run.setText("APLICAR MARCA D'ÁGUA")
        self._progress.setVisible(False)

        if result.success:
            self._lbl_status.setStyleSheet(
                f"color: {DraculaTheme.GREEN};",
            )
            self._lbl_status.setText(
                f"Concluído — {result.pages_processed} páginas.",
            )
            if self._last_output and self._last_output.exists():
                ExportDialog(self._last_output, self).exec()
        else:
            self._lbl_status.setStyleSheet(
                f"color: {DraculaTheme.RED};",
            )
            self._lbl_status.setText(f"Erro: {result.error}")

    def _on_error(self, msg: str) -> None:
        self._txt_btn_run.setEnabled(True)
        self._txt_btn_run.setText("APLICAR MARCA D'ÁGUA")
        self._img_btn_run.setEnabled(True)
        self._img_btn_run.setText("APLICAR MARCA D'ÁGUA")
        self._progress.setVisible(False)
        self._lbl_status.setStyleSheet(f"color: {DraculaTheme.RED};")
        self._lbl_status.setText(f"Erro: {msg}")


# "A arte é a mentira que nos permite ver a verdade." — Pablo Picasso
