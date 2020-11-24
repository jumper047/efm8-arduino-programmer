from efm8_arduino_programmer.efm8 import PI
import sys
import subprocess
import os
from efm8_arduino_programmer.helpers import get_root_dir
from efm8_arduino_programmer.arduino import get_avrdude_command, BIN_DIR


def flash():
    if len(sys.argv) != 3:
        print("usage: %s <port> <firmware.hex>" % sys.argv[0])
        sys.exit(1)
    print("Once")
    port = sys.argv[1]
    firmware = open(sys.argv[2], "r").read()
    programmers = PI(port)
    programmers.prog(firmware)


def read():
    if len(sys.argv) != 3:
        print("usage: %s <port> <firmware.hex>" % sys.argv[0])
        sys.exit(1)

    print("Once")
    port = sys.argv[1]
    with open(sys.argv[2], "x") as firmware:
        programmers = PI(port)
        programmers.dump(firmware)


def flash_arduino():
    boards = {
        "nano_328p": "Arduino Nano (ATmega328P)",
        "nano_168": "Arduino Nano (ATmega168)",
    }

    if len(sys.argv) != 3:
        print("usage {} <board_name> <port>".format(sys.argv[0]))
        print("possible board names are {}".format(", ".join(boards.keys())))
        sys.exit(1)

    board = sys.argv[1]
    assert board in boards

    port = sys.argv[2]
    cwd = os.path.join(get_root_dir(), BIN_DIR)
    subprocess.Popen(get_avrdude_command(board, port), cwd=cwd, shell=True)
