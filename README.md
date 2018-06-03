# Setting up

C2 is a 2-pin protocol.  Any arduino should work to implement the protocol via GPIO.  Just need to make sure that the correct pins are mapped for your Arduino.  Check the [firmware file Arduino Mega](https://github.com/christophe94700/efm8-arduino-programmer/blob/master/prog/arduino_mega.ino#L11) or [firmware file Arduino Uno](https://github.com/christophe94700/efm8-arduino-programmer/blob/master/prog/arduino_uno.ino#L11) and change the pins to map to your device if needed.  Currently, it is:
- for Arduino Mega and maps C2D and C2CK to digital pins 2 and 3, respectively.
- for Arduino Uno and maps C2D and C2CK to digital pins 5 and 6, respectively.

Program the firmware to the arduino and connect C2D, C2CK, and GND to your target device.
# Firmware
For RF Bridge [RF_Bridge](https://github.com/christophe94700/efm8-arduino-programmer/blob/master/Firmware/RF_Bridge.hex)
For Test blinking blue Led [Blinky Led](https://github.com/christophe94700/efm8-arduino-programmer/blob/master/Firmware/Blinky_Led.hex)
# Software

You need to have Python installed.  Then, install some required python modules.
Use Python 2.7 and Pyserial for [flash27.py](https://github.com/christophe94700/efm8-arduino-programmer/blob/master/flash27.py)
Use Python 3.6 and Pyserial for [flash36.py](https://github.com/christophe94700/efm8-arduino-programmer/blob/master/flash36.py)

```
pip install -r requirements.txt
```

# Running

Programming one target.

```
python flash.py <serial-port> <firmware.hex>
```

Example for Linux: 
```flash27.py /dev/ttyACM0 RF_Brige.hex```
or 
```sudo flash27.py /dev/ttyACM0 RF_Brige.hex```

Example for Windows: ```python flash27.py COM8 RF_Bridge.hex```

# Troubleshooting

- Some modules need sudo on some systems

# Changing the communication speed


Edit the following lines:
In the Python program modify the following line to switch to a speed of 115200baud / sec:

    self.ser = serial.Serial (com, 115200, timeout = 1)
In the program of your Arduino:

    Serial.begin (115200);
