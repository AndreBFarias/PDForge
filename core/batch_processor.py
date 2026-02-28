import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import fitz

from utils.file_utils import list_pdfs, ensure_output_path

logger = logging.getLogger("pdfforge.batch")


@dataclass
class FileResult:
    path: Path
    success: bool
    duration_s: float
    message: str = ""
    output_path: Path | None = None


@dataclass
class BatchReport:
    total: int
    succeeded: int
    failed: int
    duration_s: float
    results: list[FileResult] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        return (self.succeeded / self.total * 100) if self.total > 0 else 0.0

    def summary(self) -> str:
        return (
            f"Lote concluído: {self.succeeded}/{self.total} arquivos"
            f" ({self.success_rate:.0f}% sucesso) em {self.duration_s:.1f}s"
        )


class BatchProcessor:
    """
    Processa múltiplos PDFs em lote com relatório detalhado.

    Uso típico:
        processor = BatchProcessor(output_dir=Path("data_output"))
        report = processor.run(
            input_dir=Path("data_input"),
            operation=my_operation_fn,
            on_progress=update_ui,
        )
    """

    def __init__(self, output_dir: Path) -> None:
        self._output_dir = output_dir
        self._output_dir.mkdir(parents=True, exist_ok=True)

    def run(
        self,
        input_dir: Path,
        operation: Callable[[fitz.Document, Path], str | None],
        on_progress: Callable[[int, int, str], None] | None = None,
        file_list: list[Path] | None = None,
    ) -> BatchReport:
        """
        Itera sobre PDFs do diretório e aplica a função operation.

        Args:
            input_dir: diretório com PDFs de entrada.
            operation: função (doc, output_path) → mensagem opcional.
            on_progress: callback (current, total, filename).
            file_list: se fornecido, usa esta lista ao invés do diretório.
        """
        files = file_list or list_pdfs(input_dir)
        total = len(files)
        results: list[FileResult] = []
        batch_start = time.monotonic()

        logger.info("Iniciando lote: %d arquivos em %s", total, input_dir)

        for idx, pdf_path in enumerate(files):
            if on_progress:
                on_progress(idx + 1, total, pdf_path.name)

            output_path = ensure_output_path(pdf_path, self._output_dir)
            result = self._process_one(pdf_path, output_path, operation)
            results.append(result)

        batch_duration = time.monotonic() - batch_start
        succeeded = sum(1 for r in results if r.success)
        report = BatchReport(
            total=total,
            succeeded=succeeded,
            failed=total - succeeded,
            duration_s=batch_duration,
            results=results,
        )
        logger.info(report.summary())
        return report

    def _process_one(
        self,
        pdf_path: Path,
        output_path: Path,
        operation: Callable[[fitz.Document, Path], str | None],
    ) -> FileResult:
        start = time.monotonic()
        try:
            doc = fitz.open(str(pdf_path))
            message = operation(doc, output_path) or "OK"
            doc.close()
            return FileResult(
                path=pdf_path,
                success=True,
                duration_s=time.monotonic() - start,
                message=message,
                output_path=output_path,
            )
        except Exception as exc:
            logger.error("Falha ao processar %s: %s", pdf_path.name, exc, exc_info=True)
            return FileResult(
                path=pdf_path,
                success=False,
                duration_s=time.monotonic() - start,
                message=str(exc),
            )
