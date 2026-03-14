# Sprint 11 — Seguranca PDF (Protecao/Remocao de Senha)

## Visao Estrategica

Seguranca por senha e o gap mais critico vs PDF24. Usuarios corporativos precisam proteger documentos sensiveis e remover senhas de PDFs recebidos. PyMuPDF suporta AES-256 nativamente, sem dependencias extras.

**Dependencias:** Sprint 10 (base estavel)
**Impacto:** Feature critica para adocao corporativa
**Estimativa:** ~410 LOC novas, 3 arquivos novos, 2 arquivos modificados

## Contexto Tecnico

### Capacidades PyMuPDF
- `doc.save(encryption=fitz.PDF_ENCRYPT_AES_256, user_pw=..., owner_pw=..., permissions=...)`
- `fitz.open(path, password=pw)` — abre com senha
- `doc.is_encrypted` — verifica se encriptado
- `doc.permissions` — retorna permissoes como int (bitfield)
- Permissoes: `fitz.PDF_PERM_PRINT`, `fitz.PDF_PERM_MODIFY`, `fitz.PDF_PERM_COPY`, `fitz.PDF_PERM_ANNOTATE`

### Padrao de tela a seguir
- `ui/screens/page_compress.py` — referencia para layout e fluxo
- Worker em `ui/workers.py` com signals `finished(object)`, `progress(int, int, str)`, `error(str)`
- Componentes: `FilePathButton`, `SectionHeader`, `Toast`

### Posicao na sidebar
- Indice 6 (antes de Assinaturas, que passa para 7)
- Label: "Seguranca"

## Tasks

### Task 11.1 — Criar core/pdf_security.py (~120 LOC)

```python
@dataclass
class SecurityResult:
    success: bool
    output_path: Path | None = None
    is_encrypted: bool = False
    permissions: dict[str, bool] | None = None
    error: str = ""

class PDFSecurity:
    def encrypt(self, input_path, output_path, user_password, owner_password=None, permissions=None) -> SecurityResult
    def decrypt(self, input_path, output_path, password) -> SecurityResult
    def check_encryption(self, input_path) -> SecurityResult
```

### Task 11.2 — Criar ui/screens/page_security.py (~180 LOC)

Layout:
- SectionHeader "Seguranca PDF"
- FilePathButton para selecionar PDF
- QTabWidget com 2 abas:
  - Aba "Proteger": campos de senha (user/owner), checkboxes de permissoes, botao "Encriptar"
  - Aba "Desproteger": campo de senha atual, botao "Remover Senha"
- QProgressBar
- Labels de status

### Task 11.3 — Criar tests/core/test_pdf_security.py (~80 LOC)

Testes:
1. `test_encrypt_pdf` — encripta e verifica que resultado e encriptado
2. `test_decrypt_pdf` — encripta, depois decripta e verifica
3. `test_check_encryption` — verifica status de PDF normal vs encriptado
4. `test_encrypt_with_permissions` — verifica que permissoes sao aplicadas
5. `test_decrypt_wrong_password` — senha errada retorna erro

### Task 11.4 — Adicionar SecurityWorker em ui/workers.py

Seguir padrao de CompressWorker:
```python
class SecurityWorker(QThread):
    finished = pyqtSignal(object)
    progress = pyqtSignal(int, int, str)
    error = pyqtSignal(str)
```

### Task 11.5 — Integrar na sidebar em ui/main_window.py

- Adicionar "Seguranca" no indice 6 de `_SIDEBAR_ITEMS`
- Criar instancia de PageSecurity no `_setup_content()`
- Ajustar indices das telas subsequentes

## Verificacao

```bash
QT_QPA_PLATFORM=offscreen python3 -m pytest tests/ -v --tb=short
ruff check .
```

## Commit

```
feat: adiciona seguranca PDF com encriptacao AES-256 e remocao de senha
```
