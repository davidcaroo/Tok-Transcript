"""Unit tests for path resolution and temporary directory cleanup."""

from pathlib import Path
from utils.paths import get_app_root, get_temp_dir, clean_temp_dir, resolve_ffmpeg_path


def test_paths_exist():
    root = get_app_root()
    assert root.exists()
    assert (root / "utils").exists()

    temp_dir = get_temp_dir()
    assert temp_dir.exists()


def test_clean_temp_dir():
    temp_dir = get_temp_dir()
    dummy_file = temp_dir / "dummy_test.txt"
    dummy_file.write_text("temporary data", encoding="utf-8")
    assert dummy_file.exists()

    clean_temp_dir()
    assert not dummy_file.exists()


def test_resolve_ffmpeg():
    # Should resolve either system or imageio-ffmpeg or bundled
    ffmpeg_bin = resolve_ffmpeg_path()
    assert ffmpeg_bin is not None
    assert Path(ffmpeg_bin).exists()
