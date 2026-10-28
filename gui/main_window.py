from PySide6.QtWidgets import QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout


class FileManagerWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("File Manager")
        self.resize(1000, 650)

        self.container = QWidget()
        self.vertical_layout = QVBoxLayout()
        self.container.setLayout(self.vertical_layout)
        self.setCentralWidget(self.container)
    
        self.horizontal_layout = QHBoxLayout()
        self.vertical_layout.addLayout(self.horizontal_layout)


        self.label = QLabel("Welcome to my File Manager!")
        self.vertical_layout.addWidget(self.label)

        self.directory_label = QLabel(r"Current directory: C:\Users")
        self.vertical_layout.addWidget(self.directory_label)


        self.name_label = QLabel("name")
        self.horizontal_layout.addWidget(self.name_label)

        self.type_label = QLabel("type")
        self.horizontal_layout.addWidget(self.type_label)

        self.size_label = QLabel("size")
        self.horizontal_layout.addWidget(self.size_label)