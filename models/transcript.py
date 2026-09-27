"""Data models for transcription results and segments."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class TranscriptSegment:
    """Represents an individual subtitle/timestamped segment of the transcription."""

    start: float
    end: float
    text: str

    @property
    def duration(self) -> float:
        return max(0.0, self.end - self.start)


@dataclass(frozen=True)
class TranscriptResult:
    """Comprehensive representation of a completed transcription."""

    text: str
    language: str
    duration: float
    segments: List[TranscriptSegment] = field(default_factory=list)

    @property
    def word_count(self) -> int:
        """Calculate approximate word count from full transcript text."""
        words = self.text.split()
        return len(words)

    @property
    def formatted_duration(self) -> str:
        """Format total duration in MM:SS or HH:MM:SS."""
        total_seconds = int(round(self.duration))
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return f"{minutes:02d}:{seconds:02d}"

    @property
    def language_label(self) -> str:
        """Return human-readable label for detected language code."""
        lang_names = {
            "es": "Español",
            "en": "Inglés",
            "fr": "Francés",
            "de": "Alemán",
            "it": "Italiano",
            "pt": "Portugués",
            "ja": "Japonés",
            "zh": "Chino",
            "ko": "Coreano",
            "ru": "Ruso",
            "ar": "Árabe",
        }
        return lang_names.get(self.language.lower(), self.language.upper())
