import sys
from PySide6.QtWidgets import QApplication
from gui.main_window import FileManagerWindow

def main():
    app = QApplication(sys.argv)

    window = FileManagerWindow()
    window.show()

    app.exec()


if __name__ == "__main__":
    main()