# Funcionalidades

## Editor de Texto

Busca e substituição de texto em PDFs com suporte a múltiplos pares buscar/substituir.
Preserva o estilo tipográfico original (fonte, tamanho, cor). Exportação para DOCX via
`pdf2docx`.

**Limitações:** a substituição opera sobre o texto extraído do PDF; PDFs escaneados sem
camada de texto não são editáveis sem OCR prévio.

## Analisador

Exibe metadados completos do PDF: título, autor, criador, datas, versão, tamanho, número
de páginas, fontes e imagens embutidas.

## OCR

Reconhecimento óptico de caracteres via EasyOCR. Suporta GPU (NVIDIA CUDA) e CPU.
Idiomas suportados: português e inglês por padrão (configurável em preferências).

**Limitação:** arquivos maiores que 50 MB desabilitam o preview automático para evitar
travamentos de memória.

## Mesclar

Combina múltiplos PDFs em um único arquivo. Suporta drag-and-drop para reordenação.
É possível selecionar intervalos de páginas por arquivo.

## Dividir

Três modos de divisão:
- **Por Range:** intervalos de páginas em formato `0-2, 3-4, 5-9` (base 0)
- **Por Tamanho:** tamanho máximo por parte em MB
- **Por Marcadores:** usa o sumário (TOC) de nível 1 do PDF como pontos de corte

## Comprimir

Três perfis de compressão:
- **Leve:** DPI 150, JPEG 85%, sem deflate — mínima perda de qualidade
- **Médio:** DPI 120, JPEG 72%, com deflate — equilíbrio qualidade/tamanho
- **Agressivo:** DPI 96, JPEG 55%, com deflate — máxima redução

Detecta automaticamente o tipo de conteúdo (texto, imagem, misto, escaneado) para
estimar a redução esperada.

## Assinaturas

Detecta regiões de assinatura via análise de imagem (aspect ratio, contornos).
Permite extrair a assinatura como PNG e reinserí-la em uma nova posição.

**Limitação:** a detecção heurística pode ter falsos positivos em PDFs com muitas
imagens pequenas.

## Classificar

Classifica documentos automaticamente nas categorias: contrato, nota_fiscal, procuração,
laudo, relatório, ata, currículo. Usa modelo ML (`.pkl`) se disponível em
`~/.pdfforge/models/classifier.pkl`, ou fallback heurístico baseado em keywords PT-BR.

Modo lote: processa todos os PDFs de uma pasta e exibe resultados em tabela colorida
por confiança (verde ≥ 70%, amarelo 40–70%, vermelho < 40%).

## Lote

Processa múltiplos PDFs de uma pasta com uma operação: extrair metadados, aplicar OCR,
ou rotacionar (90°, 180°, 270°).
