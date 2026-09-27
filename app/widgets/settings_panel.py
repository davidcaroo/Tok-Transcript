"""Settings panel for selecting transcription language and quality/speed preset."""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from utils.config import (
    DEFAULT_LANGUAGE,
    DEFAULT_QUALITY,
    LANGUAGE_PRESETS,
    QUALITY_PRESETS,
)


class SettingsPanel(QWidget):
    """Clean segmented controls for Language and Whisper model quality preset."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self) -> None:
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(16)

        # Container frame
        container = QFrame(self)
        container.setObjectName("innerCardFrame")
        layout = QHBoxLayout(container)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(24)

        # --- Language Selection ---
        lang_group = QHBoxLayout()
        lang_group.setSpacing(8)
        lang_label = QLabel("Idioma:", container)
        lang_label.setStyleSheet("color: #94a3b8; font-weight: 500;")
        
        self.lang_combo = QComboBox(container)
        for label in LANGUAGE_PRESETS.keys():
            self.lang_combo.addItem(label)
        self.lang_combo.setCurrentText(DEFAULT_LANGUAGE)
        self.lang_combo.setCursor(Qt.PointingHandCursor)

        lang_group.addWidget(lang_label)
        lang_group.addWidget(self.lang_combo)
        layout.addLayout(lang_group)

        # --- Quality / Speed Selection ---
        quality_group = QHBoxLayout()
        quality_group.setSpacing(8)
        quality_label = QLabel("Calidad:", container)
        quality_label.setStyleSheet("color: #94a3b8; font-weight: 500;")

        self.quality_combo = QComboBox(container)
        for label in QUALITY_PRESETS.keys():
            self.quality_combo.addItem(label)
        self.quality_combo.setCurrentText(DEFAULT_QUALITY)
        self.quality_combo.setCursor(Qt.PointingHandCursor)

        quality_group.addWidget(quality_label)
        quality_group.addWidget(self.quality_combo)
        layout.addLayout(quality_group)

        layout.addStretch()
        main_layout.addWidget(container)

    def get_selected_language_code(self) -> Optional[str]:
        """Return the ISO language code or None for automatic detection."""
        label = self.lang_combo.currentText()
        return LANGUAGE_PRESETS.get(label, None)

    def get_selected_model_size(self) -> str:
        """Return the faster-whisper model identifier ('base', 'small', 'medium')."""
        label = self.quality_combo.currentText()
        return QUALITY_PRESETS.get(label, "small")

    def set_enabled_state(self, enabled: bool) -> None:
        """Enable or disable configuration controls during active jobs."""
        self.lang_combo.setEnabled(enabled)
        self.quality_combo.setEnabled(enabled)
