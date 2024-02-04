import logging
from dataclasses import dataclass, field
from pathlib import Path

import fitz

logger = logging.getLogger("pdfforge.image_converter")


@dataclass
class ConvertResult:
    success: bool = True
    output_paths: list[Path] = field(default_factory=list)
    total_pages: int = 0
    error: str = ""


class PDFImageConverter:
    """Conversao bidirecional entre PDF e imagens."""

    def pdf_to_images(
        self,
        input_path: Path,
        output_dir: Path,
        fmt: str = "png",
        dpi: int = 150,
        pages: list[int] | None = None,
    ) -> ConvertResult:
        output_dir.mkdir(parents=True, exist_ok=True)
        result = ConvertResult()
        try:
            doc = fitz.open(str(input_path))
            indices = pages if pages is not None else list(range(len(doc)))
            scale = dpi / 72.0
            mat = fitz.Matrix(scale, scale)

            for page_num in indices:
                if page_num < 0 or page_num >= len(doc):
                    continue
                page = doc[page_num]
                pix = page.get_pixmap(
                    matrix=mat,
                    alpha=False,
                )
                ext = fmt.lower()
                out_file = output_dir / f"pagina_{page_num + 1:03d}.{ext}"
                if ext == "jpg" or ext == "jpeg":
                    pix.save(str(out_file), output="jpeg")
                else:
                    pix.save(str(out_file))
                result.output_paths.append(out_file)

            result.total_pages = len(result.output_paths)
            doc.close()
            logger.info(
                "PDF convertido para %d imagens (%s, %d DPI)",
                result.total_pages,
                fmt,
                dpi,
            )
        except Exception as exc:
            logger.error(
                "Erro na conversao PDF->imagens: %s",
                exc,
            )
            result.success = False
            result.error = str(exc)
        return result

    def images_to_pdf(
        self,
        image_paths: list[Path],
        output_path: Path,
    ) -> ConvertResult:
        result = ConvertResult()
        if not image_paths:
            result.success = False
            result.error = "Lista de imagens vazia"
            return result

        try:
            output_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )
            doc = fitz.open()

            for img_path in image_paths:
                img_doc = fitz.open(str(img_path))
                rect = img_doc[0].rect
                img_doc.close()

                page = doc.new_page(
                    width=rect.width,
                    height=rect.height,
                )
                page.insert_image(
                    page.rect,
                    filename=str(img_path),
                )
                result.output_paths.append(img_path)

            result.total_pages = len(doc)
            doc.save(str(output_path))
            doc.close()
            logger.info(
                "PDF criado com %d imagens: %s",
                result.total_pages,
                output_path.name,
            )
        except Exception as exc:
            logger.error(
                "Erro na conversao imagens->PDF: %s",
                exc,
            )
            result.success = False
            result.error = str(exc)
        return result


# "Uma imagem vale mais que mil palavras." -- Fred R. Barnard
