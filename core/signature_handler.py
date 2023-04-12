import logging
from dataclasses import dataclass
from pathlib import Path

import fitz

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

logger = logging.getLogger("pdfforge")


@dataclass
class SignatureRegion:
    page_index: int
    rect: fitz.Rect
    image_index: int
    bbox: tuple[float, float, float, float]
    confidence: float = 0.0
    label: str = ""


class SignatureHandler:
    def detect_signatures(self, doc: fitz.Document) -> list[SignatureRegion]:
        regions = []

        for page_index in range(doc.page_count):
            page = doc[page_index]
            page_area = page.rect.width * page.rect.height
            images = page.get_images(full=True)

            for img_index, img_info in enumerate(images):
                xref = img_info[0]
                try:
                    pix = fitz.Pixmap(doc, xref)
                except Exception as exc:
                    logger.debug("Nao foi possivel obter pixmap xref=%d: %s", xref, exc)
                    continue

                width, height = pix.width, pix.height
                if height == 0:
                    continue

                aspect_ratio = width / height
                img_area = width * height
                area_fraction = img_area / page_area if page_area > 0 else 1.0

                confidence = 0.0

                if 2.0 <= aspect_ratio <= 8.0:
                    confidence += 0.3
                if area_fraction < 0.20:
                    confidence += 0.2

                if CV2_AVAILABLE:
                    try:
                        n = pix.n
                        img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape(height, width, n)
                        if n == 4:
                            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2GRAY)
                        elif n == 3:
                            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)

                        _, thresh = cv2.threshold(img_array, 200, 255, cv2.THRESH_BINARY_INV)
                        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                        if contours:
                            non_rect_count = sum(
                                1 for c in contours
                                if len(c) > 4 and cv2.contourArea(c) > 50
                            )
                            if non_rect_count > 0:
                                confidence += 0.3

                            if len(contours) > 3:
                                confidence += 0.2
                    except Exception as exc:
                        logger.debug("Erro na analise de contornos: %s", exc)
                else:
                    if 2.5 <= aspect_ratio <= 6.0:
                        confidence += 0.3

                if confidence >= 0.4:
                    img_rects = page.get_image_rects(xref)
                    rect = img_rects[0] if img_rects else page.rect
                    regions.append(
                        SignatureRegion(
                            page_index=page_index,
                            rect=rect,
                            image_index=img_index,
                            bbox=(rect.x0, rect.y0, rect.x1, rect.y1),
                            confidence=min(confidence, 1.0),
                            label=f"Assinatura p.{page_index + 1}",
                        )
                    )
                    logger.debug(
                        "Assinatura detectada: pagina=%d conf=%.2f", page_index, confidence
                    )

        return regions

    def extract_signature(
        self,
        doc: fitz.Document,
        region: SignatureRegion,
        output_path: Path,
        scale: float = 3.0,
    ) -> Path:
        page = doc[region.page_index]
        matrix = fitz.Matrix(scale, scale)
        pix = page.get_pixmap(matrix=matrix, clip=region.rect)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        pix.save(str(output_path))
        logger.info("Assinatura extraida em: %s", output_path)
        return output_path

    def reinsert_signature(
        self,
        doc: fitz.Document,
        region: SignatureRegion,
        image_path: Path,
        output_path: Path,
    ) -> bool:
        try:
            page = doc[region.page_index]
            page.insert_image(region.rect, filename=str(image_path))
            output_path.parent.mkdir(parents=True, exist_ok=True)
            doc.save(str(output_path))
            logger.info("Assinatura reinserida em: %s", output_path)
            return True
        except Exception as exc:
            logger.error("Erro ao reinserir assinatura: %s", exc)
            return False


# "A assinatura é a identidade do espírito." — Anônimo
