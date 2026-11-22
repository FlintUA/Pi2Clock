# G1 phone interface (layout v2)

This document describes the phone interface that implements the [redesign specification](WEB_UI_REDESIGN_SPEC.md). The user approved the visual direction (prototype v2) on 2026-11-20 and asked for implementation. The page was developed on branch `codex/phone-ui-v2` and merged into `main` on 2026-11-22. On 2026-11-21 the user installed it through the browser as OTA sequence 17, build `g1-d31a02ca0f75-bt-mp3-wifi-phone-ota17-trial` (package `Pi2Clock-G1-v1.0.0+82.gd31a02c-ota17.clockota`, 917,316 bytes, Windows SDK toolchain), and reported that it generally works. Detailed acceptance and refinements follow. First refinements after user review (2026-11-21): a light clock panel with dark digits in the light theme (a dark sea-green panel was tried first and rejected), the ringing-alarm banner and its status dot in the accent brown-orange instead of red, track number kept on one line with the sleep countdown below it, equal-width speaker buttons, and command feedback moved from pop-ups to a status line under the footer. Later the same day: shorter "Auto" appearance label in Russian and German, speaker rows in Settings wrap the buttons below the name, the speaker name was removed from the clock panel (the footer shows it), messages built at page load (for example "Stop and close the music player first.") now follow the selected language, and the update page handles a connected speaker (see below).

## Layout

The page is one vertical column at every width; on a tablet the same column is centred (maximum 560 CSS px). There are no side menus.

| Area | Content |
| --- | --- |
| Top bar | Pi2Clock G1, connection type (house icon with "Home", or the Direct icon with "Direct") and a status lamp: green live, blinking while a command or network switch is pending, red when the connection is lost |
| Urgent banner | Shown on every view above the content: ringing alarm (Stop, Snooze 3 min), snoozed alarm (Cancel snoozed repeats), finished timer (Stop timer sound) |
| Clock window | Light panel with dark digits in the light theme, amber digits on near-black in the dark theme; clock time with seconds at half size, weekday and date, next alarm, sound state and Bluetooth speaker. Information only |
| Block 1: Timer and alarms | Switch between Timer and Alarms. Timer: remaining or set time, Start/Cancel, Change opens quick durations (1, 3, 5, 10, 15, 30 min) and the three wheels with Set; completion options collapsed below with a summary. Alarms: five rows with on/off switches; a row opens the alarm editor |
| Block 2: Music | Track number and count, state, effective output, Previous / Play-Pause / Next, Stop, volume of the output that is currently playing, collapsed order and sleep timer |
| Footer (fixed) | Sound on/off, Speaker (sheet with saved speakers and Connect/Disconnect), Speak (sheet with time, date, next alarm), Settings. Below it a one-line status line shows command feedback (highlighted for 5 s; tap to show a long message in full) instead of pop-up messages |
| Settings | Groups with sub-pages and Back: Sound and display (volume and outputs, announcements and quiet hours, display light), Calendar (birthdays, date and time), Connections (Bluetooth speakers, Wi-Fi and Direct, browser access), System (firmware update, About and status), This browser (appearance, page language) |

Views use hash routes (`#/`, `#/alarm/N`, `#/birthday/N`, `#/settings/<page>`), so browser Back returns to the previous view without reloading or submitting anything. Scroll position is kept per view. Birthdays moved from the main page to Settings → Calendar because they are edited rarely. Detailed diagnostics (the former status list) are under Settings → About and status.

## Structure of the page

`services/phone_web/index.html` remains one self-contained file with three scripts:

1. `theme` (in the head) applies the stored theme before the first paint.
2. The **control layer** (the first plain `<script>`) is the previous page logic: transport, polling, command IDs and nonces, guards, drafts, revision conflicts, slider coalescing, Bluetooth/Wi-Fi/browser-access/OTA flows and the native-picker repaint hold. Its behavior is unchanged. Two mechanical changes were made: user-visible strings are wrapped in `T(...)` with the English text as key, and `updateControls()` now calls the former body (`renderControls()`) and then the optional presentation hook.
3. The **presentation layer** (`<script id="ui">`) arranges views, renders the clock window, banner, lists and footer from the same `live` snapshot, and forwards taps to the existing controls (for example the footer Sound button clicks the existing `sound-toggle`). It sends no request of its own except through the control layer's `sendCommand`, adds no polling and inserts remote names only with `textContent`.

Specific bridges:

- The timer completion fields stay in the `settings-controls` form markup (so `settingFields` and the tests see them); at start-up the presentation layer moves them into the timer block and forwards their `input`/`change` events to `settingEdited`.
- The music volume slider is a proxy for `volume_bt` or `volume_local`, chosen by the reported `output`; it writes the real field and dispatches the same events, including the active-slider hold.
- Speaker rows select the device in the existing (hidden) `bluetooth-device` select and press the existing Connect/Forget/Disconnect buttons; their enabled state follows the same guards.
- The quick on/off switch of an alarm sends the same full-record `alarm set` command as Save, with the record's current revision, and is disabled while the clock is not idle or while that alarm has an unsaved draft.

## Firmware update with a connected speaker

The clock accepts an upload only when no Bluetooth A2DP link exists (`ota_idle` in `main.c`). Before this, a connected speaker silently kept Upload disabled and the page still said "File selected. Press Upload update." The update page now lists what blocks the update (player, timer, ringing alarm, clock menu, unsaved settings, network switch). When a speaker is connected it offers **Disconnect the speaker and upload**: the page sends the ordinary Bluetooth disconnect, waits until the clock reports the update available (disconnecting saves settings, which can take several seconds), and then starts the normal upload. It remembers the speaker in the browser (`pi2clock.otaSpeaker`) and connects it again with the ordinary Connect command after the clock restarts, or immediately if the upload is cancelled, fails or does not start within 150 s. Install still requires its own tap. No firmware or endpoint changed.

## Languages and themes

Interface language (English, Russian, German) and appearance (Light, Dark, Automatic) are stored only in the browser (`localStorage` keys `pi2clock.lang` and `pi2clock.theme`); without storage the page uses the browser language and system theme. They do not change the clock's speech language, which stays under Volume and outputs.

Translations are a table of `[English, Russian, German]` entries (`UI_TEXT`). Markup text marked `data-t` and labels marked `data-ta` are translated in place; dynamic messages use `T("text {placeholder}", values)`. Because English is the key, English output is identical to the control layer's strings, which the existing tests assert. Machine values, command names, SSIDs and speaker names are never translated.

## Control and API map

All commands keep their existing endpoint, body format (`credential epoch id nonce action value`) and backend guard.

| Control in the new layout | Request or status field | Guard reproduced in the page |
| --- | --- | --- |
| Clock window | `time`, `overview.date/weekday/rtc_valid`, `overview.alarm`, `overview.sound_on`, `output` + volume, `overview.bluetooth` | None (display only) |
| Connection pill | `overview.network.mode`, network handoff state, `busy`/`pending`, poll success | None |
| Urgent banner | `POST /control alarm_stop|alarm_snooze <active_id>`, `snooze_cancel <snooze_revision>`; `POST /timer stop_sound <timer_sound_id>` | Existing ownership IDs and disabled states |
| Timer Start / Cancel / Set, presets, wheels | `POST /timer start|cancel|set <seconds>` | Running timer, open player, pending scalar settings |
| Timer completion options | `POST /settings timer_voice|timer_sound|timer_random|timer_track|timer_warning` | Clock idle, physical editor closed |
| Alarm list switches, alarm editor | `POST /alarm set <slot revision enabled hour minute days sound track>`; `POST /player test_track|test_stop` | Idle, revision conflict, dirty-draft slot lock |
| Music block | `POST /player play|pause|resume|previous|next|stop|mode|sleep` | Existing player guards and interruption state |
| Music volume, Volume and outputs | `POST /settings volume_bt|volume_local|audio_*|language` | Existing coalescing and idle rules |
| Footer Sound, Speak sheet | `POST /control sound|say_time|say_date|next_alarm` | `controlReason` |
| Speaker sheet, Bluetooth speakers | `POST /bluetooth connect|disconnect|scan|cancel|forget`; `GET /bluetooth.json` | Availability, scanning, registry limit, pending settings |
| Announcements, quiet hours, display light | `POST /settings auto_enabled|clock_mode|half_hour|exact_hour|quiet_*|light_*` | Existing scalar rules |
| Birthdays | `POST /birthday set <...>` | Idle, revision conflict |
| Date and time | `POST /clock set|sync` | Existing clock guards |
| Wi-Fi and Direct | `POST /network`, `POST /wifi`; `GET /network.json`, `/wifi.json`, `/wifi-scan.json` | Existing handoff and Direct-only editing rules |
| Browser access | `POST /browsers forget`, `POST /logout`; `GET /browsers.json` | Native picker hold, revision |
| Pairing card | `POST /pair`, `POST /access` | Unchanged |
| Firmware update | `GET /ota.json`, `POST /ota` | G1 header checks, sequence, session ownership |

Response schemas, polling intervals, request bodies, server limits and Flash settings are unchanged.

## Size

| Item | Before (main `fc03d52`) | Layout v2 |
| --- | --- | --- |
| Page source (`index.html`) | 124,934 bytes | 271,613 bytes |
| Stored in Flash and sent per load (gzip) | 31,609 bytes | 71,858 bytes |
| Web-profile image (VM build, GCC 13.2) | 832,664 bytes | 872,920 bytes (+40,256) |
| OTA-profile image, sequence 17 (VM build) | — | 881,272 bytes of the 1,572,864-byte slot |
| Static RAM (`.bss`), web profile | 165,944 bytes | 165,944 bytes (unchanged) |

The uncompressed page exceeds the specification's proposed 160 KiB target. About 95 KB of it is the translation table and about 25 KB the presentation layer; the control layer is unchanged in size apart from the `T(...)` wrappers. The firmware never stores or sends the uncompressed page: it is kept gzip-compressed in Flash (`CLOCK_WEB_GZIP`) and decompressed by the browser, so the costs on the clock are +40,249 bytes of Flash and a 71.9 KB transfer per page load. No RAM, heap, TCP or response-buffer setting changed. On 2026-11-21 the user approved this size; minification at build time is the agreed first step if Flash becomes short, for example for G2 features.

The VM figures use Ubuntu's GCC 13.2 with `__int64_t_defined` predefined, because that newlib does not define `PRIx64` otherwise; the Windows build (`build-clock-bt.ps1`) uses the SDK toolchain, so its absolute sizes differ. Compare the before/after columns, not these numbers with earlier Windows measurements.

## Verification

- The host suite registers 37 checks; all pass. `phone_sliders`, `phone_timer_wheels` and `phone_ota` run the production control layer against the new markup. Two test adjustments were needed: `phone_ota` now provides `T` to its script slice, and `phone_sliders` checks that both record editors keep an explicit Save action instead of the former button labels. The new `phone_ui_text` check fails if any visible string lacks a Russian or German translation, if placeholders differ, or if remote text could be inserted as HTML.
- With the local API stand-in [`tools/phone_web_mock.py`](../tools/phone_web_mock.py) in Chrome at 320, 360, 393 and 820 px, light and dark, English, Russian and German: no script errors and no horizontal overflow. Interactions checked: preset and Start/Cancel of the timer, quick alarm switch, Play, volume proxy, ringing alarm Snooze and Cancel, timer completion stop, footer Sound, speaker Disconnect/Connect, language switch, custom-day alarm Save and connection loss. The stand-in models the API only; this is not device evidence.

## Pending

- Hardware acceptance: page load in Home and Direct, every block on the phone, physical encoder changes while the page is open, Bluetooth music continuity, four clients, OTA upload from the new page and recovery instructions after OTA.
