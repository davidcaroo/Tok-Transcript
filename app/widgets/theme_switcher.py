"""Theme switcher widget with Sun (Light), Moon (Dark), and PC (System) buttons."""

from __future__ import annotations

from typing import Literal

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QPushButton,
    QWidget,
)

from utils.theme_manager import ThemeManager, ThemeMode


class ThemeSwitcherWidget(QWidget):
    """Segmented pill control for switching between Light, Dark, and System themes."""

    theme_changed = Signal(str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Container pill
        self.frame = QFrame(self)
        self.frame.setObjectName("themeSwitcher")
        frame_layout = QHBoxLayout(self.frame)
        frame_layout.setContentsMargins(3, 3, 3, 3)
        frame_layout.setSpacing(2)

        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)

        # 1. Light button (Sun)
        self.btn_light = QPushButton("☀️", self.frame)
        self.btn_light.setObjectName("themeButton")
        self.btn_light.setCheckable(True)
        self.btn_light.setCursor(Qt.PointingHandCursor)
        self.btn_light.setToolTip("Modo Claro")
        self.button_group.addButton(self.btn_light)
        frame_layout.addWidget(self.btn_light)

        # 2. Dark button (Moon)
        self.btn_dark = QPushButton("🌙", self.frame)
        self.btn_dark.setObjectName("themeButton")
        self.btn_dark.setCheckable(True)
        self.btn_dark.setCursor(Qt.PointingHandCursor)
        self.btn_dark.setToolTip("Modo Oscuro")
        self.button_group.addButton(self.btn_dark)
        frame_layout.addWidget(self.btn_dark)

        # 3. System button (PC)
        self.btn_system = QPushButton("💻", self.frame)
        self.btn_system.setObjectName("themeButton")
        self.btn_system.setCheckable(True)
        self.btn_system.setCursor(Qt.PointingHandCursor)
        self.btn_system.setToolTip("Modo Sistema (Detecta Windows)")
        self.button_group.addButton(self.btn_system)
        frame_layout.addWidget(self.btn_system)

        layout.addWidget(self.frame)

        # Connect signals
        self.btn_light.clicked.connect(lambda: self._on_mode_selected("light"))
        self.btn_dark.clicked.connect(lambda: self._on_mode_selected("dark"))
        self.btn_system.clicked.connect(lambda: self._on_mode_selected("system"))

        # Sync with saved mode
        saved_mode = ThemeManager.get_saved_mode()
        self.set_active_mode(saved_mode)

    def set_active_mode(self, mode: ThemeMode) -> None:
        """Update checked state of buttons without re-triggering signal."""
        if mode == "light":
            self.btn_light.setChecked(True)
        elif mode == "dark":
            self.btn_dark.setChecked(True)
        else:
            self.btn_system.setChecked(True)

    def _on_mode_selected(self, mode: ThemeMode) -> None:
        ThemeManager.apply_theme(mode)
        self.theme_changed.emit(mode)
