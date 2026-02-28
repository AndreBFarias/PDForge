import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import fitz

logger = logging.getLogger("pdfforge")


@dataclass
class MergeEntry:
    path: Path
    page_range: tuple[int, int] | None = None
    label: str = ""


@dataclass
class MergeResult:
    output_path: Path
    total_pages: int
    sources: list[str] = field(default_factory=list)
    success: bool = True
    error: str = ""


class PDFMerger:
    def merge(
        self,
        entries: list[MergeEntry],
        output_path: Path,
        on_progress: Callable[[int, int, str], None] | None = None,
    ) -> MergeResult:
        output = fitz.open()
        sources = []
        total = len(entries)

        try:
            for i, entry in enumerate(entries):
                if on_progress:
                    on_progress(i + 1, total, entry.path.name)

                with fitz.open(str(entry.path)) as src:
                    if entry.page_range:
                        from_page, to_page = entry.page_range
                        output.insert_pdf(src, from_page=from_page, to_page=to_page)
                    else:
                        output.insert_pdf(src)
                    sources.append(entry.path.name)
                    logger.debug("Mesclado: %s (%d pags)", entry.path.name, src.page_count)

            output.save(str(output_path))
            logger.info("Merge concluido: %d paginas em %s", output.page_count, output_path)
            return MergeResult(
                output_path=output_path,
                total_pages=output.page_count,
                sources=sources,
            )
        except Exception as exc:
            logger.error("Erro no merge: %s", exc)
            return MergeResult(
                output_path=output_path,
                total_pages=0,
                sources=sources,
                success=False,
                error=str(exc),
            )
        finally:
            output.close()


# "A uniao faz a forca." — Provérbio latino
