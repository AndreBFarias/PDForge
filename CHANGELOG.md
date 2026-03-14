# Changelog

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/).

## [1.0.0] - 2026-03-05

### Adicionado

- Interface grafica PyQt6 com tema Dracula e 9 telas funcionais
- Editor de PDF com busca/substituicao de texto e exportacao DOCX
- Mesclagem de multiplos PDFs com selecao de paginas
- Divisao por intervalos, tamanho maximo e bookmarks
- Compressao inteligente com perfis (leve, medio, agressivo) e analise de conteudo
- Rotacao de paginas individuais ou em lote
- Deteccao e reinsercao de assinaturas via analise de contornos (OpenCV)
- Classificacao de documentos por heuristica e modelo ML (joblib)
- OCR com EasyOCR e aceleracao CUDA, fallback automatico para CPU
- Processamento em lote com relatorio detalhado
- Visualizador inline de paginas PDF com zoom e navegacao
- Deteccao de fontes com identificacao de familias tipograficas
- Leitura e edicao de metadados PDF
- Analisador de documentos com informacoes detalhadas por pagina
- Modo CLI com click (--debug, --batch, --no-gpu)
- Variavel de ambiente PDFFORGE_DEBUG para ativar modo debug
- Logging rotacionado por dia com namespace hierarquico
- Monitoramento de GPU com fallback gracioso para CPU
- Scripts de instalacao e desinstalacao para Linux
- Packaging para .deb, AppImage e Flatpak
- Entrada .desktop com integracao ao menu de aplicativos
- Suite de 13 testes automatizados (pytest)
- Documentacao: DEVGUIDE.md, CONTRIBUTING.md, arquitetura, guias
