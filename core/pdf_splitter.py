import io
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import fitz

logger = logging.getLogger("pdfforge")


@dataclass
class SplitResult:
    output_files: list[Path] = field(default_factory=list)
    success: bool = True
    error: str = ""


class PDFSplitter:
    def split_by_range(
        self,
        doc: fitz.Document,
        ranges: list[tuple[int, int]],
        output_dir: Path,
        base_name: str,
    ) -> SplitResult:
        result = SplitResult()
        output_dir.mkdir(parents=True, exist_ok=True)
        try:
            for i, (start, end) in enumerate(ranges):
                out_path = output_dir / f"{base_name}_parte{i + 1:02d}.pdf"
                new_doc = fitz.open()
                new_doc.insert_pdf(doc, from_page=start, to_page=end)
                new_doc.save(str(out_path))
                new_doc.close()
                result.output_files.append(out_path)
                logger.debug("Split parte %d: paginas %d-%d -> %s", i + 1, start, end, out_path)
        except Exception as exc:
            logger.error("Erro no split por range: %s", exc)
            result.success = False
            result.error = str(exc)
        return result

    def split_by_size(
        self,
        doc: fitz.Document,
        max_mb: float,
        output_dir: Path,
        base_name: str,
    ) -> SplitResult:
        result = SplitResult()
        output_dir.mkdir(parents=True, exist_ok=True)
        max_bytes = max_mb * 1024 * 1024

        try:
            part_num = 1
            start_page = 0
            total_pages = doc.page_count

            while start_page < total_pages:
                end_page = start_page

                while end_page < total_pages:
                    test_doc = fitz.open()
                    test_doc.insert_pdf(doc, from_page=start_page, to_page=end_page)
                    buf = io.BytesIO()
                    test_doc.save(buf)
                    current_size = buf.tell()
                    test_doc.close()

                    if current_size > max_bytes and end_page > start_page:
                        end_page -= 1
                        break
                    end_page += 1

                out_path = output_dir / f"{base_name}_parte{part_num:02d}.pdf"
                chunk = fitz.open()
                chunk.insert_pdf(doc, from_page=start_page, to_page=end_page - 1)
                chunk.save(str(out_path))
                chunk.close()
                result.output_files.append(out_path)
                logger.debug("Split tamanho parte %d: pags %d-%d", part_num, start_page, end_page - 1)

                start_page = end_page
                part_num += 1
        except Exception as exc:
            logger.error("Erro no split por tamanho: %s", exc)
            result.success = False
            result.error = str(exc)
        return result

    def split_by_bookmarks(
        self,
        doc: fitz.Document,
        output_dir: Path,
        base_name: str,
    ) -> SplitResult:
        result = SplitResult()
        output_dir.mkdir(parents=True, exist_ok=True)
        toc = doc.get_toc()

        if not toc:
            logger.warning("Documento sem bookmarks para split")
            result.success = False
            result.error = "Documento sem bookmarks (TOC vazio)"
            return result

        try:
            ranges = []
            for entry in toc:
                level, title, page_num = entry
                if level != 1:
                    continue
                start = page_num - 1
                if ranges:
                    ranges[-1] = (ranges[-1][0], start - 1, ranges[-1][2])
                ranges.append((start, doc.page_count - 1, title))

            for i, (start, end, title) in enumerate(ranges):
                safe_title = "".join(c if c.isalnum() or c in " _-" else "_" for c in title)[:40]
                out_path = output_dir / f"{base_name}_{i + 1:02d}_{safe_title}.pdf"
                chunk = fitz.open()
                chunk.insert_pdf(doc, from_page=start, to_page=end)
                chunk.save(str(out_path))
                chunk.close()
                result.output_files.append(out_path)
                logger.debug("Split bookmark '%s': pags %d-%d", title, start, end)
        except Exception as exc:
            logger.error("Erro no split por bookmarks: %s", exc)
            result.success = False
            result.error = str(exc)
        return result


# "Dividir para conquistar." — Júlio César
