import sys

from qt_app.vendor.qtpy.QtWidgets import QApplication
from qt_app.window import MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec_()
