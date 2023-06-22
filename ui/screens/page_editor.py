import logging
from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ui.components import FilePathButton, SectionHeader, Toast
from ui.styles import DraculaTheme
from ui.workers import DocxWorker, ReplaceWorker
from utils.file_utils import ensure_output_path

logger = logging.getLogger("pdfforge.screens.editor")


class PageEditor(QWidget):
    """Tela de busca e substituição de texto em PDFs com suporte a múltiplos pares."""

    pdf_changed = pyqtSignal(Path)

    def __init__(self, use_gpu: bool = True, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._use_gpu = use_gpu
        self._worker: ReplaceWorker | None = None
        self._docx_worker: DocxWorker | None = None
        self._output_dir: Path | None = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 20)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        layout.addWidget(SectionHeader("Editor de", "Texto"))

        # Seleção de arquivo
        lbl_pdf = QLabel("Arquivo PDF")
        lbl_pdf.setStyleSheet(f"color: {DraculaTheme.COMMENT}; font-weight: bold;")
        layout.addWidget(lbl_pdf)
        self._btn_pdf = FilePathButton("Selecionar PDF  ", mode="pdf")
        self._btn_pdf.path_selected.connect(self._on_pdf_selected)
        layout.addWidget(self._btn_pdf)

        # Pasta de saída
        lbl_out = QLabel("Pasta de saída")
        lbl_out.setStyleSheet(f"color: {DraculaTheme.COMMENT}; font-weight: bold;")
        layout.addWidget(lbl_out)
        self._btn_out = FilePathButton("Selecionar Pasta de Saída  ", mode="dir")
        layout.addWidget(self._btn_out)

        layout.addSpacing(6)

        # Tabela de pares buscar/substituir
        lbl_pairs = QLabel("Pares de substituição")
        lbl_pairs.setStyleSheet(f"color: {DraculaTheme.COMMENT}; font-weight: bold;")
        layout.addWidget(lbl_pairs)

        self._pairs_table = QTableWidget(1, 2)
        self._pairs_table.setHorizontalHeaderLabels(["Buscar", "Substituir por"])
        self._pairs_table.horizontalHeader().setStretchLastSection(True)
        self._pairs_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self._pairs_table.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked
            | QAbstractItemView.EditTrigger.AnyKeyPressed
            | QAbstractItemView.EditTrigger.SelectedClicked
        )
        self._pairs_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._pairs_table.verticalHeader().setVisible(False)
        self._pairs_table.setMinimumHeight(120)
        layout.addWidget(self._pairs_table)

        # Botões gerenciar tabela
        table_btn_row = QHBoxLayout()
        table_btn_row.setSpacing(8)

        self._btn_add_pair = QPushButton("+ Par")
        self._btn_add_pair.setObjectName("secondaryBtn")
        self._btn_add_pair.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_add_pair.clicked.connect(self._add_pair_row)
        table_btn_row.addWidget(self._btn_add_pair)

        self._btn_remove_pair = QPushButton("- Remover")
        self._btn_remove_pair.setObjectName("dangerBtn")
        self._btn_remove_pair.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_remove_pair.clicked.connect(self._remove_pair_row)
        table_btn_row.addWidget(self._btn_remove_pair)

        table_btn_row.addStretch()
        layout.addLayout(table_btn_row)

        # Opção case-sensitive
        self._chk_case = QCheckBox("Diferenciar maiúsculas/minúsculas")
        layout.addWidget(self._chk_case)

        layout.addStretch()

        # Botões de ação principais
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self._btn_run = QPushButton("SUBSTITUIR")
        self._btn_run.setObjectName("actionBtn")
        self._btn_run.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_run.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._btn_run.clicked.connect(self._run)
        btn_row.addWidget(self._btn_run, stretch=2)

        self._btn_export = QPushButton("EXPORTAR DOCX")
        self._btn_export.setObjectName("secondaryBtn")
        self._btn_export.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_export.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._btn_export.clicked.connect(self._export_docx)
        btn_row.addWidget(self._btn_export, stretch=1)

        self._btn_clear = QPushButton("Limpar")
        self._btn_clear.setObjectName("secondaryBtn")
        self._btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_clear.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._btn_clear.clicked.connect(self._clear)
        btn_row.addWidget(self._btn_clear, stretch=1)

        layout.addLayout(btn_row)

        # Label de resultado
        self._lbl_result = QLabel("")
        self._lbl_result.setWordWrap(True)
        self._lbl_result.setStyleSheet(
            f"color: {DraculaTheme.GREEN}; font-weight: bold; margin-top: 8px;"
        )
        layout.addWidget(self._lbl_result)

        self._toast = Toast(self)

    def refresh_state(self, pdf_path: Path | None, output_dir: Path | None) -> None:
        if pdf_path:
            self._btn_pdf.set_path(pdf_path)
        if output_dir:
            self._output_dir = output_dir
            self._btn_out.set_path(output_dir)

    def _on_pdf_selected(self, path: Path) -> None:
        self.pdf_changed.emit(path)
        if not self._btn_out.current_path:
            default_out = path.parent / "data_output"
            self._btn_out.set_path(default_out)

    def _add_pair_row(self) -> None:
        self._pairs_table.insertRow(self._pairs_table.rowCount())

    def _remove_pair_row(self) -> None:
        rows = sorted(
            {idx.row() for idx in self._pairs_table.selectedIndexes()}, reverse=True
        )
        for row in rows:
            self._pairs_table.removeRow(row)
        if self._pairs_table.rowCount() == 0:
            self._pairs_table.insertRow(0)

    def _get_pairs(self) -> list[tuple[str, str]]:
        pairs = []
        for row in range(self._pairs_table.rowCount()):
            s_item = self._pairs_table.item(row, 0)
            r_item = self._pairs_table.item(row, 1)
            search = s_item.text().strip() if s_item else ""
            replace = r_item.text() if r_item else ""
            if search:
                pairs.append((search, replace))
        return pairs

    def _run(self) -> None:
        pdf = self._btn_pdf.current_path
        out_dir = self._btn_out.current_path

        if not pdf:
            self._toast.show_message("Selecione um arquivo PDF.")
            return
        if not out_dir:
            self._toast.show_message("Selecione a pasta de saída.")
            return

        pairs = self._get_pairs()
        if not pairs:
            self._toast.show_message("Adicione pelo menos um par buscar/substituir.")
            return

        if self._worker and self._worker.isRunning():
            return

        output_path = ensure_output_path(pdf, out_dir, suffix="_editado")
        self._btn_run.setEnabled(False)
        self._btn_run.setText("Processando...")
        self._lbl_result.setText("")

        self._worker = ReplaceWorker(
            pdf_path=pdf,
            pairs=pairs,
            output_path=output_path,
            case_sensitive=self._chk_case.isChecked(),
        )
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _export_docx(self) -> None:
        pdf = self._btn_pdf.current_path
        out_dir = self._btn_out.current_path or self._output_dir

        if not pdf or not out_dir:
            self._toast.show_message("Selecione PDF e pasta de saída.")
            return
        if self._docx_worker and self._docx_worker.isRunning():
            return

        output_path = out_dir / (pdf.stem + ".docx")
        self._btn_export.setEnabled(False)
        self._btn_export.setText("Exportando...")
        self._lbl_result.setText("")

        self._docx_worker = DocxWorker(pdf, output_path)
        self._docx_worker.finished.connect(self._on_docx_done)
        self._docx_worker.error.connect(self._on_docx_error)
        self._docx_worker.start()

    def _on_finished(self, result) -> None:
        self._btn_run.setEnabled(True)
        self._btn_run.setText("SUBSTITUIR")
        pages = ", ".join(str(p + 1) for p in result.pages_affected)
        self._lbl_result.setStyleSheet(
            f"color: {DraculaTheme.GREEN}; font-weight: bold; margin-top: 8px;"
        )
        self._lbl_result.setText(
            f"{result.total_replacements} substituição(ões) em {len(result.pages_affected)} página(s)"
            + (f" [{pages}]" if pages else "")
            + f"\nSalvo em: {result.output_path.name}"
        )
        logger.info("Substituição concluída: %s", result)

    def _on_error(self, msg: str) -> None:
        self._btn_run.setEnabled(True)
        self._btn_run.setText("SUBSTITUIR")
        self._lbl_result.setStyleSheet(
            f"color: {DraculaTheme.RED}; font-weight: bold; margin-top: 8px;"
        )
        self._lbl_result.setText(f"Erro: {msg}")

    def _on_docx_done(self, output_path: Path) -> None:
        self._btn_export.setEnabled(True)
        self._btn_export.setText("EXPORTAR DOCX")
        self._lbl_result.setStyleSheet(
            f"color: {DraculaTheme.GREEN}; font-weight: bold; margin-top: 8px;"
        )
        self._lbl_result.setText(f"DOCX gerado: {output_path.name}")
        logger.info("Exportação DOCX concluída: %s", output_path)

    def _on_docx_error(self, msg: str) -> None:
        self._btn_export.setEnabled(True)
        self._btn_export.setText("EXPORTAR DOCX")
        self._lbl_result.setStyleSheet(
            f"color: {DraculaTheme.RED}; font-weight: bold; margin-top: 8px;"
        )
        self._lbl_result.setText(f"Erro DOCX: {msg}")

    def _clear(self) -> None:
        self._pairs_table.clearContents()
        self._pairs_table.setRowCount(1)
        self._lbl_result.setText("")


# "Não há vento favorável para quem não sabe para onde vai." — Sêneca
