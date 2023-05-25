import logging
from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from ui.components import FilePathButton, SectionHeader, Toast
from ui.styles import DraculaTheme
from ui.workers import SplitWorker

logger = logging.getLogger("pdfforge.screens.split")


class PageSplit(QWidget):
    pdf_changed = pyqtSignal(Path)

    def __init__(self, use_gpu: bool = True, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._use_gpu = use_gpu
        self._worker: SplitWorker | None = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 20)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        layout.addWidget(SectionHeader("Dividir", "PDF"))

        lbl_pdf = QLabel("Arquivo PDF de entrada")
        lbl_pdf.setStyleSheet(f"color: {DraculaTheme.COMMENT}; font-weight: bold;")
        layout.addWidget(lbl_pdf)

        self._btn_pdf = FilePathButton("Selecionar PDF  ", mode="pdf")
        self._btn_pdf.path_selected.connect(self._on_pdf_selected)
        layout.addWidget(self._btn_pdf)

        lbl_out = QLabel("Pasta de saída")
        lbl_out.setStyleSheet(f"color: {DraculaTheme.COMMENT}; font-weight: bold;")
        layout.addWidget(lbl_out)

        self._btn_out = FilePathButton("Selecionar pasta de saída  ", mode="dir")
        layout.addWidget(self._btn_out)

        self._tabs = QTabWidget()

        # Aba Por Range
        tab_range = QWidget()
        vbox_range = QVBoxLayout(tab_range)
        vbox_range.setContentsMargins(12, 12, 12, 12)
        lbl_range = QLabel('Páginas base 0, separadas por vírgula. Ex: "0-2, 3-4, 5-9"')
        lbl_range.setStyleSheet(f"color: {DraculaTheme.COMMENT}; font-size: 12px;")
        vbox_range.addWidget(lbl_range)
        self._edit_ranges = QLineEdit()
        self._edit_ranges.setPlaceholderText("0-2, 3-4, 5-9")
        vbox_range.addWidget(self._edit_ranges)
        vbox_range.addStretch()
        self._tabs.addTab(tab_range, "Por Range")

        # Aba Por Tamanho
        tab_size = QWidget()
        vbox_size = QVBoxLayout(tab_size)
        vbox_size.setContentsMargins(12, 12, 12, 12)
        lbl_size = QLabel("Tamanho máximo por parte (MB):")
        lbl_size.setStyleSheet(f"color: {DraculaTheme.COMMENT};")
        vbox_size.addWidget(lbl_size)
        self._spin_mb = QDoubleSpinBox()
        self._spin_mb.setRange(1.0, 500.0)
        self._spin_mb.setValue(10.0)
        self._spin_mb.setSingleStep(1.0)
        vbox_size.addWidget(self._spin_mb)
        vbox_size.addStretch()
        self._tabs.addTab(tab_size, "Por Tamanho")

        # Aba Por Marcadores
        tab_bk = QWidget()
        vbox_bk = QVBoxLayout(tab_bk)
        vbox_bk.setContentsMargins(12, 12, 12, 12)
        lbl_bk = QLabel("Divide o PDF nos marcadores (TOC) de nível 1.")
        lbl_bk.setStyleSheet(f"color: {DraculaTheme.COMMENT};")
        lbl_bk.setWordWrap(True)
        vbox_bk.addWidget(lbl_bk)
        vbox_bk.addStretch()
        self._tabs.addTab(tab_bk, "Por Marcadores")

        layout.addWidget(self._tabs)

        self._progress = QProgressBar()
        self._progress.setRange(0, 0)
        self._progress.setVisible(False)
        layout.addWidget(self._progress)

        self._lbl_status = QLabel("Pronto.")
        self._lbl_status.setStyleSheet(f"color: {DraculaTheme.COMMENT};")
        self._lbl_status.setWordWrap(True)
        layout.addWidget(self._lbl_status)

        self._btn_run = QPushButton("DIVIDIR")
        self._btn_run.setObjectName("actionBtn")
        self._btn_run.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_run.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._btn_run.clicked.connect(self._run)
        layout.addWidget(self._btn_run)

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

    def _parse_ranges(self, text: str) -> list[tuple[int, int]] | None:
        try:
            parts = [p.strip() for p in text.split(",") if p.strip()]
            result = []
            for part in parts:
                a, b = part.split("-")
                result.append((int(a.strip()), int(b.strip())))
            return result
        except Exception:
            return None

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

        tab = self._tabs.currentIndex()
        mode, ranges, max_mb = "bookmarks", None, 10.0

        if tab == 0:
            ranges = self._parse_ranges(self._edit_ranges.text())
            if not ranges:
                self._toast.show_message("Formato de range inválido. Use: 0-2, 3-4")
                return
            mode = "range"
        elif tab == 1:
            max_mb = self._spin_mb.value()
            mode = "size"

        self._btn_run.setEnabled(False)
        self._btn_run.setText("Dividindo...")
        self._progress.setVisible(True)
        self._lbl_status.setStyleSheet(f"color: {DraculaTheme.COMMENT};")
        self._lbl_status.setText("Processando...")

        self._worker = SplitWorker(
            pdf_path=pdf,
            mode=mode,
            output_dir=out_dir,
            base_name=pdf.stem,
            ranges=ranges,
            max_mb=max_mb,
        )
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_finished(self, result) -> None:
        self._btn_run.setEnabled(True)
        self._btn_run.setText("DIVIDIR")
        self._progress.setVisible(False)
        if result.success:
            names = ", ".join(f.name for f in result.output_files[:4])
            extra = f" (+{len(result.output_files)-4} mais)" if len(result.output_files) > 4 else ""
            self._lbl_status.setStyleSheet(f"color: {DraculaTheme.GREEN};")
            self._lbl_status.setText(f"{len(result.output_files)} arquivo(s): {names}{extra}")
        else:
            self._lbl_status.setStyleSheet(f"color: {DraculaTheme.RED};")
            self._lbl_status.setText(f"Erro: {result.error}")

    def _on_error(self, msg: str) -> None:
        self._btn_run.setEnabled(True)
        self._btn_run.setText("DIVIDIR")
        self._progress.setVisible(False)
        self._lbl_status.setStyleSheet(f"color: {DraculaTheme.RED};")
        self._lbl_status.setText(f"Erro: {msg}")


# "Dividir para conquistar." — Júlio César
