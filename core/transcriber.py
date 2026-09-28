"""Local speech transcription service powered by faster-whisper."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Callable, ClassVar, Dict, Optional, Tuple

from faster_whisper import WhisperModel

from core.exceptions import TranscriptionError
from models.transcript import TranscriptResult, TranscriptSegment
from utils.config import DEFAULT_COMPUTE_TYPE, DEFAULT_DEVICE

logger = logging.getLogger("tok_transcript.transcriber")


class WhisperTranscriber:
    """Manages Whisper model instances and performs local audio transcription."""

    # In-memory session cache of models: key is (model_size, device, compute_type)
    _model_cache: ClassVar[Dict[Tuple[str, str, str], WhisperModel]] = {}

    def __init__(
        self,
        default_model_size: str = "small",
        device: str = DEFAULT_DEVICE,
        compute_type: str = DEFAULT_COMPUTE_TYPE,
    ):
        self.default_model_size = default_model_size
        self.device = device
        self.compute_type = compute_type

    def get_model(
        self,
        model_size: str,
        status_callback: Optional[Callable[[str], None]] = None,
    ) -> WhisperModel:
        """Retrieve a cached WhisperModel or load it from disk/HuggingFace."""
        cache_key = (model_size, self.device, self.compute_type)
        if cache_key in self._model_cache:
            logger.info("Using cached Whisper model: %s", model_size)
            return self._model_cache[cache_key]

        logger.info("Loading Whisper model: %s (device=%s, compute_type=%s)", model_size, self.device, self.compute_type)
        if status_callback:
            status_callback("Descargando motor de IA por primera vez (~460 MB, solo una vez)...")

        # Clean stale lock files from previous aborted sessions to prevent indefinite hangs
        try:
            locks_dir = Path.home() / ".cache" / "huggingface" / "hub" / ".locks"
            if locks_dir.exists():
                import shutil
                shutil.rmtree(locks_dir, ignore_errors=True)
        except Exception as lock_err:
            logger.debug("Non-critical error clearing HF locks: %s", lock_err)

        try:
            model = WhisperModel(
                model_size_or_path=model_size,
                device=self.device,
                compute_type=self.compute_type,
                cpu_threads=4,
            )
            self._model_cache[cache_key] = model
            logger.info("Whisper model loaded and cached: %s", model_size)
            return model
        except Exception as err:
            logger.exception("Failed to load faster-whisper model '%s': %s", model_size, err)
            raise TranscriptionError(
                f"No fue posible cargar el modelo de transcripción '{model_size}'.",
                technical_details=str(err),
            ) from err

    def transcribe(
        self,
        audio_path: Path,
        model_size: str = "small",
        language: Optional[str] = None,
        duration: float = 0.0,
        progress_callback: Optional[Callable[[int], None]] = None,
        status_callback: Optional[Callable[[str], None]] = None,
    ) -> TranscriptResult:
        """Transcribe a normalized audio file using faster-whisper.

        Args:
            audio_path: Path to the normalized WAV audio file.
            model_size: Whisper model size ('base', 'small', 'medium').
            language: Optional language code ('es', 'en') or None for auto-detect.
            duration: Video duration in seconds for progress estimation.
            progress_callback: Callback receiving progress (0-100).
            status_callback: Callback receiving user-facing status messages.

        Returns:
            TranscriptResult with text, segments, language, and duration.
        """
        if not audio_path.exists():
            raise TranscriptionError(f"El archivo de audio a transcribir no existe: {audio_path}")

        model = self.get_model(model_size, status_callback=status_callback)

        if status_callback:
            status_callback("Transcribiendo audio...")

        try:
            # transcribe returns a generator of segments and info
            segments_gen, info = model.transcribe(
                str(audio_path),
                language=language,
                beam_size=5,
                vad_filter=True,  # Voice activity detection to skip silence
                vad_parameters=dict(min_silence_duration_ms=500),
            )

            detected_lang = info.language
            total_duration = duration if duration > 0 else (info.duration or 0.0)
            logger.info("Transcription started. Detected language: %s, duration: %.2fs", detected_lang, total_duration)

            segments_list = []
            text_parts = []

            for seg in segments_gen:
                clean_text = seg.text.strip()
                if clean_text:
                    segment_obj = TranscriptSegment(
                        start=float(seg.start),
                        end=float(seg.end),
                        text=clean_text,
                    )
                    segments_list.append(segment_obj)
                    text_parts.append(clean_text)

                # Report progress based on timestamp reached vs total duration
                if progress_callback and total_duration > 0:
                    pct = int((seg.end / total_duration) * 100)
                    progress_callback(min(max(pct, 5), 98))

            full_text = " ".join(text_parts).strip()
            effective_duration = total_duration
            if not effective_duration and segments_list:
                effective_duration = segments_list[-1].end

            if progress_callback:
                progress_callback(100)

            logger.info("Transcription finished. Total segments: %d, word count: %d", len(segments_list), len(full_text.split()))

            return TranscriptResult(
                text=full_text,
                language=detected_lang,
                duration=effective_duration,
                segments=segments_list,
            )

        except TranscriptionError:
            raise
        except Exception as err:
            logger.exception("Error during faster-whisper transcription: %s", err)
            raise TranscriptionError(
                "Ocurrió un error durante la transcripción del audio.",
                technical_details=str(err),
            ) from err
