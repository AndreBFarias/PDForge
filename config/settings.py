import json
import logging
from pathlib import Path
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)

# Paleta Dracula — usada tanto no CSS Textual quanto em Rich markup
DRACULA = {
    "background": "#282a36",
    "current_line": "#44475a",
    "foreground": "#f8f8f2",
    "comment": "#6272a4",
    "cyan": "#8be9fd",
    "green": "#50fa7b",
    "orange": "#ffb86c",
    "pink": "#ff79c6",
    "purple": "#bd93f9",
    "red": "#ff5555",
    "yellow": "#f1fa8c",
}

# Diretórios de trabalho
APP_DIR = Path.home() / ".pdfforge"
LOG_DIR = APP_DIR / "logs"
CONFIG_FILE = APP_DIR / "config.json"
CACHE_DIR = APP_DIR / "cache"

# Limites de hardware (RTX 3050 4GB VRAM)
GPU_VRAM_LIMIT_GB = 3.5       # Margem de segurança de 0.5GB
OCR_BATCH_MAX_PAGES = 2       # Máximo de páginas OCR simultâneas
OCR_IMAGE_SCALE = 2.0         # Fator de escala para rasterização de páginas

# Limiares de detecção
OCR_TEXT_MIN_CHARS = 10       # Abaixo disso, página é tratada como imagem
PDF_MAX_PREVIEW_SIZE_MB = 50  # PDFs maiores que isso: preview desabilitado

# Logging
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_BACKUP_COUNT = 7          # Manter 7 dias de logs

APP_VERSION = "0.1.0"
APP_NAME = "PDFForge"


@dataclass
class UserPreferences:
    last_file: str = ""
    last_dir: str = ""
    use_gpu: bool = True
    debug_mode: bool = False
    ocr_languages: list[str] = field(default_factory=lambda: ["pt", "en"])
    theme: str = "dracula"

    @classmethod
    def load(cls) -> "UserPreferences":
        if not CONFIG_FILE.exists():
            return cls()
        try:
            data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
        except Exception as exc:
            logger.warning("Falha ao carregar config: %s — usando padrões", exc)
            return cls()

    def save(self) -> None:
        APP_DIR.mkdir(parents=True, exist_ok=True)
        CONFIG_FILE.write_text(
            json.dumps(asdict(self), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        logger.debug("Preferências salvas em %s", CONFIG_FILE)


class Settings:
    """Singleton de configuração global da aplicação."""

    _instance: "Settings | None" = None

    def __new__(cls) -> "Settings":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._initialized = True
        self.prefs = UserPreferences.load()
        self._setup_directories()

    def _setup_directories(self) -> None:
        for directory in (APP_DIR, LOG_DIR, CACHE_DIR):
            directory.mkdir(parents=True, exist_ok=True)

    def save(self) -> None:
        self.prefs.save()

    # --- Viewer inline ---
    PDF_VIEWER_DEFAULT_SCALE: float = 1.0
    PDF_VIEWER_MAX_SCALE: float = 4.0
    PDF_VIEWER_MIN_SCALE: float = 0.25

    # --- Compressao ---
    COMPRESS_DEFAULT_PROFILE: str = "medio"

    # --- Classificador ML ---
    CLASSIFIER_MODEL_PATH: Path = Path.home() / ".pdfforge" / "models" / "classifier.pkl"

    # --- Assinaturas ---
    SIGNATURE_EXTRACT_SCALE: float = 3.0
    SIGNATURE_TEMP_DIR: Path = Path.home() / ".pdfforge" / "tmp" / "signatures"
