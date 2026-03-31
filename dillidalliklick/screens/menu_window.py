"""Main menu window."""

from collections.abc import Callable

from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices, QFont
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout

from dillidalliklick.constants import theme


class MenuWindow(QWidget):
    """Application entry screen with navigation buttons."""

    _CC_LICENSE_URL = "https://creativecommons.org/share-your-work/cclicenses/"

    def __init__(
        self,
        on_open_settings: Callable[[], None],
        on_open_photobooks: Callable[[], None],
        on_change_scheme: Callable[[str], None],
        active_scheme: str,
    ) -> None:
        super().__init__()
        self._on_open_settings = on_open_settings
        self._on_open_photobooks = on_open_photobooks
        self._on_change_scheme = on_change_scheme
        self._active_scheme = active_scheme
        self._scheme_buttons: dict[str, QPushButton] = {}
        
        # Register for theme changes
        theme.register_theme_changed_callback(self._on_theme_changed)
        
        self._build_ui()

    def _on_theme_changed(self) -> None:
        """Refresh stylesheets when theme changes."""
        self._update_stylesheets()

    def _update_stylesheets(self) -> None:
        """Update all stylesheets to reflect current theme."""
        if not hasattr(self, "_logo"):
            return
        self._logo.setStyleSheet(f"color: {theme.ACCENT}; letter-spacing: 4px; margin-bottom: 8px;")
        self._subtitle.setStyleSheet(f"color: {theme.TEXT_SECONDARY}; font-size: 16px; margin-bottom: 48px;")
        # Update picker label color and refresh all scheme buttons
        if hasattr(self, "_picker_label"):
            self._picker_label.setStyleSheet(f"font-size: 12px; color: {theme.TEXT_SECONDARY};")
        if hasattr(self, "_cc_label"):
            self._cc_label.setStyleSheet(f"font-size: 12px; color: {theme.TEXT_MUTED};")
            self._cc_label.setText(
                f'<a href="{self._CC_LICENSE_URL}" style="color:{theme.TEXT_MUTED}; text-decoration:none;">CC-BY-NC</a>'
            )
        self._refresh_scheme_buttons()

    def closeEvent(self, event) -> None:
        """Clean up when window is closed."""
        theme.unregister_theme_changed_callback(self._on_theme_changed)
        super().closeEvent(event)

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setSpacing(0)
        root.setContentsMargins(40, 40, 40, 40)
        root.addStretch(1)

        # Logo
        self._logo = QLabel("DilliDalliKlick")
        logo_font = QFont()
        logo_font.setPointSize(40)
        logo_font.setBold(True)
        self._logo.setFont(logo_font)
        self._logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._logo.setStyleSheet(f"color: {theme.ACCENT}; letter-spacing: 4px; margin-bottom: 8px;")
        root.addWidget(self._logo)

        self._subtitle = QLabel("Das Foto-Enthüllungsspiel")
        self._subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._subtitle.setStyleSheet(f"color: {theme.TEXT_SECONDARY}; font-size: 16px; margin-bottom: 48px;")
        root.addWidget(self._subtitle)

        btn_start = self._make_button("▶  Spiel starten", "primary", 240, 54)
        btn_start.clicked.connect(self._on_open_settings)
        root.addWidget(btn_start, alignment=Qt.AlignmentFlag.AlignCenter)

        root.addSpacing(14)

        btn_books = self._make_button("📚  Fotobücher verwalten", "info", 240, 54)
        btn_books.clicked.connect(self._on_open_photobooks)
        root.addWidget(btn_books, alignment=Qt.AlignmentFlag.AlignCenter)

        root.addStretch(1)

        footer = QHBoxLayout()
        footer.setContentsMargins(0, 0, 0, 0)
        footer.setSpacing(12)
        footer.addWidget(self._build_scheme_picker(), alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)
        footer.addStretch(1)

        self._cc_label = QLabel("CC-NC")
        self._cc_label.setText(
            f'<a href="{self._CC_LICENSE_URL}" style="color:{theme.TEXT_MUTED}; text-decoration:none;">CC-BY-NC</a>'
        )
        self._cc_label.setStyleSheet(f"font-size: 12px; color: {theme.TEXT_MUTED};")
        self._cc_label.setTextFormat(Qt.TextFormat.RichText)
        self._cc_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        self._cc_label.setOpenExternalLinks(False)
        self._cc_label.linkActivated.connect(self._open_cc_license)
        footer.addWidget(self._cc_label, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)

        root.addLayout(footer)

    def _build_scheme_picker(self) -> QWidget:
        picker = QWidget()
        layout = QVBoxLayout(picker)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        self._picker_label = QLabel("Farbschema")
        self._picker_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self._picker_label.setStyleSheet(f"font-size: 12px; color: {theme.TEXT_SECONDARY};")
        layout.addWidget(self._picker_label)

        # Create single row of circles for all schemes
        circles_row = QHBoxLayout()
        circles_row.setSpacing(16)
        circles_row.setContentsMargins(0, 0, 0, 0)

        schemes = list(theme.COLOR_SCHEMES.items())
        for scheme_name, colors in schemes:
            circle = QPushButton()
            circle.setFixedSize(40, 40)
            circle.setCursor(Qt.CursorShape.PointingHandCursor)
            circle.setToolTip(scheme_name.replace("_", " ").title())
            circle.clicked.connect(lambda _checked=False, name=scheme_name: self._select_scheme(name))
            self._scheme_buttons[scheme_name] = circle
            circles_row.addWidget(circle)

        circles_row.addStretch(1)
        layout.addLayout(circles_row)
        
        self._refresh_scheme_buttons()
        return picker

    def _select_scheme(self, scheme_name: str) -> None:
        if scheme_name == self._active_scheme:
            return

        self._active_scheme = scheme_name
        self._on_change_scheme(scheme_name)
        self._refresh_scheme_buttons()

    def _refresh_scheme_buttons(self) -> None:
        for scheme_name, btn in self._scheme_buttons.items():
            colors = theme.COLOR_SCHEMES[scheme_name]
            is_selected = scheme_name == self._active_scheme
            
            # Use a bright border (text_primary) for selected, subtle border (muted) for unselected
            border_color = colors["text_primary"] if is_selected else colors["text_muted"]
            border_width = "4px" if is_selected else "2px"
            
            btn.setStyleSheet(
                "QPushButton {"
                f"background-color: {colors['bg_primary']};"
                f"border: {border_width} solid {border_color};"
                "border-radius: 20px;"
                "}"
                "QPushButton:hover {"
                f"border-color: {colors['text_primary']};"
                "border-width: 4px;"
                "}"
            )

    def _open_cc_license(self, url: str) -> None:
        QDesktopServices.openUrl(QUrl(url))

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
