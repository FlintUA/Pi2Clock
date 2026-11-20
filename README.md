# Pi2Clock — speaking clock on Raspberry Pi Pico 2 W

Pi2Clock is an open-source speaking clock and DIY kit: an LCD1602 clock with a DS1302 real-time clock, two rotary encoders and five buttons that announces the time in Russian or German, runs a countdown timer, five alarms, annual birthday reminders and a music player, and can play through its own speaker or a Bluetooth speaker. It can be controlled from a phone or tablet browser over the home Wi-Fi or a direct Wi-Fi connection, and updated over the air.

## Generations

| Generation | Hardware | Firmware | State |
| --- | --- | --- | --- |
| [G0](doc/generations/G0.md) | Raspberry Pi Pico, DFPlayer Mini | MicroPython 1.x–3.10.0 | Archived in [generations/g0-micropython](generations/g0-micropython/) |
| [G1](doc/generations/G1.md) | Pico 2 W, DFPlayer Mini with its card + SPI microSD for Bluetooth | C / Pico SDK, [firmware/pico2w_c](firmware/pico2w_c/) | **Current**, the assembled clock |
| [G2](doc/generations/G2.md) | Pico 2 W, MAX98357A I2S amplifier, one SD card, no DFPlayer | — | Planned |

See the [generation overview](doc/generations/README.md) for the comparison, identity rules and repository layout.

## G1 features

- Spoken time, date and nearest alarm (RU/DE); hourly speech or chime, half-hour beep, quiet hours.
- One countdown timer from 1 second to 23:59:59 with configurable completion message, signal, fixed or random music and an optional five-second warning.
- Five alarms with weekday schedules, signal / fixed music / random music and three-minute snooze; fifteen annual birthdays with optional birth year.
- Music player for folder 08 with normal, shuffle and repeat-one order, Previous/Next history, pause and a sleep timer.
- Two sound outputs: the built-in DFPlayer speaker and a Classic Bluetooth A2DP speaker (up to four remembered), with automatic fallback; separate volumes and per-event output preferences.
- Wi-Fi with two saved home networks or a Direct access point, NTP time with Europe/Berlin daylight saving, browser control with paired permissions, and A/B over-the-air updates.
- LCD light with Off/On/Auto and day/night brightness; settings stored in Flash with backward-compatible migrations.

Current work items, acceptance status and the release baseline are tracked in the [roadmap](doc/ROADMAP.md) and [testing](doc/TESTING.md). The latest tagged release is [v1.0.0](https://github.com/FlintUA/Pi2Clock/releases/tag/v1.0.0); `main` contains the newer G1 development line.

## Hardware

Parts, audio paths and Flash layout: [G1 hardware](doc/generations/G1.md#hardware). Pin assignment: [Pico 2 W pin map](doc/HARDWARE_PICO2W.md). Audio assets: [sound/_sdcard](sound/_sdcard/), copied to the root of **both** the DFPlayer card and the Pico SPI card.

## Building and installing (Windows)

Requirements under `%USERPROFILE%\.pico-sdk`: Pico SDK 2.3.1, pico-examples, CMake 4.3.4, Arm GNU toolchain, Ninja, pioasm and picotool. The MP3 decoder is fetched separately:

```powershell
git clone https://github.com/Lefucjusz/Helix-MP3-Decoder.git third_party/Helix-MP3-Decoder
git -C third_party/Helix-MP3-Decoder checkout e4f5adadb5126708144e55a862f59e318cbffb51
```

Use a short path without non-ASCII characters for build directories, for example `C:\pico_clock_compile`.

| Goal | Command |
| --- | --- |
| Build the web profile (USB install) | `.\build-clock-bt.ps1 -Mp3 -PhoneWeb -BuildDirectory C:\pico_clock_compile\phone-clock` |
| Install a reviewed build over USB | `.\update-pico.ps1 -Port COM8 -Uf2 C:\pico_clock_compile\phone-clock\speaking_clock_c.uf2` |
| Build an OTA image and package | `.\build-clock-bt.ps1 -Mp3 -PhoneWeb -OtaAb -OtaTrial -OtaSequence N …`, then `python tools\ota_web_package.py --build <dir> …` ([details](doc/OTA_WEB_UPDATE.md)) |
| Provision Wi-Fi over USB | `.\configure-wifi.ps1 -Port COM8` |

Run the PowerShell scripts with `powershell -ExecutionPolicy Bypass -File`. Building never flashes the board. Keep `speaking_clock_c.build-id.txt` next to its UF2; the updater uses it to verify the installed build. The plain `update-pico.ps1 -Build -Bluetooth -Mp3` configures the ordinary profile without the browser page. USB command `version` prints the firmware version and build ID.

Host tests run on Windows and Linux and in GitHub Actions:

```powershell
cmake -S firmware/pico2w_c/tests -B build/host-tests
cmake --build build/host-tests --config Debug
ctest --test-dir build/host-tests -C Debug --output-on-failure
```

## Bluetooth quick start

1. Put the speaker in pairing mode and choose *Scan devices* under SETTINGS → Bluetooth (or the browser's Bluetooth page, or USB `bt-scan`).
2. Select the speaker and confirm *Connect*. The clock saves it once the audio stream is active; close the menu and wait for the automatic save before switching off.
3. After a restart the clock reconnects to the saved speaker directly. *Disconnect* or a new scan keeps the speaker off until you connect one again.

Classic A2DP speakers with SBC and SSP pairing are supported; BLE-only, HFP, legacy PIN pairing and Google Cast are not. Details: [controls](doc/CONTROLS_AND_MODES.md#bluetooth) and [browser Bluetooth](doc/WEB_BLUETOOTH.md).

## Repository layout

| Path | Purpose |
| --- | --- |
| [firmware/pico2w_c](firmware/pico2w_c/) | G1 firmware, host tests, OTA partition table |
| [experiments/bluetooth_a2dp_nest](experiments/bluetooth_a2dp_nest/) | A2DP source generator used by the G1 build, and the original A2DP experiment |
| [experiments/phone_control_ap](experiments/phone_control_ap/) | Phone-control prototypes and acceptance records |
| [sound/_sdcard](sound/_sdcard/) | Numbered MP3 assets for both SD cards |
| [tools](tools/) | Log capture and OTA packaging |
| [doc](doc/) | Current documentation; [generations](doc/generations/) and [history](doc/history/) |
| [generations/g0-micropython](generations/g0-micropython/) | Archived G0 MicroPython code and documents |

Documentation is written in English; see the [conventions](doc/DOCUMENTATION.md). Key documents: [controls and modes](doc/CONTROLS_AND_MODES.md), [network and time](doc/NETWORK_TIME.md), [firmware identity](doc/FIRMWARE_IDENTITY.md), [OTA web update](doc/OTA_WEB_UPDATE.md), [web control](doc/WEB_CONTROL_SPEC.md), [hardware test evidence](doc/HARDWARE_TEST_EVIDENCE.md), [changelog](CHANGELOG.md).

## Licenses

Project: [GPL-3.0](LICENSE). External Helix sources are not included; the wrapper and core retain their GPL/RPSL/RCSL terms. Firmware distribution must also account for the Pico SDK and BTstack licenses.
