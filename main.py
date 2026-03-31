#!/usr/bin/env python3
"""DilliDalliKlick – entry point."""

import sys

from PyQt6.QtWidgets import QApplication

from dillidalliklick import store, theme
from dillidalliklick.menu_window import MenuWindow


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("DilliDalliKlick")
    app.setOrganizationName("DilliDalliKlick")

    theme.apply(app)

    data = store.load()

    window = MenuWindow(app_state=data)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
