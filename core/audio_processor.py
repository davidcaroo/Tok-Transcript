"""Audio normalization and processing module using FFmpeg."""

from __future__ import annotations

import logging
from pathlib import Path
import subprocess
import sys
from typing import Optional
import uuid

from core.exceptions import AudioProcessingError, FFmpegNotFoundError
from utils.config import DEFAULT_SAMPLE_RATE
from utils.paths import get_temp_dir, resolve_ffmpeg_path

logger = logging.getLogger("tok_transcript.audio_processor")


class AudioProcessor:
    """Processes downloaded media and normalizes audio for Whisper transcription."""

    def __init__(self, ffmpeg_path: Optional[str] = None, temp_dir: Optional[Path] = None):
        self.ffmpeg_path = ffmpeg_path or resolve_ffmpeg_path()
        self.temp_dir = temp_dir or get_temp_dir()

    def ensure_ffmpeg(self) -> str:
        """Verify FFmpeg is available and return executable path."""
        if not self.ffmpeg_path or not Path(self.ffmpeg_path).exists():
            resolved = resolve_ffmpeg_path()
            if not resolved or not Path(resolved).exists():
                logger.error("FFmpeg could not be found.")
                raise FFmpegNotFoundError("FFmpeg no está instalado o no se encuentra en el sistema.")
            self.ffmpeg_path = resolved
        return self.ffmpeg_path

    def prepare_for_whisper(
        self,
        input_media_path: Path,
        sample_rate: int = DEFAULT_SAMPLE_RATE,
    ) -> Path:
        """Convert input media (video/audio) into a 16kHz mono WAV file.

        Args:
            input_media_path: Path to the raw downloaded video or audio.
            sample_rate: Target sample rate in Hz (default 16000).

        Returns:
            Path to the normalized WAV file in the temporary directory.

        Raises:
            FFmpegNotFoundError
            AudioProcessingError
        """
        ffmpeg_bin = self.ensure_ffmpeg()

        if not input_media_path.exists():
            raise AudioProcessingError(
                f"El archivo de entrada no existe: {input_media_path}"
            )

        output_filename = f"normalized_{uuid.uuid4().hex[:8]}.wav"
        output_path = self.temp_dir / output_filename

        # Command: ffmpeg -y -i <input> -vn -acodec pcm_s16le -ar 16000 -ac 1 <output>
        command = [
            ffmpeg_bin,
            "-y",  # Overwrite output without asking
            "-i", str(input_media_path),
            "-vn",  # Disable video recording
            "-acodec", "pcm_s16le",  # Standard 16-bit PCM
            "-ar", str(sample_rate),  # Sample rate 16000 Hz
            "-ac", "1",  # Mono channel
            str(output_path),
        ]

        logger.info("Executing audio conversion with FFmpeg: %s -> %s", input_media_path.name, output_filename)

        creationflags = 0
        if sys.platform == "win32":
            creationflags = subprocess.CREATE_NO_WINDOW

        try:
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
                shell=False,
                creationflags=creationflags,
                timeout=120,  # Max 2 minutes for audio normalization
            )

            if result.returncode != 0:
                logger.error("FFmpeg failed with exit code %d: %s", result.returncode, result.stderr)
                raise AudioProcessingError(
                    f"FFmpeg falló al procesar el audio (código {result.returncode}).",
                    technical_details=result.stderr[-500:] if result.stderr else "",
                )

            if not output_path.exists() or output_path.stat().st_size == 0:
                raise AudioProcessingError("El archivo de audio normalizado no fue generado o está vacío.")

            logger.info("Audio normalized successfully: %s (%d bytes)", output_path.name, output_path.stat().st_size)
            return output_path

        except subprocess.TimeoutExpired as err:
            logger.error("FFmpeg process timed out: %s", err)
            raise AudioProcessingError("El procesamiento de audio excedió el tiempo límite.") from err
        except (FFmpegNotFoundError, AudioProcessingError):
            raise
        except Exception as err:
            logger.exception("Unexpected error during audio processing: %s", err)
            raise AudioProcessingError("Error inesperado al normalizar el audio.", technical_details=str(err)) from err
