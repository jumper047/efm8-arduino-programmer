import os
import re
import shutil
import subprocess

from cx_Freeze import Executable, setup

build_dir = "build"

shutil.rmtree(build_dir, ignore_errors=True)

options = {
    'build_exe': {
        # Including all modules from plugins except PyQt5
        'build_exe':
        build_dir,
        'include_files': [
            ("binaries", "binaries"),
        ]
    }
}

executables = [
    Executable('efm8_programmer.py', base='Win32GUI')
]

re_unwanted_files = [
    "Qt5?Bluetooth.*$", "Qt5?DBus.*$", "Qt5?Designer.*$", "Qt5?Help.*$",
    "Qt5?Location.*$", "Qt5?Multimedia.*$", "Qt5?MultimediaWidgets.*$",
    "Qt5?NetworkAuth.*$", "Qt5?Network.*$", "Qt5?Nfc.*$", "Qt5?Positioning.*$",
    "Qt5?PrintSupport.*$", "Qt5?Qml.*$", "Qt5?Quick.*$", "Qt5?QuickWidgets.*$",
    "Qt5?RemoteObjects.*$", "Qt5?Sensors.*$", "Qt5?SerialPort.*$",
    "Qt5?Sql.*$", "Qt5?Svg.*$", "Qt5?WebChannel.*$", "Qt5?WebSockets.*$",
    "Qt5?WinExtras.*$", "Qt5?XmlPatterns.*$", "Qt5?Xml.*$", ".*_de.qm",
    ".*_gd.qm", ".*_ca.qm", ".*_fi.qm", ".*_cs.qm", ".*_da.qm", ".*_fr.qm",
    ".*_bg.qm", ".*_es.qm", ".*_pl.qm", ".*_it.qm", ".*_hu.qm", ".*_ar.qm",
    ".*_uk.qm", ".*_lv.qm", ".*_he.qm", ".*_ko.qm", ".*_ja.qm", ".*_sk.qm"
]

unwanted_dirs = ["lib/PyQt5/Qt/qml"]

unwanted_files_dirs = [
    ("lib/PyQt5/",
     ["Qt5Charts.dll", "Qt5Core.dll", "Qt5Gui.dll", "Qt5Widgets.dll"])
]

plugin_dirs = ["lib/PyQt5/Qt/plugins/platforms", "lib/PyQt5/Qt/plugins/styles"]

setup(name='EFM8 Programmer',
      version='1.0',
      description='GUI for EFM8 programmer',
      options=options,
      executables=executables)

files = set()

for dirpath, dirnames, filenames in os.walk(build_dir):
    for filename in filenames:
        for entity in re_unwanted_files:
            if re.match(entity, filename):
                files.add(os.path.join(dirpath, filename))

    for dirpath, filenames in unwanted_files_dirs:
        for filename in filenames:
            files.add(os.path.join(build_dir, dirpath, filename))

for f in files:
    try:
        os.remove(f)
        print("removing file {0}".format(f))
    except Exception as e:
        print("Error occured - {0}".format(e))

for d in unwanted_dirs:
    try:
        shutil.rmtree(os.path.join(build_dir, d))
        print("removing dir {0}".format(d))
    except Exception as e:
        print("Error occured - {0}".format(e))

for d in plugin_dirs:
    shutil.copytree(os.path.join(build_dir, d),
                    os.path.join(build_dir, os.path.basename(d)))
