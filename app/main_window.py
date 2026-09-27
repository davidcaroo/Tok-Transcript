"""Main desktop window for Tok-Transcript."""

from __future__ import annotations

import logging
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent, QIcon
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)

from app.dialogs.error_dialog import ErrorDialog
from app.widgets.progress_panel import ProgressPanel
from app.widgets.settings_panel import SettingsPanel
from app.widgets.transcript_view import TranscriptView
from app.widgets.url_input import UrlInputWidget
from models.transcript import TranscriptResult
from utils.config import APP_NAME, APP_SUBTITLE
from utils.paths import get_assets_path
from utils.validators import is_valid_tiktok_url
from workers.transcription_worker import TranscriptionWorker

logger = logging.getLogger("tok_transcript.main_window")


class MainWindow(QMainWindow):
    """Primary application window coordinating GUI widgets and background worker."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(920, 680)
        self.resize(980, 720)

        self._active_worker: Optional[TranscriptionWorker] = None
        self._init_ui()
        self._setup_app_icon()

    def _setup_app_icon(self) -> None:
        icon_path = get_assets_path() / "icons" / "app_icon.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

    def _init_ui(self) -> None:
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(24, 20, 24, 20)
        root_layout.setSpacing(16)

        # 1. Header Section
        header_frame = QFrame(self)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 4)
        header_layout.setSpacing(12)

        # Header titles
        title_box = QVBoxLayout()
        title_box.setSpacing(2)

        title_label = QLabel(APP_NAME, header_frame)
        title_label.setObjectName("headerTitle")
        title_box.addWidget(title_label)

        subtitle_label = QLabel(APP_SUBTITLE, header_frame)
        subtitle_label.setObjectName("headerSubtitle")
        title_box.addWidget(subtitle_label)

        header_layout.addLayout(title_box)
        header_layout.addStretch()

        root_layout.addWidget(header_frame)

        # 2. Main Input Bar (URL + Paste + Transcribe)
        self.url_input = UrlInputWidget(self)
        self.url_input.transcribe_requested.connect(self._start_transcription)
        root_layout.addWidget(self.url_input)

        # 3. Settings Panel (Language + Quality Preset)
        self.settings_panel = SettingsPanel(self)
        root_layout.addWidget(self.settings_panel)

        # 4. Progress Panel (Shown dynamically during processing)
        self.progress_panel = ProgressPanel(self)
        root_layout.addWidget(self.progress_panel)

        # 5. Transcript Results View (Expands to fill remaining window space)
        self.transcript_view = TranscriptView(self)
        root_layout.addWidget(self.transcript_view, stretch=1)

    def _start_transcription(self, url: str) -> None:
        """Validate URL and launch background transcription worker."""
        if self._active_worker and self._active_worker.isRunning():
            logger.warning("Attempted to start transcription while another job is active.")
            return

        if not is_valid_tiktok_url(url):
            self._show_error(
                "Enlace no válido",
                "No reconocemos este enlace de TikTok. Asegúrate de pegar un enlace público de TikTok (ej. https://www.tiktok.com/@usuario/video/...)",
            )
            return

        # Prepare UI for processing
        self.url_input.set_processing_state(True)
        self.settings_panel.set_enabled_state(False)
        self.progress_panel.reset()
        self.progress_panel.show()

        model_size = self.settings_panel.get_selected_model_size()
        language = self.settings_panel.get_selected_language_code()

        logger.info("Launching worker for model=%s, language=%s", model_size, language)

        # Create worker
        self._active_worker = TranscriptionWorker(
            url=url,
            model_size=model_size,
            language=language,
        )

        # Connect signals
        self._active_worker.status_changed.connect(self.progress_panel.set_status)
        self._active_worker.progress_changed.connect(self.progress_panel.set_progress)
        self._active_worker.transcription_completed.connect(self._on_transcription_completed)
        self._active_worker.error_occurred.connect(self._on_worker_error)
        self._active_worker.processing_finished.connect(self._on_worker_finished)

        self._active_worker.start()

    def _on_transcription_completed(self, result: TranscriptResult) -> None:
        """Handle successful transcription result."""
        logger.info("Displaying transcription result (%d words)", result.word_count)
        self.transcript_view.set_result(result)

    def _on_worker_error(self, user_message: str, technical_details: str) -> None:
        """Display friendly error dialog when worker encounters an issue."""
        logger.error("Job encountered error: %s (%s)", user_message, technical_details)
        self._show_error("No se pudo completar", user_message, technical_details)

    def _on_worker_finished(self) -> None:
        """Reset UI states after background job completes or errors."""
        self.url_input.set_processing_state(False)
        self.settings_panel.set_enabled_state(True)
        self.progress_panel.hide()
        self._active_worker = None

    def _show_error(self, title: str, user_message: str, technical_details: str = "") -> None:
        """Open modern error modal."""
        dialog = ErrorDialog(
            title=title,
            user_message=user_message,
            technical_details=technical_details,
            parent=self,
        )
        dialog.exec()

    def closeEvent(self, event: QCloseEvent) -> None:
        """Safely terminate worker thread if user closes the window."""
        if self._active_worker and self._active_worker.isRunning():
            logger.info("Window closing: cancelling active worker thread...")
            self._active_worker.cancel()
            self._active_worker.wait(2000)
            if self._active_worker.isRunning():
                self._active_worker.terminate()
        event.accept()
