"""
PDFForge — Entry point CLI.

Uso:
    python main.py
    python main.py caminho/arquivo.pdf
    python main.py --no-gpu caminho/arquivo.pdf
    python main.py --batch caminho/diretorio/
    python main.py --debug caminho/arquivo.pdf
"""

import sys
from pathlib import Path

import click

# Adiciona o diretório do projeto ao sys.path para imports absolutos
sys.path.insert(0, str(Path(__file__).parent))

from utils.file_utils import setup_logging


@click.command()
@click.argument("path", required=False, type=click.Path(exists=False))
@click.option("--no-gpu", is_flag=True, default=False, help="Desabilita aceleração GPU/CUDA.")
@click.option("--debug", is_flag=True, default=False, help="Habilita logs de debug.")
@click.option(
    "--batch",
    is_flag=True,
    default=False,
    help="Modo lote: PATH deve ser um diretório de PDFs.",
)
def main(path: str | None, no_gpu: bool, debug: bool, batch: bool) -> None:
    """PDFForge — Manipulação avançada de PDFs via GUI."""
    logger = setup_logging(debug=debug)
    logger.info("PDFForge iniciando (gpu=%s, debug=%s, batch=%s)", not no_gpu, debug, batch)

    if batch:
        _run_batch_cli(path, no_gpu, logger)
        return

    _run_gui(path, use_gpu=not no_gpu)


def _run_gui(path: str | None, use_gpu: bool) -> None:
    from PyQt6.QtWidgets import QApplication
    from ui.main_window import MainWindow

    initial_pdf = None
    if path:
        p = Path(path)
        if p.is_file() and p.suffix.lower() == ".pdf":
            initial_pdf = p
        else:
            click.echo(f"Aviso: '{path}' não é um PDF válido. Iniciando sem arquivo.", err=True)

    app = QApplication(sys.argv)
    window = MainWindow(initial_pdf=initial_pdf, use_gpu=use_gpu)
    window.show()
    sys.exit(app.exec())


def _run_batch_cli(path: str | None, no_gpu: bool, logger) -> None:
    """Modo lote sem TUI — imprime relatório no terminal."""
    if not path:
        click.echo("Erro: forneça um diretório para o modo --batch.", err=True)
        sys.exit(1)

    input_dir = Path(path)
    if not input_dir.is_dir():
        click.echo(f"Erro: '{path}' não é um diretório.", err=True)
        sys.exit(1)

    output_dir = input_dir.parent / "data_output"

    from core.batch_processor import BatchProcessor
    from core.metadata import PDFMetadata

    processor = BatchProcessor(output_dir)

    def extract_op(doc, output_path: Path) -> str:
        meta = PDFMetadata().read(doc)
        return f"título='{meta.title[:40]}'"

    def on_progress(current: int, total: int, filename: str) -> None:
        click.echo(f"  [{current}/{total}] {filename}")

    click.echo(f"Processando PDFs em: {input_dir}")
    report = processor.run(input_dir, extract_op, on_progress)
    click.echo(f"\n{report.summary()}")

    for result in report.results:
        status = "OK  " if result.success else "ERRO"
        click.echo(f"  {status} | {result.path.name:<40} | {result.duration_s:.2f}s | {result.message}")


# "A mente que se abre a uma nova ideia jamais voltará ao seu tamanho original." — Oliver Wendell Holmes
if __name__ == "__main__":
    main()
