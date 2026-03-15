import io
import logging
from dataclasses import dataclass
from pathlib import Path

import fitz

logger = logging.getLogger("pdfforge.watermark")

try:
    from PIL import Image, ImageDraw, ImageFont

    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


@dataclass
class WatermarkConfig:
    text: str = ""
    font_size: int = 48
    color: tuple[int, int, int] = (128, 128, 128)
    opacity: float = 0.3
    rotation: float = -45.0
    position: str = "center"


@dataclass
class WatermarkResult:
    success: bool = True
    output_path: Path | None = None
    pages_processed: int = 0
    error: str = ""


class PDFWatermark:
    """Aplica marca d'água de texto ou imagem em PDFs."""

    def apply_text(
        self,
        input_path: Path,
        output_path: Path,
        config: WatermarkConfig,
    ) -> WatermarkResult:
        if not config.text:
            return WatermarkResult(
                success=False,
                error="Texto da marca d'água não informado",
            )
        if not PIL_AVAILABLE:
            return WatermarkResult(
                success=False,
                error="Pillow não instalado",
            )

        try:
            doc = fitz.open(str(input_path))
            for page in doc:
                overlay = self._create_text_overlay(
                    config.text,
                    int(page.rect.width),
                    int(page.rect.height),
                    config,
                )
                page.insert_image(
                    page.rect,
                    stream=overlay,
                    overlay=True,
                )

            output_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )
            doc.save(
                str(output_path),
                garbage=4,
                deflate=True,
            )
            pages = len(doc)
            doc.close()
            logger.info(
                "Marca d'água de texto aplicada: %d páginas",
                pages,
            )
            return WatermarkResult(
                output_path=output_path,
                pages_processed=pages,
            )
        except Exception as exc:
            logger.error(
                "Erro ao aplicar marca d'água: %s",
                exc,
            )
            return WatermarkResult(
                success=False,
                error=str(exc),
            )

    def apply_image(
        self,
        input_path: Path,
        output_path: Path,
        image_path: Path,
        opacity: float = 0.3,
        position: str = "center",
        scale: float = 1.0,
    ) -> WatermarkResult:
        if not PIL_AVAILABLE:
            return WatermarkResult(
                success=False,
                error="Pillow não instalado",
            )
        if not image_path.exists():
            return WatermarkResult(
                success=False,
                error=(f"Imagem não encontrada: {image_path}"),
            )

        try:
            doc = fitz.open(str(input_path))
            overlay_bytes = self._create_image_overlay(
                image_path,
                int(doc[0].rect.width),
                int(doc[0].rect.height),
                opacity,
                scale,
            )

            for page in doc:
                page.insert_image(
                    page.rect,
                    stream=overlay_bytes,
                    overlay=True,
                )

            output_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )
            doc.save(
                str(output_path),
                garbage=4,
                deflate=True,
            )
            pages = len(doc)
            doc.close()
            logger.info(
                "Marca d'água de imagem aplicada: %d páginas",
                pages,
            )
            return WatermarkResult(
                output_path=output_path,
                pages_processed=pages,
            )
        except Exception as exc:
            logger.error(
                "Erro ao aplicar marca d'água de imagem: %s",
                exc,
            )
            return WatermarkResult(
                success=False,
                error=str(exc),
            )

    def _create_text_overlay(
        self,
        text: str,
        width: int,
        height: int,
        config: WatermarkConfig,
    ) -> bytes:
        alpha = int(config.opacity * 255)
        color = (*config.color, alpha)

        if config.position == "tile":
            return self._create_tile_overlay(
                text,
                width,
                height,
                config,
                color,
            )

        img = Image.new(
            "RGBA",
            (width, height),
            (0, 0, 0, 0),
        )
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                config.font_size,
            )
        except OSError:
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        x = (width - tw) // 2
        y = (height - th) // 2

        if abs(config.rotation) > 0.1:
            txt_img = Image.new(
                "RGBA",
                (tw + 20, th + 20),
                (0, 0, 0, 0),
            )
            txt_draw = ImageDraw.Draw(txt_img)
            txt_draw.text(
                (10, 10),
                text,
                fill=color,
                font=font,
            )
            rotated = txt_img.rotate(
                -config.rotation,
                expand=True,
                resample=Image.BICUBIC,
            )
            rx = (width - rotated.width) // 2
            ry = (height - rotated.height) // 2
            img.paste(rotated, (rx, ry), rotated)
        else:
            draw.text(
                (x, y),
                text,
                fill=color,
                font=font,
            )

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()

    def _create_tile_overlay(
        self,
        text: str,
        width: int,
        height: int,
        config: WatermarkConfig,
        color: tuple,
    ) -> bytes:
        img = Image.new(
            "RGBA",
            (width, height),
            (0, 0, 0, 0),
        )
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                config.font_size,
            )
        except OSError:
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        step_x = tw + 80
        step_y = th + 80

        for y in range(-height, height * 2, step_y):
            for x in range(
                -width,
                width * 2,
                step_x,
            ):
                txt_img = Image.new(
                    "RGBA",
                    (tw + 20, th + 20),
                    (0, 0, 0, 0),
                )
                txt_draw = ImageDraw.Draw(txt_img)
                txt_draw.text(
                    (10, 10),
                    text,
                    fill=color,
                    font=font,
                )
                if abs(config.rotation) > 0.1:
                    txt_img = txt_img.rotate(
                        -config.rotation,
                        expand=True,
                        resample=Image.BICUBIC,
                    )
                img.paste(txt_img, (x, y), txt_img)

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()

    def _create_image_overlay(
        self,
        image_path: Path,
        width: int,
        height: int,
        opacity: float,
        scale: float,
    ) -> bytes:
        wm_img = Image.open(
            str(image_path),
        ).convert("RGBA")
        new_w = int(wm_img.width * scale)
        new_h = int(wm_img.height * scale)
        wm_img = wm_img.resize(
            (new_w, new_h),
            Image.LANCZOS,
        )

        alpha = wm_img.split()[3]
        alpha = alpha.point(
            lambda p: int(p * opacity),
        )
        wm_img.putalpha(alpha)

        canvas = Image.new(
            "RGBA",
            (width, height),
            (0, 0, 0, 0),
        )
        x = (width - new_w) // 2
        y = (height - new_h) // 2
        canvas.paste(wm_img, (x, y), wm_img)

        buf = io.BytesIO()
        canvas.save(buf, format="PNG")
        return buf.getvalue()


# "A marca é a alma visível do produto." — David Ogilvy
