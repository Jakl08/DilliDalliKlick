"""Qt stylesheet and colour palette for DilliDalliKlick."""

BG_PRIMARY = "#1a1a2e"
BG_SECONDARY = "#16213e"
BG_CARD = "#0f3460"
ACCENT = "#e94560"
ACCENT_HOVER = "#c73652"
GREEN = "#4caf50"
BLUE = "#2196f3"
ORANGE = "#ff9800"
TEXT_PRIMARY = "#eaeaea"
TEXT_SECONDARY = "#a0a0b0"
TEXT_MUTED = "#606070"
BORDER = "#1e3a5f"

STYLESHEET = f"""
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
    background: transparent;
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
    background-color: #1a4a80;
    border-color: {ACCENT};
}}
QPushButton:pressed {{
    background-color: {ACCENT};
    color: white;
}}
QPushButton:disabled {{
    opacity: 0.45;
    color: {TEXT_MUTED};
}}

QPushButton[class="primary"] {{
    background-color: {ACCENT};
    color: white;
    border: none;
}}
QPushButton[class="primary"]:hover {{
    background-color: {ACCENT_HOVER};
}}

QPushButton[class="success"] {{
    background-color: {GREEN};
    color: white;
    border: none;
}}
QPushButton[class="success"]:hover {{
    background-color: #388e3c;
}}

QPushButton[class="info"] {{
    background-color: {BLUE};
    color: white;
    border: none;
}}
QPushButton[class="info"]:hover {{
    background-color: #1565c0;
}}

QPushButton[class="danger"] {{
    background-color: #b71c1c;
    color: white;
    border: none;
}}
QPushButton[class="danger"]:hover {{
    background-color: #d32f2f;
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
    background: transparent;
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
    background: transparent;
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
    color: transparent;
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


def apply(app) -> None:
    """Apply the stylesheet to a QApplication instance."""
    app.setStyleSheet(STYLESHEET)
