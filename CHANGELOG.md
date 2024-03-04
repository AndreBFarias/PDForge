# Changelog

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/).

## [1.1.0] - 2026-03-15

### Adicionado

- Diálogo de exportação pós-operação em todas as telas: abre o arquivo gerado, abre a pasta ou fecha
- Módulo de segurança PDF (`core/pdf_security.py`): criptografia AES-256, remoção de senha, consulta de permissões
- Tela de segurança com encriptação e decriptação de PDFs (`ui/screens/page_security.py`)
- Conversor bidirecional PDF/imagens (`core/pdf_image_converter.py`): PDF para PNG/JPEG e imagens para PDF
- Tela de conversão de imagens com duas abas (`ui/screens/page_images.py`)
- Motor de marca d'água (`core/pdf_watermark.py`): texto e imagem, opacidade, rotação, posicionamento
- Tela de marca d'água com prévia de configuração (`ui/screens/page_watermark.py`)
- Organizador de páginas (`core/pdf_page_organizer.py`): reordenar, deletar, duplicar
- Tela de organização com drag-and-drop e grade de miniaturas (`ui/screens/page_organizer.py`)
- Workers para as quatro novas funcionalidades (`ui/workers.py`)
- Suite de testes expandida: `test_pdf_security.py`, `test_pdf_image_converter.py`, `test_pdf_watermark.py`, `test_pdf_page_organizer.py`, `test_metadata.py`, `test_font_detector.py`
- Sprints 10–15 documentadas em `docs/sprints/`

### Corrigido

- BUG-01: `save_ocr_layer` agora posiciona texto sobre as coordenadas reais extraídas pelo EasyOCR
- BUG-05: tratamento explícito de pixmaps RGBA antes de conversão cv2
- Fallback de baseline no editor de texto (`core/pdf_editor.py`)
- Dependências de sistema nos workflows CI/CD: `libgl1-mesa-glx` substituído por `libgl1 libegl1` (Ubuntu 24.04)
- Manifesto Flatpak: caminho de `requirements.txt` corrigido
- `build-flatpak` marcado como opcional no release (sandbox sem rede)
- AppImage removido do upload de release (excede limite de 2 GB do GitHub por incluir PyTorch/EasyOCR)
- Acentuação PT-BR corrigida em 20+ arquivos (código-fonte, scripts e documentação)
- Erros de mypy eliminados (12 arquivos): anotações de tipo, guards de None, `warn_unused_imports` removido

### Alterado

- Sidebar expandida de 9 para 13 itens: Segurança, Imagens, Marca d'Água, Organizar
- Versão atualizada para 1.1.0 em `pyproject.toml`, `config/settings.py`, `packaging/deb/DEBIAN/control`

## [1.0.0] - 2026-03-05

### Adicionado

- Interface gráfica PyQt6 com tema Dracula e 9 telas funcionais
- Editor de PDF com busca/substituição de texto e exportação DOCX
- Mesclagem de múltiplos PDFs com seleção de páginas
- Divisão por intervalos, tamanho máximo e bookmarks
- Compressão inteligente com perfis (leve, médio, agressivo) e análise de conteúdo
- Rotação de páginas individuais ou em lote
- Detecção e reinserção de assinaturas via análise de contornos (OpenCV)
- Classificação de documentos por heurística e modelo ML (joblib)
- OCR com EasyOCR e aceleração CUDA, fallback automático para CPU
- Processamento em lote com relatório detalhado
- Visualizador inline de páginas PDF com zoom e navegação
- Detecção de fontes com identificação de famílias tipográficas
- Leitura e edição de metadados PDF
- Analisador de documentos com informações detalhadas por página
- Modo CLI com click (--debug, --batch, --no-gpu)
- Variável de ambiente PDFFORGE_DEBUG para ativar modo debug
- Logging rotacionado por dia com namespace hierárquico
- Monitoramento de GPU com fallback gracioso para CPU
- Scripts de instalação e desinstalação para Linux
- Packaging para .deb, AppImage e Flatpak
- Entrada .desktop com integração ao menu de aplicativos
- Suite de 13 testes automatizados (pytest)
- Documentação: DEVGUIDE.md, CONTRIBUTING.md, arquitetura, guias
