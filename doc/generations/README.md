# Pi2Clock hardware and firmware generations

Pi2Clock is a speaking clock built around a Raspberry Pi Pico board, an LCD1602, a DS1302 real-time clock, two rotary encoders and five push buttons. The project has evolved in generations. A generation is a combination of hardware and firmware architecture; it is independent of the firmware version and of the OTA sequence number (see [firmware identity](../FIRMWARE_IDENTITY.md)).

| | G0 — original | G1 — current | G2 — planned |
| --- | --- | --- | --- |
| Status | Archived, read-only | **The assembled clock**, release `g1-v1.1.0` | Planned; hardware, SD, speech and UI documents in [g2/](g2/), no code yet |
| Board | Raspberry Pi Pico (RP2040); the v3 line later ran on Pico 2 W | Raspberry Pi Pico 2 W (RP2350 + CYW43439) | Pico 2 W expected; to be confirmed by a prototype |
| Firmware | MicroPython, versions 1.16 → 2.x → 3.10.0 | C / Pico SDK 2.3.1, releases v1.0.0 and `g1-v1.1.0`, `g1-` build IDs | C / Pico SDK, `g2-` build IDs on a future `codex/gen2` branch |
| Local sound | DFPlayer Mini with its own microSD card | DFPlayer Mini with its own microSD card | **MAX98357A I2S amplifier**, fed by the Pico's software MP3 decoder; DFPlayer removed |
| Bluetooth audio | None (only an off-device A2DP experiment) | Classic A2DP source: MP3 from a second, SPI-connected microSD card, Helix decoder, SBC encoder | Same decoder path as local sound |
| SD cards | 1 (DFPlayer) | 2 with identical numbered folders: DFPlayer card and Pico SPI card | 1 shared card |
| Network | v3: Wi-Fi/NTP on Pico 2 W | Wi-Fi home network or Direct access point, NTP, browser control, A/B OTA updates | Same as G1 |
| Code | [generations/g0-micropython](../../generations/g0-micropython/) | [firmware/pico2w_c](../../firmware/pico2w_c/) | Not started |
| Details | [G0](G0.md) | [G1](G1.md) | [G2](G2.md) |

## Common elements

All generations share the user-facing concept and most panel hardware:

- LCD1602 character display through a PCF8574 I2C expander (GP0 SDA, GP1 SCL).
- DS1302 real-time clock (GP2 CLK, GP5 DIO, GP4 CE).
- Volume encoder with push button (sound on/off) and timer encoder with push button (start/cancel).
- Five buttons: Alarm, Mode, Minus, Settings/Plus and Timer-mode.
- Russian and German speech assembled from numbered MP3 recordings (hours, minutes, dates, phrases), hourly announcements or chimes, quiet hours, a countdown timer, five alarms and a music player using folder 08.

## Identity rules

- Firmware version comes from Git tags: `g1-vX.Y.Z` for G1 (first: `g1-v1.1.0`), falling back to the legacy `v1.0.0` tag for older commits.
- Build IDs start with the generation prefix (`g1-…`, later `g2-…`).
- OTA packages carry a generation-specific target: G1 `0x23500002`, G2 reserved `0x23500202`. A G1 receiver refuses G2 packages before erasing Flash, and the reverse will hold for G2.
- OTA sequence numbers increase monotonically within one generation and are never reset by a release.

## Repository layout by generation

| Path | Generation | Purpose |
| --- | --- | --- |
| `generations/g0-micropython/` | G0 | Archived MicroPython sources, libraries, original schematic, G0 documents and tools |
| `firmware/pico2w_c/` | G1 | Current C firmware, host tests, OTA layout |
| `experiments/` | G1 | A2DP source generator (used by the G1 build) and the phone-control prototypes |
| `sound/_sdcard/` | G0, G1 | Numbered audio assets for the DFPlayer card and the Pico SPI card |
| `tools/`, `*.ps1` | G1 | Build, update, Wi-Fi provisioning, logging and OTA packaging |
| `doc/` | G1 (current) | Current documentation; `doc/history/` holds the G0 → G1 migration and development logs |
