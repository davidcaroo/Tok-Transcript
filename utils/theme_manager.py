"""Theme management for Tok-Transcript supporting Dark, Light, and System modes."""

from __future__ import annotations

import logging
from typing import Literal

import darkdetect
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication

from utils.paths import get_assets_path

logger = logging.getLogger("tok_transcript.theme")

ThemeMode = Literal["system", "dark", "light"]


class ThemeManager:
    """Manages application stylesheet switching and persistence."""

    SETTINGS_KEY = "ui/theme_mode"

    @classmethod
    def get_saved_mode(cls) -> ThemeMode:
        """Retrieve persisted theme mode from QSettings, defaulting to 'system'."""
        settings = QSettings("TokTranscript", "TokTranscript")
        mode = settings.value(cls.SETTINGS_KEY, "system")
        if mode in ("system", "dark", "light"):
            return mode
        return "system"

    @classmethod
    def save_mode(cls, mode: ThemeMode) -> None:
        """Persist selected theme mode to QSettings."""
        settings = QSettings("TokTranscript", "TokTranscript")
        settings.setValue(cls.SETTINGS_KEY, mode)

    @classmethod
    def get_effective_theme(cls, mode: ThemeMode) -> Literal["dark", "light"]:
        """Determine whether dark or light theme should be rendered."""
        if mode == "system":
            is_dark = darkdetect.isDark()
            return "dark" if is_dark is not False else "light"
        return mode

    @classmethod
    def load_stylesheet(cls, theme: Literal["dark", "light"]) -> str:
        """Load corresponding QSS file."""
        filename = f"{theme}.qss"
        path = get_assets_path() / "styles" / filename
        if not path.exists():
            # Fallback to app.qss
            path = get_assets_path() / "styles" / "app.qss"
        try:
            return path.read_text(encoding="utf-8")
        except Exception as err:
            logger.error("Failed to read stylesheet %s: %s", path, err)
            return ""

    @classmethod
    def apply_theme(cls, mode: ThemeMode, app: QApplication | None = None) -> Literal["dark", "light"]:
        """Apply theme to QApplication and save preference."""
        if app is None:
            app = QApplication.instance()
        cls.save_mode(mode)
        effective = cls.get_effective_theme(mode)
        qss = cls.load_stylesheet(effective)
        if app and qss:
            app.setStyleSheet(qss)
        logger.info("Applied theme mode '%s' (effective: %s)", mode, effective)
        return effective
