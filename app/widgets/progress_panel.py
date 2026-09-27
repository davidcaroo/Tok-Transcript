"""Progress panel displaying live status and progress bar during processing."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)


class ProgressPanel(QWidget):
    """Panel showing progress percentage and human-friendly phase status."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self.container = QFrame(self)
        self.container.setObjectName("cardFrame")
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(16, 12, 16, 14)
        container_layout.setSpacing(10)

        # Header row: Status description + Percentage badge
        header_row = QHBoxLayout()
        self.status_label = QLabel("Preparando...", self.container)
        self.status_label.setObjectName("statusLabel")
        header_row.addWidget(self.status_label)

        header_row.addStretch()

        self.percentage_label = QLabel("0%", self.container)
        self.percentage_label.setObjectName("badgeLabel")
        header_row.addWidget(self.percentage_label)

        container_layout.addLayout(header_row)

        # Progress bar
        self.progress_bar = QProgressBar(self.container)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        container_layout.addWidget(self.progress_bar)

        layout.addWidget(self.container)

        # Initially hidden until transcription begins
        self.hide()

    def set_status(self, text: str) -> None:
        """Update current status description."""
        self.status_label.setText(text)

    def set_progress(self, percent: int) -> None:
        """Update current percentage (0-100)."""
        clamped = max(0, min(percent, 100))
        self.progress_bar.setValue(clamped)
        self.percentage_label.setText(f"{clamped}%")

    def reset(self) -> None:
        """Reset progress panel to initial state."""
        self.set_status("Preparando...")
        self.set_progress(0)
