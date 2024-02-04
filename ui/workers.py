import logging
from pathlib import Path

import fitz
from PyQt6.QtCore import QThread, pyqtSignal

from core.batch_processor import BatchProcessor
from core.document_classifier import ClassificationResult, DocumentClassifier
from core.metadata import PDFMetadata
from core.ocr_engine import OCREngine
from core.pdf_compressor import PDFCompressor
from core.pdf_editor import PDFEditor
from core.pdf_merger import MergeEntry, PDFMerger
from core.pdf_splitter import PDFSplitter
from core.signature_handler import SignatureHandler, SignatureRegion

logger = logging.getLogger("pdfforge.workers")


class ReplaceWorker(QThread):
    """Executa PDFEditor.replace_text() com múltiplos pares em thread separada."""

    finished = pyqtSignal(object)  # ReplaceResult
    error = pyqtSignal(str)

    def __init__(
        self,
        pdf_path: Path,
        pairs: list[tuple[str, str]],
        output_path: Path,
        case_sensitive: bool = False,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._pdf_path = pdf_path
        self._pairs = pairs
        self._output_path = output_path
        self._case_sensitive = case_sensitive

    def run(self) -> None:
        try:
            doc = fitz.open(str(self._pdf_path))
            try:
                editor = PDFEditor()
                result = editor.replace_text(
                    doc,
                    self._pairs,
                    self._output_path,
                    self._case_sensitive,
                )
            finally:
                doc.close()
            self.finished.emit(result)
        except Exception as exc:
            logger.error("ReplaceWorker falhou: %s", exc, exc_info=True)
            self.error.emit(str(exc))


class DocxWorker(QThread):
    """Converte PDF para DOCX via pdf2docx em thread separada."""

    finished = pyqtSignal(Path)
    error = pyqtSignal(str)

    def __init__(self, pdf_path: Path, output_path: Path, parent=None) -> None:
        super().__init__(parent)
        self._pdf_path = pdf_path
        self._output_path = output_path

    def run(self) -> None:
        try:
            from pdf2docx import Converter  # importação lazy — graceful degradation

            cv = Converter(str(self._pdf_path))
            cv.convert(str(self._output_path))
            cv.close()
            self.finished.emit(self._output_path)
        except Exception as exc:
            logger.error("DocxWorker falhou: %s", exc, exc_info=True)
            self.error.emit(str(exc))


class OCRWorker(QThread):
    """Executa OCREngine.recognize_document() + save_ocr_layer() em thread separada."""

    finished = pyqtSignal(object)  # dict[int, str] resultados OCR
    progress = pyqtSignal(int, int, str)
    error = pyqtSignal(str)

    def __init__(
        self,
        pdf_path: Path,
        output_path: Path,
        languages: list[str],
        use_gpu: bool = True,
    ) -> None:
        super().__init__()
        self._pdf_path = pdf_path
        self._output_path = output_path
        self._languages = languages
        self._use_gpu = use_gpu

    def run(self) -> None:
        try:
            engine = OCREngine(languages=self._languages, use_gpu=self._use_gpu)
            doc = fitz.open(str(self._pdf_path))
            try:

                def _on_progress(cur: int, tot: int, msg: str) -> None:
                    self.progress.emit(cur, tot, msg)

                results = engine.recognize_document(doc, on_progress=_on_progress)
                engine.save_ocr_layer(doc, results, self._output_path)
            finally:
                doc.close()
            self.finished.emit(results)
        except Exception as exc:
            logger.error("OCRWorker falhou: %s", exc, exc_info=True)
            self.error.emit(str(exc))


class BatchWorker(QThread):
    """Executa BatchProcessor.run() em thread separada."""

    finished = pyqtSignal(object)  # BatchReport
    progress = pyqtSignal(int, int, str)
    error = pyqtSignal(str)

    def __init__(
        self,
        input_dir: Path,
        output_dir: Path,
        operation_name: str = "metadata",
        use_gpu: bool = True,
    ) -> None:
        super().__init__()
        self._input_dir = input_dir
        self._output_dir = output_dir
        self._operation_name = operation_name
        self._use_gpu = use_gpu

    def run(self) -> None:
        try:
            processor = BatchProcessor(self._output_dir)
            operation = self._build_operation()

            def _on_progress(cur: int, tot: int, fname: str) -> None:
                self.progress.emit(cur, tot, fname)

            report = processor.run(self._input_dir, operation, on_progress=_on_progress)
            self.finished.emit(report)
        except Exception as exc:
            logger.error("BatchWorker falhou: %s", exc, exc_info=True)
            self.error.emit(str(exc))

    def _build_operation(self):
        if self._operation_name == "ocr":
            use_gpu = self._use_gpu

            def _ocr_op(doc: fitz.Document, output_path: Path) -> str:
                engine = OCREngine(use_gpu=use_gpu)
                results = engine.recognize_document(doc)
                engine.save_ocr_layer(doc, results, output_path)
                return f"{len(results)} páginas com OCR"

            return _ocr_op

        if self._operation_name.startswith("rotate_"):
            angle = int(self._operation_name.split("_")[1])

            def _rotate_op(doc: fitz.Document, output_path: Path) -> str:
                from core.pdf_rotator import PDFRotator

                result = PDFRotator().rotate_all(doc, angle, output_path)
                return f"{result.pages_rotated} paginas rotacionadas {angle}°"

            return _rotate_op

        def _meta_op(doc: fitz.Document, output_path: Path) -> str:
            meta = PDFMetadata().read(doc)
            title = meta.title[:40] if meta.title else "(sem título)"
            return f"título='{title}'"

        return _meta_op


class MergeWorker(QThread):
    finished = pyqtSignal(object)  # MergeResult
    progress = pyqtSignal(int, int, str)
    error = pyqtSignal(str)

    def __init__(self, entries: list[MergeEntry], output_path: Path, parent=None) -> None:
        super().__init__(parent)
        self._entries = entries
        self._output_path = output_path

    def run(self) -> None:
        try:
            result = PDFMerger().merge(
                self._entries,
                self._output_path,
                on_progress=lambda c, t, n: self.progress.emit(c, t, n),
            )
            self.finished.emit(result)
        except Exception as exc:
            logger.error("MergeWorker falhou: %s", exc, exc_info=True)
            self.error.emit(str(exc))


class SplitWorker(QThread):
    finished = pyqtSignal(object)  # SplitResult
    error = pyqtSignal(str)

    def __init__(
        self,
        pdf_path: Path,
        mode: str,
        output_dir: Path,
        base_name: str,
        ranges: list[tuple[int, int]] | None = None,
        max_mb: float = 10.0,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._pdf_path = pdf_path
        self._mode = mode
        self._output_dir = output_dir
        self._base_name = base_name
        self._ranges = ranges
        self._max_mb = max_mb

    def run(self) -> None:
        try:
            doc = fitz.open(str(self._pdf_path))
            try:
                splitter = PDFSplitter()
                if self._mode == "range" and self._ranges:
                    result = splitter.split_by_range(
                        doc, self._ranges, self._output_dir, self._base_name
                    )
                elif self._mode == "size":
                    result = splitter.split_by_size(
                        doc, self._max_mb, self._output_dir, self._base_name
                    )
                else:
                    result = splitter.split_by_bookmarks(doc, self._output_dir, self._base_name)
            finally:
                doc.close()
            self.finished.emit(result)
        except Exception as exc:
            logger.error("SplitWorker falhou: %s", exc, exc_info=True)
            self.error.emit(str(exc))


class CompressWorker(QThread):
    finished = pyqtSignal(object)  # CompressResult
    error = pyqtSignal(str)

    def __init__(self, pdf_path: Path, output_path: Path, profile: str, parent=None) -> None:
        super().__init__(parent)
        self._pdf_path = pdf_path
        self._output_path = output_path
        self._profile = profile

    def run(self) -> None:
        try:
            doc = fitz.open(str(self._pdf_path))
            try:
                result = PDFCompressor().compress(doc, self._output_path, self._profile)
            finally:
                doc.close()
            self.finished.emit(result)
        except Exception as exc:
            logger.error("CompressWorker falhou: %s", exc, exc_info=True)
            self.error.emit(str(exc))


class SignatureWorker(QThread):
    finished = pyqtSignal(object)  # list[SignatureRegion]
    error = pyqtSignal(str)

    def __init__(self, pdf_path: Path, parent=None) -> None:
        super().__init__(parent)
        self._pdf_path = pdf_path

    def run(self) -> None:
        try:
            doc = fitz.open(str(self._pdf_path))
            try:
                regions = SignatureHandler().detect_signatures(doc)
            finally:
                doc.close()
            self.finished.emit(regions)
        except Exception as exc:
            logger.error("SignatureWorker falhou: %s", exc, exc_info=True)
            self.error.emit(str(exc))


class ReinsertWorker(QThread):
    finished = pyqtSignal(bool)
    error = pyqtSignal(str)

    def __init__(
        self,
        pdf_path: Path,
        region: SignatureRegion,
        image_path: Path,
        output_path: Path,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._pdf_path = pdf_path
        self._region = region
        self._image_path = image_path
        self._output_path = output_path

    def run(self) -> None:
        try:
            doc = fitz.open(str(self._pdf_path))
            try:
                ok = SignatureHandler().reinsert_signature(
                    doc, self._region, self._image_path, self._output_path
                )
            finally:
                doc.close()
            self.finished.emit(ok)
        except Exception as exc:
            logger.error("ReinsertWorker falhou: %s", exc, exc_info=True)
            self.error.emit(str(exc))


class ClassifyWorker(QThread):
    finished = pyqtSignal(object)  # ClassificationResult
    error = pyqtSignal(str)

    def __init__(self, pdf_path: Path, parent=None) -> None:
        super().__init__(parent)
        self._pdf_path = pdf_path

    def run(self) -> None:
        try:
            doc = fitz.open(str(self._pdf_path))
            try:
                result = DocumentClassifier().classify(doc)
            finally:
                doc.close()
            self.finished.emit(result)
        except Exception as exc:
            logger.error("ClassifyWorker falhou: %s", exc, exc_info=True)
            self.error.emit(str(exc))


class ClassifyBatchWorker(QThread):
    finished = pyqtSignal(object)  # list[tuple[str, ClassificationResult]]
    progress = pyqtSignal(int, int, str)
    error = pyqtSignal(str)

    def __init__(self, folder: Path, parent=None) -> None:
        super().__init__(parent)
        self._folder = folder

    def run(self) -> None:
        try:
            pdfs = sorted(self._folder.glob("*.pdf"))
            if not pdfs:
                self.finished.emit([])
                return

            classifier = DocumentClassifier()
            results: list[tuple[str, ClassificationResult]] = []

            for i, pdf_path in enumerate(pdfs):
                self.progress.emit(i + 1, len(pdfs), pdf_path.name)
                doc = fitz.open(str(pdf_path))
                try:
                    result = classifier.classify(doc)
                finally:
                    doc.close()
                results.append((pdf_path.name, result))

            self.finished.emit(results)
        except Exception as exc:
            logger.error("ClassifyBatchWorker falhou: %s", exc, exc_info=True)
            self.error.emit(str(exc))


class SecurityWorker(QThread):
    finished = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(
        self,
        mode: str,
        input_path: Path,
        output_path: Path,
        password: str,
        owner_password: str | None = None,
        permissions: int | None = None,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._mode = mode
        self._input_path = input_path
        self._output_path = output_path
        self._password = password
        self._owner_password = owner_password
        self._permissions = permissions

    def run(self) -> None:
        try:
            from core.pdf_security import PDFSecurity

            security = PDFSecurity()
            if self._mode == "encrypt":
                kwargs = {
                    "input_path": self._input_path,
                    "output_path": self._output_path,
                    "user_password": self._password,
                }
                if self._owner_password:
                    kwargs["owner_password"] = self._owner_password
                if self._permissions is not None:
                    kwargs["permissions"] = self._permissions
                result = security.encrypt(**kwargs)
            else:
                result = security.decrypt(
                    self._input_path,
                    self._output_path,
                    self._password,
                )
            self.finished.emit(result)
        except Exception as exc:
            logger.error("SecurityWorker falhou: %s", exc)
            self.error.emit(str(exc))


class ImageConvertWorker(QThread):
    finished = pyqtSignal(object)
    progress = pyqtSignal(int, int, str)
    error = pyqtSignal(str)

    def __init__(
        self,
        mode: str,
        input_path: Path | None = None,
        output_path: Path | None = None,
        output_dir: Path | None = None,
        image_paths: list[Path] | None = None,
        fmt: str = "png",
        dpi: int = 150,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._mode = mode
        self._input_path = input_path
        self._output_path = output_path
        self._output_dir = output_dir
        self._image_paths = image_paths or []
        self._fmt = fmt
        self._dpi = dpi

    def run(self) -> None:
        try:
            from core.pdf_image_converter import PDFImageConverter

            converter = PDFImageConverter()
            if self._mode == "pdf_to_images":
                result = converter.pdf_to_images(
                    self._input_path,
                    self._output_dir,
                    fmt=self._fmt,
                    dpi=self._dpi,
                )
            else:
                result = converter.images_to_pdf(
                    self._image_paths,
                    self._output_path,
                )
            self.finished.emit(result)
        except Exception as exc:
            logger.error("ImageConvertWorker falhou: %s", exc)
            self.error.emit(str(exc))


class WatermarkWorker(QThread):
    finished = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(
        self,
        mode: str,
        input_path: Path,
        output_path: Path,
        config=None,
        image_path: Path | None = None,
        opacity: float = 0.3,
        scale: float = 1.0,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._mode = mode
        self._input_path = input_path
        self._output_path = output_path
        self._config = config
        self._image_path = image_path
        self._opacity = opacity
        self._scale = scale

    def run(self) -> None:
        try:
            from core.pdf_watermark import PDFWatermark

            wm = PDFWatermark()
            if self._mode == "text":
                result = wm.apply_text(
                    self._input_path,
                    self._output_path,
                    self._config,
                )
            else:
                result = wm.apply_image(
                    self._input_path,
                    self._output_path,
                    self._image_path,
                    opacity=self._opacity,
                    scale=self._scale,
                )
            self.finished.emit(result)
        except Exception as exc:
            logger.error("WatermarkWorker falhou: %s", exc)
            self.error.emit(str(exc))


class ReorderWorker(QThread):
    finished = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(
        self,
        mode: str,
        input_path: Path,
        output_path: Path,
        new_order: list[int] | None = None,
        pages_to_delete: list[int] | None = None,
        page_index: int = 0,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._mode = mode
        self._input_path = input_path
        self._output_path = output_path
        self._new_order = new_order or []
        self._pages_to_delete = pages_to_delete or []
        self._page_index = page_index

    def run(self) -> None:
        try:
            from core.pdf_page_organizer import PDFPageOrganizer

            org = PDFPageOrganizer()
            if self._mode == "reorder":
                result = org.reorder(
                    self._input_path,
                    self._output_path,
                    self._new_order,
                )
            elif self._mode == "delete":
                result = org.delete_pages(
                    self._input_path,
                    self._output_path,
                    self._pages_to_delete,
                )
            else:
                result = org.duplicate_page(
                    self._input_path,
                    self._output_path,
                    self._page_index,
                )
            self.finished.emit(result)
        except Exception as exc:
            logger.error("ReorderWorker falhou: %s", exc)
            self.error.emit(str(exc))


# "A ação é o antídoto do desespero." — Joan Baez
