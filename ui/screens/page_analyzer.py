import logging
from pathlib import Path

import fitz
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.font_detector import FontDetector
from core.metadata import PDFMetadata
from ui.components import FilePathButton, SectionHeader, Toast
from utils.file_utils import ensure_output_path
from ui.styles import DraculaTheme

logger = logging.getLogger("pdfforge.screens.analyzer")


class PageAnalyzer(QWidget):
    """Tela de análise de fontes e metadados de PDFs."""

    pdf_changed = pyqtSignal(Path)

    def __init__(self, use_gpu: bool = True, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._output_dir: Path | None = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 20)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        layout.addWidget(SectionHeader("Analisador de", "PDF"))

        lbl_pdf = QLabel("Arquivo PDF")
        lbl_pdf.setStyleSheet(f"color: {DraculaTheme.COMMENT}; font-weight: bold;")
        layout.addWidget(lbl_pdf)

        self._btn_pdf = FilePathButton("Selecionar PDF  ", mode="pdf")
        self._btn_pdf.path_selected.connect(self._on_pdf_selected)
        layout.addWidget(self._btn_pdf)

        # Botão analisar
        btn_row = QHBoxLayout()
        self._btn_analyze = QPushButton("ANALISAR")
        self._btn_analyze.setObjectName("actionBtn")
        self._btn_analyze.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_analyze.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._btn_analyze.clicked.connect(self._run_analysis)
        btn_row.addWidget(self._btn_analyze)
        layout.addLayout(btn_row)

        lbl_out = QLabel("Pasta de saída")
        lbl_out.setStyleSheet(f"color: {DraculaTheme.COMMENT}; font-weight: bold;")
        layout.addWidget(lbl_out)

        self._btn_out = FilePathButton("Selecionar Pasta de Saída  ", mode="dir")
        layout.addWidget(self._btn_out)

        btn_row_meta = QHBoxLayout()
        self._btn_clear_meta = QPushButton("LIMPAR METADADOS")
        self._btn_clear_meta.setObjectName("dangerBtn")
        self._btn_clear_meta.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_clear_meta.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._btn_clear_meta.clicked.connect(self._clear_metadata)
        btn_row_meta.addWidget(self._btn_clear_meta)
        layout.addLayout(btn_row_meta)

        # TabWidget — Fontes | Metadados
        self._tabs = QTabWidget()
        self._tabs.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self._tabs)

        self._setup_fonts_tab()
        self._setup_metadata_tab()

        self._toast = Toast(self)

    def _setup_fonts_tab(self) -> None:
        container = QWidget()
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(0, 8, 0, 0)

        self._font_table = QTableWidget(0, 4)
        self._font_table.setHorizontalHeaderLabels(
            ["Fonte", "Ocorrências", "Páginas", "Tamanho médio (pt)"]
        )
        self._font_table.horizontalHeader().setStretchLastSection(True)
        self._font_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._font_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._font_table.verticalHeader().setVisible(False)
        vbox.addWidget(self._font_table)

        self._tabs.addTab(container, "Fontes")

    def _setup_metadata_tab(self) -> None:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")

        container = QWidget()
        container.setStyleSheet(f"background-color: {DraculaTheme.BACKGROUND};")
        self._meta_form = QFormLayout(container)
        self._meta_form.setContentsMargins(12, 12, 12, 12)
        self._meta_form.setSpacing(10)
        self._meta_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        scroll.setWidget(container)
        self._tabs.addTab(scroll, "Metadados")

    def refresh_state(self, pdf_path: Path | None, output_dir: Path | None) -> None:
        if pdf_path:
            self._btn_pdf.set_path(pdf_path)
        if output_dir:
            self._output_dir = output_dir
            self._btn_out.set_path(output_dir)

    def _on_pdf_selected(self, path: Path) -> None:
        self.pdf_changed.emit(path)

    def _run_analysis(self) -> None:
        pdf = self._btn_pdf.current_path
        if not pdf:
            self._toast.show_message("Selecione um arquivo PDF.")
            return

        self._btn_analyze.setEnabled(False)
        self._btn_analyze.setText("Analisando...")

        try:
            doc = fitz.open(str(pdf))
            self._load_fonts(doc)
            self._load_metadata(doc)
            doc.close()
        except Exception as exc:
            logger.error("Análise falhou: %s", exc, exc_info=True)
            self._toast.show_message(f"Erro: {exc}")
        finally:
            self._btn_analyze.setEnabled(True)
            self._btn_analyze.setText("ANALISAR")

    def _load_fonts(self, doc: fitz.Document) -> None:
        detector = FontDetector()
        usages = detector.extract(doc)

        self._font_table.setRowCount(0)
        for usage in usages:
            row = self._font_table.rowCount()
            self._font_table.insertRow(row)

            pages_str = ", ".join(str(p + 1) for p in usage.pages[:8])
            if len(usage.pages) > 8:
                pages_str += f" (+{len(usage.pages) - 8})"

            items = [
                QTableWidgetItem(usage.info.name),
                QTableWidgetItem(str(usage.occurrences)),
                QTableWidgetItem(pages_str),
                QTableWidgetItem(f"{usage.avg_size:.1f}"),
            ]
            for col, item in enumerate(items):
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self._font_table.setItem(row, col, item)

        self._font_table.resizeColumnsToContents()

    def _load_metadata(self, doc: fitz.Document) -> None:
        while self._meta_form.rowCount():
            self._meta_form.removeRow(0)

        meta = PDFMetadata().read(doc)
        display = meta.as_display_dict()

        if not display:
            no_meta = QLabel("Nenhum metadado encontrado.")
            no_meta.setStyleSheet(f"color: {DraculaTheme.COMMENT};")
            self._meta_form.addRow(no_meta)
            return

        label_map = {
            "title": "Título",
            "author": "Autor",
            "subject": "Assunto",
            "keywords": "Palavras-chave",
            "creator": "Criador",
            "producer": "Produtor",
            "creation_date": "Criado em",
            "mod_date": "Modificado em",
        }

        for key, value in display.items():
            lbl_key = QLabel(label_map.get(key, key) + ":")
            lbl_key.setStyleSheet(
                f"color: {DraculaTheme.PURPLE}; font-weight: bold;"
            )
            lbl_val = QLabel(str(value))
            lbl_val.setWordWrap(True)
            lbl_val.setStyleSheet(f"color: {DraculaTheme.FOREGROUND};")
            self._meta_form.addRow(lbl_key, lbl_val)

    def _clear_metadata(self) -> None:
        pdf = self._btn_pdf.current_path
        out_dir = self._btn_out.current_path or self._output_dir
        if not pdf:
            self._toast.show_message("Selecione um arquivo PDF.")
            return
        if not out_dir:
            self._toast.show_message("Selecione a pasta de saída.")
            return

        output_path = ensure_output_path(pdf, out_dir, suffix="_sem_meta")
        self._btn_clear_meta.setEnabled(False)
        self._btn_clear_meta.setText("Limpando...")
        try:
            doc = fitz.open(str(pdf))
            PDFMetadata().clear(doc, output_path)
            doc.close()
            self._toast.show_message(f"Metadados removidos → {output_path.name}")
        except Exception as exc:
            logger.error("Falha ao limpar metadados: %s", exc, exc_info=True)
            self._toast.show_message(f"Erro: {exc}")
        finally:
            self._btn_clear_meta.setEnabled(True)
            self._btn_clear_meta.setText("LIMPAR METADADOS")


# "O homem que move montanhas começa carregando pequenas pedras." — Confúcio
