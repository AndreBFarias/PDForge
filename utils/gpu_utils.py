import logging
from dataclasses import dataclass

logger = logging.getLogger("pdfforge.gpu")

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logger.warning("torch não disponível — sem suporte CUDA")

try:
    import GPUtil
    GPUTIL_AVAILABLE = True
except ImportError:
    GPUTIL_AVAILABLE = False
    logger.debug("GPUtil não disponível — stats de VRAM via torch")


@dataclass
class GPUStats:
    available: bool
    name: str
    vram_total_mb: float
    vram_used_mb: float
    vram_free_mb: float
    utilization_pct: float
    temperature_c: float

    @property
    def vram_used_pct(self) -> float:
        if self.vram_total_mb == 0:
            return 0.0
        return (self.vram_used_mb / self.vram_total_mb) * 100

    @property
    def is_safe_to_use(self) -> bool:
        """Seguro se < 85% da VRAM está em uso."""
        return self.available and self.vram_used_pct < 85.0


def _stats_via_gputil() -> GPUStats | None:
    if not GPUTIL_AVAILABLE:
        return None
    try:
        gpus = GPUtil.getGPUs()
        if not gpus:
            return None
        gpu = gpus[0]
        return GPUStats(
            available=True,
            name=gpu.name,
            vram_total_mb=gpu.memoryTotal,
            vram_used_mb=gpu.memoryUsed,
            vram_free_mb=gpu.memoryFree,
            utilization_pct=gpu.load * 100,
            temperature_c=gpu.temperature,
        )
    except Exception as exc:
        logger.debug("GPUtil falhou: %s", exc)
        return None


def _stats_via_torch() -> GPUStats | None:
    if not TORCH_AVAILABLE or not torch.cuda.is_available():
        return None
    try:
        props = torch.cuda.get_device_properties(0)
        total = props.total_memory / (1024 ** 2)
        reserved = torch.cuda.memory_reserved(0) / (1024 ** 2)
        allocated = torch.cuda.memory_allocated(0) / (1024 ** 2)
        used = max(reserved, allocated)
        return GPUStats(
            available=True,
            name=props.name,
            vram_total_mb=total,
            vram_used_mb=used,
            vram_free_mb=total - used,
            utilization_pct=0.0,       # torch não expõe utilização do shader
            temperature_c=0.0,
        )
    except Exception as exc:
        logger.debug("torch CUDA stats falhou: %s", exc)
        return None


def _stats_unavailable() -> GPUStats:
    return GPUStats(
        available=False,
        name="Nenhuma GPU detectada",
        vram_total_mb=0.0,
        vram_used_mb=0.0,
        vram_free_mb=0.0,
        utilization_pct=0.0,
        temperature_c=0.0,
    )


class GPUMonitor:
    """Monitor de GPU com fallback gracioso para ambientes sem CUDA."""

    def __init__(self) -> None:
        stats = self.get_stats()
        if stats.available:
            logger.info("GPU detectada: %s (%.0f MB VRAM)", stats.name, stats.vram_total_mb)
        else:
            logger.info("Sem GPU CUDA disponível — modo CPU")

    def get_stats(self) -> GPUStats:
        return _stats_via_gputil() or _stats_via_torch() or _stats_unavailable()

    @property
    def cuda_available(self) -> bool:
        return TORCH_AVAILABLE and torch.cuda.is_available() if TORCH_AVAILABLE else False

    def clear_cache(self) -> None:
        """Libera cache de VRAM do PyTorch."""
        if self.cuda_available:
            torch.cuda.empty_cache()
            logger.debug("Cache CUDA liberado")
