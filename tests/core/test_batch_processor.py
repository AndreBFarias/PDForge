from pathlib import Path

import fitz

from core.batch_processor import BatchProcessor, BatchReport


def _dummy_operation(doc: fitz.Document, output_path: Path) -> str:
    doc.save(str(output_path))
    return "OK"


def _failing_operation(doc: fitz.Document, output_path: Path) -> str:
    raise ValueError("Erro simulado")


def test_batch_process(sample_pdf_path, tmp_output_dir):
    input_dir = sample_pdf_path.parent
    output_dir = tmp_output_dir / "batch_out"
    processor = BatchProcessor(output_dir=output_dir)
    report = processor.run(
        input_dir=input_dir,
        operation=_dummy_operation,
        file_list=[sample_pdf_path],
    )
    assert isinstance(report, BatchReport)
    assert report.total == 1
    assert report.succeeded == 1
    assert report.failed == 0
    assert report.success_rate == 100.0


def test_batch_empty_list(tmp_output_dir):
    output_dir = tmp_output_dir / "batch_empty"
    processor = BatchProcessor(output_dir=output_dir)
    report = processor.run(
        input_dir=tmp_output_dir,
        operation=_dummy_operation,
        file_list=[],
    )
    assert report.total == 0
    assert report.succeeded == 0
    assert report.failed == 0


def test_batch_invalid_file(tmp_output_dir):
    fake_pdf = tmp_output_dir / "fake.pdf"
    fake_pdf.write_text("não é um pdf")
    output_dir = tmp_output_dir / "batch_invalid"
    processor = BatchProcessor(output_dir=output_dir)
    report = processor.run(
        input_dir=tmp_output_dir,
        operation=_dummy_operation,
        file_list=[fake_pdf],
    )
    assert report.total == 1
    assert report.failed == 1
    assert not report.results[0].success


def test_batch_with_progress(sample_pdf_path, tmp_output_dir):
    output_dir = tmp_output_dir / "batch_progress"
    processor = BatchProcessor(output_dir=output_dir)
    progress_calls = []

    def on_progress(cur: int, total: int, name: str) -> None:
        progress_calls.append((cur, total, name))

    processor.run(
        input_dir=sample_pdf_path.parent,
        operation=_dummy_operation,
        file_list=[sample_pdf_path],
        on_progress=on_progress,
    )
    assert len(progress_calls) == 1
    assert progress_calls[0][0] == 1
