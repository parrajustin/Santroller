# Compiling and Uploading for Raspberry Pi Pico on macOS

These instructions will guide you through compiling the `src/pico/main.cpp` firmware and uploading it to a Raspberry Pi Pico using the command line on a macOS device.

**Important Note:** This project has a complex build system that is tightly coupled to the **Santroller Configurator** GUI tool. Building directly from the source code without using this tool is a non-trivial task. The following instructions will guide you through a manual build process, which requires several workarounds and a manual configuration.

## Prerequisites

Before you begin, you will need to install a few tools.

### 1. Homebrew

If you don't have Homebrew, the macOS package manager, install it by following the instructions on the [official Homebrew website](https://brew.sh/).

### 2. Python 3

PlatformIO is built on Python. You can install Python 3 using Homebrew:

```bash
brew install python3
```

### 3. PlatformIO CLI

PlatformIO is a powerful tool for embedded development. Install the PlatformIO command-line interface (CLI) using pip, which comes with Python:

```bash
pip3 install -U platformio
```

You may need to add the PlatformIO script directory to your `PATH`. The installer will provide you with the necessary command, which will look something like this (the exact path may vary):

```bash
export PATH=$PATH:/Users/your-username/Library/Python/3.x/bin
```

Add this line to your shell's profile file (e.g., `~/.zshrc` or `~/.bash_profile`) to make the change permanent.

## Configuration

The firmware will not compile without a valid configuration. The Santroller Configurator tool normally generates this automatically. For a manual command-line build, you must provide the configuration as build flags in the `platformio.ini` file.

Open `platformio.ini` and locate the `[pico_parent]` section. Modify the `build_flags` to include the following definitions. This minimal configuration will build the firmware as a generic Xbox-style gamepad.

```ini
build_flags =
	-DPIO_USB_DP_PIN_DEFAULT=20
	-Isrc/pico
	-DPIO_FRAMEWORK_ARDUINO_NO_USB
	; Core Configuration
	; Sets the primary device type. 1 = GAMEPAD
	-DDEVICE_TYPE=1
	; Allows build without a static config array by using pointers instead.
	-DCONFIGURABLE_BLOBS
	; Hardware Pin & LED Configuration
	; Placeholder for pin initialization code.
	-DPIN_INIT=
	; Placeholder for LED initialization code.
	-DLED_INIT=
	; Number of standard LEDs. 0 = disabled.
	-DLED_COUNT=0
	; Number of LEDs on a peripheral. 0 = disabled.
	-DLED_COUNT_PERIPHERAL=0
	; Number of LEDs that require debouncing.
	-DLED_DEBOUNCE_COUNT=0
	; Default LED brightness (0-255).
	-DLED_BRIGHTNESS=100
	; GPIO pin for sleep mode. -1 = disabled.
	-DSLEEP_PIN=-1
	; Logic level for sleep pin.
	-DSLEEP_ACTIVE_HIGH=0
	; Inactivity timeout for auto-sleep in seconds. 0 = disabled.
	-DSLEEP_INACTIVITY_TIMEOUT_SEC=0
	; Input Processing Configuration
	; Number of digital button inputs. 16 is a safe value for a generic gamepad.
	-DDIGITAL_COUNT=16
	; Use an input queue. 0 = disabled.
	-DINPUT_QUEUE=0
	; USB polling rate in ms. 1 = 1000Hz.
	-DPOLL_RATE=1
	; Low-pass filter alpha for accelerometer.
	-DLOW_PASS_ALPHA=0.5
	; Swap A/B and X/Y buttons for Nintendo layout. 0 = disabled.
	-DSWAP_SWITCH_FACE_BUTTONS=0
	; Controller Emulation & Miscellaneous
	; Board name for USB descriptor.
	-DARDWIINO_BOARD="\"Pico\""
	; Length of the config array, used for bounds checking.
	-DCONFIGURATION_LEN=0
	; Use XInput protocol on Windows. 1 = enabled.
	-DWINDOWS_USES_XINPUT=1
	; Enable RPCS3 (PS3 emulator) compatibility workarounds. 0 = disabled.
	-DRPCS3_COMPAT=0
	; Placeholders for protocol-specific tick functions.
	-DTICK_SHARED=
	-DTICK_DETECTION=
	-DTICK_OG_XBOX=
	-DTICK_XINPUT=
	-DTICK_PS4=
	-DTICK_PC=
	-DTICK_PS3_WITHOUT_CAPTURE=
	-DTICK_PS3=
	-DTICK_RESET=
	; Placeholders for LED and rumble handlers.
	-DHANDLE_AUTH_LED=
	-DHANDLE_PLAYER_LED=
	-DHANDLE_LIGHTBAR_LED=
	-DHANDLE_RUMBLE=
	-DHANDLE_RUMBLE_EXPANDED=
	-DHANDLE_KEYBOARD_LED=
```

## Compiling the Firmware

With the prerequisites and configuration in place, you can now compile the firmware.

1.  **Navigate to the project directory:**
    Open a terminal and `cd` into the root of this repository.

2.  **Compile the `pico` environment:**
    The `platformio.ini` file defines several environments. To compile the main firmware for the Pico, use the following command:

    ```bash
    platformio run -e pico
    ```

    This command will download the necessary toolchains and libraries and then build the firmware. The compiled firmware file will be located at `.pio/build/pico/firmware.uf2`.

### Build Notes & Workarounds

During the process of creating these instructions, a bug in the project's build scripts (`ardwiino_script_pre.py`) was identified and fixed. The fix has been applied directly to the repository. If you encounter build issues, they may be related to this script.

## Uploading to the Raspberry Pi Pico

1.  **Enter Bootloader Mode:**
    - Disconnect your Raspberry Pi Pico from your computer.
    - Press and hold the **BOOTSEL** button on the Pico.
    - While still holding the button, connect the Pico to your Mac with a USB cable.
    - Release the **BOOTSEL** button.

    Your Mac should now detect the Pico as a mass storage device named `RPI-RP2`.

2.  **Upload the Firmware:**
    There are two ways to upload the firmware:

    **Method 1: Drag and Drop**
    - Open the `RPI-RP2` drive that appeared on your desktop.
    - Drag and drop the `firmware.uf2` file from `.pio/build/pico/firmware.uf2` into the `RPI-RP2` drive.
    - The Pico will automatically reboot and run the new firmware.

    **Method 2: PlatformIO Upload Command**
    - With the Pico in bootloader mode, run the following command in your terminal:

      ```bash
      platformio run -e pico --target upload
      ```

    PlatformIO will automatically find the Pico and upload the firmware. The Pico will then reboot and start running the program.
