"""Photobook management window."""

from collections.abc import Callable
from pathlib import Path

from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtWidgets import (
    QFileDialog,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSplitter,
    QStyle,
    QVBoxLayout,
    QWidget,
)

from dillidalliklick.logic.photobook_logic import PhotobookLogic
from dillidalliklick.store import StoreData
from dillidalliklick.constants import theme


class PhotobookWindow(QWidget):
    """Manage photobooks and their photo collections."""

    def __init__(self, app_state: StoreData, on_back: Callable[[], None]) -> None:
        super().__init__()
        self._logic = PhotobookLogic(app_state)
        self._on_back = on_back
        self._current_book_id: str | None = None
        
        # Register for theme changes
        theme.register_theme_changed_callback(self._on_theme_changed)
        
        self._build_ui()
        self._refresh_book_list()

    def _on_theme_changed(self) -> None:
        """Refresh stylesheets when theme changes."""
        self._update_stylesheets()

    def _update_stylesheets(self) -> None:
        """Update all stylesheets to reflect current theme."""
        if not hasattr(self, "_toolbar"):
            return
        self._toolbar.setStyleSheet(
            f"background:{theme.BG_SECONDARY}; border-bottom:1px solid {theme.BORDER};"
        )
        self._title.setStyleSheet(f"color:{theme.ACCENT};")
        self._books_label.setStyleSheet(
            f"font-weight:700; font-size:13px; color:{theme.TEXT_SECONDARY};"
        )
        self._splitter.setStyleSheet(f"QSplitter::handle {{ background:{theme.BORDER}; }}")
        if hasattr(self, "_book_list"):
            self._book_list.setStyleSheet(
                f"QListWidget {{ background:{theme.BG_SECONDARY}; border:1px solid {theme.BORDER}; border-radius:6px; }}"
                "QListWidget::item { padding:10px 12px; border-radius:4px; }"
                f"QListWidget::item:selected {{ background:{theme.ACCENT}; color:{theme.WHITE}; }}"
                f"QListWidget::item:hover:!selected {{ background:{theme.BUTTON_HOVER}; }}"
            )
        if hasattr(self, "_dir_label"):
            self._dir_label.setStyleSheet(f"color:{theme.TEXT_SECONDARY}; font-size:12px;")
        if hasattr(self, "_photo_container"):
            self._photo_container.setStyleSheet(f"background:{theme.BG_SECONDARY};")
        if hasattr(self, "_no_photos_label"):
            self._no_photos_label.setStyleSheet(
                f"color:{theme.TEXT_MUTED}; font-size:13px; padding:40px;"
            )
        if hasattr(self, "_photo_grid_layout"):
            for i in range(self._photo_grid_layout.count()):
                widget = self._photo_grid_layout.itemAt(i).widget() if self._photo_grid_layout.itemAt(i) else None
                if widget and isinstance(widget, _PhotoThumb):
                    widget._update_stylesheet()

    def closeEvent(self, event) -> None:
        """Clean up when window is closed."""
        theme.unregister_theme_changed_callback(self._on_theme_changed)
        super().closeEvent(event)

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        self._toolbar = QWidget()
        self._toolbar.setStyleSheet(
            f"background:{theme.BG_SECONDARY}; border-bottom:1px solid {theme.BORDER};"
        )
        self._toolbar.setFixedHeight(56)
        tb_layout = QHBoxLayout(self._toolbar)
        tb_layout.setContentsMargins(16, 0, 16, 0)

        self._title = QLabel("📚  Fotobücher")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        self._title.setFont(title_font)
        self._title.setStyleSheet(f"color:{theme.ACCENT};")
        tb_layout.addWidget(self._title)

        tb_layout.addStretch()

        self._back_btn = QPushButton("← Menü")
        self._back_btn.clicked.connect(self._go_back)
        tb_layout.addWidget(self._back_btn)

        # Main area: left = book list, right = photo manager
        self._splitter = QSplitter(Qt.Orientation.Horizontal)
        self._splitter.setHandleWidth(1)
        self._splitter.setStyleSheet(f"QSplitter::handle {{ background:{theme.BORDER}; }}")

        # Left panel
        left = QWidget()
        left.setMinimumWidth(230)
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(12, 12, 6, 12)
        left_layout.setSpacing(8)

        self._books_label = QLabel("Meine Fotobücher")
        self._books_label.setStyleSheet(
            f"font-weight:700; font-size:13px; color:{theme.TEXT_SECONDARY};"
        )
        left_layout.addWidget(self._books_label)

        self._book_list = QListWidget()
        self._book_list.setStyleSheet(
            f"QListWidget {{ background:{theme.BG_SECONDARY}; border:1px solid {theme.BORDER}; border-radius:6px; }}"
            "QListWidget::item { padding:10px 12px; border-radius:4px; }"
            f"QListWidget::item:selected {{ background:{theme.ACCENT}; color:{theme.WHITE}; }}"
            f"QListWidget::item:hover:!selected {{ background:{theme.BUTTON_HOVER}; }}"
        )
        self._book_list.currentRowChanged.connect(self._on_book_selected)
        left_layout.addWidget(self._book_list)

        self._add_btn = QPushButton("➕  Neues Fotobuch")
        self._add_btn.setProperty("class", "success")
        self._add_btn.clicked.connect(self._create_book)
        left_layout.addWidget(self._add_btn)

        self._del_btn = QPushButton("🗑  Fotobuch löschen")
        self._del_btn.setProperty("class", "danger")
        self._del_btn.clicked.connect(self._delete_book)
        left_layout.addWidget(self._del_btn)

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
        self._dir_label.setStyleSheet(f"color:{theme.TEXT_SECONDARY}; font-size:12px;")
        self._dir_label.setWordWrap(True)
        dir_hlayout.addWidget(self._dir_label, 1)
        self._choose_dir_btn = QPushButton("📁  Verzeichnis wählen")
        self._choose_dir_btn.setProperty("class", "info")
        self._choose_dir_btn.clicked.connect(self._choose_directory)
        dir_hlayout.addWidget(self._choose_dir_btn)
        right_layout.addWidget(dir_group)

        # Import row
        self._import_btn = QPushButton("➕  Einzelne Fotos importieren")
        self._import_btn.setProperty("class", "info")
        self._import_btn.clicked.connect(self._import_photos)
        right_layout.addWidget(self._import_btn)

        # Photo grid (scroll area)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(
            f"QScrollArea {{ border:1px solid {theme.BORDER}; border-radius:6px; }}"
        )
        self._photo_container = QWidget()
        self._photo_container.setStyleSheet(f"background:{theme.BG_SECONDARY};")
        self._photo_grid_layout = _WrapLayout(self._photo_container)
        scroll.setWidget(self._photo_container)
        right_layout.addWidget(scroll, 1)

        self._no_photos_label = QLabel("Noch keine Fotos – wähle ein Verzeichnis\noder importiere einzelne Bilder.")
        self._no_photos_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._no_photos_label.setStyleSheet(
            f"color:{theme.TEXT_MUTED}; font-size:13px; padding:40px;"
        )
        right_layout.addWidget(self._no_photos_label)
        self._no_photos_label.hide()

        self._splitter.addWidget(left)
        self._splitter.addWidget(right)
        self._splitter.setSizes([240, 660])

        # Root layout
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        root_layout.addWidget(self._toolbar)
        root_layout.addWidget(self._splitter)

    # ------------------------------------------------------------------
    # Book list
    # ------------------------------------------------------------------

    def refresh_books(self) -> None:
        self._refresh_book_list()

    def _refresh_book_list(self, selected_book_id: str | None = None) -> None:
        if selected_book_id is None:
            selected_book_id = self._current_book_id

        self._book_list.blockSignals(True)
        self._book_list.clear()

        selected_row = -1
        for row, (book_id, name, count) in enumerate(self._logic.books()):
            item = QListWidgetItem(f"{name}  ({count})")
            item.setData(Qt.ItemDataRole.UserRole, book_id)
            self._book_list.addItem(item)
            if book_id == selected_book_id:
                selected_row = row

        self._book_list.blockSignals(False)

        if selected_row >= 0:
            self._book_list.setCurrentRow(selected_row)
        else:
            self._current_book_id = None
            self._clear_photo_grid()

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
        if not ok:
            return
        book_id = self._logic.create_book(name)
        if not book_id:
            return
        self._refresh_book_list(book_id)

    def _delete_book(self) -> None:
        if not self._current_book_id:
            return
        book = self._logic.get_book(self._current_book_id)
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
        self._logic.delete_book(self._current_book_id)
        self._current_book_id = None
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
        self._logic.set_book_directory(self._current_book_id, dir_path)
        self._dir_label.setText(dir_path)
        self._refresh_book_list()
        self._refresh_photo_grid()

    def _refresh_directory(self) -> None:
        if not self._current_book_id:
            return
        try:
            new_count = self._logic.refresh_book_directory(self._current_book_id)
        except ValueError:
            return
        self._refresh_book_list()
        self._refresh_photo_grid()
        QMessageBox.information(self, "Aktualisiert", f"{new_count} neue Foto(s) gefunden.")

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
        added_count = self._logic.import_photos(self._current_book_id, paths)
        self._refresh_book_list()
        self._refresh_photo_grid()
        QMessageBox.information(self, "Importiert", f"{added_count} Foto(s) hinzugefügt.")

    def _remove_photo(self, path: str) -> None:
        if not self._current_book_id:
            return
        self._logic.remove_photo(self._current_book_id, path)
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
        book = self._logic.get_book(self._current_book_id)
        if not book:
            return

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
        self._on_back()


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
        self._update_stylesheet()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        image_wrap = QFrame()
        image_wrap.setFixedSize(112, 100)

        img_label = QLabel(image_wrap)
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
            img_label.setStyleSheet(f"font-size:28px; color:{theme.TEXT_MUTED};")

        remove_btn = QPushButton(image_wrap)
        remove_btn.setFixedSize(24, 20)
        remove_btn.move(84, 4)
        remove_btn.setToolTip("Foto entfernen")
        remove_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_TrashIcon))
        remove_btn.setIconSize(QSize(14, 14))
        remove_btn.setStyleSheet(
            f"QPushButton {{ background:{theme.DANGER}; color:{theme.WHITE}; border:none; border-radius:4px; }}"
            f"QPushButton:hover {{ background:{theme.DANGER_HOVER}; }}"
        )
        remove_btn.clicked.connect(lambda: self.remove_requested.emit(self._path))
        remove_btn.raise_()
        layout.addWidget(image_wrap)

        name_label = QLabel(Path(path).name)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setStyleSheet(f"font-size:10px; color:{theme.TEXT_SECONDARY};")
        name_label.setWordWrap(True)
        layout.addWidget(name_label)

    def _update_stylesheet(self) -> None:
        """Update the frame stylesheet to reflect current theme."""
        self.setStyleSheet(
            f"QFrame {{ background:{theme.BG_CARD}; border:1px solid {theme.BORDER}; border-radius:6px; }}"
        )


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
                    # Keep widget parent intact while reflowing.
                    # Detaching here can make child widgets appear as tiny top-level windows.
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


