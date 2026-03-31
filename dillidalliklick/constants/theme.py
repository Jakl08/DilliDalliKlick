"""Qt stylesheet and colour palette for DilliDalliKlick."""

from collections.abc import Callable

from PyQt6.QtWidgets import QApplication

from .color_schemes import COLOR_SCHEMES

DEFAULT_SCHEME = "deep_navy"
_active_scheme = DEFAULT_SCHEME
_colors = COLOR_SCHEMES[_active_scheme]

# Callback system for theme changes
_theme_changed_callbacks: list[Callable[[], None]] = []


def _is_light_color(hex_color: str) -> bool:
    """Return True if the color is light enough for dark text."""
    color = hex_color.strip()
    if not color.startswith("#") or len(color) != 7:
        return False
    r = int(color[1:3], 16)
    g = int(color[3:5], 16)
    b = int(color[5:7], 16)
    # Perceived luminance
    luminance = (0.299 * r) + (0.587 * g) + (0.114 * b)
    return luminance >= 155


def _best_text_on(bg_color: str, default_text: str) -> str:
    """Choose a readable text color for a background, preserving explicit defaults when valid."""
    if bg_color.lower() == default_text.lower():
        return "#111111" if _is_light_color(bg_color) else "#f5f5f5"
    return default_text


def register_theme_changed_callback(callback: Callable[[], None]) -> None:
    """Register a callback to be called when the active theme changes."""
    _theme_changed_callbacks.append(callback)


def unregister_theme_changed_callback(callback: Callable[[], None]) -> None:
    """Unregister a theme change callback."""
    if callback in _theme_changed_callbacks:
        _theme_changed_callbacks.remove(callback)


def _notify_theme_changed() -> None:
    """Notify all registered callbacks that the theme has changed."""
    for callback in _theme_changed_callbacks:
        try:
            callback()
        except Exception:
            pass

def _apply_colors(colors: dict[str, str]) -> None:
    global BG_PRIMARY, BG_SECONDARY, BG_CARD
    global ACCENT, ACCENT_HOVER, GREEN, BLUE, ORANGE
    global TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED
    global BORDER, WHITE, TRANSPARENT
    global BUTTON_HOVER, SUCCESS_HOVER, INFO_HOVER
    global DANGER, DANGER_HOVER
    global BUTTON_TEXT_PRIMARY, BUTTON_TEXT_SECONDARY, BUTTON_TEXT_ACCENT
    global BUTTON_TEXT_SUCCESS, BUTTON_TEXT_INFO, BUTTON_TEXT_DANGER

    BG_PRIMARY = colors["bg_primary"]
    BG_SECONDARY = colors["bg_secondary"]
    BG_CARD = colors["bg_card"]
    ACCENT = colors["accent"]
    ACCENT_HOVER = colors["accent_hover"]
    GREEN = colors["green"]
    BLUE = colors["blue"]
    ORANGE = colors["orange"]
    TEXT_PRIMARY = colors["text_primary"]
    TEXT_SECONDARY = colors["text_secondary"]
    TEXT_MUTED = colors["text_muted"]
    BORDER = colors["border"]
    WHITE = colors["white"]
    TRANSPARENT = colors["transparent"]
    BUTTON_HOVER = colors["button_hover"]
    SUCCESS_HOVER = colors["success_hover"]
    INFO_HOVER = colors["info_hover"]
    DANGER = colors["danger"]
    DANGER_HOVER = colors["danger_hover"]
    BUTTON_TEXT_PRIMARY = colors.get("button_text_primary", WHITE)
    BUTTON_TEXT_SECONDARY = colors.get("button_text_secondary", WHITE)
    BUTTON_TEXT_ACCENT = _best_text_on(
        ACCENT,
        colors.get("button_text_accent", BUTTON_TEXT_PRIMARY),
    )
    BUTTON_TEXT_SUCCESS = _best_text_on(
        GREEN,
        colors.get("button_text_success", BUTTON_TEXT_PRIMARY),
    )
    BUTTON_TEXT_INFO = _best_text_on(
        BLUE,
        colors.get("button_text_info", BUTTON_TEXT_PRIMARY),
    )
    BUTTON_TEXT_DANGER = _best_text_on(
        DANGER,
        colors.get("button_text_danger", BUTTON_TEXT_PRIMARY),
    )


def _build_stylesheet() -> str:
    return f"""
/* ── Global ── */
QWidget {{
    background-color: {BG_PRIMARY};
    color: {TEXT_PRIMARY};
    font-family: "Segoe UI", "Arial", sans-serif;
    font-size: 14px;
}}

QMainWindow, QDialog {{
    background-color: {BG_PRIMARY};
}}

/* ── Labels ── */
QLabel {{
    background: {TRANSPARENT};
    color: {TEXT_PRIMARY};
}}

/* ── Push buttons ── */
QPushButton {{
    background-color: {BG_CARD};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 8px 18px;
    font-size: 14px;
    font-weight: 500;
}}
QPushButton:hover {{
    background-color: {BUTTON_HOVER};
    border-color: {ACCENT};
}}
QPushButton:pressed {{
    background-color: {ACCENT};
    color: {BUTTON_TEXT_ACCENT};
}}
QPushButton:disabled {{
    opacity: 0.45;
    color: {TEXT_MUTED};
}}

QPushButton[class="primary"] {{
    background-color: {ACCENT};
    color: {BUTTON_TEXT_ACCENT};
    border: none;
}}
QPushButton[class="primary"]:hover {{
    background-color: {ACCENT_HOVER};
}}

QPushButton[class="success"] {{
    background-color: {GREEN};
    color: {BUTTON_TEXT_SUCCESS};
    border: none;
}}
QPushButton[class="success"]:hover {{
    background-color: {SUCCESS_HOVER};
}}

QPushButton[class="info"] {{
    background-color: {BLUE};
    color: {BUTTON_TEXT_INFO};
    border: none;
}}
QPushButton[class="info"]:hover {{
    background-color: {INFO_HOVER};
}}

QPushButton[class="danger"] {{
    background-color: {DANGER};
    color: {BUTTON_TEXT_DANGER};
    border: none;
}}
QPushButton[class="danger"]:hover {{
    background-color: {DANGER_HOVER};
}}

/* ── Line edits / spin boxes ── */
QLineEdit, QSpinBox, QComboBox {{
    background-color: {BG_SECONDARY};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    border-radius: 5px;
    padding: 6px 10px;
    font-size: 14px;
}}
QLineEdit:focus, QSpinBox:focus, QComboBox:focus {{
    border-color: {ACCENT};
}}

QSpinBox::up-button, QSpinBox::down-button {{
    background-color: {BG_CARD};
    border: none;
    width: 22px;
}}
QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
    background-color: {ACCENT};
}}

QComboBox::drop-down {{
    background-color: {BG_CARD};
    border: none;
    border-radius: 0 5px 5px 0;
    width: 28px;
}}
QComboBox QAbstractItemView {{
    background-color: {BG_SECONDARY};
    color: {TEXT_PRIMARY};
    selection-background-color: {ACCENT};
    border: 1px solid {BORDER};
}}

/* ── Radio buttons ── */
QRadioButton {{
    background: {TRANSPARENT};
    spacing: 8px;
    font-size: 14px;
}}
QRadioButton::indicator {{
    width: 16px;
    height: 16px;
    border-radius: 8px;
    border: 2px solid {BORDER};
    background: {BG_SECONDARY};
}}
QRadioButton::indicator:checked {{
    background: {ACCENT};
    border-color: {ACCENT};
}}

/* ── Group boxes ── */
QGroupBox {{
    background-color: {BG_SECONDARY};
    border: 1px solid {BORDER};
    border-radius: 8px;
    margin-top: 14px;
    padding: 12px 16px;
    font-weight: 600;
    color: {TEXT_SECONDARY};
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 14px;
    top: 2px;
    color: {TEXT_SECONDARY};
}}

/* ── Scroll areas ── */
QScrollArea {{
    border: none;
    background: {TRANSPARENT};
}}
QScrollBar:vertical {{
    background: {BG_SECONDARY};
    width: 8px;
    margin: 0;
    border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background: {BG_CARD};
    border-radius: 4px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{
    background: {ACCENT};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

/* ── Progress bar ── */
QProgressBar {{
    background: {BG_CARD};
    border: none;
    border-radius: 3px;
    height: 6px;
    text-align: center;
    color: {TRANSPARENT};
}}
QProgressBar::chunk {{
    background: {ACCENT};
    border-radius: 3px;
}}

/* ── Separators ── */
QFrame[frameShape="4"], QFrame[frameShape="5"] {{
    color: {BORDER};
    background: {BORDER};
}}

/* ── Message boxes ── */
QMessageBox {{
    background-color: {BG_SECONDARY};
}}
QMessageBox QLabel {{
    color: {TEXT_PRIMARY};
    font-size: 14px;
}}
"""


def set_active_scheme(scheme_name: str) -> None:
    """Select the active color scheme and rebuild theme variables."""
    global _active_scheme, _colors
    if scheme_name not in COLOR_SCHEMES:
        raise ValueError(f"Unknown color scheme: {scheme_name}")

    _active_scheme = scheme_name
    _colors = COLOR_SCHEMES[_active_scheme]
    _apply_colors(_colors)
    _notify_theme_changed()


def get_active_scheme() -> str:
    """Return the current scheme identifier."""
    return _active_scheme


_apply_colors(_colors)


def apply(app: QApplication) -> None:
    """Apply the stylesheet to a QApplication instance."""
    app.setStyleSheet(_build_stylesheet())
