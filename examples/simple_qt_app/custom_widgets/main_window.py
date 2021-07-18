from PyQt5.QtWidgets import QLabel, QMainWindow
from PyQt5.QtCore import Qt


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.setWindowTitle("Example App")

        label = QLabel("This is a window!")
        label.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(label)
