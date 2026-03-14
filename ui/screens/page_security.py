import logging
from pathlib import Path

import fitz
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from ui.components import ExportDialog, FilePathButton, SectionHeader, Toast
from ui.styles import DraculaTheme
from ui.workers import SecurityWorker

logger = logging.getLogger("pdfforge.screens.security")


class PageSecurity(QWidget):
    def __init__(
        self, use_gpu: bool = True, parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._use_gpu = use_gpu
        self._worker: SecurityWorker | None = None
        self._last_output: Path | None = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 20)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        layout.addWidget(SectionHeader("Segurança", "PDF"))

        tabs = QTabWidget()
        tabs.addTab(self._build_encrypt_tab(), "Proteger")
        tabs.addTab(self._build_decrypt_tab(), "Desproteger")
        layout.addWidget(tabs)

        self._progress = QProgressBar()
        self._progress.setRange(0, 0)
        self._progress.setVisible(False)
        layout.addWidget(self._progress)

        self._lbl_status = QLabel("Pronto.")
        self._lbl_status.setStyleSheet(
            f"color: {DraculaTheme.COMMENT};",
        )
        self._lbl_status.setWordWrap(True)
        layout.addWidget(self._lbl_status)

        self._toast = Toast(self)

    def _build_encrypt_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(8)

        lbl = QLabel("Arquivo PDF")
        lbl.setStyleSheet(
            f"color: {DraculaTheme.COMMENT}; font-weight: bold;",
        )
        layout.addWidget(lbl)
        self._enc_btn_in = FilePathButton(
            "Selecionar PDF  ", mode="pdf",
        )
        layout.addWidget(self._enc_btn_in)

        lbl_out = QLabel("Arquivo de saída")
        lbl_out.setStyleSheet(
            f"color: {DraculaTheme.COMMENT}; font-weight: bold;",
        )
        layout.addWidget(lbl_out)
        self._enc_btn_out = FilePathButton(
            "Selecionar arquivo de saída (.pdf)  ", mode="save",
        )
        layout.addWidget(self._enc_btn_out)

        lbl_pw = QLabel("Senha do usuário")
        lbl_pw.setStyleSheet(
            f"color: {DraculaTheme.COMMENT}; font-weight: bold;",
        )
        layout.addWidget(lbl_pw)
        self._enc_user_pw = QLineEdit()
        self._enc_user_pw.setEchoMode(QLineEdit.EchoMode.Password)
        self._enc_user_pw.setPlaceholderText("Senha para abrir o PDF")
        layout.addWidget(self._enc_user_pw)

        lbl_opw = QLabel("Senha do proprietário (opcional)")
        lbl_opw.setStyleSheet(
            f"color: {DraculaTheme.COMMENT}; font-weight: bold;",
        )
        layout.addWidget(lbl_opw)
        self._enc_owner_pw = QLineEdit()
        self._enc_owner_pw.setEchoMode(QLineEdit.EchoMode.Password)
        self._enc_owner_pw.setPlaceholderText(
            "Senha para editar permissões",
        )
        layout.addWidget(self._enc_owner_pw)

        perm_lbl = QLabel("Permissões")
        perm_lbl.setStyleSheet(
            f"color: {DraculaTheme.COMMENT}; font-weight: bold;",
        )
        layout.addWidget(perm_lbl)
        self._chk_print = QCheckBox("Permitir impressão")
        self._chk_print.setChecked(True)
        self._chk_copy = QCheckBox("Permitir cópia de texto")
        self._chk_copy.setChecked(True)
        self._chk_annotate = QCheckBox("Permitir anotações")
        self._chk_annotate.setChecked(True)
        layout.addWidget(self._chk_print)
        layout.addWidget(self._chk_copy)
        layout.addWidget(self._chk_annotate)

        btn = QPushButton("ENCRIPTAR")
        btn.setObjectName("actionBtn")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed,
        )
        btn.clicked.connect(self._encrypt)
        layout.addWidget(btn)
        self._enc_btn_run = btn

        layout.addStretch()
        return tab

    def _build_decrypt_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(8)

        lbl = QLabel("Arquivo PDF protegido")
        lbl.setStyleSheet(
            f"color: {DraculaTheme.COMMENT}; font-weight: bold;",
        )
        layout.addWidget(lbl)
        self._dec_btn_in = FilePathButton(
            "Selecionar PDF  ", mode="pdf",
        )
        layout.addWidget(self._dec_btn_in)

        lbl_out = QLabel("Arquivo de saída")
        lbl_out.setStyleSheet(
            f"color: {DraculaTheme.COMMENT}; font-weight: bold;",
        )
        layout.addWidget(lbl_out)
        self._dec_btn_out = FilePathButton(
            "Selecionar arquivo de saída (.pdf)  ", mode="save",
        )
        layout.addWidget(self._dec_btn_out)

        lbl_pw = QLabel("Senha atual")
        lbl_pw.setStyleSheet(
            f"color: {DraculaTheme.COMMENT}; font-weight: bold;",
        )
        layout.addWidget(lbl_pw)
        self._dec_pw = QLineEdit()
        self._dec_pw.setEchoMode(QLineEdit.EchoMode.Password)
        self._dec_pw.setPlaceholderText("Senha do PDF")
        layout.addWidget(self._dec_pw)

        btn = QPushButton("REMOVER SENHA")
        btn.setObjectName("actionBtn")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed,
        )
        btn.clicked.connect(self._decrypt)
        layout.addWidget(btn)
        self._dec_btn_run = btn

        layout.addStretch()
        return tab

    def refresh_state(
        self, pdf_path: Path | None, output_dir: Path | None,
    ) -> None:
        if pdf_path:
            self._enc_btn_in.set_path(pdf_path)
            self._dec_btn_in.set_path(pdf_path)

    def _encrypt(self) -> None:
        pdf = self._enc_btn_in.current_path
        out = self._enc_btn_out.current_path
        pw = self._enc_user_pw.text().strip()

        if not pdf:
            self._toast.show_message("Selecione um arquivo PDF.")
            return
        if not out:
            self._toast.show_message("Selecione o arquivo de saída.")
            return
        if not pw:
            self._toast.show_message("Informe a senha.")
            return
        if self._worker and self._worker.isRunning():
            return

        permissions = 0
        if self._chk_print.isChecked():
            permissions |= fitz.PDF_PERM_PRINT
        if self._chk_copy.isChecked():
            permissions |= fitz.PDF_PERM_COPY
        if self._chk_annotate.isChecked():
            permissions |= fitz.PDF_PERM_ANNOTATE

        owner_pw = self._enc_owner_pw.text().strip() or None
        self._last_output = out
        self._enc_btn_run.setEnabled(False)
        self._enc_btn_run.setText("Encriptando...")
        self._progress.setVisible(True)
        self._lbl_status.setText("Processando...")

        self._worker = SecurityWorker(
            mode="encrypt",
            input_path=pdf,
            output_path=out,
            password=pw,
            owner_password=owner_pw,
            permissions=permissions,
        )
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _decrypt(self) -> None:
        pdf = self._dec_btn_in.current_path
        out = self._dec_btn_out.current_path
        pw = self._dec_pw.text().strip()

        if not pdf:
            self._toast.show_message("Selecione um arquivo PDF.")
            return
        if not out:
            self._toast.show_message("Selecione o arquivo de saída.")
            return
        if not pw:
            self._toast.show_message("Informe a senha.")
            return
        if self._worker and self._worker.isRunning():
            return

        self._last_output = out
        self._dec_btn_run.setEnabled(False)
        self._dec_btn_run.setText("Removendo senha...")
        self._progress.setVisible(True)
        self._lbl_status.setText("Processando...")

        self._worker = SecurityWorker(
            mode="decrypt",
            input_path=pdf,
            output_path=out,
            password=pw,
        )
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_finished(self, result) -> None:
        self._enc_btn_run.setEnabled(True)
        self._enc_btn_run.setText("ENCRIPTAR")
        self._dec_btn_run.setEnabled(True)
        self._dec_btn_run.setText("REMOVER SENHA")
        self._progress.setVisible(False)

        if result.success:
            self._lbl_status.setStyleSheet(
                f"color: {DraculaTheme.GREEN};",
            )
            self._lbl_status.setText("Operação concluída.")
            if self._last_output and self._last_output.exists():
                ExportDialog(self._last_output, self).exec()
        else:
            self._lbl_status.setStyleSheet(
                f"color: {DraculaTheme.RED};",
            )
            self._lbl_status.setText(f"Erro: {result.error}")

    def _on_error(self, msg: str) -> None:
        self._enc_btn_run.setEnabled(True)
        self._enc_btn_run.setText("ENCRIPTAR")
        self._dec_btn_run.setEnabled(True)
        self._dec_btn_run.setText("REMOVER SENHA")
        self._progress.setVisible(False)
        self._lbl_status.setStyleSheet(f"color: {DraculaTheme.RED};")
        self._lbl_status.setText(f"Erro: {msg}")


# "Quem troca liberdade por segurança não merece nenhuma." — Benjamin Franklin
