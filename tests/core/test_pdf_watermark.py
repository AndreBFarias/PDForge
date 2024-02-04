import pytest

from core.pdf_watermark import (
    PDFWatermark,
    WatermarkConfig,
)

try:
    from PIL import Image

    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not PIL_AVAILABLE,
    reason="Pillow não instalado",
)


def test_apply_text_watermark(
    sample_pdf_path,
    tmp_output_dir,
):
    wm = PDFWatermark()
    config = WatermarkConfig(
        text="CONFIDENCIAL",
        opacity=0.5,
    )
    output = tmp_output_dir / "wm_text.pdf"
    result = wm.apply_text(
        sample_pdf_path,
        output,
        config,
    )
    assert result.success
    assert output.exists()
    assert result.pages_processed == 1


def test_apply_image_watermark(
    sample_pdf_path,
    tmp_output_dir,
):
    img_path = tmp_output_dir / "wm_logo.png"
    img = Image.new(
        "RGBA",
        (100, 100),
        (255, 0, 0, 128),
    )
    img.save(str(img_path))

    wm = PDFWatermark()
    output = tmp_output_dir / "wm_image.pdf"
    result = wm.apply_image(
        sample_pdf_path,
        output,
        img_path,
        opacity=0.4,
    )
    assert result.success
    assert output.exists()


def test_watermark_diagonal(
    sample_pdf_path,
    tmp_output_dir,
):
    wm = PDFWatermark()
    config = WatermarkConfig(
        text="RASCUNHO",
        rotation=-45.0,
        opacity=0.3,
    )
    output = tmp_output_dir / "wm_diag.pdf"
    result = wm.apply_text(
        sample_pdf_path,
        output,
        config,
    )
    assert result.success


def test_watermark_tile(
    sample_pdf_path,
    tmp_output_dir,
):
    wm = PDFWatermark()
    config = WatermarkConfig(
        text="DRAFT",
        position="tile",
        font_size=24,
        opacity=0.2,
    )
    output = tmp_output_dir / "wm_tile.pdf"
    result = wm.apply_text(
        sample_pdf_path,
        output,
        config,
    )
    assert result.success


def test_watermark_empty_text(
    sample_pdf_path,
    tmp_output_dir,
):
    wm = PDFWatermark()
    config = WatermarkConfig(text="")
    output = tmp_output_dir / "wm_empty.pdf"
    result = wm.apply_text(
        sample_pdf_path,
        output,
        config,
    )
    assert not result.success
