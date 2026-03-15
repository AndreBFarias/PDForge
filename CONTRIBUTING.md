# Contribuindo com o PDForge

Contribuições são bem-vindas. Este guia descreve o processo e as convenções do projeto.

## Processo

1. Fork do repositorio
2. Crie um branch a partir de `develop`: `git checkout -b feat/minha-feature develop`
3. Implemente com testes
4. Verifique: `python3 -m pytest tests/ -v --tb=short`
5. Commit seguindo o padrao abaixo
6. Abra PR contra `develop` (nunca contra `main`)

## Padrao de Commits

```
tipo: descrição imperativa em PT-BR com acentuação

# Tipos: feat, fix, refactor, docs, test, perf, chore
```

Exemplos:
- `feat: adiciona exportação para DOCX`
- `fix: corrige rotação em PDFs protegidos`
- `refactor: extrai lógica de compressão para módulo separado`

## Regras

- **PT-BR** em commits, logs e mensagens de interface
- **Zero emojis** em codigo, commits e documentacao
- **Zero menções a IA** — commits devem ser anônimos e limpos
- **Type hints** em todas as funções públicas
- **Logger**: `logging.getLogger("pdfforge.submodulo")` — nunca `print()`
- **Assinatura filosofica** como comentario final em cada arquivo Python
- **800 linhas** máximo por arquivo — se ultrapassar, extraia para módulo separado
- **Dataclasses** para resultados de operações com `success: bool` e `error: str`
- **Workers**: QThread com sinais `finished(object)`, `progress(int, int, str)`, `error(str)`

## Testes

```bash
python3 -m pytest tests/ -v --tb=short
```

Novos modulos em `core/` devem ter testes correspondentes em `tests/core/`.
Use o `conftest.py` existente para fixtures de PDFs de teste.

## Estrutura de Branches

- `main`: releases estáveis
- `develop`: integração de features

## Ambiente de Desenvolvimento

```bash
git clone https://github.com/AndreBFarias/PDForge.git
cd PDForge
make dev
```

## Checklist Pré-Commit

- [ ] Testes passando
- [ ] Zero emojis no código
- [ ] Zero menções a IA
- [ ] Commit message em PT-BR com acentuação
- [ ] Assinatura filosófica presente
- [ ] Documentação atualizada se necessário
