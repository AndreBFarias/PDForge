import logging
from pathlib import Path
from typing import Callable

import fitz

from config.settings import OCR_BATCH_MAX_PAGES, OCR_IMAGE_SCALE
from utils.gpu_utils import GPUMonitor

logger = logging.getLogger("pdfforge.ocr")


class OCREngine:
    """
    Motor OCR baseado em EasyOCR com suporte a CUDA.

    Carregamento do modelo é lazy (primeira chamada a recognize()).
    Fallback automático para CPU se CUDA indisponível ou VRAM insuficiente.
    """

    def __init__(
        self,
        languages: list[str] | None = None,
        use_gpu: bool = True,
    ) -> None:
        self._languages = languages or ["pt", "en"]
        self._gpu_monitor = GPUMonitor()
        self._use_gpu = use_gpu and self._gpu_monitor.cuda_available
        self._reader = None  # lazy init
        logger.info(
            "OCREngine configurado: langs=%s gpu=%s",
            self._languages,
            self._use_gpu,
        )

    def _get_reader(self):
        if self._reader is None:
            try:
                import easyocr
                stats = self._gpu_monitor.get_stats()
                # Verificar VRAM disponível antes de carregar modelo
                if self._use_gpu and stats.vram_free_mb < 1500:
                    logger.warning(
                        "VRAM livre insuficiente (%.0f MB) — forçando CPU",
                        stats.vram_free_mb,
                    )
                    self._use_gpu = False
                self._reader = easyocr.Reader(
                    self._languages,
                    gpu=self._use_gpu,
                )
                logger.info("EasyOCR carregado (gpu=%s)", self._use_gpu)
            except ImportError:
                raise RuntimeError("EasyOCR não instalado. Execute: pip install easyocr")
        return self._reader

    def recognize_page(
        self,
        page: fitz.Page,
        on_progress: Callable[[str], None] | None = None,
    ) -> str:
        """
        Executa OCR em uma página do PDF.
        Retorna o texto extraído como string.
        """
        mat = fitz.Matrix(OCR_IMAGE_SCALE, OCR_IMAGE_SCALE)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img_bytes = pix.tobytes("png")

        if on_progress:
            on_progress(f"Processando página {page.number + 1}...")

        reader = self._get_reader()
        results = reader.readtext(img_bytes, detail=0, paragraph=True)
        text = "\n".join(results)
        logger.debug("Página %d: %d chars extraídos via OCR", page.number, len(text))
        return text

    def recognize_document(
        self,
        doc: fitz.Document,
        page_indices: list[int] | None = None,
        on_progress: Callable[[int, int, str], None] | None = None,
    ) -> dict[int, str]:
        """
        Executa OCR nas páginas indicadas (ou em todas se None).
        Respeita o limite de páginas simultâneas para RTX 3050.

        Retorna {page_num: texto_ocr}.
        """
        indices = page_indices if page_indices is not None else list(range(len(doc)))
        results: dict[int, str] = {}

        total = len(indices)
        for batch_start in range(0, total, OCR_BATCH_MAX_PAGES):
            batch = indices[batch_start : batch_start + OCR_BATCH_MAX_PAGES]
            for idx, page_num in enumerate(batch):
                global_idx = batch_start + idx
                if on_progress:
                    on_progress(global_idx + 1, total, f"OCR página {page_num + 1}/{len(doc)}")

                page = doc[page_num]
                results[page_num] = self.recognize_page(page)
                self._gpu_monitor.clear_cache()

        logger.info("OCR concluído: %d páginas processadas", len(results))
        return results

    def save_ocr_layer(
        self,
        doc: fitz.Document,
        ocr_results: dict[int, str],
        output_path: Path,
    ) -> None:
        """
        Insere texto OCR como camada invisível sobre as páginas-imagem.
        Permite busca no texto mesmo em PDFs escaneados.
        """
        for page_num, text in ocr_results.items():
            page = doc[page_num]
            page.insert_text(
                fitz.Point(10, 10),
                text,
                fontsize=1,
                color=(1, 1, 1),    # branco invisível
                overlay=True,
            )
        doc.save(str(output_path), garbage=4, deflate=True)
        logger.info("Camada OCR salva em: %s", output_path.name)
