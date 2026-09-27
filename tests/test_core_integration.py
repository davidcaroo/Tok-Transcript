"""Integration tests for audio processing and core pipeline components."""

import wave
import struct
from pathlib import Path
import pytest
from core.audio_processor import AudioProcessor
from core.downloader import TikTokDownloader
from core.exceptions import InvalidURLError, AudioProcessingError
from utils.paths import get_temp_dir


def create_synthetic_wav(path: Path, duration_sec: float = 1.0, sample_rate: int = 44100):
    """Generate a clean synthetic sine/silence WAV file for testing conversion."""
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(2)  # Stereo
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sample_rate)
        # 1 second of silence / minimal tone
        num_frames = int(sample_rate * duration_sec)
        data = struct.pack(f"<{num_frames * 2}h", *([0] * (num_frames * 2)))
        wf.writeframes(data)


def test_downloader_invalid_url():
    downloader = TikTokDownloader()
    with pytest.raises(InvalidURLError):
        downloader.download_audio("https://invalid-url.com/something")


def test_audio_processor_ffmpeg_conversion(tmp_path):
    # Create input stereo 44.1kHz WAV
    raw_audio = tmp_path / "raw_stereo.wav"
    create_synthetic_wav(raw_audio, duration_sec=1.5, sample_rate=44100)
    assert raw_audio.exists()

    processor = AudioProcessor(temp_dir=tmp_path)
    normalized = processor.prepare_for_whisper(raw_audio)

    assert normalized.exists()
    assert normalized.suffix == ".wav"

    # Verify normalized file specs: 16000 Hz, mono (1 channel), 16-bit
    with wave.open(str(normalized), "rb") as wf:
        assert wf.getnchannels() == 1  # Mono
        assert wf.getframerate() == 16000  # 16kHz
        assert wf.getsampwidth() == 2  # 16-bit PCM


def test_audio_processor_missing_file(tmp_path):
    processor = AudioProcessor(temp_dir=tmp_path)
    with pytest.raises(AudioProcessingError):
        processor.prepare_for_whisper(tmp_path / "non_existent_audio.mp4")
