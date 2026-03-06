# Sprint 03 — Core ML/CV (compressor, signature_handler, document_classifier)

**Diretório:** `/home/andrefarias/Desenvolvimento/PDForge`
**Conta git:** `AndreBFarias` / `andre.dsbf@gmail.com`
**Pré-requisito:** Sprint 02 concluído e commitado.

Execute todas as tasks direto, sem criar task list, sem confirmar etapas, sem parar a não ser em erro real.

---

## Contexto dos módulos existentes

Padrões do codebase a seguir:
- `logging.getLogger("pdfforge")`, nunca `print()`
- Dataclasses com type hints para resultados
- Error handling explícito com `logger.error()`, nunca silent failures
- PT-BR em logs e mensagens
- Zero comentários desnecessários dentro do código
- Assinatura filosófica no final de cada arquivo: `# "frase." — Autor`

---

## Task 1 — core/pdf_compressor.py

Criar `core/pdf_compressor.py` com:

**Enum `PageContentType`**: `TEXT_ONLY`, `IMAGE_HEAVY`, `MIXED`, `SCANNED`

**Dict `COMPRESS_PROFILES`** com 3 perfis hardcoded:
- `"leve"`: dpi=150, jpeg_quality=85, deflate_images=False
- `"medio"`: dpi=120, jpeg_quality=72, deflate_images=True
- `"agressivo"`: dpi=96, jpeg_quality=55, deflate_images=True

Cada perfil é um `dict` com as chaves acima.

**Classe `PDFCompressor`** com 3 métodos:

1. `analyze_content_type(doc: fitz.Document, sample_pages: int = 5) -> PageContentType`
   - Amostra até `sample_pages` páginas igualmente espaçadas
   - Para cada página: extrai texto com `page.get_text()`, conta imagens com `page.get_images()`
   - Calcula razão texto/imagem na amostra
   - Usa `cv2` para analisar variância de pixel (indicador de página scanned vs digital):
     - Renderiza página em pixmap via `fitz.Pixmap`, converte para numpy array
     - `cv2.Laplacian` + `var()` — variância baixa (<50) sugere scan
   - Retorna o tipo adequado:
     - Sem imagens e com texto: `TEXT_ONLY`
     - Variância média baixa: `SCANNED`
     - Mais imagens que texto: `IMAGE_HEAVY`
     - Caso contrário: `MIXED`

2. `compress(doc: fitz.Document, output_path: Path, profile: str = "medio") -> CompressResult`
   - Valida que `profile` existe em `COMPRESS_PROFILES`, erro explícito se não
   - Para cada página, reprocessa imagens: extrai via `fitz.Pixmap`, recomprime com
     `cv2.imencode(".jpg", img_array, [cv2.IMWRITE_JPEG_QUALITY, quality])`
     e reinserire via `page.insert_image(rect, stream=jpeg_bytes)`
   - Salva com `doc.save(output_path, deflate=deflate_images, garbage=4, clean=True)`
   - Retorna `CompressResult`

3. `get_compression_estimate(doc: fitz.Document, profile: str) -> dict[str, float]`
   - Retorna `{"original_mb": float, "estimated_mb": float, "reduction_pct": float}`
   - Estimativa heurística: TEXT_ONLY reduz ~5%, SCANNED ~45%, IMAGE_HEAVY ~35%, MIXED ~20%
   - Multiplica pelo fator do perfil: leve=0.5, medio=1.0, agressivo=1.5

**Dataclass `CompressResult`**:
```python
@dataclass
class CompressResult:
    output_path: Path
    original_size_mb: float
    compressed_size_mb: float
    reduction_pct: float
    content_type: PageContentType
    profile_used: str
    success: bool = True
    error: str = ""
```

Import guard para cv2: `try: import cv2; CV2_AVAILABLE = True except ImportError: CV2_AVAILABLE = False`
Se cv2 não disponível, `analyze_content_type` usa só heurística texto/imagem sem variância.

---

## Task 2 — core/signature_handler.py

Criar `core/signature_handler.py` com:

**Dataclass `SignatureRegion`**:
```python
@dataclass
class SignatureRegion:
    page_index: int
    rect: fitz.Rect
    image_index: int
    bbox: tuple[float, float, float, float]
    confidence: float = 0.0
    label: str = ""
```

**Classe `SignatureHandler`** com 3 métodos:

1. `detect_signatures(doc: fitz.Document) -> list[SignatureRegion]`
   - Para cada página, chama `page.get_images(full=True)`
   - Para cada imagem na página: obtém `fitz.Pixmap` da imagem
   - Converte para numpy array e usa `cv2.findContours` para detectar bordas/contornos
   - Heurística de assinatura: imagem com aspect ratio entre 2:1 e 8:1 (mais larga que alta),
     área menor que 20% da página, com contornos irregulares (não retangulares)
   - `confidence` baseada no quanto os critérios acima são satisfeitos (0.0–1.0)
   - Retorna apenas regiões com `confidence >= 0.4`
   - Import guard para cv2, se não disponível usa heurística só por tamanho/posição

2. `extract_signature(doc: fitz.Document, region: SignatureRegion, output_path: Path, scale: float = 3.0) -> Path`
   - Renderiza a página na escala indicada via `fitz.Matrix(scale, scale)`
   - Usa `page.get_pixmap(matrix=matrix, clip=region.rect)`
   - Salva como PNG em `output_path`
   - Retorna `output_path`

3. `reinsert_signature(doc: fitz.Document, region: SignatureRegion, image_path: Path, output_path: Path) -> bool`
   - Abre `image_path` como bytes
   - Na página `region.page_index`, usa `page.insert_image(region.rect, filename=str(image_path))`
   - Salva doc em `output_path`
   - Retorna True em sucesso, False em falha (com log de erro)

---

## Task 3 — core/document_classifier.py

Criar `core/document_classifier.py` com:

**Constante `HEURISTIC_RULES`** — dict mapeando tipo de documento a lista de keywords PT-BR:
```python
HEURISTIC_RULES = {
    "contrato": ["cláusula", "contratante", "contratado", "objeto do contrato", "vigência"],
    "nota_fiscal": ["CNPJ", "valor total", "NF-e", "nota fiscal", "tributos"],
    "procuracao": ["outorgante", "outorgado", "poderes", "instrumento particular"],
    "laudo": ["laudo", "perícia", "parecer técnico", "conclusão", "examinado"],
    "relatorio": ["relatório", "período", "resultados", "conclusões", "recomendações"],
    "ata": ["ata", "reunião", "presentes", "deliberou", "aprovado por unanimidade"],
    "curriculo": ["formação", "experiência profissional", "habilidades", "objetivo profissional"],
}
```

**Dataclass `ClassificationResult`**:
```python
@dataclass
class ClassificationResult:
    doc_type: str
    confidence: float
    method: str  # "ml" ou "heuristic"
    scores: dict[str, float] = field(default_factory=dict)
```

**Classe `DocumentClassifier`** com 2 métodos:

1. `classify(doc: fitz.Document) -> ClassificationResult`
   - Extrai texto das primeiras 3 páginas concatenado
   - Tenta carregar modelo sklearn do path em `Settings().CLASSIFIER_MODEL_PATH`
   - Se modelo existe:
     - Carrega `.pkl` com `joblib.load()` (import guard, lazy)
     - Espera objeto com `.predict()` e `.predict_proba()` treinado com TF-IDF + LinearSVC
     - Retorna resultado com `method="ml"`
   - Se modelo não existe ou falha: usa fallback heurístico
     - Para cada tipo em `HEURISTIC_RULES`, conta keywords presentes no texto (case-insensitive)
     - Score = matches / total_keywords_do_tipo
     - Tipo vencedor = maior score; se todos zero, retorna `"indefinido"` com confidence 0.0
     - Retorna resultado com `method="heuristic"`

2. `classify_batch(docs: list[tuple[Path, fitz.Document]]) -> list[tuple[Path, ClassificationResult]]`
   - Itera sobre a lista e chama `classify()` para cada doc
   - Retorna lista de tuplas `(path, result)`
   - Log de progresso a cada documento

---

## Commit final do sprint

```bash
git add core/pdf_compressor.py core/signature_handler.py core/document_classifier.py
git commit -m "feat: módulos core de compressão, detecção de assinaturas e classificação de documentos"
```

**Próximo sprint:** `sprint-04.md`
