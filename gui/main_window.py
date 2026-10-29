from PySide6.QtWidgets import QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit


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

        self.test_button = QPushButton("Click me")
        self.vertical_layout.addWidget(self.test_button)
        self.test_button.clicked.connect(self.button_clicked)

        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Enter a directory path....")
        self.vertical_layout.addWidget(self.path_input)
        entered_path = self.path_input.text()

    def button_clicked(self):
        self.label.setText("You clicked the button!")