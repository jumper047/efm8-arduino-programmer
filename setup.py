from setuptools import setup

setup(name='efm8_arduino_programmer',
      version='1.0',
      description='Program efm8 micro controller via arduino board',
      url='http://github.com/jumper047/efm8_arduino_programmer',
      packages=['efm8_arduino_programmer'],
      zip_safe=False,
      install_requires=['pyserial'],
      extras_require={
          "gui": "PyQt5"}, 
      entry_points = {
          "console_scripts": [
              "efm8_flash = efm8_arduino_programmer.scripts:flash",
              "efm8_read = efm8_arduino_programmer.scripts:read",
              "efm8_arduino_flash = efm8_arduino_programmer.scripts:flash_arduino"],
          "gui_scripts": ["efm8_programmer = efm8_arduino_programmer.efm8_arduino_programmer:main [gui]"]}
      )
