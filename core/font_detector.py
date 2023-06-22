import logging
from collections import Counter
from dataclasses import dataclass

import fitz

from utils.font_matcher import FontMatcher, FontInfo

logger = logging.getLogger("pdfforge.font_detector")


@dataclass
class FontUsage:
    info: FontInfo
    occurrences: int
    pages: list[int]
    sizes: list[float]

    @property
    def avg_size(self) -> float:
        return sum(self.sizes) / len(self.sizes) if self.sizes else 0.0

    @property
    def size_range(self) -> tuple[float, float]:
        if not self.sizes:
            return (0.0, 0.0)
        return (min(self.sizes), max(self.sizes))


class FontDetector:
    """Extrai e classifica todas as fontes usadas em um PDF."""

    def __init__(self) -> None:
        self._matcher = FontMatcher()

    def extract(self, doc: fitz.Document) -> list[FontUsage]:
        """
        Extrai todas as fontes do documento.
        Retorna lista ordenada por número de ocorrências (desc).
        """
        raw_fonts: dict[str, dict] = {}

        for page_num, page in enumerate(doc):
            text_dict = page.get_text("dict")
            for block in text_dict.get("blocks", []):
                if block.get("type") != 0:  # 0 = bloco de texto
                    continue
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        self._register_span(span, page_num, raw_fonts)

        return self._build_usage_list(raw_fonts)

    def _register_span(self, span: dict, page_num: int, registry: dict) -> None:
        font_name = span.get("font", "desconhecida")
        size = span.get("size", 0.0)
        text = span.get("text", "").strip()
        if not text:
            return

        if font_name not in registry:
            registry[font_name] = {
                "count": 0,
                "pages": set(),
                "sizes": [],
            }
        entry = registry[font_name]
        entry["count"] += 1
        entry["pages"].add(page_num)
        entry["sizes"].append(round(size, 1))

    def _build_usage_list(self, raw: dict) -> list[FontUsage]:
        result = []
        for font_name, data in raw.items():
            info = self._matcher.match(font_name)
            result.append(FontUsage(
                info=info,
                occurrences=data["count"],
                pages=sorted(data["pages"]),
                sizes=data["sizes"],
            ))
        result.sort(key=lambda u: u.occurrences, reverse=True)
        logger.info("Fontes detectadas: %d tipos únicos", len(result))
        return result

    def get_dominant_font(self, doc: fitz.Document) -> FontUsage | None:
        """Retorna a fonte mais usada no documento."""
        usages = self.extract(doc)
        return usages[0] if usages else None
