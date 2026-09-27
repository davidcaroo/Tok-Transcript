"""Styled dialog for displaying user-friendly error messages with optional technical details."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class ErrorDialog(QDialog):
    """Modern modal dialog showing friendly error feedback and optional technical diagnostics."""

    def __init__(
        self,
        title: str,
        user_message: str,
        technical_details: str = "",
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(440)
        self.setModal(True)
        self.technical_details = technical_details
        self._init_ui(user_message)

    def _init_ui(self, user_message: str) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        # Message container card
        card = QFrame(self)
        card.setObjectName("cardFrame")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(18, 18, 18, 18)
        card_layout.setSpacing(12)

        # Error title and message
        title_label = QLabel("Aviso", card)
        title_label.setStyleSheet("font-size: 16px; font-weight: 700; color: #f87171;")
        card_layout.addWidget(title_label)

        msg_label = QLabel(user_message, card)
        msg_label.setWordWrap(True)
        msg_label.setStyleSheet("font-size: 13px; color: #e2e8f0; line-height: 1.4;")
        card_layout.addWidget(msg_label)

        # Expandable technical details box
        if self.technical_details:
            self.details_edit = QPlainTextEdit(card)
            self.details_edit.setPlainText(self.technical_details)
            self.details_edit.setReadOnly(True)
            self.details_edit.setFixedHeight(90)
            self.details_edit.setStyleSheet(
                "font-family: monospace; font-size: 11px; background-color: #0b0f19; "
                "color: #94a3b8; border: 1px solid #334155; border-radius: 6px; padding: 6px;"
            )
            self.details_edit.hide()
            card_layout.addWidget(self.details_edit)

        main_layout.addWidget(card)

        # Bottom actions row
        actions_row = QHBoxLayout()
        actions_row.setSpacing(10)

        if self.technical_details:
            self.toggle_details_btn = QPushButton("Ver detalles técnicos", self)
            self.toggle_details_btn.setObjectName("secondaryButton")
            self.toggle_details_btn.setCheckable(True)
            self.toggle_details_btn.clicked.connect(self._toggle_details)
            actions_row.addWidget(self.toggle_details_btn)

        actions_row.addStretch()

        close_btn = QPushButton("Entendido", self)
        close_btn.setObjectName("primaryButton")
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.accept)
        actions_row.addWidget(close_btn)

        main_layout.addLayout(actions_row)

    def _toggle_details(self, checked: bool) -> None:
        if hasattr(self, "details_edit"):
            self.details_edit.setVisible(checked)
            self.toggle_details_btn.setText("Ocultar detalles" if checked else "Ver detalles técnicos")
            self.adjustSize()
