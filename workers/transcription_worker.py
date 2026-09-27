"""Background worker thread for downloading, processing, and transcribing TikTok videos."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QThread, Signal

from core.audio_processor import AudioProcessor
from core.downloader import TikTokDownloader
from core.exceptions import TokTranscriptError
from core.transcriber import WhisperTranscriber
from models.transcript import TranscriptResult
from utils.paths import clean_temp_dir

logger = logging.getLogger("tok_transcript.worker")


class TranscriptionWorker(QThread):
    """QThread worker executing the end-to-end transcription pipeline asynchronously."""

    # Typed Qt signals
    processing_started = Signal()
    status_changed = Signal(str)
    progress_changed = Signal(int)
    transcription_completed = Signal(TranscriptResult)
    error_occurred = Signal(str, str)  # user_message, technical_details
    processing_finished = Signal()

    def __init__(
        self,
        url: str,
        model_size: str = "small",
        language: Optional[str] = None,
        device: str = "cpu",
        compute_type: str = "int8",
        parent=None,
    ):
        super().__init__(parent)
        self.url = url
        self.model_size = model_size
        self.language = language
        self.device = device
        self.compute_type = compute_type
        self._is_cancelled = False

    def cancel(self) -> None:
        """Request cooperative cancellation."""
        self._is_cancelled = True
        self.requestInterruption()

    def run(self) -> None:
        """Main worker execution loop."""
        logger.info("TranscriptionWorker started for URL: %s", self.url)
        self.processing_started.emit()

        downloaded_media: Optional[Path] = None
        normalized_audio: Optional[Path] = None

        try:
            # 1. Validation & Initialization
            self.status_changed.emit("Preparando...")
            self.progress_changed.emit(5)

            if self.isInterruptionRequested() or self._is_cancelled:
                return

            self.status_changed.emit("Validando enlace...")
            self.progress_changed.emit(10)

            # 2. Download audio
            self.status_changed.emit("Descargando audio...")
            downloader = TikTokDownloader()

            def _dl_progress(p: int) -> None:
                # Scale download progress to 10% - 40% of the overall bar
                overall = 10 + int(p * 0.30)
                self.progress_changed.emit(min(overall, 40))

            download_info = downloader.download_audio(self.url, progress_callback=_dl_progress)
            downloaded_media = download_info["file_path"]
            duration = download_info.get("duration", 0.0)

            if self.isInterruptionRequested() or self._is_cancelled:
                return

            # 3. Audio Normalization with FFmpeg
            self.status_changed.emit("Procesando audio...")
            self.progress_changed.emit(45)

            audio_proc = AudioProcessor()
            normalized_audio = audio_proc.prepare_for_whisper(downloaded_media)

            if self.isInterruptionRequested() or self._is_cancelled:
                return

            # 4. Transcription with faster-whisper
            self.status_changed.emit("Cargando modelo...")
            self.progress_changed.emit(50)

            transcriber = WhisperTranscriber(
                device=self.device,
                compute_type=self.compute_type,
            )

            def _transcription_progress(p: int) -> None:
                # Scale transcription progress from 50% to 95%
                overall = 50 + int(p * 0.45)
                self.progress_changed.emit(min(overall, 95))

            def _status_update(msg: str) -> None:
                self.status_changed.emit(msg)

            result = transcriber.transcribe(
                audio_path=normalized_audio,
                model_size=self.model_size,
                language=self.language,
                duration=duration,
                progress_callback=_transcription_progress,
                status_callback=_status_update,
            )

            if self.isInterruptionRequested() or self._is_cancelled:
                return

            # 5. Completion
            self.status_changed.emit("Preparando resultado...")
            self.progress_changed.emit(100)
            self.transcription_completed.emit(result)
            self.status_changed.emit("Completado")
            logger.info("TranscriptionWorker completed successfully.")

        except TokTranscriptError as err:
            logger.warning("Worker caught TokTranscriptError: %s", err)
            self.error_occurred.emit(err.user_message, err.technical_details)
        except Exception as err:
            logger.exception("Unexpected exception in worker thread: %s", err)
            self.error_occurred.emit(
                "Ocurrió un error inesperado durante el procesamiento.",
                str(err),
            )
        finally:
            # 6. Strict cleanup of temporary files
            clean_temp_dir()
            self.processing_finished.emit()
