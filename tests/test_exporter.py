"""Unit tests for TXT, SRT, and VTT exporters."""

import tempfile
from pathlib import Path
from models.transcript import TranscriptResult, TranscriptSegment
from core.exporter import export_txt, export_srt, export_vtt, format_timestamp_srt, format_timestamp_vtt


def test_timestamp_formatting():
    # 0 seconds
    assert format_timestamp_srt(0.0) == "00:00:00,000"
    assert format_timestamp_vtt(0.0) == "00:00:00.000"

    # 65.5 seconds = 1 minute, 5 seconds, 500 ms
    assert format_timestamp_srt(65.5) == "00:01:05,500"
    assert format_timestamp_vtt(65.5) == "00:01:05.500"

    # 3661.123 seconds = 1 hour, 1 minute, 1 second, 123 ms
    assert format_timestamp_srt(3661.123) == "01:01:01,123"
    assert format_timestamp_vtt(3661.123) == "01:01:01.123"


def test_export_txt_srt_vtt():
    segments = [
        TranscriptSegment(start=0.0, end=2.45, text="Hola a todos"),
        TranscriptSegment(start=2.5, end=5.12, text="Bienvenidos a este tutorial"),
    ]
    result = TranscriptResult(
        text="Hola a todos Bienvenidos a este tutorial",
        language="es",
        duration=5.12,
        segments=segments,
    )

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        
        # TXT
        txt_path = export_txt(result, tmp_path / "output.txt")
        assert txt_path.exists()
        txt_content = txt_path.read_text(encoding="utf-8")
        assert "Hola a todos Bienvenidos a este tutorial" in txt_content

        # SRT
        srt_path = export_srt(result, tmp_path / "output.srt")
        assert srt_path.exists()
        srt_content = srt_path.read_text(encoding="utf-8")
        assert "1\n00:00:00,000 --> 00:00:02,450\nHola a todos" in srt_content
        assert "2\n00:00:02,500 --> 00:00:05,120\nBienvenidos a este tutorial" in srt_content

        # VTT
        vtt_path = export_vtt(result, tmp_path / "output.vtt")
        assert vtt_path.exists()
        vtt_content = vtt_path.read_text(encoding="utf-8")
        assert vtt_content.startswith("WEBVTT")
        assert "00:00:00.000 --> 00:00:02.450" in vtt_content
