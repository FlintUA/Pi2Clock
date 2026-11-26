# Testing

How the G1 firmware is tested: host tests, firmware builds, version checks and the acceptance steps for a release. What has been accepted on the clock is listed in [FEATURE_STATUS.md](FEATURE_STATUS.md); recorded device evidence is in [HARDWARE_TEST_EVIDENCE.md](HARDWARE_TEST_EVIDENCE.md). The stage-by-stage verification notes up to 2026-11-22 are archived in [history](history/TESTING_2026-11-22.md).

## Host tests

No Pico SDK is needed. With a C11 compiler and CMake; Node.js and Python 3 are optional:

```sh
cmake -S firmware/pico2w_c/tests -B build/host-tests -DCMAKE_BUILD_TYPE=Debug
cmake --build build/host-tests --config Debug
ctest --test-dir build/host-tests -C Debug --output-on-failure
```

GitHub Actions runs the suite on Windows and Linux for pushes to `main` and `codex/**`, pull requests and manual dispatch. If an incremental MSVC build misses a changed header, rebuild with `--clean-first`.

At release `g1-v1.1.0` the suite registers **37 checks**; all pass with Linux GCC and in CI. Four checks need Node.js and three need Python 3; they are registered only when the interpreter is found at configuration.

| Area | Checks | Coverage |
| --- | --- | --- |
| Time | `clock_time`, `network_time` | Calendar, leap days, Europe/Berlin transitions, NTP era and reply validation; asynchronous join, idle deferral of RTC writes, retries (mocked radio) |
| Timer | `timer_controls`, `timer_warning` | Precise editor, 23:59:59 limit, accelerated minutes, monotonic completion; warning edges 5…1, skips without catch-up |
| Alarms and birthdays | `alarm_engine`, `birthday` | Weekday masks, ties, snooze deadlines and cancellation, next alarm; annual claims, handled year, leap days, expiry |
| Audio | `audio_queue`, `speech_plan`, `music_playlist`, `music_sleep`, `music_retry`, `music_catalog`, `sd_catalog`, `mp3_interrupt` | DFPlayer queue with pause/resume, RU/DE speech plans, playlist modes and history, sleep timer, undecodable-track retry, folder-08 catalog, Bluetooth music suspend/restore |
| Bluetooth | `bt_catalog`, `bt_policy` | Device list and names, connection policy, OFF persistence, stale callbacks |
| Settings | `settings_store`, `settings_store_ota` | v1–v18 decoding and round trips, migrations, CRC fallback, A/B sectors with OTA layout |
| Display | `lcd_cursor` | Cursor commands through a mocked PCF8574 |
| Web server | `phone_access`, `phone_control`, `phone_overview`, `phone_bluetooth`, `phone_network`, `phone_wifi`, `wifi_scan`, `web_fsdata` | Pairing, keys, home trust, command envelope and retries, admission guards, status JSON bounds, Bluetooth/network/Wi-Fi commands, scan catalogue, gzip page data (Python) |
| Page script (Node.js) | `phone_sliders`, `phone_timer_wheels`, `phone_ota`, `phone_ui_text` | Production control layer with a DOM model: slider coalescing, alarm audition, timer wheels, OTA flow, translation completeness and safe insertion of remote names |
| OTA | `ota_layout`, `ota_boot`, `ota_upload`, `ota_package`, `ota_web_package` | Partition layout, trial boot, upload and header checks before erase, package format and naming (Python) |
| Identity | `git_version` | Version from `g1-v*` and legacy `v*` tags, distance, dirty marker, source archives |

Host tests do not prove radio, audio or LCD behaviour on hardware.

## Firmware builds

```powershell
# Web profile with A/B OTA (the installed clock)
powershell -ExecutionPolicy Bypass -File .\build-clock-bt.ps1 -Mp3 -PhoneWeb -OtaAb -OtaSequence N -OtaTrial -BuildDirectory C:\pico_clock_compile\otaN
# Web profile for USB installation
powershell -ExecutionPolicy Bypass -File .\build-clock-bt.ps1 -Mp3 -PhoneWeb -BuildDirectory C:\pico_clock_compile\phone-clock
# Ordinary profile, Bluetooth-only fallback
powershell -ExecutionPolicy Bypass -File .\build-clock-bt.ps1 -Mp3
powershell -ExecutionPolicy Bypass -File .\build-clock-bt.ps1 -Mp3 -NoWifi
```

Use short ASCII build paths. The script records the Git revision and marks tracked uncommitted changes as dirty; release builds must come from a clean checkout of the release tag. Keep each UF2 with its `speaking_clock_c.build-id.txt`. OTA packages: `python tools\ota_web_package.py --build <dir>` ([details](OTA_WEB_UPDATE.md)). Building never installs anything; installation needs a separate decision.

## Firmware version

The version is generated from the nearest reachable Git tag `g1-vX.Y.Z` (falling back to the legacy `vX.Y.Z` tags) at configuration and before each build:

- Clean checkout at `g1-v1.1.0`: USB `version` reports `1.1.0`, About shows `v1.1.0`.
- Commits after the tag: `1.1.0+N.gHASH`; About shows `v1.1.0+`.
- Tracked local edits: `.dirty` in USB metadata, `+` on About.
- No reachable tag: `0.0.0+gHASH`; no Git metadata (source archive): `0.0.0+unknown`.

Run `git fetch --tags` before building; a shallow checkout must include the tag.

## Acceptance after installing a release

1. USB `version`: version, build ID and OTA sequence as expected; About on the LCD.
2. Settings unchanged: `flash-info`, `alarm-status`, `audio-settings`, `bt-known`, `birthday-status`, `timer-sound`; Wi-Fi profiles and browser permissions in the page.
3. LCD, both encoders and all buttons; spoken time (MODE hold), date and next alarm (MINUS).
4. Timer start, warning (if enabled), completion; an alarm with snooze and stop.
5. Music player on LOCAL and Bluetooth: play, pause, next/previous, sleep; Bluetooth reconnects after a restart.
6. Browser page in the current network mode: status, timer, player, a setting change confirmed by "Settings saved".
7. Hourly speech during Bluetooth music resumes the track.
8. Manual speech during music (Speak sheet or MODE hold): Bluetooth music continues in place, built-in speaker music restarts the track; during a countdown MINUS short and the Speak sheet say the time left.

For Bluetooth audio problems, capture the USB log (`tools/capture-pico-log.ps1`) and check `[BT-DIAG]` and `bt-status` ([BT_AUDIO_CHAIN.md](BT_AUDIO_CHAIN.md)).
