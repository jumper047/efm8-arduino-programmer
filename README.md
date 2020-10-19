# Setting up

C2 is a 2-pin protocol.  Any arduino should work to implement the protocol via GPIO.  Just need to make sure that the correct pins are mapped for your Arduino. Currently, it is:
- for Arduino Mega and maps C2D and C2CK to digital pins 2 and 3, respectively.
- for Arduino Uno and maps C2D and C2CK to digital pins 5 and 6, respectively.

Program the firmware to the arduino and connect C2D, C2CK, and GND to your target device.
# Software

You need to have Python installed.  Then, install module pyserial.

```
pip install -r pyserial
```

# Running

Programming one target.

```
python flash.py <serial-port> <firmware.hex>
```

Dumping one target.

```
python read.py <serial-port> <firmware.hex>
```
# Troubleshooting

- Some modules need sudo on some systems

# Changing the communication speed


Edit the following lines:
In the Python program modify the following line to switch to a speed of 115200baud / sec:

    self.ser = serial.Serial (com, 115200, timeout = 1)
In the program of your Arduino:

    Serial.begin (115200);
