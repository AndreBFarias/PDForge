import logging
from pathlib import Path

from PyQt6.QtCore import Qt, QByteArray
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ui.components import ExportDialog, FilePathButton, SectionHeader, Toast
from ui.styles import DraculaTheme
from ui.workers import ReorderWorker

logger = logging.getLogger("pdfforge.screens.organizer")


class _ThumbnailItem(QWidget):
    """Widget individual de thumbnail com número da página."""

    def __init__(
        self, page_num: int, png_bytes: bytes,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.page_num = page_num
        self.selected = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)

        self._img_label = QLabel()
        img = QImage()
        img.loadFromData(QByteArray(png_bytes))
        pix = QPixmap.fromImage(img).scaledToWidth(
            140, Qt.TransformationMode.SmoothTransformation,
        )
        self._img_label.setPixmap(pix)
        self._img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._img_label)

        self._num_label = QLabel(f"Pág. {page_num + 1}")
        self._num_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._num_label.setStyleSheet(
            f"color: {DraculaTheme.FOREGROUND}; font-size: 11px;",
        )
        layout.addWidget(self._num_label)

        self.setFixedSize(160, 200)
        self._update_style()

    def mousePressEvent(self, event) -> None:
        self.selected = not self.selected
        self._update_style()
        super().mousePressEvent(event)

    def _update_style(self) -> None:
        border = DraculaTheme.PURPLE if self.selected else "transparent"
        self.setStyleSheet(
            f"background-color: {DraculaTheme.CURRENT_LINE};"
            f" border: 2px solid {border}; border-radius: 6px;",
        )


class PageOrganizer(QWidget):
    def __init__(
        self, use_gpu: bool = True, parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._use_gpu = use_gpu
        self._worker: ReorderWorker | None = None
        self._thumbnails: list[_ThumbnailItem] = []
        self._page_order: list[int] = []
        self._current_pdf: Path | None = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 20)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        layout.addWidget(SectionHeader("Organizar", "Páginas"))

        lbl = QLabel("Arquivo PDF")
        lbl.setStyleSheet(
            f"color: {DraculaTheme.COMMENT}; font-weight: bold;",
        )
        layout.addWidget(lbl)
        self._btn_in = FilePathButton(
            "Selecionar PDF  ", mode="pdf",
        )
        self._btn_in.path_selected.connect(self._load_thumbnails)
        layout.addWidget(self._btn_in)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setMinimumHeight(250)
        self._grid_widget = QWidget()
        self._grid_layout = QGridLayout(self._grid_widget)
        self._grid_layout.setSpacing(8)
        self._scroll.setWidget(self._grid_widget)
        layout.addWidget(self._scroll)

        btn_row = QHBoxLayout()
        self._btn_move_left = QPushButton("Mover Esquerda")
        self._btn_move_left.setObjectName("secondaryBtn")
        self._btn_move_left.setCursor(
            Qt.CursorShape.PointingHandCursor,
        )
        self._btn_move_left.clicked.connect(self._move_left)
        btn_row.addWidget(self._btn_move_left)

        self._btn_move_right = QPushButton("Mover Direita")
        self._btn_move_right.setObjectName("secondaryBtn")
        self._btn_move_right.setCursor(
            Qt.CursorShape.PointingHandCursor,
        )
        self._btn_move_right.clicked.connect(self._move_right)
        btn_row.addWidget(self._btn_move_right)

        self._btn_dup = QPushButton("Duplicar")
        self._btn_dup.setObjectName("secondaryBtn")
        self._btn_dup.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_dup.clicked.connect(self._duplicate_selected)
        btn_row.addWidget(self._btn_dup)

        self._btn_del = QPushButton("Deletar")
        self._btn_del.setObjectName("dangerBtn")
        self._btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_del.clicked.connect(self._delete_selected)
        btn_row.addWidget(self._btn_del)
        layout.addLayout(btn_row)

        lbl_out = QLabel("Arquivo de saída")
        lbl_out.setStyleSheet(
            f"color: {DraculaTheme.COMMENT}; font-weight: bold;",
        )
        layout.addWidget(lbl_out)
        self._btn_out = FilePathButton(
            "Selecionar arquivo de saída (.pdf)  ", mode="save",
        )
        layout.addWidget(self._btn_out)

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

        self._btn_save = QPushButton("SALVAR")
        self._btn_save.setObjectName("actionBtn")
        self._btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_save.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed,
        )
        self._btn_save.clicked.connect(self._save)
        layout.addWidget(self._btn_save)

        self._toast = Toast(self)

    def refresh_state(
        self, pdf_path: Path | None, output_dir: Path | None,
    ) -> None:
        if pdf_path:
            self._btn_in.set_path(pdf_path)

    def _load_thumbnails(self, path: Path) -> None:
        self._current_pdf = path
        self._thumbnails.clear()
        self._page_order.clear()

        while self._grid_layout.count():
            item = self._grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        try:
            from core.pdf_page_organizer import PDFPageOrganizer
            organizer = PDFPageOrganizer()
            thumbs = organizer.get_page_thumbnails(path)

            cols = 4
            for i, png_bytes in enumerate(thumbs):
                item = _ThumbnailItem(i, png_bytes)
                self._thumbnails.append(item)
                self._page_order.append(i)
                row = i // cols
                col = i % cols
                self._grid_layout.addWidget(item, row, col)

            self._lbl_status.setText(
                f"{len(thumbs)} páginas carregadas.",
            )
        except Exception as exc:
            logger.error("Erro ao carregar thumbnails: %s", exc)
            self._lbl_status.setText(f"Erro: {exc}")

    def _get_selected_indices(self) -> list[int]:
        return [
            i for i, t in enumerate(self._thumbnails) if t.selected
        ]

    def _refresh_grid(self) -> None:
        while self._grid_layout.count():
            item = self._grid_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        cols = 4
        for i, thumb in enumerate(self._thumbnails):
            row = i // cols
            col = i % cols
            self._grid_layout.addWidget(thumb, row, col)

    def _move_left(self) -> None:
        selected = self._get_selected_indices()
        if not selected or selected[0] == 0:
            return
        for idx in selected:
            if idx > 0:
                self._thumbnails[idx], self._thumbnails[idx - 1] = (
                    self._thumbnails[idx - 1], self._thumbnails[idx],
                )
                self._page_order[idx], self._page_order[idx - 1] = (
                    self._page_order[idx - 1], self._page_order[idx],
                )
        self._refresh_grid()

    def _move_right(self) -> None:
        selected = self._get_selected_indices()
        if not selected or selected[-1] >= len(self._thumbnails) - 1:
            return
        for idx in reversed(selected):
            if idx < len(self._thumbnails) - 1:
                self._thumbnails[idx], self._thumbnails[idx + 1] = (
                    self._thumbnails[idx + 1], self._thumbnails[idx],
                )
                self._page_order[idx], self._page_order[idx + 1] = (
                    self._page_order[idx + 1], self._page_order[idx],
                )
        self._refresh_grid()

    def _duplicate_selected(self) -> None:
        selected = self._get_selected_indices()
        if not selected or not self._current_pdf:
            self._toast.show_message("Selecione páginas.")
            return

        out = self._btn_out.current_path
        if not out:
            self._toast.show_message("Selecione o arquivo de saída.")
            return

        self._btn_save.setEnabled(False)
        self._progress.setVisible(True)
        idx = self._page_order[selected[0]]
        self._worker = ReorderWorker(
            mode="duplicate",
            input_path=self._current_pdf,
            output_path=out,
            page_index=idx,
        )
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _delete_selected(self) -> None:
        selected = self._get_selected_indices()
        if not selected or not self._current_pdf:
            self._toast.show_message("Selecione páginas.")
            return

        out = self._btn_out.current_path
        if not out:
            self._toast.show_message("Selecione o arquivo de saída.")
            return

        pages = [self._page_order[i] for i in selected]
        self._btn_save.setEnabled(False)
        self._progress.setVisible(True)
        self._worker = ReorderWorker(
            mode="delete",
            input_path=self._current_pdf,
            output_path=out,
            pages_to_delete=pages,
        )
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _save(self) -> None:
        if not self._current_pdf:
            self._toast.show_message("Selecione um PDF.")
            return
        out = self._btn_out.current_path
        if not out:
            self._toast.show_message("Selecione o arquivo de saída.")
            return
        if self._worker and self._worker.isRunning():
            return

        self._btn_save.setEnabled(False)
        self._btn_save.setText("Salvando...")
        self._progress.setVisible(True)
        self._lbl_status.setText("Processando...")

        self._worker = ReorderWorker(
            mode="reorder",
            input_path=self._current_pdf,
            output_path=out,
            new_order=list(self._page_order),
        )
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_finished(self, result) -> None:
        self._btn_save.setEnabled(True)
        self._btn_save.setText("SALVAR")
        self._progress.setVisible(False)

        if result.success:
            self._lbl_status.setStyleSheet(
                f"color: {DraculaTheme.GREEN};",
            )
            self._lbl_status.setText(
                f"Concluído — {result.total_pages} páginas.",
            )
            out = self._btn_out.current_path
            if out and out.exists():
                ExportDialog(out, self).exec()
        else:
            self._lbl_status.setStyleSheet(
                f"color: {DraculaTheme.RED};",
            )
            self._lbl_status.setText(f"Erro: {result.error}")

    def _on_error(self, msg: str) -> None:
        self._btn_save.setEnabled(True)
        self._btn_save.setText("SALVAR")
        self._progress.setVisible(False)
        self._lbl_status.setStyleSheet(f"color: {DraculaTheme.RED};")
        self._lbl_status.setText(f"Erro: {msg}")


# "A ordem é o primeiro passo para a maestria." — Jocko Willink
