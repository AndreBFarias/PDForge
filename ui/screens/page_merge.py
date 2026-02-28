import logging
from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFileDialog,
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
from ui.widgets.drag_drop_list import DragDropPDFList
from ui.workers import MergeWorker

logger = logging.getLogger("pdfforge.screens.merge")


class PageMerge(QWidget):
    pdf_changed = pyqtSignal(Path)

    def __init__(self, use_gpu: bool = True, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._use_gpu = use_gpu
        self._worker: MergeWorker | None = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 20)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        layout.addWidget(SectionHeader("Mesclar", "PDFs"))

        lbl_hint = QLabel("Arraste PDFs ou clique [+ Adicionar PDF] para adicionar")
        lbl_hint.setStyleSheet(f"color: {DraculaTheme.COMMENT}; font-size: 13px;")
        layout.addWidget(lbl_hint)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        self._btn_add = QPushButton("+ Adicionar PDF")
        self._btn_add.setObjectName("secondaryBtn")
        self._btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_add.clicked.connect(self._add_pdfs)
        btn_row.addWidget(self._btn_add)

        self._btn_remove = QPushButton("Remover selecionado")
        self._btn_remove.setObjectName("dangerBtn")
        self._btn_remove.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_remove.clicked.connect(self._remove_selected)
        btn_row.addWidget(self._btn_remove)

        btn_row.addStretch()
        layout.addLayout(btn_row)

        self._list = DragDropPDFList()
        self._list.setMinimumHeight(160)
        self._list.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self._list)

        lbl_out = QLabel("Arquivo de saída")
        lbl_out.setStyleSheet(f"color: {DraculaTheme.COMMENT}; font-weight: bold;")
        layout.addWidget(lbl_out)

        self._btn_out = FilePathButton("Selecionar arquivo de saída (.pdf)  ", mode="pdf")
        layout.addWidget(self._btn_out)

        self._progress = QProgressBar()
        self._progress.setRange(0, 100)
        self._progress.setValue(0)
        layout.addWidget(self._progress)

        self._lbl_status = QLabel("Pronto.")
        self._lbl_status.setStyleSheet(f"color: {DraculaTheme.COMMENT};")
        layout.addWidget(self._lbl_status)

        self._btn_run = QPushButton("MESCLAR")
        self._btn_run.setObjectName("actionBtn")
        self._btn_run.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_run.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._btn_run.clicked.connect(self._run)
        layout.addWidget(self._btn_run)

        self._toast = Toast(self)

    def refresh_state(self, pdf_path: Path | None, output_dir: Path | None) -> None:
        pass

    def _add_pdfs(self) -> None:
        paths, _ = QFileDialog.getOpenFileNames(self, "Selecionar PDFs", "", "PDF (*.pdf)")
        for raw in paths:
            self._list._add_pdf(Path(raw))

    def _remove_selected(self) -> None:
        for item in self._list.selectedItems():
            self._list.takeItem(self._list.row(item))

    def _run(self) -> None:
        if self._list.count() == 0:
            self._toast.show_message("Adicione ao menos um PDF à lista.")
            return

        output_path = self._btn_out.current_path
        if not output_path:
            self._toast.show_message("Selecione o arquivo de saída.")
            return

        if self._worker and self._worker.isRunning():
            return

        entries = self._list.get_merge_entries()
        self._btn_run.setEnabled(False)
        self._btn_run.setText("Mesclando...")
        self._progress.setValue(0)
        self._lbl_status.setText("")

        self._worker = MergeWorker(entries=entries, output_path=output_path)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_progress(self, current: int, total: int, name: str) -> None:
        if total > 0:
            self._progress.setValue(int(current / total * 100))
        self._lbl_status.setText(f"[{current}/{total}] {name}")

    def _on_finished(self, result) -> None:
        self._btn_run.setEnabled(True)
        self._btn_run.setText("MESCLAR")
        self._progress.setValue(100)
        self._lbl_status.setStyleSheet(f"color: {DraculaTheme.GREEN};")
        size_mb = result.output_path.stat().st_size / (1024 * 1024) if result.output_path.exists() else 0
        self._lbl_status.setText(
            f"Concluido: {result.total_pages} paginas, {size_mb:.2f} MB -> {result.output_path.name}"
        )
        self.pdf_changed.emit(result.output_path)

    def _on_error(self, msg: str) -> None:
        self._btn_run.setEnabled(True)
        self._btn_run.setText("MESCLAR")
        self._lbl_status.setStyleSheet(f"color: {DraculaTheme.RED};")
        self._lbl_status.setText(f"Erro: {msg}")


# "A uniao faz a forca." — Provérbio latino
