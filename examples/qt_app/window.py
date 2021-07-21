from .vendor.qtpy.QtCore import Qt
from .vendor.qtpy.QtWidgets import QLabel, QMainWindow


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.setWindowTitle('Example App')

        label = QLabel('This is a window!')
        label.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(label)
