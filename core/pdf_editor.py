import logging
from dataclasses import dataclass
from pathlib import Path

import fitz

from utils.file_utils import ensure_output_path

logger = logging.getLogger("pdfforge.editor")


@dataclass
class ReplaceResult:
    total_replacements: int
    pages_affected: list[int]
    output_path: Path


class PDFEditor:
    """
    Busca e substituição de texto em PDFs preservando estilo tipográfico original.

    Estratégia:
      1. Para todos os pares buscar→substituir, coletar rects + atributos de span em uma
         única passagem por página.
      2. Marcar todas as áreas com redact annotation em lote (sem fill, preservando fundo).
      3. Aplicar redações uma única vez por página (images=0, graphics=0).
      4. Reinserir cada texto no baseline exato, com auto-escala se o substituto for mais
         largo que a bbox original.
    """

    def replace_text(
        self,
        doc: fitz.Document,
        pairs: list[tuple[str, str]],
        output_path: Path,
        case_sensitive: bool = False,
    ) -> ReplaceResult:
        total = 0
        pages_affected: list[int] = []

        for page_num, page in enumerate(doc):
            count = self._replace_on_page(page, pairs, case_sensitive)
            if count > 0:
                total += count
                pages_affected.append(page_num)

        doc.save(str(output_path), garbage=4, deflate=True)
        logger.info(
            "Multi-substituição: %d par(es), %d ocorrências em %d página(s) → %s",
            len(pairs), total, len(pages_affected), output_path.name,
        )
        return ReplaceResult(
            total_replacements=total,
            pages_affected=pages_affected,
            output_path=output_path,
        )

    def _replace_on_page(
        self,
        page: fitz.Page,
        pairs: list[tuple[str, str]],
        case_sensitive: bool,
    ) -> int:
        # Fase 1: coletar todos os rects + atributos para todos os pares
        tasks: list[tuple[str, fitz.Rect, dict, fitz.Point]] = []

        for search, replacement in pairs:
            rects = page.search_for(search)
            if not rects:
                continue
            occurrences = self._collect_occurrences(page, search, case_sensitive)
            fallback_attrs = occurrences[0]["attrs"] if occurrences else {}
            for i, rect in enumerate(rects):
                if i < len(occurrences):
                    attrs = occurrences[i]["attrs"]
                    origin = occurrences[i]["origin"]
                else:
                    attrs = fallback_attrs
                    origin = fitz.Point(rect.x0, rect.y1)
                tasks.append((replacement, rect, attrs, origin))

        if not tasks:
            return 0

        # Fase 2: uma única chamada a apply_redactions() por página
        for _, rect, _, _ in tasks:
            page.add_redact_annot(rect, fill=None)
        page.apply_redactions(images=0, graphics=0)

        # Fase 3: reinserir com auto-escala
        for replacement, rect, attrs, origin in tasks:
            raw_font = attrs.get("font", "")
            fontname = self._map_to_builtin(raw_font)
            fontsize = attrs.get("size", 11.0)
            color = self._unpack_color(attrs.get("color", 0))

            available_width = rect.x1 - rect.x0
            text_width = fitz.get_text_length(replacement, fontname=fontname, fontsize=fontsize)
            if text_width > available_width and available_width > 0:
                fontsize = fontsize * (available_width / text_width)

            page.insert_text(
                point=origin,
                text=replacement,
                fontname=fontname,
                fontsize=fontsize,
                color=color,
            )

        return len(tasks)

    def _collect_occurrences(
        self, page: fitz.Page, search: str, case_sensitive: bool
    ) -> list[dict]:
        """
        Retorna lista de {attrs, origin} para cada span que contém o texto buscado.
        origin é o ponto de baseline exato do span — posição correta para insert_text().
        """
        text_dict = page.get_text("dict")
        search_lower = search if case_sensitive else search.lower()
        results = []
        for block in text_dict.get("blocks", []):
            if block.get("type") != 0:
                continue
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    span_text = span.get("text", "")
                    compare = span_text if case_sensitive else span_text.lower()
                    if search_lower in compare:
                        results.append({
                            "attrs": span,
                            "origin": fitz.Point(span["origin"]),
                        })
        return results

    _BUILTIN_FONTS = {"helv", "tiro", "cour", "symb", "zadb"}
    _SERIF_KEYWORDS = {"times", "serif", "roman", "georgia", "garamond", "palatino"}
    _MONO_KEYWORDS = {"courier", "mono", "consolas", "inconsolata", "sourcecodemono"}

    def _map_to_builtin(self, raw: str) -> str:
        """
        Mapeia um nome de fonte do PDF para a built-in mais próxima do PyMuPDF.
        Fontes embutidas chegam como 'XXXXXX+FontName' — extrai a parte útil e
        compara keywords para escolher helv/tiro/cour. Fallback: helv.
        Fontes built-in têm cobertura completa Latin-1, sem risco de glifo ausente.
        """
        if raw in self._BUILTIN_FONTS:
            return raw
        name = raw.split("+")[-1].lower()
        for keyword in self._MONO_KEYWORDS:
            if keyword in name:
                return "cour"
        for keyword in self._SERIF_KEYWORDS:
            if keyword in name:
                return "tiro"
        return "helv"

    def _unpack_color(self, color: int | tuple) -> tuple[float, float, float]:
        """Converte cor do formato fitz (int RGB) para tuple normalizada (0.0-1.0)."""
        if isinstance(color, (list, tuple)):
            return tuple(color[:3])  # type: ignore[return-value]
        r = ((color >> 16) & 0xFF) / 255.0
        g = ((color >> 8) & 0xFF) / 255.0
        b = (color & 0xFF) / 255.0
        return (r, g, b)


# "A ação é o antídoto do desespero." — Joan Baez
