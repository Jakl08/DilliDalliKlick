"""Main menu window."""

from collections.abc import Callable

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton


class MenuWindow(QWidget):
    """Application entry screen with navigation buttons."""

    def __init__(
        self,
        on_open_settings: Callable[[], None],
        on_open_photobooks: Callable[[], None],
    ) -> None:
        super().__init__()
        self._on_open_settings = on_open_settings
        self._on_open_photobooks = on_open_photobooks
        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.setSpacing(0)
        root.setContentsMargins(40, 40, 40, 40)

        # Logo
        logo = QLabel("DilliDalliKlick")
        logo_font = QFont()
        logo_font.setPointSize(40)
        logo_font.setBold(True)
        logo.setFont(logo_font)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet("color: #e94560; letter-spacing: 4px; margin-bottom: 8px;")
        root.addWidget(logo)

        subtitle = QLabel("Das Foto-Enthüllungsspiel")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #a0a0b0; font-size: 16px; margin-bottom: 48px;")
        root.addWidget(subtitle)

        btn_start = self._make_button("▶  Spiel starten", "primary", 240, 54)
        btn_start.clicked.connect(self._on_open_settings)
        root.addWidget(btn_start, alignment=Qt.AlignmentFlag.AlignCenter)

        root.addSpacing(14)

        btn_books = self._make_button("📚  Fotobücher verwalten", "info", 240, 54)
        btn_books.clicked.connect(self._on_open_photobooks)
        root.addWidget(btn_books, alignment=Qt.AlignmentFlag.AlignCenter)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _make_button(text: str, style_class: str, width: int, height: int) -> QPushButton:
        btn = QPushButton(text)
        btn.setProperty("class", style_class)
        btn.setFixedSize(width, height)
        font = QFont()
        font.setPointSize(13)
        btn.setFont(font)
        btn.style().unpolish(btn)
        btn.style().polish(btn)
        return btn
