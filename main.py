import sys

from PySide6.QtWidgets import QApplication

from app import theme
from app.db import Database, seed_demo
from app.shell import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Visia")
    theme.load_fonts()
    app.setFont(theme.font(theme.BODY, 14))
    app.setStyleSheet(theme.STYLESHEET)

    db = Database()
    seed_demo(db)

    window = MainWindow(db)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
