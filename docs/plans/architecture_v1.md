# Arquitetura v1

## Camadas

```
┌─────────────────────────────────────────────────────────────┐
│  ui/                          Apresentação (PyQt6)           │
│  ├── main_window.py           Janela principal + navegação   │
│  ├── screens/                 Telas por funcionalidade       │
│  │   ├── page_editor.py       Substituição de texto          │
│  │   ├── page_analyzer.py     Análise de metadados           │
│  │   ├── page_ocr.py          OCR                            │
│  │   ├── page_merge.py        Mesclagem                      │
│  │   ├── page_split.py        Divisão                        │
│  │   ├── page_compress.py     Compressão                     │
│  │   ├── page_signature.py    Assinaturas                    │
│  │   ├── page_classifier.py   Classificação                  │
│  │   └── page_batch.py        Processamento em lote          │
│  ├── widgets/                 Componentes reutilizáveis       │
│  │   ├── pdf_page_viewer.py   Visualizador de páginas        │
│  │   └── drag_drop_list.py    Lista com drag-and-drop        │
│  ├── workers.py               QThreads para operações longas │
│  ├── components.py            Toast, FilePathButton, Header   │
│  └── styles.py                Tema Dracula (constantes CSS)  │
├─────────────────────────────────────────────────────────────┤
│  core/                        Lógica de domínio (sem UI)     │
│  ├── pdf_reader.py            Leitura e info de PDFs         │
│  ├── pdf_editor.py            Substituição de texto          │
│  ├── pdf_merger.py            Mesclagem de documentos        │
│  ├── pdf_splitter.py          Divisão de documentos          │
│  ├── pdf_rotator.py           Rotação de páginas             │
│  ├── pdf_compressor.py        Compressão com análise ML      │
│  ├── signature_handler.py     Detecção/extração assinaturas  │
│  ├── document_classifier.py   Classificação de documentos    │
│  ├── ocr_engine.py            Motor OCR (EasyOCR)            │
│  ├── batch_processor.py       Processamento em lote          │
│  ├── metadata.py              Leitura/escrita de metadados   │
│  └── font_detector.py         Detecção de fontes             │
├─────────────────────────────────────────────────────────────┤
│  config/                      Configuração global            │
│  └── settings.py              Singleton Settings + prefs     │
├─────────────────────────────────────────────────────────────┤
│  utils/                       Utilitários transversais       │
│  ├── file_utils.py            Logging, paths, I/O            │
│  ├── font_matcher.py          Mapeamento de fontes           │
│  └── gpu_utils.py             Detecção e gestão de GPU       │
└─────────────────────────────────────────────────────────────┘
```

## Fluxo de dados

```
Tela (QWidget)
  │  evento do usuário
  ▼
Worker (QThread)
  │  chama módulo core
  ▼
Core (lógica pura)
  │  retorna dataclass Result
  ▼
Worker.finished.emit(result)
  │  sinal Qt
  ▼
Tela._on_finished(result)
  │  atualiza UI
  ▼
MainWindow._load_pdf(path)  ← se novo PDF gerado
```

## Princípios de design

- **Core sem UI:** módulos em `core/` nunca importam PyQt6
- **Workers para I/O:** toda operação longa roda em QThread para não bloquear a UI
- **Graceful degradation:** cv2 e joblib são opcionais — fallback automático se ausentes
- **Singleton Settings:** uma única instância de configuração por processo
- **Local First:** tudo funciona offline; APIs de terceiros são opcionais
