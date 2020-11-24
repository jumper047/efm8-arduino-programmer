import os
import re
import sys
import site

from cx_Freeze import Executable, setup

def get_qt_plugin_includes(plugin_list):
    includes = []
    for ppath in plugin_list:
        includes.append(_get_include(ppath))
        pass
    return includes


def _get_include(plugin_path):
    foundPath = None

    if sys.platform == "darwin":
        packagesDirs = [c for c in sys.path if c.find("site-packages") != -1]
    else:
        # search site packages locations to see if we can find required .dll
        packagesDirs = site.getsitepackages()
        pass
    for pdir in packagesDirs:
        testPath = os.path.join(
            pdir, os.path.join("PyQt5", "Qt", "plugins", plugin_path)
        )
        bname = os.path.basename(plugin_path)

        # print("Checking for {} at {}".format(bname, testPath))
        if os.path.exists(testPath):
            foundPath = testPath
            # print("DLL Found")
            break
        pass
    if foundPath is None:
        print(f"Error, could not find: {plugin_path}")
        sys.exit(1)

    return (foundPath, plugin_path)

build_dir = "build"
include_files = [("bin", "bin")]

required_plugins = []
if sys.platform == "win32":
    # force the inclusion of certain plugins that cx-freeze cannot find on its own
    required_plugins = [
        "styles/qwindowsvistastyle.dll"
    ]

# # fix for building with wine
# try:
#     winreg.OpenKeyEx(winreg.HKEY_LOCAL_MACHINE, "Software\Wine")
# except FileNotFoundError:
#     pass
# else:
#     for py_dir in site.getsitepackages():
#         base_dir, _, files = next(os.walk(py_dir))
#         if 'python3.dll' not in files:
#             continue
#         python3_dll = os.path.join(py_dir, 'python3.dll')
#         vcruntime140_dll = os.path.join(py_dir, 'vcruntime140.dll')
#         for f in files:
#             if re.match('python3[0-9]+\.dll', f):
#                 python3x_dll = os.path.join(py_dir, f)
#                 python3x_name = f
#                 break
#     include_files += [(python3_dll, os.path.join('lib','PyQt5', 'python3.dll')),
#                       (vcruntime140_dll, 'vcruntime140.dll'),
#                       (python3x_dll, python3x_name)]

if len(required_plugins) > 0:
    include_files += get_qt_plugin_includes(plugin_list=required_plugins)

options = {
    'build_exe': {
        'build_exe': build_dir,
        'include_files': include_files, 
        'include_msvcr': True,
        'zip_include_packages': ["PyQt5"],
        'packages': ["PyQt5.sip"]
    }
}

base = None
# if sys.platform == "win32":
#     base = "Win32GUI"

executables = [
    Executable('gui_flasher.py', base=base)
]

setup(name='efm8-programmer',
      version="1.0.0",
      description='EFM8 Programmer',
      options=options,
      executables=executables)
