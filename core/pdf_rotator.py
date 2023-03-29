import logging
from dataclasses import dataclass
from pathlib import Path

import fitz

logger = logging.getLogger("pdfforge")

VALID_ANGLES = {90, 180, 270}


@dataclass
class RotateResult:
    output_path: Path
    pages_rotated: int
    success: bool = True
    error: str = ""


class PDFRotator:
    def rotate_pages(
        self,
        doc: fitz.Document,
        page_indices: list[int],
        angle: int,
        output_path: Path,
    ) -> RotateResult:
        if angle not in VALID_ANGLES:
            return RotateResult(
                output_path=output_path,
                pages_rotated=0,
                success=False,
                error=f"Angulo invalido: {angle}. Use 90, 180 ou 270.",
            )
        try:
            new_doc = fitz.open()
            new_doc.insert_pdf(doc)
            for idx in page_indices:
                if 0 <= idx < new_doc.page_count:
                    page = new_doc[idx]
                    page.set_rotation((page.rotation + angle) % 360)
            new_doc.save(str(output_path))
            new_doc.close()
            logger.info(
                "Rotacionadas %d paginas (%d°) -> %s", len(page_indices), angle, output_path
            )
            return RotateResult(output_path=output_path, pages_rotated=len(page_indices))
        except Exception as exc:
            logger.error("Erro ao rotacionar paginas: %s", exc)
            return RotateResult(
                output_path=output_path, pages_rotated=0, success=False, error=str(exc)
            )

    def rotate_all(
        self,
        doc: fitz.Document,
        angle: int,
        output_path: Path,
    ) -> RotateResult:
        return self.rotate_pages(doc, list(range(doc.page_count)), angle, output_path)


# "A perspectiva muda tudo." — Anônimo
