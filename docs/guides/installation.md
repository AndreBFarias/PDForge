# Instalação

## Requisitos de sistema

- Ubuntu 22.04+ (ou derivados Debian)
- Python 3.10 ou superior
- 4 GB de RAM (8 GB recomendado para OCR)
- GPU NVIDIA opcional (CUDA 11.8+ para OCR acelerado)

## Instalação via script

```bash
git clone https://github.com/AndreBFarias/PDForge.git
cd PDForge
bash install.sh
```

O script instala dependências do sistema via `apt-get`, cria ambiente virtual em
`~/.local/pdfforge/venv`, copia o código para `~/.local/pdfforge/app` e cria o
wrapper `pdfforge` em `/usr/local/bin`.

## Instalação manual

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

## Variáveis de ambiente

| Variável | Efeito |
|----------|--------|
| `PDFFORGE_DEBUG=1` | Equivalente a `--debug` |
| `QT_QPA_PLATFORM=offscreen` | Modo headless (testes CI) |

## Suporte a GPU

Instale o PyTorch com suporte CUDA separadamente se desejar GPU para OCR:

```bash
pip install torch --index-url https://download.pytorch.org/whl/cu121
```
