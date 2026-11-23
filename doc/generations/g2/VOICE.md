# G2 speech: events, phrases and voice packs (RU/DE)

> **Status (2026-11-23): editorial script; no speech files exist yet.** The texts are phrases to be recorded or synthesised, not transcripts of the G1 DFPlayer files. Translated and structured from the user's `Pi2Clock_G2_VOICE_PHRASES_RU_DE.md` ([original](sources/docs/Pi2Clock_G2_VOICE_PHRASES_RU_DE.md)). The complete event catalogue is the machine-readable [voice_phrases_ru_de.csv](voice_phrases_ru_de.csv); review notes are marked **Review**.

## Conventions

- An **event ID** (for example `timer.finished`) is a permanent identifier used by the firmware.
- Placeholders `[N]`, `[ORD]`, `[TIME]`, `[HOUR]`, `[DURATION]`, `[DATE]`, `[WEEKDAY]`, `[DAY]`, `[MONTH]`, `[YEAR]`, `[NAME]`, `[TEMP]`, `[HUMIDITY]`, `[PRESSURE]`, `[PERCENT]`, `[VOICE]`, `[LEVEL]`, `[CONDITION]` are **variables** assembled by the speech engine from verified tokens. Brackets and variable names are never spoken.
- Languages: Russian (`ru-RU`) and German (`de-DE`), each with six voices `female_01..03` and `male_01..03` — twelve packs. A first release may ship one validated voice per language; the others are optional packs. Every pack declared installed must pass full validation. Voices are never mixed within one sentence.
- Speech must never delay the timer or alarm event itself.

## Event catalogue

The CSV has 122 events with Russian and German text, notes (playback conditions) and status (`plan` for all). Groups:

| Group | Events | Examples |
| --- | ---: | --- |
| `alarm.*` | 10 | announced, enabled, disabled, next, snoozed, stopped |
| `birthday.*` | 3 | today, tomorrow, age |
| `bt.*` | 11 | connected, disconnected, searching, output local/remote |
| `clock.*` | 7 | current time and date, exact hour, chime, sync |
| `music.*` | 11 | started, paused, next, shuffle, sleep timer, track missing |
| `network.*`, `wifi.*` | 3 + 5 | web interface, Wi-Fi connected/unavailable |
| `ota.*` | 7 | checking, installing, success, rollback |
| `recording.*` | 3 | start, saved, failed (microphone) |
| `sound.*` | 7 | enabled, disabled, volume, night and silent mode |
| `system.*` | 18 | ready, SD missing, battery, audio unavailable |
| `timer.*` | 16 | set, started, remaining, finished, cancelled, paused for three timers |
| `voice.*` | 2 | voice changed, preview |
| `weather.*` | 19 | temperature, humidity, pressure, forecast, stale data |

The CSV in this folder was cleaned from the original: stray closing quotation marks removed, notes translated to English, and notes about G1 updated (for example, snooze already exists in G1).

## Phrases that cannot be assembled from generic words

### Time

| Time | RU | DE (official 24-hour style) |
| --- | --- | --- |
| 00:00 | Сейчас полночь. | Es ist Mitternacht. |
| 01:00 | Сейчас один час ровно. | Es ist ein Uhr. |
| 02:01 | Сейчас два часа одна минута. | Es ist zwei Uhr eins. |
| 05:02 | Сейчас пять часов две минуты. | Es ist fünf Uhr zwei. |
| 14:25 | Сейчас четырнадцать часов двадцать пять минут. | Es ist vierzehn Uhr fünfundzwanzig. |
| 23:59 | Сейчас двадцать три часа пятьдесят девять минут. | Es ist dreiundzwanzig Uhr neunundfünfzig. |

Russian needs agreement of `час/часа/часов` and `минута/минуты/минут`; clock time uses the masculine "один час", a duration after "на" uses "одну минуту". German uses `ein Uhr` for 01:00 and the standard 24-hour reading otherwise; colloquial forms like *halb drei* are optional.

### Three timers

| Event | RU | DE |
| --- | --- | --- |
| T1, 14 min, set | Первый таймер установлен на четырнадцать минут. | Timer eins auf vierzehn Minuten eingestellt und gestartet. |
| T1, 14 min, finished | **Первый таймер на четырнадцать минут завершён.** | **Timer eins mit vierzehn Minuten Laufzeit ist abgelaufen.** |
| T2, 1 min, finished | Второй таймер на одну минуту завершён. | Timer zwei mit einer Minute Laufzeit ist abgelaufen. |
| T3, 1 h 2 min 3 s, finished | Третий таймер на один час две минуты три секунды завершён. | Timer drei mit einer Stunde, zwei Minuten und drei Sekunden Laufzeit ist abgelaufen. |
| T2, 5 s left | Второй таймер — осталось пять секунд. | Timer zwei: noch fünf Sekunden. |

The finished message speaks the **originally set duration**, not the remaining zero; the timer state must keep `initial_duration` separately from the remaining time. Events finishing together are queued and each is confirmed separately.

**Review:** the CSV entry `timer.finished` has the German pattern "Timer [N] über [DURATION] ist abgelaufen", while the table above uses "Timer [N] mit [DURATION] Laufzeit ist abgelaufen". One wording must be chosen (the table's version reads more naturally; to be confirmed by listening).

### Dates and birthdays

| Event | RU | DE |
| --- | --- | --- |
| 1 November 2026 | Сегодня воскресенье, первое ноября две тысячи двадцать шестого года. | Heute ist Sonntag, der erste November zweitausendsechsundzwanzig. |
| Alarm 4, 07:30 | Будильник номер четыре. Сейчас семь часов тридцать минут. | Wecker vier. Es ist sieben Uhr dreißig. |
| Birthday | Сегодня день рождения Михаила. | Heute hat Michail Geburtstag. |

If a name is not in the voice dictionary, announce the neutral «Напоминание о дне рождения» / „Geburtstagserinnerung" and show the name on the OLED; never substitute another file.

## Required tokens (in every voice pack)

1. `numbers/cardinal`: 0–59 at least, 60–100 and hundreds for percent, years, pressure, temperature. German compounds (`einundzwanzig`, `zweiundvierzig`, …) must be checked.
2. `numbers/ordinal_timer`: RU первый/второй/третий; DE eins/zwei/drei or erste/zweite/dritte, consistent with the chosen syntax.
3. `numbers/alarm` 1–5; `numbers/birthday` 1–15 (event number); age 0–120 if needed.
4. `units/duration`: RU `час/часа/часов`, `минуту/минуты/минут`, `секунду/секунды/секунд`, and for "осталось" the nominative `минута/минуты/минут`, `секунда/секунды/секунд`; DE `eine Stunde/Stunden`, `eine Minute/Minuten`, `eine Sekunde/Sekunden`.
5. `calendar`: seven weekdays in both languages; twelve months (RU genitive: января, февраля, …; DE nominative); day ordinals RU `первое … тридцать первое`, DE `erste … einunddreißigste` after "der" (separate forms after "am" if used).
6. `time`: `Uhr`, `ровно`, `полночь`, `сейчас`, `Es ist`, fixed phrases for 00:00 and 01:00; Russian in 24-hour form.
7. `weather`: `минус`, `градус/градуса/градусов`, `Prozent`, `Hektopascal`, weather categories, data age; weather is spoken only when fresh.
8. `ui`: Wi-Fi/Bluetooth connections, menus, SD errors, voice/sound, battery, fallback notices (if the card is available).

**Grammar is a program rule, not file magic.** For example, Russian after "на": 1 → одну минуту; 2/3/4 → две/три/четыре минуты; 5/11/14/25 → пять/одиннадцать/четырнадцать/двадцать пять минут. Test the forms for 1, 2, 5, 11, 12, 14, 21, 22, 25 and 101 with several units.

## Audio files

- Path: `/PI2CLOCK/voices/<language>/<voice_id>/phrases/<event_id>.wav` for complete messages without variables (for example `system.ready.wav`); messages with parameters use `templates/<event_id>.json` plus named files under `tokens/`.
- **Do not copy** old G1 files such as `01/001.mp3` or `17/013.mp3` by number; their content is not verified without listening.
- Short phrases and tokens: mono PCM WAV 16-bit at 16 or 24 kHz, if the playback path joins them without gaps; MP3 for music and long phrases. Choose the rate by testing I2S and Bluetooth (see the review note in [SD_LAYOUT.md](SD_LAYOUT.md#7-audio-formats-and-resources)).
- All twelve voices share the event IDs, loudness levels and normalised dynamics. Check the licences for synthesis and for distributing recordings in kits.
- `voice.json` and `manifest.json` describe the packs actually installed, schema version, format and checksums. A missing file means text on the OLED and the fallback tone from Flash — never a random other track.

## Notification priority

Alarm or finished timer → mandatory indication and, if allowed by the settings, sound → other spoken status messages → music. Network-dependent speech is never a mandatory source. In silent mode OLED and WS2812 indication is mandatory; the alarm sound policy is a separate setting. Queued messages must not be lost while the audio path is busy.

## Test cases for recording

- RU/DE 00:00, 01:01, 02:02, 05:05, 14:14, 23:59; dates with day 1, 2, 5, 21, 31 and years 2027, 2030, 2099.
- T1 = 14 min, T2 = 1 min, T3 = 01:02:03; simultaneous finish and confirming one timer.
- Birthday with a name in the dictionary and without; five alarms; choosing each of the six voices per language.
- No Wi-Fi, NTP long ago, SD removed, Bluetooth lost, low battery, no answer from the weather service.
- Speech interrupting music; Bluetooth stereo → local mono; the track must not restart after a notification.
