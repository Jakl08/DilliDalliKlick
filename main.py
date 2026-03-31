#!/usr/bin/env python3
"""DilliDalliKlick – entry point."""

import sys
import ctypes
from pathlib import Path

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget

from dillidalliklick import store
from dillidalliklick.constants import strings, theme
from dillidalliklick.logic.game_logic import GameConfig
from dillidalliklick.screens.menu_window import MenuWindow
from dillidalliklick.screens.game_window import GameWindow
from dillidalliklick.screens.photobook_window import PhotobookWindow
from dillidalliklick.screens.settings_window import SettingsWindow
from dillidalliklick.store import StoreData


ICON_PATH = Path(__file__).parent / "project_image" / "generated" / "dalli_klick_icon.ico"
APP_ID = f"{strings.ORGANIZATION_NAME}.{strings.APP_NAME}"


def _configure_windows_app_id() -> None:
    if sys.platform != "win32":
        return
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)


class AppWindow(QMainWindow):

    def __init__(self, app_state: StoreData) -> None:
        super().__init__()
        self._state = app_state
        self.setWindowTitle(strings.APP_NAME)
        if ICON_PATH.exists():
            self.setWindowIcon(QIcon(str(ICON_PATH)))
        self.setMinimumSize(900, 680)

        self._stack = QStackedWidget(self)
        self.setCentralWidget(self._stack)

        self._menu = MenuWindow(
            on_open_settings=self._open_settings,
            on_open_photobooks=self._open_photobooks,
            on_change_scheme=self._change_color_scheme,
            active_scheme=theme.get_active_scheme(),
        )
        self._settings = SettingsWindow(
            app_state=self._state,
            on_back=self._show_menu,
            on_start_game=self._open_game,
        )
        self._photobooks = PhotobookWindow(
            app_state=self._state,
            on_back=self._show_menu,
        )
        self._game = GameWindow(
            on_back_settings=self._open_settings,
            on_back_menu=self._show_menu,
        )

        self._stack.addWidget(self._menu)
        self._stack.addWidget(self._settings)
        self._stack.addWidget(self._photobooks)
        self._stack.addWidget(self._game)
        self._stack.setCurrentWidget(self._menu)

    def _open_settings(self) -> None:
        self._settings.refresh_books()
        self._stack.setCurrentWidget(self._settings)

    def _open_photobooks(self) -> None:
        self._photobooks.refresh_books()
        self._stack.setCurrentWidget(self._photobooks)

    def _show_menu(self) -> None:
        self._stack.setCurrentWidget(self._menu)

    def _change_color_scheme(self, scheme_name: str) -> None:
        theme.set_active_scheme(scheme_name)
        app = QApplication.instance()
        if app is not None:
            theme.apply(app)

    def _open_game(self, config: GameConfig) -> None:
        self._game.start_game(config)
        self._stack.setCurrentWidget(self._game)


def main() -> None:
    _configure_windows_app_id()

    app = QApplication(sys.argv)
    app.setApplicationName(strings.APP_NAME)
    app.setOrganizationName(strings.ORGANIZATION_NAME)
    if ICON_PATH.exists():
        app.setWindowIcon(QIcon(str(ICON_PATH)))

    theme.apply(app)

    data = store.load()

    window = AppWindow(app_state=data)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
