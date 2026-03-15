# Auditoria Externa — PDForge v1.0.0

**Data:** 2026-03-14
**Escopo:** Revisão completa de maturidade, bugs, arquitetura, gaps e recomendações

---

## 1. Resumo Executivo

O PDForge é uma ferramenta desktop PyQt6 para manipulação avançada de PDFs no Linux, posicionada como alternativa ao PDF24. O projeto está na v1.0.0 com ~5.500 LOC Python, 13 módulos core, 10 telas UI, 13 testes passando.

### Pontuacao de Maturidade (1-5)

| Eixo | Nota | Justificativa |
|------|------|---------------|
| Arquitetura | 4 | Separacao core/UI limpa, dataclasses, workers QThread |
| Qualidade de Codigo | 3.5 | Type hints, logging hierarquico, mas alguns code smells |
| Cobertura de Testes | 2 | 13 testes, 6 modulos sem cobertura alguma |
| Packaging | 2 | Scripts existem mas frágeis, sem validação |
| CI/CD | 2.5 | Pipeline básica, sem testes de packaging |
| Funcionalidades | 3 | Core sólido, mas gaps críticos vs PDF24 |
| Documentação | 3.5 | README, DEVGUIDE, CONTRIBUTING, CHANGELOG presentes |
| Segurança | 1.5 | Sem proteção por senha, sem validação de input em PDFs malformados |

**Média geral: 2.75/5 — Projeto funcional mas imaturo para distribuição pública.**

---

## 2. Inventario de Bugs Confirmados

Todos os bugs foram verificados por leitura direta do código-fonte e/ou execução de testes.

| ID | Sev. | Arquivo | Descricao | Verificacao |
|----|------|---------|-----------|-------------|
| BUG-01 | ALTO | `core/ocr_engine.py:121-127` | `save_ocr_layer` insere TODO o texto OCR em `Point(10,10)` com `fontsize=1`. Texto não fica posicionado sobre o conteúdo original. Seleção de texto em leitor PDF retorna tudo de um único ponto | Confirmado por leitura direta |
| BUG-02 | MEDIO | `core/pdf_compressor.py:87` | Limiar Laplaciano = 50 para detectar SCANNED. Com scale 0.5, valores reais podem variar. Threshold não calibrado com dados reais | Debatable — funciona em alguns cenários mas pode classificar errado |
| BUG-03 | MEDIO | `core/pdf_compressor.py:146` | `page.insert_image(rect, stream=jpeg)` sobrepõe imagem JPEG sobre imagem original. Original permanece no PDF. `garbage=4` remove objetos não referenciados, mas imagem original pode ainda ser referenciada | Compressão funcionou em teste (30.8%), mas mecanismo é frágil |
| BUG-04 | MEDIO | `core/pdf_splitter.py:63-74` | `split_by_size()` cria doc temporário + BytesIO para cada iteração. O(n^2) em páginas. Com 50 páginas e 10KB max, levou 0.11s — performance aceitável para volumes normais, mas degrada com PDFs grandes | Confirmado, impacto baixo na prática |
| BUG-05 | BAIXO | `core/pdf_compressor.py:78` | `cv2.COLOR_RGB2GRAY` em array 4-channel (RGBA). OpenCV 4.x aceita e produz resultado correto, mas depende de comportamento não documentado | Verificado: NÃO causa crash, resultado idêntico a RGBA2GRAY |
| BUG-06 | BAIXO | `core/pdf_editor.py:80` | Fallback de baseline usa `rect.y1` (bottom do rect). Para `insert_text`, o ponto é interpretado como baseline. Posicionamento pode ficar ligeiramente deslocado | Code smell, impacto visual menor |
| BUG-07 | INFO | `core/font_detector.py:86` | Assinatura filosófica colocada entre métodos da classe (antes de `get_dominant_font`). Método está dentro da classe (confirmado via AST). Code smell visual, sem impacto funcional | FALSO POSITIVO — verificado via ast.parse() |

---

## 3. Revisão Arquitetural

### 3.1 Camada Core (`core/`)
- 13 módulos com responsabilidade única
- Padrão consistente: dataclass de resultado + método principal
- Logging hierárquico (`pdfforge.modulo`)
- Dependências opcionais (cv2, easyocr) com lazy loading
- **Ponto forte:** Separação limpa da UI, testável isoladamente

### 3.2 Camada UI (`ui/`)
- 10 telas seguindo padrao uniforme (QWidget + `pdf_changed` signal + `refresh_state`)
- 12 workers QThread com sinais `finished/progress/error`
- Componentes reutilizáveis (Toast, FilePathButton, SectionHeader)
- Tema Dracula com 331 linhas de QSS
- **Ponto fraco:** `page_editor.py` pode ter tamanho excessivo

### 3.3 Configuracao (`config/`)
- Singleton Settings com UserPreferences persistido em JSON
- Constantes de hardware (GPU, OCR) bem definidas
- Paleta Dracula centralizada
- **Adequado para o escopo atual**

### 3.4 Utilitários (`utils/`)
- file_utils.py: logging e validação de paths
- gpu_utils.py: GPUMonitor para CUDA/VRAM
- font_matcher.py: classificação de famílias de fontes
- **Funcional, sem problemas identificados**

---

## 4. Análise de Gaps vs PDF24

| Feature | PDForge | PDF24 | Gap | Prioridade |
|---------|---------|-------|-----|------------|
| Leitura/visualizacao PDF | Sim | Sim | — | — |
| Edicao de texto (busca/substituicao) | Sim | Sim | — | — |
| OCR | Sim (EasyOCR + CUDA) | Sim | — | — |
| Merge de PDFs | Sim | Sim | — | — |
| Split de PDFs | Sim | Sim | — | — |
| Compressao | Sim (3 perfis) | Sim | — | — |
| Rotacao | Sim | Sim | — | — |
| Classificação de documentos | Sim (ML) | Não | Vantagem PDForge | — |
| Detecção de assinaturas | Sim (CV) | Não | Vantagem PDForge | — |
| Processamento em lote | Sim | Sim | — | — |
| **Proteção por senha** | **Não** | Sim | **Crítico** | P0 |
| **Remover senha** | **Não** | Sim | **Crítico** | P0 |
| **PDF para imagens** | Parcial (interno) | Sim | **Alto** | P1 |
| **Imagens para PDF** | **Não** | Sim | **Alto** | P1 |
| **Marca d'água (texto)** | **Não** | Sim | **Alto** | P1 |
| **Marca d'água (imagem)** | **Não** | Sim | **Alto** | P1 |
| **Reordenar páginas** | **Não** | Sim | **Alto** | P1 |
| **Duplicar/deletar páginas** | **Não** | Sim | **Alto** | P1 |
| Anotações | Não | Sim | Médio | P2 |
| Comparar PDFs | Não | Sim | Médio | P2 |
| Assinatura digital | Não | Sim | Médio | P2 |
| Flatten PDF | Não | Sim | Baixo | P3 |

**Resumo:** 6 features críticas/altas faltantes. 3 médias. 1 baixa.

---

## 5. Avaliacao de Packaging

### 5.1 build-deb.sh
- **Problema:** Wrapper aponta para `/opt/pdfforge/venv/bin/python` que só existe após postinst. Se postinst falhar, app não funciona
- **Problema:** rsync com excludes mas sem validação do resultado
- **Recomendação:** Wrapper com fallback para python3 do sistema

### 5.2 build-appimage.sh
- **Problema:** Copia venv com `|| true` — dependências não garantidas
- **Problema:** Downloads appimagetool sem cache, sem verificação de integridade
- **Recomendação:** Usar `pip install --target` em vez de copiar venv

### 5.3 build-flatpak.sh
- **Problema:** Sem verificação de pré-requisitos (flatpak-builder)
- **Problema:** Ausente do release.yml apesar de prometido no README
- **Recomendação:** Adicionar verificação de dependências + incluir no CI

### 5.4 set-version.sh
- **Funcional:** Sincroniza versão em pyproject.toml, settings.py, DEBIAN/control
- **Falta:** Validação de formato semver

### 5.5 Dependências
- **opencv-python-headless e joblib:** Usados condicionalmente mas não documentados como opcionais em requirements.txt
- **Recomendação:** Documentar deps opcionais explicitamente

---

## 6. Avaliacao de Testes

### 6.1 Cobertura por Módulo

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
- **Fixtures:** 3 (sample_pdf_path, sample_multipage_path, sample_pdf_doc) — mínimo viável
- **CI:** pytest roda em Python 3.10 e 3.11
- **Falta:** Python 3.12 na matrix, testes de integração UI, testes de packaging

### 6.3 Recomendações
1. Priorizar testes para módulos com 0% de cobertura
2. Expandir fixtures com PDFs de cenários específicos (encriptado, com imagens, múltiplas fontes)
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
- **Falta:** Validação de artefatos (dpkg-deb --info, --appimage-extract)
- **Falta:** Job de testes antes do build
- **Problema:** Token OAuth sem escopo `workflow` impede push de alterações

---

## 8. Matriz de Recomendações

### Prioridade x Esforço

| Recomendação | Prioridade | Esforço | Sprint |
|-------------|------------|---------|--------|
| Corrigir BUG-01 (OCR layer) | Alta | Médio | 10 |
| Corrigir BUG-02/03/05 (compressor) | Média | Baixo | 10 |
| Cobertura de testes (6 módulos a 0%) | Alta | Médio | 10 |
| Segurança PDF (senha) | Crítica | Médio | 11 |
| Conversão PDF <-> imagens | Alta | Médio | 12 |
| Marca d'água | Alta | Médio | 13 |
| Reordenação de páginas | Alta | Alto | 14 |
| Correções de packaging | Alta | Médio | 15 |
| CI/CD completo com Flatpak | Média | Médio | 15 |
| Anotações PDF | Média | Alto | Futuro |
| Comparação de PDFs | Média | Alto | Futuro |
| Assinatura digital | Média | Alto | Futuro |

### Roadmap Recomendado

```
Sprint 10 (bugs + testes) → Sprint 11 (seguranca) → Sprint 12 (imagens)
                                                          ↓
Sprint 15 (packaging + CI/CD) ← Sprint 14 (organizar) ← Sprint 13 (marca d'agua)
```

---

## 9. Conclusão

O PDForge tem uma base arquitetural sólida com separação de responsabilidades, padrão de workers consistente e tema visual coeso. Os principais pontos de melhoria são:

1. **Bugs críticos:** OCR layer positioning precisa de reescrita
2. **Cobertura de testes:** 6 módulos sem testes comprometem confiança
3. **Features faltantes:** 6 gaps críticos/altos vs PDF24
4. **Packaging:** Scripts frágeis sem validação
5. **CI/CD:** Incompleto, sem Flatpak, sem validação de artefatos

O roadmap de 6 sprints (10-15) endereça todos esses pontos de forma incremental e sustentável.

---

*"A qualidade não é um ato, é um hábito." — Aristóteles*
