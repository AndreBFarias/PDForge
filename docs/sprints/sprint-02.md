# Sprint 02 — Settings + Core CRUD (merger, splitter, rotator)

**Diretório:** `/home/andrefarias/Desenvolvimento/PDForge`
**Conta git:** `AndreBFarias` / `andre.dsbf@gmail.com`
**Pré-requisito:** Sprint 01 concluído e commitado.

Execute todas as tasks direto, sem criar task list, sem confirmar etapas, sem parar a não ser em erro real.

---

## Task 1 — Atualizar config/settings.py

Adicionar ao final de `config/settings.py`, antes do comentário de assinatura (`# "A ordem..."`):

```python
# --- Viewer inline ---
PDF_VIEWER_DEFAULT_SCALE: float = 1.0
PDF_VIEWER_MAX_SCALE: float = 4.0
PDF_VIEWER_MIN_SCALE: float = 0.25

# --- Compressao ---
COMPRESS_DEFAULT_PROFILE: str = "medio"

# --- Classificador ML ---
CLASSIFIER_MODEL_PATH: Path = Path.home() / ".pdfforge" / "models" / "classifier.pkl"

# --- Assinaturas ---
SIGNATURE_EXTRACT_SCALE: float = 3.0
SIGNATURE_TEMP_DIR: Path = Path.home() / ".pdfforge" / "tmp" / "signatures"
```

Essas constantes devem ficar dentro da classe `Settings`, após os atributos existentes.
Leia o arquivo antes de editar para garantir o posicionamento correto.

---

## Task 2 — core/pdf_merger.py

Criar `core/pdf_merger.py` com o conteúdo exato abaixo:

```python
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
```

---

## Task 3 — core/pdf_splitter.py

Criar `core/pdf_splitter.py`:

```python
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
```

---

## Task 4 — core/pdf_rotator.py

Criar `core/pdf_rotator.py`:

```python
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
```

---

## Commit final do sprint

```bash
git add config/settings.py core/pdf_merger.py core/pdf_splitter.py core/pdf_rotator.py
git commit -m "feat: adiciona constantes de settings e módulos core de merge, split e rotação"
```

**Próximo sprint:** `sprint-03.md`
