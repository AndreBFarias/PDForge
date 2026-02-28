import logging
import re
from dataclasses import dataclass

logger = logging.getLogger("pdfforge.font_matcher")

# Famílias de fontes conhecidas com aliases comuns
_FONT_FAMILIES: dict[str, list[str]] = {
    "helvetica": ["helvetica", "arial", "nimbus sans", "liberation sans"],
    "times": ["times", "times new roman", "nimbus roman", "liberation serif"],
    "courier": ["courier", "courier new", "nimbus mono", "liberation mono"],
    "georgia": ["georgia"],
    "garamond": ["garamond", "eb garamond", "cormorant garamond"],
    "palatino": ["palatino", "palatino linotype", "book antiqua", "uri"],
    "calibri": ["calibri"],
    "cambria": ["cambria"],
    "verdana": ["verdana"],
    "tahoma": ["tahoma"],
    "trebuchet": ["trebuchet ms"],
    "franklin gothic": ["franklin gothic", "itc franklin gothic"],
}

# Padrões para detectar variantes de peso/estilo no nome da fonte
_BOLD_PATTERN = re.compile(r"\b(bold|heavy|black|semibold|demi)\b", re.IGNORECASE)
_ITALIC_PATTERN = re.compile(r"\b(italic|oblique|it)\b", re.IGNORECASE)
_MONO_PATTERN = re.compile(r"\b(mono|monospace|console|code|courier|typewriter)\b", re.IGNORECASE)
_SERIF_NAMES = {"times", "georgia", "garamond", "palatino", "cambria", "book antiqua"}


@dataclass
class FontInfo:
    raw_name: str
    family: str
    is_bold: bool
    is_italic: bool
    is_monospace: bool
    is_serif: bool

    @property
    def display_name(self) -> str:
        parts = [self.family.title()]
        if self.is_bold:
            parts.append("Bold")
        if self.is_italic:
            parts.append("Italic")
        return " ".join(parts)


class FontMatcher:
    """Identifica famílias de fontes e características a partir de nomes brutos do PDF."""

    def match(self, raw_name: str) -> FontInfo:
        clean = self._clean_name(raw_name)
        family = self._find_family(clean)
        return FontInfo(
            raw_name=raw_name,
            family=family,
            is_bold=bool(_BOLD_PATTERN.search(raw_name)),
            is_italic=bool(_ITALIC_PATTERN.search(raw_name)),
            is_monospace=bool(_MONO_PATTERN.search(raw_name)),
            is_serif=self._is_serif(family, raw_name),
        )

    def _clean_name(self, name: str) -> str:
        # Remove prefixo de subset (ex: "ABCDEF+TimesNewRoman" → "timesnewroman")
        name = re.sub(r"^[A-Z]{6}\+", "", name)
        # Remove variantes após hífen: "Arial-BoldMT" → "arial"
        name = name.split("-")[0]
        return name.lower().strip()

    def _find_family(self, clean: str) -> str:
        for family, aliases in _FONT_FAMILIES.items():
            for alias in aliases:
                if alias in clean or clean in alias:
                    return family
        # Fallback: usa o nome limpo como família
        return clean if clean else "desconhecida"

    def _is_serif(self, family: str, raw_name: str) -> bool:
        if family in _SERIF_NAMES:
            return True
        lower = raw_name.lower()
        return any(name in lower for name in _SERIF_NAMES)

    def are_compatible(self, name_a: str, name_b: str) -> bool:
        """Verifica se duas fontes pertencem à mesma família tipográfica."""
        info_a = self.match(name_a)
        info_b = self.match(name_b)
        return info_a.family == info_b.family
