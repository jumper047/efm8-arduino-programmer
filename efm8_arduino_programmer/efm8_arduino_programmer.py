import sys
from PyQt5.QtWidgets import QApplication

from efm8_arduino_programmer.gui import FlasherWindow

def main():
    app = QApplication(sys.argv)
    flasher = FlasherWindow()
    return app.exec_()
