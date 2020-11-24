import io
import sys
import glob
import struct
import serial
import shutil
import subprocess
import threading
import traceback

from PyQt5.QtWidgets import QApplication, QComboBox, QFrame, QGridLayout, QHBoxLayout, QLineEdit, QPushButton, QSizePolicy, QTextEdit, QToolButton, QVBoxLayout, QWidget, QLabel, QInputDialog, QMessageBox, QFileDialog, QStyle
import os
from PyQt5.QtCore import pyqtSignal, QTimer
from PyQt5.QtGui import QColor

from flash import PI as flash_PI
from read import PI as read_PI

BIN_DIR = "bin"
BOARDS = {"Arduino Nano (ATmega328P)":{"speed": 57600,
                                       "mcu": "atmega328p",
                                       "hex": "nano_ATmega328P.hex"},

          "Arduino Nano (ATmega168)": {"speed": 19200,
                                       "mcu": "atmega168",
                                       "hex": "nano_ATmega168.hex"}}

AVRDUDE_CONF = "avrdude.conf"
AVRDUDE_BIN = {"win": {"32": "avrdude.exe",
                       "64": "avrdude.exe"},
               "linux": {"32": "avrdude",
                         "64": "avrdude_x64"}}
AVRDUDE_COMMAND = "{bin} -C{config} -v -p{mcu} -carduino -P{port} -b{speed} -D -Uflash:w:{hex}:i"

# from https://stackoverflow.com/questions/12090503/listing-available-com-ports-with-python
def list_serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


def get_root_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.curdir

def get_avrdude_command(target, port):
    """Returns list containing command and arguments, or None if platform not supported"""

    params = dict()

    arch = str(struct.calcsize("P") * 8)
    if sys.platform.startswith('win'):
        platform = 'win'
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        platform = 'linux'
    else:
        return None
    params["bin"] = os.path.join(os.curdir, AVRDUDE_BIN[platform][arch])
    params["config"] = AVRDUDE_CONF
    params.update(BOARDS[target])
    params["port"] = port

    return AVRDUDE_COMMAND.format(**params)


class StdoutProxy:

    def __init__(self, wdgt):
        self.out = sys.stdout
        self.textwidget = wdgt
        self.message_buffer = []
        self.message_timer = QTimer()
        self.message_timer.timeout.connect(self.display_from_buffer)
        self.message_timer.start(500)

    def write(self, message):
        self.out.write(message)
        self.message_buffer.append(message)

    def display_from_buffer(self):
        if len(self.message_buffer) == 0:
            return None
        messages = " ".join(self.message_buffer) + "\n"
        self.textwidget.add_and_scroll(messages)
        self.message_buffer = []

    def fileno(self, *args):
        return self.out.fileno(*args)

    def flush(self):
        self.out.flush()

class StdOutWidget(QTextEdit):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        
    
    def add_and_scroll(self, text):
        self.insertPlainText(text)
        vert_scroll = self.verticalScrollBar()
        if vert_scroll.isVisible():
            vert_scroll.setValue(vert_scroll.maximum())

class FlasherWindow(QWidget):

    new_message = pyqtSignal(str)
    proc_success = pyqtSignal(str)
    proc_failure = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.ports_combobox = QComboBox()
        self.refresh_ports_button = QToolButton()
        self.flash_arduino_button = QPushButton("Flash Arduino")
        self.flash_arduino_button.clicked.connect(self.flash_arduino)
        self.flash_efm_button = QPushButton("Flash EFM8")
        self.flash_efm_button.clicked.connect(self.flash_efm)
        self.read_efm_button = QPushButton("Read from EFM8")
        self.read_efm_button.clicked.connect(self.read_efm)

        self.refresh_ports_button.clicked.connect(self.refresh_ports)

        self.stdout_textedit = StdOutWidget()
        self.new_message.connect(self.stdout_textedit.add_and_scroll)
        self.proxy = StdoutProxy(self.stdout_textedit)
        sys.stdout = self.proxy

        self.proc_success.connect(lambda x: QMessageBox.information(self, "Info", x))
        self.proc_failure.connect(lambda x: QMessageBox.warning(self, "Error", x))

        # if get_avrdude_command is None:
        #     self.flash_arduino_button.setEnabled(False)
        #     self.flash_arduino_button.setToolTip("Platform not supported")

        self.setup_ui()
        self.refresh_ports()


    def setup_ui(self):

        self.refresh_ports_button.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))
        self.refresh_ports_button.setToolTip("Refresh ports list")

        pblayout = QHBoxLayout()
        pblayout.addWidget(QLabel("Com port:"))
        pblayout.addWidget(self.ports_combobox)
        pblayout.addWidget(self.refresh_ports_button)
        pblayout.setStretchFactor(self.ports_combobox, 3)

        btnlayout = QHBoxLayout()
        for b in [self.flash_arduino_button,
                  self.flash_efm_button,
                  self.read_efm_button]:
            s = b.sizePolicy()
            s.setHorizontalPolicy(QSizePolicy.Maximum)
            b.setSizePolicy(s)
            btnlayout.addWidget(b)
        
        main_layout = QVBoxLayout()
        main_layout.addLayout(pblayout)
        main_layout.addLayout(btnlayout)
        main_layout.addWidget(self.stdout_textedit)
        self.setLayout(main_layout)
        self.show()

    def refresh_ports(self):
        self.ports_combobox.clear()
        self.ports_combobox.addItems(list_serial_ports())

    def prepare_flashing(self):
        self.stdout_textedit.clear()
        port = self.ports_combobox.currentText()
        if len(port) == 0:
            QMessageBox.warning(self, "Warning",
                                "Com port not choosen")
            return None
        self.read_efm_button.setEnabled(False)
        self.flash_efm_button.setEnabled(False)
        self.flash_arduino_button.setEnabled(False)
        return port

    def finalize_flashing(self):
        self.read_efm_button.setEnabled(True)
        self.flash_efm_button.setEnabled(True)
        self.flash_arduino_button.setEnabled(True)
        

    def flash_arduino(self):
        port = self.prepare_flashing()
        if port is None:
            return None
            
        board_type, flash = QInputDialog.getItem(self,
                                                 "Flashing Arduino",
                                                 "Choose board type:",
                                                 BOARDS,
                                                 editable=False)
        if not flash:
            return None

        cwd = os.path.join(get_root_dir(), BIN_DIR)

        def run_avrdude():
            process = subprocess.Popen(get_avrdude_command(board_type, port), cwd=cwd, encoding='utf-8', stderr=subprocess.PIPE, shell=True)
            while True:
                output = process.stderr.readline()
                if output == '' and process.poll() is not None:
                    break
                else:
                    self.new_message.emit(output)
            rc = process.poll()
            if rc == 0:
                self.proc_success.emit("Flashing performed successfully")
            else:
                self.proc_failure.emit("Something went wrong while flashing")
            self.finalize_flashing()

        self.avrdude_thread = threading.Thread(target=run_avrdude)
        self.avrdude_thread.start()
        self.read_efm_button.setEnabled(False)
        self.flash_efm_button.setEnabled(False)
        self.flash_arduino_button.setEnabled(False)
        

    def flash_efm(self):
        port = self.prepare_flashing()
        if port is None:
            return None

        firmware_path, flash = QFileDialog.getOpenFileName(self, "Open hex file", get_root_dir(), "Hex (*.hex)")
        if not flash or not os.path.exists(firmware_path):
            self.finalize_flashing()
            return None
        
        def run_efm_flashing():
            try:
                programmers = flash_PI(port)
                with open(firmware_path, 'r') as firmware:
                    programmers.prog(firmware.read())
            except Exception:
                print("Exception occured:")
                print("===============================================")
                traceback.print_exc(file=sys.stdout)
                print("===============================================")
                self.proc_failure.emit("Something went wrong during flashing")
            else:
                self.proc_success.emit("EFM8 flashed successfully")

            self.finalize_flashing()

        self.flash_efm_thread = threading.Thread(target=run_efm_flashing)
        self.flash_efm_thread.start()


    def read_efm(self):
        port = self.prepare_flashing()
        if port is None:
            return None

        save_path, read = QFileDialog.getSaveFileName(self, "Save hex file",
                                                      os.path.join(get_root_dir(), "firmware.hex"),
                                                      "Hex (*.hex)")
        if not read:
            self.finalize_flashing()
            return None

        if os.path.exists(save_path):
            os.remove(save_path)
         
        def run_efm_reading():
            try:
                programmers = read_PI(port)
                with open(save_path, 'x') as firmware:
                    programmers.dump(firmware)
            except Exception:
                print("Exception occured:")
                print("===============================================")
                traceback.print_exc(file=sys.stdout)
                print("===============================================")
                self.proc_failure.emit("Something went wrong during reading")
            else:
                self.proc_success.emit("EFM8 firmware saved successfully")

            self.finalize_flashing()

        self.read_efm_thread = threading.Thread(target=run_efm_reading)
        self.read_efm_thread.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    flasher = FlasherWindow()
    sys.exit(app.exec_())
