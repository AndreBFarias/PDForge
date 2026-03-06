# Sprint 08 — Repositório GitHub + Push Final

**Diretório:** `/home/andrefarias/Desenvolvimento/PDForge`
**Conta git:** `AndreBFarias` / `andre.dsbf@gmail.com`
**Pré-requisito:** Sprint 07 concluído e commitado. Todos os arquivos do projeto existem.

Execute todas as tasks direto, sem criar task list, sem confirmar etapas, sem parar a não ser em erro real.

---

## Verificação antes de começar

```bash
git log --oneline
git status
gh auth status
```

Confirme que:
- Há commits no repositório local
- Working tree está limpo (nada pendente)
- `gh` está autenticado

---

## Task 1 — Trocar conta gh para AndreBFarias

```bash
gh auth switch --hostname github.com --user AndreBFarias
```

Verifique com `gh auth status` — deve mostrar `AndreBFarias`.

---

## Task 2 — Criar repositório no GitHub

```bash
gh repo create AndreBFarias/PDForge \
    --public \
    --description "Editor de PDF com GUI e ML para Linux" \
    --license gpl-3.0
```

Se o repo já existir (criado em sessão anterior), pule este passo.

---

## Task 3 — Adicionar remote e push

```bash
git remote add origin git@github.com:AndreBFarias/PDForge.git
git push -u origin main
```

Se o remote já existir: `git remote set-url origin git@github.com:AndreBFarias/PDForge.git`

---

## Task 4 — Criar branch develop e push

```bash
git checkout -b develop
git push -u origin develop
git checkout main
```

---

## Task 5 — Verificação final

```bash
gh repo view AndreBFarias/PDForge
gh run list --limit 3
```

Confirme que:
- Repositório está público e acessível
- Branch `main` e `develop` existem no remote
- CI foi disparado (se houver commits após o setup do workflow)

---

## Conclusão

Ao finalizar este sprint, invocar o skill `superpowers:finishing-a-development-branch`
para decidir sobre merge, PR ou limpeza de branches.
