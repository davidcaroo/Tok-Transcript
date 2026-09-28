"""Custom exceptions for the Tok-Transcript application.

Provides clean separation between user-facing friendly error messages
and technical diagnosis details.
"""

from __future__ import annotations


class TokTranscriptError(Exception):
    """Base exception for all Tok-Transcript errors."""

    def __init__(self, user_message: str = "Ocurrió un error en Tok-Transcript.", technical_details: str = ""):
        super().__init__(user_message)
        self.user_message = user_message
        self.technical_details = technical_details

    def __str__(self) -> str:
        if self.technical_details:
            return f"{self.user_message} (Detalles: {self.technical_details})"
        return self.user_message


class InvalidURLError(TokTranscriptError):
    """Raised when the provided URL is not a recognized TikTok link."""

    def __init__(
        self,
        user_message: str = "No reconocemos este enlace de TikTok. Verifica que la URL sea válida.",
        technical_details: str = "",
    ):
        super().__init__(user_message=user_message, technical_details=technical_details)


class VideoUnavailableError(TokTranscriptError):
    """Raised when the TikTok video cannot be accessed or was deleted."""

    def __init__(
        self,
        user_message: str = "No fue posible acceder a este video. Puede haber sido eliminado o no está disponible.",
        technical_details: str = "",
    ):
        super().__init__(user_message=user_message, technical_details=technical_details)


class PrivateVideoError(TokTranscriptError):
    """Raised when the video is private or restricted."""

    def __init__(
        self,
        user_message: str = "Este video es privado o tiene restricciones de privacidad.",
        technical_details: str = "",
    ):
        super().__init__(user_message=user_message, technical_details=technical_details)


class NetworkError(TokTranscriptError):
    """Raised when network connectivity fails during download or model setup."""

    def __init__(
        self,
        user_message: str = "Error de conexión a internet. Revisa tu conexión de red e intenta nuevamente.",
        technical_details: str = "",
    ):
        super().__init__(user_message=user_message, technical_details=technical_details)


class FFmpegNotFoundError(TokTranscriptError):
    """Raised when FFmpeg binary cannot be resolved."""

    def __init__(
        self,
        user_message: str = "No se encontró FFmpeg en el sistema para procesar el audio.",
        technical_details: str = "",
    ):
        super().__init__(user_message=user_message, technical_details=technical_details)


class AudioProcessingError(TokTranscriptError):
    """Raised when audio conversion or normalization fails."""

    def __init__(
        self,
        user_message: str = "No fue posible procesar el audio del video para la transcripción.",
        technical_details: str = "",
    ):
        super().__init__(user_message=user_message, technical_details=technical_details)


class TranscriptionError(TokTranscriptError):
    """Raised when faster-whisper fails during transcription."""

    def __init__(
        self,
        user_message: str = "No fue posible completar la transcripción local del audio.",
        technical_details: str = "",
    ):
        super().__init__(user_message=user_message, technical_details=technical_details)
