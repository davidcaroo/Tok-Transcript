"""Path management and system resource resolution for Tok-Transcript.

Supports both standard Python development mode and PyInstaller packaged execution.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
import shutil
import sys
from typing import Optional

logger = logging.getLogger("tok_transcript.paths")


def is_frozen() -> bool:
    """Check if the application is running as a packaged PyInstaller executable."""
    return getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")


def get_app_root() -> Path:
    """Return the root directory of the application.

    In development: the repository root folder.
    In packaged exe: the temporary extraction directory (_MEIPASS) or exe folder.
    """
    if is_frozen():
        return Path(getattr(sys, "_MEIPASS"))
    # In development, paths.py is in utils/ -> parent.parent is project root
    return Path(__file__).resolve().parent.parent


def get_user_data_dir() -> Path:
    """Return a persistent directory for writable application data (logs, temp)."""
    if is_frozen():
        base = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "TokTranscript"
    else:
        base = get_app_root()
    base.mkdir(parents=True, exist_ok=True)
    return base


def get_assets_path() -> Path:
    """Return the assets directory containing icons and styles."""
    return get_app_root() / "assets"


def get_temp_dir() -> Path:
    """Return the temporary directory for downloading and converting audio."""
    temp_dir = get_user_data_dir() / "temp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    return temp_dir


def get_logs_dir() -> Path:
    """Return the directory where log files are stored."""
    logs_dir = get_user_data_dir() / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir


def clean_temp_dir() -> None:
    """Remove all intermediate files from the temporary directory safely."""
    temp_dir = get_temp_dir()
    if not temp_dir.exists():
        return
    for item in temp_dir.iterdir():
        try:
            if item.is_file() or item.is_symlink():
                item.unlink(missing_ok=True)
            elif item.is_dir():
                shutil.rmtree(item, ignore_errors=True)
        except Exception as err:
            logger.warning("Failed to remove temp file %s: %s", item, err)


def resolve_ffmpeg_path() -> Optional[str]:
    """Find FFmpeg executable in bundled assets, PATH, or fallback provider.

    Resolution order:
    1. Bundled in assets/bin/ffmpeg.exe (packaged or manual drop-in)
    2. System PATH (ffmpeg / ffmpeg.exe)
    3. imageio-ffmpeg library bundled binary (if installed)
    """
    # 1. Bundled folder
    bundled_ffmpeg = get_app_root() / "assets" / "bin" / ("ffmpeg.exe" if sys.platform == "win32" else "ffmpeg")
    if bundled_ffmpeg.exists() and os.access(str(bundled_ffmpeg), os.X_OK):
        return str(bundled_ffmpeg)

    # 2. System PATH
    system_ffmpeg = shutil.which("ffmpeg") or shutil.which("ffmpeg.exe")
    if system_ffmpeg:
        return system_ffmpeg

    # 3. imageio-ffmpeg package
    try:
        import imageio_ffmpeg
        exe_path = imageio_ffmpeg.get_ffmpeg_exe()
        if exe_path and os.path.exists(exe_path):
            return exe_path
    except ImportError:
        pass

    return None
