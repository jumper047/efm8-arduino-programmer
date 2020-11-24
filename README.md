# Setting up

C2 is a 2-pin protocol.  Any arduino should work to implement the protocol via GPIO.  Just need to make sure that the correct pins are mapped for your Arduino. Currently, it  maps C2D and C2CK to digital pins 2 and 3, respectively.
Flash the firmware to the arduino and connect C2D, C2CK, and GND to your target device.

# Installing via pip

You need to have Python installed.  Then run from project's folder

```
python -m pip install git+https://github.com/jumper047/efm8-arduino-programmer.git
```

# Running

Programming one target.

```
efm8_flash <serial-port> <firmware.hex>
```

Dumping one target.

```
efm8_read <serial-port> <firmware.hex>
```

Flash arduino
```
efm8_arduino_flash <board> <serial-port>
```
For now supported only Arduino Nano boards: "nano_328p" for Nano with ATmega328p and "nano_168" for Nano with ATmega168

Run gui
```
efm8_programmer
```

# Troubleshooting

- Some modules need sudo on some systems

# Changing the communication speed


Edit the following lines:
In the Python program modify the following line to switch to a speed of 115200baud / sec:

    self.ser = serial.Serial (com, 115200, timeout = 1)
In the program of your Arduino:

    Serial.begin (115200);
