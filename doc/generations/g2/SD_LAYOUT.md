# G2 microSD layout, offline and network data

> **Status (2026-11-23): specification for the new G2 card.** Not compatible with the numbered folders 01–19 of the G1 DFPlayer cards. The skeleton in [`sound/g2_sdcard`](../../../sound/g2_sdcard/) contains only folders and example JSON, no audio. Translated and structured from the user's `Pi2Clock_G2_SD_LAYOUT.md` ([original](sources/docs/Pi2Clock_G2_SD_LAYOUT.md)); review notes are marked **Review**.

## 1. Format and limits

- FAT32, one file system, ASCII `snake_case` names, short unique `track_id`s; artist and title as UTF-8 inside JSON. Test 8/16/32 GB A1/U1 cards from reliable makers first.
- The G1 driver `firmware/pico2w_c/drivers/sd_fat32.c` reads 8.3 names only and is read-only. **G2 needs** FatFs with long file names (or an equivalent proven driver), nested folders, safe writes and no SD access during an unfinished SPI transaction with the OLED.
- One `/PI2CLOCK/` folder in the card root. Files are identified by **path and manifest**, not by DFPlayer numbers.
- Schema `g2-sd-1`; change only with a migration. On first start check integrity and never delete unknown user files.

## 2. Folder tree

```text
microSD (FAT32)
└── PI2CLOCK/
    ├── manifest.json                  # card schema and the packs ACTUALLY installed
    ├── config/
    │   ├── README.md
    │   └── user_settings.example.json # example only, not read by the firmware
    ├── voices/
    │   ├── README.md
    │   ├── ru-RU/
    │   │   ├── female_01/{voice.json, phrases/, tokens/, templates/}
    │   │   ├── female_02/ … female_03/
    │   │   └── male_01/ … male_03/
    │   └── de-DE/ (the same six voices)
    ├── music/
    │   ├── catalog.json               # tracks and collections (empty at first)
    │   ├── collections/
    │   │   ├── classical/             # add your own licensed MP3 files here
    │   │   ├── disco/
    │   │   └── ru_music/
    │   └── playlists/                 # later
    ├── sounds/
    │   ├── ui/                        # click, confirm, error
    │   ├── alerts/                    # timer_done, alarm, battery_low
    │   └── chimes/                    # hourly, half_hour
    ├── cache/
    │   ├── weather/                   # optional cached forecasts
    │   └── ntp/                       # optional last successful sync
    ├── logs/                          # ring diagnostic log with size limits
    ├── recordings/                    # optional voice notes from the INMP441
    ├── updates/                       # service downloads only; firmware protects A/B
    └── backup/                        # settings/alarm export without secrets
```

Empty folders hold `.gitkeep` files so they survive copying on Windows and Git. A voice folder does not mean recordings exist.

## 3. Music catalog

`music/catalog.json` lists tracks `{track_id, path, artist, title, collection, enabled}` and the collections. A `track_id` does not depend on FAT32 order; playlists and alarms store `track_id`s, not file indexes.

```json
{
  "schema": "g2-music-1",
  "tracks": [
    {
      "track_id": "song_0001",
      "path": "music/collections/classical/artist_-_title.mp3",
      "artist": "Example Artist",
      "title": "Example Title",
      "collection": "classical",
      "enabled": true
    }
  ],
  "collections": ["classical", "disco", "ru_music"]
}
```

If a file is deleted or renamed, its `track_id` becomes unavailable: the player skips it, an alarm falls back to a safe system signal, and the event is logged. The number of files in a folder is never assumed to be the number of songs. Modes: sequential, shuffle, repeat-one and *All music*; `voices/` and `sounds/` are never part of a random selection.

**Review:** who writes `catalog.json`? Writing it by hand for hundreds of tracks is impractical. Options: a PC tool (`tools/g2_catalog.py`) that scans the collections, reads ID3 tags and writes the catalog, or the firmware building an index in Flash/RAM by scanning the collections at start. A PC tool keeps the firmware simple and can also run the validator.

## 4. Voice packs

- One pack = one language + one voice: `voices/ru-RU/female_01/`, `voices/de-DE/male_02/`, …
- `voice.json`: ID, language, display name, licence, audio parameters, `installed=false` until audio exists and has been validated, list of supported phrases.
- `phrases/` for **complete fixed** phrases (`system.ready.wav`, `wifi.connected.wav`); `tokens/` for numbers, dates, units, ordinals; `templates/` for grammar rules that assemble messages. A variable such as `[TIME]` is never stored as a whole WAV.

```text
voices/ru-RU/female_01/phrases/system.ready.wav
voices/ru-RU/female_01/phrases/sound.enabled.wav
voices/ru-RU/female_01/tokens/timer/first.wav
voices/ru-RU/female_01/tokens/numbers/14.wav
voices/ru-RU/female_01/tokens/units/minutes_acc_many.wav
voices/de-DE/female_01/phrases/system.ready.wav
voices/de-DE/female_01/tokens/timer/one.wav
voices/de-DE/female_01/tokens/units/minuten_plural.wav
```

Example template `timer.finished` (RU): `timer_first + timer_on + number_14 + minutes_acc_many + timer_finished` → «Первый таймер на четырнадцать минут завершён» ("The first timer of fourteen minutes has finished"). The German template is built independently with German word order, not translated token by token. Details: [VOICE.md](VOICE.md).

## 5. What the card must hold for offline operation

**Required for full offline sound:** speech files with their manifests (at least one voice for RU and DE), `sounds/alerts/` and `sounds/chimes/`, and optionally music with its catalog. Clock and timers must work **without** the SD card, then without voice and music; a minimal beep from Flash (or PIO) plus OLED and WS2812 indication is mandatory for critical events.

**Kept in Flash, not only on SD:** time and RTC state, time zone and DST, alarm schedules, timers and event IDs, language and voice choice, volumes (separate local/Bluetooth), saved Bluetooth devices, Wi-Fi credentials, browser permissions, OTA A/B metadata. A backup on SD is allowed **without passwords and keys**. Without network the time comes from the DS3231 if fitted, otherwise only from the running clock while powered; NTP is not needed for music, speech or timers.

**Timers after a reset:** restoring a running timer requires a trustworthy clock and a saved state; without an RTC and a dedicated journal, keeping a running timer across a full power loss cannot be promised.

## 6. With a network

- Wi-Fi and Bluetooth drivers are part of the firmware, not files on the card.
- NTP corrects the clock; DST for Europe/Berlin is computed by the firmware rules (as in G1). A DS3231 receives the correction; without NTP use the RTC or manual setting with a validity indicator.
- `cache/weather/` keeps only the last forecast with timestamp and expiry; **an expired cache is never shown as current weather**. Alarms never depend on a server.
- Browser control, permissions and A/B OTA come from G1 and keep critical settings in Flash; the SD card is only for temporary files, logs and exports. OTA writes must not conflict with audio or display and never erase the active slot without verification.
- Bluetooth A2DP from G1 keeps the saved addresses and names, but G2 must verify I2S, MP3, SD, OLED and CYW43 working together. The built-in speaker plays a mono mix of L+R; Bluetooth keeps stereo.

## 7. Audio formats and resources

- Short speech tokens: preferably PCM WAV mono 16-bit at 16 or 24 kHz (no MP3 encoder delay, no audible joins). Long messages and music may be MP3. Confirm the conversion to the I2S and Bluetooth rate and the RAM needed.
- OLED 256×64 at 4 bits per pixel = 8,192 bytes of frame buffer. Never hold a whole MP3 in RAM; read in chunks. Serialise the shared SPI1 between SD and OLED (separate CS).
- An early build may use 8.3 names, but that is not the requested folder hierarchy; the real plan needs VFAT long names and recursive traversal. A `manifest.json` validator is required for a G2 release.

**Review:** the G1 pipeline converts everything to 44.1 kHz (Bluetooth requires it; the I2S clock can stay at 44.1 kHz too). Speech recorded at 22.05 kHz converts by an exact factor of two; 16 or 24 kHz needs fractional resampling, which G1 already has (linear interpolation for 32 and 48 kHz). Either works; 22.05 kHz is the simplest and about the same card space as 24 kHz.

## 8. Open questions

- Licence and a complete set of WAV files for all twelve voices.
- OLED and card current; the 3.3 V regulator and power path.
- GPIO state with simultaneous microphone RX and amplifier TX.
- FAT32 long names, recursive search, write permissions, card wear.
- Detecting a missing or bad card and a graceful fallback without missing a timer.
