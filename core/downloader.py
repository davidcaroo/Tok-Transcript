"""TikTok audio and video downloader powered by yt-dlp."""

from __future__ import annotations

import logging
from pathlib import Path
import tempfile
from typing import Any, Callable, Dict, Optional
import uuid

import yt_dlp

from core.exceptions import (
    InvalidURLError,
    NetworkError,
    PrivateVideoError,
    TokTranscriptError,
    VideoUnavailableError,
)
from utils.paths import get_temp_dir, resolve_ffmpeg_path
from utils.validators import is_valid_tiktok_url, sanitize_url

logger = logging.getLogger("tok_transcript.downloader")


class TikTokDownloader:
    """Handles downloading audio tracks from public TikTok videos."""

    def __init__(self, temp_dir: Optional[Path] = None):
        self.temp_dir = temp_dir or get_temp_dir()

    def download_audio(
        self,
        url: str,
        progress_callback: Optional[Callable[[int], None]] = None,
    ) -> Dict[str, Any]:
        """Download only the required audio for the given TikTok URL.

        Args:
            url: The public TikTok video URL.
            progress_callback: Optional callback receiving progress percentage (0-100).

        Returns:
            Dict containing:
                - 'file_path': Path to the downloaded audio/media file.
                - 'title': Video title/description if available.
                - 'duration': Video duration in seconds.
                - 'id': TikTok video ID.

        Raises:
            InvalidURLError
            PrivateVideoError
            VideoUnavailableError
            NetworkError
            TokTranscriptError
        """
        clean_url = sanitize_url(url)
        if not is_valid_tiktok_url(clean_url):
            logger.warning("Invalid TikTok URL provided: %s", clean_url)
            raise InvalidURLError(f"URL no válida: {clean_url}")

        unique_id = uuid.uuid4().hex[:8]
        output_template = str(self.temp_dir / f"tt_{unique_id}_%(id)s.%(ext)s")

        def _progress_hook(d: Dict[str, Any]) -> None:
            if not progress_callback:
                return
            status = d.get("status")
            if status == "downloading":
                total_bytes = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
                downloaded_bytes = d.get("downloaded_bytes") or 0
                if total_bytes > 0:
                    percent = int((downloaded_bytes / total_bytes) * 100)
                    progress_callback(min(percent, 99))
            elif status == "finished":
                progress_callback(100)

        ydl_opts: Dict[str, Any] = {
            "format": "bestaudio/best",
            "outtmpl": output_template,
            "quiet": True,
            "no_warnings": True,
            "progress_hooks": [_progress_hook],
            "noplaylist": True,
            "socket_timeout": 15,
            "retries": 3,
        }

        ffmpeg_bin = resolve_ffmpeg_path()
        if ffmpeg_bin:
            ydl_opts["ffmpeg_location"] = str(Path(ffmpeg_bin).parent)

        logger.info("Starting download for URL: %s", clean_url)

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(clean_url, download=True)
                if not info:
                    raise VideoUnavailableError("No se obtuvo información del video.")

                # Determine the resulting filepath
                downloaded_path = None
                if "requested_downloads" in info and info["requested_downloads"]:
                    downloaded_path = Path(info["requested_downloads"][0]["filepath"])
                else:
                    # Fallback to prepare_filename
                    downloaded_path = Path(ydl.prepare_filename(info))

                if not downloaded_path.exists():
                    # Check any files matching pattern in temp dir
                    candidates = list(self.temp_dir.glob(f"tt_{unique_id}_*"))
                    if candidates:
                        downloaded_path = candidates[0]
                    else:
                        raise VideoUnavailableError("El archivo descargado no fue encontrado en disco.")

                logger.info("Download completed successfully: %s", downloaded_path)
                return {
                    "file_path": downloaded_path,
                    "title": info.get("title", "TikTok Video"),
                    "duration": float(info.get("duration") or 0.0),
                    "id": info.get("id", ""),
                }

        except yt_dlp.utils.DownloadError as err:
            err_msg = str(err).lower()
            logger.error("yt-dlp DownloadError: %s", err)
            if "private" in err_msg or "login" in err_msg:
                raise PrivateVideoError(str(err)) from err
            elif "unavailable" in err_msg or "not found" in err_msg or "404" in err_msg:
                raise VideoUnavailableError(str(err)) from err
            elif "connection" in err_msg or "timed out" in err_msg or "network" in err_msg:
                raise NetworkError(str(err)) from err
            else:
                raise VideoUnavailableError(str(err)) from err
        except (InvalidURLError, PrivateVideoError, VideoUnavailableError, NetworkError):
            raise
        except Exception as err:
            logger.exception("Unexpected error downloading TikTok video: %s", err)
            raise TokTranscriptError("Error inesperado al descargar el video.", technical_details=str(err)) from err
