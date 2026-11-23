# Pi2Clock G1 firmware (C, Pico SDK)

Firmware of the current clock generation, [G1](../../doc/generations/G1.md): Raspberry Pi Pico 2 W, DFPlayer Mini for local sound and a second SPI microSD card for Bluetooth audio.

- Behaviour and USB commands: [controls and modes](../../doc/CONTROLS_AND_MODES.md)
- Browser page: [phone interface](../../doc/WEB_UI.md)
- Network, NTP and rollback: [network and time](../../doc/NETWORK_TIME.md)
- Browser updates: [OTA web update](../../doc/OTA_WEB_UPDATE.md)
- Status per feature: [feature status](../../doc/FEATURE_STATUS.md)
- Wiring: [Pico 2 W pin map](../../doc/HARDWARE_PICO2W.md)
- Building and installing: [main README](../../README.md#building-and-installing-windows)
- Host tests: [testing](../../doc/TESTING.md)

## Source layout

| Path | Content |
| --- | --- |
| `main.c` | Main loop, LCD screens and menus, USB commands, glue between audio, Bluetooth and Wi-Fi |
| `app/` | Pure application logic, host-tested: countdown and timer editor, timer warning, alarm engine (weekdays, snooze), birthdays, music playlist/sleep/catalog/retry, civil time and DST |
| `audio/` | DFPlayer command queue, speech planner, output router, PCM ring buffer (16,384 frames), Helix MP3 decoding with resampling |
| `drivers/` | LCD1602 over PCF8574, DS1302, DFPlayer UART, encoders and buttons, SD over SPI, read-only FAT32 |
| `services/` | Flash settings (v18), Bluetooth device catalog, Wi-Fi/NTP, phone web server and access control, Wi-Fi profiles and scan, OTA image/boot/upload, `phone_web/index.html` |
| `ota/partitions.json` | A/B partition table |
| `tests/` | Host tests (C and Node.js), registered with CTest |

The A2DP source is generated at configure time from the Pico SDK's BTstack `a2dp_source_demo.c` by [experiments/bluetooth_a2dp_nest](../../experiments/bluetooth_a2dp_nest/) (`patch_a2dp_source.cmake`); the generated file is `clock_a2dp_source_generated.c` in the build directory. All clock-specific changes to the demo (policy, pacing, packet size, bitpool, send-result handling, AVRCP) live in that patch script.

## Build options

| Option | `build-clock-bt.ps1` | CMake default | Effect |
| --- | --- | --- | --- |
| `CLOCK_ENABLE_A2DP` | always ON | OFF | Bluetooth A2DP source |
| `CLOCK_ENABLE_WIFI` | ON, OFF with `-NoWifi` | OFF | Wi-Fi, NTP |
| `CLOCK_ENABLE_MP3` | `-Mp3` | OFF | SPI card, Helix decoder, music over Bluetooth |
| `CLOCK_ENABLE_PHONE_WEB` | `-PhoneWeb` (needs Wi-Fi) | OFF | Browser page, Phone Control menu, 48 KiB lwIP heap |
| `CLOCK_ENABLE_OTA_AB`, `CLOCK_OTA_SEQUENCE`, `CLOCK_OTA_TRIAL` | `-OtaAb -OtaSequence N -OtaTrial` | OFF | A/B image for browser updates |
| `CLOCK_WEB_GZIP` | — | ON | Page stored gzip-compressed |
| `CLOCK_SIZE_OPTIMIZE_APP` | — | ON | `-Os` for `main.c`, `app/`, `services/` (except `phone_web.c`); audio, SD, drivers, A2DP stay `-O3` |
| `CLOCK_A2DP_MAX_BITPOOL` | — | 53 | Highest SBC bitpool offered to speakers |

The installed clock uses `-Mp3 -PhoneWeb -OtaAb`. The clock's own sources build with `-Wall -Wextra` without warnings.

## Storage

Clock settings use two A/B Flash sectors (−6 and −5 from the end of Flash) holding CRC-protected records; the current format is v18 and every earlier format (v1–v17) is read. Loading never writes; saving is deferred until the clock is idle. Sector −4 is the legacy slot (read-only), −3 and −2 belong to BTstack pairing keys, the last sector is reserved. Format history and rollback limits: [network and time](../../doc/NETWORK_TIME.md#settings-compatibility-and-rollback). The SPI card is only read.

## After installing a build

1. USB `version`: check version, build ID and OTA sequence.
2. `flash-info`, `alarm-status`, `audio-settings`, `bt-known`: settings and speakers unchanged.
3. LCD, both encoders and the buttons; LOCAL speech and the timer.
4. Bluetooth: the saved speaker reconnects; music, speech, timer and alarm on Bluetooth; `bt-status`.
5. Browser: page loads in the current network mode, status updates.

The development notes that accumulated here until 2026-11-23 are archived in [history](../../doc/history/FIRMWARE_README_2026-11.md).
