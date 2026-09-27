"""Application entry point for Tok-Transcript."""

from __future__ import annotations

import logging
import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from app.main_window import MainWindow
from utils.config import APP_NAME
from utils.logger import setup_logger
from utils.paths import get_assets_path


def load_stylesheet() -> str:
    """Load QSS stylesheet from assets/styles/app.qss."""
    qss_path = get_assets_path() / "styles" / "app.qss"
    if qss_path.exists():
        try:
            return qss_path.read_text(encoding="utf-8")
        except Exception as err:
            logging.getLogger("tok_transcript").warning("Could not read stylesheet: %s", err)
    return ""


def main() -> None:
    """Initialize application, configure logger, load stylesheet, and run event loop."""
    logger = setup_logger()
    logger.info("Initializing %s...", APP_NAME)

    # Enable High DPI attributes
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationDisplayName(APP_NAME)

    # Apply saved theme (System / Dark / Light)
    from utils.theme_manager import ThemeManager
    saved_mode = ThemeManager.get_saved_mode()
    ThemeManager.apply_theme(saved_mode, app)

    window = MainWindow()
    window.show()

    logger.info("Main window displayed. Starting event loop.")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
