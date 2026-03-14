# Sprint 15 — Correcoes de Packaging + Workflow CI/CD

## Visao Estrategica

Sprint final que prepara o projeto para distribuicao. Corrige fragilidades nos scripts de empacotamento e implementa pipeline CI/CD completa com validacao de artefatos.

**Dependencias:** Sprints 11-14 (todas as features prontas)
**Impacto:** Habilita distribuicao confiavel do software
**Estimativa:** ~350 LOC modificadas, 0 arquivos novos, 7 arquivos modificados

**Pre-requisito do usuario:** `gh auth refresh -h github.com -s workflow` para push de workflows.

## Contexto Tecnico

### Problemas identificados na auditoria
1. build-deb.sh: wrapper depende de venv que pode nao existir
2. build-appimage.sh: copia venv com `|| true`, downloads sem cache
3. build-flatpak.sh: sem verificacao de pre-requisitos
4. set-version.sh: sem validacao semver
5. release.yml: sem Flatpak, sem validacao de artefatos, sem testes pre-build
6. ci.yml: falta Python 3.12 na matrix
7. requirements.txt: deps opcionais nao documentadas

## Tasks

### Task 15.1 — Corrigir packaging/build-deb.sh

Melhorias:
1. Wrapper com fallback: tenta venv primeiro, depois python3 do sistema
2. Validar que rsync copiou arquivos essenciais
3. Verificar que .desktop entry esta correto
4. Adicionar `dpkg-deb --build` com verificacao de saida

### Task 15.2 — Corrigir packaging/appimage/build-appimage.sh

Melhorias:
1. Usar `pip install --target` em vez de copiar venv
2. Cachear appimagetool (verificar se ja existe antes de baixar)
3. Remover `|| true` e tratar erros explicitamente
4. Adicionar verificacao SHA256 do appimagetool

### Task 15.3 — Corrigir packaging/build-flatpak.sh

Melhorias:
1. Verificar pre-requisitos (flatpak-builder, flatpak)
2. Adicionar tratamento de erros
3. Verificar que manifesto YAML e valido

### Task 15.4 — Corrigir packaging/set-version.sh

Melhorias:
1. Validar formato semver (X.Y.Z)
2. Verificar que todos os arquivos-alvo existem
3. Reportar alteracoes feitas

### Task 15.5 — Atualizar requirements.txt

Adicionar secao de dependencias opcionais com comentarios:
```
# Opcionais (OCR avancado e classificacao)
# opencv-python-headless>=4.8.0
# joblib>=1.3.0
```

### Task 15.6 — Atualizar .github/workflows/ci.yml

- Adicionar Python 3.12 na matrix
- Verificar que pytest roda com `QT_QPA_PLATFORM=offscreen`

### Task 15.7 — Reescrever .github/workflows/release.yml

YAML completo com:
1. **Trigger:** `on: push: tags: ['v*.*.*']`
2. **Job validate-tag:** Verifica formato vX.Y.Z
3. **Job test:** Matrix Python 3.10, 3.11, 3.12
4. **Job build-deb:**
   - Ubuntu latest
   - Instala deps
   - Roda `bash packaging/build-deb.sh`
   - Valida com `dpkg-deb --info`
   - Upload artifact
5. **Job build-appimage:**
   - Ubuntu latest
   - Roda `bash packaging/appimage/build-appimage.sh`
   - Valida com `--appimage-extract` (smoke test)
   - Upload artifact
6. **Job build-flatpak:**
   - Ubuntu latest
   - Instala flatpak + flatpak-builder
   - Roda `bash packaging/build-flatpak.sh`
   - Upload artifact
7. **Job release:**
   - Depende de todos os jobs anteriores
   - Download artifacts
   - Cria GitHub Release via `softprops/action-gh-release@v2`
   - Attach .deb, .AppImage, .flatpak como assets

## Verificacao

```bash
# Testes
QT_QPA_PLATFORM=offscreen python3 -m pytest tests/ -v --tb=short
ruff check .

# Packaging (local)
bash packaging/build-deb.sh
dpkg-deb --info packaging/*.deb

bash packaging/appimage/build-appimage.sh
# AppImage: verificar que arquivo foi gerado

bash packaging/build-flatpak.sh
# Flatpak: verificar que bundle foi gerado
```

## Commit

```
chore: corrige packaging e reescreve workflow CI/CD com validacao de artefatos
```
