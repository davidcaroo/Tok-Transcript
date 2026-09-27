"""Transcript view widget displaying formatted text, metadata, copy action, and export buttons."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.exporter import export_srt, export_txt, export_vtt
from models.transcript import TranscriptResult

logger = logging.getLogger("tok_transcript.transcript_view")


class TranscriptView(QWidget):
    """Modern transcript visualizer with metadata tags, copy button, and format exports."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._current_result: Optional[TranscriptResult] = None
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Main Card container
        self.card = QFrame(self)
        self.card.setObjectName("cardFrame")
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.setSpacing(12)

        # Header: Section title + metadata chips + actions
        top_bar = QHBoxLayout()
        top_bar.setSpacing(10)

        title_label = QLabel("TRANSCRIPCIÓN", self.card)
        title_label.setObjectName("sectionTitle")
        top_bar.addWidget(title_label)

        # Metadata badges container
        self.metadata_container = QWidget(self.card)
        meta_layout = QHBoxLayout(self.metadata_container)
        meta_layout.setContentsMargins(0, 0, 0, 0)
        meta_layout.setSpacing(6)

        self.lang_badge = QLabel("Español", self.metadata_container)
        self.lang_badge.setObjectName("badgeLabel")
        self.duration_badge = QLabel("00:00", self.metadata_container)
        self.duration_badge.setObjectName("badgeLabel")
        self.words_badge = QLabel("0 palabras", self.metadata_container)
        self.words_badge.setObjectName("badgeLabel")

        meta_layout.addWidget(self.lang_badge)
        meta_layout.addWidget(self.duration_badge)
        meta_layout.addWidget(self.words_badge)
        top_bar.addWidget(self.metadata_container)

        top_bar.addStretch()

        # Temporary feedback badge ("¡Copiado!")
        self.copied_feedback = QLabel("¡Copiado!", self.card)
        self.copied_feedback.setObjectName("copiedBadge")
        self.copied_feedback.hide()
        top_bar.addWidget(self.copied_feedback)

        # "Copiar" button
        self.copy_button = QPushButton("Copiar", self.card)
        self.copy_button.setObjectName("secondaryButton")
        self.copy_button.setCursor(Qt.PointingHandCursor)
        self.copy_button.setToolTip("Copiar todo el texto al portapapeles")
        self.copy_button.clicked.connect(self._on_copy_clicked)
        self.copy_button.setEnabled(False)
        top_bar.addWidget(self.copy_button)

        card_layout.addLayout(top_bar)

        # Text area
        self.text_edit = QPlainTextEdit(self.card)
        self.text_edit.setReadOnly(True)
        self.text_edit.setPlaceholderText("La transcripción aparecerá aquí cuando se procese el video...")
        card_layout.addWidget(self.text_edit, stretch=1)

        # Bottom Bar: Export buttons + Edit Toggle
        bottom_bar = QHBoxLayout()
        bottom_bar.setSpacing(8)

        export_label = QLabel("Exportar:", self.card)
        export_label.setStyleSheet("color: #64748b; font-size: 11px; font-weight: 600;")
        bottom_bar.addWidget(export_label)

        self.export_txt_btn = QPushButton("Descargar TXT", self.card)
        self.export_txt_btn.setObjectName("secondaryButton")
        self.export_txt_btn.setCursor(Qt.PointingHandCursor)
        self.export_txt_btn.clicked.connect(self._on_export_txt)
        self.export_txt_btn.setEnabled(False)
        bottom_bar.addWidget(self.export_txt_btn)

        self.export_srt_btn = QPushButton("Descargar SRT", self.card)
        self.export_srt_btn.setObjectName("secondaryButton")
        self.export_srt_btn.setCursor(Qt.PointingHandCursor)
        self.export_srt_btn.clicked.connect(self._on_export_srt)
        self.export_srt_btn.setEnabled(False)
        bottom_bar.addWidget(self.export_srt_btn)

        self.export_vtt_btn = QPushButton("Descargar VTT", self.card)
        self.export_vtt_btn.setObjectName("secondaryButton")
        self.export_vtt_btn.setCursor(Qt.PointingHandCursor)
        self.export_vtt_btn.clicked.connect(self._on_export_vtt)
        self.export_vtt_btn.setEnabled(False)
        bottom_bar.addWidget(self.export_vtt_btn)

        bottom_bar.addStretch()

        # Editable toggle checkbox/button
        self.edit_toggle_btn = QPushButton("Habilitar edición", self.card)
        self.edit_toggle_btn.setObjectName("secondaryButton")
        self.edit_toggle_btn.setCheckable(True)
        self.edit_toggle_btn.clicked.connect(self._toggle_editable)
        self.edit_toggle_btn.setEnabled(False)
        bottom_bar.addWidget(self.edit_toggle_btn)

        card_layout.addLayout(bottom_bar)
        layout.addWidget(self.card, stretch=1)

        # Initially hide metadata chips until first result
        self.metadata_container.hide()

    def set_result(self, result: TranscriptResult) -> None:
        """Display the complete transcription and enable action buttons."""
        self._current_result = result
        self.text_edit.setPlainText(result.text)

        # Update metadata chips
        self.lang_badge.setText(result.language_label)
        self.duration_badge.setText(result.formatted_duration)
        self.words_badge.setText(f"{result.word_count} palabras")
        self.metadata_container.show()

        # Enable action buttons
        has_content = bool(result.text.strip())
        self.copy_button.setEnabled(has_content)
        self.export_txt_btn.setEnabled(has_content)
        self.export_srt_btn.setEnabled(has_content)
        self.export_vtt_btn.setEnabled(has_content)
        self.edit_toggle_btn.setEnabled(has_content)

    def clear(self) -> None:
        """Clear the current transcript and disable actions."""
        self._current_result = None
        self.text_edit.clear()
        self.metadata_container.hide()
        self.copy_button.setEnabled(False)
        self.export_txt_btn.setEnabled(False)
        self.export_srt_btn.setEnabled(False)
        self.export_vtt_btn.setEnabled(False)
        self.edit_toggle_btn.setEnabled(False)
        self.edit_toggle_btn.setChecked(False)
        self.text_edit.setReadOnly(True)

    def _toggle_editable(self, checked: bool) -> None:
        self.text_edit.setReadOnly(not checked)
        self.edit_toggle_btn.setText("Bloquear edición" if checked else "Habilitar edición")

    def _on_copy_clicked(self) -> None:
        text = self.text_edit.toPlainText().strip()
        if not text:
            return
        clipboard = QApplication.clipboard()
        clipboard.setText(text)

        # Show temporary visual badge for 1.5 seconds
        self.copied_feedback.show()
        QTimer.singleShot(1500, self.copied_feedback.hide)

    def _on_export_txt(self) -> None:
        if not self._current_result:
            return
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar Transcripción TXT",
            "transcripcion.txt",
            "Archivos de texto (*.txt)",
        )
        if file_path:
            try:
                # Use edited text if modified
                current_text = self.text_edit.toPlainText()
                edited_result = TranscriptResult(
                    text=current_text,
                    language=self._current_result.language,
                    duration=self._current_result.duration,
                    segments=self._current_result.segments,
                )
                export_txt(edited_result, file_path)
            except Exception as err:
                logger.error("Failed to export TXT: %s", err)
                QMessageBox.critical(self, "Error al exportar", f"No se pudo guardar el archivo TXT: {err}")

    def _on_export_srt(self) -> None:
        if not self._current_result:
            return
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar Subtítulos SRT",
            "subtitulos.srt",
            "Archivos SubRip (*.srt)",
        )
        if file_path:
            try:
                export_srt(self._current_result, file_path)
            except Exception as err:
                logger.error("Failed to export SRT: %s", err)
                QMessageBox.critical(self, "Error al exportar", f"No se pudo guardar el archivo SRT: {err}")

    def _on_export_vtt(self) -> None:
        if not self._current_result:
            return
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar Subtítulos VTT",
            "subtitulos.vtt",
            "Archivos WebVTT (*.vtt)",
        )
        if file_path:
            try:
                export_vtt(self._current_result, file_path)
            except Exception as err:
                logger.error("Failed to export VTT: %s", err)
                QMessageBox.critical(self, "Error al exportar", f"No se pudo guardar el archivo VTT: {err}")
