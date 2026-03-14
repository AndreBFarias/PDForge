import logging
from dataclasses import dataclass
from pathlib import Path

import fitz

logger = logging.getLogger("pdfforge.page_organizer")


@dataclass
class ReorderResult:
    success: bool = True
    output_path: Path | None = None
    total_pages: int = 0
    error: str = ""


class PDFPageOrganizer:
    """Reorganizacao, duplicacao e exclusao de paginas em PDFs."""

    def reorder(
        self,
        input_path: Path,
        output_path: Path,
        new_order: list[int],
    ) -> ReorderResult:
        try:
            doc = fitz.open(str(input_path))
            total = len(doc)
            for idx in new_order:
                if idx < 0 or idx >= total:
                    doc.close()
                    return ReorderResult(
                        success=False,
                        error=(
                            f"Indice de pagina invalido: {idx}"
                        ),
                    )
            doc.select(new_order)
            output_path.parent.mkdir(
                parents=True, exist_ok=True,
            )
            doc.save(
                str(output_path), garbage=4, deflate=True,
            )
            pages = len(doc)
            doc.close()
            logger.info(
                "Paginas reordenadas: %d paginas -> %s",
                pages, output_path.name,
            )
            return ReorderResult(
                output_path=output_path,
                total_pages=pages,
            )
        except Exception as exc:
            logger.error("Erro ao reordenar: %s", exc)
            return ReorderResult(
                success=False, error=str(exc),
            )

    def delete_pages(
        self,
        input_path: Path,
        output_path: Path,
        pages_to_delete: list[int],
    ) -> ReorderResult:
        try:
            doc = fitz.open(str(input_path))
            total = len(doc)
            keep = [
                i for i in range(total)
                if i not in pages_to_delete
            ]
            if not keep:
                doc.close()
                return ReorderResult(
                    success=False,
                    error=(
                        "Nao e possivel deletar"
                        " todas as paginas"
                    ),
                )
            doc.select(keep)
            output_path.parent.mkdir(
                parents=True, exist_ok=True,
            )
            doc.save(
                str(output_path), garbage=4, deflate=True,
            )
            pages = len(doc)
            doc.close()
            logger.info(
                "Paginas deletadas: %d removidas,"
                " %d restantes",
                len(pages_to_delete), pages,
            )
            return ReorderResult(
                output_path=output_path,
                total_pages=pages,
            )
        except Exception as exc:
            logger.error(
                "Erro ao deletar paginas: %s", exc,
            )
            return ReorderResult(
                success=False, error=str(exc),
            )

    def duplicate_page(
        self,
        input_path: Path,
        output_path: Path,
        page_index: int,
    ) -> ReorderResult:
        try:
            doc = fitz.open(str(input_path))
            if page_index < 0 or page_index >= len(doc):
                doc.close()
                return ReorderResult(
                    success=False,
                    error=(
                        "Indice de pagina"
                        f" invalido: {page_index}"
                    ),
                )
            order = list(range(len(doc)))
            order.insert(page_index + 1, page_index)
            doc.select(order)
            output_path.parent.mkdir(
                parents=True, exist_ok=True,
            )
            doc.save(
                str(output_path), garbage=4, deflate=True,
            )
            pages = len(doc)
            doc.close()
            logger.info(
                "Pagina %d duplicada: %d paginas total",
                page_index, pages,
            )
            return ReorderResult(
                output_path=output_path,
                total_pages=pages,
            )
        except Exception as exc:
            logger.error(
                "Erro ao duplicar pagina: %s", exc,
            )
            return ReorderResult(
                success=False, error=str(exc),
            )

    def get_page_thumbnails(
        self,
        input_path: Path,
        scale: float = 0.3,
    ) -> list[bytes]:
        doc = fitz.open(str(input_path))
        mat = fitz.Matrix(scale, scale)
        thumbnails = []
        for page in doc:
            pix = page.get_pixmap(
                matrix=mat, alpha=False,
            )
            thumbnails.append(pix.tobytes("png"))
        doc.close()
        return thumbnails


# "A ordem e o primeiro passo para a maestria."
# — Jocko Willink
