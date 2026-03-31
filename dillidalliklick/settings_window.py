"""Settings window – configure game parameters before starting."""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


class SettingsWindow(QMainWindow):
    """Game configuration screen."""

    def __init__(self, app_state: dict, parent_window) -> None:
        super().__init__()
        self._state = app_state
        self._parent_window = parent_window
        self.setWindowTitle("DilliDalliKlick – Einstellungen")
        self.setMinimumSize(640, 560)
        self._build_ui()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        # Toolbar
        toolbar = QWidget()
        toolbar.setStyleSheet("background:#16213e; border-bottom:1px solid #1e3a5f;")
        toolbar.setFixedHeight(56)
        tb_layout = QHBoxLayout(toolbar)
        tb_layout.setContentsMargins(16, 0, 16, 0)

        title = QLabel("⚙️  Einstellungen")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color:#e94560;")
        tb_layout.addWidget(title)
        tb_layout.addStretch()

        back_btn = QPushButton("← Menü")
        back_btn.clicked.connect(self._go_back)
        tb_layout.addWidget(back_btn)

        # Scroll content
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(60, 24, 60, 24)
        content_layout.setSpacing(20)

        # ── Photobook section ──
        book_group = QGroupBox("Fotobuch")
        book_layout = QVBoxLayout(book_group)

        self._book_combo = QComboBox()
        self._populate_books()
        book_layout.addWidget(self._book_combo)
        content_layout.addWidget(book_group)

        # ── Photo count ──
        count_group = QGroupBox("Anzahl der Fotos")
        count_layout = QHBoxLayout(count_group)
        count_layout.setSpacing(12)
        count_lbl = QLabel("Fotos pro Durchlauf:")
        count_lbl.setStyleSheet("color:#a0a0b0;")
        count_layout.addWidget(count_lbl)
        self._photo_count_spin = QSpinBox()
        self._photo_count_spin.setRange(1, 500)
        self._photo_count_spin.setValue(5)
        self._photo_count_spin.setFixedWidth(80)
        count_layout.addWidget(self._photo_count_spin)
        count_layout.addStretch()
        content_layout.addWidget(count_group)

        # ── Grid size ──
        grid_group = QGroupBox("Raster (Spalten × Zeilen)")
        grid_layout = QHBoxLayout(grid_group)
        grid_layout.setSpacing(12)

        cols_lbl = QLabel("Spalten:")
        cols_lbl.setStyleSheet("color:#a0a0b0;")
        grid_layout.addWidget(cols_lbl)
        self._cols_spin = QSpinBox()
        self._cols_spin.setRange(1, 20)
        self._cols_spin.setValue(4)
        self._cols_spin.setFixedWidth(70)
        grid_layout.addWidget(self._cols_spin)

        grid_layout.addSpacing(20)

        rows_lbl = QLabel("Zeilen:")
        rows_lbl.setStyleSheet("color:#a0a0b0;")
        grid_layout.addWidget(rows_lbl)
        self._rows_spin = QSpinBox()
        self._rows_spin.setRange(1, 20)
        self._rows_spin.setValue(3)
        self._rows_spin.setFixedWidth(70)
        grid_layout.addWidget(self._rows_spin)
        grid_layout.addStretch()
        content_layout.addWidget(grid_group)

        # ── Reveal mode ──
        mode_group = QGroupBox("Enthüllungsmodus")
        mode_layout = QVBoxLayout(mode_group)

        self._radio_click = QRadioButton("🖱️  Klick-Modus – Felder werden per Mausklick aufgedeckt")
        self._radio_click.setChecked(True)
        self._radio_timer = QRadioButton("⏱️  Timer-Modus – Felder werden automatisch aufgedeckt")
        mode_layout.addWidget(self._radio_click)
        mode_layout.addWidget(self._radio_timer)

        # Timer interval (only visible in timer mode)
        self._timer_row = QWidget()
        timer_row_layout = QHBoxLayout(self._timer_row)
        timer_row_layout.setContentsMargins(24, 8, 0, 0)
        interval_lbl = QLabel("Intervall (Sekunden):")
        interval_lbl.setStyleSheet("color:#a0a0b0;")
        timer_row_layout.addWidget(interval_lbl)
        self._interval_spin = QSpinBox()
        self._interval_spin.setRange(1, 60)
        self._interval_spin.setValue(3)
        self._interval_spin.setFixedWidth(70)
        timer_row_layout.addWidget(self._interval_spin)
        timer_row_layout.addStretch()
        mode_layout.addWidget(self._timer_row)
        self._timer_row.setVisible(False)

        self._radio_timer.toggled.connect(self._timer_row.setVisible)

        content_layout.addWidget(mode_group)

        # ── Start button ──
        content_layout.addStretch()
        start_btn = QPushButton("▶  Spiel starten")
        start_btn.setProperty("class", "primary")
        start_btn.setFixedHeight(52)
        start_font = QFont()
        start_font.setPointSize(14)
        start_btn.setFont(start_font)
        start_btn.clicked.connect(self._start_game)
        content_layout.addWidget(start_btn)

        # Root
        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        root_layout.addWidget(toolbar)
        root_layout.addWidget(content)
        self.setCentralWidget(root)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _populate_books(self) -> None:
        self._book_combo.clear()
        self._book_combo.addItem("– Fotobuch auswählen –", None)
        for book_id, book in self._state.get("photobooks", {}).items():
            count = len(book.get("photos", []))
            self._book_combo.addItem(f"{book['name']}  ({count} Fotos)", book_id)

    def _start_game(self) -> None:
        book_id = self._book_combo.currentData()
        if book_id is None:
            QMessageBox.warning(self, "Kein Fotobuch", "Bitte ein Fotobuch auswählen.")
            return
        book = self._state["photobooks"].get(book_id)
        if not book or not book.get("photos"):
            QMessageBox.warning(self, "Leeres Fotobuch", "Das gewählte Fotobuch enthält keine Fotos.")
            return

        config = {
            "book_id": book_id,
            "photos": list(book["photos"]),
            "photo_count": self._photo_count_spin.value(),
            "cols": self._cols_spin.value(),
            "rows": self._rows_spin.value(),
            "mode": "timer" if self._radio_timer.isChecked() else "click",
            "interval": self._interval_spin.value(),
        }

        from dillidalliklick.game_window import GameWindow
        self._game_win = GameWindow(config, self)
        self._game_win.show()
        self.hide()

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def _go_back(self) -> None:
        self._parent_window.show()
        self.close()

    def closeEvent(self, event):
        self._parent_window.show()
        super().closeEvent(event)
