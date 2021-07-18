import sys

from PyQt5.QtWidgets import QApplication

# import our packed file first for initialize our virtual bundle
import packed.my_lib
from packed.my_lib.custom_widgets.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec_()
