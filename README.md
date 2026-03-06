<div align="center">

[![opensource](https://badges.frapsoft.com/os/v1/open-source.png?v=103)](#)
[![Licenca](https://img.shields.io/badge/licenca-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python](https://img.shields.io/badge/python-3.10+-green.svg)](https://www.python.org/)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.x-green.svg)](https://www.riverbankcomputing.com/software/pyqt/)
[![Estrelas](https://img.shields.io/github/stars/AndreBFarias/PDForge.svg?style=social)](https://github.com/AndreBFarias/PDForge/stargazers)
[![Contribuicoes](https://img.shields.io/badge/contribuicoes-bem--vindas-brightgreen.svg)](https://github.com/AndreBFarias/PDForge/issues)

<h1>PDForge</h1>

<img src="assets/icon.png" width="120" alt="Logo PDForge">

</div>

---

### Descricao

Editor e manipulador de PDF para Linux com interface PyQt6, tema Dracula, OCR com aceleracao GPU (CUDA), classificacao de documentos por ML e processamento em lote.

---

### Principais Funcionalidades

| Categoria | Funcionalidade |
|-----------|---------------|
| **Edicao** | Busca/substituicao de texto, exportacao DOCX, metadados |
| **Mesclagem** | Combinar multiplos PDFs com drag-and-drop e selecao de paginas |
| **Divisao** | Por intervalo, tamanho maximo e bookmarks |
| **Compressao** | Perfis leve/medio/agressivo com analise de conteudo (OpenCV) |
| **Rotacao** | Paginas individuais ou em lote (90, 180, 270 graus) |
| **Assinaturas** | Deteccao por visao computacional, extracao e reinsercao |
| **Classificacao** | Heuristica PT-BR + modelo ML (joblib) |
| **OCR** | EasyOCR com CUDA, fallback automatico para CPU |
| **Lote** | Processamento em massa com relatorio detalhado |
| **Analise** | Informacoes por pagina, deteccao de fontes, preview inline |
| **Deploy** | AppImage, .deb, Flatpak |

---

### Instalacao

#### AppImage (Recomendado)

```bash
chmod +x PDForge-*.AppImage
./PDForge-*.AppImage
```

#### Ubuntu/Debian (.deb)

```bash
wget https://github.com/AndreBFarias/PDForge/releases/latest/download/pdfforge_1.0.0_all.deb
sudo dpkg -i pdfforge_1.0.0_all.deb
sudo apt-get install -f
pdfforge
```

#### Flatpak

```bash
flatpak install pdfforge.flatpak
flatpak run com.github.andrebfarias.pdfforge
```

#### Via Script (Desenvolvimento)

```bash
git clone https://github.com/AndreBFarias/PDForge.git
cd PDForge
chmod +x install.sh
./install.sh
```

---

### Requisitos

**Obrigatorios:**
- Python 3.10+
- PyQt6
- PyMuPDF (fitz)
- click

**Recomendados (GPU):**
- GPU NVIDIA com CUDA
- EasyOCR
- PyTorch com suporte CUDA

**Opcionais:**
- OpenCV (compressao avancada, deteccao de assinaturas)
- joblib (classificacao ML)
- pdf2docx (exportacao DOCX)

---

### Uso

**Via menu de aplicativos:** Procure por "PDForge"

**Via terminal (GUI):**
```bash
pdfforge
pdfforge arquivo.pdf
```

**Via CLI:**
```bash
pdfforge --help
pdfforge --debug arquivo.pdf
pdfforge --batch /pasta/pdfs/
pdfforge --no-gpu arquivo.pdf
PDFFORGE_DEBUG=1 pdfforge
```

---

### Estrutura do Projeto

```
PDForge/
  main.py              # Entry point CLI (click)
  config/              # Configuracoes e constantes
  core/                # Logica de negocio (sem dependencia de UI)
  ui/                  # Interface PyQt6 com tema Dracula
    screens/           # 9 telas funcionais
    widgets/           # Componentes customizados
  utils/               # Helpers (logging, GPU, fontes)
  tests/               # Testes (pytest)
  packaging/           # Scripts de build (.deb, AppImage, Flatpak)
  assets/              # Icones e imagens
  docs/                # Documentacao
```

---

### Documentacao

- [Referencia do Projeto](DEVGUIDE.md)
- [Arquitetura](docs/plans/architecture_v1.md)
- [Guia de Instalacao](docs/guides/installation.md)

---

### Contribuindo

Contribuicoes sao bem-vindas. Veja [CONTRIBUTING.md](CONTRIBUTING.md) para detalhes.

---

### Desinstalar

```bash
bash uninstall.sh
```

---

### Licenca

GPLv3 - Veja [LICENSE](LICENSE) para detalhes.
