"""Photobook management window."""

import os
import time
from pathlib import Path

from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QIcon
from PyQt6.QtWidgets import (
    QDialog,
    QFileDialog,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from dillidalliklick import store

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg"}


class PhotobookWindow(QMainWindow):
    """Manage photobooks and their photo collections."""

    def __init__(self, app_state: dict, parent_window) -> None:
        super().__init__()
        self._state = app_state
        self._parent_window = parent_window
        self._current_book_id: str | None = None
        self.setWindowTitle("DilliDalliKlick – Fotobücher")
        self.setMinimumSize(900, 620)
        self._build_ui()
        self._refresh_book_list()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        toolbar = QWidget()
        toolbar.setStyleSheet("background:#16213e; border-bottom:1px solid #1e3a5f;")
        toolbar.setFixedHeight(56)
        tb_layout = QHBoxLayout(toolbar)
        tb_layout.setContentsMargins(16, 0, 16, 0)

        title = QLabel("📚  Fotobücher")
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

        # Main area: left = book list, right = photo manager
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(1)
        splitter.setStyleSheet("QSplitter::handle { background:#1e3a5f; }")

        # Left panel
        left = QWidget()
        left.setMinimumWidth(230)
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(12, 12, 6, 12)
        left_layout.setSpacing(8)

        books_label = QLabel("Meine Fotobücher")
        books_label.setStyleSheet("font-weight:700; font-size:13px; color:#a0a0b0;")
        left_layout.addWidget(books_label)

        self._book_list = QListWidget()
        self._book_list.setStyleSheet(
            "QListWidget { background:#16213e; border:1px solid #1e3a5f; border-radius:6px; }"
            "QListWidget::item { padding:10px 12px; border-radius:4px; }"
            "QListWidget::item:selected { background:#e94560; color:white; }"
            "QListWidget::item:hover:!selected { background:#1a4a80; }"
        )
        self._book_list.currentRowChanged.connect(self._on_book_selected)
        left_layout.addWidget(self._book_list)

        add_btn = QPushButton("➕  Neues Fotobuch")
        add_btn.setProperty("class", "success")
        add_btn.clicked.connect(self._create_book)
        left_layout.addWidget(add_btn)

        del_btn = QPushButton("🗑  Fotobuch löschen")
        del_btn.setProperty("class", "danger")
        del_btn.clicked.connect(self._delete_book)
        left_layout.addWidget(del_btn)

        # Right panel
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(6, 12, 12, 12)
        right_layout.setSpacing(10)

        # Directory row
        dir_group = QGroupBox("Verzeichnis")
        dir_hlayout = QHBoxLayout(dir_group)
        dir_hlayout.setSpacing(8)
        self._dir_label = QLabel("(kein Verzeichnis gewählt)")
        self._dir_label.setStyleSheet("color:#a0a0b0; font-size:12px;")
        self._dir_label.setWordWrap(True)
        dir_hlayout.addWidget(self._dir_label, 1)
        choose_dir_btn = QPushButton("📁  Verzeichnis wählen")
        choose_dir_btn.setProperty("class", "info")
        choose_dir_btn.clicked.connect(self._choose_directory)
        dir_hlayout.addWidget(choose_dir_btn)
        refresh_dir_btn = QPushButton("🔄")
        refresh_dir_btn.setToolTip("Verzeichnis neu einlesen")
        refresh_dir_btn.setFixedWidth(36)
        refresh_dir_btn.clicked.connect(self._refresh_directory)
        dir_hlayout.addWidget(refresh_dir_btn)
        right_layout.addWidget(dir_group)

        # Import row
        import_btn = QPushButton("➕  Einzelne Fotos importieren")
        import_btn.setProperty("class", "info")
        import_btn.clicked.connect(self._import_photos)
        right_layout.addWidget(import_btn)

        # Photo grid (scroll area)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border:1px solid #1e3a5f; border-radius:6px; }")
        self._photo_container = QWidget()
        self._photo_container.setStyleSheet("background:#16213e;")
        self._photo_grid_layout = _WrapLayout(self._photo_container)
        scroll.setWidget(self._photo_container)
        right_layout.addWidget(scroll, 1)

        self._no_photos_label = QLabel("Noch keine Fotos – wähle ein Verzeichnis\noder importiere einzelne Bilder.")
        self._no_photos_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._no_photos_label.setStyleSheet("color:#606070; font-size:13px; padding:40px;")
        right_layout.addWidget(self._no_photos_label)
        self._no_photos_label.hide()

        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setSizes([240, 660])

        # Root layout
        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        root_layout.addWidget(toolbar)
        root_layout.addWidget(splitter)
        self.setCentralWidget(root)

    # ------------------------------------------------------------------
    # Book list
    # ------------------------------------------------------------------

    def _refresh_book_list(self) -> None:
        self._book_list.clear()
        books = self._state.get("photobooks", {})
        for book_id, book in books.items():
            count = len(book.get("photos", []))
            item = QListWidgetItem(f"{book['name']}  ({count})")
            item.setData(Qt.ItemDataRole.UserRole, book_id)
            self._book_list.addItem(item)

    def _on_book_selected(self, row: int) -> None:
        if row < 0:
            self._current_book_id = None
            self._clear_photo_grid()
            return
        item = self._book_list.item(row)
        self._current_book_id = item.data(Qt.ItemDataRole.UserRole)
        self._refresh_photo_grid()

    # ------------------------------------------------------------------
    # Book operations
    # ------------------------------------------------------------------

    def _create_book(self) -> None:
        name, ok = QInputDialog.getText(self, "Neues Fotobuch", "Name des Fotobuchs:")
        if not ok or not name.strip():
            return
        book_id = f"book_{int(time.time() * 1000)}"
        self._state["photobooks"][book_id] = {
            "id": book_id,
            "name": name.strip(),
            "photos": [],
            "directory": None,
        }
        store.save(self._state)
        self._refresh_book_list()
        # Select the new book
        for i in range(self._book_list.count()):
            if self._book_list.item(i).data(Qt.ItemDataRole.UserRole) == book_id:
                self._book_list.setCurrentRow(i)
                break

    def _delete_book(self) -> None:
        if not self._current_book_id:
            return
        book = self._state["photobooks"].get(self._current_book_id)
        if not book:
            return
        reply = QMessageBox.question(
            self,
            "Löschen bestätigen",
            f'Fotobuch „{book["name"]}" wirklich löschen?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        del self._state["photobooks"][self._current_book_id]
        self._current_book_id = None
        store.save(self._state)
        self._refresh_book_list()
        self._clear_photo_grid()

    # ------------------------------------------------------------------
    # Photo operations
    # ------------------------------------------------------------------

    def _choose_directory(self) -> None:
        if not self._current_book_id:
            QMessageBox.warning(self, "Kein Fotobuch", "Bitte zuerst ein Fotobuch auswählen.")
            return
        dir_path = QFileDialog.getExistingDirectory(self, "Verzeichnis wählen")
        if not dir_path:
            return
        book = self._state["photobooks"][self._current_book_id]
        book["directory"] = dir_path
        images = _scan_directory(dir_path)
        existing = set(book["photos"])
        book["photos"] = list(existing | set(images))
        store.save(self._state)
        self._dir_label.setText(dir_path)
        self._refresh_book_list()
        self._refresh_photo_grid()

    def _refresh_directory(self) -> None:
        if not self._current_book_id:
            return
        book = self._state["photobooks"][self._current_book_id]
        if not book.get("directory"):
            return
        images = _scan_directory(book["directory"])
        existing = set(book["photos"])
        new_images = set(images) - existing
        book["photos"] = list(existing | set(images))
        store.save(self._state)
        self._refresh_book_list()
        self._refresh_photo_grid()
        QMessageBox.information(self, "Aktualisiert", f"{len(new_images)} neue Foto(s) gefunden.")

    def _import_photos(self) -> None:
        if not self._current_book_id:
            QMessageBox.warning(self, "Kein Fotobuch", "Bitte zuerst ein Fotobuch auswählen.")
            return
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Fotos importieren",
            "",
            "Bilder (*.jpg *.jpeg *.png *.gif *.bmp *.webp *.svg)",
        )
        if not paths:
            return
        book = self._state["photobooks"][self._current_book_id]
        existing = set(book["photos"])
        added = [p for p in paths if p not in existing]
        book["photos"] = list(existing | set(paths))
        store.save(self._state)
        self._refresh_book_list()
        self._refresh_photo_grid()
        QMessageBox.information(self, "Importiert", f"{len(added)} Foto(s) hinzugefügt.")

    def _remove_photo(self, path: str) -> None:
        if not self._current_book_id:
            return
        book = self._state["photobooks"][self._current_book_id]
        book["photos"] = [p for p in book["photos"] if p != path]
        store.save(self._state)
        self._refresh_book_list()
        self._refresh_photo_grid()

    # ------------------------------------------------------------------
    # Photo grid
    # ------------------------------------------------------------------

    def _clear_photo_grid(self) -> None:
        while self._photo_grid_layout.count():
            item = self._photo_grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._dir_label.setText("(kein Verzeichnis gewählt)")

    def _refresh_photo_grid(self) -> None:
        self._clear_photo_grid()
        if not self._current_book_id:
            return
        book = self._state["photobooks"][self._current_book_id]

        # Directory label
        if book.get("directory"):
            self._dir_label.setText(book["directory"])
        else:
            self._dir_label.setText("(kein Verzeichnis gewählt)")

        photos = book.get("photos", [])
        if not photos:
            self._no_photos_label.show()
            return
        self._no_photos_label.hide()

        for photo_path in photos:
            thumb = _PhotoThumb(photo_path)
            thumb.remove_requested.connect(self._remove_photo)
            self._photo_grid_layout.addWidget(thumb)

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def _go_back(self) -> None:
        self._parent_window.show()
        self.close()

    def closeEvent(self, event):
        self._parent_window.show()
        super().closeEvent(event)


# ──────────────────────────────────────────────────────────────────────
# Helper widgets
# ──────────────────────────────────────────────────────────────────────

class _PhotoThumb(QFrame):
    """Thumbnail card with a remove button."""

    remove_requested = pyqtSignal(str)

    def __init__(self, path: str) -> None:
        super().__init__()
        self._path = path
        self.setFixedSize(120, 140)
        self.setStyleSheet(
            "QFrame { background:#0f3460; border:1px solid #1e3a5f; border-radius:6px; }"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        img_label = QLabel()
        img_label.setFixedSize(112, 100)
        img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pixmap = QPixmap(path)
        if not pixmap.isNull():
            img_label.setPixmap(
                pixmap.scaled(112, 100, Qt.AspectRatioMode.KeepAspectRatio,
                              Qt.TransformationMode.SmoothTransformation)
            )
        else:
            img_label.setText("🖼")
            img_label.setStyleSheet("font-size:28px; color:#606070;")
        layout.addWidget(img_label)

        name_label = QLabel(Path(path).name)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setStyleSheet("font-size:10px; color:#a0a0b0;")
        name_label.setWordWrap(True)
        layout.addWidget(name_label)

        remove_btn = QPushButton("✕")
        remove_btn.setFixedHeight(20)
        remove_btn.setStyleSheet(
            "QPushButton { background:#b71c1c; color:white; border:none; border-radius:4px; font-size:11px; }"
            "QPushButton:hover { background:#d32f2f; }"
        )
        remove_btn.clicked.connect(lambda: self.remove_requested.emit(self._path))
        layout.addWidget(remove_btn)


class _WrapLayout(QVBoxLayout):
    """
    Simple flow/wrap layout that arranges child widgets in a grid.
    Re-uses a series of horizontal rows.
    """

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setContentsMargins(8, 8, 8, 8)
        self.setSpacing(8)
        self._rows: list[QHBoxLayout] = []
        self._widgets: list[QWidget] = []

    # Override addWidget to track widgets and rebuild layout
    def addWidget(self, widget: QWidget) -> None:  # type: ignore[override]
        self._widgets.append(widget)
        self._rebuild()

    def count(self) -> int:
        return len(self._widgets)

    def takeAt(self, index: int):
        if index < len(self._widgets):
            w = self._widgets.pop(index)
            self._rebuild()

            class _FakeItem:
                def widget(self_inner):
                    return w
            return _FakeItem()

        class _NullItem:
            def widget(self_inner):
                return None
        return _NullItem()

    def _rebuild(self) -> None:
        # Remove all existing rows
        while super().count():
            item = super().takeAt(0)
            if item.layout():
                while item.layout().count():
                    child = item.layout().takeAt(0)
                    if child.widget():
                        child.widget().setParent(None)
                item.layout().deleteLater()

        self._rows = []
        COLS = 5
        for i, widget in enumerate(self._widgets):
            if i % COLS == 0:
                row = QHBoxLayout()
                row.setSpacing(8)
                row.addStretch(0)
                self._rows.append(row)
                super().addLayout(row)
            self._rows[-1].addWidget(widget)

        super().addStretch(1)


# ──────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────

def _scan_directory(dir_path: str) -> list[str]:
    """Return all image file paths inside dir_path (non-recursive)."""
    result = []
    try:
        for entry in os.scandir(dir_path):
            if entry.is_file() and Path(entry.path).suffix.lower() in IMAGE_EXTENSIONS:
                result.append(entry.path)
    except OSError:
        pass
    return result
