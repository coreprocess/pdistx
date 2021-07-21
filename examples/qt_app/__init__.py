import sys

from .vendor.qtpy.QtWidgets import QApplication
from .window import MainWindow


def exec_():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec_()
