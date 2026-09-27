"""Application configuration, constants, and quality/language presets."""

from __future__ import annotations

from typing import Dict, Optional

APP_NAME = "Tok-Transcript"
APP_SUBTITLE = "Convierte videos de TikTok en texto."
APP_VERSION = "1.0.0"
EXECUTABLE_NAME = "TokTranscript.exe"

# Model presets mapping user-facing labels to Whisper model identifiers
QUALITY_PRESETS: Dict[str, str] = {
    "Rápido": "base",
    "Equilibrado": "small",
    "Alta precisión": "medium",
}

DEFAULT_QUALITY = "Equilibrado"

# Language presets mapping user-facing labels to ISO language codes (or None for auto-detect)
LANGUAGE_PRESETS: Dict[str, Optional[str]] = {
    "Automático": None,
    "Español": "es",
    "Inglés": "en",
}

DEFAULT_LANGUAGE = "Automático"

# Audio & Whisper defaults
DEFAULT_DEVICE = "cpu"
DEFAULT_COMPUTE_TYPE = "int8"
DEFAULT_SAMPLE_RATE = 16000  # Optimal for Whisper models
