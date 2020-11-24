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


def get_avrdude_command(target, port):
    """Returns command string or None if platform not supported"""

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
