import logging
from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ui.components import FilePathButton, SectionHeader, Toast
from ui.styles import DraculaTheme
from ui.workers import BatchWorker

logger = logging.getLogger("pdfforge.screens.batch")

_OPERATIONS = {
    "Extrair Metadados": "metadata",
    "Aplicar OCR": "ocr",
    "Rotacionar 90°": "rotate_90",
    "Rotacionar 180°": "rotate_180",
    "Rotacionar 270°": "rotate_270",
}


class PageBatch(QWidget):
    """Tela de processamento em lote de múltiplos PDFs."""

    pdf_changed = pyqtSignal(Path)

    def __init__(self, use_gpu: bool = True, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._use_gpu = use_gpu
        self._worker: BatchWorker | None = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 20)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        layout.addWidget(SectionHeader("Processamento", "em Lote"))

        lbl_in = QLabel("Pasta de entrada (PDFs)")
        lbl_in.setStyleSheet(f"color: {DraculaTheme.COMMENT}; font-weight: bold;")
        layout.addWidget(lbl_in)
        self._btn_in = FilePathButton("Selecionar Pasta de Entrada  ", mode="dir")
        layout.addWidget(self._btn_in)

        lbl_out = QLabel("Pasta de saída")
        lbl_out.setStyleSheet(f"color: {DraculaTheme.COMMENT}; font-weight: bold;")
        layout.addWidget(lbl_out)
        self._btn_out = FilePathButton("Selecionar Pasta de Saída  ", mode="dir")
        layout.addWidget(self._btn_out)

        lbl_op = QLabel("Operação")
        lbl_op.setStyleSheet(f"color: {DraculaTheme.COMMENT}; font-weight: bold;")
        layout.addWidget(lbl_op)
        self._cmb_op = QComboBox()
        for name in _OPERATIONS:
            self._cmb_op.addItem(name)
        layout.addWidget(self._cmb_op)

        layout.addSpacing(4)

        # Progresso
        self._progress = QProgressBar()
        self._progress.setRange(0, 100)
        self._progress.setValue(0)
        layout.addWidget(self._progress)

        self._lbl_status = QLabel("Pronto.")
        self._lbl_status.setStyleSheet(f"color: {DraculaTheme.COMMENT};")
        layout.addWidget(self._lbl_status)

        # Botão executar
        btn_row = QHBoxLayout()
        self._btn_run = QPushButton("EXECUTAR LOTE")
        self._btn_run.setObjectName("actionBtn")
        self._btn_run.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_run.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._btn_run.clicked.connect(self._run)
        btn_row.addWidget(self._btn_run)
        layout.addLayout(btn_row)

        # Tabela de resultados
        lbl_res = QLabel("Resultados")
        lbl_res.setStyleSheet(f"color: {DraculaTheme.COMMENT}; font-weight: bold; margin-top: 8px;")
        layout.addWidget(lbl_res)

        self._table = QTableWidget(0, 4)
        self._table.setHorizontalHeaderLabels(["Arquivo", "Status", "Duração (s)", "Mensagem"])
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.verticalHeader().setVisible(False)
        self._table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self._table)

        self._toast = Toast(self)

    def refresh_state(self, pdf_path: Path | None, output_dir: Path | None) -> None:
        if output_dir:
            self._btn_out.set_path(output_dir)

    def _run(self) -> None:
        input_dir = self._btn_in.current_path
        output_dir = self._btn_out.current_path

        if not input_dir:
            self._toast.show_message("Selecione a pasta de entrada.")
            return
        if not output_dir:
            self._toast.show_message("Selecione a pasta de saída.")
            return
        if self._worker and self._worker.isRunning():
            return

        op_name = _OPERATIONS[self._cmb_op.currentText()]

        self._btn_run.setEnabled(False)
        self._btn_run.setText("Processando...")
        self._progress.setValue(0)
        self._table.setRowCount(0)

        self._worker = BatchWorker(
            input_dir=input_dir,
            output_dir=output_dir,
            operation_name=op_name,
            use_gpu=self._use_gpu,
        )
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_progress(self, current: int, total: int, filename: str) -> None:
        if total > 0:
            self._progress.setValue(int(current / total * 100))
        self._lbl_status.setText(f"[{current}/{total}] {filename}")

    def _on_finished(self, report) -> None:
        self._btn_run.setEnabled(True)
        self._btn_run.setText("EXECUTAR LOTE")
        self._progress.setValue(100)
        self._lbl_status.setText(report.summary())

        self._table.setRowCount(0)
        for file_result in report.results:
            row = self._table.rowCount()
            self._table.insertRow(row)

            status_text = "OK" if file_result.success else "ERRO"
            status_color = DraculaTheme.GREEN if file_result.success else DraculaTheme.RED

            items = [
                QTableWidgetItem(file_result.path.name),
                QTableWidgetItem(status_text),
                QTableWidgetItem(f"{file_result.duration_s:.2f}"),
                QTableWidgetItem(file_result.message),
            ]
            for col, item in enumerate(items):
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if col == 1:
                    item.setForeground(
                        __import__("PyQt6.QtGui", fromlist=["QColor"]).QColor(status_color)
                    )
                self._table.setItem(row, col, item)

        self._table.resizeColumnsToContents()

    def _on_error(self, msg: str) -> None:
        self._btn_run.setEnabled(True)
        self._btn_run.setText("EXECUTAR LOTE")
        self._lbl_status.setStyleSheet(f"color: {DraculaTheme.RED};")
        self._lbl_status.setText(f"Erro: {msg}")


# "A jornada de mil milhas começa com um único passo." — Lao Tsé
