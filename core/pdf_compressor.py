import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import fitz

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

logger = logging.getLogger("pdfforge")

COMPRESS_PROFILES: dict[str, dict] = {
    "leve": {"dpi": 150, "jpeg_quality": 85, "deflate_images": False},
    "medio": {"dpi": 120, "jpeg_quality": 72, "deflate_images": True},
    "agressivo": {"dpi": 96, "jpeg_quality": 55, "deflate_images": True},
}

_REDUCTION_BY_TYPE = {
    "TEXT_ONLY": 0.05,
    "SCANNED": 0.45,
    "IMAGE_HEAVY": 0.35,
    "MIXED": 0.20,
}

_PROFILE_FACTOR = {"leve": 0.5, "medio": 1.0, "agressivo": 1.5}


class PageContentType(Enum):
    TEXT_ONLY = "TEXT_ONLY"
    IMAGE_HEAVY = "IMAGE_HEAVY"
    MIXED = "MIXED"
    SCANNED = "SCANNED"


@dataclass
class CompressResult:
    output_path: Path
    original_size_mb: float
    compressed_size_mb: float
    reduction_pct: float
    content_type: PageContentType
    profile_used: str
    success: bool = True
    error: str = ""


class PDFCompressor:
    def analyze_content_type(
        self, doc: fitz.Document, sample_pages: int = 5
    ) -> PageContentType:
        total = doc.page_count
        step = max(1, total // sample_pages)
        indices = list(range(0, total, step))[:sample_pages]

        text_counts = []
        image_counts = []
        variances = []

        for idx in indices:
            page = doc[idx]
            text = page.get_text()
            images = page.get_images()
            text_counts.append(len(text.strip()))
            image_counts.append(len(images))

            if CV2_AVAILABLE:
                try:
                    mat = fitz.Matrix(0.5, 0.5)
                    pix = page.get_pixmap(matrix=mat)
                    img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
                        pix.height, pix.width, pix.n
                    )
                    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY) if pix.n >= 3 else img_array
                    lap_var = cv2.Laplacian(gray, cv2.CV_64F).var()
                    variances.append(lap_var)
                except Exception as exc:
                    logger.debug("Erro na analise de variancia: %s", exc)

        total_text = sum(text_counts)
        total_images = sum(image_counts)

        if variances and (sum(variances) / len(variances)) < 50:
            return PageContentType.SCANNED

        if total_images == 0 and total_text > 0:
            return PageContentType.TEXT_ONLY

        if total_images > total_text / 100:
            return PageContentType.IMAGE_HEAVY

        return PageContentType.MIXED

    def compress(
        self, doc: fitz.Document, output_path: Path, profile: str = "medio"
    ) -> CompressResult:
        if profile not in COMPRESS_PROFILES:
            return CompressResult(
                output_path=output_path,
                original_size_mb=0.0,
                compressed_size_mb=0.0,
                reduction_pct=0.0,
                content_type=PageContentType.MIXED,
                profile_used=profile,
                success=False,
                error=f"Perfil invalido: '{profile}'. Use: {list(COMPRESS_PROFILES.keys())}",
            )

        cfg = COMPRESS_PROFILES[profile]
        quality = cfg["jpeg_quality"]
        deflate = cfg["deflate_images"]
        content_type = self.analyze_content_type(doc)

        import io
        buf_orig = io.BytesIO()
        doc.save(buf_orig)
        original_mb = buf_orig.tell() / (1024 * 1024)

        try:
            new_doc = fitz.open()
            new_doc.insert_pdf(doc)

            if CV2_AVAILABLE:
                import numpy as np
                for page in new_doc:
                    for img_info in page.get_images(full=True):
                        xref = img_info[0]
                        try:
                            pix = fitz.Pixmap(new_doc, xref)
                            if pix.n > 4:
                                pix = fitz.Pixmap(fitz.csRGB, pix)
                            img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
                                pix.height, pix.width, pix.n
                            )
                            if pix.n == 4:
                                img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)
                            _, jpeg_bytes = cv2.imencode(
                                ".jpg", img_array,
                                [cv2.IMWRITE_JPEG_QUALITY, quality]
                            )
                            rect = page.rect
                            page.insert_image(rect, stream=jpeg_bytes.tobytes())
                        except Exception as exc:
                            logger.debug("Nao foi possivel recomprimir imagem xref=%d: %s", xref, exc)

            output_path.parent.mkdir(parents=True, exist_ok=True)
            new_doc.save(
                str(output_path),
                deflate=deflate,
                garbage=4,
                clean=True,
            )
            new_doc.close()

            compressed_mb = output_path.stat().st_size / (1024 * 1024)
            reduction = max(0.0, (original_mb - compressed_mb) / original_mb * 100) if original_mb > 0 else 0.0

            logger.info(
                "Compressao concluida: %.2fMB -> %.2fMB (%.1f%%) perfil=%s",
                original_mb, compressed_mb, reduction, profile,
            )
            return CompressResult(
                output_path=output_path,
                original_size_mb=round(original_mb, 3),
                compressed_size_mb=round(compressed_mb, 3),
                reduction_pct=round(reduction, 1),
                content_type=content_type,
                profile_used=profile,
            )
        except Exception as exc:
            logger.error("Erro na compressao: %s", exc)
            return CompressResult(
                output_path=output_path,
                original_size_mb=round(original_mb, 3),
                compressed_size_mb=0.0,
                reduction_pct=0.0,
                content_type=content_type,
                profile_used=profile,
                success=False,
                error=str(exc),
            )

    def get_compression_estimate(
        self, doc: fitz.Document, profile: str
    ) -> dict[str, float]:
        import io
        buf = io.BytesIO()
        doc.save(buf)
        original_mb = buf.tell() / (1024 * 1024)

        content_type = self.analyze_content_type(doc)
        base_reduction = _REDUCTION_BY_TYPE.get(content_type.value, 0.20)
        factor = _PROFILE_FACTOR.get(profile, 1.0)
        reduction = min(base_reduction * factor, 0.90)
        estimated_mb = original_mb * (1.0 - reduction)

        return {
            "original_mb": round(original_mb, 3),
            "estimated_mb": round(estimated_mb, 3),
            "reduction_pct": round(reduction * 100, 1),
        }


# "A arte de comprimir é a arte de preservar o essencial." — Anônimo
