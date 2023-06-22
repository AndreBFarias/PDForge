import logging
from pathlib import Path
from dataclasses import dataclass

import fitz  # pymupdf

from config.settings import OCR_TEXT_MIN_CHARS, OCR_IMAGE_SCALE
from utils.file_utils import validate_pdf_path, human_size

logger = logging.getLogger("pdfforge.reader")


@dataclass
class PageInfo:
    number: int          # 0-indexed
    width: float
    height: float
    text_length: int
    is_image_only: bool
    has_images: bool


@dataclass
class PDFInfo:
    path: Path
    page_count: int
    file_size: str
    pdf_version: str
    is_encrypted: bool
    pages: list[PageInfo]
    metadata: dict[str, str]


class PDFReader:
    """
    Abstração sobre fitz.Document para leitura e inspeção de PDFs.
    Mantém o documento aberto enquanto o objeto existir; fechar com close().
    """

    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)
        validate_pdf_path(self._path)
        self._doc: fitz.Document = fitz.open(str(self._path))
        logger.info("PDF aberto: %s (%d páginas)", self._path.name, len(self._doc))

    def close(self) -> None:
        if self._doc and not self._doc.is_closed:
            self._doc.close()
            logger.debug("PDF fechado: %s", self._path.name)

    def __enter__(self) -> "PDFReader":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    @property
    def doc(self) -> fitz.Document:
        return self._doc

    @property
    def page_count(self) -> int:
        return len(self._doc)

    def get_info(self) -> PDFInfo:
        pages = [self._inspect_page(i) for i in range(len(self._doc))]
        return PDFInfo(
            path=self._path,
            page_count=len(self._doc),
            file_size=human_size(self._path.stat().st_size),
            pdf_version=self._doc.metadata.get("format", "PDF"),
            is_encrypted=self._doc.is_encrypted,
            pages=pages,
            metadata={k: v for k, v in self._doc.metadata.items() if v},
        )

    def _inspect_page(self, page_num: int) -> PageInfo:
        page = self._doc[page_num]
        text = page.get_text()
        images = page.get_images()
        return PageInfo(
            number=page_num,
            width=page.rect.width,
            height=page.rect.height,
            text_length=len(text.strip()),
            is_image_only=len(text.strip()) < OCR_TEXT_MIN_CHARS,
            has_images=len(images) > 0,
        )

    def get_page_text(self, page_num: int) -> str:
        """Retorna texto extraído de uma página (0-indexed)."""
        return self._doc[page_num].get_text()

    def get_page_text_dict(self, page_num: int) -> dict:
        """
        Retorna estrutura completa de spans com atributos tipográficos.
        Formato: {"blocks": [{"lines": [{"spans": [{"text", "font", "size", ...}]}]}]}
        """
        return self._doc[page_num].get_text("dict")

    def get_page_image(self, page_num: int, scale: float = OCR_IMAGE_SCALE) -> bytes:
        """
        Rasteriza a página para PNG em memória.
        Scale=2.0 gera ~150 DPI — adequado para OCR.
        """
        page = self._doc[page_num]
        mat = fitz.Matrix(scale, scale)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        return pix.tobytes("png")

    def search_text(self, query: str, case_sensitive: bool = False) -> dict[int, list[fitz.Rect]]:
        """
        Busca texto em todas as páginas.
        Retorna {page_num: [lista de rects com matches]}.
        """
        flags = fitz.TEXT_PRESERVE_WHITESPACE
        if not case_sensitive:
            flags |= fitz.TEXT_INHIBIT_SPACES
        results: dict[int, list[fitz.Rect]] = {}
        for i, page in enumerate(self._doc):
            hits = page.search_for(query, quads=False)
            if hits:
                results[i] = hits
                logger.debug("Página %d: %d ocorrências de '%s'", i, len(hits), query)
        logger.info("Busca por '%s': %d páginas com matches", query, len(results))
        return results

    def get_image_only_pages(self) -> list[int]:
        """Retorna índices de páginas que são imagens (sem texto extraível)."""
        return [i for i in range(len(self._doc)) if self._inspect_page(i).is_image_only]
