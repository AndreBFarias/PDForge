# PDForge

[![CI](https://github.com/AndreBFarias/PDForge/actions/workflows/ci.yml/badge.svg)](https://github.com/AndreBFarias/PDForge/actions/workflows/ci.yml)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)

Editor de PDF para Linux com interface Qt6 e recursos de ML.

## Funcionalidades

- Substituição de texto com suporte a regex
- OCR com EasyOCR (GPU/CPU automático)
- Mesclar múltiplos PDFs com drag-and-drop
- Dividir por range de páginas, tamanho ou marcadores
- Compressão inteligente com análise de conteúdo (3 perfis)
- Detecção e edição de assinaturas via visão computacional
- Classificação automática de documentos (ML + heurística PT-BR)
- Visualizador inline de páginas com zoom
- Processamento em lote

## Instalação

### Dependências

Python 3.10+ e as bibliotecas do sistema são instaladas automaticamente pelo script.

### Instalação rápida

```bash
git clone https://github.com/AndreBFarias/PDForge.git
cd PDForge
bash install.sh
```

Após a instalação, execute `pdfforge` no terminal ou pelo launcher do sistema.

### Ambiente de desenvolvimento

```bash
make dev
make test
make lint
```

## Uso via CLI

```bash
pdfforge --help
pdfforge arquivo.pdf
pdfforge --batch /pasta/pdfs --output /saida --debug
```

## Desinstalar

```bash
bash uninstall.sh
```

## Licença

GPL-3.0 — veja [LICENSE](LICENSE).
