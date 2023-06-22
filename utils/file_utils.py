import logging
import logging.handlers
from pathlib import Path

from config.settings import LOG_DIR, LOG_FORMAT, LOG_DATE_FORMAT, LOG_BACKUP_COUNT


def setup_logging(debug: bool = False) -> logging.Logger:
    """
    Configura logging rotacionado por dia.
    Retorna o logger raiz da aplicação.
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOG_DIR / "pdfforge.log"

    root = logging.getLogger("pdfforge")
    root.setLevel(logging.DEBUG if debug else logging.INFO)

    if root.handlers:
        return root

    # Handler para arquivo — rotação diária
    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=log_file,
        when="midnight",
        backupCount=LOG_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT))
    root.addHandler(file_handler)

    # Handler para console (stderr) apenas em modo debug
    if debug:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT))
        root.addHandler(console_handler)

    return root


def ensure_output_path(input_path: Path, output_dir: Path, suffix: str = "_edited") -> Path:
    """
    Deriva caminho de saída a partir do caminho de entrada.
    Garante que o diretório de saída exista.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = input_path.stem + suffix
    return output_dir / (stem + input_path.suffix)


def human_size(num_bytes: int) -> str:
    """Converte bytes em string legível (KB, MB, GB)."""
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(num_bytes) < 1024.0:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024.0  # type: ignore[assignment]
    return f"{num_bytes:.1f} PB"


def list_pdfs(directory: Path) -> list[Path]:
    """Lista todos os PDFs em um diretório (não recursivo)."""
    return sorted(directory.glob("*.pdf"))


def validate_pdf_path(path: Path) -> None:
    """
    Valida que o caminho aponta para um PDF legível.
    Lança ValueError com mensagem descritiva em caso de falha.
    """
    if not path.exists():
        raise ValueError(f"Arquivo não encontrado: {path}")
    if not path.is_file():
        raise ValueError(f"Não é um arquivo: {path}")
    if path.suffix.lower() != ".pdf":
        raise ValueError(f"Extensão inválida (esperado .pdf): {path.suffix}")
    if path.stat().st_size == 0:
        raise ValueError(f"Arquivo vazio: {path}")
