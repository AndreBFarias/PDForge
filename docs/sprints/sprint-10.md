# Sprint 10 — Correção de Bugs + Cobertura de Testes

## Visão Estratégica

Esta sprint é a fundação para todas as demais. Corrige bugs confirmados pela auditoria e preenche lacunas críticas de cobertura de testes. Sem esta base sólida, as features das sprints 11-14 herdariam os mesmos problemas.

**Dependências:** Nenhuma
**Impacto:** Estabilidade do core, confiança para refatorações futuras
**Estimativa:** ~400 LOC novas, 3-5 arquivos novos, 5 arquivos modificados

## Contexto Tecnico

### Estado atual
- 13 testes passando, 6 módulos com 0% de cobertura
- BUG-01 (OCR) é o mais grave: texto invisível posicionado em coordenada fixa
- BUG-02/03/05 (compressor) são code smells com risco de regressão
- Assinatura filosófica mal posicionada em font_detector.py

### Padrões a seguir
- Fixtures em `tests/conftest.py`: `sample_pdf_path`, `sample_multipage_path`, `tmp_output_dir`
- Logger: `logging.getLogger("pdfforge.submodulo")`
- Resultados: dataclass com campos `success`, `error`
- Testes: `python3 -m pytest tests/ -v --tb=short`

## Tasks

### Task 10.1 — Corrigir BUG-01: OCR layer positioning
**Arquivo:** `core/ocr_engine.py`
**Método:** `save_ocr_layer()`

Reescrever para posicionar texto sobre coordenadas reais:
1. Usar `reader.readtext(image, detail=1)` que retorna `[(bbox, text, confidence)]`
2. Para cada resultado, converter bbox (coordenadas de imagem) para coordenadas PDF
3. Inserir texto invisível na posição correta com fontsize proporcional ao bbox

Logica:
```python
for bbox, text, conf in results:
    # bbox e lista de 4 pontos [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
    x0 = min(p[0] for p in bbox) * (page.rect.width / img_width)
    y0 = min(p[1] for p in bbox) * (page.rect.height / img_height)
    x1 = max(p[0] for p in bbox) * (page.rect.width / img_width)
    y1 = max(p[1] for p in bbox) * (page.rect.height / img_height)
    fontsize = (y1 - y0) * 0.8
    page.insert_text(fitz.Point(x0, y1), text, fontsize=fontsize, color=(1,1,1), overlay=True)
```

### Task 10.2 — Corrigir BUG-05: RGBA para grayscale
**Arquivo:** `core/pdf_compressor.py`
**Método:** `analyze_content_type()` (linha ~78)

Adicionar tratamento explicito para 4 canais:
```python
if img_array.shape[2] == 4:
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGBA2GRAY)
elif img_array.shape[2] == 3:
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
else:
    gray = img_array
```

### Task 10.3 — Melhorar BUG-02: threshold Laplaciano
**Arquivo:** `core/pdf_compressor.py`
**Método:** `analyze_content_type()` (linha ~87)

Aumentar threshold de 50 para 100 (mais conservador) e adicionar log do valor:
```python
SCANNED_THRESHOLD = 100
logger.debug("Variância Laplaciana: %.2f (threshold: %d)", variance, SCANNED_THRESHOLD)
```

### Task 10.4 — Melhorar BUG-03: compressão de imagens
**Arquivo:** `core/pdf_compressor.py`
**Método:** `compress()` (linhas ~127-148)

Antes de inserir imagem comprimida, deletar a original:
```python
page.delete_image(xref)
page.insert_image(rect, stream=jpeg_bytes)
```

### Task 10.5 — Corrigir BUG-07: assinatura em font_detector.py
**Arquivo:** `core/font_detector.py`

Mover a assinatura filosófica (linha ~86) para o final do arquivo, após todos os métodos da classe.

### Task 10.6 — Criar testes para metadata
**Arquivo:** `tests/core/test_metadata.py`

Testes mínimos:
1. `test_read_metadata` — lê metadata de PDF de teste
2. `test_write_metadata` — escreve title/author e verifica
3. `test_metadata_empty_pdf` — PDF sem metadata retorna dict vazio/defaults

### Task 10.7 — Criar testes para font_detector
**Arquivo:** `tests/core/test_font_detector.py`

Testes mínimos:
1. `test_detect_fonts` — detecta fontes em PDF com texto
2. `test_detect_fonts_empty` — PDF sem texto retorna lista vazia
3. `test_get_dominant_font` — retorna fonte mais usada

### Task 10.8 — Criar testes para batch_processor
**Arquivo:** `tests/core/test_batch_processor.py`

Testes mínimos:
1. `test_batch_compress` — comprime lista de PDFs
2. `test_batch_empty_list` — lista vazia retorna resultado vazio
3. `test_batch_invalid_file` — arquivo inválido reporta erro sem crash

### Task 10.9 — Expandir testes de pdf_splitter
**Arquivo:** `tests/core/test_pdf_splitter.py`

Adicionar:
1. `test_split_by_size` — divide por tamanho máximo
2. `test_split_by_bookmarks` — divide por bookmarks (sem bookmarks = arquivo único)

### Task 10.10 — Expandir testes de pdf_editor
**Arquivo:** `tests/core/test_pdf_editor.py`

Adicionar:
1. `test_replace_multiple_terms` — múltiplos pares busca/substituição
2. `test_replace_case_sensitive` — busca case-sensitive

## Verificacao

```bash
QT_QPA_PLATFORM=offscreen python3 -m pytest tests/ -v --tb=short
ruff check .
```

## Commit

```
fix: corrige posicionamento OCR, bugs do compressor e expande cobertura de testes
```
