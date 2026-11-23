# Roadmap

Plans for Pi2Clock after release [`g1-v1.1.0`](releases/g1-v1.1.0.md) (2026-11-23). What each feature does: [CONTROLS_AND_MODES.md](CONTROLS_AND_MODES.md) and [WEB_UI.md](WEB_UI.md); what is accepted and what remains to be checked: [FEATURE_STATUS.md](FEATURE_STATUS.md). The detailed stage-by-stage roadmap up to 2026-11-22 is archived in [history](history/ROADMAP_2026-11-22.md).

## Releases

| Release | Date | Content |
| --- | --- | --- |
| [v1.0.0](releases/v1.0.0.md) | 2026-11-09 | First stable C firmware: clock, speech, timer, alarms, birthdays, player, DFPlayer and Bluetooth audio, Wi-Fi/NTP, LCD light |
| [g1-v1.1.0](releases/g1-v1.1.0.md) | 2026-11-23 | Browser control (layout v2), A/B OTA updates, two home networks and Direct mode, fifteen birthdays, timer to 23:59:59 with completion options, random event music, Bluetooth music continuation, stable Bluetooth audio |

## G1: open checks and small items

These are not new features; they complete the acceptance of G1 and can be done at any time. The full list is in [FEATURE_STATUS.md](FEATURE_STATUS.md).

1. Copy the interim timer-warning cue `19/001.mp3` to both SD cards and check it on the clock.
2. Focused checks: a full 23:59:59 countdown, birthday timed firing and expiry, birthday slot 15 after restart, alarm tracks above 45, four browsers at once with music playing, Backup network failover, overnight operation and NTP outage recovery.
3. Draw the electrical schematic of the installed Pico 2 W wiring and power modules.
4. Offline RTC drift calibration only if a measured need appears.

## G1: technical work

1. Split `main.c` (about 6,200 lines: main loop, LCD screens and menus, USB commands, Bluetooth/Wi-Fi glue) into modules with host-testable screen rendering and a table-driven USB command dispatcher. Behaviour-neutral, needs on-device acceptance; plan it as a separate stage.
2. Minify the browser page at build time if Flash becomes short.

## Deferred, in approved order

1. The occasional double sound on Bluetooth: cause unknown; passive-capture findings are in [HARDWARE_TEST_EVIDENCE.md](HARDWARE_TEST_EVIDENCE.md).
2. Sound redesign: audible LOCAL beeps, next-alarm wording, German timer-completion and alarm-slot recordings (the German completion phrase last, once the recording is supplied).
3. Timed AUTO transitions of the LCD light and Wi-Fi router outage tests, deferred by the user.

The initial Bluetooth switch status `0x56` was resolved in OTA 19 (fast 250 ms retries instead of the 5 s backoff).

## Existing behavior retained

Separate DFPlayer/Bluetooth volume levels remain intentional. MAC addresses remain internal identifiers and USB diagnostics; the LCD displays names. SD access remains read-only. SSP confirmation remains automatic, and legacy PIN-only speakers are unsupported.

## Future device hardware

The second generation is described in [G2.md](generations/G2.md): MAX98357A I2S amplifier instead of DFPlayer, one shared SD card, music collections, three timers, a 3.1" OLED display, WS2812 LEDs and a microphone (INMP441-class), subject to Flash and RAM budgets.


Generation naming is installed as **Pi2Clock G1**, build `g1-accbeb708131-bt-mp3-wifi-phone-ota11-trial`; **Pi2Clock G2** is reserved for the successor. Model, Git-derived version and OTA sequence remain separate. G1 receivers validate the embedded target/prefix, while retaining the ota10 transition layout. Home installation, accepted B, settings preservation and restored Nest connection were verified on November 20. See [identity and release conventions](FIRMWARE_IDENTITY.md); the user confirmed the requested LCD/browser displays and normal playback on November 20.

On 2026-11-11, the user selected I2S audio through a MAX98357A amplifier as a logical direction for a likely new device with updated hardware. This is a future hardware milestone. Current web-control development continues on the assembled DFPlayer-based clock.

The proposed audio path is the Pico-connected SPI SD card, the existing software MP3 decoder, a PCM buffer, PIO/DMA I2S output and the MAX98357A speaker amplifier. A shared decode path could serve local audio and Bluetooth and consolidate audio assets onto one SD card. A separate hardware prototype should first verify available GPIO/PIO/DMA resources, amplifier power, speaker compatibility, memory use and sound continuity with Wi-Fi active. Exact wiring, resource allocation and performance remain to be measured.

### Generation 2: one-card audio and folder collections (2026-11-20)

The user explicitly deferred folder-based music collections to the second-generation device. Generation 2 is planned to replace DFPlayer with I2S/MAX98357A local output and use one shared SD card for local and Bluetooth audio, eliminating the current need to maintain two matching cards. This is a future implementation requirement, not a change to the assembled clock.

- Organize music into named folders/collections, for example Disco, Classical and Russian music. Allow selection and playback of one collection independently.
- Provide an All music selection that combines the music collections and supports shuffled playback across their tracks. Exclude speech assets, beeps and other system audio from this selection.
- Keep collection selection separate from playback order (sequential, shuffle and repeat-one); preserve useful Previous/Next history. Prefer a shuffled pass without repeats until the selected catalog is exhausted.
- Use the same catalog for local I2S output and Bluetooth. Numeric folder restrictions imposed by the current DFPlayer must not dictate the generation-2 folder layout.
- Define supported filenames/encodings, catalog limits, missing-file behavior, persistence and resource budgets during generation-2 design. Selection of arbitrary subsets of collections and editable playlists remain optional follow-up ideas, not committed scope.

Do not implement folder collections or migrate the current two-card audio layout as part of the present web-control/OTA work.
