import logging
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QButtonGroup,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ui.components import FilePathButton, SectionHeader, Toast
from ui.styles import DraculaTheme
from ui.workers import ClassifyWorker

logger = logging.getLogger("pdfforge.screens.classifier")


class PageClassifier(QWidget):
    def __init__(self, use_gpu: bool = True, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._use_gpu = use_gpu
        self._worker: ClassifyWorker | None = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 20)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        layout.addWidget(SectionHeader("Classificar", "Documentos"))

        radio_row = QHBoxLayout()
        self._radio_single = QRadioButton("Arquivo único")
        self._radio_single.setChecked(True)
        self._radio_batch = QRadioButton("Pasta (lote)")
        self._btn_group = QButtonGroup(self)
        self._btn_group.addButton(self._radio_single)
        self._btn_group.addButton(self._radio_batch)
        radio_row.addWidget(self._radio_single)
        radio_row.addWidget(self._radio_batch)
        radio_row.addStretch()
        layout.addLayout(radio_row)
        self._radio_single.toggled.connect(self._on_mode_changed)

        self._btn_path = FilePathButton("Selecionar PDF  ", mode="pdf")
        layout.addWidget(self._btn_path)

        self._btn_run = QPushButton("CLASSIFICAR")
        self._btn_run.setObjectName("actionBtn")
        self._btn_run.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_run.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._btn_run.clicked.connect(self._run)
        layout.addWidget(self._btn_run)

        lbl_res = QLabel("Resultados")
        lbl_res.setStyleSheet(f"color: {DraculaTheme.COMMENT}; font-weight: bold; margin-top: 6px;")
        layout.addWidget(lbl_res)

        self._table = QTableWidget(0, 4)
        self._table.setHorizontalHeaderLabels(["Arquivo", "Tipo", "Confiança", "Método"])
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.verticalHeader().setVisible(False)
        self._table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self._table)

        self._toast = Toast(self)

    def refresh_state(self, pdf_path: Path | None, output_dir: Path | None) -> None:
        if pdf_path and self._radio_single.isChecked():
            self._btn_path.set_path(pdf_path)

    def _on_mode_changed(self, single: bool) -> None:
        if single:
            self._btn_path._mode = "pdf"
            self._btn_path._default_label = "Selecionar PDF  "
            self._btn_path.setText("Selecionar PDF  ")
            self._btn_path._path = None
        else:
            self._btn_path._mode = "dir"
            self._btn_path._default_label = "Selecionar Pasta  "
            self._btn_path.setText("Selecionar Pasta  ")
            self._btn_path._path = None

    def _run(self) -> None:
        path = self._btn_path.current_path
        if not path:
            self._toast.show_message("Selecione um arquivo ou pasta.")
            return

        self._table.setRowCount(0)

        if self._radio_single.isChecked():
            self._classify_single(path)
        else:
            self._classify_batch(path)

    def _classify_single(self, pdf_path: Path) -> None:
        if self._worker and self._worker.isRunning():
            return

        self._btn_run.setEnabled(False)
        self._btn_run.setText("Classificando...")
        self._worker = ClassifyWorker(pdf_path=pdf_path)
        self._worker.finished.connect(lambda r: self._add_row(pdf_path.name, r))
        self._worker.finished.connect(lambda _: self._restore_btn())
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _classify_batch(self, folder: Path) -> None:
        import fitz
        from core.document_classifier import DocumentClassifier

        pdfs = list(folder.glob("*.pdf"))
        if not pdfs:
            self._toast.show_message("Nenhum PDF encontrado na pasta.")
            return

        self._btn_run.setEnabled(False)
        self._btn_run.setText("Classificando...")
        try:
            classifier = DocumentClassifier()
            for pdf_path in pdfs:
                doc = fitz.open(str(pdf_path))
                result = classifier.classify(doc)
                doc.close()
                self._add_row(pdf_path.name, result)
        except Exception as exc:
            logger.error("Erro no lote: %s", exc)
        finally:
            self._restore_btn()

    def _add_row(self, filename: str, result) -> None:
        row = self._table.rowCount()
        self._table.insertRow(row)

        conf = result.confidence
        if conf >= 0.7:
            color = QColor(DraculaTheme.GREEN)
        elif conf >= 0.4:
            color = QColor(DraculaTheme.YELLOW)
        else:
            color = QColor(DraculaTheme.RED)

        items = [
            QTableWidgetItem(filename),
            QTableWidgetItem(result.doc_type),
            QTableWidgetItem(f"{conf:.0%}"),
            QTableWidgetItem(result.method),
        ]
        for col, item in enumerate(items):
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setForeground(color)
            self._table.setItem(row, col, item)

        self._table.resizeColumnsToContents()

    def _restore_btn(self) -> None:
        self._btn_run.setEnabled(True)
        self._btn_run.setText("CLASSIFICAR")

    def _on_error(self, msg: str) -> None:
        self._restore_btn()
        self._toast.show_message(f"Erro: {msg}")


# "Classificar é o primeiro ato de compreender." — Carl Linnaeus
