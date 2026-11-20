# Speaking Timer-Clock - Project Status

## Overview
Two implementations exist in this repository:

### 1. Legacy v1 (Working) - `source/speaking_timer_clock.py`
Monolithic single-file implementation using:
- Direct hardware access
- Legacy sound folder structure (`/sd/sound/_sdcard/01-20/`)
- Blocking synchronous code
- German display messages, Russian/German voice

### 2. Modular v2 (New Architecture) - `speaking_clock/` + `main.py`
Clean modular architecture with:
- Async/await main loop
- Hardware abstraction layer
- Persistent JSON configuration storage
- Multi-language support (RU/DE/UA)
- Priority speech queue
- Multiple alarms with day masks
- Countdown timer + Pomodoro
- Music player with shuffle
- Clean separation of concerns

## New Architecture Structure

```
speaking_clock/
├── __init__.py          # Package info
├── config.py            # All hardware pins, defaults, constants
├── storage.py           # JSON config with atomic writes, migration
├── hardware/
│   ├── __init__.py
│   ├── rtc_ds1302.py    # DS1302 RTC with ppm calibration
│   ├── lcd_i2c.py       # I2C LCD 1602 with double buffering
│   ├── dfplayer.py      # Async DFPlayer with command queue
│   ├── rotary_encoder.py # Interrupt-driven with acceleration
│   └── buttons.py       # Debounced buttons with short/long press
├── core/
│   ├── __init__.py
│   ├── clock.py         # Timekeeping, RTC sync, DST, formatting
│   ├── speech.py        # Priority speech queue (CRITICAL/HIGH/NORMAL/LOW)
│   ├── alarms.py        # Multi-alarm manager with day masks
│   ├── timer.py         # Countdown + Pomodoro timers
│   └── music.py         # Music player with folder scanning
├── locale/
│   ├── __init__.py
│   └── manager.py       # TTS folder mapping, phrases, UI strings
└── ui/
    ├── __init__.py
    └── display.py       # Display manager with custom chars, screens

main.py                  # Application entry point
```

## Hardware Pin Mapping (config.py)

| Component | Pins |
|-----------|------|
| I2C LCD (PCF8574) | SDA=GP0, SCL=GP1 |
| DFPlayer Mini | UART0: TX=GP16, RX=GP17, BUSY=GP18 |
| DS1302 RTC | CLK=GP2, DAT=GP5, RST=GP4 |
| Encoder 1 (Left/Volume) | DT=GP14, CLK=GP15, SW=GP20 |
| Encoder 2 (Right/Timer) | DT=GP11, CLK=GP10, SW=GP19 |
| Buttons 1-5 | GP28, GP21, GP22, GP26, GP27 |

## Sound Folder Structure (Legacy v1 - sound/_sdcard/)

```
01/ - Russian hours (000-023)
02/ - Russian minutes (000-059)
03/ - Russian day numbers (001-031)
04/ - Russian months (001-012)
05/ - Russian years (003=2023...)
06/ - Russian weekdays (001-007)
07/ - Russian phrases (007=timer set, 008=sound on, 009=sound off, 014=timer off, 015=minuten)
08/ - Music files (1-45.mp3)
09/ - Russian numbers 0-30
11/ - German hours (000=noon, 001-023)
12/ - German minutes (000=exact, 001-059)
13/ - German day numbers (001-031, erste...)
14/ - German months (000=Januar, 001-012)
15/ - German years (003=2023...)
16/ - German weekdays (001=Montag)
17/ - German phrases (same track numbers as RU folder 07)
18/ - Chimes (000=melody, 001-012=hour strikes)
19/ - Simple beeps (001=1 beep, 002=2 beeps)
```

## Locale Manager TTS Mapping (v2)
Matches legacy folder numbers perfectly:
- **RU**: base=1 → hours=1, minutes=2, days=3, months=4, years=5, weekdays=6, phrases=7
- **DE**: base=11 → hours=11, minutes=12, days=13, months=14, years=15, weekdays=16, phrases=17
- **UA**: base=21 → hours=21, minutes=22, days=23, months=24, years=25, weekdays=26, phrases=27

## ⚠️ Compatibility Notes

### Phrase Track Numbers Mismatch
The v2 locale manager expects different track numbers than the legacy sound files:

| Phrase Key | v2 Expected Track | Legacy Track (folder 07/17) |
|------------|-------------------|------------------------------|
| alarm | 1 | N/A |
| timer_done | 2 | N/A |
| volume_on | 5 | 8 |
| volume_off | 6 | 9 |
| timer_set | 10 | 7 |
| timer_cancelled | 11 | 14 |
| menu_enter | 7 | N/A |

**Action needed**: Either renumber MP3 files on SD card or update `locale/manager.py` phrase_tracks to match legacy.

### Music Folder
- Legacy: folder 08 (tracks 1-45)
- v2 expects: `/sd/music/` with folder structure
- **Action needed**: Copy/move music files to new structure or update MusicPlayer to use folder 08

### Chimes
- Legacy: folder 18 (000=melody, 001-012=strikes)
- v2: Not yet mapped in locale manager
- **Action needed**: Add chime folder mapping to locale manager

## Features Implemented in v2

✅ Hardware abstraction (all drivers)
✅ Configuration storage with migration
✅ Multi-language locale system
✅ Priority speech queue
✅ Alarm manager with day masks
✅ Countdown timer with presets
✅ Pomodoro timer
✅ Music player framework
✅ Display manager with custom chars
✅ Encoder handling with acceleration
✅ Button handling with short/long press
✅ Main async event loop
✅ Quiet/night mode
✅ RTC calibration (ppm)

## TODO for Full Feature Parity with v1

- [ ] Map phrase track numbers to legacy sound files
- [ ] Implement hourly/half-hour chimes
- [ ] Implement chime styles (grandfather, westminster, simple)
- [ ] Add menu system (MenuSystem, ScreenManager classes)
- [ ] First-boot wizard
- [ ] Time/date setting via UI
- [ ] Alarm editing via UI
- [ ] RTC calibration via UI
- [ ] Settings persistence for all new options
- [ ] Music folder scanning for legacy structure
- [ ] Display screens for all menu items

## Running the Project

### Legacy v1 (proven working)
```bash
# Copy source/speaking_timer_clock.py to Pico as main.py
# Ensure SD card has sound/_sdcard/ structure
```

### Modular v2 (new architecture)
```bash
# Copy entire speaking_clock/ package + main.py to Pico
# Ensure SD card has either:
#   - Legacy structure at /sd/sound/_sdcard/ (for migration)
#   - New structure at /sd/tts/, /sd/music/, /sd/chimes/
# First boot will run wizard (when implemented)
```

## Configuration

All settings stored in `config.json` on Pico flash (LittleFS):
- Volume, language, quiet mode
- Alarms (time, days, sound, label)
- Timer presets, Pomodoro settings
- Chime settings
- Display settings (brightness, timeout)
- RTC calibration (ppm)

## Migration Path

1. **Keep v1 working** - it's proven on hardware
2. **Test v2 incrementally** - hardware drivers work independently
3. **Map sound files** - update locale manager or reorganize SD card
4. **Implement missing UI** - menus, settings screens
5. **Switch over** - once v2 has full feature parity

## Key Design Decisions

1. **Async main loop** - Non-blocking, responsive UI
2. **Priority speech queue** - Alarms interrupt music/timers
3. **Double-buffered LCD** - No flicker, only changed chars updated
4. **Atomic config writes** - No corruption on power loss
5. **Interrupt-driven encoders** - No polling, with acceleration
6. **Hardware abstraction** - Easy to test, swap implementations
7. **Dot-notation config keys** - `storage.get("quiet_mode.start")`