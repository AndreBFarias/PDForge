# Auditoria Externa — PDForge v1.0.0

**Data:** 2026-03-14
**Escopo:** Revisao completa de maturidade, bugs, arquitetura, gaps e recomendacoes

---

## 1. Resumo Executivo

O PDForge e uma ferramenta desktop PyQt6 para manipulacao avancada de PDFs no Linux, posicionada como alternativa ao PDF24. O projeto esta na v1.0.0 com ~5.500 LOC Python, 13 modulos core, 10 telas UI, 13 testes passando.

### Pontuacao de Maturidade (1-5)

| Eixo | Nota | Justificativa |
|------|------|---------------|
| Arquitetura | 4 | Separacao core/UI limpa, dataclasses, workers QThread |
| Qualidade de Codigo | 3.5 | Type hints, logging hierarquico, mas alguns code smells |
| Cobertura de Testes | 2 | 13 testes, 6 modulos sem cobertura alguma |
| Packaging | 2 | Scripts existem mas frageis, sem validacao |
| CI/CD | 2.5 | Pipeline basica, sem testes de packaging |
| Funcionalidades | 3 | Core solido, mas gaps criticos vs PDF24 |
| Documentacao | 3.5 | README, DEVGUIDE, CONTRIBUTING, CHANGELOG presentes |
| Seguranca | 1.5 | Sem protecao por senha, sem validacao de input em PDFs malformados |

**Media geral: 2.75/5 — Projeto funcional mas imaturo para distribuicao publica.**

---

## 2. Inventario de Bugs Confirmados

Todos os bugs foram verificados por leitura direta do codigo-fonte e/ou execucao de testes.

| ID | Sev. | Arquivo | Descricao | Verificacao |
|----|------|---------|-----------|-------------|
| BUG-01 | ALTO | `core/ocr_engine.py:121-127` | `save_ocr_layer` insere TODO o texto OCR em `Point(10,10)` com `fontsize=1`. Texto nao fica posicionado sobre o conteudo original. Selecao de texto em leitor PDF retorna tudo de um unico ponto | Confirmado por leitura direta |
| BUG-02 | MEDIO | `core/pdf_compressor.py:87` | Limiar Laplaciano = 50 para detectar SCANNED. Com scale 0.5, valores reais podem variar. Threshold nao calibrado com dados reais | Debatable — funciona em alguns cenarios mas pode classificar errado |
| BUG-03 | MEDIO | `core/pdf_compressor.py:146` | `page.insert_image(rect, stream=jpeg)` sobrepoe imagem JPEG sobre imagem original. Original permanece no PDF. `garbage=4` remove objetos nao referenciados, mas imagem original pode ainda ser referenciada | Compressao funcionou em teste (30.8%), mas mecanismo e fragil |
| BUG-04 | MEDIO | `core/pdf_splitter.py:63-74` | `split_by_size()` cria doc temporario + BytesIO para cada iteracao. O(n^2) em paginas. Com 50 paginas e 10KB max, levou 0.11s — performance aceitavel para volumes normais, mas degrada com PDFs grandes | Confirmado, impacto baixo na pratica |
| BUG-05 | BAIXO | `core/pdf_compressor.py:78` | `cv2.COLOR_RGB2GRAY` em array 4-channel (RGBA). OpenCV 4.x aceita e produz resultado correto, mas depende de comportamento nao documentado | Verificado: NAO causa crash, resultado identico a RGBA2GRAY |
| BUG-06 | BAIXO | `core/pdf_editor.py:80` | Fallback de baseline usa `rect.y1` (bottom do rect). Para `insert_text`, o ponto e interpretado como baseline. Posicionamento pode ficar ligeiramente deslocado | Code smell, impacto visual menor |
| BUG-07 | INFO | `core/font_detector.py:86` | Assinatura filosofica colocada entre metodos da classe (antes de `get_dominant_font`). Metodo esta dentro da classe (confirmado via AST). Code smell visual, sem impacto funcional | FALSO POSITIVO — verificado via ast.parse() |

---

## 3. Revisao Arquitetural

### 3.1 Camada Core (`core/`)
- 13 modulos com responsabilidade unica
- Padrao consistente: dataclass de resultado + metodo principal
- Logging hierarquico (`pdfforge.modulo`)
- Dependencias opcionais (cv2, easyocr) com lazy loading
- **Ponto forte:** Separacao limpa da UI, testavel isoladamente

### 3.2 Camada UI (`ui/`)
- 10 telas seguindo padrao uniforme (QWidget + `pdf_changed` signal + `refresh_state`)
- 12 workers QThread com sinais `finished/progress/error`
- Componentes reutilizaveis (Toast, FilePathButton, SectionHeader)
- Tema Dracula com 331 linhas de QSS
- **Ponto fraco:** `page_editor.py` pode ter tamanho excessivo

### 3.3 Configuracao (`config/`)
- Singleton Settings com UserPreferences persistido em JSON
- Constantes de hardware (GPU, OCR) bem definidas
- Paleta Dracula centralizada
- **Adequado para o escopo atual**

### 3.4 Utilitarios (`utils/`)
- file_utils.py: logging e validacao de paths
- gpu_utils.py: GPUMonitor para CUDA/VRAM
- font_matcher.py: classificacao de familias de fontes
- **Funcional, sem problemas identificados**

---

## 4. Analise de Gaps vs PDF24

| Feature | PDForge | PDF24 | Gap | Prioridade |
|---------|---------|-------|-----|------------|
| Leitura/visualizacao PDF | Sim | Sim | — | — |
| Edicao de texto (busca/substituicao) | Sim | Sim | — | — |
| OCR | Sim (EasyOCR + CUDA) | Sim | — | — |
| Merge de PDFs | Sim | Sim | — | — |
| Split de PDFs | Sim | Sim | — | — |
| Compressao | Sim (3 perfis) | Sim | — | — |
| Rotacao | Sim | Sim | — | — |
| Classificacao de documentos | Sim (ML) | Nao | Vantagem PDForge | — |
| Deteccao de assinaturas | Sim (CV) | Nao | Vantagem PDForge | — |
| Processamento em lote | Sim | Sim | — | — |
| **Protecao por senha** | **Nao** | Sim | **Critico** | P0 |
| **Remover senha** | **Nao** | Sim | **Critico** | P0 |
| **PDF para imagens** | Parcial (interno) | Sim | **Alto** | P1 |
| **Imagens para PDF** | **Nao** | Sim | **Alto** | P1 |
| **Marca d'agua (texto)** | **Nao** | Sim | **Alto** | P1 |
| **Marca d'agua (imagem)** | **Nao** | Sim | **Alto** | P1 |
| **Reordenar paginas** | **Nao** | Sim | **Alto** | P1 |
| **Duplicar/deletar paginas** | **Nao** | Sim | **Alto** | P1 |
| Anotacoes | Nao | Sim | Medio | P2 |
| Comparar PDFs | Nao | Sim | Medio | P2 |
| Assinatura digital | Nao | Sim | Medio | P2 |
| Flatten PDF | Nao | Sim | Baixo | P3 |

**Resumo:** 6 features criticas/altas faltantes. 3 medias. 1 baixa.

---

## 5. Avaliacao de Packaging

### 5.1 build-deb.sh
- **Problema:** Wrapper aponta para `/opt/pdfforge/venv/bin/python` que so existe apos postinst. Se postinst falhar, app nao funciona
- **Problema:** rsync com excludes mas sem validacao do resultado
- **Recomendacao:** Wrapper com fallback para python3 do sistema

### 5.2 build-appimage.sh
- **Problema:** Copia venv com `|| true` — dependencias nao garantidas
- **Problema:** Downloads appimagetool sem cache, sem verificacao de integridade
- **Recomendacao:** Usar `pip install --target` em vez de copiar venv

### 5.3 build-flatpak.sh
- **Problema:** Sem verificacao de pre-requisitos (flatpak-builder)
- **Problema:** Ausente do release.yml apesar de prometido no README
- **Recomendacao:** Adicionar verificacao de dependencias + incluir no CI

### 5.4 set-version.sh
- **Funcional:** Sincroniza versao em pyproject.toml, settings.py, DEBIAN/control
- **Falta:** Validacao de formato semver

### 5.5 Dependencias
- **opencv-python-headless e joblib:** Usados condicionalmente mas nao documentados como opcionais em requirements.txt
- **Recomendacao:** Documentar deps opcionais explicitamente

---

## 6. Avaliacao de Testes

### 6.1 Cobertura por Modulo

| Modulo | Testes | Cobertura Estimada | Status |
|--------|--------|--------------------|--------|
| pdf_reader | 3 | ~70% | Adequada |
| pdf_merger | 1 | ~50% | Minima |
| pdf_splitter | 1 | ~25% | Insuficiente |
| pdf_compressor | 3 | ~40% | Parcial |
| pdf_rotator | 2 | ~70% | Adequada |
| pdf_editor | 1 | ~30% | Insuficiente |
| document_classifier | 2 | ~60% | Parcial |
| ocr_engine | 0 | 0% | Ausente |
| batch_processor | 0 | 0% | Ausente |
| signature_handler | 0 | 0% | Ausente |
| metadata | 0 | 0% | Ausente |
| font_detector | 0 | 0% | Ausente |

### 6.2 Infraestrutura de Testes
- **Fixtures:** 3 (sample_pdf_path, sample_multipage_path, sample_pdf_doc) — minimo viavel
- **CI:** pytest roda em Python 3.10 e 3.11
- **Falta:** Python 3.12 na matrix, testes de integracao UI, testes de packaging

### 6.3 Recomendacoes
1. Priorizar testes para modulos com 0% de cobertura
2. Expandir fixtures com PDFs de cenarios especificos (encriptado, com imagens, multiplas fontes)
3. Adicionar Python 3.12 na matrix de CI

---

## 7. Avaliacao de CI/CD

### 7.1 ci.yml
- **Funcional:** ruff + mypy + pytest em push/PR para main/develop
- **Falta:** Python 3.12 na matrix
- **Falta:** Testes de packaging como step adicional

### 7.2 release.yml
- **Funcional:** Tag-triggered, builda .deb e AppImage
- **Falta:** Flatpak (prometido no README)
- **Falta:** Validacao de artefatos (dpkg-deb --info, --appimage-extract)
- **Falta:** Job de testes antes do build
- **Problema:** Token OAuth sem escopo `workflow` impede push de alteracoes

---

## 8. Matriz de Recomendacoes

### Prioridade x Esforco

| Recomendacao | Prioridade | Esforco | Sprint |
|-------------|------------|---------|--------|
| Corrigir BUG-01 (OCR layer) | Alta | Medio | 10 |
| Corrigir BUG-02/03/05 (compressor) | Media | Baixo | 10 |
| Cobertura de testes (6 modulos a 0%) | Alta | Medio | 10 |
| Seguranca PDF (senha) | Critica | Medio | 11 |
| Conversao PDF <-> imagens | Alta | Medio | 12 |
| Marca d'agua | Alta | Medio | 13 |
| Reordenacao de paginas | Alta | Alto | 14 |
| Correcoes de packaging | Alta | Medio | 15 |
| CI/CD completo com Flatpak | Media | Medio | 15 |
| Anotacoes PDF | Media | Alto | Futuro |
| Comparacao de PDFs | Media | Alto | Futuro |
| Assinatura digital | Media | Alto | Futuro |

### Roadmap Recomendado

```
Sprint 10 (bugs + testes) → Sprint 11 (seguranca) → Sprint 12 (imagens)
                                                          ↓
Sprint 15 (packaging + CI/CD) ← Sprint 14 (organizar) ← Sprint 13 (marca d'agua)
```

---

## 9. Conclusao

O PDForge tem uma base arquitetural solida com separacao de responsabilidades, padrao de workers consistente e tema visual coeso. Os principais pontos de melhoria sao:

1. **Bugs criticos:** OCR layer positioning precisa de reescrita
2. **Cobertura de testes:** 6 modulos sem testes comprometem confianca
3. **Features faltantes:** 6 gaps criticos/altos vs PDF24
4. **Packaging:** Scripts frageis sem validacao
5. **CI/CD:** Incompleto, sem Flatpak, sem validacao de artefatos

O roadmap de 6 sprints (10-15) endereca todos esses pontos de forma incremental e sustentavel.

---

*"A qualidade nao e um ato, e um habito." — Aristoteles*
