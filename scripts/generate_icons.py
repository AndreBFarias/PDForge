"""Gera icones quadrados multi-tamanho a partir do asset PDForge.png."""

import logging
import shutil
from pathlib import Path

from PIL import Image

logger = logging.getLogger("pdfforge.scripts.icons")

SIZES = (48, 64, 128, 256, 512)
BASE_DIR = Path(__file__).parent.parent
SOURCE = BASE_DIR / "assets" / "PDForge.png"
ICONS_DIR = BASE_DIR / "assets" / "icons"


def generate() -> None:
    if not SOURCE.exists():
        logger.error("Asset nao encontrado: %s", SOURCE)
        return

    ICONS_DIR.mkdir(parents=True, exist_ok=True)
    img = Image.open(SOURCE).convert("RGBA")
    w, h = img.size
    side = max(w, h)

    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    offset_x = (side - w) // 2
    offset_y = (side - h) // 2
    canvas.paste(img, (offset_x, offset_y))

    for size in SIZES:
        resized = canvas.resize((size, size), Image.Resampling.LANCZOS)
        out_path = ICONS_DIR / f"pdfforge-{size}.png"
        resized.save(out_path, "PNG")
        logger.info("Gerado: %s", out_path)

    icon_256 = ICONS_DIR / "pdfforge-256.png"
    icon_compat = BASE_DIR / "assets" / "icon.png"
    if icon_256.exists():
        shutil.copy2(icon_256, icon_compat)
        logger.info("Copiado para compatibilidade: %s", icon_compat)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    generate()


# "Simplicidade é a sofisticação definitiva." — Leonardo da Vinci
