# Documentation index

Documentation for Pi2Clock, written in English ([conventions](DOCUMENTATION.md)). Current release: [g1-v1.1.0](releases/g1-v1.1.0.md).

## Using the clock

| Document | Content |
| --- | --- |
| [CONTROLS_AND_MODES.md](CONTROLS_AND_MODES.md) | Buttons, encoders, LCD, settings menu, timer, alarms, birthdays, player, audio outputs, Bluetooth, USB commands |
| [WEB_UI.md](WEB_UI.md) | Browser page: opening it, layout, settings pages, polling, languages and themes |
| [NETWORK_TIME.md](NETWORK_TIME.md) | Wi-Fi provisioning, NTP and Europe/Berlin time, Home and Direct modes, settings compatibility and rollback |
| [OTA_WEB_UPDATE.md](OTA_WEB_UPDATE.md) | Updating the firmware from the browser |
| [FEATURE_STATUS.md](FEATURE_STATUS.md) | What is accepted on the clock, what remains to be checked, known limitations |

## Hardware and firmware

| Document | Content |
| --- | --- |
| [generations/](generations/README.md) | G0, G1 and G2: hardware, firmware, resources |
| [generations/g2/](generations/G2.md) | G2 plan: [hardware](generations/g2/HARDWARE.md), [SD layout](generations/g2/SD_LAYOUT.md), [speech](generations/g2/VOICE.md), [UI concept](generations/g2/UI_CONCEPT.md), [microphone](generations/g2/MICROPHONE.md) |
| [HARDWARE_PICO2W.md](HARDWARE_PICO2W.md) | Pin map |
| [FIRMWARE_IDENTITY.md](FIRMWARE_IDENTITY.md) | Generation, version tags, build IDs, OTA sequence and package identity |
| [../firmware/pico2w_c/README.md](../firmware/pico2w_c/README.md) | Source layout, build options, storage |
| [TESTING.md](TESTING.md) | Host tests, builds, version checks, acceptance after installing a release |
| [ROADMAP.md](ROADMAP.md) | Open checks, technical work, deferred items, G2 |
| [releases/](releases/) | Release notes |

## Feature notes

Design, implementation and installation history of individual features; current behaviour is in the documents above.

- Browser: [WEB_ANNOUNCEMENTS.md](WEB_ANNOUNCEMENTS.md), [WEB_BLUETOOTH.md](WEB_BLUETOOTH.md), [WEB_BROWSER_ACCESS.md](WEB_BROWSER_ACCESS.md), [WEB_CLOCK.md](WEB_CLOCK.md), [WEB_NETWORK_MODES.md](WEB_NETWORK_MODES.md), [WEB_PLAYER_OPTIONS.md](WEB_PLAYER_OPTIONS.md), [WEB_RECONNECT.md](WEB_RECONNECT.md), [WEB_SCALAR_SETTINGS.md](WEB_SCALAR_SETTINGS.md), [WEB_WIFI_SETUP.md](WEB_WIFI_SETUP.md)
- Timer and music: [TIMER_PREWARNING.md](TIMER_PREWARNING.md), [RANDOM_EVENT_MUSIC.md](RANDOM_EVENT_MUSIC.md), [BT_MUSIC_INTERRUPTION.md](BT_MUSIC_INTERRUPTION.md)
- Bluetooth audio: [BT_AUDIO_CHAIN.md](BT_AUDIO_CHAIN.md)
- Updates: [OTA_FEASIBILITY.md](OTA_FEASIBILITY.md), [OTA_FOUNDATION.md](OTA_FOUNDATION.md)
- Specifications: [WEB_CONTROL_SPEC.md](WEB_CONTROL_SPEC.md), [WEB_UI_REDESIGN_SPEC.md](WEB_UI_REDESIGN_SPEC.md)
- Phone-control development record: [experiments/phone_control_ap](../experiments/phone_control_ap/README.md)

## Evidence and history

- [HARDWARE_TEST_EVIDENCE.md](HARDWARE_TEST_EVIDENCE.md): recorded device tests with builds, logs and dates.
- [history/](history/README.md): G0 → G1 migration, development logs, and the README, roadmap and testing notes as they stood before `g1-v1.1.0`.
- [../CHANGELOG.md](../CHANGELOG.md): change log.
