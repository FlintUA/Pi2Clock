# G1 feature status

Status of every G1 feature at release `g1-v1.1.0` (2026-11-23), in one place. The feature descriptions are in [CONTROLS_AND_MODES.md](CONTROLS_AND_MODES.md) (clock, USB) and [WEB_UI.md](WEB_UI.md) (browser); detailed evidence is in [HARDWARE_TEST_EVIDENCE.md](HARDWARE_TEST_EVIDENCE.md), [TESTING.md](TESTING.md) and the linked feature notes.

**Status values**

- **Accepted** — the user explicitly confirmed the feature on the assembled clock (date or build given).
- **In use** — installed and in daily use since the given build without a reported problem, but not separately tested.
- **Open checks** — specific cases that were never exercised; they are not known defects.

The clock runs the web profile with A/B OTA; OTA 17–28 were installed by the user through the browser between 2026-11-21 and 2026-11-22.

## Clock, speech and announcements

| Feature | Status | Open checks |
| --- | --- | --- |
| Clock screen, RTC, start-up splash, editing cursor, `MUTE`/`BT`/`SPK` indicators | Accepted (cursor build 755f55b; indicators 2026-11-15) | — |
| Wi-Fi/NTP time, Europe/Berlin DST, offline RTC operation | Accepted (initial sync build 7964939; periodic refresh 7378aa1) | Overnight run, NTP server outage and recovery; Wi-Fi router outage is deferred by the user |
| Hourly VOICE/CHIME, half-hour beep, exact-hour word, quiet hours, automatic on/off (clock and browser) | Accepted, general (2026-11-14) | Individual hour boundaries, restart persistence; the LOCAL short beep is quiet (sound redesign deferred) |
| Spoken date and next alarm (MINUS) | Accepted (build 02b4a51) | Language/output combinations |
| Date/time setting from the browser | In use (since `1.0.0+33`) | Functional acceptance not recorded |
| Hourly speech interrupting Bluetooth music and resuming it | Accepted (sequence 12–14) | Alarm interruption with resume; bad-file policy |
| Manual speech (time, date, next alarm) during music and a running timer; time left on the timer | Candidate, OTA 31 (not installed) | BT music resumes in place; LOCAL track restarts; RU/DE time-left wording; timer finish during a phrase |

## Timer, alarms, birthdays

| Feature | Status | Open checks |
| --- | --- | --- |
| Countdown 1 s – 23:59:59, quick encoder, precise editor, browser presets and wheels | Accepted, general (2026-11-13; layout v2 2026-11-21) | A full-length 23:59:59 run |
| Timer completion: message, signal/music/none, Stop timer sound | Stop timer sound accepted; choices in use (since `1.0.0+27`) | Each combination per output; German completion message missing (recording) |
| Random timer and alarm music | Accepted, general (`1.0.0+28`) | Per-slot and per-output cases |
| Five-second timer warning | In use (since `1.0.0+29`) | Cadence on the clock; the new 4.1 kHz cue `19/001.mp3` must be copied to both cards |
| Five alarms, weekday schedules, three-minute snooze, cancel snoozes | Accepted (snooze and weekdays; browser repeat/cancel 2026-11-13) | Tracks above 45 on both cards; collisions with a running timer |
| Browser alarm actions: Stop, Snooze, Cancel snoozed repeats | Accepted, general (2026-11-13) | Stale-page cases |
| Fifteen birthdays with optional birth year | Accepted for editing and saving (2026-11-13) | Timed firing, 30-minute expiry, slot 15 save/restart |

## Music and audio

| Feature | Status | Open checks |
| --- | --- | --- |
| Music player: NORM/SHUF/REP1, history, pause with position, sleep timer (clock and browser) | Accepted (2026-11-14) | Full sleep expiry on each output |
| Two outputs, four output preferences, LOCAL fallback, separate volumes, one volume encoder | Accepted | — |
| Bluetooth speakers: scan, connect, up to four saved, direct reconnect, persistent Disconnect | Accepted (build 7378aa1; browser management `1.0.0+36`) | Scan cancel/timeout, speaker-initiated reconnect, a forgotten speaker after power loss |
| Bluetooth audio quality (OTA 25–28: packet fixes, Wi-Fi power saving off while streaming, automatic bitpool, 300 ms stall recovery) | Accepted 2026-11-22/23: Portable 25 min clean, PRO X 2 and Nest clean, SSTB 10 one crackle in 15 min | Stall recovery under real radio disturbance not yet observed |
| Speaker Play/Pause buttons control the player | Accepted (2026-11-22) | — |
| AVRCP volume with PCM fallback when a speaker refuses it | In use (OTA 25) | A speaker that refuses Absolute Volume |

## Display and settings

| Feature | Status | Open checks |
| --- | --- | --- |
| LCD light OFF/ON/AUTO, day/night levels (clock and browser) | Accepted (build ab06727) | AUTO transitions at 22:00/07:00 (deferred by the user) |
| Settings in Flash (v18), autosave, migrations from v1 | Accepted (v11 migration; all settings preserved across OTA 9–28) | — |

## Network, browser and updates

| Feature | Status | Open checks |
| --- | --- | --- |
| Phone page layout v2 (EN/RU/DE, light/dark/auto) | In use (since OTA 17, 2026-11-21) | Four simultaneous clients with audio |
| Home and Direct modes and switching | Accepted (2026-11-15) | Explicit and busy cancellation of a switch |
| Two home networks, search, test and save, manual Connect | Accepted (`1.0.0+43`–`+46`) | Automatic failover between the two networks |
| Browser pairing, home trust, permission list and Forget | Accepted in part (home without re-pairing, Direct reconnect, picker stability) | Sign out, second-browser removal, power-cycle persistence |
| A/B OTA from the browser, trial boot, rollback, network return after update | Accepted (rollback 2026-11-16; Direct return sequence 10; used for OTA 11–28) | Recovery instructions after a failed trial |
| Guided update with a connected speaker (disconnect, upload, reconnect) | In use (since OTA 20) | — |
| Compressed page and `-Os` build | In use (since 2026-11-20) | — |

## Known limitations

- German timer-completion and alarm-slot recordings are missing; years are spoken only for 2023–2029.
- Occasional double sound on Bluetooth: cause unknown, investigation deferred.
- The LOCAL half-hour and warning beeps are quiet on the DFPlayer; an interim 4.1 kHz cue is in the repository, a wider sound redesign is deferred.
- A Bluetooth radio stall longer than the speaker's own buffer still produces a short crackle.
- Legacy PIN pairing, BLE-only and HFP-only speakers are not supported.
- The complete electrical schematic of the installed modules is still to be drawn.
