# G1 controls and modes

This is the reference for the clock's physical controls, LCD screens, settings menu, audio behaviour and USB commands in the current G1 firmware (release `g1-v1.1.0`). The browser page is described in [WEB_UI.md](WEB_UI.md), network and time in [NETWORK_TIME.md](NETWORK_TIME.md), and acceptance status per feature in [FEATURE_STATUS.md](FEATURE_STATUS.md). Pins: [HARDWARE_PICO2W.md](HARDWARE_PICO2W.md). The earlier MicroPython controls are kept in [history](../generations/g0-micropython/doc/MICROPYTHON_CONTROLS_AND_MODES.md).

Two firmware profiles exist: the **web profile** (`-PhoneWeb`, the installed clock, adds the browser page and the Phone Control menu item) and the **ordinary profile** (no web server). Everything below applies to both unless noted.

## Clock screen

```text
12:34:56    MUTE        12:34:56   QUIET
15.11.2026    BT        15.11.2026   SPK
```

`MUTE` (columns 13–16 of the first row) appears while global sound is OFF. Otherwise `QUIET` (columns 12–16) appears while quiet hours are in effect: automatic announcements are silent, while alarms, timer, music and requested speech still play. The second row ends with `BT` or `SPK`: the output the volume encoder currently controls — the active audio owner's output, otherwise the Manual preference, with `SPK` when Bluetooth is unavailable. It is not a connection indicator. Volume 0 does not show `MUTE`. Menus, player, timer, alarm, snooze and temporary overlays use their own screens; RTC error guidance takes precedence.

At start-up the LCD shows the device name and compact firmware version for about 1.6 seconds without blocking the clock; no start-up sound is played.

| Control on the idle clock | Action |
| --- | --- |
| Volume encoder | Adjust the volume of the active output (LOCAL and Bluetooth levels 0–30 are separate) |
| Volume encoder button | Toggle global sound on/off (works on all screens; during a ringing alarm use ALARM) |
| Timer encoder | Set the countdown in whole minutes, 1–1439; steps accelerate to 5 and 10 minutes |
| Timer encoder button | Start or cancel the countdown |
| TIMER_MODE (GP28) | Open the precise hours/minutes/seconds timer editor; press again to cancel it |
| SETTINGS | Open the settings menu |
| MINUS, short (on release) | Show the date for 4 s and speak it; while the countdown runs, speak the time left instead |
| MINUS, hold ≥ 900 ms | Show and speak the next scheduled or snoozed alarm |
| ALARM, short | Open/close the alarm editor; while snoozes are pending on the clock screen, cancel all snoozes |
| ALARM, hold ≥ 900 ms | Open the music player |
| MODE, short | Switch hourly mode VOICE ↔ CHIME (not while the countdown runs) |
| MODE, hold ≥ 900 ms | Speak the current time (also while the countdown runs) |

While an alarm rings: ALARM stops it, GP28 snoozes it for three minutes, the volume encoder still works. A ringing alarm, open menus, a track test or other audio (for example the timer's own phrases) block speech requests; a running countdown and the music player do not (see [manual speech](#manual-speech-during-music-and-the-timer)). A running countdown still blocks some settings.

## Countdown timer

One countdown from 1 second to 23:59:59. Quick encoder steps work in whole minutes (consecutive detents less than 260 ms apart reach 5-minute steps on the third detent and 10-minute steps on the fifth; a pause or direction change resets). The precise editor (GP28) starts from the current duration: TIMER or SETTINGS advances HOUR → MIN → SEC, confirming SEC sets the duration and starts the countdown; MINUS goes back or cancels from HOUR; GP28 and the 20 s idle timeout cancel without change. Zero cannot be confirmed.

**Completion** (SETTINGS → Timer sound, saved):

| Option | Choices | Default |
| --- | --- | --- |
| Five-second warning | single beeps at 5…1 s remaining (`19/001.mp3`) | OFF |
| Message | spoken completion message ON/OFF | ON |
| Extra sound | NONE / SIGNAL / MUSIC | SIGNAL |
| Music | FIXED track 1–255 or RANDOM from folder 08 | track 1 |

The message plays first, then the signal or one music track. Silent completion is valid and still updates the display. Warning beeps that cannot play on time (busy audio, mute, start phrase) are skipped, never queued. The German completion message recording is missing; German message-only completion is therefore silent. Start/cancel phrases and timer output routing are separate settings.

## Settings menu

SETTINGS opens the list; the timer encoder selects; SETTINGS or the timer encoder button enters and confirms; MINUS goes back or discards an unfinished edit. Idle menus close after 20 s (a running Bluetooth scan is allowed to finish). A blinking character cursor marks the field being edited. Only the final confirmation of an editor saves; saved values are written to Flash by a deferred autosave — wait for it (`autosave-status`, or the browser's "Settings saved") before removing power.

| # (web profile) | # (ordinary) | Item | Content |
| --- | --- | --- | --- |
| 1 | 1 | Language | Speech language RU / DE |
| 2 | 2 | Time | HH → MM → SS; written to the RTC on final confirmation |
| 3 | 3 | Date | DD → MM → YYYY |
| 4 | 4 | Quiet mode | ON/OFF, start hour, end hour (default 22–07) |
| 5 | 5 | Half-hour beep | ON/OFF |
| 6 | 6 | Exact-hour word | Adds the exact-hour word to spoken time |
| 7 | 7 | Audio Output | LOCAL/BT preference for Manual (speech and music), Hourly, Timer, Alarm |
| 8 | 8 | Bluetooth | Scan, saved speakers, connect, Disconnect |
| 9 | 9 | Birthdays | 15 annual dates |
| 10 | 10 | Display Light | OFF / ON / AUTO, day and night brightness |
| 11 | — | Phone Control | Address, Home/Direct switch, browser pairing, home trust, forget browsers, Direct key |
| 12 | 11 | About | Two pages: `Pi2Clock G1 / Pico 2 W`, version and `FlintUA OTA<n>` |
| 13 | 12 | Timer sound | Warning, message, extra sound, music (see above) |

**Display Light** drives the LCD LED on GP6. OFF; ON uses the day level; AUTO uses the night level from 22:00 to 06:59 and the day level from 07:00 to 21:59 (night level when the RTC is unavailable). Levels 0–100 % in 5 % steps; defaults OFF, day 100 %, night 20 %. Independent of quiet hours and mute.

**Phone Control** (web profile): shows the current address; switches between Home and Direct Wi-Fi; starts browser pairing (6-digit code for 60 s); toggles home-network trust; forgets paired browsers; rotates the Direct password (shown for 50 s). Home connection progress stays visible while a join is pending. See [NETWORK_TIME.md](NETWORK_TIME.md) and [WEB_BROWSER_ACCESS.md](WEB_BROWSER_ACCESS.md).

## Automatic announcements and quiet hours

- **Hourly:** VOICE speaks the time (Hourly output preference, Bluetooth with LOCAL fallback); CHIME strikes 1–12 times from folder 18 on LOCAL. MODE short press or the browser switches the saved mode.
- **Half-hour:** optional double beep (`07/015.mp3`) on LOCAL.
- **Exact-hour word:** optional word in spoken time.
- **Automatic announcements on/off:** a RAM-only switch (USB `auto on|off`, browser). It returns to ON after restart and is separate from global sound.
- **Quiet hours:** whole hours, start inclusive, end exclusive; a start later than the end crosses midnight; equal hours mean quiet all day. Quiet hours suppress automatic announcements and postpone birthday melodies; they do not affect manual speech, music, the timer or alarms.

An hourly VOICE announcement that falls into Bluetooth music suspends the track, speaks, and resumes the same position ([details](BT_MUSIC_INTERRUPTION.md)). Chimes and half-hour beeps do not interrupt the player.

## Date and next alarm

The date is spoken as weekday, day, month and year (RU folders 06/03/04/05, DE 16/13/14/15). Year recordings cover 2023–2029; other years are shown but not spoken. The next alarm is the nearest future occurrence of an enabled alarm, honouring weekdays; pending snoozes are included. Russian speech adds the alarm-slot phrase (`07/001`–`005`); German has no slot recordings and speaks date and time only. With no enabled alarm the LCD shows `NEXT ALARM / None enabled`. Information speech follows the Manual output and is suppressed (not queued) while other audio or an alarm owns the output or sound is off.

## Manual speech during music and the timer

Since OTA 31 the manual requests — current time, date, next alarm and the new *time left on the timer* — also work while the music player is open and while the countdown runs (browser Speak sheet, MODE hold, MINUS, USB `say`, `say-date`, `next-alarm`, `say-timer`).

- **Bluetooth music** pauses with the same snapshot as the hourly announcement and continues from the same position after the phrase. The phrase uses the Manual output.
- **Built-in speaker music (DFPlayer)** cannot keep its position under another file: the track stops, the phrase plays on the built-in speaker, and the same track restarts from the beginning. A paused track stays paused; TIMER then restarts it. The LCD shows `Clock speech / Track restarts` (Bluetooth: `Music paused BT`).
- A track test in the alarm editor or the player still refuses speech; an alarm, the timer start/cancel/finish audio and the timer warning ticks take priority over the phrase.
- **Time left on the timer** is rounded to the nearest whole minute, at least one minute, and spoken from the existing recordings only: Russian `N часов` (folder 01) + `N минут` (folder 02); German number (folder 12) + `Minuten` (`17/017` on the clock's card; `17/015` there is the half-hour double beep), below one hour only — for an hour or more in German the clock does not speak and the browser reports it. There is no "remaining" word and no seconds recording. During the countdown the date overlay is not shown on the LCD (the countdown stays visible); speech is unaffected.

## Alarms

Five alarms. ALARM opens the editor; the timer encoder selects a slot and changes fields: enabled, hour, minute, days, sound, music track. TIMER confirms/advances; in the track field SETTINGS starts/stops a preview instead. Changes stay a draft until the final confirmation; MINUS returns to the list and discards the draft.

- **Days:** Daily, Mon–Fri, Sat–Sun or Custom. In Custom, TIMER steps Monday → Sunday and the encoder toggles each day; at least one day must stay selected.
- **Sound:** SIGNAL, MUSIC (fixed track 1–255 from folder 08) or RANDOM (one random track per occurrence, kept through snooze and fallback; the previous random choice of the same alarm is avoided when at least two files exist).
- **Snooze:** GP28 during ringing stops the sound and repeats it after three minutes (monotonic time, unaffected by RTC/NTP changes); repeated snooze is possible. The clock screen shows the next snoozed alarm; ALARM on the clock screen cancels all snoozes. Snoozes are RAM-only.
- **Deferral:** an alarm that falls due while the countdown runs, sound is off or an editor is open waits; it expires 30 minutes after it was due. A due alarm interrupts music; Bluetooth music resumes after the alarm ([details](BT_MUSIC_INTERRUPTION.md)).
- Disabling or editing a slot cancels its waiting or snoozed occurrence.

## Birthdays

Fifteen annual dates under SETTINGS → Birthdays, each disabled by default (1 January, 09:00). Edit ON/OFF → MONTH → DAY → HOUR → MINUTE; confirming the minute saves. February 29 fires only in leap years. The browser also stores an optional birth year (`DD.MM.YYYY`), which does not change recurrence.

At the matching minute the event is claimed once per year (the year is saved, so restarts, DST and backward clock corrections do not repeat it). The melody `07/000.mp3` follows the Manual output and waits for an idle clock, sound on and non-quiet hours for at most 30 minutes; the LCD shows `BIRTHDAY N` and the date for 8 s. There is no catch-up for minutes missed while powered off, and a match in the first valid minute after boot is consumed silently.

## Music player

ALARM hold opens the player; playback starts automatically when sound is on. Music comes from folder 08 (tracks 1–255). Each opening starts in SHUF mode.

| Control in the player | Action |
| --- | --- |
| TIMER button | Pause/resume; start the selected track when stopped |
| GP28 | Sleep timer OFF → 15 → 30 → 60 → 90 min → OFF |
| SETTINGS or timer encoder clockwise | Next |
| MINUS short or timer encoder counter-clockwise | Previous (history of up to 128 selections) |
| ALARM short | Mode SHUF → REP1 → NORM |
| ALARM, MODE or MINUS hold ≥ 900 ms | Stop and exit |
| Volume encoder / button | Volume of the active output / sound on-off |

NORM plays in number order and wraps; SHUF plays every track once per cycle and keeps the last seven out of the start of the next cycle; REP1 repeats the current track. The LCD shows mode and output (`MUSIC SHUF BT`), track/count, `PLAY/PAUS/STOP/WAIT/MUTE` and the sleep field (`OFF` or remaining minutes). Muting stops music; unmuting does not restart it.

Pause keeps the position on both outputs. If Bluetooth is lost, music restarts the current track on LOCAL (positions cannot move between the two cards); if Bluetooth is lost while paused, the next TIMER press restarts the track on LOCAL. Sleep counts wall time including pauses; expiry stops playback silently and returns to the clock. Player mode, history, pause and sleep are RAM-only.

## Audio outputs and volume

**LOCAL** (`SPK`) is the DFPlayer with its own card. **BT** is the selected Bluetooth speaker, fed from the Pico's SPI card (MP3 → Helix decoder → SBC → A2DP). Four saved preferences choose the output for Manual (speech, information, music, birthdays), Hourly, Timer and Alarm. A preference is a wish: if no speaker stream is active or a file is missing on the SPI card, the clock falls back to LOCAL. Both cards must contain the same numbered folders.

LOCAL and Bluetooth volumes (0–30) are stored separately; the volume encoder changes the one in use. Bluetooth volume is sent to the speaker as AVRCP Absolute Volume; if the speaker refuses it, the clock scales the audio itself.

## Bluetooth speakers

SETTINGS → Bluetooth lists *Scan devices*, saved speakers (up to four), newly found devices and *Disconnect*. Choose a speaker and confirm *Connect*; the clock saves it once the audio stream is active (close the menu and wait for autosave). After a restart it reconnects to the saved speaker directly, without scanning. *Disconnect* or starting a scan turns the connection OFF until the next explicit Connect, also across restarts; a lost link with a selected speaker retries automatically. Speaker buttons Play/Pause control the clock's music player.

Supported: Classic A2DP sinks with SBC and SSP pairing. Not supported: BLE-only, HFP-only, legacy PIN pairing, Google Cast.

Streaming details (automatic, see [BT_AUDIO_CHAIN.md](BT_AUDIO_CHAIN.md)): Wi-Fi power saving is switched off while a Bluetooth stream is active; the SBC bitpool is the highest negotiated value that puts at least seven frames into one packet (40 for speakers with a 656-byte payload such as JBL Link Portable, 53 for larger payloads); after a radio stall the sender catches up to 300 ms of audio.

The LCD Bluetooth status shows ON (streaming), RETRY (selected speaker offline) or OFF (no selected speaker). MAC addresses appear only in USB diagnostics.

## Persistence

Settings are stored in Flash (record v18; all earlier records are read; loading never writes). Saving is deferred until the clock is idle; `autosave-status` reports it. RAM-only: global sound (ON after restart), automatic announcements switch, snoozes and waiting events, player session, random-track history. Bluetooth pairing keys are kept by BTstack in their own sectors.

## USB serial commands

Serial port at 115200 baud (`tools/capture-pico-log.ps1` records it). `help` prints the list. Read-only commands are safe at any time; commands that change settings require the clock to be idle and close the menu first.

| Area | Commands |
| --- | --- |
| Information | `version`, `status`, `help`, `flash-info`, `flash-inspect`, `flash-tail`, `autosave-status`, `audio-health`, `audio-settings`, `mode-status`, `quiet-status`, `auto-status`, `auto-debug`, `rtc-debug`, `rtc-reset-stats`, `display-light-status`, `phone-web-status` (web profile) |
| Timer | `t <seconds>`, `start`, `cancel`, `timer-sound`, `timer-sound none\|signal\|music N`, `timer-voice on\|off`, `timer-random on\|off`, `timer-warning [on\|off]`, `random-music-status` |
| Speech and modes | `say [HH MM]`, `say-date`, `next-alarm`, `say-timer`, `lang ru\|de`, `exact on\|off`, `mode voice\|chime`, `auto on\|off`, `auto-test HH MM` (silent), `auto-voice-play HH`, `sound`, `vol N`, `save` |
| Alarms | `alarm-status`, `alarm-set HH MM signal\|music\|random [track]` (slot 1), `alarm-config N HH MM signal\|music\|random [track]`, `alarm-enable N on\|off`, `alarm-days N daily\|weekdays\|weekends\|135`, `alarm-off`, `alarm-stop`, `alarm-test HH MM [slot]`, `alarm-snooze`, `alarm-snooze-status`, `alarm-snooze-cancel`, `alarm-pending`, `alarm-pending-test N`, `alarm-pending-clear` |
| Birthdays | `birthday-status`, `birthday-set N DD MM HH MM on\|off`, `birthday-test N`, `birthday-pending-clear` |
| Player | `play F T`, `pause`, `audio`, `menu` |
| Audio routing | `audio-select local\|bt`, `auto-audio local\|bt`, `timer-audio local\|bt`, `alarm-audio local\|bt` (`jbl` is accepted as an alias of `bt`), `audio-route`, `audio-route-test F T`, `auto-audio-test H`, `alarm-audio-test N` |
| Bluetooth | `bt-scan`, `bt-scan-stop`, `bt-devices`, `bt-known`, `bt-use N\|name\|MAC`, `bt-connect MAC`, `bt-disconnect`, `bt-forget N\|MAC`, `bt-target`, `bt-status`, `bt-volume`, `bt-vol 0..30` |
| Bluetooth tests (not saved) | `bt-bitpool N` (0 = automatic), `bt-frames 0..15` (0 = automatic), `wifi-pm auto\|none\|default\|aggr`, `bt-tone`, `bt-clip`, `bt-silence` |
| Network | `wifi-config SSID\|password`, `wifi-config`, `wifi-clear`, `ntp-status`, `ntp-sync` |
| SD and MP3 diagnostics | `sd-test`, `sd-info`, `sd-list [folder]`, `sd-file F/T.mp3`, `sd-stream F/T.mp3`, `sd-stop`, `mp3-play F/T.mp3`, `mp3-pause`, `mp3-resume`, `mp3-stop`, `mp3-status`, `mp3-test F/T.mp3`, `mp3-pause-test F/T.mp3` |
| Maintenance | `bootsel arm` then `bootsel confirm` within 15 s (`bootsel cancel`); refused while busy or before autosave |

The `[BT-DIAG]` line (printed every 10 s during streaming only when packets were trimmed, refused or delayed by more than 150 ms) and `bt-status` are the starting points for Bluetooth audio problems.
