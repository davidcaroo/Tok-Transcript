"""Exporters for transcript results into TXT, SRT, and VTT formats."""

from __future__ import annotations

from pathlib import Path
from typing import Union

from models.transcript import TranscriptResult, TranscriptSegment


def format_timestamp_srt(seconds: float) -> str:
    """Format seconds into SRT timestamp: HH:MM:SS,mmm."""
    if seconds < 0:
        seconds = 0.0
    total_msec = int(round(seconds * 1000))
    hours = total_msec // 3_600_000
    minutes = (total_msec % 3_600_000) // 60_000
    secs = (total_msec % 60_000) // 1_000
    msec = total_msec % 1_000
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{msec:03d}"


def format_timestamp_vtt(seconds: float) -> str:
    """Format seconds into WebVTT timestamp: HH:MM:SS.mmm."""
    if seconds < 0:
        seconds = 0.0
    total_msec = int(round(seconds * 1000))
    hours = total_msec // 3_600_000
    minutes = (total_msec % 3_600_000) // 60_000
    secs = (total_msec % 60_000) // 1_000
    msec = total_msec % 1_000
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{msec:03d}"


def export_txt(result: TranscriptResult, target_path: Union[str, Path]) -> Path:
    """Export clean text to a .txt file encoded in UTF-8."""
    path = Path(target_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(result.text.strip() + "\n", encoding="utf-8")
    return path


def export_srt(result: TranscriptResult, target_path: Union[str, Path]) -> Path:
    """Export timestamped segments to a SubRip (.srt) file encoded in UTF-8."""
    path = Path(target_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    lines = []
    # If no segments exist, create a single fallback segment with full duration
    segments = result.segments
    if not segments and result.text.strip():
        segments = [TranscriptSegment(start=0.0, end=result.duration, text=result.text.strip())]

    for index, segment in enumerate(segments, start=1):
        lines.append(str(index))
        lines.append(f"{format_timestamp_srt(segment.start)} --> {format_timestamp_srt(segment.end)}")
        lines.append(segment.text.strip())
        lines.append("")  # Blank line separator

    content = "\n".join(lines).strip() + "\n"
    path.write_text(content, encoding="utf-8")
    return path


def export_vtt(result: TranscriptResult, target_path: Union[str, Path]) -> Path:
    """Export timestamped segments to a WebVTT (.vtt) file encoded in UTF-8."""
    path = Path(target_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    lines = ["WEBVTT", ""]
    segments = result.segments
    if not segments and result.text.strip():
        segments = [TranscriptSegment(start=0.0, end=result.duration, text=result.text.strip())]

    for index, segment in enumerate(segments, start=1):
        lines.append(str(index))
        lines.append(f"{format_timestamp_vtt(segment.start)} --> {format_timestamp_vtt(segment.end)}")
        lines.append(segment.text.strip())
        lines.append("")

    content = "\n".join(lines).strip() + "\n"
    path.write_text(content, encoding="utf-8")
    return path
