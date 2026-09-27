"""Widget for entering TikTok URLs, pasting from clipboard, and triggering transcription."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class UrlInputWidget(QWidget):
    """Modern input bar with Paste and Transcribe action buttons."""

    transcribe_requested = Signal(str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Card container
        container = QFrame(self)
        container.setObjectName("innerCardFrame")
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(8, 8, 8, 8)
        container_layout.setSpacing(8)

        # Main URL input
        self.url_line_edit = QLineEdit(container)
        self.url_line_edit.setPlaceholderText("Pega una URL de TikTok (ej. https://www.tiktok.com/@usuario/video/...)")
        self.url_line_edit.setClearButtonEnabled(True)
        self.url_line_edit.returnPressed.connect(self._on_transcribe_clicked)
        container_layout.addWidget(self.url_line_edit, stretch=1)

        # "Pegar" button
        self.paste_button = QPushButton("Pegar", container)
        self.paste_button.setObjectName("secondaryButton")
        self.paste_button.setCursor(Qt.PointingHandCursor)
        self.paste_button.setToolTip("Pegar enlace desde el portapapeles")
        self.paste_button.clicked.connect(self._on_paste_clicked)
        container_layout.addWidget(self.paste_button)

        # "Transcribir" button
        self.transcribe_button = QPushButton("Transcribir", container)
        self.transcribe_button.setObjectName("primaryButton")
        self.transcribe_button.setCursor(Qt.PointingHandCursor)
        self.transcribe_button.clicked.connect(self._on_transcribe_clicked)
        container_layout.addWidget(self.transcribe_button)

        layout.addWidget(container)

    def _on_paste_clicked(self) -> None:
        clipboard = QApplication.clipboard()
        text = clipboard.text().strip()
        if text:
            self.url_line_edit.setText(text)
            self.url_line_edit.setFocus()

    def _on_transcribe_clicked(self) -> None:
        url = self.get_url()
        if url:
            self.transcribe_requested.emit(url)

    def get_url(self) -> str:
        return self.url_line_edit.text().strip()

    def set_url(self, url: str) -> None:
        self.url_line_edit.setText(url)

    def set_processing_state(self, is_processing: bool) -> None:
        """Update widget interactive state while processing is active."""
        if is_processing:
            self.transcribe_button.setText("Procesando...")
            self.transcribe_button.setEnabled(False)
            self.url_line_edit.setEnabled(False)
            self.paste_button.setEnabled(False)
        else:
            self.transcribe_button.setText("Transcribir")
            self.transcribe_button.setEnabled(True)
            self.url_line_edit.setEnabled(True)
            self.paste_button.setEnabled(True)
