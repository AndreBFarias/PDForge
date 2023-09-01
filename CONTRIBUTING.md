# Contribuindo com o PDForge

Contribuicoes sao bem-vindas. Este guia descreve o processo e as convencoes do projeto.

## Processo

1. Fork do repositorio
2. Crie um branch a partir de `develop`: `git checkout -b feat/minha-feature develop`
3. Implemente com testes
4. Verifique: `python3 -m pytest tests/ -v --tb=short`
5. Commit seguindo o padrao abaixo
6. Abra PR contra `develop` (nunca contra `main`)

## Padrao de Commits

```
tipo: descricao imperativa em PT-BR com acentuacao

# Tipos: feat, fix, refactor, docs, test, perf, chore
```

Exemplos:
- `feat: adiciona exportacao para DOCX`
- `fix: corrige rotacao em PDFs protegidos`
- `refactor: extrai logica de compressao para modulo separado`

## Regras

- **PT-BR** em commits, logs e mensagens de interface
- **Zero emojis** em codigo, commits e documentacao
- **Zero mencoes a IA** — commits devem ser anonimos e limpos
- **Type hints** em todas as funcoes publicas
- **Logger**: `logging.getLogger("pdfforge.submodulo")` — nunca `print()`
- **Assinatura filosofica** como comentario final em cada arquivo Python
- **800 linhas** maximo por arquivo — se ultrapassar, extraia para modulo separado
- **Dataclasses** para resultados de operacoes com `success: bool` e `error: str`
- **Workers**: QThread com sinais `finished(object)`, `progress(int, int, str)`, `error(str)`

## Testes

```bash
python3 -m pytest tests/ -v --tb=short
```

Novos modulos em `core/` devem ter testes correspondentes em `tests/core/`.
Use o `conftest.py` existente para fixtures de PDFs de teste.

## Estrutura de Branches

- `main`: releases estaveis
- `develop`: integracao de features

## Ambiente de Desenvolvimento

```bash
git clone https://github.com/AndreBFarias/PDForge.git
cd PDForge
make dev
```

## Checklist Pre-Commit

- [ ] Testes passando
- [ ] Zero emojis no codigo
- [ ] Zero mencoes a IA
- [ ] Commit message em PT-BR com acentuacao
- [ ] Assinatura filosofica presente
- [ ] Documentacao atualizada se necessario
