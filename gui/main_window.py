from PySide6.QtWidgets import QMainWindow


class FileManagerWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("File Manager")
        self.resize(1000, 650)