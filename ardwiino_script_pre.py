#!/usr/bin/env python3
from pprint import pp
import subprocess
import sys
from os.path import join
try:
    import libusb_package
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "libusb-package"])
from platformio.util import get_serial_ports, get_systype
from platformio.exception import ReturnErrorCode, UserSideException
from platformio.package.manager.tool import ToolPackageManager
from platformio.proc import get_pythonexe_path, where_is_program
from serial import Serial, SerialException
import os

try:
    import psutil
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])
import glob
from time import sleep
import subprocess
import platform

REBOOT=48
BOOTLOADER=49
BOOTLOADER_SERIAL=50
class Context:
    def __init__(self):
        self.meta = ""

me = psutil.Process(os.getpid())
Import("env")
pioasm_tool = {"Windows": "x86_64-w64-mingw32.pioasm-efe2103.240919.zip","Linux":"x86_64-linux-gnu.pioasm-efe2103.240919.tar.gz","Darwin":"x86_64-apple-darwin20.4.pioasm-efe2103.240919.tar.gz"}
# Compile any .pio files
if "pico" in env["BOARD"]:
    pioasm_path = os.path.join(env.PioPlatform().get_package_dir("framework-arduinopico"), "pico-sdk", "tools", "pioasm", "build", "pioasm")
    for file in glob.iglob(os.path.join(env["PROJECT_SRC_DIR"],"pico","**","*.pio"),recursive=True):
        subprocess.call([pioasm_path, os.path.join(env["PROJECT_SRC_DIR"],"pico",file), os.path.join(env["PROJECT_SRC_DIR"],"pico",file+".h")])

if "upload" in BUILD_TARGETS:
    upload_options = env.BoardConfig().get("upload", {})
    if "detect_controller" in upload_options and upload_options["detect_controller"] == "true":
        if (libusb_package.find(idVendor=0x03eb,idProduct=0x0010) or libusb_package.find(idVendor=0x03eb,idProduct=0x003f) or libusb_package.find(idVendor=0x03eb,idProduct=0x0001)):
            print("Found Uno/Mega, touching port")
            env.AutodetectUploadPort()
            env.TouchSerialPort("$UPLOAD_PORT", 1200)
        print("Detecting microcontroller type")
        dev = None
        while not dev:
            if me.parent is None:
                exit(1)
            dev = libusb_package.find(idVendor=0x03eb, idProduct=0x2FF7)
            if dev:
                env["BOARD_MCU"] = "at90usb82"
                break
            dev = libusb_package.find(idVendor=0x03eb, idProduct=0x2FEF)
            if dev:
                env["BOARD_MCU"] = "atmega16u2"
                break
            pass
        # Windows needs to erase before programming
        if sys.platform == 'win32':
            print("Erasing")
            subprocess.run([join(env["PROJECT_CORE_DIR"],"dfu-programmer"), env["BOARD_MCU"], "erase", "--force"], stderr=subprocess.STDOUT)
    if "detect_frequency_mini" in upload_options and upload_options["detect_frequency_mini"] == "true":
        print("Uploading script to detect speed")
        cwd = os.getcwd()
        os.chdir(env["PROJECT_DIR"])
        subprocess.run([sys.executable, "-m", "platformio", "run", "--target", "upload", "--environment", "minidetect", "--upload-port", env.subst("$UPLOAD_PORT")], stderr=subprocess.STDOUT)
        os.chdir(cwd)
        port = env.subst("$UPLOAD_PORT")
        s = Serial(port=port, baudrate=115200)
        rate = f"{s.readline().decode('utf-8').strip()}000000"
        print(rate)
        # rate = usb.util.get_string(dev, dev.iProduct, 0x0409).split("\x00")[0].rpartition(" - ")[2]
        rate = f"{rate}L"
        env["BOARD_F_CPU"] = rate
    if "detect_frequency" in upload_options and upload_options["detect_frequency"] == "true":
        print("Uploading script to detect speed")
        cwd = os.getcwd()
        os.chdir(env["PROJECT_DIR"])
        subprocess.run([sys.executable, "-m", "platformio", "run", "--target", "upload", "--environment", "microdetect", "--upload-port", env.subst("$UPLOAD_PORT")], stderr=subprocess.STDOUT)
        os.chdir(cwd)
        print("Uploaded, waiting for device to show up")
        dev = None
        while not dev:
            if me.parent is None:
                exit(1)
            dev = libusb_package.find(idVendor=0x1209, idProduct=0x2886)
            pass
        sleep(5)
        dev = libusb_package.find(idVendor=0x1209, idProduct=0x2886)
        rate = dev.product.split('\x00',1)[0].split(" - ")[2]
        rate = f"{rate}L"
        env["BOARD_F_CPU"] = rate
        print("Found rate: "+rate)
        print("Returning to bootloader")
        try:
            dev.ctrl_transfer(0x21, BOOTLOADER)
        except Exception as e:
            print(e)
            pass
        dev = None
        print("Waiting for bootloader device")
        sleep(3)
        subprocess.run([join(env.PioPlatform().get_package_dir("tool-avrdude"),"avrdude"), "-C", join(env.PioPlatform().get_package_dir("tool-avrdude"), "avrdude.conf"), "-p", "atmega32u4", "-P", env.subst("$UPLOAD_PORT"), "-c","avr109", "-e"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

def mytarget_callback(*args, **kwargs):
    env.TouchSerialPort("$UPLOAD_PORT", 1200)
    env["UPLOAD_PORT"] = None
    env.AutodetectUploadPort()
    print("PORT: "+env.subst("$UPLOAD_PORT"))

def mytarget_callback2(*args, **kwargs):
    env["UPLOAD_PORT"] = None
    before_ports = get_serial_ports()
    print("Waiting for bootloader device")
    env.Replace(UPLOAD_PORT=env.WaitForNewSerialPort(before_ports))
    print("PORT: "+env.subst("$UPLOAD_PORT"))

env.AddCustomTarget(
    name="micro_clean",
    dependencies=None,
    actions=['"$PROJECT_PACKAGES_DIR/tool-avrdude/avrdude" -C "$PROJECT_PACKAGES_DIR/tool-avrdude/avrdude.conf" -p atmega32u4 -P $UPLOAD_PORT -c avr109 -e'],
    title=None,
    description=None
)

env.AddCustomTarget(
    name="micro_clean_existing",
    dependencies=None,
    actions=[mytarget_callback2,'"$PROJECT_PACKAGES_DIR/tool-avrdude/avrdude" -C "$PROJECT_PACKAGES_DIR/tool-avrdude/avrdude.conf" -p atmega32u4 -P $UPLOAD_PORT -c avr109 -e'],
    title=None,
    description=None
)

env.AddCustomTarget(
    name="micro_clean_jump",
    dependencies=None,
    actions=[mytarget_callback,'"$PROJECT_PACKAGES_DIR/tool-avrdude/avrdude" -C "$PROJECT_PACKAGES_DIR/tool-avrdude/avrdude.conf" -p atmega32u4 -P $UPLOAD_PORT -c avr109 -e'],
    title=None,
    description=None
)

# Windows needs to use a different programmer command
if sys.platform == 'win32':
    for type in ["arduino_mega_2560", "arduino_mega_adk", "arduino_uno"]:
        for proc, board in [("8","at90usb82"), ("16","atmega16u2")]:
            env.AddCustomTarget(
                name=f"{type}_{proc}_clean",
                dependencies=None,
                actions=[f'"$PROJECT_CORE_DIR/dfu-programmer" {board} erase --force', f'"$PROJECT_CORE_DIR/dfu-programmer" {board} flash "$PROJECT_PACKAGES_DIR/../../default_firmwares/{type}_usb.hex"'],
                title=None,
                description=None
            )
else:
    for type in ["arduino_mega_2560", "arduino_mega_adk", "arduino_uno"]:
        for proc, board in [("8","at90usb82"), ("16","atmega16u2")]:
            env.AddCustomTarget(
                name=f"{type}_{proc}_clean",
                dependencies=None,
                actions=[f'"$PROJECT_PACKAGES_DIR/tool-avrdude/avrdude" -F -C "$PROJECT_PACKAGES_DIR/tool-avrdude/avrdude.conf" -p {board} -u -c flip1 -U flash:w:"$PROJECT_PACKAGES_DIR/../../default_firmwares/{type}_usb.hex:i"'],
                title=None,
                description=None
            )