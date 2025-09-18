# Compiling and Uploading for Raspberry Pi Pico on macOS

These instructions will guide you through compiling the `src/pico/main.cpp` firmware and uploading it to a Raspberry Pi Pico using the command line on a macOS device.

**Important Note:** This project has a complex build system that is tightly coupled to the **Santroller Configurator** GUI tool. Building directly from the source code without using this tool is a non-trivial task. The following instructions will guide you through a manual build process, which requires several workarounds and the creation of a manual configuration file.

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

The firmware will not compile without a valid configuration. The Santroller Configurator tool normally generates this automatically. For a manual build, you must create a configuration file by hand.

1.  **Create the `config_data.h` file:**
    Create a new file located at `include/config_data.h`.

2.  **Populate the file:**
    Paste the following content into the `include/config_data.h` file. This is a minimal, working configuration that will allow the firmware to compile as a generic gamepad.

    ```c
    #pragma once

    // This is a manually generated config file to allow for a from-source build
    // without the official Santroller Configurator tool.

    // --- Batch 1: From initial compilation failures ---
    #define DEVICE_TYPE 1 // 1 = GAMEPAD
    #define CONFIGURABLE_BLOBS

    // --- Batch 2: From second wave of failures ---
    #define PIN_INIT
    #define WINDOWS_USES_XINPUT 0
    #define LED_COUNT 0
    #define LED_COUNT_PERIPHERAL 0
    #define SLEEP_PIN -1
    #define SLEEP_ACTIVE_HIGH 0

    // --- Batch 3: From third wave of failures ---
    #define LOW_PASS_ALPHA 0.5
    #define ARDWIINO_BOARD "Pico"
    #define HANDLE_AUTH_LED
    #define HANDLE_PLAYER_LED
    #define HANDLE_LIGHTBAR_LED
    #define HANDLE_RUMBLE
    #define HANDLE_RUMBLE_EXPANDED
    #define HANDLE_KEYBOARD_LED
    #define CONFIGURATION_LEN 0

    // --- Batch 4: From fourth wave of failures ---
    #define LED_BRIGHTNESS 100
    #define DIGITAL_COUNT 0
    #define LED_DEBOUNCE_COUNT 0
    #define LED_INIT
    #define WINDOWS_TURNTABLE_FULLRANGE 0
    #define TICK_SHARED
    #define TICK_DETECTION
    #define INPUT_QUEUE 0
    #define TICK_OG_XBOX
    #define TICK_XINPUT
    #define TICK_PS4
    #define TICK_PC
    #define TICK_PS3_WITHOUT_CAPTURE
    #define TICK_PS3
    #define SWAP_SWITCH_FACE_BUTTONS 0
    #define TICK_RESET
    #define SLEEP_INACTIVITY_TIMEOUT_SEC 0
    #define POLL_RATE 0
    #define RPCS3_COMPAT 0
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

During the process of creating these instructions, several bugs in the project's build scripts were identified and fixed. The fixes have been applied directly to the repository. These included:
*   Fixing a dependency issue with the `psutil` Python library.
*   Correcting the path to the `pioasm` tool by compiling it from source and updating the build script.

If you encounter build issues, they may be related to these scripts.

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
