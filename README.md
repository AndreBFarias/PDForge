<div align="center">

[![opensource](https://badges.frapsoft.com/os/v1/open-source.png?v=103)](#)
[![Licenca](https://img.shields.io/badge/licenca-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python](https://img.shields.io/badge/python-3.10+-green.svg)](https://www.python.org/)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.x-green.svg)](https://www.riverbankcomputing.com/software/pyqt/)
[![Estrelas](https://img.shields.io/github/stars/AndreBFarias/PDForge.svg?style=social)](https://github.com/AndreBFarias/PDForge/stargazers)
[![Contribuições](https://img.shields.io/badge/contribui%C3%A7%C3%B5es-bem--vindas-brightgreen.svg)](https://github.com/AndreBFarias/PDForge/issues)

<h1>PDForge</h1>

<img src="assets/icon.png" width="120" alt="Logo PDForge">

</div>

---

### Descrição

Editor e manipulador de PDF para Linux com interface PyQt6, tema Dracula, OCR com aceleracao GPU (CUDA), classificacao de documentos por ML e processamento em lote.

---

### Principais Funcionalidades

| Categoria | Funcionalidade |
|-----------|---------------|
| **Edição** | Busca/substituição de texto, exportação DOCX, metadados |
| **Mesclagem** | Combinar múltiplos PDFs com drag-and-drop e seleção de páginas |
| **Divisão** | Por intervalo, tamanho máximo e bookmarks |
| **Compressão** | Perfis leve/médio/agressivo com análise de conteúdo (OpenCV) |
| **Rotação** | Páginas individuais ou em lote (90, 180, 270 graus) |
| **Assinaturas** | Detecção por visão computacional, extração e reinserção |
| **Classificação** | Heurística PT-BR + modelo ML (joblib) |
| **OCR** | EasyOCR com CUDA, fallback automático para CPU |
| **Lote** | Processamento em massa com relatório detalhado |
| **Análise** | Informações por página, detecção de fontes, preview inline |
| **Deploy** | AppImage, .deb, Flatpak |

---

### Instalação

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

**Obrigatórios:**
- Python 3.10+
- PyQt6
- PyMuPDF (fitz)
- click

**Recomendados (GPU):**
- GPU NVIDIA com CUDA
- EasyOCR
- PyTorch com suporte CUDA

**Opcionais:**
- OpenCV (compressão avançada, detecção de assinaturas)
- joblib (classificação ML)
- pdf2docx (exportação DOCX)

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
  config/              # Configurações e constantes
  core/                # Lógica de negócio (sem dependência de UI)
  ui/                  # Interface PyQt6 com tema Dracula
    screens/           # 9 telas funcionais
    widgets/           # Componentes customizados
  utils/               # Helpers (logging, GPU, fontes)
  tests/               # Testes (pytest)
  packaging/           # Scripts de build (.deb, AppImage, Flatpak)
  assets/              # Ícones e imagens
  docs/                # Documentação
```

---

### Documentacao

- [Referencia do Projeto](DEVGUIDE.md)
- [Arquitetura](docs/plans/architecture_v1.md)
- [Guia de Instalacao](docs/guides/installation.md)

---

### Contribuindo

Contribuições são bem-vindas. Veja [CONTRIBUTING.md](CONTRIBUTING.md) para detalhes.

---

### Desinstalar

```bash
bash uninstall.sh
```

---

### Licenca

GPLv3 - Veja [LICENSE](LICENSE) para detalhes.
