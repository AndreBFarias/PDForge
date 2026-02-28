import logging
from pathlib import Path

import fitz
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QAbstractItemView, QListWidget, QListWidgetItem

from core.pdf_merger import MergeEntry

logger = logging.getLogger("pdfforge.widgets.dragdrop")


class DragDropPDFList(QListWidget):
    items_reordered = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)

    def dragEnterEvent(self, event) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            for url in event.mimeData().urls():
                file_path = Path(url.toLocalFile())
                if file_path.suffix.lower() == ".pdf":
                    self._add_pdf(file_path)
        else:
            super().dropEvent(event)
            self.items_reordered.emit()

    def _add_pdf(self, path: Path) -> None:
        try:
            with fitz.open(str(path)) as doc:
                page_count = doc.page_count
        except Exception as exc:
            logger.warning("Nao foi possivel abrir PDF para contagem: %s — %s", path.name, exc)
            page_count = 0

        label = f"{path.name}  ({page_count} pág{'s' if page_count != 1 else ''})"
        item = QListWidgetItem(label)
        item.setData(Qt.ItemDataRole.UserRole, path)
        self.addItem(item)
        logger.debug("PDF adicionado: %s (%d pags)", path.name, page_count)

    def get_merge_entries(self) -> list[MergeEntry]:
        entries = []
        for i in range(self.count()):
            item = self.item(i)
            path = item.data(Qt.ItemDataRole.UserRole)
            if path:
                entries.append(MergeEntry(path=path))
        return entries


# "A ordem dos fatores altera o produto." — Álgebra
